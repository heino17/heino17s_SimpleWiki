import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mkcopy
import mwsserver
from mwsserver import Wiki, starten, beenden, anfragen, leeren
from _hilfe import dumpdom_url, bericht

# ------------------------------------------------------------------ Inhalt
# So kommt das Wiki beim Server an: title ist die Kennung der Seite,
# caption der Name, dazu Zeitstempel im TiddlyWiki-Format.
def zw(jahr, monat, tag, stunde, minute, sekunde, ms):
    return '%d%02d%02d%02d%02d%02d%03d' % (jahr, monat, tag, stunde, minute, sekunde, ms)

ALPHA = {
    'title': 'a1', 'caption': 'Alpha', 'text': '# Alpha\n\nText mit [[Beta]].',
    'tags': '[[wichtig]] [[test]]', 'created': zw(2026, 2, 3, 10, 0, 0, 0),
    'modified': zw(2026, 2, 3, 11, 30, 45, 678), 'reihenfolge': '0001',
    'thema': 'dark', 'sprache': 'en',
}
BETA = {
    'title': 'b2', 'caption': 'Beta', 'text': '# Beta\n\nNur Inhalt.',
    'tags': '', 'created': zw(2026, 2, 3, 10, 5, 0, 0),
    'modified': zw(2026, 2, 3, 12, 0, 0, 0), 'reihenfolge': '0000',
}
STANDARD = {'title': '$:/DefaultTiddlers', 'text': 'a1'}
NURLEBEN = {'title': '$:/nurlesen', 'text': '1'}

# Was im Browser liegt, bevor die App startet. Der Marker dieses Wikis
# ist leer - die App muss den Browser nehmen und den Server nie fragen.
# _maskieren macht aus dem JSON-Text eine Zeichenkette. Ohne das
# bekaeme localStorage ein Feld und schriebe "[object Object]".
BROWSER_SEITEN = mkcopy._maskieren(json.dumps([{
    'id': 'x1', 'title': 'Aus dem Browser', 'content': '# Aus dem Browser',
    'links': [], 'tags': [], 'created': '2026-03-01T10:00:00.000Z',
    'updated': '2026-03-01T10:00:00.000Z'
}], ensure_ascii=False))
VORAB = ('<script>try{localStorage.setItem("simplewiki_pages",' + BROWSER_SEITEN + ');'
         'localStorage.setItem("simplewiki_startpage","x1");'
         'localStorage.setItem("simplewiki_theme","light");}catch(e){}</' + 'script>')

wikis = {
    'alpha': Wiki('alpha', [BETA, ALPHA, STANDARD], titel='Alpha-Wiki'),
    'nurlesen': Wiki('nurlesen', [ALPHA, BETA, STANDARD, NURLEBEN], nurLesen=True,
                     titel='Fremdes Wiki'),
    'leer': Wiki('leer', []),          # Marker mit Inhalt, aber ohne Seiten
    'ohne': Wiki('ohne', [ALPHA, BETA, STANDARD], marker_leer=True,
                 vorab=VORAB),        # Marker leer: der Browser soll her
}

server, thread, port = starten(wikis)
basis = 'http://127.0.0.1:%d' % port

