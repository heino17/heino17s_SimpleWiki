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

    if PRE_SCRIPT:
        h = h.replace('<body>', '<body>\n' + PRE_SCRIPT, 1)

    # Testhaken: Editor-Instanz erreichbar machen
    h = h.replace("                        usageStatistics: false\n                    });",
                  "                        usageStatistics: false\n                    });\n"
                  "                    window.__ed = this.mdEditor;   /* Testhaken */")

    h = h.replace('</head>', seed_block + '</head>')
    h = h.replace('</body>', script + '</body>')

    pfad = os.path.join(KOPIEN, out_name)
    with io.open(pfad, 'w', encoding='utf-8') as fh:
        fh.write(h)
    return pfad