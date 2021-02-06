import datetime
import unittest
from unittest.mock import patch

import tests.fixtures
from application_code import read_data


class ReadLexiconTests(unittest.TestCase):
    """Test the code that reads the spreadsheet"""

    def test_read_lexicon_return_type(self):
        # test also proves that .ods is being read
        data = read_data.read_lexicon(config_file=tests.fixtures)

        self.assertEqual(type(data), list, 'Wrong data type returned')
        self.assertEqual(type(data[0]), dict, 'Wrong data type returned')

    def test_read_lexicon_all_rows_read(self):
        data = read_data.read_lexicon(config_file=tests.fixtures)
        self.assertEqual(len(data), 5, 'Number of rows read not correct')

    def test_read_lexicon_xlsx(self):
        with patch("tests.fixtures.settings", tests.fixtures.xlsx):
            data = read_data.read_lexicon(config_file=tests.fixtures)
        self.assertEqual(type(data), list, 'Wrong data type returned, xlsx not read')
        self.assertEqual(5, len(data), 'Number of rows read not correct in xlsx')

    def test_read_lexicon_xls(self):
        with patch("tests.fixtures.settings", tests.fixtures.xls):
            data = read_data.read_lexicon(config_file=tests.fixtures)

        self.assertEqual(type(data), list, 'Wrong data type returned, xls not read')
        self.assertEqual(len(data), 5, 'Number of rows read not correct in xls')

    def test_read_lexicon_incorrect_file_format(self):
        error_msg = 'is not a valid file extension. Must be .ods, .xls or .xlsx.'
        with patch("tests.fixtures.settings", tests.fixtures.bad_ext1):
            with self.assertRaises(TypeError) as error:
                read_data.read_lexicon(config_file=tests.fixtures)
            self.assertIn(error_msg, str(error.exception))

        with patch("tests.fixtures.settings", tests.fixtures.bad_ext2):
            with self.assertRaises(TypeError) as error:
                read_data.read_lexicon(config_file=tests.fixtures)
            self.assertIn(error_msg, str(error.exception))

    def test_read_lexicon_file_not_found(self):
        with patch("tests.fixtures.settings", tests.fixtures.no_spreadsheet):
            with self.assertRaises(FileNotFoundError) as error:
                read_data.read_lexicon(config_file=tests.fixtures)
            self.assertIn('The following file doesn\'t exist', str(error.exception))

    def test_read_lexicon_blank_file(self):
        with patch('tests.fixtures.settings', tests.fixtures.blank_sheet):
            print(tests.fixtures.settings)
            with self.assertRaises(AttributeError) as error:
                read_data.read_lexicon(config_file=tests.fixtures)
            self.assertIn('The file is blank', str(error.exception))

    def test_read_lexicon_blank_rows(self):
        with patch("tests.fixtures.settings", tests.fixtures.blank_rows):
            data = read_data.read_lexicon(config_file=tests.fixtures)
            self.assertEqual(5, len(data), 'Blank rows included in return')
            self.assertEqual('undum', data[0]['phon'], 'First row incorrect')
            self.assertEqual('limoŋ', data[4]['phon'], 'Last row incorrect')

    def test_read_lexicon_header_row_missing(self):
        with patch("tests.fixtures.settings", tests.fixtures.no_header):
            data = read_data.read_lexicon(config_file=tests.fixtures)

            self.assertEqual(5, len(data), 'All rows not read when header is missing')
            self.assertEqual('undum', data[0]['phon'], 'First row is incorrect')

    def test_read_lexicon_row_contents(self):
        data = read_data.read_lexicon(config_file=tests.fixtures)
        self.assertEqual(data[0], {'ant': '',
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
                                   'tag': 'test'}, 'First row not as expected')

    def test_read_lexicon_settings_column_undefined(self):
        with patch("tests.fixtures.spreadsheet_config", {'id_col': 'A'}):
            with self.assertRaises(AssertionError) as error:
                read_data.read_lexicon(config_file=tests.fixtures)
            self.assertIn('items expected in spreadsheet_config,', str(error.exception))

    def test_read_lexicon_sheet_name_unexpected(self):
        with patch("tests.fixtures.settings", tests.fixtures.no_sheet):
            with self.assertRaises(KeyError) as error:
                read_data.read_lexicon(config_file=tests.fixtures)
            self.assertIn('is not a valid sheet name.', str(error.exception))

    def test_read_lexicon_mostly_empty_row(self):
        """Test to catch rows that don't include essential information"""
        with patch("tests.fixtures.settings", tests.fixtures.mostly_empty):
            data = read_data.read_lexicon(config_file=tests.fixtures)
            self.assertEqual(len(data), 5, 'A mostly blank row has been read in')

    def test_read_lexicon_blank_cell_response(self):
        """Tests every column for response to blank"""
        with patch("tests.fixtures.settings", tests.fixtures.missing_cells):
            data = read_data.read_lexicon(config_file=tests.fixtures)
            self.assertEqual(len(data), 6, 'Incorrect number of rows read')
            # missing ID - should recieve an ID of 0
            self.assertEqual(0, data[0]['id'], 'ID incorrect on blank cell')
            # missing phonetics - return ''
            self.assertEqual('', data[5]['phon'], "Blank phonetics not returning correctly")
            # missing sense - return 1
            self.assertEqual(1, data[5]['sense'], "Blank sense not returning correctly")
            # missing POS - return ''
            self.assertEqual('', data[4]['pos'], "Blank POS not returning correctly")
            # missing English - return ''
            self.assertEqual('', data[1]['eng'], "Blank English not returning correctly")
            # missing Tok Pisin - return ''
            self.assertEqual('', data[1]['tpi'], "Blank Tok pisin not returning correctly")
            # missing definition - return ''
            self.assertEqual('', data[1]['def'], "Blank definition not returning correctly")
            # missing example - return ''
            self.assertEqual('', data[1]['ex'], "Blank example not returning correctly")
            # missing translation - return ''
            self.assertEqual('', data[1]['trans'], "Blank example translation not returning correctly")
            # missing date - return ''
            self.assertEqual('', data[1]['date'])
            # missing entered - return ''
            self.assertEqual('', data[1]['enter'], "Blank entered by not returning correctly")
            # missing check, syn, ant, see also, tag - return ''
            self.assertEqual('', data[1]['syn'], "Blank synonym not returning correctly")
            self.assertEqual('', data[1]['ant'], "Blank antonym not returning correctly")
            self.assertEqual('', data[1]['check'], "Blank check not returning correctly")
            self.assertEqual('', data[1]['link'], "Blank see also not returning correctly")
            self.assertEqual('', data[1]['tag'], "Blank tag not returning correctly")

    def test_read_lexicon_no_blank_senses_in_return(self):
        data = read_data.read_lexicon(config_file=tests.fixtures)
        for row in data:
            self.assertIsNot(row['sense'], '', 'Blank sense numbers are in the return value')
            self.assertIs(int, type(row['sense']), 'Sense number for row isn\'t an integer')

    def test_read_lexicon_no_blank_id_in_return(self):
        def check_ids(d):
            for row in d:
                self.assertIsNot(row['id'], '', 'Blank ID numbers are in the return value')
                self.assertIs(int, type(row['id']), 'ID number for row isn\'t an integer')

        data = read_data.read_lexicon(config_file=tests.fixtures)
        check_ids(data)
        self.assertEqual(1, data[0]['id'], 'First id number incorrect')

        with patch("tests.fixtures.settings", tests.fixtures.missing_cells):
            data = read_data.read_lexicon(config_file=tests.fixtures)
            check_ids(data)
            self.assertEqual(0, data[0]['id'], 'First id number incorrect')

    def test_read_lexicon_data_not_as_expected(self):
        """Tests each column for data of unexpected type. Data validation on the spreadsheet stops a lot of nonsense"""
        with patch("tests.fixtures.settings", tests.fixtures.dodgy_data):
            data = read_data.read_lexicon(config_file=tests.fixtures)
            for k, v in data[0].items():
                if k == 'id':
                    self.assertEqual(type(v), int, 'value for {k} is not a int'.format(k=k))
                elif k == 'sense':
                    self.assertEqual(type(v), int, 'value for {k} is not a int'.format(k=k))
                elif k == 'date':
                    self.assertEqual(type(v), datetime.date, 'value for {k} is not a datetime'.format(k=k))
                else:
                    self.assertEqual(type(v), str, 'value for {k} is not a string'.format(k=k))


