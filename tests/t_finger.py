import sys, os, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mkcopy
from mkcopy import build
from _hilfe import dumpdom, bericht, ziel, zahlen

# ------------------------------------------------------------------ Inhalt
# Zwei verschiedene Wiki-Dateien, deren Datenbloecke als Stapel im Browser
# landen. Der Fingerabdruck aus dem Datenblock entscheidet, welche von
# beiden beim naechsten Oeffnen gilt - ohne dass der Browserspeicher
# geleert werden muss (t_export legt den Stand schon fest, die Suche ist
# die Frage "andere Datei?". Die Suite prueft dieselbe Datei nur einmal;
# hier wird die Datei dasselbe zweimal geoeffnet, und danach eine andere.)
DATEN_A = {
    'version': 1,
    'startseite': 'a1',
    'sprache': 'de', 'thema': 'light', 'palette': 'pergament',
    'seiten': [{
        'id': 'a1', 'title': 'Eins',
        'content': '# Eins\n\nInhalt der Datei A.',
        'links': [], 'tags': [],
        'created': '2026-10-01T10:00:00.000Z', 'updated': '2026-10-01T10:00:00.000Z'
    }],
}
DATEN_B = {
    'version': 1,
    'startseite': 'b1',
    'sprache': 'de', 'thema': 'light', 'palette': 'pergament',
    'seiten': [
        {'id': 'b1', 'title': 'Alpha',
         'content': '# Alpha\n\nInhalt der Datei B, Seite 1.',
         'links': [], 'tags': [], 'created': '2026-10-02T10:00:00.000Z',
         'updated': '2026-10-02T10:00:00.000Z'},
        {'id': 'b2', 'title': 'Beta',
         'content': '# Beta\n\nInhalt der Datei B, Seite 2.',
         'links': [], 'tags': [], 'created': '2026-10-02T10:00:01.000Z',
         'updated': '2026-10-02T10:00:01.000Z'},
    ],
}

# Profil, in dem die drei Lauefe denselben Browserspeicher teilen - beim
# Oeffnen einer lokalen Datei sind sonst alle file://-Wikis derselben
# Herkunft, und genau das ist hier das Thema.
PROFIL = ziel('_profil_finger')

KOMMUN = r"""
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function btn(re) { return all('.footer .btn').filter(function (b) { return re.test(b.textContent); })[0]; }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      function titel() { return all('.toc-menu .toc-item-title').map(function (t) { return t.textContent.trim(); }); }
"""

# ---------------------------------------------------------------- Teil 1
# Datei A zum ersten Mal: nichts im Browser, der Datenblock gewinnt.
teil1 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + KOMMUN + r"""
      setTimeout(function () {
        log.push('--- Lauef 1: Datei A zum ersten Mal');
        ok(q('.content-title') && q('.content-title').textContent.trim() === 'Eins',
           'Startseite aus dem Datenblock: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
        ok(titel().join('|') === 'Eins', 'eine Seite: ' + titel().join('|'));
        var ps = JSON.parse(localStorage.getItem('simplewiki_pages'));
        ok(ps.length === 1 && ps[0].title === 'Eins', 'Seite im Browserspeicher');
        ok(/^f\d+-[0-9a-z]+$/.test(localStorage.getItem('simplewiki_digest') || ''),
           'Fingerabdruck steht jetzt: ' + localStorage.getItem('simplewiki_digest'));

        log.push('--- Lauef 1: eine Aenderung im Browser');
        ps[0].content = '# Eins\n\nGeaendert im Browser.';
        localStorage.setItem('simplewiki_pages', JSON.stringify(ps));
        setTimeout(function () {
          var gea = JSON.parse(localStorage.getItem('simplewiki_pages'));
          ok(gea[0].content.indexOf('Geaendert im Browser') >= 0, 'Aenderung liegt im Browserspeicher');
          log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
          out();
        }, 500);
      }, 2500);
    })();
    </script>
"""

