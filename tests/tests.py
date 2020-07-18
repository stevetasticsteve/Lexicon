import logging
import unittest
from unittest.mock import patch

logging.disable(logging.CRITICAL)

import lexicon
import tests.fixtures


class MiscTests(unittest.TestCase):
    """Test all the small miscellaneous functions"""
    def test_letter_to_number(self):
        # valid input
        self.assertEqual(lexicon.letter_to_number('A'), 0, 'Letter to number giving wrong output')
        self.assertEqual(lexicon.letter_to_number('B'), 1, 'Letter to number giving wrong output')
        self.assertEqual(lexicon.letter_to_number('a'), 0, 'Letter to number giving wrong output')
        self.assertEqual(lexicon.letter_to_number('Z'), 25, 'Letter to number giving wrong output')
        # invalid input
        with self.assertRaises(AssertionError):
            lexicon.letter_to_number(1)
        with self.assertRaises(AssertionError):
            lexicon.letter_to_number('AA')
        with self.assertRaises(AssertionError):
            lexicon.letter_to_number('1')
        with self.assertRaises(AssertionError):
            lexicon.letter_to_number('')
        with self.assertRaises(AssertionError):
            lexicon.letter_to_number(' ')

    def test_sort_by_id(self):
        self.fail('Finish the test')
        # test case - ID number missing

    def test_sort_by_tag(self):
        self.fail('Finish the test')
        # test case - tag missing

    def test_sort_by_sense(self):
        self.fail('Finish the test')

    def test_check_processed_data(self):
        """Function should raise an assert error if argument isn't in the form of the return value of the
        read_lexicon() function"""
        self.fail('Finish the test')

    def test_check_lexicon_entries(self):
        """Function should raise an assert error if argument isn't in the form of the return value of the
        create_lexicon_entries() function"""
        self.fail('Finish the test')

    def test_get_word_beginnings_all_initial_words_present(self):
        self.fail('Finish the test')

    def test_get_word_beginnings_returns_in_alphabetical_order(self):
        self.fail('Finish the test')

    def test_assert_templates_exist(self):
        self.fail('Finish the test')

    def test_generate_context(self):
        self.fail('Finish the test')


class ReadLexiconTests(unittest.TestCase):
    """Test the code that reads the spreadsheet"""
    def test_read_lexicon_return_type(self):
        # test also proves that .ods is being read
        data = lexicon.read_lexicon(config_file=tests.fixtures)

        self.assertEqual(type(data), list, 'Wrong data type returned')
        self.assertEqual(type(data[0]), dict, 'Wrong data type returned')

    def test_read_lexicon_all_rows_read(self):
        data = lexicon.read_lexicon(config_file=tests.fixtures)
        self.assertEqual(len(data), 5, 'Number of rows read not correct')

    def test_read_lexicon_xlsx(self):
        with patch("tests.fixtures.settings", {'spreadsheet_name': 'tests/test_data/test_data_1.xlsx'}):
            data = lexicon.read_lexicon(config_file=tests.fixtures)
        self.assertEqual(type(data), list, 'Wrong data type returned, xlsx not read')
        self.assertEqual(5, len(data), 'Number of rows read not correct in xlsx')

    def test_read_lexicon_xls(self):
        with patch("tests.fixtures.settings", {'spreadsheet_name': 'tests/test_data/test_data_1.xls'}):
            data = lexicon.read_lexicon(config_file=tests.fixtures)

        self.assertEqual(type(data), list, 'Wrong data type returned, xls not read')
        self.assertEqual(len(data), 5, 'Number of rows read not correct in xls')

    def test_read_lexicon_incorrect_file_format(self):
        with patch("tests.fixtures.settings", {'spreadsheet_name': 'tests/test_data/test_data_1.xl'}):
            with self.assertRaises(AssertionError) as error:
                lexicon.read_lexicon(config_file=tests.fixtures)
            self.assertIn('Invalid file', str(error.exception))

        with patch("tests.fixtures.settings", {'spreadsheet_name': 'tests/test_data/test_data_1.db'}):
            with self.assertRaises(AssertionError) as error:
                lexicon.read_lexicon(config_file=tests.fixtures)
            self.assertIn('Invalid file', str(error.exception))

    def test_read_lexicon_file_not_found(self):
        with patch("tests.fixtures.settings", {'spreadsheet_name': 'tests/test_data/non_existent.ods'}):
            with self.assertRaises(AssertionError) as error:
                lexicon.read_lexicon(config_file=tests.fixtures)
            self.assertIn('does not exist', str(error.exception))

    def test_read_lexicon_blank_file(self):
        with patch("tests.fixtures.settings", {'spreadsheet_name': 'tests/test_data/blank_spreadsheet.ods'}):
            with self.assertRaises(AssertionError) as error:
                lexicon.read_lexicon(config_file=tests.fixtures)
            self.assertIn('That file is blank', str(error.exception))

    def test_read_lexicon_blank_rows(self):
        # @ start
        # @ middle
        # @ end
        self.fail('Finish the test')

    def test_read_lexicon_header_row_missing(self):
        with patch("tests.fixtures.settings", {'spreadsheet_name': 'tests/test_data/header_missing.ods'}):
            data = lexicon.read_lexicon(config_file=tests.fixtures)

            self.assertEqual(5, len(data), 'All rows not read when header is missing')
            self.assertEqual('undum', data[0]['phon'], 'First row is incorrect')

    def test_read_lexicon_row_contents(self):
        self.fail('Finish the test')

    def test_read_lexicon_settings_column_undefined(self):
        self.fail('Finish the test')

    def test_read_lexicon_sheet_name_unexpected(self):
        self.fail('Finish the test')

    def test_read_lexicon_all_entries_have_senses(self):
        self.fail('Finish the test')

    def test_read_lexicon_blank_cell_response(self):
        self.fail('Finish the test')

    def test_read_lexicon_no_blank_senses_in_return(self):
        data = lexicon.read_lexicon(config_file=tests.fixtures)
        for row in data:
            self.assertIsNot(row['sense'], '', 'Blank sense numbers are in the return value')
            self.assertIs(int, type(row['sense']))


