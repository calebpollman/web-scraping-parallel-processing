import unittest
from unittest.mock import patch

from scrapers.scraper import parse_html


class TestParseFunction(unittest.TestCase):

    # def setUp(self):
    #     with open('test/test.html', encoding='utf-8') as f:
    #         html = f.read()
    #         self.output = parse_html(html)

    @patch('scrapers.scraper.get_load_time')
    def setUp(self, mock_get_load_time):
        mock_get_load_time.return_value = 'mocked!'
        with open('test/test.html', encoding='utf-8') as f:
            html = f.read()
            self.output = parse_html(html)

    def tearDown(self):
        self.output = []

    def test_output_is_not_none(self):
        self.assertIsNotNone(self.output)

    def test_output_is_a_list(self):
        self.assertTrue(isinstance(self.output, list))

    def test_output_is_a_list_of_dicts(self):
        self.assertTrue(all(isinstance(elem, dict) for elem in self.output))


if __name__ == '__main__':
    unittest.main()
