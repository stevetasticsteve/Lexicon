# This file contains functions that output data by calling on functions in process_data. This is the
# third and final layer. HTML pages and Phonology assistant databases can be produced

import csv
import datetime
import logging
import os

from jinja2 import Environment, FileSystemLoader

import lexicon_config
from application_code import process_data

logger = logging.getLogger('LexiconLog')


def assert_templates_exist(template_dir='templates'):
    templates = ['check_template.html', 'dictionary_template.html', 'error_template.html', 'help_template.html']
    partial_templates = ['base.html', 'entry.html', 'header.html', 'reverse_entry.html', 'sidebar.html']

    partial_templates = ['partial/' + t for t in partial_templates]
    templates = templates + partial_templates

    try:
        for template in templates:
            template = os.path.join(template_dir, template)
            if not os.path.exists(template):
                raise FileNotFoundError
        return True
    except FileNotFoundError:
        msg = 'Template: "{template}" not found'.format(template=template)
        logger.exception(msg)
        raise FileNotFoundError(msg)


def generate_html(processed_data):
    """Generate the HTML pages"""
    assert_templates_exist()
    errors = process_data.validate_data(processed_data)

    generate_lexicon_page(processed_data, errors)
    generate_eng_page(processed_data)
    generate_help_page()
    generate_check_page(processed_data)
    logger.info('HTML pages sucessfully generated')
    if errors:
        generate_error_page(errors)
        logger.info('   - an error page has been generated')


def generate_lexicon_page(processed_data, errors):
    """Create suitable headwords for a dictionary and create a dictionary HTML page"""
    process_data.check_processed_data(processed_data, 'generate_HTML()')

    # Create the HTML header and navbar
    context = generate_context(title='{language} Lexicon'.format(language=lexicon_config.settings['language']),
                               header='lexicon')

    lexicon_entries = process_data.create_lexicon_entries(processed_data)
    initial_letters = process_data.get_word_beginnings(lexicon_entries)

    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader, autoescape=True)
    template = env.get_template('dictionary_template.html')

    html = os.path.join(lexicon_config.settings['target_folder'], 'main_dict.html')
    with open(html, 'w') as file:
        print(template.render(context=context, entries=lexicon_entries, errors=errors, letters=initial_letters),
              file=file)


def generate_error_page(errors):
    """Creates a page that shows all the validation errors discovered in the spreadsheet"""

    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader, autoescape=True)
    template = env.get_template('error_template.html')

    context = generate_context(title='Data errors', header='errors')
    html = os.path.join(lexicon_config.settings['target_folder'], 'errors.html')

    with open(html, 'w') as file:
        print(template.render(context=context, errors=errors), file=file)


def generate_eng_page(processed_data):
    """Creates a English to language lookup version of dictionary as html"""
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader, autoescape=True)
    template = env.get_template('dictionary_template.html')

    # Create the HTML header and navbar
    context = generate_context(title='{language} Lexicon'.format(language=lexicon_config.settings['language']),
                               header='reverse')
    context['dict_type'] = 'reverse'

    lexicon_entries = process_data.create_reverse_lexicon_entries(processed_data)
    initial_letters = process_data.get_word_beginnings(lexicon_entries)

    html = os.path.join(lexicon_config.settings['target_folder'], 'reverse_dict.html')
    with open(html, 'w') as file:
        print(template.render(context=context, entries=lexicon_entries, letters=initial_letters),
              file=file)


def generate_check_page(processed_data):
    """Creates a page that shows all the phonetics that need to be checked. The HTML is sparse and is designed
    for printing."""
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader, autoescape=True)
    template = env.get_template('check_template.html')

    # filter out and return only unchecked entries
    words_to_check = [word for word in processed_data if not word['check']]
    # use a list to represent brand new entries, and one for new senses
    new_senses = [word for word in words_to_check if word['sense'] > 1]
    new_entries = [word for word in words_to_check if word['sense'] == 1]
    # order by tag for more structured language checking session
    new_entries = process_data.sort_by_tag(new_entries)
    new_senses = process_data.sort_by_tag(new_senses)
    logger.info('   -{words_to_check} words need checking'.format(words_to_check=len(words_to_check)))

    context = generate_context(title='{language} checklist'.format(language=lexicon_config.settings['language']),
                               header='check_list')

    html = os.path.join(lexicon_config.settings['target_folder'], 'check_list.html')
    with open(html, 'w') as file:
        print(template.render(context=context, new_entries=new_entries, new_senses=new_senses), file=file)


def generate_help_page():
    """Creates a help page"""
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader, autoescape=True)
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
    process_data.check_processed_data(processed_data, 'create_phonemic_assistant_db()')

    logger.info('Writing phonology assistant file')
    if checked_only:
        processed_data = [data for data in processed_data if data['check']]
        logger.info('   - writing checked words only to phonology assistant file')
        if len(processed_data) == 0:
            raise AssertionError('No checked data to work with!')
    else:
        logger.info('   - writing unchecked words to phonology assistant file')

    pa_db = '\\_sh v3.0  400  PhoneticData\n'

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


def create_csv(processed_data, *args):
    """Creates a CSV to use as a simple wordlist"""
    logger.info('Writing CSV file')
    csv_path = os.path.join(lexicon_config.settings['target_folder'], 'word_list.csv')

    additional_words = []
    for arg in args:
        for row in arg:
            if row['kovol']:
                word = row['kovol']
            else:
                word = row['phonetic']
            additional_words.append(word)

    with open(csv_path, 'w') as csvfile:
        writer = csv.writer(csvfile)
        for item in processed_data:
            writer.writerow([item['phon']])
        for item in additional_words:
            writer.writerow(item)


