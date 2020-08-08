import datetime
import os
import unittest
from unittest.mock import patch

from application_code import output
from tests import fixtures


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

        self.fail()