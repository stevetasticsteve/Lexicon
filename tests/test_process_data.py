import unittest

from application_code import process_data
from tests import fixtures


class ValidationTests(unittest.TestCase):
    """Test the code that validates the data read from the spreadsheet"""

    def test_validate_data_return_type(self):
        """Function should return a list of error tuples ('error', 'data') or None"""
        rtn = process_data.validate_data(fixtures.good_processed_data)
        self.assertEqual(None, rtn, "Good return type not None")
        if rtn:
            self.fail("Error value not None")

        rtn = process_data.validate_data(fixtures.repeated_sense_processed_data)
        self.assertIsInstance(rtn, list, "Return type not a list")
        self.assertIsInstance(
            rtn[0], process_data.DataValidationError, "Return type not an error object"
        )
        if not rtn:
            self.fail("Error value not triggering loop entry")

    def test_validate_data_incorrect_data_input_response(self):
        """Function should raise an assertion error if processed data isn't provided"""
        with self.assertRaises(AssertionError):
            process_data.validate_data("A string")

    def test_error_return_types(self):
        rtn = process_data.validate_find_missing_pos(fixtures.good_processed_data)
        self.assertEqual(None, rtn, "Good return type not None")

        error_types = (
            process_data.validate_find_missing_pos(fixtures.missing_pos_processed_data),
            process_data.validate_find_missing_senses(
                fixtures.repeated_sense_processed_data
            ),
            process_data.validate_translation_missing(
                fixtures.translation_missing_processed_data
            ),
            process_data.validate_repeated_id(fixtures.repeated_id_processed_data),
            process_data.validate_missing_id(fixtures.id_missing_processed_data),
            process_data.validate_words_unique(fixtures.words_unique_processed_data),
            process_data.validate_entered_by(fixtures.entered_by_processed_data),
            process_data.validate_sense_number_order(
                fixtures.senses_misnumbered_processed_data
            ),
        )

        for error in error_types:
            self.assertIsInstance(
                error,
                process_data.DataValidationError,
                "Return type not an error object",
            )
            self.assertIsInstance(error.error_type, str, "Type not a string")
            self.assertIsInstance(error.error_data, list, "Data not a list")

    def test_validate_find_missing_senses_return_contents(self):
        rtn = process_data.validate_find_missing_senses(
            fixtures.repeated_sense_processed_data
        )
        self.assertEqual(
            "Sense number repeated", rtn.error_type, "Incorrect error type"
        )
        self.assertEqual(
            ["sinasim uses same sense number multiple times."],
            rtn.error_data,
            "Incorrect error data",
        )

    def test_validate_find_missing_pos_return_contents(self):
        rtn = process_data.validate_find_missing_pos(
            fixtures.missing_pos_processed_data
        )
        self.assertEqual(
            "Part of speech missing", rtn.error_type, "Incorrect error type"
        )
        self.assertEqual(
            ["sinasim is missing pos"], rtn.error_data, "Incorrect error data"
        )

    def test_validate_translation_missing_return_contents(self):
        rtn = process_data.validate_translation_missing(
            fixtures.translation_missing_processed_data
        )
        self.assertEqual(
            "Example is missing a translation", rtn.error_type, "Incorrect error type"
        )
        self.assertEqual(
            ['sinasim example: "om sinasim", is missing a translation'],
            rtn.error_data,
            "Incorrect error data",
        )

    def test_validate_repeated_id_contents(self):
        rtn = process_data.validate_repeated_id(fixtures.repeated_id_processed_data)
        self.assertEqual(
            "An ID number has been incorrectly repeated",
            rtn.error_type,
            "Incorrect error type",
        )
        self.assertEqual(
            ["ID number 2 is used for both inda and sinasim"],
            rtn.error_data,
            "Incorrect error data",
        )

    def test_validate_repeated_id_ignores_0(self):
        rtn = process_data.validate_repeated_id(fixtures.id_0_repeated)
        self.assertEqual(None, rtn, "return type not None")

    def test_validate_missing_id(self):
        rtn = process_data.validate_missing_id(fixtures.id_missing_processed_data)
        self.assertEqual("ID number is missing", rtn.error_type, "Incorrect error type")
        self.assertEqual(
            ["mutol is missing an ID number"], rtn.error_data, "Incorrect error data"
        )

    def test_validate_words_unique(self):
        rtn = process_data.validate_words_unique(fixtures.words_unique_processed_data)
        self.assertEqual("Word is duplicated", rtn.error_type, "Incorrect error type")
        self.assertEqual(
            ["sinasim appears multiple times with differing ID number"],
            rtn.error_data,
            "Incorrect error data",
        )

    def test_validate_entered_by(self):
        rtn = process_data.validate_entered_by(fixtures.entered_by_processed_data)
        self.assertEqual("Author is missing", rtn.error_type, "Incorrect error type")
        self.assertEqual(
            ["sinasim is lacking an author"], rtn.error_data, "Incorrect error data"
        )

    def test_validate_sense_number_order(self):
        rtn = process_data.validate_sense_number_order(
            fixtures.senses_misnumbered_processed_data
        )
        self.assertEqual(
            "Sense numbers misnumbered", rtn.error_type, "Incorrect error type"
        )
        self.assertEqual(
            ["sinasim has sense numbers [1, 3]"], rtn.error_data, "Incorrect error data"
        )

    def test_validate_sense_number_order_starting_number_off(self):
        rtn = process_data.validate_sense_number_order(
            fixtures.senses_misnumbered_processed_data2
        )
        self.assertEqual(
            "Sense numbers misnumbered", rtn.error_type, "Incorrect error type"
        )
        self.assertEqual(
            ["sinasim has sense numbers [2, 3]"], rtn.error_data, "Incorrect error data"
        )


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
        # number of headwords should be less than data rows
        self.assertLess(len(data), len(fixtures.good_processed_data))
        self.assertEqual("inda", data[0].headword, "Headword wrong")
        self.assertEqual(
            [
                {
                    "definition": "A large person",
                    "english": "dad",
                    "example": "ɛŋ inda",
                    "example_translation": "my dad",
                    "phonetics": "inda",
                    "pos": "n",
                    "sense": 1,
                    "tok_pisin": "papa",
                }
            ],
            data[0].entry,
            "Entry wrong",
        )
        self.assertEqual(3, len(data), "Number of headwords wrong")
        self.assertEqual(1, len(data[0].entry))
        # check the entry with multiple senses has an entry of len 2
        self.assertEqual(2, len(data[1].entry))

    def test_create_lexicon_entries_orthography_trumps_phonetics(self):
        """Function should use orthographic text for headword when available"""
        data = process_data.create_lexicon_entries(fixtures.good_processed_data)

        self.assertEqual("undum__", data[2].headword)

    def test_sort_by_id(self):
        data = process_data.sort_by_id(fixtures.good_processed_data)
        self.assertEqual(1, data[0]["id"], "First is not ID 1")
        self.assertEqual(2, data[1]["id"], "Second is not ID 2")
        self.assertEqual(3, data[3]["id"], "Last is not ID 3")

    def test_sort_by_tag(self):
        data = process_data.sort_by_tag(fixtures.good_processed_data)
        self.assertEqual("", data[0]["tag"], "Tags not in alphabetical order")
        self.assertEqual("animal", data[1]["tag"], "Tags not in alphabetical order")
        self.assertEqual("test", data[3]["tag"], "Tags not in alphabetical order")

    def test_sort_by_sense(self):
        data = process_data.sort_by_sense(fixtures.good_processed_data)
        self.assertEqual(1, data[0]["sense"], "Sense numbers not in order")
        self.assertEqual(2, data[3]["sense"], "Sense numbers not in order")

    def test_check_processed_data(self):
        """Function should raise an assert error if argument isn't in the form of the return value of the
        read_lexicon() function"""
        self.assertTrue(
            process_data.check_processed_data(fixtures.good_processed_data, "Test")
        )
        with self.assertRaises(AssertionError) as error:
            process_data.check_processed_data("String", "Test")
            self.assertIn("Function called incorrectly", str(error.exception))
        with self.assertRaises(AssertionError) as error:
            process_data.check_processed_data(1, "Test")
            self.assertIn("Function called incorrectly", str(error.exception))
        with self.assertRaises(AssertionError) as error:
            process_data.check_processed_data([], "Test")
            self.assertIn("Function called incorrectly", str(error.exception))
        with self.assertRaises(AssertionError) as error:
            process_data.check_processed_data({}, "Test")
            self.assertIn("Function called incorrectly", str(error.exception))

    def test_check_lexicon_entries(self):
        """Function should raise a Type error if argument isn't in the form of the return value of the
        create_lexicon_entries() function"""
        with self.assertRaises(TypeError):
            process_data.check_lexicon_entries("String", "test")
        process_data.check_lexicon_entries(
            [process_data.LexiconEntry("Test", {})], "test"
        )

    def test_get_word_beginnings_returns_in_alphabetical_order(self):
        data = process_data.get_word_beginnings(fixtures.jumbled_lexicon_entries)

        self.assertEqual(["t", "x"], data)
