#!/usr/bin/python3
import pyexcel_ods3
import datetime
import os
import socket
import logging


class Lexicon:
    def __init__(self):
        self.hostname = socket.gethostname()
        self.settings = {
            'language': 'Kovol',
            'spreadsheet_name': '/media/NAS/Team Share/Kovol_lexicon.ods',
            'target_folder': '/media/NAS/CLAHub/other_sites/Lexicon',                 # the folder the web page should be created in
            'sort': 'phonetics',                             # order dictionary by 'phonetics' or 'orthography'
            'id_col': self.letter_to_number('A'),            # Column containing id number
            'orth_col': self.letter_to_number('B'),          # Column containing orthographic text
            'phon_col': self.letter_to_number('C'),          # Column containing phonetics
            'dial_col': self.letter_to_number('D'),          # Column containing dialect varient phonetics
            'sense_col': self.letter_to_number('E'),         # Column containing sense number
            'pos_col': self.letter_to_number('F'),           # Column containing part of speech
            'eng_col': self.letter_to_number('G'),           # Column containing English translation
            'tpi_col': self.letter_to_number('H'),           # Column containing Tok Pisin translation
            'def_col': self.letter_to_number('I'),           # Column containing a definition
            'ex_col': self.letter_to_number('J'),            # Column containing example(s)
            'trans_col': self.letter_to_number('K'),         # Column containing example translation
            'date_col': self.letter_to_number('L'),          # Column containing entry date
            'enter_col': self.letter_to_number('M'),         # Column containing team member who entered data
            'check_col': self.letter_to_number('N'),         # Column containing team member who checked
            'syn_col': self.letter_to_number('O'),           # Column containing synonyms
            'ant_col': self.letter_to_number('P'),           # Column containing antonyms
            'link_col': self.letter_to_number('Q'),           # Column containing links
        }

        # Initiate error logging
        self.logger = logging.getLogger('LexiconLog')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        
        # If working on Steve's laptop change source and target for dev work
        if self.hostname == 'steve-stanley-latitude':
            self.settings['spreadsheet_name'] = 'Kovol_lexicon.ods'
            self.settings['target_folder'] = ''
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            ch.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)
            self.logger.info('Logging to stream')
        else:
            fh = logging.FileHandler('Lexicon_error.log')
            fh.setFormatter(formatter)
            fh.setLevel(logging.ERROR)
            self.logger.addHandler(fh)



    def letter_to_number(self, letter):
        # returns an integer to use as an index for a given column letter
        return ord(letter.upper()) - 65

    def read_lexicon(self):
        # Read the lexicon and return a list of (Python) dictionary entries
        raw_data = pyexcel_ods3.get_data(self.settings['spreadsheet_name'])['Sheet1']
        raw_data.pop(0) # get rid of the first row
        raw_data = [x for x in raw_data if x != []] # get rid of blank rows at the end
        raw_data.sort(key=lambda raw_data: raw_data[self.settings['id_col']]) # sort by ID number
        data = []

        for entry in raw_data:
            while len(entry) < 17: # add blank columns to avoid index errors
                entry.append('')
            d = {
                'id': entry[self.settings['id_col']],
                'orth': entry[self.settings['orth_col']],
                'phon': entry[self.settings['phon_col']],
                'dial': entry[self.settings['dial_col']],
                'sense': entry[self.settings['sense_col']],
                'pos': entry[self.settings['pos_col']],
                'eng': entry[self.settings['eng_col']],
                'tpi': entry[self.settings['tpi_col']],
                'def': entry[self.settings['def_col']],
                'ex': entry[self.settings['ex_col']],
                'trans': entry[self.settings['trans_col']],
                'date': entry[self.settings['date_col']],
                'enter': entry[self.settings['enter_col']],
                'check': entry[self.settings['check_col']],
                'syn': entry[self.settings['syn_col']],
                'ant': entry[self.settings['ant_col']],
                'link': entry[self.settings['link_col']]
            }

            data.append(d)
        if self.settings['sort'] == 'orthography':
            data.sort(key=lambda data: data['orth']) # sort alphabetically by orthography
        else:
            data.sort(key=lambda data: data['phon']) # sort alphabetically by phonetics
        return data

    def generate_HTML(self):
        data = self.read_lexicon()
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
            </head>''' % self.settings['language']

        btn_group = '''<div class="btn-group" role="group" aria-label="Basic example">
                        <button type="button" class="btn btn-light">{0} - English</button>
                        <button type="button" class="btn btn-dark">English - {0}</button>
                        </div>'''.format(self.settings['language'])
        body = '''
        <body>
        <div class="container-fluid p-3 mb-2 bg-info text-white">
        <h1>%s Lexicon</h1> <div class="container-fluid float-right">%s</div> 
        <p>Updated %s </p>
        </div>
        <div class="container-fluid" id="entries_pane">''' % (self.settings['language'], btn_group, date)

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
            last_id = entry['id'] # update previous id for this check

            body += lex_entry # add the entry to the HTML body

        # HTML closing tags
        html_close = '''
            </div>
            </body>
        </html>'''

        # Write the document by joining header, body and close
        with open(os.path.join(self.settings['target_folder'], '%s_Lexicon.html') % self.settings['language'], 'w') as file:
            print(html_header, body, html_close, file=file)

if __name__ == '__main__':
    L = Lexicon()
    L.generate_HTML()