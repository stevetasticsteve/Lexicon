import datetime
import os
import unittest
from unittest.mock import patch

from application_code import output
from tests import fixtures


class HTMLGenerationTests(unittest.TestCase):
    """Tests the generation of HTML pages"""

    def setUp(self):
        parent_folder = (os.path.abspath(os.path.join(__file__, '..')))
        self.test_folder = os.path.join(parent_folder, 'test_output')
        self.lex_page = os.path.join(self.test_folder, 'main_dict.html')
        self.reverse_page = os.path.join(self.test_folder, 'reverse_dict.html')
        self.check_page = os.path.join(self.test_folder, 'check_list.html')

    def tearDown(self):
        for file in os.listdir(self.test_folder):
            os.remove(os.path.join(self.test_folder, file))

    def test_generate_html(self):
        self.fail('Finish the test')

    def test_generate_lexicon_page_exists(self):
        with patch('lexicon_config.settings', fixtures.settings):
            output.generate_lexicon_page(fixtures.good_processed_data, None)
        self.assertTrue(os.path.exists(self.lex_page))

    def test_generate_lexicon_page_good_html(self):
        self.fail('Finish the test')

    def test_generate_lexicon_page_contents(self):
        self.fail('Finish the test')

    def test_generate_error_page_with_errors(self):
        self.fail('Finish the test')

    def test_generate_error_page_without_errors(self):
        self.fail('Finish the test')

    def test_generate_Eng_page_exists(self):
        with patch('lexicon_config.settings', fixtures.settings):
            output.generate_eng_page(fixtures.good_processed_data)
        self.assertTrue(os.path.exists(self.reverse_page))

    def test_generate_Eng_page_good_html(self):
        self.fail('Finish the test')

    def test_generate_Eng_page_contents(self):
        self.fail('Finish the test')

    def test_generate_check_page_exists(self):
        with patch('lexicon_config.settings', fixtures.settings):
            output.generate_check_page(fixtures.good_processed_data)
        self.assertTrue(os.path.exists(self.check_page))

    def test_generate_check_page_good_html(self):
        self.fail('Finish the test')

    def test_generate_check_page_contents(self):
        self.fail('Finish the test')

    def test_assert_templates_exist(self):
        self.assertTrue(output.assert_templates_exist())
        with self.assertRaises(FileNotFoundError) as error:
            output.assert_templates_exist(template_dir='Fake directory')
            self.assertIn('Template:', str(error.exception))

    def test_generate_context(self):
        with patch('lexicon_config.settings', fixtures.settings):
            context = output.generate_context('title', 'header')
            self.assertEqual('Test', context['language'])
            self.assertEqual('title', context['title'])
            self.assertEqual('header', context['header'])
            self.assertEqual(datetime.datetime.now().strftime('%A %d %B %Y'), context['date'])


class OtherFileGenerationTests(unittest.TestCase):
    def setUp(self):
        parent_folder = (os.path.abspath(os.path.join(__file__, '..')))
        self.path = os.path.join(parent_folder, 'test_output', '{language}_phonology_assistant.db'.format(
            language=fixtures.settings['language']))

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_create_phonemic_assistant_new_file_exists(self):
        with patch('lexicon_config.settings', fixtures.settings):
            output.create_phonemic_assistant_db(fixtures.good_processed_data, checked_only=False)
        self.assertTrue(os.path.exists(self.path))
        with patch('lexicon_config.settings', fixtures.settings):
            with self.assertRaises(AssertionError) as error:
                output.create_phonemic_assistant_db(fixtures.good_processed_data, checked_only=True)
            self.assertIn('No checked data to work with!', str(error.exception))

    def test_create_phonemic_assistant_contents(self):
        with patch('lexicon_config.settings', fixtures.settings):
            output.create_phonemic_assistant_db(fixtures.good_processed_data, checked_only=False)

        with open(self.path, 'r') as file:
            expected_contents = """\\_sh v3.0  400  PhoneticData

\\ref 001
\ge child
\gn pikinini
\ph undum
\ps n

\\ref 002
\ge dad
\gn papa
\ph inda
\ps n

\\ref 003
\ge rat
\gn rat
\ph sinasim
\ps n

\\ref 004
\ge rat
\gn rat
\ph sinasim
\ps n

"""
            self.assertEqual(expected_contents, file.read())
