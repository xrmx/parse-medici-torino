import datetime
import fileinput
import functools
import json
import os
import re
import sys
import unittest
import urllib.parse

import requests

from fixups import ESPANDI_INDIRIZZO

MESI = {
    'gennaio': 1,
    'febbraio': 2,
    'marzo': 3,
    'aprile': 4,
    'maggio': 5,
    'giugno': 6,
    'luglio': 7,
    'agosto': 8,
    'settembre': 9,
    'ottobre': 10,
    'novembre': 11,
    'dicembre': 12,
}

AGGIORNAMENTO_RE = re.compile(r"AGGIORNAMENTO: (?P<giorno>\d+) (?P<mese>\w+) (?P<anno>\d+)")
CIRCOSCRIZIONE_RE = re.compile(r"CIRCOSCRIZIONE (?P<numero>\d+): (?P<nome>.+)")
MMG_RE = re.compile(r"MMG")

NOME_DOTTORE_RE = re.compile(r"(?P<nome>[\w\s']+) \[(?P<codice>\w+)\]")
BLOCCO_ASSOCIAZIONE_RE = re.compile(r"Associazione:")
INDIRIZZO_RE = re.compile(r"(?P<indirizzo>.+) TORINO (?P<cap>\d+) \(TORINO\) Telefono: ?(?P<telefono>\d*)?")
FAX_RE = re.compile(r"FAX \d+")
TELEFONO_RE = re.compile(r"(TELEFONO.*:\s*)?(?P<telefono>\d+)$")

BLOCCO_ORARI_RE = re.compile(r"Giorno")
GIORNO_RE = re.compile(r"(?P<giorno>Lunedi|Martedi|Mercoledi|Giovedi|Venerdi|Sabato)")
ORARI_DA_RE = re.compile(r"Dalle")
ORARIO_RE = re.compile(r"(?P<orario>\d{2}:\d{2})")
ORARI_A_RE = re.compile(r"Alle")
BLOCCO_NOTE_RE = re.compile(r"Note")


def do_geocoding(indirizzo, token):
    mapbox_geocoding_v5 = "https://api.mapbox.com/geocoding/v5/mapbox.places/"
    url = "{}{}.json?limit=1&country=IT&access_token={}".format(
        mapbox_geocoding_v5,
        urllib.parse.quote(indirizzo, safe=""),
        token,
    )
    response = requests.get(url)
    data = response.json()
    feature = data["features"][0]
    if "address" in feature["place_type"]:
        if "Torino Turin" in feature["place_name"] or "Collegno" in feature["place_name"]:
            return feature["center"]
    return None


@functools.lru_cache(maxsize=128)
def geocoding(indirizzo, token):
    # sostituiamo i sc. con scala per farli piacere a mapbox
    indirizzo = indirizzo.replace(" sc. ", " scala ")
    posizione = do_geocoding(indirizzo, token)
    if posizione:
        return posizione

    # se non abbiamo trovato l'indirizzo proviamo a sistemarlo a mano
    correzione = [(k, v) for k, v in ESPANDI_INDIRIZZO.items() if k in indirizzo]
    if correzione:
        via, via_corretta = correzione[0]
        indirizzo_corretto = indirizzo.replace(via, via_corretta)
        posizione = do_geocoding(indirizzo_corretto, token)
        if posizione:
            return posizione

    print("Geocoding fallito per {}".format(indirizzo), file=sys.stderr)
    return None


