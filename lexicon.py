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
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # If working on Steve's laptop change source and target for dev work
    if socket.gethostname() == 'steve-stanley-latitude':
        s.settings['spreadsheet_name'] = 'Kovol_lexicon.ods'
        s.settings['target_folder'] = ''
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        ch.setLevel(logging.DEBUG)
        logger.addHandler(ch)
        logger.info('Logging to stream')
    else:
        fh = logging.FileHandler('Lexicon_error.log')
        fh.setFormatter(formatter)
        fh.setLevel(logging.ERROR)
        logger.addHandler(fh)


def letter_to_number(letter):
    # returns an integer to use as an index for a given column letter
    return ord(letter.upper()) - 65


def read_lexicon():
    # Convert column letters to list integers
    col = {k: letter_to_number(v) for k, v in s.spreadsheet_config.items()}
    # Read the lexicon and return a list of (Python) dictionary entries
    raw_data = pyexcel_ods3.get_data(s.settings['spreadsheet_name'])['Sheet1']
    raw_data.pop(0)  # get rid of the first row
    raw_data = [x for x in raw_data if x != []]  # get rid of blank rows at the end
    raw_data.sort(key=lambda raw_data: raw_data[col['id_col']])  # sort by ID number
    data = []

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

        data.append(d)
    if s.settings['sort'] == 'orthography':
        data.sort(key=lambda data: data['orth'])  # sort alphabetically by orthography
    else:
        data.sort(key=lambda data: data['phon'])  # sort alphabetically by phonetics
    return data


def generate_HTML():
    data = read_lexicon()
    # order by id number so the for loop sees all the senses of a word one after another
    data.sort(key=lambda data: data['id'])

    # Create the HTML header and navbar
    date = datetime.datetime.now().strftime('%A %d %B %Y')
    html_header = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta lang="en-US">
        <meta charset="UTF-8">
        <meta name="author" content="New Tribes Mission">
        <title>%s Lexicon</title>
        <link rel="stylesheet" type="text/css" href="bootstrap/css/bootstrap.min.css">
        <script src="bootstrap/js/bootstrap.min.js"></script>
        </head>''' % s.settings['language']

    btn_group = '''<div class="btn-group" role="group" aria-label="Basic example">
                    <button type="button" class="btn btn-light">{0} - English</button>
                    <button type="button" class="btn btn-dark">English - {0}</button>
                    </div>'''.format(s.settings['language'])
    body = '''
    <body>
    <div class="container-fluid p-3 mb-2 bg-info text-white">
    <h1>%s Lexicon</h1> <div class="container-fluid float-right">%s</div> 
    <p>Updated %s </p>
    </div>
    <div class="container-fluid" id="entries_pane">''' % (s.settings['language'], btn_group, date)

    # Loop throgh the entries and create the dictionary entries
    last_id = 0
    for entry in data:
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
        <strong><em style="color:dodgerblue"> %s</em></strong>, <strong style="color:gray">%s</strong> : %s</p>
        ''' % (sense, entry['pos'], entry['phon'], entry['eng'], entry['tpi'], entry['def'])
        lex2 = '''
        <p>%s</p>
        <p>%s</p>
        </div>
        ''' % (entry['ex'], entry['trans'])
        lex_body = lex1 + lex2

        # If the entry is a sense of the previous iteration add the sense without a repeated header
        if entry['id'] == last_id:
            lex_entry = lex_body
        else:
            lex_entry = lex_heading + lex_body
        last_id = entry['id']  # update previous id for this check

        body += lex_entry  # add the entry to the HTML body

    # HTML closing tags
    html_close = '''
        </div>
        </body>
    </html>'''

    # Write the document by joining header, body and close
    with open(os.path.join(s.settings['target_folder'], '%s_Lexicon.html') % s.settings['language'], 'w') as file:
        print(html_header, body, html_close, file=file)


if __name__ == '__main__':
    initiate_logging()
    generate_HTML()
