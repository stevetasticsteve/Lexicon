#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import datetime
import logging
import os
import sys
import traceback
from collections import Counter

import pyexcel_ods3
from jinja2 import Environment, FileSystemLoader

import lexicon_config


def initiate_logging():
    # Initiate error logging
    logger = logging.getLogger('LexiconLog')
    logger.setLevel(logging.DEBUG)

    # add a stream log, and a file log for errors
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    logger.info('Updating Lexicon')
    if __name__ == '__main__':
        log_file = lexicon_config.settings['log_file']
        fh = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        fh.setLevel(logging.ERROR)
        logger.addHandler(fh)
    return logger


def excepthook(exctype, value, tb):
    if exctype == AssertionError:
        logger.error('A critical error occurred: {value} \nAdjust settings and try again'.format(value=value))
    else:
        logger.critical('''An unhandled error occured, please contact the developer:
        Error type : {type}
        Error value: {value}
        Traceback: {tb}'''.format(type=exctype, value=value, tb=traceback.format_tb(tb)))


def letter_to_number(letter):
    """returns an integer to use as an index for a given column letter. Can only accept up to column Z"""
    assert type(letter) == str, 'Must provide a string'
    assert len(letter) == 1, 'Function only designed for single letter columns'
    assert letter.isalpha(), 'Must provide alphabetic input'

    return ord(letter.upper()) - 65


# def check_config():
#     #todo write it!
#     pass


def read_lexicon(*args, config_file=lexicon_config, number_of_columns=18):
    """Reads the .ods and returns a list of dictionary items representing the lexicon,
    unlike create_lexicon_entries() it doesn't group senses under 1 headword - it's just a data dump."""
    spreadsheet = config_file.settings['spreadsheet_name']
    assert os.path.exists(spreadsheet), '{spreadsheet} does not exist'.format(spreadsheet=spreadsheet)
    _, extension = os.path.splitext(spreadsheet)
    valid_extensions = ('.ods', '.xls', '.xlsx')
    assert any(ex == extension for ex in valid_extensions), \
        'Invalid file {extension}, must be .ods, .xls or .xlsx'.format(extension=extension)
    if args:
        logger.info('Function not designed to accept arguments. \nDefine the settings in lexicon_config.py or pass a '
                    'different config via the config_file **kwarg')

    # Convert column letters to list integers
    col = {k: letter_to_number(v) for k, v in config_file.spreadsheet_config.items()}
    assert len(col) == number_of_columns, \
        '{n} items expected in spreadsheet_config, {m} defined'.format(n=number_of_columns, m=len(col))

    # Read the lexicon and return a list of (Python) dictionary entries
    try:
        raw_data = pyexcel_ods3.get_data(spreadsheet)[config_file.settings['sheet_name']]
    except KeyError:
        raise AssertionError('That sheet doesn\'t exist.')
    # Throw an assertion error if the file is blank (pyxcel returns [[]] )
    assert len(raw_data) > 1, 'That file is blank'

    # If the first row is identified as a header row (ID column is a string rather than int) get rid of it
    if type(raw_data[0][col['id_col']]) == str:
        raw_data.pop(0)

    # create a list of dictionaries
    raw_data = [x for x in raw_data if x != []]  # get rid of blank rows
    # set the id number to 0 if it's blank - preventing sort failures later
    for row in raw_data:
        if row[col['id_col']] == '':
            row[col['id_col']] = 0
    raw_data.sort(key=lambda raw_data: raw_data[col['id_col']])  # sort by ID number
    processed_data = []
    for entry in raw_data:
        while len(entry) < number_of_columns:  # add blank columns to avoid index errors
            entry.append('')
        d = {
            'id': entry[col['id_col']],
            'orth': entry[col['orth_col']],
            'phon': entry[col['phon_col']],
            'dial': entry[col['dial_col']],
            'sense': entry[col['sense_col']],
            'pos': entry[col['pos_col']],
            'eng': entry[col['eng_col']],
            'tpi': entry[col['tpi_col']],
            'def': entry[col['def_col']],
            'ex': entry[col['ex_col']],
            'trans': entry[col['trans_col']],
            'date': entry[col['date_col']],
            'enter': entry[col['enter_col']],
            'check': entry[col['check_col']],
            'syn': entry[col['syn_col']],
            'ant': entry[col['ant_col']],
            'link': entry[col['link_col']],
            'tag': entry[col['tag_col']],
        }

        processed_data.append(d)
    # pre processing tasks
    for entry in processed_data:
        if entry['sense'] == '':
            entry['sense'] = 1

    logger.info('   -%d dictionary entries read' % len(processed_data))
    return processed_data


