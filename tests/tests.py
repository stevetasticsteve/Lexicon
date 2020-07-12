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
    def test_read_lexicon_return_type(self):
        read_return = lexicon.read_lexicon(config_file=test_settings)

        self.assertEqual(type(read_return), list, 'Wrong data type returned')
        self.assertEqual(type(read_return[0]), dict, 'Wrong data type returned')


if __name__ == '__main__':
    unittest.main()
