"""Baut eine Wiki-Datei, die so aussieht, wie MWS sie ausliefert.

MWS nimmt simplewiki.html, setzt als erstes Element nach dem Kopf einen
script-Block der Klasse tiddlywiki-tiddler-store mit den Tiddlern des
Wikis und liefert die Seite aus. Diese Datei macht genau das - ohne
Server, damit der Browser die Datei per Doppelklick oeffnen kann.

Warum erzeugt und nicht gespeichert:
    Eine mitgecheckte Kopie von simplewiki.html waere bei der naechsten
    Aenderung an der Datei still veraltet, und niemand merkt es, bis
    ein Test etwas anderes prueft als gedacht. Deshalb wird die Datei
    bei Bedarf gebaut und nicht dem Repository anvertraut.

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
import re
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy                                             # noqa: E402

HIN = os.path.dirname(os.path.abspath(__file__))
PROJEKT = os.path.dirname(HIN)
QUELLE = os.path.join(PROJEKT, 'simplewiki.html')

MARKER_KLASSE = mkcopy.MARKER_KLASSE


def _marker_tauschen(html, marker):
    """Das Element direkt nach </head> durch 'marker' ersetzen.

    'marker' ist der ganze Element-Text oder None, um es zu entfernen.
    Gesucht wird nicht nach dem Klassennamen - der steht auch im
    Kommentar -, sondern nach dem Element, das dort wirklich steht.
    """
    head_at = mkcopy._echte_tags(html)[0] + len('</head>')
    vorhanden = re.match(r'\s*<script class="' + re.escape(MARKER_KLASSE) +
                         r'"[^>]*>[\s\S]*?</' + 'script>', html[head_at:])
    if not vorhanden:
        return (html[:head_at] + '\n' + marker + html[head_at:]) if marker else html
    a = head_at + vorhanden.start()
    b = head_at + vorhanden.end()
    return html[:a] + (marker + '\n' if marker else '') + html[b:]


def einsetzen(html, tiddler, marker_leer=False):
    """Den leeren Platzhalter-Marker durch die Tiddler ersetzen.

    simplewiki.html bringt den Marker schon mit - leer, als erstes
    Element nach </head>. MWS schreibt die Tiddler an seine Stelle; hier
    wird genauso verfahren. Wuerde der Marker nur davor gesetzt, stuende
    er zweimal im Dokument, und querySelector naehme den falschen.

    Die echte Head-Grenze wird gesucht, nicht die erste Zeichenkette
    "</head>": im Dokument steht das Wort auch im Kommentar, und dort
    gehoert der Marker nicht hin.
    """
    inhalt = [] if marker_leer else list(tiddler or [])
    koerper = json.dumps(inhalt, ensure_ascii=False).replace('<', '\\u003c')
    return _marker_tauschen(html, '<script class="' + MARKER_KLASSE + '" '
                                 'type="application/json">' + koerper + '</' + 'script>')


def entfernen(html):
    """Den Marker ganz rausnehmen - die Datei, wie man sie oeffnet."""
    return _marker_tauschen(html, None)


def bauen(name, tiddler, skript='', vorab='', marker_leer=False,
          marker_keiner=False, ersetzungen=None):
    """Fixture schreiben und ihren Pfad zurueckgeben.

    marker_leer   ein Marker, dessen Array leer ist
    marker_keiner gar kein Marker - die Datei, wie man sie per
                  Doppelklick oeffnet
    """
    with io.open(QUELLE, encoding='utf-8') as fh:
        html = fh.read()
    for a, b in (ersetzungen or []):
        html = html.replace(a, b)
    html = entfernen(html) if marker_keiner else einsetzen(html, tiddler, marker_leer)
    html = mkcopy.hauptskripte(html, pre=vorab, script=skript)
    return mkcopy.build_roh(name, html)


def beispiel_tiddler():
    """Drei Tiddler: Startseite, eine verlinkte Seite, ein Systemtiddler."""
    return [
        {'title': 'b1', 'caption': 'Erste Seite', 'text': '# Erste\n\nSiehe [[Zweite Seite]].',
         'tags': '[[beispiel]]', 'created': '20260704120000000',
         'modified': '20260704120000000', 'reihenfolge': '0001',
         'thema': 'dark', 'sprache': 'en'},
        {'title': 'b2', 'caption': 'Zweite Seite',
         'text': '# Zweite\n\nZurück mit [Text](wiki:b1) und [[Erste Seite]].',
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
    # Der Marker endet genau an der Head-Grenze. Gesucht wird deshalb
    # rueckwaerts vor ihr: dieselbe Zeichenkette steht weiter oben im
    # Vertrag, und gezeigt werden soll der Marker, der wirklich im
    # Dokument steht.
    ab = mkcopy._echte_tags(html)[0]
    i = html.rfind('<script class="' + MARKER_KLASSE + '"', 0, ab)
    j = html.find('</' + 'script>', i)
    if i < 0:
        print('FEHLER: kein Marker gefunden')
        return 1
    print('Groesse: %d Bytes' % len(html.encode('utf-8')))
    print()
    print('Der Block, den ein Server statt des Platzhalters setzt:')
    print(html[i:j + len('</' + 'script>')])
    print()
    print('Danach geht es weiter mit:')
    rest = html[j + len('</' + 'script>'):].lstrip()
    print(rest[:120].replace('\n', ' '))


if __name__ == '__main__':
    main()