def validate_data(processed_data):
    """Check the spreadsheet for incorrectly entered data"""
    check_processed_data(processed_data, 'validate_data()')

    errors = []
    errors.append(validate_find_missing_senses(processed_data))
    if not errors[0]:
        errors = None
    return errors


def validate_find_missing_senses(processed_data):
    """Returns a list (or None if n/a) of phonetic entries that are the same but aren't marked as senses of
    each other. This may reveal data entry errors."""
    words = [item['phon'] for item in processed_data]
    count = Counter(words)
    count = count.items()  # convert to list of tuples (phonetics, number of times counted)
    repeated_phonetics = [item for item in count if item[1] > 1]  # filter out single occurences

    repeated_senses = []
    for entry in repeated_phonetics:
        phonetics = entry[0]
        entries_matching_phonetics = [entry for entry in processed_data if entry['phon'] == phonetics]

        entry_sense_count = Counter([entry['sense'] for entry in entries_matching_phonetics])
        entry_sense_count = entry_sense_count.items()
        repeated_sense = [item for item in entry_sense_count if item[1] > 1]
        if repeated_sense:
            error_msg = '{phonetics} use same sense  number multiple times.'.format(phonetics=phonetics)
            repeated_senses.append(error_msg)

    if repeated_senses:
        logger.info('   -Data validation found repeated senses')
        error = ('Sense number repeated', repeated_senses)
        return error
    else:
        return None


def sort_by_id(processed_data):
    return sorted(processed_data, key=lambda data: data['id'])


def sort_by_tag(processed_data):
    return sorted(processed_data, key=lambda data: data['tag'])


# def sort_phonetically(processed_data):
#     return sorted(processed_data, key=lambda data: data['phon'])
#
#
# def sort_orthographically(processed_data):
#     return sorted(processed_data, key=lambda data: data['orth'])


def sort_by_sense(processed_data):
    return sorted(processed_data, key=lambda data: data['sense'])


# Define some quick asserts to make sure functions are given the correct data model to work on (they are similar)
def check_processed_data(processed_data, function):
    """A quick assert that the right data model is given to function, a list of dictionaries produced by
    read_lexicon()"""
    try:
        assert len(processed_data) > 0, 'No data to work on!'
        assert type(processed_data) == list, \
            'wrong data type given to {function} - needs the result of read_lexicon()'.format(function=function)
        assert type(processed_data[0]) == dict, \
            'wrong data type given to {function} - needs the result of read_lexicon()'.format(function=function)
    except AssertionError:
        logger.exception('Function called incorrectly')
        raise AssertionError


def check_lexicon_entries(lexicon_entries, function):
    """A quick assert that the data model comes from create_lexicon_entries, a list of tuples"""
    try:
        assert len(lexicon_entries) > 0, 'No data to work on!'
        assert type(lexicon_entries) == list, \
            'wrong data type given to {function} - needs the result of create_lexicon_entries()'.format(
                function=function)
        assert type(lexicon_entries[0]) == tuple, \
            'wrong data type given to {function} - needs the result of create_lexicon_entries()'.format(
                function=function)
    except AssertionError:
        logger.exception('Function called incorrectly')
        raise AssertionError


