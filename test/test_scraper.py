import unittest

from scraper.scraper import parse_html


class TestParseFunction(unittest.TestCase):

    def setUp(self):
        with open('test/test.html', encoding='utf-8') as f:
            html = f.read()
            self.output = parse_html(html)

    def tearDown(self):
        self.output = []

    def test_output_is_not_none(self):
        self.assertIsNotNone(self.output)

    def test_output_is_a_list(self):
        empty_list = []
        self.assertIs(type(self.output), type(empty_list))

    def test_output_is_a_list_of_dicts(self):
        empty_dict = {}
        self.assertIs(type(self.output[0]), type(empty_dict))


if __name__ == '__main__':
    unittest.main()
