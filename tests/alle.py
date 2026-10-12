"""Alle Tests ausfuehren - mehrere gleichzeitig.

    python3 tests/alle.py            # alles
    python3 tests/alle.py fluss      # nur die Tests mit "fluss" im Namen
    python3 tests/alle.py -j 1       # nacheinander, wie frueher
    python3 tests/alle.py -j 8       # acht gleichzeitig

Endcode 0 heisst: alles bestanden. Endcode 1 heisst: mindestens
eine Pruefung ist fehlgeschlagen - dann lohnt der Blick in die
Ausgabe, die den Namen der Pruefung nennt.

Jeder Test ist ein eigener Prozess: er baut seine eigene Kopie der
Wiki und oeffnet sein eigenes Browserfenster. Deshalb koennen sie
gleichzeitig laufen. Die Voreinstellung ist die Zahl der Prozessoren
(hoechstens acht); -j stellt sie ein. Der Bericht steht trotzdem in
der Reihenfolge von REIHENFOLGE da, damit zwei Laeufe vergleichbar
bleiben - oben laufen nur die Fortschrittszeilen.
"""

import concurrent.futures
import os
import re
import subprocess
import sys
import time

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
    't_tags.py',       # Schlagworte: Pillen, Register, Bearbeiten
    't_kopf.py',        # Knopf im Kopf: Fluss umschalten, schmale Fenster
    't_menue.py',       # Inhaltsverzeichnis links als Menue, am Faehnchen zu- und aufklappbar
    't_panels.py',      # Panels rechts: geparkt am Rand, nicht neben dem Fenster
    't_order.py',      # Reihenfolge per Ziehen
    't_hierarchie.py', # Verschachtelung: Ebenen, Ziehen in drei Zonen, Alt + Pfeil
    't_klapp.py',      # Verzeichnis auf- und zuklappen: Zaehler, Pfeile, Suche
    't_abbrechen.py',  # Anlegen und Abbrechen: die Huellseite verschwindet wieder
    't_file.py',       # Als Datei sichern und laden
    't_mws.py',        # Austausch mit MWS: JSON, Version, Fremdfelder
    't_mwsmode.py',    # Betrieb auf einem MWS-Server: Marker, Speicher, 403
    't_anmeldung.py',  # Anmeldung und Schreibrechte: Status, Kopf, ausgeblendete Knoepfe
    't_login.py',      # Anmelden und abmelden: Link zum Server, POST /logout
    't_speicher.py',   # Eine Abstraktion, zwei Auspraegungen
    't_mwsdatei.py',   # MWS-Modus an einer Datei: Auswahl am Marker, Verweise
    't_abnahme.py',    # Abnahme: ohne Netz, mit Marker, nach dem Neuladen
    't_leerwiki.py',   # Leere Wiki-Datei, Vorlage fuellen und oeffnen
    't_export.py',     # Die gesicherte Datei wirklich oeffnen
    't_finger.py',     # Fingerabdruck: eine andere Datei gewinnt ohne Speicher leeren
    't_fluss.py',      # Fluss und Druckansicht
    't_scroll.py',     # Scrollen und Druck ueber Blaetter
    't_textur.py',     # Die Textur kommt in beiden Modi an
    't_palette.py',    # Farbwelten: Auswahl, Hell/Dunkel darin, Austausch
    't_farbwelt.py',   # Die eigene Farbwelt: klonen, aendern, behalten
    't_sprachen.py',   # Sprachauswahl: alle Sprachen, jede uebersetzt
    't_bild.py',       # Bild nach leeren Absaetzen: <br>-Blöcke aus dem Editor trennen
    't_umbruch.py',    # Ein einzelner Zeilenumbruch bleibt ein Umbruch
]