def create_lexicon_entries(processed_data):
    """Takes the data and creates actual dictionary entries that takes account of multiple senses for the same word.
    Returns a list of tuples (headword, list of sense dictionary) sorted alphabetically by headword"""
    check_processed_data(processed_data, 'create_lexicon_entries()')
    processed_data = sort_by_sense(processed_data)  # get the sense numbers in order
    processed_data = sort_by_id(processed_data)
    lexicon_entries = []
    last_id = 0  # blank variable to check if headwords are the same
    lexeme_index = -1  # counter for lexicon_entries
    # Loop through the entries and create the dictionary entries
    for entry in processed_data:
        # choose phonetics for headword if orthography not available
        if entry['orth']:
            headword = entry['orth']
        else:
            headword = entry['phon']
        sense_data = {
            'pos': entry['pos'],
            'phonetics': entry['phon'],
            'english': entry['eng'],
            'tok_pisin': entry['tpi'],
            'definition': entry['def'],
            'example': entry['ex'],
            'example_translation': entry['trans'],
            'sense': entry['sense']
        }

        if last_id == entry['id']:  # this is a sense of the previous headword
            lexicon_entries[lexeme_index][1].append(sense_data)
        else:  # this is a new headword
            lexeme = (headword, [sense_data])
            lexicon_entries.append(lexeme)
            lexeme_index += 1
        last_id = entry['id']
    # sort alphabetically
    lexicon_entries = sorted(lexicon_entries, key=lambda lexeme_tuple: lexeme_tuple[0])
    return lexicon_entries


def create_reverse_lexicon_entries(processed_data):
    """Adjust the processed data so it's suitable to be displayed in an English to Lang dict"""
    check_processed_data(processed_data, 'create_reverse_lexicon_entries()')

    processed_data = sorted(processed_data, key=lambda d: d['eng'].lower())
    lexicon_entries = []
    for item in processed_data:
        if item['orth']:
            item['headword'] = item['orth']
        else:
            item['headword'] = item['phon']
        lexicon_entries.append((item['eng'].lower(), item))
    return lexicon_entries


def get_word_beginnings(lexicon_entries):
    """Takes the tuple (headwords, entry html) and returns an alphabetically sorted set of the first letters of all
     headwords"""
    check_lexicon_entries(lexicon_entries, 'get_word_beginnings()')
    letters = [x[0][0] for x in lexicon_entries]
    return sorted(set(letters))


def assert_templates_exist():
    template_dir = 'templates'
    assert os.path.exists(template_dir), '{dir} is missing'.format(dir=template_dir)
    assert os.path.isdir(template_dir), '{dir} is not a directory'.format(dir=template_dir)

    templates = ['check_template.html', 'dictionary_template.html', 'error_template.html', 'help_template.html']
    partial_templates = ['base.html', 'entry.html', 'header.html', 'reverse_entry.html', 'sidebar.html']

    partial_templates = ['partial/' + x for x in partial_templates]

    templates = templates + partial_templates
    for template in templates:
        template = os.path.join(template_dir, template)
        assert os.path.exists(template), 'Template Error: {template} is missing'.format(template=template)


def generate_html(processed_data):
    """Generate the HTML pages"""
    assert_templates_exist()
    errors = validate_data(processed_data)

    generate_lexicon_page(processed_data, errors)
    generate_Eng_page(processed_data)
    generate_help_page()
    generate_check_page(processed_data)
    logger.info('HTML pages sucessfully generated')
    if errors:
        generate_error_page(errors)
        logger.info('   - an error page has been generated')


def generate_lexicon_page(processed_data, errors):
    """Create suitable headwords for a dictionary and create a dictionary HTML page"""
    check_processed_data(processed_data, 'generate_HTML()')

    # Create the HTML header and navbar
    context = generate_context(title='{language} Lexicon'.format(language=lexicon_config.settings['language']),
                               header='lexicon')

    lexicon_entries = create_lexicon_entries(processed_data)
    initial_letters = get_word_beginnings(lexicon_entries)

    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('dictionary_template.html')

    html = os.path.join(lexicon_config.settings['target_folder'], 'main_dict.html')
    with open(html, 'w') as file:
        print(template.render(context=context, entries=lexicon_entries, errors=errors, letters=initial_letters),
              file=file)


