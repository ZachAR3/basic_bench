import unittest
from tokenizer import tokenize


class HiddenTokenizerTests(unittest.TestCase):
    def test_escaped_quote_and_backslash(self):
        self.assertEqual(
            tokenize(r'"say \"hi\"" "c:\\temp"'),
            ['say "hi"', r"c:\temp"],
        )

    def test_unterminated_quote(self):
        with self.assertRaises(ValueError):
            tokenize('alpha "unfinished')

    def test_trailing_escape_is_literal(self):
        self.assertEqual(tokenize("path\\\\"), ["path\\"])

    def test_empty_quoted_token_is_preserved(self):
        self.assertEqual(tokenize('alpha "" omega'), ["alpha", "", "omega"])

    def test_adjacent_quoted_and_unquoted_segments(self):
        self.assertEqual(tokenize('pre"two words"post'), ["pretwo wordspost"])

    def test_tabs_newlines_and_escaped_whitespace(self):
        self.assertEqual(
            tokenize('"a\\tb"\n"c\\nd"\tend'),
            ["atb", "cnd", "end"],
        )

    def test_multiple_escaped_backslashes(self):
        self.assertEqual(tokenize(r'"a\\\\b"'), [r"a\\b"])
