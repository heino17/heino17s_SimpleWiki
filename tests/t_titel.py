"""Der eigene Wiki-Name oben im Kopf.

Unter file:// ist der Name anklickbar: er wird zum Eingabefeld, Enter
uebernimmt, Escape verwirft, Wegklicken uebernimmt ebenfalls. Der Name
gehoert zur Datei, nicht zu den Seiten - er steht deshalb als meta im
Kopf (simplewiki-title) und nicht im Datenblock. Beim Sichern wird er
mitgeschrieben, beim Oeffnen wieder gelesen.

Die vier Teile:

  1. Bearbeiten: klicken, tippen, Enter; Escape; leer heisst fester
     Name. Und der Export backt den Namen, die leere Vorlage nicht.
  2. Der Browserspeicher bringt den Namen mit.
  3. Eine geoeffnete Datei bringt ihren Namen mit (der Weg
     Sichern -> Oeffnen).
  4. Im Serverbetrieb ist der Name kein Gegenstand dieser Oberflaeche
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


def vorab(docid, titel):
    """Den Browserspeicher fuellen: Entwurf mit Kennung und Name."""
    return ("<script>try{"
            "localStorage.setItem('simplewiki_pages', %s);"
            "localStorage.setItem('simplewiki_startpage','a');"
            "localStorage.setItem('simplewiki_doc_id','%s');"
            "localStorage.setItem('simplewiki_titel',%s);"
            "localStorage.setItem('simplewiki_theme','light');"
            "localStorage.setItem('simplewiki_lang','de');"
            "localStorage.setItem('simplewiki_refs','0');"
            "}catch(e){}</script>"
            % (json.dumps(json.dumps(SEITEN)), docid, json.dumps(titel)))


KOMMUN = r"""
      function q(s) { return document.querySelector(s); }
      function h1() { var h = q('.kopf-titel h1'); return h ? h.textContent.replace('📚', '').trim() : '-'; }
      function feld() { return q('.kopf-titel-feld'); }
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
        ok(h1().indexOf('SimpleWiki') >= 0, 'ohne eigenen Namen der feste: ' + h1());
        ok((' ' + q('.kopf-titel h1').className + ' ').indexOf(' kopf-titel-editierbar ') >= 0,
           'der Name ist anklickbar');
        ok(!feld(), 'kein Eingabefeld, solange niemand klickt');

        q('.kopf-titel h1').click();
        tick(function () {
          ok(!!feld(), 'nach dem Klick ist es ein Eingabefeld');
          ok(feld().value === 'SimpleWiki', 'es steht der bisherige Name darin: ' + (feld() ? feld().value : '-'));

          feld().value = 'Meine erste Wiki';
          feld().dispatchEvent(new Event('input', { bubbles: true }));
          feld().dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
          tick(function () {
            ok(!feld(), 'Enter schliesst das Feld');
            ok(h1().indexOf('Meine erste Wiki') >= 0, 'der neue Name steht im Kopf: ' + h1());
            ok(localStorage.getItem('simplewiki_titel') === 'Meine erste Wiki', 'der Name steht im Browserspeicher');
            ok(document.title === 'Meine erste Wiki', 'auch der Fenstertitel: ' + document.title);
            ok(!!q('.datei-warn-punkt'), 'die Warnung sagt: die Datei kennt den Namen noch nicht');

            var doc = new DOMParser().parseFromString(v.bauExport(), 'text/html');
            var meta = doc.querySelector('meta[name="simplewiki-title"]');
            ok(meta && meta.getAttribute('content') === 'Meine erste Wiki',
               'der Export traegt den Namen im Kopf: ' + (meta ? meta.getAttribute('content') : '-'));

            var leer = new DOMParser().parseFromString(v.bauExport(v.bauDaten(), 'leer', ''), 'text/html');
            var mleer = leer.querySelector('meta[name="simplewiki-title"]');
            ok(mleer && mleer.getAttribute('content') === '', 'die leere Vorlage erbt den Namen nicht');

            q('.kopf-titel h1').click();
            tick(function () {
              var f2 = feld();
              f2.value = 'Wegwerfen';
              f2.dispatchEvent(new Event('input', { bubbles: true }));
              f2.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
              tick(function () {
                ok(h1().indexOf('Meine erste Wiki') >= 0, 'Escape verwirft: ' + h1());
                ok(localStorage.getItem('simplewiki_titel') === 'Meine erste Wiki', 'der Speicher bleibt');

                q('.kopf-titel h1').click();
                tick(function () {
                  var f3 = feld();
                  f3.value = '';
                  f3.dispatchEvent(new Event('input', { bubbles: true }));
                  f3.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
                  tick(function () {
                    ok(h1().indexOf('SimpleWiki') >= 0, 'leer heisst: der feste Name: ' + h1());
                    ok(localStorage.getItem('simplewiki_titel') === '', 'der Speicher ist leer');
""" + ende() + r"""
                  });
                });
              });
            });
          });
        });