if __name__ == '__main__':

    # se abbiamo un token di mapbox nell'environment facciamo il geocoding degli indirizzi
    mapbox_token = os.getenv("MAPBOX_ACCESS_TOKEN")

    documento = {
        'aggiornamento': None,
        'circoscrizione_numero': None,
        'circoscrizione_nome': None,
        'mmg': None,
        'dottori': None,
    }
    dottori = []
    dottore = None
    blocco_associazione = False
    blocco_note = False
    indirizzo = None

    for line in fileinput.input():

        line = line.strip('\x0c')
        if not line.strip():
            continue

        match = AGGIORNAMENTO_RE.match(line)
        if match:
            match_dict = match.groupdict()
            update = datetime.date(
                int(match_dict['anno']),
                MESI[match_dict['mese'].lower()],
                int(match_dict['giorno'])
            )
            documento['aggiornamento'] = update.isoformat()
            continue

        match = CIRCOSCRIZIONE_RE.match(line)
        if match:
            match_dict = match.groupdict()
            documento['circoscrizione_numero'] = match_dict['numero']
            documento['circoscrizione_nome'] = match_dict['nome']
            continue

        match = MMG_RE.match(line)
        if match:
            documento['mmg'] = True
            continue

        match = NOME_DOTTORE_RE.match(line)
        if match:
            match_dict = match.groupdict()
            blocco_note = False
            if dottore:
                dottore['indirizzi'].append(indirizzo)
                dottori.append(dottore)
                indirizzo = None

            dottore = {
                'nome': match_dict['nome'],
                'codice': match_dict['codice'],
                'associazione': [],
                'indirizzi': [],
            }
            continue

        match = BLOCCO_ASSOCIAZIONE_RE.match(line)
        if match:
            blocco_associazione = True
            continue

        match = INDIRIZZO_RE.match(line)
        if match:
            match_dict = match.groupdict()
            blocco_note = False
            blocco_associazione = False
            if indirizzo:
                dottore['indirizzi'].append(indirizzo)
            indirizzo = {
                'indirizzo': '{} {} TORINO'.format(match_dict['indirizzo'], match_dict['cap']),
                'telefono': [match_dict['telefono']],
                'giorni': [],
                'ore': [],
                'note': [],
            }
            continue

        # ci sono dottori senza associazione
        if blocco_associazione:
            dottore['associazione'].append(line.strip())
            continue

        match = FAX_RE.match(line)
        if match:
            continue

        match = TELEFONO_RE.match(line)
        if match:
            match_dict = match.groupdict()
            indirizzo['telefono'].append(match_dict['telefono'])
            continue

        match = BLOCCO_ORARI_RE.match(line)
        if match:
            continue

        match = GIORNO_RE.match(line)
        if match:
            match_dict = match.groupdict()
            indirizzo['giorni'].append(match_dict['giorno'])
            continue

        match = ORARI_DA_RE.match(line)
        if match:
            continue

        match = ORARIO_RE.match(line)
        if match:
            match_dict = match.groupdict()
            indirizzo['ore'].append(match_dict['orario'])
            continue

        match = ORARI_A_RE.match(line)
        if match:
            continue

        match = BLOCCO_NOTE_RE.match(line)
        if match:
            blocco_note = True
            continue

        if blocco_note:
            indirizzo['note'].append(line.strip())
            continue

        print(line, file=sys.stderr)

    # l'ultimo dottore
    if dottore:
        dottore['indirizzi'].append(indirizzo)
        dottori.append(dottore)
        indirizzo = None

    for dottore in dottori:
        for indirizzo in dottore['indirizzi']:
            # Proviamo a sistemare gli orari
            num_orari = len(indirizzo['ore']) / 2
            indirizzo['orario_affidabile'] = num_orari == len(indirizzo['giorni'])
            num_orari = int(num_orari)
            orari = [(indirizzo['ore'][i], indirizzo['ore'][i+num_orari]) for i in range(num_orari)]
            if indirizzo['orario_affidabile']:
                indirizzo['orari'] = [
                    {'giorno': giorno, 'da': orario[0], 'a': orario[1]}
                        for giorno, orario in zip(indirizzo['giorni'], orari)
                ]
            else:
                indirizzo['orari'] = [{'giorno': None, 'da': da, 'a': a} for da, a in orari]

            if mapbox_token:
                posizione = geocoding(indirizzo['indirizzo'], mapbox_token)
                indirizzo['posizione'] = posizione

    documento['dottori'] = dottori
    print(json.dumps(documento))


class ParseTestCase(unittest.TestCase):
    def test_nome_dottore_deve_fare_il_match_degli_apostrofi(self):
        match = NOME_DOTTORE_RE.match("NUR ADDO' [01234]")
        match_dict = match.groupdict()
        self.assertEqual(match_dict, {"nome": "NUR ADDO'", "codice": "01234"})
