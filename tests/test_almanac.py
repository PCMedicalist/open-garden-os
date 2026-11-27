"""Offline tests for the almanac source registry and user-entered seasonal context."""
import unittest
from datetime import date

from garden_os.almanac import SOURCES, SeasonalContext, source_by_label


class AlmanacTests(unittest.TestCase):
    def test_two_distinct_publications_registered(self):
        self.assertEqual(len(SOURCES), 2)
        self.assertEqual({s.label for s in SOURCES}, {"Farmers' Almanac", "The Old Farmer's Almanac"})
        self.assertNotEqual(SOURCES[0].publisher, SOURCES[1].publisher)

    def test_no_public_api_recorded(self):
        for s in SOURCES:
            self.assertIn("none found", s.api)
            self.assertTrue(s.url.startswith("https://"))

    def test_source_lookup(self):
        self.assertEqual(source_by_label("the old farmer's almanac").publisher, "Yankee Publishing Inc.")
        with self.assertRaises(ValueError):
            source_by_label("unknown")

    def test_user_entered_context_valid(self):
        c = SeasonalContext(date(2026, 4, 15), date(2026, 10, 15), "The Old Farmer's Almanac", "https://www.almanac.com/gardening/planting-calendar")
        self.assertIn("Within", c.status(date(2026, 6, 1)))
        self.assertIn("Outside", c.status(date(2026, 12, 1)))
        d = c.public_dict()
        self.assertTrue(d["user_entered"])
        self.assertIn("not agronomic advice", d["status_note"])

    def test_scraped_context_rejected(self):
        with self.assertRaises(ValueError):
            SeasonalContext(date(2026, 4, 15), date(2026, 10, 15), "x", "https://x.com", user_entered=False)

    def test_invalid_window_rejected(self):
        with self.assertRaises(ValueError):
            SeasonalContext(date(2026, 10, 15), date(2026, 4, 15), "x", "https://x.com")

    def test_missing_citation_rejected(self):
        with self.assertRaises(ValueError):
            SeasonalContext(date(2026, 4, 15), date(2026, 10, 15), "", "https://x.com")


if __name__ == "__main__":
    unittest.main(verbosity=2)
