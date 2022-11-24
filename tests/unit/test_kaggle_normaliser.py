import json
import re
from unittest import TestCase
from unittest.mock import patch, mock_open, sentinel, call, Mock

import sys
print(sys.path)

from kaggle_normaliser import main as kag_normain, get_output_name, save_json, load_json, add_quote, get_int_input, word_normaliser, get_case_bump, iterate_through_quotes, UserEscape, key_decider, sample_quotes, csv_all_quotes


QUOTES = [
    {
        "Quote":
            "Darkness cannot drive out darkness: only light can do that. Hate cannot drive out hate: only love can do that.",
        "Author": "Martin Luther King Jr.,  A Testament of Hope: The Essential Writings and Speeches",
        "Tags": ["darkness", "drive-out", "peace"],
        "Popularity": 0.05806205806205806,
        "Category": "love"
    },
    {
        "Quote":
            "To live is the rarest thing in the world. Most people exist, that is all.",
        "Author": "Oscar Wilde",
        "Tags": ["life "],
        "Popularity": 0.058033058033058034,
        "Category": "life"
    },
]

UNIQUE_QUOTES = {x["Quote"]:x["Author"] for x in QUOTES}

BAD_QUOTES = [
    {
        "Quote":
            "The organizers of WorldFest hope vegetarian.",
        "Author": "dmoe"
    }
]


class Test(TestCase):
    def test_save_json(self):
        with patch("builtins.open") as mock_file:
            save_json(sentinel.file_nm, QUOTES)
        mock_file.assert_has_calls([
            call(sentinel.file_nm, "w", encoding='utf8')
        ], any_order=True)

    @patch('kaggle_normaliser.add_quote')
    def test_load_json(self, mock_add_quote):
        with patch("builtins.open", mock_open(read_data=json.dumps(QUOTES))) as mock_file:
            load_json(sentinel.file_nm)
        mock_file.assert_has_calls([call(sentinel.file_nm, encoding='utf8')], any_order=True)

    @patch('kaggle_normaliser.save_json')
    @patch('kaggle_normaliser.add_quote', side_effect = lambda *x: x[2].append((x[0], x[1])))
    def test_iterate_through_quotes(self, mock_add_quote, mock_save_json):
        sample_name = "path/to/fictitious/file.json"
        expected_op = "path/to/fictitious/file_slimmed.json"
        with patch("builtins.open", mock_open(read_data=json.dumps(QUOTES))) as mock_file:
            mock_file.side_effect = FileNotFoundError
            iterate_through_quotes(UNIQUE_QUOTES, sample_name, sentinel.decider)
        mock_file.assert_has_calls([call(expected_op, encoding='utf8')], any_order=True)
        expected_quotes = [(x["Quote"], x["Author"]) for x in QUOTES]
        mock_save_json.assert_called_once_with(expected_op, expected_quotes)

    @patch('kaggle_normaliser.save_json')
    @patch('kaggle_normaliser.random', side_effect = [0, 0, 0.51])
    def test_sample_quotes(self, mock_rnd, mock_save_json):
        sample_name = "path/to/fictitious/file.json"
        expected_op = "path/to/fictitious/file_selection.json"
        sample_quotes(UNIQUE_QUOTES, sample_name, 2)
        mock_save_json.assert_called_once_with(expected_op, [(x[0], x[1]) for x in UNIQUE_QUOTES.items()])
        mock_rnd.assert_has_calls([call(), call(), call()])

    def test_csv_all_quotes(self):
        sample_name = "path/to/fictitious/file.json"
        expected_op = "path/to/fictitious/file_all.csv"
        with patch("builtins.open") as mock_file:
            csv_all_quotes(UNIQUE_QUOTES, sample_name)
        mock_file.assert_has_calls([call(expected_op, "w")])

    @patch('kaggle_normaliser.load_json', return_value=sentinel.all_quotes)
    @patch('kaggle_normaliser.iterate_through_quotes', return_value=sentinel.quote_dict)
    def test_main_all(self, mock_iterate_through_quotes, mock_load_json):
        kag_normain("all", sentinel.file_nm)
        mock_iterate_through_quotes.assert_called_once_with(
            sentinel.all_quotes, sentinel.file_nm, key_decider)
        mock_load_json.assert_called_once_with(sentinel.file_nm)

    @patch('kaggle_normaliser.load_json', return_value=sentinel.all_quotes)
    @patch('kaggle_normaliser.sample_quotes', return_value=sentinel.quote_dict)
    def test_main_rnd5(self, mock_sample_quotes, mock_load_json):
        kag_normain("random5", sentinel.file_nm)
        mock_sample_quotes.assert_called_once_with(
            sentinel.all_quotes, sentinel.file_nm, 5)
        mock_load_json.assert_called_once_with(sentinel.file_nm)

    @patch('kaggle_normaliser.load_json', return_value=sentinel.all_quotes)
    @patch('kaggle_normaliser.csv_all_quotes', return_value=sentinel.quote_dict)
    def test_main_csv(self, mock_csv_all_quotes, mock_load_json):
        kag_normain("csv", sentinel.file_nm)
        mock_csv_all_quotes.assert_called_once_with(
            sentinel.all_quotes, sentinel.file_nm)
        mock_load_json.assert_called_once_with(sentinel.file_nm)

    @patch('kaggle_normaliser.load_json', return_value=sentinel.all_quotes)
    @patch('builtins.print')
    def test_main_undef_meth(self, mock_print, mock_load_json):
        kag_normain("undefined", sentinel.file_nm)
        mock_print.assert_has_calls([
            call("Ctrl-C will update your progress and quit."),
            call(f"undefined was not recognised. Please use one of: ['all', 'random', 'csv']"),
        ])
        mock_load_json.assert_called_once_with(sentinel.file_nm)

    op_name_list = [
        ("this/test/must_end_in.json", "this/test/must_end_in_slimmed.json"),
        ("this/in.json", "this/in_slimmed.json"),
        ("in.json", "in_slimmed.json"),
        (".json", "_slimmed.json"),
    ]
    def test_get_output_name(self):
        for in1, expect1 in Test.op_name_list:
            self.assertEqual(expect1, get_output_name(in1))


