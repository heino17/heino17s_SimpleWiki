"""Welche Datei ist offen, und was ist neuer?

Unter file:// traegt jede gesicherte Datei zwei Angaben im Kopf:
die Kennung des Dokuments (simplewiki-doc-id) und den Zeitpunkt der
Sicherung (simplewiki-exported). Zusammen mit dem Zeitpunkt des
Entwurfs im Browserspeicher (simplewiki_draft_time) entscheiden sie
ohne Nachfrage, wer gilt.

Die vier Faelle:

  1. Die Datei ist neuer als der Entwurf  -> die Datei gewinnt, keine
     Warnung. Der Fall "in Firefox gesichert, in Chrome geoeffnet".
  2. Die Datei ist aelter als der Entwurf   -> der Entwurf bleibt, und
     die Warnung sagt: diese Datei kennt den Stand noch nicht.
  3. Gleichstand -> die Datei gewinnt (sie ist zum Weitergeben da).
  4. Eine leere Datei mit frischer Kennung zeigt nicht den Entwurf
     einer anderen Datei - genau der Fehler, der die Leute zwang, den
     Browserspeicher zu leeren.
"""

import sys, os, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mkcopy
from mkcopy import build
from _hilfe import dumpdom, bericht, ziel, zahlen

ALT_ISO = '2026-01-01T00:00:00.000Z'
NEU_ISO = '2027-01-01T00:00:00.000Z'
ALT_MS = '1767225600000'    # 2026-01-01
NEU_MS = '1798761600000'    # 2027-01-01

DATEI_SEITEN = [{
    'id': 'd1', 'title': 'Aus der Datei',
    'content': '# Aus der Datei\n\nDer Inhalt der Datei.',
    'links': [], 'tags': [], 'created': ALT_ISO, 'updated': ALT_ISO,
}]
DATEN = {
    'version': 1, 'startseite': 'd1', 'sprache': 'de', 'thema': 'light',
    'palette': 'pergament', 'seiten': DATEI_SEITEN,
}
ENTWURF = [{
    'id': 'e1', 'title': 'Entwurf',
    'content': '# Entwurf\n\nNur im Browser.',
    'links': [], 'tags': [], 'created': ALT_ISO, 'updated': ALT_ISO,
}]

PROFIL = ziel('_profil_dokument')


def metas(docid, iso):
    """Die beiden Kopfangaben der Datei fuellen (sonst leer)."""
    return [
        ('<meta name="simplewiki-doc-id" content="">',
         '<meta name="simplewiki-doc-id" content="%s">' % docid),
        ('<meta name="simplewiki-exported" content="">',
         '<meta name="simplewiki-exported" content="%s">' % iso),
    ]


def vorab(docid, draft_ms, seiten):
    """Den Browserspeicher fuellen: Entwurf mit Kennung und Zeitpunkt."""
    import json
    return ("<script>try{"
            "localStorage.setItem('simplewiki_pages', %s);"
            "localStorage.setItem('simplewiki_startpage','%s');"
            "localStorage.setItem('simplewiki_doc_id','%s');"
            "localStorage.setItem('simplewiki_draft_time','%s');"
            "localStorage.setItem('simplewiki_theme','light');"
            "localStorage.setItem('simplewiki_lang','de');"
            "localStorage.setItem('simplewiki_refs','0');"
            "}catch(e){}</script>"
            % (json.dumps(json.dumps(seiten)), seiten[0]['id'], docid, draft_ms))


KOMMUN = r"""
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function titel() { return all('.toc-menu .toc-item-title').map(function (t) { return t.textContent.trim(); }); }
      function titel1() { var t = q('.content-title'); return t ? t.textContent.trim() : '-'; }
      function inhalt() { var p = q('.preview'); return p ? p.textContent : ''; }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
"""


def teil(text, block):
    return (r"""
    <script>
    (function () {
      var log = [], fails = 0;
""" + KOMMUN + r"""
      setTimeout(function () {
        log.push('--- """ + text + r"""');
""" + block + r"""
        log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN'
                                : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }, 2500);
    })();
    </script>
""")


