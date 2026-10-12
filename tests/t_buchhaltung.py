"""Die Buchhaltung pruefen, ohne Browser und ohne letzten Suite-Lauf.

`tests/buchhaltung.py` schreibt die wiederkehrenden Zahlen an ihre
Stellen. Dieses Testfile liest dieselben Quellen und stellt fest, ob
das Geschriebene noch stimmt. Es braucht keinen Browser und keinen
Bericht: nur die vier Dateien und die Liste in `alle.py`.

Was nicht geprueft wird: die Pruefungszahl selbst. Sie kommt aus dem
letzten Suite-Lauf und ist erst nach dem Lauf bekannt - ein Test, der
sie fordert, wuerde bei jeder neuen Pruefung scheitern, bevor die
Buchhaltung nachgezogen ist. Geprueft wird die Uebereinstimmung der
Stellen untereinander und mit simplewiki.html.
"""

import importlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

buchhaltung = importlib.import_module('buchhaltung')
alle = importlib.import_module('alle')

bestanden = 0
fehler = 0


def pruefe(bedingung, text):
    global bestanden, fehler
    if bedingung:
        bestanden += 1
    else:
        fehler += 1
    print(('    OK   ' if bedingung else '    FAIL ') + text)


def meta(text):
    m = buchhaltung.META.search(text)
    return m.group(2) if m else None


html = buchhaltung.lies(buchhaltung.HTML)
chronik = buchhaltung.lies(buchhaltung.CHRONIK)
readme = buchhaltung.lies(buchhaltung.README)
agents = buchhaltung.lies(buchhaltung.AGENTS)

s = buchhaltung.struktur(html)
version = buchhaltung.fassung(chronik)
anzahl = len(alle.REIHENFOLGE)

# ---- Der Aufbau in der README -----------------------------------
spannen = buchhaltung.readme_spannen(readme)
pruefe(spannen == s['spannen'],
       'Strukturtafel der README stimmt mit simplewiki.html: %s' % (spannen,))
pruefe(('`simplewiki.html` ist %d Zeilen lang' % s['gesamt']) in readme,
       'README nennt die Laenge: %d Zeilen' % s['gesamt'])

# ---- Die Fassung aus dem CHANGELOG steht an allen drei Stellen ---
pruefe(version is not None, 'oberste Fassung im CHANGELOG: %s' % version)
pruefe(meta(html) == version, 'simplewiki.html nennt die Fassung: %s' % meta(html))
pruefe(meta(readme) == version, 'README-Beispiel nennt die Fassung: %s' % meta(readme))
pruefe(meta(chronik) == version, 'CHANGELOG-Kopf nennt die Fassung: %s' % meta(chronik))

# ---- Die Zahl der Testdateien ------------------------------------
readme_zahlen = buchhaltung.README_ZAHLEN.search(readme)
agents_stand = buchhaltung.AGENTS_STAND.search(agents)
pruefe(bool(readme_zahlen) and readme_zahlen.group(1) == str(anzahl),
       'README nennt %d Testdateien' % anzahl)
pruefe(bool(agents_stand) and agents_stand.group(1) == str(anzahl),
       'AGENTS nennt %d Testdateien' % anzahl)

# ---- Die Pruefungszahl ist wenigstens in sich stimmig ------------
gleich = bool(readme_zahlen) and bool(agents_stand) \
    and readme_zahlen.group(2) == agents_stand.group(2)
pruefe(gleich, 'Pruefungszahl in README und AGENTS gleich: %s'
       % (readme_zahlen.group(2) if readme_zahlen else '?'))

kopf = buchhaltung.UEBERSCHRIFT.search(chronik)
zahl_kopf = kopf and re.search(r'(\d+)\s+Prüfungen\s*$', kopf.group(1))
if zahl_kopf and readme_zahlen:
    pruefe(zahl_kopf.group(1) == readme_zahlen.group(2),
           'oberste CHANGELOG-Ueberschrift zaehlt %s' % zahl_kopf.group(1))
else:
    print('    (Notiz) oberste CHANGELOG-Ueberschrift traegt noch keine Zahl')

print('')
print('GESAMT: %d bestanden, %d fehlgeschlagen' % (bestanden, fehler))
raise SystemExit(1 if fehler else 0)
