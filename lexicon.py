#!/usr/bin/python3
import pyexcel_ods3
import datetime
import os
import socket
import logging
import lexicon_config as s


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
    """Reads the .ods and returns a list of dictionary items representing the lexicon"""
    # Convert column letters to list integers
    col = {k: letter_to_number(v) for k, v in s.spreadsheet_config.items()}
    # Read the lexicon and return a list of (Python) dictionary entries
    raw_data = pyexcel_ods3.get_data(s.settings['spreadsheet_name'])['Sheet1']
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


def HTML_header(title):
    html_header = '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta lang="en-US">
            <meta charset="UTF-8">
            <meta name="author" content="New Tribes Mission">
            <title>%s</title>
            <link rel="stylesheet" type="text/css" href="bootstrap/css/bootstrap.min.css">
            <script src="bootstrap/js/bootstrap.min.js"></script>
            </head>''' % title
    return html_header


def generate_help_page():
    html_header = HTML_header('%s Lexicon help' % s.settings['language'])
    body = '<h1>HELP PAGE</h1>'
    html_close = '</div></body></html>'
    with open(os.path.join(s.settings['target_folder'], 'Lexicon_help.html'), 'w') as file:
        print(html_header, body, html_close, file=file)


def create_headwords_HTML(processed_data):
    '''Takes the data and creates actual dictionary entries that takes account of multiple senses for the same word.
    Returns a tuple (headword, html for entry) sorted alphabetically by headword'''
    processed_data = sort_by_sense(processed_data) # get the sense numbers in order
    processed_data = sort_by_id(processed_data)
    lexicon_entries = []
    # Loop throgh the entries and create the dictionary entries
    last_id = 0
    for entry in processed_data:
        # choose phonetics for headword if orthography not available
        if entry['orth']:
            headword = entry['orth']
        else:
            headword = entry['phon']
        # get which sense of the word
        if entry['sense']:
            sense = str(entry['sense']) + '.'
        else:
            sense = '1.'

        lex_heading = '''
            <div class="lexeme">
            <h3>%s</h3>''' % headword
        # pos [phonetics] english, tpi : definition
        lex1 = '''
            <p>%s <strong>%s</strong> [%s]
            <strong><em style="color:dodgerblue"> %s</em></strong>, <strong style="color:gray">%s</strong>''' \
               % (sense, entry['pos'], entry['phon'], entry['eng'], entry['tpi'])
        if entry['def']:
            definition = ': %s</p>' % entry['def']
        else:
            definition = '</p>'
        if entry['ex']:
            examples = '''<dl class="row">
                <dt class="col-sm-1">%s</dt>
                <dd class="col-sm-1">%s</dd>
                </dl>
                ''' % (entry['ex'], entry['trans'])
        else:
            examples = ''
        lex_body = lex1 + definition + examples

        # If the entry is a sense of the previous iteration add the sense without a repeated header
        if entry['id'] == last_id:
            lex_entry = lex_body
        else:
            lex_entry = lex_heading + lex_body
        last_id = entry['id']  # update previous id for this check

        # create a tuple of the entry so it can be sorted by headword
        lexicon_entries.append((headword, lex_entry))
    lexicon_entries.sort()
    return lexicon_entries


def get_word_beginings(lexicon_entries):
    '''Takes the tuple (headwords, entry html) and returns an alphabetically sorted set of the first letters of all
     headwords'''
    letters = [x[0][0] for x in lexicon_entries]
    return sorted(set(letters))

def generate_HTML():
    # Create the HTML header and navbar
    date = datetime.datetime.now().strftime('%A %d %B %Y')
    html_header = HTML_header('%s Lexicon' % s.settings['language'])

    btn_group = '''<div class="btn-group" role="group" aria-label="Basic example">
                    <button type="button" class="btn btn-light">{0} - English</button>
                    <button type="button" class="btn btn-dark">English - {0}</button>
                    </div>'''.format(s.settings['language'])
    navbar = '''
    <body>
    <div class="container-fluid p-3 mb-2 bg-info text-white">
    <h1>%s Lexicon</h1> <div class="container-fluid float-right">%s 
    <a href="Lexicon_help.html" button type="button" class="btn btn-light">Help</a> </div>
    <p>Updated %s </p>
    </div>''' % (s.settings['language'], btn_group, date)

    data = read_lexicon()
    lexicon_entries = create_headwords_HTML(data)
    initial_letters = get_word_beginings(lexicon_entries)

    main_div = '''<div class="container-fluid" id="main_body">
    <div class="row">'''
    side_bar = '''<div class=col-sm-1>''' % initial_letters
    for letter in initial_letters:
        side_bar += '''<ul>%s</ul>''' % letter
    side_bar += '</div>'
    entries_pane ='''<div class=col-sm-11>'''

    # build the body of lexicon entries
    for entry in lexicon_entries:
        entries_pane += entry[1]
    entries_pane += '</div>'
    # HTML closing tags
    html_close = '</div></body></html>'

    body = main_div + side_bar + entries_pane + '</div>'

    # Write the document by joining header, body and close
    with open(os.path.join(s.settings['target_folder'], '%s_Lexicon.html') % s.settings['language'], 'w') as file:
        print(html_header, navbar, body, html_close, file=file)
    generate_help_page()


if __name__ == '__main__':
    logger = initiate_logging()
    generate_HTML()
