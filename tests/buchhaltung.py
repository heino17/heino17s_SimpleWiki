"""Die Buchhaltung: die wiederkehrenden Zahlen an einer Stelle herstellen.

Zwei Quellen, ein Befehl:

  - `simplewiki.html` selbst: wie lang die Datei ist und wo ihre Teile
    anfangen und aufhoeren, und welche Fassung das CHANGELOG nennt.
  - der letzte volle Suite-Lauf, den `alle.py` in
    `tests/_kopien/letzter_lauf.json` hinterlegt.

Geschrieben wird an diese Stellen:

  - `simplewiki.html`: `<meta name="mws-shell-version">`
  - `CHANGELOG.md`: die Fassung im Kopf und die Pruefungszahl der
    obersten Ueberschrift
  - `README.md`: die Pruefungszahl im Fliesstext, die Strukturtafel und
    die Fassung im Beispiel
  - `AGENTS.md`: Testdateien und Pruefungen

Aufruf:

    python3 tests/buchhaltung.py             # schreiben, was nicht stimmt
    python3 tests/buchhaltung.py --check     # nur melden (Endcode 1 = veraltet)
    python3 tests/buchhaltung.py --pruefungen 1030   # ohne letzten Lauf

Die Fassung kommt aus der obersten `### vX.Y.Z`-Ueberschrift des
CHANGELOG. Wer eine neue Fassung will, schreibt sie dort samt
Beschreibung hin und laesst dieses Werkzeug den Rest nachtragen.

Nicht angefasst werden die Pruefungszahlen der aelteren Ueberschriften:
das ist die Geschichte, nicht der Stand.
"""

import importlib
import json
import os
import re
import sys

HIN = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.dirname(HIN)

HTML = os.path.join(WURZEL, 'simplewiki.html')
CHRONIK = os.path.join(WURZEL, 'CHANGELOG.md')
README = os.path.join(WURZEL, 'README.md')
AGENTS = os.path.join(WURZEL, 'AGENTS.md')
BERICHT = os.path.join(HIN, '_kopien', 'letzter_lauf.json')

FASSUNG = re.compile(r'^### v(\d+\.\d+\.\d+)', re.M)
META = re.compile(r'(<meta name="mws-shell-version" content=")(v\d+\.\d+\.\d+)(")')
UEBERSCHRIFT = re.compile(r'^### (.*)$', re.M)
README_ZAHLEN = re.compile(r'\*\*(\d+) Testdateien\*\*, (\d+) Prüfungen')
AGENTS_STAND = re.compile(r'Stand: (\d+)\s*Testdateien, (\d+) Prüfungen')
README_LAENGE = re.compile(r'(`simplewiki\.html` ist )\d+( Zeilen lang)')
ANZAHL_AM_ENDE = re.compile(r'\s+—\s+\d+\s+Prüfungen\s*$')


def lies(pfad):
    with open(pfad, encoding='utf-8') as fh:
        return fh.read()


def spanne(a, b):
    return '%d–%d' % (a, b) if a != b else '%d' % a


def struktur(html):
    """Die Zeilenspannen der Teile aus der Datei selbst lesen.

    Kein Zaehlen von Hand: die Grenzen werden an ihren Merkmalen
    gesucht - die Kommentare schliessen mit `-->`, die Dateninsel am
    `id`, die Bibliotheken beginnen mit dem ersten `<script>` danach,
    das grosse Stylesheet ist das letzte `<style>` vor dem Store-Punkt,
    das Programm das letzte `<script>` der Datei.
    """
    z = html.splitlines()
    n = len(z)

    def finde(text, ab=0, genau=False):
        for i in range(ab, n):
            if (z[i].strip() == text) if genau else (text in z[i]):
                return i + 1
        raise LookupError('Merkmal nicht gefunden: %s' % text)

    daten = finde('id="simplewiki-daten"')
    kopf_ende = max(i + 1 for i in range(daten - 1) if z[i].rstrip().endswith('-->'))
    libs_start = finde('<script', daten)
    store = finde('class="simplewiki-store-point"')
    style_start = max(i + 1 for i in range(store - 1) if z[i].strip() == '<style>')
    style_ende = finde('</style>', style_start, genau=True)
    ui_start = finde('<div id="app"')
    prog_start = None
    for i in range(n - 1, -1, -1):
        if z[i].lstrip().startswith('<script') and 'simplewiki-daten' not in z[i] \
                and 'store-point' not in z[i]:
            prog_start = i + 1
            break
    if prog_start is None:
        raise LookupError('kein Programm-Script gefunden')
    ui_ende = prog_start - 1
    while ui_ende > ui_start and z[ui_ende - 1].strip() == '':
        ui_ende -= 1
    return {
        'spannen': [
            spanne(1, kopf_ende),
            spanne(daten, daten),
            spanne(libs_start, style_start - 1),
            spanne(style_start, style_ende),
            spanne(store, store),
            spanne(ui_start, ui_ende),
            spanne(prog_start, n),
        ],
        'gesamt': n,
    }


