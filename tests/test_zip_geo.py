"""Offline tests for ZIP geocoding."""
import json
import unittest

from garden_os.zip_geo import parse_zip_response, resolve_zip

PAYLOAD = {
    "country": "United States",
    "post code": "78701",
    "places": [{
        "place name": "Austin", "longitude": "-97.7426", "latitude": "30.2713",
        "state": "Texas", "state abbreviation": "TX",
    }],
}


class ZipTests(unittest.TestCase):
    def test_payload_parses(self):
        z = parse_zip_response(PAYLOAD)
        self.assertEqual((z.zip_code, z.place, z.state), ("78701", "Austin", "TX"))
        self.assertAlmostEqual(z.latitude, 30.2713)
        self.assertAlmostEqual(z.longitude, -97.7426)
        self.assertIn("78701", z.public_dict()["zip_code"])

    def test_bad_zip_format_rejected_before_network(self):
        for bad in ["123", "1234", "123456", "abcde", ""]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                resolve_zip(bad, fetch=lambda _: json.dumps(PAYLOAD))

    def test_injected_fetch_used(self):
        seen = {}
        def fake(url):
            seen["url"] = url
            return json.dumps(PAYLOAD)
        z = resolve_zip("78701", fetch=fake)
        self.assertEqual(z.place, "Austin")
        self.assertTrue(seen["url"].endswith("/us/78701"))

    def test_empty_places_fails_loudly(self):
        with self.assertRaises(ValueError):
            parse_zip_response({"places": []})

    def test_invalid_coordinates_rejected(self):
        bad = json.loads(json.dumps(PAYLOAD))
        bad["places"][0]["latitude"] = "999"
        with self.assertRaises(ValueError):
            parse_zip_response(bad)


if __name__ == "__main__":
    unittest.main(verbosity=2)