def generate_error_page(errors):
    """Creates a page that shows all the validation errors discovered in the spreadsheet"""

    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('error_template.html')

    context = generate_context(title='Data errors'.format(language=lexicon_config.settings['language']),
                               header='errors')

    with open('errors.html', 'w') as file:
        print(template.render(context=context, errors=errors), file=file)


def generate_Eng_page(processed_data):
    """Creates a English to language lookup version of dictionary as html"""
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('dictionary_template.html')

    # Create the HTML header and navbar
    context = generate_context(title='{language} Lexicon'.format(language=lexicon_config.settings['language']),
                               header='reverse')
    context['dict_type'] = 'reverse'

    lexicon_entries = create_reverse_lexicon_entries(processed_data)
    initial_letters = get_word_beginnings(lexicon_entries)

    html = os.path.join(lexicon_config.settings['target_folder'], 'reverse_dict.html')
    with open(html, 'w') as file:
        print(template.render(context=context, entries=lexicon_entries, letters=initial_letters), file=file)


def generate_check_page(processed_data):
    """Creates a page that shows all the phonetics that need to be checked. The HTML is sparse and is designed
    for printing."""
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('check_template.html')

    # filter out and return only unchecked entries
    words_to_check = [word for word in processed_data if not word['check']]
    # use a list to represent brand new entries, and one for new senses
    new_senses = [word for word in words_to_check if word['sense'] > 1]
    new_entries = [word for word in words_to_check if word['sense'] == 1]
    # order by tag for more structured language checking session
    new_entries = sort_by_tag(new_entries)
    new_senses = sort_by_tag(new_senses)
    logger.info('   -{words_to_check} words need checking'.format(words_to_check=len(words_to_check)))

    context = generate_context(title='{language} checklist'.format(language=lexicon_config.settings['language']),
                               header='check_list')

    html = os.path.join(lexicon_config.settings['target_folder'], 'check_list.html')
    with open(html, 'w') as file:
        print(template.render(context=context, new_entries=new_entries, new_senses=new_senses), file=file)


def generate_help_page():
    """Creates a help page"""
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('help_template.html')

    context = generate_context(title='Help', header='help')
    html = os.path.join(lexicon_config.settings['target_folder'], 'help.html')
    with open(html, 'w') as file:
        print(template.render(context=context), file=file)


def generate_context(title, header):
    date = datetime.datetime.now().strftime('%A %d %B %Y')
    context = {
        'title': title,
        'date': date,
        'language': lexicon_config.settings['language'],
        'header': header,
        'stylesheets': lexicon_config.settings['stylesheets']
    }

    return context


def create_phonemic_assistant_db(processed_data, checked_only=True):
    """Takes processed data and uses them to produce a .db file that can be read by phonemic assistant.
    Takes a boolean keyword argument 'checked_only' that limits the entries used to those marked as check
    (default=True)"""
    check_processed_data(processed_data, 'create_phonemic_assistant_db()')

    logger.info('Writing phonology assistant file')
    if checked_only:
        processed_data = [data for data in processed_data if data['check']]
        logger.info('   - writing checked words only to phonology assistant file')
        if len(processed_data) == 0:
            raise AssertionError('No checked data to work with!')
    else:
        logger.info('   - writing unchecked words to phonology assistant file')

    pa_db = '﻿\_sh v3.0  400  PhoneticData\n'

    for i, item in enumerate(processed_data, 1):
        item['ref'] = '{:03d}'.format(i)  # format ref as 001, 002 etc
        entry = '''
\\ref {ref}
\\ge {eng}
\\gn {tpi}
\\ph {phon}
\\ps {pos}\n'''.format(**item)  # use the dict from read_lexicon()

        pa_db += entry

    db = (os.path.join(lexicon_config.settings['target_folder'],
                       '{language}_phonology_assistant.db'.format(language=lexicon_config.settings['language'])))
    with open(db, 'w') as file:
        print(pa_db, file=file)

    logger.info('   - {n} words written to phonology assistant file'.format(n=len(processed_data)))


logger = initiate_logging()
if __name__ == '__main__':
    sys.excepthook = excepthook

    data = read_lexicon()
    generate_html(data)
    create_phonemic_assistant_db(data, checked_only=False)