class TestKeyGrabber(TestCase):
    @patch('kaggle_normaliser.Getch', autospec=True)
    def test_get_int_input_unicode_err(self, mock_getch):
        mock_getch.return_value = Mock(side_effect = [b"\x80", b"1"])
        ans = get_int_input(4)
        self.assertEqual(ans, 0)

    @patch('kaggle_normaliser.Getch', autospec=True)
    def test_get_int_input1(self, mock_getch):
        mock_getch.return_value = lambda: b"\x03"
        with self.assertRaises(UserEscape):
            get_int_input(4)

    @patch('builtins.print')
    @patch('kaggle_normaliser.Getch', autospec=True)
    def test_get_int_input2(self, mock_getch, mock_print):
        mock_getch.return_value = Mock(side_effect=[b"h", b"2"])
        ans = get_int_input(4)
        self.assertEqual(ans, 1)
        mock_print.assert_has_calls([
            call("h"),
            call("2")
        ])

    @patch('builtins.print')
    @patch('kaggle_normaliser.Getch', autospec=True)
    def test_get_int_input3(self, mock_getch, mock_print):
        mock_getch.return_value = Mock(side_effect=[b"0", b"5", b"2"])
        ans = get_int_input(4)
        self.assertEqual(ans, 1)
        mock_print.assert_has_calls([
            call("0"),
            call(f"Please enter 1..{4}"),
            call("5"),
            call(f"Please enter 1..{4}"),
            call("2")
        ])

    @patch('kaggle_normaliser.Getch', autospec=True)
    def test_get_int_inputs(self, mock_getch):
        for x in range(1, 5):
            mock_getch.return_value = lambda: str(x).encode()
            ans = get_int_input(4)
            self.assertEqual(ans, x - 1)