# ---------------------------------------------------------------- Teil 1
# Laden aus dem Marker: Seiten, Reihenfolge, Startseite, Sprache, Farbe
teil1 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function titel() { return all('.toc-item-title').map(function (t) { return t.textContent.trim(); }); }
      function ende() { log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN')); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        log.push('--- Seiten kommen vom Server');
        ok(titel().join('|') === 'Beta|Alpha', 'Reihenfolge aus reihenfolge: ' + titel().join('|'));
        ok(q('.content-title') && q('.content-title').textContent.trim() === 'Alpha',
           'Startseite aus $:/DefaultTiddlers: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
        ok(q('.preview h1') && q('.preview h1').textContent.trim() === 'Alpha', 'Inhalt der Startseite');
        ok(q('.preview').textContent.indexOf('Nur Inhalt') < 0, 'nur die Startseite ist offen');

        log.push('--- Inhalt genaue');
        ok(q('.preview').innerHTML.indexOf('data-wiki-link="Beta"') > 0,
           'Verweis auf Beta wird klickbar gemacht');

        log.push('--- Sprache und Farbe von den Feldern der Startseite');
        ok(document.body.className.indexOf('dark') >= 0, 'dunkel uebernommen');
        ok(q('.settings-toggle').getAttribute('title') === 'Settings',
           'englisch uebernommen: ' + q('.settings-toggle').getAttribute('title'));

        log.push('--- Kein localStorage im Serverbetrieb');
        ok(localStorage.getItem('simplewiki_pages') === null, 'keine Seiten im Browser');

        log.push('--- Schlagworte und Zeitstempel in der App');
        /* Die App zeigt Schlagworte nicht an. Der JSON-Export sagt, was
           wirklich in ihr steht - und geht dabei durch denselben Weg
           wie das Lesen aus den Tiddlern. */
        window.__blob = null;
        var echtesErzeugen = URL.createObjectURL;
        URL.createObjectURL = function (b) { window.__blob = b; return echtesErzeugen.call(URL, b); };
        HTMLAnchorElement.prototype.click = function () {};
        q('.settings-toggle').click();
        setTimeout(function () {
          all('.settings-btn').filter(function (b) { return /JSON/.test(b.textContent); })[0].click();
          setTimeout(function () {
            ok(!!window.__blob, 'JSON erzeugt');
            if (!window.__blob) { ende(); return; }
            window.__blob.text().then(function (text) {
              var d = JSON.parse(text);
              var alpha = d.seiten.filter(function (x) { return x.title === 'Alpha'; })[0] || {};
              ok(JSON.stringify(alpha.tags) === '["wichtig","test"]',
                 'Schlagworte aus [[..]] gelesen: ' + JSON.stringify(alpha.tags));
              ok(alpha.created === '2026-02-03T10:00:00.000Z',
                 'created aus 20260203100000000: ' + alpha.created);
              ok(alpha.updated === '2026-02-03T11:30:45.678Z',
                 'updated aus 20260203113045678: ' + alpha.updated);
              ok(alpha.id === 'a1', 'id ist die Tiddler-Kennung: ' + alpha.id);
              ende();
            });
          }, 700);
        }, 700);
      }, 2500);
    })();
    </script>
"""

# ---------------------------------------------------------------- Teil 2
# Schreiben: Seite aendern, anlegen, loeschen, Startseite und Farbe
teil2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function titel() { return all('.toc-item-title').map(function (t) { return t.textContent.trim(); }); }
      function knopf(re) { return all('.footer .btn').filter(function (b) { return re.test(b.textContent); })[0]; }
      function ende() { log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN')); out(); }
      /* 'new-page-btn' traegt im Kopf den Fluss-Knopf und im Verzeichnis
         die neue Seite. Nach dem Text suchen, nicht nach der Klasse. */
      function neuKnopf() { return all('.new-page-btn').filter(function (b) { return /Neue Seite|New Page/.test(b.textContent); })[0]; }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        log.push('--- Seite umbenennen und Inhalt aendern');
        knopf(/Bearbeiten|Edit/).click();
        setTimeout(function () {
          var feld = q('.title-editor');
          feld.value = 'Alpha neu';
          feld.dispatchEvent(new Event('input', { bubbles: true }));
          if (window.__ed) window.__ed.setMarkdown('# Alpha neu\n\nNeuer Text.');
          setTimeout(function () {
            knopf(/Speichern|Save/).click();
            setTimeout(function () {
              ok(titel().indexOf('Alpha neu') >= 0, 'neuer Name in der Liste: ' + titel().join('|'));
              ok(q('.content-title') && q('.content-title').textContent.trim() === 'Alpha neu',
                 'Seite zeigt den neuen Namen');
              ok(document.body.className.indexOf('dark') >= 0, 'Farbe unveraendert dunkel');

              log.push('--- Farbe wechseln');
              q('.theme-toggle').click();
              setTimeout(function () {
                ok(document.body.className.indexOf('dark') < 0, 'jetzt hell');

                log.push('--- Seite anlegen');
                q('.menu-toggle').click();
                setTimeout(function () {
                  var neu = neuKnopf();
                  ok(!!neu, 'Knopf fuer neue Seite da');
                  if (neu) neu.click();
                  setTimeout(function () {
                    var speichern = knopf(/Speichern|Save/);
                    if (speichern) speichern.click();
                    setTimeout(function () {
                      ok(titel().length === 3, 'drei Seiten: ' + titel().join('|'));
                      ende();
                    }, 1200);
                  }, 2600);
                }, 900);
              }, 900);
            }, 1200);
          }, 700);
        }, 3000);
      }, 2500);
    })();
    </script>
"""

