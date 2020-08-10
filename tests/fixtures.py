import copy
import datetime

from application_code.process_data import LexiconEntry

settings = {
    'language': 'Test',
    'spreadsheet_name': 'tests/test_data/good_data.ods',
    'sheet_name': 'header',  # Name of the sheet containing data
    'target_folder': 'tests/test_output/',  # the folder the web page should be created in
    'sort': 'phonetics',  # order dictionary by 'phonetics' or 'orthography'
    'stylesheets': '/home/steve/Documents/Computing/Python_projects/Lexicon/stylesheets',
    'log_file': 'tests/test_log'
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

# Slightly modify the test settings for different tests
bad_data = settings.copy()
bad_data['spreadsheet_name'] = 'tests/test_data/bad_data.ods'

missing_cells = bad_data.copy()
missing_cells['sheet_name'] = 'missing_cells'

blank_sheet = bad_data.copy()
blank_sheet['sheet_name'] = 'blank_sheet'

blank_rows = bad_data.copy()
blank_rows['sheet_name'] = 'blank_rows'

dodgy_data = bad_data.copy()
dodgy_data['sheet_name'] = 'dodgy_data'

no_spreadsheet = settings.copy()
no_spreadsheet['spreadsheet_name'] = 'Made up spreadsheet.ods'

no_header = settings.copy()
no_header['sheet_name'] = 'no_header'

bad_ext1 = settings.copy()
bad_ext1['spreadsheet_name'] = 'tests/test_data/test_data_1.xl'
bad_ext2 = settings.copy()
bad_ext2['spreadsheet_name'] = 'tests/test_data/test_data_1.xl'

xls = settings.copy()
xls['spreadsheet_name'] = 'tests/test_data/test_xls.xls'
xls['sheet_name'] = 'Sheet1'

xlsx = settings.copy()
xlsx['spreadsheet_name'] = 'tests/test_data/test_xlsx.xlsx'
xlsx['sheet_name'] = 'Sheet1'

no_sheet = settings.copy()
no_sheet['sheet_name'] = 'ImaginarySheet'

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
                        'orth': 'undum__',
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

repeated_sense_processed_data = copy.deepcopy(good_processed_data)
repeated_sense_processed_data[3]['sense'] = 1

jumbled_lexicon_entries = [LexiconEntry('x test_word_1', {}), LexiconEntry('Test_word_1', {})]
