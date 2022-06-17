import datetime
import os
import unittest
from unittest.mock import patch

from application_code import output
from tests import fixtures


class HTMLGenerationTests(unittest.TestCase):
    """Tests the generation of HTML pages"""

    def setUp(self):
        parent_folder = os.path.dirname(__file__)
        self.test_folder = os.path.join(parent_folder, "test_output")
        self.lex_page = os.path.join(self.test_folder, "main_dict.html")
        self.check_page = os.path.join(self.test_folder, "check_list.html")
        self.error_page = os.path.join(self.test_folder, "errors.html")

    def tearDown(self):
        for file in os.listdir(self.test_folder):
            if file == "blank_file":
                continue
            os.remove(os.path.join(self.test_folder, file))

    def test_generate_html(self):
        with patch("lexicon_config.settings", fixtures.settings):
            output.generate_html(fixtures.good_processed_data)

        self.assertTrue(os.path.exists(self.lex_page))

    def test_generate_lexicon_page_exists(self):
        with patch("lexicon_config.settings", fixtures.settings):
            output.generate_lexicon_page(fixtures.good_processed_data, None)
        self.assertTrue(os.path.exists(self.lex_page))

    def test_generate_lexicon_page_contents(self):
        with patch("lexicon_config.settings", fixtures.settings):
            output.generate_lexicon_page(fixtures.good_processed_data, None)
        with open(self.lex_page, "r") as file:
            file = file.read()
            # check fixture data in the html
            for word in fixtures.good_processed_data:
                self.assertIn(word["phon"], file)
                self.assertIn(word["eng"], file)
                self.assertIn(word["tpi"], file)
            self.assertIn(
                datetime.datetime.now().strftime("%A %d %B %Y"), file, "Date missing"
            )

    def test_generate_error_page_with_repeated_sense_errors(self):
        with patch("lexicon_config.settings", fixtures.settings):
            output.generate_html(fixtures.repeated_sense_processed_data)
        self.assertTrue(os.path.exists(self.error_page))
        with open(self.error_page, "r") as file:
            file = file.read()
            self.assertIn(
                "<h3>Sense number repeated</h3>", file, "Error heading missing"
            )
            self.assertIn(
                "sinasim uses same sense number multiple times.",
                file,
                "Error detail missing",
            )

        with open(self.lex_page, "r") as file:
            file = file.read()
        self.assertIn(
            "Errors in the data have been identified",
            file,
            "Error message should be showing",
        )

    def test_generate_error_page_with_pos_errors(self):
        with patch("lexicon_config.settings", fixtures.settings):
            output.generate_html(fixtures.missing_pos_processed_data)
        self.assertTrue(os.path.exists(self.error_page))
        with open(self.error_page, "r") as file:
            file = file.read()
            self.assertIn(
                "<h3>Part of speech missing</h3>", file, "Error heading missing"
            )
            self.assertIn("sinasim is missing pos", file, "Error detail missing")

        with open(self.lex_page, "r") as file:
            file = file.read()
        self.assertIn(
            "Errors in the data have been identified",
            file,
            "Error message should be showing",
        )

    def test_error_page_multiple_errors(self):
        with patch("lexicon_config.settings", fixtures.settings):
            output.generate_html(fixtures.multiple_error_processed_data)
        self.assertTrue(os.path.exists(self.error_page))
        with open(self.error_page, "r") as file:
            file = file.read()
            self.assertIn(
                "<h3>Part of speech missing</h3>", file, "Error heading missing"
            )
            self.assertIn("sinasim is missing pos", file, "Error detail missing")
            self.assertIn(
                "<h3>Sense number repeated</h3>", file, "Error heading missing"
            )
            self.assertIn(
                "sinasim uses same sense number multiple times.",
                file,
                "Error detail missing",
            )

        with open(self.lex_page, "r") as file:
            file = file.read()
        self.assertIn(
            "Errors in the data have been identified",
            file,
            "Error message should be showing",
        )

    def test_generate_error_page_without_errors(self):
        with patch("lexicon_config.settings", fixtures.settings):
            output.generate_html(fixtures.good_processed_data)
        self.assertFalse(os.path.exists(self.error_page))
        with open(self.lex_page, "r") as file:
            file = file.read()
        self.assertNotIn(
            "Errors in the data have been identified",
            file,
            "Error message shouldn't be showing",
        )

    def test_assert_templates_exist(self):
        self.assertTrue(output.assert_templates_exist())
        with self.assertRaises(FileNotFoundError) as error:
            output.assert_templates_exist(template_dir="Fake directory")
            self.assertIn("Template:", str(error.exception))

    def test_generate_context(self):
        with patch("lexicon_config.settings", fixtures.settings):
            context = output.generate_context("title", "header")
            self.assertEqual("Test", context["language"])
            self.assertEqual("title", context["title"])
            self.assertEqual("header", context["header"])
            self.assertEqual(
                datetime.datetime.now().strftime("%A %d %B %Y"), context["date"]
            )


class OtherFileGenerationTests(unittest.TestCase):
    def setUp(self):
        parent_folder = os.path.abspath(os.path.join(__file__, ".."))
        self.paDb_path = os.path.join(
            parent_folder,
            "test_output",
            "{language}_phonology_assistant.db".format(
                language=fixtures.settings["language"]
            ),
        )
        self.dataset_path = os.path.join(
            parent_folder, "test_output", "phonemic_dataset.csv"
        )

    def tearDown(self):
        if os.path.exists(self.paDb_path):
            os.remove(self.paDb_path)
        if os.path.exists(self.dataset_path):
            os.remove(self.dataset_path)
