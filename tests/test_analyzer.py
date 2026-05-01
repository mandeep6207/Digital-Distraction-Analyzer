import unittest

from utils.analyzer import analyze_distraction, validate_inputs


class AnalyzerTests(unittest.TestCase):
    def test_focused_day_scores_low(self):
        data, errors = validate_inputs(
            {
                "screen_time": "5",
                "social_media": "0.5",
                "productive_hours": "4",
                "app_switches": "20",
            }
        )

        self.assertEqual(errors, {})
        result = analyze_distraction(data)
        self.assertLessEqual(result["score"], 30)
        self.assertEqual(result["focus_level"], "Highly Focused")

    def test_invalid_time_distribution_is_rejected(self):
        data, errors = validate_inputs(
            {
                "screen_time": "4",
                "social_media": "3",
                "productive_hours": "3",
                "app_switches": "10",
            }
        )

        self.assertIsNone(data)
        self.assertIn("productive_hours", errors)


if __name__ == "__main__":
    unittest.main()