# ---------------------------------------------------------------- Teil 3
# Wiki ohne Schivrecht: Bearbeiten abgeschaltet, Grund sichtbar
teil3 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        log.push('--- Wiki ohne Schivrecht');
        ok(q('.header') !== null, 'Oberflaeche ist da (lesbar)');
        ok(q('.content-title') && q('.content-title').textContent.trim() === 'Alpha',
           'Startseite lesbar: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
        ok(!q('.nurlesen-hinweis'),
           'vor dem ersten Schreibversuch gibt es keinen Hinweis (es wird nicht blind geprobt)');

        log.push('--- Der erste Schreibversuch sagt, woran es liegt');
        /* Die Farbe zu wechseln geht auch ohne Seitenrechte - und genau
           da faellt der Server mit 403 auf. */
        q('.theme-toggle').click();
        setTimeout(function () {
          var hinweis = q('.nurlesen-hinweis');
          ok(!!hinweis, 'Hinweis erscheint: ' + (hinweis ? hinweis.textContent.trim() : 'KEINER'));
          /* Dieses Wiki ist englisch - der Hinweis darf in beiden
             Sprachen kommen, nur nicht ohne Grund. */
          ok(hinweis && /nicht geschrieben|cannot be written/.test(hinweis.textContent),
             'nennt den Grund: ' + (hinweis ? hinweis.textContent.trim() : '-'));
          var bearbeiten = all('.footer .btn').filter(function (b) { return /Bearbeiten|Edit/.test(b.textContent); })[0];
          ok(bearbeiten && bearbeiten.disabled === true, 'Bearbeiten ist jetzt abgeschaltet');
          q('.menu-toggle').click();
          setTimeout(function () {
            var neu = all('.new-page-btn').filter(function (b) { return /Neue Seite|New Page/.test(b.textContent); })[0];
            ok(!!neu && neu.disabled === true, 'Neue Seite ist jetzt abgeschaltet');
            log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
            out();
          }, 500);
          log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
          out();
        }, 1200);
      }, 2500);
    })();
    </script>
"""

# ---------------------------------------------------------------- Teil 4
# Marker mit Inhalt, aber ohne Seiten: leer bleibt leer, nichts erfunden
teil4 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        log.push('--- Server-Wiki ohne Seiten');
        ok(!!q('.empty-state'), 'Leer-Zustand statt Willkommensseite: ' + (q('.empty-state h2') ? q('.empty-state h2').textContent.trim() : 'kein Leer-Zustand'));
        ok(localStorage.getItem('simplewiki_pages') === null,
           'nichts in den Browser geschrieben: ' + (localStorage.getItem('simplewiki_pages') || 'leer'));
        ok(all('.toc-item-title').length === 0, 'Verzeichnis leer');
        log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }, 2500);
    })();
    </script>
"""