BESCHRIEBUNG = {
    't_empty.py': 'Leerzustand, wenn keine Seite da ist',
    't_suite.py': 'Grundfunktionen der Oberflaeche',
    't_link4.py': 'Verlinken: Dialog, Anlegen, Rueckverweise',
    't_dup.py': 'Kopieren einer Seite',
    't_dupen.py': 'Kopieren in englischer Oberflaeche',
    't_wikisyn.py': 'TiddlyWiki-Syntax [[Seite]]',
    't_refs.py': 'Verweis-Panel mit Zaehler und Speichern',
    't_tags.py': 'Schlagworte: Pillen, Register, Bearbeiten, Ablehnung',
    't_kopf.py': 'Fluss-Knopf im Kopf, Reihenfolge, schmale Fenster',
    't_menue.py': 'Inhaltsverzeichnis links als Menue, Faehnchen, kein Loeschkreuz',
    't_panels.py': 'Panels rechts: geparkt genau auf der Fensterkante',
    't_order.py': 'Reihenfolge per Ziehen und Alt + Pfeil',
    't_hierarchie.py': 'Verschachtelung: Ebenen, drei Zonen beim Ziehen, Alt + Pfeil',
    't_klapp.py': 'Verzeichnis auf- und zuklappen: Zaehler, Pfeile, Suche hebt die Deckung auf',
    't_abbrechen.py': 'Huellseite beim Anlegen: Abbrechen und Wegklicken nehmen sie zurueck, Sichern macht sie dauerhaft',
    't_file.py': 'Wiki als Datei sichern und laden',
    't_mws.py': 'Austauschformat: JSON, Version, fremde Felder, doppelte Titel',
    't_mwsmode.py': 'Serverbetrieb: Marker, Speicher, Schreiben, 403, leerer Marker',
    't_anmeldung.py': 'Anmeldung und Schreibrechte: Status, Name, ausgeblendete Knoepfe',
    't_login.py': 'Anmelden und abmelden: Link auf /login, POST /logout, Fehlerfall',
    't_speicher.py': 'Speicherabstraktion: gleicher Vertrag, Browser und Server',
    't_mwsdatei.py': 'MWS an einer Datei: Auswahl am Marker, Verweise, kein Schreiben',
    't_abnahme.py': 'Abnahme: kein Nachladen, Doppelklick ohne Netz, Aenderung bleibt',
    't_leerwiki.py': 'Leere Wiki-Datei als Vorlage, Angaben oben, der Weg zurueck',
    't_export.py': 'Die gesicherte Datei wirklich oeffnen',
    't_finger.py': 'Fingerabdruck: eine andere Datei gewinnt ohne Speicher leeren',
    't_fluss.py': 'Fluss und Druckansicht',
    't_scroll.py': 'Scrollen im Fluss, Druck ueber Blaetter',
    't_textur.py': 'Textur im Kopf, im Text und im Verzeichnis - hell und dunkel',
    't_palette.py': 'Farbwelten: Auswahl, Hell und Dunkel darin, Austausch',
    't_farbwelt.py': 'Die eigene Farbwelt: klonen, einzelne Werte aendern, behalten',
    't_sprachen.py': 'Sprachauswahl: alle Sprachen im Dropdown, jede uebersetzt die Oberflaeche',
    't_bild.py': 'Bild nach leeren Absaetzen: <br>-Blöcke aus dem Editor trennen',
    't_umbruch.py': 'Ein einzelner Zeilenumbruch bleibt ein Umbruch',
}


def _stellen():
    """Wie viele Tests gleichzeitig? Voreinstellung: die Zahl der Prozessoren.

    Oben gedeckelt: jeder Test startet ein Chromium, und mehr als acht
    Browser gleichzeitig bringen keinen Gewinn mehr, sondern nur noch
    Gedraenge um Speicher und Prozessorzeit.
    """
    return max(1, min(os.cpu_count() or 4, 8))


def _arg(argv):
    """Filtertext und Stellenzahl aus der Kommandozeile lesen.

    Erlaubt sind 'flug' (Filter, wie bisher), '-j N' und '--jobs=N'.
    Ohne Angabe gilt _stellen().
    """
    jobs = _stellen()
    filtertext = ''
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ('-j', '--jobs') and i + 1 < len(argv):
            try:
                jobs = int(argv[i + 1])
            except ValueError:
                pass
            i += 2
            continue
        if a.startswith('--jobs='):
            try:
                jobs = int(a.split('=', 1)[1])
            except ValueError:
                pass
        elif a.startswith('-j') and len(a) > 2:
            try:
                jobs = int(a[2:])
            except ValueError:
                pass
        elif not a.startswith('-'):
            filtertext = a
        i += 1
    return filtertext, max(1, jobs)