# 1. Datei neuer als der Entwurf: die Datei gewinnt, keine Warnung.
neuer_block = r"""
        ok(titel1() === 'Aus der Datei', 'Startseite aus der neueren Datei: ' + titel1());
        ok(titel().join('|') === 'Aus der Datei', 'nur die Seite der Datei: ' + titel().join('|'));
        ok(inhalt().indexOf('Der Inhalt der Datei') >= 0, 'Inhalt der Datei ist da');
        ok(inhalt().indexOf('Nur im Browser') < 0, 'der Entwurf ist verdrangt');
        ok(!q('.datei-warn-punkt'), 'keine Warnung - die Datei ist der Stand');
        ok(localStorage.getItem('simplewiki_doc_id') === 'gleich', 'Kennung der Datei gilt weiter');
        var ps = JSON.parse(localStorage.getItem('simplewiki_pages'));
        ok(ps.length === 1 && ps[0].title === 'Aus der Datei', 'Browserspeicher traegt die Datei');
"""

# 2. Datei aelter als der Entwurf: der Entwurf bleibt, die Warnung steht.
alter_block = r"""
        ok(titel1() === 'Entwurf', 'der Entwurf bleibt: ' + titel1());
        ok(titel().join('|') === 'Entwurf', 'nur der Entwurf: ' + titel().join('|'));
        ok(inhalt().indexOf('Nur im Browser') >= 0, 'Inhalt des Entwurfs steht');
        ok(inhalt().indexOf('Der Inhalt der Datei') < 0, 'die aeltere Datei draengt sich nicht auf');
        ok(!!q('.datei-warn-punkt'), 'die Warnung sagt: diese Datei kennt den Stand noch nicht');
"""

# 3. Gleichstand: die Datei gewinnt.
gleich_block = r"""
        ok(titel1() === 'Aus der Datei', 'Gleichstand, die Datei gewinnt: ' + titel1());
        ok(inhalt().indexOf('Nur im Browser') < 0, 'der gleichalte Entwurf weicht der Datei');
        ok(!q('.datei-warn-punkt'), 'kein Grund zur Warnung');
"""

# 4. Leere Datei mit frischer Kennung: kein fremder Entwurf.
leer_block = r"""
        ok(titel1().indexOf('Willkommen') >= 0 || titel1() === '', 'leere Datei: ' + titel1());
        ok(inhalt().indexOf('Nur im Browser') < 0 && inhalt().indexOf('Entwurf') < 0,
           'der fremde Entwurf taucht nicht auf');
        ok(!q('.datei-warn-punkt'), 'kein Grund zur Warnung');
        ok(localStorage.getItem('simplewiki_doc_id') === 'leer-frisch', 'frische Kennung gilt');
"""

NAMEN = ['_dok_neu.html', '_dok_alt.html', '_dok_gleich.html', '_dok_leer.html']

mkcopy.EXTRA_REPLACEMENTS = metas('gleich', NEU_ISO)
mkcopy.PRE_SCRIPT = vorab('gleich', ALT_MS, ENTWURF)
build(NAMEN[0], teil('Neue Datei gegen alten Entwurf', neuer_block), [], seed=False, daten=DATEN)

mkcopy.EXTRA_REPLACEMENTS = metas('gleich', ALT_ISO)
mkcopy.PRE_SCRIPT = vorab('gleich', NEU_MS, ENTWURF)
build(NAMEN[1], teil('Alte Datei gegen neuen Entwurf', alter_block), [], seed=False, daten=DATEN)

mkcopy.EXTRA_REPLACEMENTS = metas('gleich', ALT_ISO)
mkcopy.PRE_SCRIPT = vorab('gleich', ALT_MS, ENTWURF)
build(NAMEN[2], teil('Gleichstand', gleich_block), [], seed=False, daten=DATEN)

mkcopy.EXTRA_REPLACEMENTS = metas('leer-frisch', NEU_ISO)
mkcopy.PRE_SCRIPT = vorab('andere', NEU_MS, ENTWURF)
build(NAMEN[3], teil('Leere Datei, fremder Entwurf', leer_block), [], seed=False, daten=None)

mkcopy.EXTRA_REPLACEMENTS = []
mkcopy.PRE_SCRIPT = ''

shutil.rmtree(PROFIL, ignore_errors=True)


def lauef(name, budget=120000):
    text = bericht(dumpdom(name, budget=budget, zusatz=['--user-data-dir=' + PROFIL]))
    print('%-16s %s' % (name, text.split('\n')[-1] if text else 'KEIN REPORT'))
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