# ---------------------------------------------------------------- Teil 5
# Loeschen und Startseite wechseln
teil5 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function titel() { return all('.toc-item-title').map(function (t) { return t.textContent.trim(); }); }
      function ende() { log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN')); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        log.push('--- Startseite wechseln');
        q('.settings-toggle').click();
        setTimeout(function () {
          var auswahl = q('#settings-startpage');
          var werte = all('#settings-startpage option').map(function (o) { return o.value; });
          var ziel = werte.filter(function (v) { return v && v !== q('.content-title').dataset.x; })[1] || werte.filter(function (v) { return !!v; })[1];
          ok(!!ziel, 'eine andere Seite zum Waehlen: ' + werte.join('|'));
          auswahl.value = ziel;
          auswahl.dispatchEvent(new Event('change', { bubbles: true }));
          setTimeout(function () {
            var stern = all('.toc-item').filter(function (i) { return !i.querySelector('.toc-item-start').classList.contains('is-empty'); })[0];
            ok(!!stern, 'genau ein Stern: ' + all('.toc-item').filter(function (i) { return !i.querySelector('.toc-item-start').classList.contains('is-empty'); }).length);
            q('.side-close').click();
            setTimeout(function () {
              log.push('--- Seite loeschen');
              q('.menu-toggle').click();
              setTimeout(function () {
                var ziel2 = all('.toc-item-title').filter(function (t) { return t.textContent.trim() !== (stern ? stern.querySelector('.toc-item-title').textContent.trim() : ''); })[0];
                var id2 = ziel2 ? ziel2.closest('.toc-item').querySelector('.toc-item-delete') : null;
                var vorher = titel().length;
                if (id2) id2.click();
                setTimeout(function () {
                  all('.modal .btn').filter(function (b) { return /öschen|Delete/.test(b.textContent); })[0].click();
                  setTimeout(function () {
                    ok(titel().length === vorher - 1,
                       'eine Seite weniger: ' + vorher + ' -> ' + titel().length + ' (' + titel().join('|') + ')');
                    ende();
                  }, 900);
                }, 700);
              }, 900);
            }, 700);
          }, 900);
        }, 900);
      }, 2500);
    })();
    </script>
"""

# ---------------------------------------------------------------- Teil 6
# Neuladen: was steht jetzt im Wiki?
teil6 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function titel() { return all('.toc-item-title').map(function (t) { return t.textContent.trim(); }); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        log.push('--- Neuladen zeigt den Stand des Servers');
        ok(titel().indexOf('Alpha neu') >= 0, 'der umbenannte Name steht noch da: ' + titel().join('|'));
        log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }, 2500);
    })();
    </script>
"""

# ---------------------------------------------------------------- Teil 7
# Marker ohne Inhalt: der Browser soll her, der Server nicht
teil7 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        log.push('--- Marker ohne Inhalt: der Browser');
        ok(q('.content-title') && q('.content-title').textContent.trim() === 'Aus dem Browser',
           'Seite aus dem Browser: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
        ok(!q('.mws-hinweis'), 'kein Serverhinweis');
        ok(all('.toc-item-title').length === 1, 'eine Seite: ' + all('.toc-item-title').length);
        log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }, 2500);
    })();
    </script>