def tafel_zeile(zeile):
    """Ist das der Anfang einer Tafelzeile? Dann (Einrueckung, Spanne, Rest).

    Nur der Zeilenanfang der README-Tafel traegt eine Spanne; die
    Fortsetzungszeilen darunter beginnen mit Prosa. So findet das
    Ersetzen genau die Zahlen und laesst den Text, wo er steht.
    """
    m = re.match(r'^(\s*)(\d+(?:–\d+)?)(\s+)(\S.*)$', zeile)
    return m if m else None


def fassung(chronik):
    """Die oberste `### vX.Y.Z`-Ueberschrift - die eine Quelle der Fassung."""
    m = FASSUNG.search(chronik)
    return 'v' + m.group(1) if m else None


def mit_zahl(chronik, pruefungen):
    """Die Pruefungszahl an die oberste Ueberschrift schreiben."""
    m = UEBERSCHRIFT.search(chronik)
    if not m:
        return chronik, None
    titel = ANZAHL_AM_ENDE.sub('', m.group(1))
    neu = '%s — %d Prüfungen' % (titel, pruefungen)
    if neu == m.group(1):
        return chronik, None
    return chronik[:m.start(1)] + neu + chronik[m.end(1):], neu


def tafel_indexe(readme):
    """Die Zeilen der README und die Zeilennummern ihrer Tafelzeilen.

    Die Tafel steht zwischen zwei Zaeunen; ihre Zeilen beginnen mit
    einer Spanne. Findet das Skript die Tafel nicht, ist die Liste
    `None`.
    """
    zeilen = readme.split('\n')
    start = next((i for i, z in enumerate(zeilen)
                  if 'und hat diese Teile, immer in derselben' in z), None)
    if start is None:
        return zeilen, None
    auf = next((i for i in range(start, len(zeilen)) if zeilen[i].strip() == '```'), None)
    if auf is None:
        return zeilen, None
    zu = next((i for i in range(auf + 1, len(zeilen)) if zeilen[i].strip() == '```'), None)
    if zu is None:
        return zeilen, None
    return zeilen, [i for i in range(auf + 1, zu) if tafel_zeile(zeilen[i])]


def readme_spannen(readme):
    """Die Spannen, die in der README-Tafel stehen - oder None."""
    zeilen, stellen = tafel_indexe(readme)
    if stellen is None:
        return None
    return [tafel_zeile(zeilen[i]).group(2) for i in stellen]


def struktur_tauschen(readme, s):
    """Nur die Zahlen der README-Strukturtafel austauschen.

    Der Text der Tafel bleibt, wie er dasteht: ersetzt wird nur die
    Spanne am Anfang jeder Tafelzeile, in der Reihenfolge der Teile.
    Findet das Skript nicht genau so viele Zeilen, wie Teile bekannt
    sind, laesst es die Finger davon.
    """
    zeilen, stellen = tafel_indexe(readme)
    if stellen is None or len(stellen) != len(s['spannen']):
        return readme, None
    for i, nummer in zip(stellen, s['spannen']):
        alt = tafel_zeile(zeilen[i])
        zeilen[i] = '    %8s  %s' % (nummer, alt.group(4))
    neu = '\n'.join(zeilen)
    return (neu, 'Strukturtafel') if neu != readme else (readme, None)


