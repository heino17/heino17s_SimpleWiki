"""Der eigene Wiki-Untertitel unter dem Namen.

Unter file:// ist der Untertitel genauso anklickbar wie der Name: er
wird zum Eingabefeld, Enter uebernimmt, Escape verwirft, Wegklicken
uebernimmt ebenfalls. Leer heisst: keine Zeile - dann steht an ihrer
Stelle ein Platzhalter, damit der Untertitel ueberhaupt erst entstehen
kann. Er gehoert zur Datei, nicht zu den Seiten - er steht deshalb als
meta im Kopf (simplewiki-subtitle) und nicht im Datenblock. Beim
Sichern wird er mitgeschrieben, beim Oeffnen wieder gelesen.

Die drei Teile:

  1. Bearbeiten: klicken, tippen, Enter; Escape; leer heisst: der
     Platzhalter. Und der Export backt den Untertitel, die leere
     Vorlage nicht.
  2. Der Browserspeicher bringt den Untertitel mit.
  3. Eine geoeffnete Datei bringt ihren Untertitel mit.

Im Serverbetrieb ist der Untertitel kein Gegenstand dieser Oberflaeche
(das prueft t_mwsmode.py).
"""

import sys, os, shutil, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mkcopy
from mkcopy import build
from _hilfe import dumpdom, bericht, ziel, zahlen

ISO = '2026-01-01T00:00:00.000Z'
SEITEN = [{
    'id': 'a', 'title': 'Erste',
    'content': '# Erste\n\nEin Text.',
    'links': [], 'tags': [], 'created': ISO, 'updated': ISO,
}]
DATEN = {
    'version': 1, 'startseite': 'a', 'sprache': 'de', 'thema': 'light',
    'palette': 'pergament', 'seiten': SEITEN,
}


def vorab(docid, untertitel):
    """Den Browserspeicher fuellen: Entwurf mit Kennung und Untertitel."""
    return ("<script>try{"
            "localStorage.setItem('simplewiki_pages', %s);"
            "localStorage.setItem('simplewiki_startpage','a');"
            "localStorage.setItem('simplewiki_doc_id','%s');"
            "localStorage.setItem('simplewiki_untertitel',%s);"
            "localStorage.setItem('simplewiki_theme','light');"
            "localStorage.setItem('simplewiki_lang','de');"
            "localStorage.setItem('simplewiki_refs','0');"
            "}catch(e){}</script>"
            % (json.dumps(json.dumps(SEITEN)), docid, json.dumps(untertitel)))


KOMMUN = r"""
      function q(s) { return document.querySelector(s); }
      function zeile() { return q('.kopf-untertitel'); }
      function feld() { return q('.kopf-untertitel-feld'); }
      function text() { var p = zeile(); return p ? p.textContent.trim() : '-'; }
      function klasse(name) {
        var p = zeile();
        return p && (' ' + p.className + ' ').indexOf(' ' + name + ' ') >= 0;
      }
      function tippe(wert) {
        var f = feld();
        f.value = wert;
        f.dispatchEvent(new Event('input', { bubbles: true }));
        return f;
      }
      function taste(k) {
        feld().dispatchEvent(new KeyboardEvent('keydown', { key: k, bubbles: true }));
      }
"""


def teil(text, block):
    return (r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function tick(fn) { setTimeout(fn, 200); }
""" + KOMMUN + r"""
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      setTimeout(function () {
        log.push('--- """ + text + r"""');
""" + block + r"""
      }, 2500);
    })();
    </script>
""")


def ende():
    return (r"""
        log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN'
                                : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        document.getElementById('report').textContent = log.join('\n');