class ValidationTests(unittest.TestCase):
    """Test the code that validates the data read from the spreadsheet"""
    def test_validate_data_return_type(self):
        """Function should return a list of error tuples ('error', 'data') or None"""
        self.fail('Finish the test')

    def test_validate_data_incorrect_data_input_response(self):
        """Function should raise an assertion error if processed data isn't provided"""
        self.fail('Finish the test')

    def test_validate_find_missing_senses_return_type(self):
        """Function should return list of tuples ('Sense number repeated', 'data') or None"""
        self.fail('Finish the test')

    def test_validate_find_missing_senses_return_contents(self):
        self.fail('Finish the test')


class DataProcessingTests(unittest.TestCase):
    """Test all the functions that process and reorganise data read from spreadsheet"""
    def test_create_lexicon_entries_return_type(self):
        """Function should return a list of tuples (str, list)"""
        self.fail('Finish the test')

    def test_create_lexicon_entries_return_alphabetical_order(self):
        self.fail('Finish the test')

    def test_create_lexicon_entries_return_contents(self):
        self.fail('Finish the test')

    def test_create_reverse_lexicon_entries_return_type(self):
        """Function should return a list of tuples (str, dict)"""
        self.fail('Finish the test')

    def test_create_reverse_lexicon_entries_return_alphabetical_order(self):
        """Function should sort alphabetically based on tuple[0]"""
        self.fail('Finish the test')

    def test_create_reverse_lexicon_entries_return_contents(self):
        self.fail('Finish the test')

    def test_create_reverse_lexicon_entries_orthography_trumps_phonetics(self):
        """Function should use orthographic text for headword when available"""
        self.fail('Finish the test')


class HTMLGenerationTests(unittest.TestCase):
    """Tests the generation of HTML pages"""
    def test_generate_html(self):
        self.fail('Finish the test')

    def test_generate_lexicon_page_exits(self):
        self.fail('Finish the test')

    def test_generate_lexicon_page_good_html(self):
        self.fail('Finish the test')

    def test_generate_lexicon_page_contents(self):
        self.fail('Finish the test')

    def test_generate_error_page_with_errors(self):
        self.fail('Finish the test')

    def test_generate_error_page_without_errors(self):
        self.fail('Finish the test')

    def test_generate_Eng_page_exits(self):
        self.fail('Finish the test')

    def test_generate_Eng_page_good_html(self):
        self.fail('Finish the test')

    def test_generate_Eng_page_contents(self):
        self.fail('Finish the test')

    def test_generate_check_page_exits(self):
        self.fail('Finish the test')

    def test_generate_check_page_good_html(self):
        self.fail('Finish the test')

    def test_generate_check_page_contents(self):
        self.fail('Finish the test')


class OtherFileGenerationTests(unittest.TestCase):
    def test_create_phonemic_assistant_new_file_exists(self):
        self.fail('Finish the test')

    def test_create_phonemic_assistant_contents(self):
        self.fail('Finish the test')

    def test_create_phonemic_assistant_check_false(self):
        self.fail('Finish the test')


if __name__ == '__main__':
    unittest.main()
