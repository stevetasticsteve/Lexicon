import unittest
import logging
logging.disable(logging.CRITICAL)

import lexicon
import tests.TestSettings as test_settings


class MiscTests(unittest.TestCase):
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


class ReadLexiconTests(unittest.TestCase):
    def setUp(self):
        self.data = lexicon.read_lexicon(config_file=test_settings)

    def test_read_lexicon_return_type(self):
        self.assertEqual(type(self.data), list, 'Wrong data type returned')
        self.assertEqual(type(self.data[0]), dict, 'Wrong data type returned')

    def test_read_lexicon_all_rows_read(self):
        self.assertEqual(len(self.data), 5, 'Number of rows read not correct')

    def test_read_lexicon_xlsx(self):
        self.fail('Finish the test')

    def test_read_lexicon_xls(self):
        self.fail('Finish the test')

    def test_read_lexicon_ods(self):
        self.fail('Finish the test')

    def test_read_lexicon_incorrect_file_format(self):
        self.fail('Finish the test')

    def test_read_lexicon_file_not_found(self):
        self.fail('Finish the test')

    def test_read_lexicon_blank_file(self):
        self.fail('Finish the test')

    def test_read_lexicon_blank_rows(self):
        # @ start
        # @ middle
        # @ end
        self.fail('Finish the test')

    def test_read_lexicon_header_row_missing(self):
        self.fail('Finish the test')

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


class ValidationTestRunner(unittest.TestCase):
    """validate_data() is a simple caller to run all the validation tests that should assert data provided is suitable
    and clean up the return if there are no errors"""
    def test_validate_data_return_type(self):
        """Function should return a list of error tuples ('error', 'data') or None"""
        self.fail('Finish the test')

    def test_validate_data_incorrect_data_input_response(self):
        """Function should raise an assertion error if processed data isn't provided"""
        self.fail('Finish the test')


class ValidateSenseNumbers(unittest.TestCase):
    def test_validate_find_missing_senses_return_type(self):
        """Function should return list of tuples ('Sense number repeated', 'data') or None"""
        self.fail('Finish the test')

    def test_validate_find_missing_senses_return_contents(self):
        self.fail('Finish the test')


if __name__ == '__main__':
    unittest.main()
