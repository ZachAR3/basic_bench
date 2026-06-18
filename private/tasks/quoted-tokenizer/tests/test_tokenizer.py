import unittest
from tokenizer import tokenize


class TokenizerTests(unittest.TestCase):
    def test_words(self):
        self.assertEqual(tokenize("alpha beta"), ["alpha", "beta"])

    def test_quoted_space(self):
        self.assertEqual(tokenize('alpha "two words"'), ["alpha", "two words"])


if __name__ == "__main__":
    unittest.main()