class SupportingFunctionsTests(unittest.TestCase):
    """Tests the functions supporting read_lexicon()"""

    def test_check_config(self):
        settings = {
            'language': 1,
            'spreadsheet_name': 'tests/test_data/good_data.ods',  # the abs path to the spreadsheet used as a data source
            'sheet_name': 'Sheet1',  # Name of the sheet containing data
            'target_folder': 'tests/',  # the folder the web page should be created in,
            'log_file': 'tests/test_log',  # path for the log file
            'sort': 'phonetics',  # order dictionary by 'phonetics' or 'orthography'
        }

        with self.assertRaises(TypeError) as error:
            read_data.check_settings(config_file=settings)
        self.assertIn('The language is not a string', str(error.exception))

        settings['language'] = 'Test'
        settings['target_folder'] = 'Fake directory'
        with self.assertRaises(FileNotFoundError)as error:
            read_data.check_settings(config_file=settings)
        self.assertIn('The following file doesn\'t exist: {t}'.format(t=settings['target_folder']),
                      str(error.exception), 'Error message wrong')

    def test_letter_to_number(self):
        # valid input
        self.assertEqual(read_data.letter_to_number('A'), 0, 'Letter to number giving wrong output')
        self.assertEqual(read_data.letter_to_number('B'), 1, 'Letter to number giving wrong output')
        self.assertEqual(read_data.letter_to_number('a'), 0, 'Letter to number giving wrong output')
        self.assertEqual(read_data.letter_to_number('Z'), 25, 'Letter to number giving wrong output')
        # invalid input
        with self.assertRaises(AssertionError):
            read_data.letter_to_number(1)
        with self.assertRaises(AssertionError):
            read_data.letter_to_number('AA')
        with self.assertRaises(AssertionError):
            read_data.letter_to_number('1')
        with self.assertRaises(AssertionError):
            read_data.letter_to_number('')
        with self.assertRaises(AssertionError):
            read_data.letter_to_number(' ')