def pruefungen_lesen(argument):
    """Die Pruefungszahl: aus --pruefungen, sonst aus dem letzten Lauf."""
    if argument is not None:
        return int(argument), None
    try:
        with open(BERICHT, encoding='utf-8') as fh:
            daten = json.load(fh)
        return int(daten['bestanden']), daten.get('dateien')
    except (OSError, ValueError, KeyError):
        return None, None


def main(argv):
    pruef_arg = None
    if '--pruefungen' in argv and argv.index('--pruefungen') + 1 < len(argv):
        pruef_arg = argv[argv.index('--pruefungen') + 1]
    nur_pruefen = '--check' in argv

    alle = importlib.import_module('alle')
    dateien = len(alle.REIHENFOLGE)

    pruefungen, gelaufene = pruefungen_lesen(pruef_arg)
    if pruefungen is None:
        print('Kein letzter Lauf gefunden. Erst `python3 tests/alle.py` laufen '
              'lassen oder --pruefungen N angeben.')
        return 2
    if gelaufene is not None and gelaufene != dateien:
        print('Warnung: der letzte Lauf hatte %d Dateien, die Suite zaehlt %d.'
              % (gelaufene, dateien))

    original = {pfad: lies(pfad) for pfad in (HTML, CHRONIK, README, AGENTS)}
    html, chronik, readme, agents = (original[HTML], original[CHRONIK],
                                     original[README], original[AGENTS])
    s = struktur(html)
    version = fassung(chronik)
    aenderungen = []

    def merke(datei, neu, was, alt):
        if neu != alt:
            aenderungen.append('%s: %s' % (os.path.basename(datei), was))

    if version is not None:
        def setze(m):
            return m.group(1) + version + m.group(3)
        # Nur das erste Vorkommen: das ist die geltende Zeile. Aeltere
        # Eintraege im CHANGELOG zitieren die Zeile mit der damaligen
        # Fassung - die Geschichte bleibt, wie sie war.
        neu = META.sub(setze, html, count=1)
        merke(HTML, neu, 'Fassung ' + version, html)
        html = neu
        neu = META.sub(setze, readme, count=1)
        merke(README, neu, 'Fassung ' + version, readme)
        readme = neu
        neu = META.sub(setze, chronik, count=1)
        merke(CHRONIK, neu, 'Fassung ' + version, chronik)
        chronik = neu
    else:
        print('Warnung: keine `### vX.Y.Z`-Ueberschrift im CHANGELOG - '
              'die Fassung bleibt, wie sie ist.')

    neu, was = mit_zahl(chronik, pruefungen)
    merke(CHRONIK, neu, was or 'Pruefungszahl', chronik)
    chronik = neu

    def setz_zahlen(m):
        return '**%d Testdateien**, %d Prüfungen' % (dateien, pruefungen)

    zahlen = '%d Testdateien, %d Prüfungen' % (dateien, pruefungen)
    neu = README_ZAHLEN.sub(setz_zahlen, readme)
    merke(README, neu, zahlen, readme)
    readme = neu
    # Der Umbruch in AGENTS geht ueber zwei Zeilen; er bleibt erhalten.
    neu = AGENTS_STAND.sub(
        lambda m: 'Stand: %d\nTestdateien, %d Prüfungen' % (dateien, pruefungen), agents)
    merke(AGENTS, neu, 'Stand: ' + zahlen, agents)
    agents = neu

    neu = README_LAENGE.sub(
        lambda m: m.group(1) + str(s['gesamt']) + m.group(2), readme)
    merke(README, neu, 'Dateilaenge %d' % s['gesamt'], readme)
    readme = neu
    neu, was = struktur_tauschen(readme, s)
    merke(README, neu, was or 'Strukturtafel', readme)
    readme = neu

    if not aenderungen:
        print('Die Buchhaltung stimmt: %d Testdateien, %d Prüfungen, Fassung %s.'
              % (dateien, pruefungen, version))
        return 0
    for a in aenderungen:
        print(('wuerde ' if nur_pruefen else '') + 'aendern: ' + a)
    if nur_pruefen:
        return 1

    neu_inhalt = {HTML: html, CHRONIK: chronik, README: readme, AGENTS: agents}
    for pfad, text in neu_inhalt.items():
        if text != original[pfad]:
            with open(pfad, 'w', encoding='utf-8') as fh:
                fh.write(text)
    print('%d Stellen geschrieben.' % len(aenderungen))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