# ---------------------------------------------------------------- Teil 2
# Dieselbe Datei A noch einmal: Fingerabdruck gleich, der Browserspeicher
# gewinnt und die Aenderung ueberlebt.
teil2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + KOMMUN + r"""
      setTimeout(function () {
        log.push('--- Lauef 2: dieselbe Datei A noch einmal');
        ok(q('.content-title') && q('.content-title').textContent.trim() === 'Eins',
           'Startseite wieder Eins');
        ok(titel().join('|') === 'Eins', 'eine Seite, keine Verdopplung');
        ok(q('.preview').textContent.indexOf('Geaendert im Browser') >= 0,
           'die Aenderung aus Lauef 1 steht noch: gleiche Datei, gleicher Fingerabdruck');
        var ps = JSON.parse(localStorage.getItem('simplewiki_pages'));
        ok(ps.length === 1 && ps[0].content.indexOf('Geaendert im Browser') >= 0,
           'der Browserspeicher bleibt der Stand der Arbeit');
        log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }, 2500);
    })();
    </script>
"""

# ---------------------------------------------------------------- Teil 3
# Eine andere Datei B: der Fingerabdruck ist anders, die Datei gewinnt -
# das ist der Fall, fuer den es den Fingerabdruck gibt.
teil3 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + KOMMUN + r"""
      setTimeout(function () {
        log.push('--- Lauef 3: eine andere Datei B');
        ok(q('.content-title') && q('.content-title').textContent.trim() === 'Alpha',
           'Startseite aus B: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
        ok(titel().join('|') === 'Alpha|Beta', 'zwei Seiten aus B: ' + titel().join('|'));
        ok(q('.preview').textContent.indexOf('Datei B, Seite 1') >= 0, 'Inhalt von B wirklich da');
        var ps = JSON.parse(localStorage.getItem('simplewiki_pages'));
        ok(ps.length === 2 && ps[0].title === 'Alpha' && ps[1].title === 'Beta',
           'der Browserspeicher traegt B, nichts mehr von A');
        ok(ps[0].content.indexOf('Geaendert im Browser') < 0,
           'der alte Stand von A ist weg - die Datei hat gewonnen');
        log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }, 2500);
    })();
    </script>
"""

# ---------------------------------------------------------------- Teil 4
# Und zurueck zu A: auch die andere Richtung erkennt der Fingerabdruck.
teil4 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + KOMMUN + r"""
      setTimeout(function () {
        log.push('--- Lauef 4: zurueck zur Datei A');
        ok(q('.content-title') && q('.content-title').textContent.trim() === 'Eins',
           'Startseite wieder Eins: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
        ok(titel().join('|') === 'Eins', 'wieder nur Eins');
        ok(q('.preview').textContent.indexOf('Inhalt der Datei A.') >= 0,
           'der Stand von A aus dem Datenblock ist zurueck');
        ok(q('.preview').textContent.indexOf('Geaendert im Browser') < 0,
           'ohne die Aenderung aus Lauef 1 - die Datei war der Stand');
        log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }, 2500);
    })();
    </script>
"""

# Kopien bauen; seed=False, damit der Datenblock der Datei zaehlt und
# nicht ein vorausgefuellter Browserspeicher.
NAMEN = ['_p_a.html', '_p_a_2.html', '_p_b.html', '_p_a_3.html']
build(NAMEN[0], teil1, [], seed=False, daten=DATEN_A)
build(NAMEN[1], teil2, [], seed=False, daten=DATEN_A)
build(NAMEN[2], teil3, [], seed=False, daten=DATEN_B)
build(NAMEN[3], teil4, [], seed=False, daten=DATEN_A)

# Alle vier Laeufe liegen in ein und demselben Profil, damit derselbe
# Browserspeicher steuerbar bleibt. Vor dem ersten Lauf das Profil
# loeschen: ein frueherer Lauf darf hier nicht mitrauschen.
shutil.rmtree(PROFIL, ignore_errors=True)

def lauef(name, budget=120000):
    text = bericht(dumpdom(name, budget=budget, zusatz=['--user-data-dir=' + PROFIL]))
    print('%-14s %s' % (name, text.split('\n')[-1] if text else 'KEIN REPORT'))
    for z in text.split('\n'):
        if z.startswith('FAIL'):
            print('    ' + z)
    return text

fehler = 0
bestanden = 0
for name in NAMEN:
    t = lauef(name)
    o, f = zahlen(t)
    bestanden += o
    fehler += f

shutil.rmtree(PROFIL, ignore_errors=True)

print()
print('GESAMT: %d bestanden, %d fehlgeschlagen' % (bestanden, fehler))
sys.exit(1 if fehler else 0)