"""

# 2. Der Browserspeicher bringt den Namen mit.
speicher = r"""
        ok(h1() === 'Aus dem Speicher', 'der Name kommt aus dem Browserspeicher: ' + h1());
        ok(document.title === 'Aus dem Speicher', 'auch der Fenstertitel: ' + document.title);
""" + ende()

# 3. Eine geoeffnete Datei bringt Namen und Untertitel mit.
datei = r"""
        ok(h1() === 'Datei-Wiki', 'der Name kommt aus der Datei: ' + h1());
        ok(localStorage.getItem('simplewiki_titel') === 'Datei-Wiki', 'die Datei setzt den Speicher');
        var u = q('.kopf-untertitel');
        ok(u && u.textContent.trim() === 'Klein und fein',
           'der Untertitel kommt aus der Datei: ' + (u ? u.textContent.trim() : '-'));
        var exp = new DOMParser().parseFromString(window.__vm.bauExport(), 'text/html');
        var em = exp.querySelector('meta[name="simplewiki-subtitle"]');
        ok(em && em.getAttribute('content') === 'Klein und fein',
           'der Export traegt den Untertitel: ' + (em ? em.getAttribute('content') : '-'));
        var leer = new DOMParser().parseFromString(
            window.__vm.bauExport(window.__vm.bauDaten(), 'leer', '', ''), 'text/html');
        var lm = leer.querySelector('meta[name="simplewiki-subtitle"]');
        ok(lm && lm.getAttribute('content') === '', 'die leere Vorlage erbt den Untertitel nicht');
""" + ende()

NAMEN = ['_titel_bearbeiten.html', '_titel_speicher.html', '_titel_datei.html']

mkcopy.EXTRA_REPLACEMENTS = []
mkcopy.PRE_SCRIPT = vorab('titel-test', '')
build(NAMEN[0], teil('Bearbeiten unter file://', bearbeiten), [], seed=False, daten=None)

mkcopy.EXTRA_REPLACEMENTS = []
mkcopy.PRE_SCRIPT = vorab('titel-speicher', 'Aus dem Speicher')
build(NAMEN[1], teil('Der Browserspeicher bringt den Namen mit', speicher), [], seed=False, daten=None)

mkcopy.EXTRA_REPLACEMENTS = [
    ('<meta name="simplewiki-title" content="">',
     '<meta name="simplewiki-title" content="Datei-Wiki">'),
    ('<meta name="simplewiki-subtitle" content="">',
     '<meta name="simplewiki-subtitle" content="Klein und fein">'),
]
mkcopy.PRE_SCRIPT = ''
build(NAMEN[2], teil('Eine geoeffnete Datei bringt ihren Namen mit', datei), [], seed=False, daten=DATEN)

mkcopy.EXTRA_REPLACEMENTS = []
mkcopy.PRE_SCRIPT = ''

PROFIL = ziel('_profil_titel')
shutil.rmtree(PROFIL, ignore_errors=True)


def lauef(name, budget=120000):
    text = bericht(dumpdom(name, budget=budget, zusatz=['--user-data-dir=' + PROFIL]))
    print('%-24s %s' % (name, text.split('\n')[-1] if text else 'KEIN REPORT'))
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
