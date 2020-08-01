import datetime

settings = {
    'language': 'Test',
    'spreadsheet_name': 'tests/test_data/good_data.ods',
    'sheet_name': 'header',  # Name of the sheet containing data
    'target_folder': 'test_output',  # the folder the web page should be created in
    'sort': 'phonetics',  # order dictionary by 'phonetics' or 'orthography'
    'stylesheets': '/home/steve/Documents/Computing/Python_projects/Lexicon/stylesheets'
}

spreadsheet_config = {
    'id_col': 'A',  # Column containing id number
    'orth_col': 'B',  # Column containing orthographic text
    'phon_col': 'C',  # Column containing phonetics
    'dial_col': 'D',  # Column containing dialect variant phonetics
    'sense_col': 'E',  # Column containing sense number
    'pos_col': 'F',  # Column containing part of speech
    'eng_col': 'G',  # Column containing English translation
    'tpi_col': 'H',  # Column containing Tok Pisin translation
    'def_col': 'I',  # Column containing a definition
    'ex_col': 'J',  # Column containing example(s)
    'trans_col': 'K',  # Column containing example translation
    'date_col': 'L',  # Column containing entry date
    'enter_col': 'M',  # Column containing team member who entered data
    'check_col': 'N',  # Column containing team member who checked
    'syn_col': 'O',  # Column containing synonyms
    'ant_col': 'P',  # Column containing antonyms
    'link_col': 'Q',  # Column containing links,
    'tag_col': 'R',  # Column containing semantic tags
}

good_processed_data = [{'ant': '',
                        'check': '',
                        'date': datetime.date(2020, 4, 30),
                        'def': 'A small person',
                        'dial': '',
                        'eng': 'child',
                        'enter': 'Steve',
                        'ex': 'ɛŋ undum',
                        'id': 1,
                        'link': '',
                        'orth': '',
                        'phon': 'undum',
                        'pos': 'n',
                        'sense': 1,
                        'syn': '',
                        'tpi': 'pikinini',
                        'trans': 'my child',
                        'tag': 'test'},
                       {'ant': '',
                        'check': '',
                        'date': datetime.date(2020, 5, 1),
                        'def': 'A large person',
                        'dial': '',
                        'eng': 'dad',
                        'enter': 'Steve',
                        'ex': 'ɛŋ inda',
                        'id': 2,
                        'link': '',
                        'orth': '',
                        'phon': 'inda',
                        'pos': 'n',
                        'sense': 1,
                        'syn': '',
                        'tpi': 'papa',
                        'trans': 'my dad',
                        'tag': 'family'},
                       {'ant': '',
                        'check': '',
                        'date': datetime.date(2020, 5, 2),
                        'def': 'Generic name for rat',
                        'dial': '',
                        'eng': 'rat',
                        'enter': 'Steve',
                        'ex': 'om sinasim',
                        'id': 3,
                        'link': '',
                        'orth': '',
                        'phon': 'sinasim',
                        'pos': 'n',
                        'sense': 1,
                        'syn': '',
                        'tpi': 'rat',
                        'trans': 'that is a rat',
                        'tag': 'animal'},
                       {'ant': '',
                        'check': '',
                        'date': datetime.date(2020, 5, 3),
                        'def': 'A sneaky guy',
                        'dial': '',
                        'eng': 'rat',
                        'enter': 'Steve',
                        'ex': '',
                        'id': 3,
                        'link': '',
                        'orth': '',
                        'phon': 'sinasim',
                        'pos': 'n',
                        'sense': 2,
                        'syn': '',
                        'tpi': 'rat',
                        'trans': '',
                        'tag': ''}
                       ]
