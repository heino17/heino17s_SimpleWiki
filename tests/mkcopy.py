"""Baut eine instrumentierte Testkopie von simplewiki.html.

Die Kopie bekommt:
  * ein Seed-Skript, das localStorage mit Testseiten fuellt
  * optional den Datenblock der Datei (fuer den Fall: Inhalt steckt
    nur in der Datei, der Browser ist leer)
  * das Testskript vor </body>
  * einen Testhaken, der den Markdown-Editor erreichbar macht

Die Pfade sind absichtlich relativ, damit das hier funktioniert,
egal wo der Ordner liegt.
"""

import io
import json
import os
import re
import sys

HIN = os.path.dirname(os.path.abspath(__file__))
PROJEKT = os.path.dirname(HIN)
SRC = os.path.join(PROJEKT, 'simplewiki.html')
KOPIEN = os.path.join(HIN, '_kopien')

# zusaetzliche Ersetzungen, die ein Test setzen kann
PRE_SCRIPT = ''
EXTRA_REPLACEMENTS = []

_SEED_VORHAGE = ('<script>try{localStorage.setItem("simplewiki_pages",%s);'
                'localStorage.setItem("simplewiki_theme","%s");'
                'localStorage.setItem("simplewiki_lang","%s");'
                'localStorage.setItem("simplewiki_startpage","%s");'
                # Auch das Verweis-Panel zuruecksetzen: sonst schleppt ein
                # früherer Testlauf seinen Zustand in den naechsten.
                'localStorage.setItem("simplewiki_refs","0");}'
                'catch(e){}</script>\n')

_DATENBLOCK = r'<script id="simplewiki-daten"[^>]*>[\s\S]*?</script>'

# Alles, was beim Suchen nach echten Tags beachtet werden muss:
# script- und style-Bloecke stehen im Rohtext, ihr Inhalt ist kein HTML.
# Kommentare ebenso: der Vertrag im Kopf nennt </head> und <body>, ohne
# dass damit etwas im Dokument zu tun waere.
_SCAN = re.compile(r'<!--[\s\S]*?-->|<script\b[^>]*>|</script\s*>|<style\b[^>]*>|</style\s*>'
                   r'|</head>|<body[^>]*>', re.I)


def _echte_tags(h):
    """Positionen der echten </head>, <body ...> und </body>.

    Die eingebetteten Bibliotheken enthalten die Zeichenkette
    '<head></head><body>' mehrfach - Toast UI baut damit Druckseiten.
    Ein blosses replace() landet dort also mitten im JavaScript und
    zerschiesst die Testkopie. Deshalb wird der Dokumenttext ueber
    Kommentare und script-/style-Bloecke hinweg gescannt und nur Tags
    ausserhalb deren Inhalt verwendet.

    Liefert (ende_von_head, ende_vom_body_tag, beginn_vom_/body).
    """
    roh = False
    kommentar = False
    head = body_tag_ende = body = None
    for m in _SCAN.finditer(h):
        t = m.group(0).lower()
        if t.startswith('<!--'):
            kommentar = not kommentar
            continue
        if kommentar:
            continue
        if t.startswith('<script') or t.startswith('<style'):
            roh = True
            continue
        if t.startswith('</script') or t.startswith('</style'):
            roh = False
            continue
        if roh:
            continue
        if t.startswith('</head>'):
            head = m.start()
        elif t.startswith('<body'):
            body_tag_ende = m.end()
            if body is None:
                body = h.rfind('</body>')
    if head is None or body_tag_ende is None or body < 0:
        raise AssertionError('Head-/Body-Grenze in simplewiki.html nicht gefunden')
    return head, body_tag_ende, body


def hauptskripte(h, seed='', pre='', script=''):
    """Seed und Testskripte an die echten Head-/Body-Tags haengen.

    'seed' landet vor </head>, 'pre' direkt hinter <body ...> und
    'script' vor </body>. Die Positionen kommen von hinten nach vorn
    dran, damit die uebrigen gueltig bleiben.

    Wichtig: nicht einfach replace('<body>', ...) - die eingebetteten
    Bibliotheken enthalten die Zeichenkette '<head></head><body>' selbst.
    """
    head_at, body_tag_ende, body_at = _echte_tags(h)
    teile = []
    if script:
        teile.append((body_at, script))
    if seed:
        teile.append((head_at, seed))
    if pre:
        teile.append((body_tag_ende, pre))
    for pos, text in sorted(teile, key=lambda t: -t[0]):
        h = h[:pos] + text + h[pos:]
    return h


def _maskieren(text):
    """'<' als '\\u003c' - sonst koennte ein </script> im Testtext
    die Kopie zerreissen."""
    return json.dumps(text, ensure_ascii=False).replace('<', '\\u003c')


def build(out_name, script, pages, theme='light', lang='de', startpage='1',
          seed=True, daten=None):
    """Testkopie schreiben und ihren Pfad zurueckgeben."""
    global PRE_SCRIPT
    if not os.path.isdir(KOPIEN):
        os.makedirs(KOPIEN)

    with io.open(SRC, encoding='utf-8') as fh:
        h = fh.read()

    seed_block = ''
    if seed:
        seed_block = _SEED_VORHAGE % (_maskieren(json.dumps(pages, ensure_ascii=False)),
                                      theme, lang, startpage)

    # Datenblock setzen: leer oder mit Testdaten. Nicht ueber einen
    # Platzhalter ersetzen - in der Vorlage koennen echte Daten stehen.
    inhalt = json.dumps(daten, ensure_ascii=False).replace('<', '\\u003c') \
        if daten is not None else '{}'
    h = re.sub(r'(<script id="simplewiki-daten"[^>]*>)[\s\S]*?(</script>)',
               lambda m: m.group(1) + inhalt + m.group(2), h, count=1)

    for a, b in EXTRA_REPLACEMENTS:
        h = h.replace(a, b)

    # Testhaken: Editor-Instanz erreichbar machen
    h = h.replace("                        usageStatistics: false\n                    });",
                  "                        usageStatistics: false\n                    });\n"
                  "                    window.__ed = this.mdEditor;   /* Testhaken */")

    # Einfuegungen an den echten Tags
    h = hauptskripte(h, seed=seed_block, pre=PRE_SCRIPT, script=script)

    pfad = os.path.join(KOPIEN, out_name)
    with io.open(pfad, 'w', encoding='utf-8') as fh:
        fh.write(h)
    return pfad