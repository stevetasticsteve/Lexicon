#!/usr/bin/python3
import pyexcel_ods3
import datetime
import os
import socket
import logging
import lexicon_config as s

from jinja2 import Environment, FileSystemLoader

def initiate_logging():
    # Initiate error logging
    logger = logging.getLogger('LexiconLog')
    logger.setLevel(logging.DEBUG)

    # If working on Steve's laptop change source and target for dev work
    if socket.gethostname() == 'steve-stanley-latitude':
        s.settings['spreadsheet_name'] = 'Kovol_lexicon.ods'
        # s.settings['spreadsheet_name'] = 'excel_test.xlsx'
        s.settings['target_folder'] = ''
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(message)s')
        ch.setFormatter(formatter)
        ch.setLevel(logging.DEBUG)
        logger.addHandler(ch)
        logger.info('Logging to stream')
    else:
        fh = logging.FileHandler('Lexicon_error.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        fh.setLevel(logging.ERROR)
        logger.addHandler(fh)
    return logger


def letter_to_number(letter):
    # returns an integer to use as an index for a given column letter
    return ord(letter.upper()) - 65


def read_lexicon():
    """Reads the .ods and returns a list of dictionary items representing the lexicon,
    unlike create_lexicon_entries() it doesn't group senses under 1 headword - it's just a data dump."""
    spreadsheet = s.settings['spreadsheet_name']
    assert os.path.exists(spreadsheet), '{spreadsheet} does not exist'.format(spreadsheet=spreadsheet)
    _, extension = os.path.splitext(spreadsheet)
    valid_extensions = ('.ods', '.xls', '.xlsx')
    assert any(ex == extension for ex in valid_extensions),  \
        'Invalid file {extension}, must be .ods, .xls or .xlsx'.format(extension=extension)

    # Convert column letters to list integers
    col = {k: letter_to_number(v) for k, v in s.spreadsheet_config.items()}
    assert len(col) == 17, '17 Columns expected, %d found' % len(col)

    # Read the lexicon and return a list of (Python) dictionary entries
    raw_data = pyexcel_ods3.get_data(spreadsheet)['Sheet1']
    raw_data.pop(0)  # get rid of the first row
    raw_data = [x for x in raw_data if x != []]  # get rid of blank rows at the end
    raw_data.sort(key=lambda raw_data: raw_data[col['id_col']])  # sort by ID number
    processed_data = []

    for entry in raw_data:
        while len(entry) < 17:  # add blank columns to avoid index errors
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
            'link': entry[col['link_col']]
        }

        processed_data.append(d)
    # pre processing tasks
    for entry in processed_data:
        if entry['sense'] == '':
            entry['sense'] = 1

    logger.info('%d dictionary entries read' % len(processed_data))
    return processed_data


def sort_by_id(processed_data):
    return sorted(processed_data, key=lambda data: data['id'])


def sort_phonetically(processed_data):
    return sorted(processed_data, key=lambda data: data['phon'])


def sort_orthographically(processed_data):
    return sorted(processed_data, key=lambda data: data['orth'])


def sort_by_sense(processed_data):
    return sorted(processed_data, key=lambda data: data['sense'])


# def generate_help_page():
#     html_header = HTML_header('%s Lexicon help' % s.settings['language'])
#     body = '<h1>HELP PAGE</h1>'
#     html_close = '</div></body></html>'
#     with open(os.path.join(s.settings['target_folder'], 'Lexicon_help.html'), 'w') as file:
#         print(html_header, body, html_close, file=file)


def create_lexicon_entries(processed_data):
    """Takes the data and creates actual dictionary entries that takes account of multiple senses for the same word.
    Returns a tuple (headword, list of sense dictionary) sorted alphabetically by headword"""
    processed_data = sort_by_sense(processed_data) # get the sense numbers in order
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

        if last_id == entry['id']: # this is a sense of the previous headword
            lexicon_entries[lexeme_index][1].append(sense_data)
        else: # this is a new headword
            lexeme = (headword, [sense_data])
            lexicon_entries.append(lexeme)
            lexeme_index += 1
        last_id = entry['id']
    # sort alphabetically
    lexicon_entries = sorted(lexicon_entries, key=lambda lexeme_tuple: lexeme_tuple[0])
    return lexicon_entries


def get_word_beginings(lexicon_entries):
    """Takes the tuple (headwords, entry html) and returns an alphabetically sorted set of the first letters of all
     headwords"""
    letters = [x[0][0] for x in lexicon_entries]
    return sorted(set(letters))


def generate_HTML():
    # Create the HTML header and navbar
    date = datetime.datetime.now().strftime('%A %d %B %Y')
    context = {
        'language': s.settings['language'],
        'date': date
    }

    data = read_lexicon()
    lexicon_entries = create_lexicon_entries(data)
    initial_letters = get_word_beginings(lexicon_entries)


    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('lang-Eng.html')

    with open(os.path.join(s.settings['target_folder'], '%s_Lexicon.html') % s.settings['language'], 'w') as file:
        print(template.render(context=context, entries=lexicon_entries), file=file)
    # generate_help_page()

def create_phonemic_assistant_db(processed_data, checked_only =True):
    """Takes processed data and uses them to produce a .db file that can be read by phonemic assistant.
    Takes a boolean keyword argument 'checked_only' that limits the entries used to those marked as check
    (default=True)"""
    pa_db = '﻿\_sh v3.0  400  PhoneticData\n'

    # for item in processed_data:
        # pa_db += pass

logger = initiate_logging()
if __name__ == '__main__':
    # logger = initiate_logging()
    generate_HTML()