class TestWordNormaliser(TestCase):
    def test_word_normaliser_nop1(self):
        match = re.search("\\b\\w*[a-z]+[A-Z]+\\w*\\b", "this is fine")
        assert not match

    def test_word_normaliser_nop2(self):
        match = re.search("\\b\\w*[a-z]+[A-Z]+\\w*\\b", "This is also fine.")
        assert not match

    def test_word_normaliser_camel1(self):
        whole_quote = "CaMel cased is not fine."
        match = re.search("\\b\\w*[a-z]+[A-Z]+\\w*\\b", whole_quote)
        assert match
        mock_decider = Mock(return_value=0)
        bumpy_word = word_normaliser(match, mock_decider, whole_quote)
        self.assertEqual(bumpy_word, "Ca, mel")

    def test_word_normaliser_camel2(self):
        whole_quote = "CaMel cased is not fine."
        match = re.search("\\b\\w*[a-z]+[A-Z]+\\w*\\b", whole_quote)
        assert match
        bumpy_word = word_normaliser(match, Mock(return_value=1), whole_quote)
        self.assertEqual(bumpy_word, "Ca. Mel")

    def test_word_normaliser_camel3(self):
        whole_quote = "CaMel cased is not fine."
        match = re.search("\\b\\w*[a-z]+[A-Z]+\\w*\\b", whole_quote)
        assert match
        bumpy_word = word_normaliser(match, Mock(return_value=2), whole_quote)
        self.assertEqual(bumpy_word, "Ca mel")

    def test_word_normaliser_camel5(self):
        whole_quote = "CaMel cased is not fine."
        match = re.search("\\b\\w*[a-z]+[A-Z]+\\w*\\b", whole_quote)
        assert match
        bumpy_word = word_normaliser(match, Mock(return_value=4), whole_quote)
        self.assertEqual(bumpy_word, "CaMel")

    def test_word_normaliser_camel2_1(self):
        whole_quote = "Delayed CaMel is not fine."
        match = re.search("\\b\\w*[a-z]+[A-Z]+\\w*\\b", whole_quote)
        assert match
        bumpy_word = word_normaliser(match, Mock(return_value=0), whole_quote)
        self.assertEqual(bumpy_word, "Ca, mel")

    def test_word_normaliser_camel2_2(self):
        whole_quote = "Delayed CaMel is not fine."
        match = re.search("\\b\\w*[a-z]+[A-Z]+\\w*\\b", whole_quote)
        assert match
        bumpy_word = word_normaliser(match, Mock(return_value=1), whole_quote)
        self.assertEqual(bumpy_word, "Ca. Mel")

    def test_word_normaliser_camel2_5(self):
        whole_quote = "Delayed CaMel is not fine."
        match = re.search("\\b\\w*[a-z]+[A-Z]+\\w*\\b", whole_quote)
        assert match
        bumpy_word = word_normaliser(match, Mock(return_value=4), whole_quote)
        self.assertEqual(bumpy_word, "CaMel")

    def test_word_normaliser_multi_join(self):
        whole_quote = "a phoenixFirstMustBurn."
        match = re.search("\\b\\w*[a-z]+[A-Z]+\\w*\\b", whole_quote)
        assert match
        bumpy_word = word_normaliser(match, Mock(return_value=3), whole_quote)
        self.assertEqual(bumpy_word, "phoenix First Must Burn")

    @patch('builtins.print')
    @patch('kaggle_normaliser.get_int_input', return_value=2)
    def test_key_decider(self, mock_get_int_input, mock_print):
        self.assertEqual(key_decider("The Simple PathSilence is PrayerPrayer", 14, 16, ["x S", "y S", "z S"]), 2)
        mock_print.assert_has_calls([
            call(' 1. The Simple Pathx Silence is Praye'),
            call(' 2. The Simple Pathy Silence is Praye'),
            call(' 3. The Simple Pathz Silence is Praye')
        ])
        mock_get_int_input.assert_called_once_with(3)


class TestAddQuote(TestCase):
    @patch('kaggle_normaliser.word_normaliser', return_value="REPLACEMENT")
    @patch('kaggle_normaliser.get_case_bump', return_value=True)
    def test_add_quote(self, mock_get_case_bump, mock_word_normaliser):
        quote_list = []
        add_quote(BAD_QUOTES[0]["Quote"], BAD_QUOTES[0]["Author"], quote_list, sentinel.decider)
        self.assertIn(('The organizers of REPLACEMENT hope vegetarian.', 'dmoe'), quote_list)
        mock_get_case_bump.assert_called_once_with(BAD_QUOTES[0]["Quote"])
        self.assertEqual(({
            "decider": sentinel.decider, "whole_quote": BAD_QUOTES[0]["Quote"]
        },), mock_word_normaliser.call_args_list[0][1:])


class TestCaseBump(TestCase):
    def test_get_case_bump(self):
        matches = get_case_bump(BAD_QUOTES[0]["Quote"])
        assert matches

    def test_get_case_bump_nop(self):
        matches = get_case_bump(QUOTES[0]["Quote"])
        assert not matches

    def test_get_case_bump_known_exceptions_1(self):
        matches = get_case_bump("This will match eBay is unknown.")
        assert matches

    def test_get_case_bump_known_exceptions_2(self):
        matches = get_case_bump("This will match iPhone is unknown.")
        assert matches