""")


# 1. Bearbeiten unter file://.
bearbeiten = r"""
        var v = window.__vm;
        ok(!!v, 'die App ist da');
        ok(!!zeile(), 'die Zeile unter dem Namen ist da');
        ok(klasse('kopf-untertitel-editierbar'), 'der Untertitel ist anklickbar');
        ok(klasse('kopf-untertitel-leer'), 'ohne Untertitel ist die Zeile als leere markiert');
        ok(text() === 'Untertitel hinzufügen',
           'ohne Untertitel steht der Platzhalter: ' + text());
        ok(!feld(), 'kein Eingabefeld, solange niemand klickt');

        zeile().click();
        tick(function () {
          ok(!!feld(), 'nach dem Klick ist es ein Eingabefeld');
          ok(feld().value === '', 'es steht leer darin: ' + (feld() ? feld().value : '-'));

          tippe('Mein Untertitel');
          taste('Enter');
          tick(function () {
            ok(!feld(), 'Enter schliesst das Feld');
            ok(text() === 'Mein Untertitel', 'der neue Untertitel steht in der Zeile: ' + text());
            ok(!klasse('kopf-untertitel-leer'), 'die Zeile ist nicht mehr leer');
            ok(localStorage.getItem('simplewiki_untertitel') === 'Mein Untertitel',
               'der Untertitel steht im Browserspeicher');
            ok(!!q('.datei-warn-punkt'),
               'die Warnung sagt: die Datei kennt den Untertitel noch nicht');

            var doc = new DOMParser().parseFromString(v.bauExport(), 'text/html');
            var meta = doc.querySelector('meta[name="simplewiki-subtitle"]');
            ok(meta && meta.getAttribute('content') === 'Mein Untertitel',
               'der Export traegt den Untertitel im Kopf: ' + (meta ? meta.getAttribute('content') : '-'));

            var leer = new DOMParser().parseFromString(
                v.bauExport(v.bauDaten(), 'leer', '', ''), 'text/html');
            var mleer = leer.querySelector('meta[name="simplewiki-subtitle"]');
            ok(mleer && mleer.getAttribute('content') === '',
               'die leere Vorlage erbt den Untertitel nicht');

            zeile().click();
            tick(function () {
              tippe('Wegwerfen');
              taste('Escape');
              tick(function () {
                ok(text() === 'Mein Untertitel', 'Escape verwirft: ' + text());
                ok(localStorage.getItem('simplewiki_untertitel') === 'Mein Untertitel',
                   'der Speicher bleibt');

                zeile().click();
                tick(function () {
                  tippe('');
                  taste('Enter');
                  tick(function () {
                    ok(text() === 'Untertitel hinzufügen',
                       'leer heisst: keine Zeile, sondern der Platzhalter: ' + text());
                    ok(localStorage.getItem('simplewiki_untertitel') === '',
                       'der Speicher ist leer');
""" + ende() + r"""
                  });
                });
              });
            });
          });
        });
"""

# 2. Der Browserspeicher bringt den Untertitel mit.
speicher = r"""
        ok(text() === 'Aus dem Speicher',
           'der Untertitel kommt aus dem Browserspeicher: ' + text());
        var exp = new DOMParser().parseFromString(window.__vm.bauExport(), 'text/html');
        var em = exp.querySelector('meta[name="simplewiki-subtitle"]');
        ok(em && em.getAttribute('content') === 'Aus dem Speicher',
           'der Export traegt ihn mit: ' + (em ? em.getAttribute('content') : '-'));
""" + ende()

# 3. Eine geoeffnete Datei bringt ihren Untertitel mit.
datei = r"""
        ok(text() === 'Klein und fein', 'der Untertitel kommt aus der Datei: ' + text());
        ok(localStorage.getItem('simplewiki_untertitel') === 'Klein und fein',
           'die Datei setzt den Speicher');
        var exp = new DOMParser().parseFromString(window.__vm.bauExport(), 'text/html');
        var em = exp.querySelector('meta[name="simplewiki-subtitle"]');
        ok(em && em.getAttribute('content') === 'Klein und fein',
           'der Export traegt den Untertitel: ' + (em ? em.getAttribute('content') : '-'));

        zeile().click();
        tick(function () {
          tippe('Groesser und feiner');
          taste('Enter');
          tick(function () {
            ok(text() === 'Groesser und feiner',
               'der neue Untertitel steht in der Zeile: ' + text());
            ok(localStorage.getItem('simplewiki_untertitel') === 'Groesser und feiner',
               'der Untertitel steht im Browserspeicher');
            var neu = new DOMParser().parseFromString(window.__vm.bauExport(), 'text/html');
            var nm = neu.querySelector('meta[name="simplewiki-subtitle"]');
            ok(nm && nm.getAttribute('content') === 'Groesser und feiner',
               'der Export traegt den neuen Untertitel: ' + (nm ? nm.getAttribute('content') : '-'));
""" + ende() + r"""
          });
        });
"""

NAMEN = ['_untertitel_bearbeiten.html', '_untertitel_speicher.html',
         '_untertitel_datei.html']

mkcopy.EXTRA_REPLACEMENTS = []
mkcopy.PRE_SCRIPT = vorab('untertitel-test', '')
build(NAMEN[0], teil('Bearbeiten unter file://', bearbeiten), [], seed=False, daten=None)

mkcopy.EXTRA_REPLACEMENTS = []
mkcopy.PRE_SCRIPT = vorab('untertitel-speicher', 'Aus dem Speicher')
build(NAMEN[1], teil('Der Browserspeicher bringt den Untertitel mit', speicher),
      [], seed=False, daten=None)

mkcopy.EXTRA_REPLACEMENTS = [
    ('<meta name="simplewiki-subtitle" content="">',
     '<meta name="simplewiki-subtitle" content="Klein und fein">'),
]
mkcopy.PRE_SCRIPT = ''
build(NAMEN[2], teil('Eine geoeffnete Datei bringt ihren Untertitel mit', datei),
      [], seed=False, daten=DATEN)

mkcopy.EXTRA_REPLACEMENTS = []
mkcopy.PRE_SCRIPT = ''

PROFIL = ziel('_profil_untertitel')
shutil.rmtree(PROFIL, ignore_errors=True)


def lauef(name, budget=120000):
    text = bericht(dumpdom(name, budget=budget, zusatz=['--user-data-dir=' + PROFIL]))
    print('%-26s %s' % (name, text.split('\n')[-1] if text else 'KEIN REPORT'))
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
