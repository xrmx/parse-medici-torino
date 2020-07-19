import json
import sys
import unittest


def time_to_range_index(t):
    hour, minutes = t.split(":")
    int_hour = int(hour.lstrip("0") or 0)
    index = int_hour * 2
    return index + int(minutes != "00")


def build_orari_range(orari):
    """Build a structure to hold doctor availability

    For each half hour in the day returns how many times the doctor
    is available during the week or 0 if it is not"""
    availability = [0] * 48
    ranges = [(o["da"], o["a"]) for o in orari]
    for start, end in ranges:
        start_index = time_to_range_index(start)
        end_index = time_to_range_index(end)
        for i in range(start_index, end_index):
            availability[i] += 1
    return availability


def get_features(to_convert):
    for data in to_convert:
        circoscrizione = data["circoscrizione_numero"]
        mmg = data["mmg"]
        for doc in data["dottori"]:
            nome = doc["nome"]
            codice = doc["codice"]
            associazione = doc["associazione"]
            for address in doc["indirizzi"]:
                yield {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": address["posizione"],
                    },
                    "properties": {
                        "circoscrizione": circoscrizione,
                        "mmg": mmg,
                        "nome": nome,
                        "codice": codice,
                        "indirizzo": address["indirizzo"],
                        "associazione": associazione,
                        "orari": build_orari_range(address["orari"])
                    }
                }


def convert_to_geojson(to_convert):
    return json.dumps({
        "type": "FeatureCollection",
        "features": list(get_features(to_convert))
    })


if __name__ == '__main__':
    to_convert = []
    for arg in sys.argv[1:]:
        with open(arg) as f:
            data = json.load(f)
            to_convert.append(data)

    if not to_convert:
        print("Non ci sono json da convertire", file=sys.stderr)
        sys.exit(1)

    geojson = convert_to_geojson(to_convert)
    print(geojson)


class Geo2JSONTestCase(unittest.TestCase):
    def test_time_to_range_index_works_fine(self):
        index = time_to_range_index("00:00")
        self.assertEqual(index, 0)
        index = time_to_range_index("00:30")
        self.assertEqual(index, 1)
        index = time_to_range_index("01:00")
        self.assertEqual(index, 2)

    def test_build_orari_range_returns_properly_sized_list(self):
        availability = build_orari_range([])
        self.assertEqual(len(availability), 48)
        self.assertEqual(availability, [0] * 48)

    def test_build_orari_range_parse_ranges_correctly(self):
        availability = build_orari_range([{"da": "00:00", "a": "24:00"}])
        self.assertEqual(len(availability), 48)
        self.assertEqual(availability, [1] * 48)

        availability = build_orari_range([{"da": "00:00", "a": "00:30"}])
        self.assertEqual(availability, [1] + [0] * 47)

    def test_get_features_returns_features(self):
        data = [
            {
                "circoscrizione_numero": "1",
                "mmg": True,
                "dottori": [
                    {
                        "nome": "Ciccio Pasticcio",
                        "codice": "CODICE",
                        "associazione": ["associazione"],
                        "indirizzi": [
                            {
                                "indirizzo": "via le mani di dosso",
                                "posizione": [10, 10],
                                "orari": [],
                            }
                        ]
                    }
                ]
            }
        ]
        features = get_features(data)
        self.assertEqual(list(features), [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [10, 10],
                },
                "properties": {
                    "circoscrizione": "1",
                    "mmg": True,
                    "nome": "Ciccio Pasticcio",
                    "codice": "CODICE",
                    "indirizzo": "via le mani di dosso",
                    "associazione": ["associazione"],
                    "orari": [0] * 48,
                }
            }
        ])
