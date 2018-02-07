# import scraper functions
from scraper.scraper import parse_html

import unittest
 

class testParseFunction(unittest.TestCase):
 
    def setUp(self):
        with open('test/test.html', encoding='utf-8') as f:
            html = f.read()
            self.output = parse_html(html)
    
    def tearDown(self):
        self.output = []

    def test_output_is_not_none(self):
        self.assertIsNotNone(self.output)

    def test_output_is_a_list_of_dicts(self):
        test_item = {
            'title': 'U.S. consumer protection official puts Equifax probe on ice', 
            'rank': '1.', 
            'score': '502 points', 
            'id': '16308961'
        }
        self.assertEqual(self.output[0], test_item)


if __name__ == '__main__':
    unittest.main()
    