def _einer(name):
    """Einen Test als eigenen Prozess laufen lassen.

    Rueckgabe ist ein kleiner Bericht: Name, was auf stdout und stderr
    stand, der Fehlercode und die Dauer. Fehlt die Datei, wird das so
    gemeldet wie im sequentiellen Lauf.
    """
    pfad = os.path.join(HIN, name)
    if not os.path.exists(pfad):
        return {'name': name, 'fehlt': True, 'ausgabe': '', 'stderr': '',
                'code': 1, 'dauer': 0.0}
    start = time.time()
    try:
        lauf = subprocess.run([sys.executable, pfad],
                              capture_output=True, text=True,
                              timeout=1800)   # der MWS-Test startet einen Server
    except subprocess.TimeoutExpired:
        # Ein haengender Test soll nicht den ganzen Lauf mitreissen -
        # er zaehlt als fehlgeschlagen, die anderen laufen weiter.
        return {'name': name, 'fehlt': False, 'ausgabe': '',
                'stderr': 'Zeitueberschreitung nach 1800s', 'code': 1,
                'dauer': time.time() - start}
    return {'name': name, 'fehlt': False, 'ausgabe': lauf.stdout,
            'stderr': lauf.stderr, 'code': lauf.returncode,
            'dauer': time.time() - start}


def main():
    filtertext, jobs = _arg(sys.argv[1:])
    dateien = [d for d in REIHENFOLGE if filtertext in d]

    if not dateien:
        print('Kein Test passt zu "%s".' % filtertext)
        print('Vorhanden: ' + ', '.join(REIHENFOLGE))
        return 1

    print('SimpleWiki – Tests')
    print('=================')
    print()
    print('%d Dateien, %d gleichzeitig.' % (len(dateien), min(jobs, len(dateien))))
    print()

    # Erst laufen lassen, dann der Reihe nach ausgeben. Die
    # Fortschrittszeile erscheint, sobald eine Datei fertig ist -
    # welcher Test wie lange braucht, steht also da, bevor der
    # Bericht beginnt.
    laeufe = {}
    fertig = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        auftraege = {pool.submit(_einer, n): n for n in dateien}
        for auftrag in concurrent.futures.as_completed(auftraege):
            ergebnis = auftrag.result()
            laeufe[ergebnis['name']] = ergebnis
            fertig += 1
            if ergebnis['fehlt']:
                stand = 'FEHLT'
            elif ergebnis['code'] == 0:
                stand = 'ok'
            else:
                stand = 'FEHLGESCHLAGEN'
            print('  [%2d/%2d] %-16s %-14s %5.1fs'
                  % (fertig, len(dateien), ergebnis['name'], stand,
                     ergebnis['dauer']))
    print()

    gesamt_ok = 0
    gesamt_fehler = 0
    ergebnisse = []

    for name in dateien:
        ergebnis = laeufe[name]
        if ergebnis['fehlt']:
            print('FEHLT: ' + name)
            gesamt_fehler += 1
            ergebnisse.append((name, False))
            print()
            continue
        print('--- ' + name + '  (' + BESCHRIEBUNG.get(name, '') + ')')
        # Die Reports der Tests sind ausfuehrlich; hier nur die Fazits.
        for zeile in ergebnis['ausgabe'].split('\n'):
            # Auch die Zeilen zeigen, die kein Pruefergebnis sind, sondern
            # eine Auswertung: "KEIN REPORT" und "UNVOLLSTAENDIG" sagen,
            # dass der Browser zu langsam war - genau das, was man sonst
            # nicht sieht und fuer einen Programmbug haelt.
            if re.match(r'^(>>>|\s{4}(OK|FAIL)|.*FEHLGESCHLAGEN|.*BESTANDEN'
                        r'|.*KEIN REPORT|.*UNVOLLSTAENDIG|GESAMT)', zeile):
                print(zeile)
        # Jeder Test meldet am Ende "GESAMT: N bestanden, M fehlgeschlagen";
        # das ist die Zahl, die zaehlt - nicht die Zeilen im Bericht.
        for m2 in re.finditer(r'GESAMT: (\d+) bestanden, (\d+) fehlgeschlagen',
                              ergebnis['ausgabe']):
            gesamt_ok += int(m2.group(1))
            gesamt_fehler += int(m2.group(2))
        if ergebnis['code'] and not gesamt_fehler:
            gesamt_fehler += 1
        ergebnisse.append((name, ergebnis['code'] == 0))
        if ergebnis['stderr'].strip():
            print('  (Ausgabe auf stderr: '
                  + ergebnis['stderr'].strip().split('\n')[0][:80] + ')')
        print()

    print('=================')
    for name, ok in ergebnisse:
        print('%-16s %s' % (name, 'ok' if ok else 'FEHLGESCHLAGEN'))
    print()
    print('GESAMT: %d Pruefungen bestanden, %d fehlgeschlagen' % (gesamt_ok, gesamt_fehler))
    return 1 if gesamt_fehler else 0


if __name__ == '__main__':
    sys.exit(main())