"""


def lauf(name, skript, pfad, fenster=None):
    leeren()
    wikis[pfad.strip('/').split('/')[-1]].skript = skript
    dom = dumpdom_url(basis + pfad + '/', fenster, budget=120000)
    text = bericht(dom)
    print('%-22s %s' % (name, text.split('\n')[-1] if text else 'KEIN REPORT'))
    zeilen = [l for l in text.split('\n') if l.startswith('FAIL')]
    for l in zeilen:
        print('    ' + l)
    return text, anfragen()


print('=== MWS-Betrieb gegen einen eigenen kleinen Server ===')
try:
    text1, ruf1 = lauf('_mws_alpha', teil1, '/wiki/alpha')
    print()
    text2, ruf2 = lauf('_mws_schreiben', teil2, '/wiki/alpha')
    print()
    text3, ruf3 = lauf('_mws_nurlesen', teil3, '/wiki/nurlesen')
    print()
    text4, ruf4 = lauf('_mws_leer', teil4, '/wiki/leer')
    print()
    text5, ruf5 = lauf('_mws_streichen', teil5, '/wiki/alpha')
    print()
    text6, ruf6 = lauf('_mws_neuladen', teil6, '/wiki/alpha')
    print()
    text7, ruf7 = lauf('_mws_browser', teil7, '/wiki/ohne')
finally:
    beenden(server)

# ------------------------------------------------------------------ Auswertung
ok = fail = 0
for t in (text1, text2, text3, text4, text5, text6, text7):
    import re
    ok += len(re.findall(r'(?m)^OK\s', t))
    fail += len(re.findall(r'(?m)^FAIL\s', t))

print()
print('=== Was der Server bekommen hat ===')
post = [a for a in (ruf1 + ruf2) if a.get('weg') == 'POST']
print('Schreibaufrufe: %d, alle mit passendem Kopf: %s'
      % (len(post), all(a['kopf'] == 'fetch' for a in post)))
saves = [a for a in post if a.get('op') == 'save']
print('save-Aufrufe: %d' % len(saves))
print('davon einzelne Tiddler: %s'
      % ('ja' if all(len(a['nutzlast'].get('tiddlers') or []) == 1 for a in saves) else 'nein'))
print('Reihenfolge geschrieben: %s'
      % sorted(set(str((a['nutzlast']['tiddlers'][0] or {}).get('reihenfolge'))
                  for a in saves if (a['nutzlast'].get('tiddlers') or [{}])[0])))
alle_rufe = ruf1 + ruf2 + ruf3 + ruf4 + ruf5 + ruf6 + ruf7
print('updates abgerufen: %s'
      % ('ja' if any('updates' in (a.get('pfad') or '') for a in alle_rufe) else 'nein'))
post5 = [a for a in ruf5 if a.get('weg') == 'POST']
print('Loeschen als delete geschickt: %s'
      % ('ja, ' + str([a['nutzlast'].get('titles') for a in post5 if a.get('op') == 'delete'])
         if any(a.get('op') == 'delete' for a in post5) else 'nein'))
print('Startseite als $:/DefaultTiddlers geschickt: %s'
      % ('ja' if any((a['nutzlast'].get('tiddlers') or [{}])[0].get('title') == '$:/DefaultTiddlers'
                     for a in post5 if a.get('op') == 'save') else 'nein'))
print('Server bei leerem Marker angefragt: %s'
      % ('ja' if [a for a in ruf7 if a.get('weg') == 'POST'] else 'nein - der Browser reicht'))

# Was steht jetzt im Wiki?
wiki = wikis['alpha'].tiddler
print()
print('=== Stand im Wiki nach dem Schreiben ===')
print('Tiddler: %s' % sorted(k for k in wiki if k[:2] != '$:'))
start = [a for a in ruf1 + ruf2 if a.get('op') == 'save'
         and (a['nutzlast'].get('tiddlers') or [{}])[0].get('title') == '$:/DefaultTiddlers']
print('Startseite geschrieben: %s' % ('ja' if start else 'nein'))
alpha = wiki.get('a1', {})
print('a1 caption: %r  tags: %r  modified: %r'
      % (alpha.get('caption'), alpha.get('tags'), alpha.get('modified')))
print('Schreibversuch im Wiki ohne Schivrecht: %s'
      % ([('%s -> %s' % (a.get('op'), a.get('antwort'))) for a in ruf3 if a.get('weg') == 'POST']
         or 'keiner'))

print()
print('GESAMT: %d bestanden, %d fehlgeschlagen' % (ok, fail))
sys.exit(1 if fail else 0)