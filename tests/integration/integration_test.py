import json
import os
import re
from unittest import TestCase
from unittest.mock import patch, mock_open, sentinel, call, Mock

import sys
print(sys.path)

from kaggle_normaliser import main as kag_normain, get_output_name, save_json, load_json, add_quote, get_int_input, word_normaliser, get_case_bump, iterate_through_quotes, UserEscape, key_decider, sample_quotes, csv_all_quotes


class TestComponent(TestCase):
    output_name = "test-quotes_slimmed.json"

    def setUp(self):
        try:
            os.remove(TestComponent.output_name)
        except FileNotFoundError as e:
            pass

    def assert_easy_quotes(self, quote_list):
        assert quote_list[0] == ["Don't cry because it's over, smile because it happened.", 'Dr. Seuss']
        assert quote_list[1] == [
            "I'm selfish, impatient and a little insecure. I make mistakes, I am out of control and at times hard to "
            "handle. But if you can't handle me at my worst, then you sure as hell don't deserve me at my best.",
            'Marilyn Monroe']

    @patch('kaggle_normaliser.get_int_input', return_value=0)
    def test_use_case0(self, mock_get_int_input):
        kag_normain("all", "test-quotes.json")
        # 4% of the top quotations have obviously bad formatting:
        mock_get_int_input.assert_has_calls([
            call(5),
            call(5)
        ])
        with open(TestComponent.output_name, encoding="utf8") as f:
            quote_list = json.load(f)
        self.assert_easy_quotes(quote_list)
        self.assertEqual(
            quote_list[14],
            ['Don’t walk in front of me… I may not follow, don’t walk behind me… I may not lead, walk beside me… just be my friend', 'Albert Camus']
        )

    @patch('kaggle_normaliser.get_int_input', return_value=1)
    def test_use_case1(self, mock_get_int_input):
        kag_normain("all", "test-quotes.json")
        # 4% of the top quotations have obviously bad formatting:
        mock_get_int_input.assert_has_calls([
            call(5),
            call(5)
        ])
        with open(TestComponent.output_name, encoding="utf8") as f:
            quote_list = json.load(f)
        self.assert_easy_quotes(quote_list)
        self.assertEqual(
            quote_list[14],
            ['Don’t walk in front of me… I may not follow. Don’t walk behind me… I may not lead. Walk beside me… just be my friend', 'Albert Camus']
        )

    @patch('kaggle_normaliser.get_int_input', return_value=2)
    def test_use_case2(self, mock_get_int_input):
        kag_normain("all", "test-quotes.json")
        # 4% of the top quotations have obviously bad formatting:
        mock_get_int_input.assert_has_calls([
            call(5),
            call(5)
        ])
        with open(TestComponent.output_name, encoding="utf8") as f:
            quote_list = json.load(f)
        self.assert_easy_quotes(quote_list)
        self.assertEqual(
            quote_list[14],
            ['Don’t walk in front of me… I may not follow don’t walk behind me… I may not lead walk beside me… just be my friend', 'Albert Camus']
        )


