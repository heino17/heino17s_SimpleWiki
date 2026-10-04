"""Alle Tests nacheinander ausfuehren.

    python3 tests/alle.py            # alles
    python3 tests/alle.py fluss      # nur die Tests mit "fluss" im Namen

Endcode 0 heisst: alles bestanden. Endcode 1 heisst: mindestens
eine Pruefung ist fehlgeschlagen - dann lohnt der Blick in die
Ausgabe, die den Namen der Pruefung nennt.
"""

import os
import re
import subprocess
import sys

HIN = os.path.dirname(os.path.abspath(__file__))

# Reihenfolge von innen nach aussen: erst das Kleine, dann das Ganze.
REIHENFOLGE = [
    't_empty.py',      # Leerzustand
    't_suite.py',      # Oberflaeche, Suche, Editor
    't_link4.py',      # Verlinken
    't_dup.py',        # Kopieren
    't_dupen.py',      # Kopieren, englisch
    't_wikisyn.py',    # [[Seite]] und [[Text|Seite]]
    't_refs.py',       # Verweis-Panel
    't_kopf.py',        # Knopf im Kopf: Fluss umschalten, schmale Fenster
    't_order.py',      # Reihenfolge per Ziehen
    't_file.py',       # Als Datei sichern und laden
    't_mws.py',        # Austausch mit MWS: JSON, Version, Fremdfelder
    't_mwsmode.py',    # Betrieb auf einem MWS-Server: Marker, Speicher, 403
    't_speicher.py',   # Eine Abstraktion, zwei Auspraegungen
    't_mwsdatei.py',   # MWS-Modus an einer Datei: Auswahl am Marker, Verweise
    't_abnahme.py',    # Abnahme: ohne Netz, mit Marker, nach dem Neuladen
    't_leerwiki.py',   # Leere Wiki-Datei, Vorlage fuellen und oeffnen
    't_export.py',     # Die gesicherte Datei wirklich oeffnen
    't_fluss.py',      # Fluss und Druckansicht
    't_scroll.py',     # Scrollen und Druck ueber Blaetter
]

BESCHRIEBUNG = {
    't_empty.py': 'Leerzustand, wenn keine Seite da ist',
    't_suite.py': 'Grundfunktionen der Oberflaeche',
    't_link4.py': 'Verlinken: Dialog, Anlegen, Rueckverweise',
    't_dup.py': 'Kopieren einer Seite',
    't_dupen.py': 'Kopieren in englischer Oberflaeche',
    't_wikisyn.py': 'TiddlyWiki-Syntax [[Seite]]',
    't_refs.py': 'Verweis-Panel mit Zaehler und Speichern',
    't_kopf.py': 'Fluss-Knopf im Kopf, Reihenfolge, schmale Fenster',
    't_order.py': 'Reihenfolge per Ziehen und Alt + Pfeil',
    't_file.py': 'Wiki als Datei sichern und laden',
    't_mws.py': 'Austauschformat: JSON, Version, fremde Felder, doppelte Titel',
    't_mwsmode.py': 'Serverbetrieb: Marker, Speicher, Schreiben, 403, leerer Marker',
    't_speicher.py': 'Speicherabstraktion: gleicher Vertrag, Browser und Server',
    't_mwsdatei.py': 'MWS an einer Datei: Auswahl am Marker, Verweise, kein Schreiben',
    't_abnahme.py': 'Abnahme: kein Nachladen, Doppelklick ohne Netz, Aenderung bleibt',
    't_leerwiki.py': 'Leere Wiki-Datei als Vorlage, Angaben oben, der Weg zurueck',
    't_export.py': 'Die gesicherte Datei wirklich oeffnen',
    't_fluss.py': 'Fluss und Druckansicht',
    't_scroll.py': 'Scrollen im Fluss, Druck ueber Blaetter',
}


def main():
    filtertext = sys.argv[1] if len(sys.argv) > 1 else ''
    dateien = [d for d in REIHENFOLGE if filtertext in d]

    if not dateien:
        print('Kein Test passt zu "%s".' % filtertext)
        print('Vorhanden: ' + ', '.join(REIHENFOLGE))
        return 1

    print('SimpleWiki – Tests')
    print('=================')
    print()
    gesamt_ok = 0
    gesamt_fehler = 0
    ergebnisse = []

    for name in dateien:
        pfad = os.path.join(HIN, name)
        if not os.path.exists(pfad):
            print('FEHLT: ' + name)
            gesamt_fehler += 1
            continue
        print('--- ' + name + '  (' + BESCHRIEBUNG.get(name, '') + ')')
        lauf = subprocess.run([sys.executable, pfad],
                              capture_output=True, text=True,
                              timeout=1800)   # der MWS-Test startet einen Server
        ausgabe = lauf.stdout
        # Die Reports der Tests sind ausfuehrlich; hier nur die Fazits.
        for zeile in ausgabe.split('\n'):
            # Auch die Zeilen zeigen, die kein Pruefergebnis sind, sondern
            # eine Auswertung: "KEIN REPORT" und "UNVOLLSTAENDIG" sagen,
            # dass der Browser zu langsam war - genau das, was man sonst
            # nicht sieht und fuer einen Programmbug haelt.
            if re.match(r'^(>>>|\s{4}(OK|FAIL)|.*FEHLGESCHLAGEN|.*BESTANDEN'
                        r'|.*KEIN REPORT|.*UNVOLLSTAENDIG|GESAMT)', zeile):
                print(zeile)
        # Jeder Test meldet am Ende "GESAMT: N bestanden, M fehlgeschlagen";
        # das ist die Zahl, die zaehlt - nicht die Zeilen im Bericht.
        for m2 in re.finditer(r'GESAMT: (\d+) bestanden, (\d+) fehlgeschlagen', ausgabe):
            gesamt_ok += int(m2.group(1))
            gesamt_fehler += int(m2.group(2))
        if lauf.returncode and not gesamt_fehler:
            gesamt_fehler += 1
        ergebnisse.append((name, lauf.returncode == 0))
        if lauf.stderr.strip():
            print('  (Ausgabe auf stderr: ' + lauf.stderr.strip().split('\n')[0][:80] + ')')
        print()

    print('=================')
    for name, ok in ergebnisse:
        print('%-16s %s' % (name, 'ok' if ok else 'FEHLGESCHLAGEN'))
    print()
    print('GESAMT: %d Pruefungen bestanden, %d fehlgeschlagen' % (gesamt_ok, gesamt_fehler))
    return 1 if gesamt_fehler else 0


if __name__ == '__main__':
    sys.exit(main())