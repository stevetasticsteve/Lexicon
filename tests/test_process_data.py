import unittest

from application_code import process_data
from tests import fixtures


class ValidationTests(unittest.TestCase):
    """Test the code that validates the data read from the spreadsheet"""

    def test_validate_data_return_type(self):
        """Function should return a list of error tuples ('error', 'data') or None"""
        rtn = process_data.validate_data(fixtures.good_processed_data)
        self.assertEqual(None, rtn, 'Good return type not None')

        rtn = process_data.validate_data(fixtures.repeated_sense_processed_data)
        self.assertIsInstance(rtn, list, 'Return type not a list')
        self.assertIsInstance(rtn[0], process_data.DataValidationError, 'Return type not an error object')

    def test_validate_data_incorrect_data_input_response(self):
        """Function should raise an assertion error if processed data isn't provided"""
        with self.assertRaises(AssertionError):
            process_data.validate_data('A string')

    def test_validate_find_missing_senses_return_type(self):
        """Function should return list of tuples ('Sense number repeated', 'data') or None"""
        rtn = process_data.validate_find_missing_senses(fixtures.good_processed_data)
        self.assertEqual(None, rtn, 'Good return type not None')
        rtn = process_data.validate_find_missing_senses(fixtures.repeated_sense_processed_data)
        self.assertIsInstance(rtn, process_data.DataValidationError, 'Return type not an error object')
        self.assertIsInstance(rtn.error_type, str, 'Type not a string')
        self.assertIsInstance(rtn.error_data, list, 'Data not a list')

    def test_validate_find_missing_senses_return_contents(self):
        rtn = process_data.validate_find_missing_senses(fixtures.repeated_sense_processed_data)
        self.assertEqual('Sense number repeated', rtn.error_type, 'Incorrect error type')
        self.assertEqual(['sinasim use same sense  number multiple times.'], rtn.error_data, 'Incorrect error data')


class DataProcessingTests(unittest.TestCase):
    """Test all the functions that process and reorganise data read from spreadsheet"""

    def test_create_lexicon_entries_return_type(self):
        """Function should return a list of tuples (str, list)"""
        data = process_data.create_lexicon_entries(fixtures.good_processed_data)
        self.assertIsInstance(data, list)
        self.assertIsInstance(data[0], process_data.LexiconEntry)

    def test_create_lexicon_entries_return_alphabetical_order(self):
        data = process_data.create_lexicon_entries(fixtures.good_processed_data)

        self.assertGreater(ord(data[1].headword[0]), ord(data[0].headword[0]))
        self.assertGreater(ord(data[2].headword[0]), ord(data[1].headword[0]))

    def test_create_lexicon_entries_return_contents(self):
        data = process_data.create_lexicon_entries(fixtures.good_processed_data)

        self.assertEqual('inda', data[0].headword, 'Headword wrong')
        self.assertEqual([{'definition': 'A large person',
                           'english': 'dad',
                           'example': 'ɛŋ inda',
                           'example_translation': 'my dad',
                           'phonetics': 'inda',
                           'pos': 'n',
                           'sense': 1,
                           'tok_pisin': 'papa'}], data[0].entry, 'Entry wrong')
        self.assertEqual(3, len(data), 'Number of headwords wrong')


    def test_create_lexicon_entries_orthography_trumps_phonetics(self):
        """Function should use orthographic text for headword when available"""
        data = process_data.create_lexicon_entries(fixtures.good_processed_data)

        self.assertEqual('undum__', data[2].headword)

    def test_create_reverse_lexicon_entries_return_type(self):
        """Function should return a list of tuples (str, dict)"""
        data = process_data.create_reverse_lexicon_entries(fixtures.good_processed_data)

        self.assertIsInstance(data, list, 'List not returned')
        self.assertIsInstance(data[0], process_data.LexiconEntry, 'List doesn\'t contain entry objects')


    def test_create_reverse_lexicon_entries_return_contents(self):
        data = process_data.create_reverse_lexicon_entries(fixtures.good_processed_data)

        self.assertEqual(4, len(data))
        self.assertEqual('child', data[0].headword)
        print(data[0].entry)
        self.assertEqual('pikinini', data[0].entry[0]['tpi'])
        self.assertEqual('dad', data[1].headword)


    def test_sort_by_id(self):
        data = process_data.sort_by_id(fixtures.good_processed_data)
        self.assertEqual(1, data[0]['id'], 'First is not ID 1')
        self.assertEqual(2, data[1]['id'], 'Second is not ID 2')
        self.assertEqual(3, data[3]['id'], 'Last is not ID 3')

    def test_sort_by_tag(self):
        data = process_data.sort_by_tag(fixtures.good_processed_data)
        self.assertEqual('', data[0]['tag'], 'Tags not in alphabetical order')
        self.assertEqual('animal', data[1]['tag'], 'Tags not in alphabetical order')
        self.assertEqual('test', data[3]['tag'], 'Tags not in alphabetical order')

    def test_sort_by_sense(self):
        data = process_data.sort_by_sense(fixtures.good_processed_data)
        self.assertEqual(1, data[0]['sense'], 'Sense numbers not in order')
        self.assertEqual(2, data[3]['sense'], 'Sense numbers not in order')

    def test_check_processed_data(self):
        """Function should raise an assert error if argument isn't in the form of the return value of the
        read_lexicon() function"""
        self.assertTrue(process_data.check_processed_data(fixtures.good_processed_data, 'Test'))
        with self.assertRaises(AssertionError) as error:
            process_data.check_processed_data('String', 'Test')
            self.assertIn('Function called incorrectly', str(error.exception))
        with self.assertRaises(AssertionError) as error:
            process_data.check_processed_data(1, 'Test')
            self.assertIn('Function called incorrectly', str(error.exception))
        with self.assertRaises(AssertionError) as error:
            process_data.check_processed_data([], 'Test')
            self.assertIn('Function called incorrectly', str(error.exception))
        with self.assertRaises(AssertionError) as error:
            process_data.check_processed_data({}, 'Test')
            self.assertIn('Function called incorrectly', str(error.exception))

    def test_check_lexicon_entries(self):
        """Function should raise a Type error if argument isn't in the form of the return value of the
        create_lexicon_entries() function"""
        with self.assertRaises(TypeError):
            process_data.check_lexicon_entries('String', 'test')
        process_data.check_lexicon_entries([process_data.LexiconEntry('Test', {})], 'test')

    def test_get_word_beginnings_returns_in_alphabetical_order(self):
        data = process_data.get_word_beginnings(fixtures.jumbled_lexicon_entries)

        self.assertEqual(['t', 'x'], data)
