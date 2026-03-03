import unittest

from src.utils.wordcloud_gen import _normalize_hex_color, _sanitize_tags, is_dark_color


class TestWordCloudHelpers(unittest.TestCase):
    def test_sanitize_tags_filters_invalid_values(self):
        result = _sanitize_tags(["  科技  ", "", "   ", None, "动画"])  # type: ignore[list-item]
        self.assertEqual(result, ["科技", "动画"])

    def test_normalize_hex_color_accepts_valid_color(self):
        self.assertEqual(_normalize_hex_color("#a1b2c3"), "#A1B2C3")

    def test_normalize_hex_color_rejects_invalid_color(self):
        self.assertEqual(_normalize_hex_color("#zzz999"), "#18191C")
        self.assertEqual(_normalize_hex_color("#fff"), "#18191C")

    def test_is_dark_color_handles_invalid_input(self):
        # invalid input should fallback to default dark color
        self.assertTrue(is_dark_color("oops"))
        self.assertTrue(is_dark_color("#000000"))
        self.assertFalse(is_dark_color("#FFFFFF"))


if __name__ == "__main__":
    unittest.main()
