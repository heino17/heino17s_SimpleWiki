"""Baut eine Wiki-Datei, die so aussieht, wie MWS sie ausliefert.

MWS nimmt simplewiki.html und stellt an den Store-Punkt einen
script-Block mit den Tiddlern des Wikis, einen Aufruf $tw.preloadTiddler
je Tiddler. Der Aufbau, der die Aufrufe entgegennimmt, steht mit in der
Datei. Diese Fixture macht genau das - ohne Server, damit der Browser
die Datei per Doppelklick oeffnen kann.

Warum erzeugt und nicht gespeichert:
    Eine mitgecheckte Kopie von simplewiki.html waere bei der naechsten
    Aenderung an der Datei still veraltet, und niemand merkt es, bis
    ein Test etwas anderes prueft als gedacht. Deshalb wird die Datei
    bei Bedarf gebaut und nicht dem Repository anvertraut.

Ohne Tiddler bleibt die Datei unveraendert: das ist die Datei, wie man
sie per Doppelklick oeffnet, und genau so verhaelt sie sich - der
Aufbau fuehlt keine Tiddler, also bleibt alles im Browser.

Aufrufen:

    python3 tests/mwsfixture.py            # Beispiel erzeugen und zeigen
    python3 tests/mwsfixture.py --out tests/fixtures/beispiel.html

In den Tests:

    pfad = bauen('_mws_datei.html', TIDDLER, skript=...)

Was die Beispieldatei zeigt, steht in tests/mwsserver.py - dort steht
derselbe Aufbau als laufender Server, mit dem Unterschied, dass dort
auch geschrieben werden kann.
"""

import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy                                             # noqa: E402

HIN = os.path.dirname(os.path.abspath(__file__))
PROJEKT = os.path.dirname(HIN)
QUELLE = os.path.join(PROJEKT, 'simplewiki.html')

STORE_PUNKT = mkcopy.STORE_PUNKT


def einsetzen(html, tiddler):
    """Die Tiddler als $tw.preloadTiddler-Aufrufe vor den Store-Punkt setzen.

    Genau an der Stelle und in genau der Form, in der MWS es tut: ein
    script-Block unmittelbar vor dem Punkt, ein Aufruf je Tiddler, JSON
    mit '<' als \\u003c.

    Ohne Tiddler wird nichts eingesetzt. Die Datei bleibt damit die
    Datei fuer den Doppelklick - der Aufbau im Kopf laeuft, fuehrt aber
    keine Tiddler zu.
    """
    aufrufe = ''.join(
        '$tw.preloadTiddler(%s);\n' % json.dumps(t, ensure_ascii=False).replace('<', '\\u003c')
        for t in list(tiddler or []))
    if not aufrufe:
        return html
    i = html.index(STORE_PUNKT)
    return html[:i] + '<script>\n' + aufrufe + '</' + 'script>\n' + html[i:]


def bauen(name, tiddler, skript='', vorab='', ersetzungen=None):
    """Fixture schreiben und ihren Pfad zurueckgeben."""
    with io.open(QUELLE, encoding='utf-8') as fh:
        html = fh.read()
    for a, b in (ersetzungen or []):
        html = html.replace(a, b)
    html = einsetzen(html, tiddler)
    html = mkcopy.hauptskripte(html, pre=vorab, script=skript)
    return mkcopy.build_roh(name, html)


def beispiel_tiddler():
    """Drei Tiddler: Startseite, eine verlinkte Seite, ein Systemtiddler."""
    return [
        {'title': 'b1', 'text': '# Erste\n\nSiehe [[Zweite Seite]].',
         'tags': '[[beispiel]]', 'created': '20260704120000000',
         'modified': '20260704120000000', 'reihenfolge': '0001',
         'thema': 'dark', 'sprache': 'en'},
        {'title': 'b2', 'text': '# Zweite\n\nZurück mit [Text](wiki:b1) und [[Erste Seite]].',
         'tags': '', 'created': '20260704120100000',
         'modified': '20260704120100000', 'reihenfolge': '0000'},
        {'title': '$:/DefaultTiddlers', 'text': 'b1'},
        {'title': '$:/SiteTitle', 'text': 'Beispielwiki'},
        {'title': '$:/bag-info', 'text': '{"bag":"default"}'},
    ]


def main():
    ziel = os.path.join(HIN, '_kopien', '_mws_beispiel.html')
    for arg in sys.argv[1:]:
        if arg.startswith('--out='):
            ziel = arg.split('=', 1)[1]
        elif arg == '--out' and sys.argv.index(arg) + 1 < len(sys.argv):
            ziel = sys.argv[sys.argv.index(arg) + 1]

    pfad = bauen(os.path.basename(ziel), beispiel_tiddler())
    if os.path.abspath(pfad) != os.path.abspath(ziel):
        with io.open(pfad, encoding='utf-8') as fh:
            html = fh.read()
        with io.open(ziel, 'w', encoding='utf-8') as fh:
            fh.write(html)

    print('geschrieben: ' + ziel)
    with io.open(ziel, encoding='utf-8') as fh:
        html = fh.read()
    i = html.rfind('<script>\n$tw.preloadTiddler', 0, html.index(STORE_PUNKT))
    j = html.index('</' + 'script>', i)
    if i < 0:
        print('FEHLER: kein Store-Block gefunden')
        return 1
    print('Groesse: %d Bytes' % len(html.encode('utf-8')))
    print()
    print('Der Block, den ein Server vor dem Punkt setzt:')
    print(html[i:j + len('</' + 'script>')])
    print()
    print('Danach geht es weiter mit:')
    rest = html[j + len('</' + 'script>'):].lstrip()
    print(rest[:120].replace('\n', ' '))


if __name__ == '__main__':
    main()
