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

# Die Konvention aus §102: der Tiddler heisst wie die Seite, die
# Kennung wandert als sw-id mit. Genau so schreibt MWS es.
ALPHA = {
    'title': 'Alpha', 'sw-id': 'a1', 'text': '# Alpha\n\nText mit [[Beta]].',
    'tags': '[[wichtig]] [[test]]', 'created': zw(2026, 2, 3, 10, 0, 0, 0),
    'modified': zw(2026, 2, 3, 11, 30, 45, 678), 'reihenfolge': '0001',
    'thema': 'dark', 'sprache': 'en',
}
BETA = {
    'title': 'Beta', 'sw-id': 'b2', 'text': '# Beta\n\nNur Inhalt.',
    'tags': '', 'created': zw(2026, 2, 3, 10, 5, 0, 0),
    'modified': zw(2026, 2, 3, 12, 0, 0, 0), 'reihenfolge': '0000',
}
# Ein Tiddler ganz ohne sw-id - so etwas hat ein Mensch oder MWS
# angelegt. Er muss sich laden lassen.
OHNE_KENNUNG = {
    'title': 'Ohne Kennung', 'text': '# Ohne Kennung\n\nKein sw-id am Tiddler.',
    'tags': '', 'created': zw(2026, 2, 3, 10, 6, 0, 0),
    'modified': zw(2026, 2, 3, 12, 1, 0, 0), 'reihenfolge': '0002',
}
STANDARD = {'title': '$:/DefaultTiddlers', 'text': 'Alpha'}
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
         'localStorage.setItem("simplewiki_theme","light");}catch(e){}</' + 'script>'
         + mkcopy.digest_seed())

# Was das Mapping aushalten muss: Umlaute, Sonderzeichen, ein Tiddler
# ohne Namen, doppelte Schlagworte, eine Zeit ohne Millisekunden und
# Systemtiddler, die keine Seiten sind.
KRAUS = [
    {'title': 'Ärzte & Söhne 🎉', 'sw-id': 'k1',
     'text': '# Ä\n\n[[Dritte]] und [Text](wiki:Dritte)',
     'tags': '[[mit leerzeichen]] [[emoji 🎉]]',
     'created': zw(2026, 7, 4, 12, 34, 56, 789), 'modified': zw(2026, 7, 4, 12, 34, 56, 789),
     'reihenfolge': '0000', 'thema': 'light', 'sprache': 'de'},
    {'title': 'Dritte', 'sw-id': 'k3', 'tags': '[[doppelt]] [[doppelt]]'},
    {'title': 'Ohne Millisekunden', 'sw-id': 'k4',
     'created': '20260203100000', 'modified': '20260203100000'},   # nur 14 Stellen
    {'title': '$:/bag-info', 'text': '{"bag":"default"}'},
    {'title': '$:/recipe-info', 'text': '{"recipe":"default"}'},
    {'title': '$:/EigeneSystemSache', 'text': 'nicht eine Seite'},
    {'title': '$:/SiteTitle', 'text': 'Krauses Wiki'},
    {'title': '$:/DefaultTiddlers', 'text': 'Ärzte & Söhne 🎉'},
]

wikis = {
    'alpha': Wiki('alpha', [BETA, ALPHA, OHNE_KENNUNG, STANDARD], titel='Alpha-Wiki',
                  untertitel='Klein und fein'),
    'nurlesen': Wiki('nurlesen', [ALPHA, BETA, STANDARD, NURLEBEN], nurLesen=True,
                     titel='Fremdes Wiki'),
    'leer': Wiki('leer', []),          # Marker mit Inhalt, aber ohne Seiten
    'ohne': Wiki('ohne', [ALPHA, BETA, STANDARD], store_leer=True,
                 vorab=VORAB),        # der Browser soll her
    'kaputt': Wiki('kaputt', [ALPHA, BETA, STANDARD],
                   fehler={'save': 500}),   # der Server faellt aus
    'kraus': Wiki('kraus', KRAUS, titel='Krauses Wiki'),
    # Leer, aber mit Inhalt im Marker: sonst wuerde der Browser die
    # Seiten nehmen und es gaebe nichts zu retten.
    'sackgasse': Wiki('sackgasse', [{'title': '$:/SiteTitle', 'text': 'Leeres Wiki'}]),
    # Fuer das Umbenennen: zwei Seiten, von denen eine auf die andere
    # verweist - in beiden Schreibweisen und mit Leerzeichen.
    'umbenannt': Wiki('umbenannt', [
        {'title': 'Alpha', 'sw-id': 'u1', 'text': '# Alpha\n\nIch verweise auf [[Beta]] '
         'und auf [Text](wiki:Beta).', 'tags': '',
         'created': zw(2026, 5, 1, 9, 0, 0, 0), 'modified': zw(2026, 5, 1, 9, 0, 0, 0),
         'reihenfolge': '0000'},
        {'title': 'Beta', 'sw-id': 'u2', 'text': '# Beta\n\nZurueck auf [[Alpha]].',
         'tags': '', 'created': zw(2026, 5, 1, 9, 1, 0, 0),
         'modified': zw(2026, 5, 1, 9, 1, 0, 0), 'reihenfolge': '0001'},
        {'title': '$:/DefaultTiddlers', 'text': 'Alpha'},
    ], titel='Umbenennungs-Wiki'),
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
      /* '.toc-menu' ist das Verzeichnis links. Es war einmal zweimal da -
         als Panel rechts und als Spalte links - und ohne diese
         Einschraenkung zaehlte jede Seite zweimal. */
      function titel() { return all('.toc-menu .toc-item-title').map(function (t) { return t.textContent.trim(); }); }
      function ende() { log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN')); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        log.push('--- Seiten kommen vom Server');
        ok(titel().join('|') === 'Beta|Alpha|Ohne Kennung',
           'Reihenfolge aus reihenfolge: ' + titel().join('|'));
        ok(q('.content-title') && q('.content-title').textContent.trim() === 'Alpha',
           'Startseite aus $:/DefaultTiddlers: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
        ok(titel().join('|') === 'Beta|Alpha|Ohne Kennung',
           'auch der Tiddler ohne sw-id ist eine Seite: ' + titel().join('|'));
        ok(q('.preview h1') && q('.preview h1').textContent.trim() === 'Alpha', 'Inhalt der Startseite');
        ok(q('.preview').textContent.indexOf('Nur Inhalt') < 0, 'nur die Startseite ist offen');

        log.push('--- Der Kopf traegt den Wiki-Namen');
        ok(q('.header h1') && q('.header h1').textContent.indexOf('Alpha-Wiki') >= 0,
           'Kopf zeigt $:/SiteTitle statt des festen Namens: ' +
           (q('.header h1') ? q('.header h1').textContent.trim() : '-'));
        ok(q('.kopf-untertitel') && q('.kopf-untertitel').textContent.trim() === 'Klein und fein',
           'Untertitel aus $:/SiteSubtitle: ' +
           (q('.kopf-untertitel') ? q('.kopf-untertitel').textContent.trim() : '-'));

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
      /* '.toc-menu' ist das Verzeichnis links. Es war einmal zweimal da -
         als Panel rechts und als Spalte links - und ohne diese
         Einschraenkung zaehlte jede Seite zweimal. */
      function titel() { return all('.toc-menu .toc-item-title').map(function (t) { return t.textContent.trim(); }); }
      function knopf(re) { return all('.footer .btn').filter(function (b) { return re.test(b.textContent); })[0]; }
      function ende() { log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN')); out(); }
      /* Nach der Klasse .kopf-neu suchen. Der Knopf traegt ein Zeichen
         und nicht seinen Namen; der Name steht als title daran. */
      function neuKnopf() { return q('.kopf-neu'); }
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
                setTimeout(function () {
                  var neu = neuKnopf();
                  ok(!!neu, 'Knopf fuer neue Seite da');
                  if (neu) neu.click();
                  setTimeout(function () {
                    var speichern = knopf(/Speichern|Save/);
                    if (speichern) speichern.click();
                    setTimeout(function () {
                      ok(titel().length === 4, 'vier Seiten: ' + titel().join('|'));
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
# Wiki ohne Schivrecht: die Schreibknöpfe sind weg, der Grund steht da -
# und zwar, BEVOR jemand irgendetwas probiert hat, weil /status es sagt
teil3 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function bearbeiten() { return all('.footer .btn').filter(function (b) { return /Bearbeiten|Edit/.test(b.textContent); })[0]; }
      function neueSeite() { return q('.kopf-neu'); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        log.push('--- Wiki ohne Schivrecht');
        ok(q('.header') !== null, 'Oberflaeche ist da (lesbar)');
        ok(q('.content-title') && q('.content-title').textContent.trim() === 'Alpha',
           'Startseite lesbar: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));

        log.push('--- Der Server sagt es von sich aus, ohne dass jemand fragt');
        var hinweis = q('.nurlesen-hinweis');
        ok(!!hinweis, 'Hinweis steht da, ohne Schreibversuch: ' + (hinweis ? hinweis.textContent.trim() : 'KEINER'));
        /* Dieses Wiki ist englisch - der Hinweis darf in beiden
           Sprachen kommen, nur nicht ohne Grund. */
        ok(hinweis && /nicht geschrieben|cannot be written/.test(hinweis.textContent),
           'nennt den Grund (hier: angemeldet, aber kein Schreibrecht): ' + (hinweis ? hinweis.textContent.trim() : '-'));
        var name = q('.benutzer-anzeige');
        ok(!!name && /Testnutzer/.test(name.textContent),
           'der Name steht im Kopf: ' + (name ? name.textContent.trim() : 'KEINER'));

        log.push('--- Die Schreibknoepfe sind weg, nicht nur blass');
        ok(!bearbeiten(), 'Bearbeiten ist weg (nicht abgeschaltet)');
        ok(!neueSeite(), 'Neue Seite ist weg');
        setTimeout(function () {
          ok(!q('.toc-item-delete'), 'das Kreuz im Verzeichnis ist auch weg');
          log.push('--- Lesen geht trotzdem');
          ok(!!q('.content-title'), 'die Seite laesst sich weiter lesen');
          log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
          out();
        }, 500);
        out();
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
        ok(all('.toc-menu .toc-item-title').length === 0, 'Verzeichnis leer');
        log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }, 2500);
    })();
    </script>
"""


# ---------------------------------------------------------------- Teil 11
# Die leere Wiki war eine Sackgasse: kein Knopf, mit dem man hereinkommt
teil11 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function knopf() { return q('.empty-state .empty-state-btn'); }
      function ende() { log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN')); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      window.addEventListener('unhandledrejection', function (e) {
        ok(false, 'Fehler in einer Zusage: ' + (e.reason && e.reason.message ? e.reason.message : e.reason));
      });

      setTimeout(function () {
        log.push('--- Ein Wiki ohne jede Seite');
        ok(!!q('.empty-state'), 'der Leer-Zustand steht da');
        var k = knopf();
        ok(!!k, 'und es gibt einen Knopf: ' + (k ? k.textContent.trim() : 'KEINER'));
        ok(!!q('.mws-hinweis'), 'es ist ein Wiki vom Server');
        ok(localStorage.getItem('simplewiki_pages') === null, 'im Browser ist noch nichts');

        log.push('--- Das X am Serverhinweis');
        var x = q('.mws-hinweis .mws-hinweis-weg');
        ok(!!x, 'das X ist da');
        if (x) x.click();
        setTimeout(function () {
          ok(!q('.mws-hinweis'), 'nach dem Klick ist der Hinweis weg');
          ok(sessionStorage.getItem('simplewiki_mws_hinweis') === '1',
             'fuer die Session gemerkt: ' + sessionStorage.getItem('simplewiki_mws_hinweis'));

          log.push('--- Klick');
          if (k) k.click();
          setTimeout(function () {
            var titel = all('.toc-menu .toc-item-title').map(function (t) { return t.textContent.trim(); });
            ok(titel.length === 1, 'eine Seite ist da: ' + titel.join('|'));
            ok(!q('.empty-state'), 'der Leer-Zustand ist vorbei');
            ok(!!q('.md-host .toastui-editor-defaultUI') || !!q('.editor'),
               'und man kann gleich reinschreiben');
            ende();
          }, 3000);
        }, 900);
      }, 2500);
    })();
    </script>
"""

# ---------------------------------------------------------------- Teil 12
# ... und sie ist nach dem Neuladen noch da, samt Startseite
teil12 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      setTimeout(function () {
        var titel = all('.toc-menu .toc-item-title').map(function (t) { return t.textContent.trim(); });
        ok(titel.length === 1, 'die Seite vom Server ist wieder da: ' + titel.join('|'));
        ok(!q('.empty-state'), 'kein Leer-Zustand mehr');
        var stern = all('.toc-menu .toc-item').filter(function (i) { return !i.querySelector('.toc-item-start').classList.contains('is-empty'); })[0];
        ok(!!stern, 'und sie ist die Startseite');
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
      /* '.toc-menu' ist das Verzeichnis links. Es war einmal zweimal da -
         als Panel rechts und als Spalte links - und ohne diese
         Einschraenkung zaehlte jede Seite zweimal. */
      function titel() { return all('.toc-menu .toc-item-title').map(function (t) { return t.textContent.trim(); }); }
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
            var stern = all('.toc-menu .toc-item').filter(function (i) { return !i.querySelector('.toc-item-start').classList.contains('is-empty'); })[0];
            ok(!!stern, 'genau ein Stern: ' + all('.toc-menu .toc-item').filter(function (i) { return !i.querySelector('.toc-item-start').classList.contains('is-empty'); }).length);
            q('.side-close').click();
            setTimeout(function () {
              log.push('--- Seite loeschen');
              setTimeout(function () {
                var ziel2 = all('.toc-menu .toc-item-title').filter(function (t) { return t.textContent.trim() !== (stern ? stern.querySelector('.toc-item-title').textContent.trim() : ''); })[0];
                var vorher = titel().length;
                /* Geloescht wird nur noch im Editor - im Verzeichnis gibt
                   es kein Kreuz mehr, es loescht eine ganze Seite. */
                ok(!q('.toc-item-delete'), 'im Verzeichnis ist kein Loeschkreuz');
                if (ziel2) ziel2.closest('.toc-item').click();
                setTimeout(function () {
                  all('.footer .btn').filter(function (b) { return /Bearbeiten|Edit/.test(b.textContent); })[0].click();
                  setTimeout(function () {
                    all('.footer .btn').filter(function (b) { return /öschen|Delete/.test(b.textContent); })[0].click();
                    setTimeout(function () {
                      all('.modal .btn').filter(function (b) { return /öschen|Delete/.test(b.textContent); })[0].click();
                      setTimeout(function () {
                        ok(titel().length === vorher - 1,
                           'eine Seite weniger: ' + vorher + ' -> ' + titel().length + ' (' + titel().join('|') + ')');
                        ende();
                      }, 900);
                    }, 700);
                  }, 700);
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
      /* '.toc-menu' ist das Verzeichnis links. Es war einmal zweimal da -
         als Panel rechts und als Spalte links - und ohne diese
         Einschraenkung zaehlte jede Seite zweimal. */
      function titel() { return all('.toc-menu .toc-item-title').map(function (t) { return t.textContent.trim(); }); }
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
        ok(all('.toc-menu .toc-item-title').length === 1, 'eine Seite: ' + all('.toc-menu .toc-item-title').length);
        log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }, 2500);
    })();
    </script>
"""


# ---------------------------------------------------------------- Teil 8
# Der Server faellt aus: der Grund muss im Bild stehen, und es darf
# nicht so tun, als waere das Wiki nur lesbar
teil8 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function hinweis() { var h = q('.hinweis'); return h ? h.textContent.trim() : ''; }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        log.push('--- Wiki, dessen Server ausfaellt');
        ok(!q('.nurlesen-hinweis'), 'zuerst kein Nur-Lesen-Hinweis');
        ok(all('.footer .btn').filter(function (b) { return /Bearbeiten|Edit/.test(b.textContent); })[0].disabled === false,
           'Bearbeiten ist an');
        log.push('--- Speichern und der Grund');
        all('.footer .btn').filter(function (b) { return /Bearbeiten|Edit/.test(b.textContent); })[0].click();
        setTimeout(function () {
          if (window.__ed) window.__ed.setMarkdown('# Alpha\n\nGeaendert.');
          setTimeout(function () {
            all('.footer .btn').filter(function (b) { return /Speichern|Save/.test(b.textContent); })[0].click();
            setTimeout(function () {
              ok(hinweis().length > 0, 'es steht ein Hinweis: "' + hinweis() + '"');
              ok(/SERVER_TEAPOT_save/.test(hinweis()), 'nennt den Grund vom Server: ' + hinweis());
              ok(/nicht gespeichert|not saved/i.test(hinweis()), 'sagt, dass es nicht gespeichert wurde');
              ok(!q('.nurlesen-hinweis'),
                 'kein Nur-Lesen-Hinweis: ein Ausfall ist kein Rechteproblem');
              var b2 = all('.footer .btn').filter(function (b) { return /Bearbeiten|Edit/.test(b.textContent); })[0];
              ok(!!b2 && b2.disabled === false, 'Bearbeiten bleibt moeglich');
              log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
              out();
            }, 1200);
          }, 700);
        }, 2800);
      }, 2500);
    })();
    </script>
"""


# ---------------------------------------------------------------- Teil 9
# Das Mapping an seinen Ecken: Sonderzeichen, fehlender Name, doppelte
# Schlagworte, eine Zeit ohne Millisekunden, Systemtiddler
teil9 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      /* '.toc-menu' ist das Verzeichnis links. Es war einmal zweimal da -
         als Panel rechts und als Spalte links - und ohne diese
         Einschraenkung zaehlte jede Seite zweimal. */
      function titel() { return all('.toc-menu .toc-item-title').map(function (t) { return t.textContent.trim(); }); }
      function ende() { log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN')); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      /* Ein Fehler in einem then() landet in einer unbehandelten
         Zusage und feuert kein error-Ereignis - ohne diesen Zuhaenger
         verschwaende er spurlos. */
      window.addEventListener('unhandledrejection', function (e) {
        ok(false, 'Fehler in einer Zusage: ' + (e.reason && e.reason.message ? e.reason.message : e.reason));
      });

      /* Die Daten holt der JSON-Export: er zeigt, was wirklich in der
         App steht, und geht dabei durch denselben Weg wie das Lesen. */
      function ueberJson(dann) {
        window.__blob = null;
        var echtesErzeugen = URL.createObjectURL;
        URL.createObjectURL = function (b) { window.__blob = b; return echtesErzeugen.call(URL, b); };
        HTMLAnchorElement.prototype.click = function () {};
        q('.settings-toggle').click();
        setTimeout(function () {
          all('.settings-btn').filter(function (b) { return /JSON/.test(b.textContent); })[0].click();
          setTimeout(function () {
            if (!window.__blob) { ok(false, 'JSON nicht erzeugt'); dann(null); return; }
            window.__blob.text().then(function (t) { dann(JSON.parse(t)); });
          }, 700);
        }, 700);
      }

      setTimeout(function () {
        log.push('--- Was als Seite ankommt');
        ok(titel().length === 3, 'genau drei Seiten, kein Systemtiddler: ' + titel().length + ' (' + titel().join('|') + ')');
        ok(titel()[0] === 'Ärzte & Söhne 🎉', 'Name mit Umlauten, kaufmaenischem Und und Emoji: ' + titel()[0]);
        ok(titel()[1] === 'Dritte' && titel()[2] === 'Ohne Millisekunden', 'die beiden anderen: ' + titel().slice(1).join('|'));
        ok(q('.content-title') && q('.content-title').textContent.trim() === 'Ärzte & Söhne 🎉',
           'Startseite aus $:/DefaultTiddlers: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));

        ueberJson(function (d) {
          if (!d) { ende(); return; }
          var seiten = {};
          d.seiten.forEach(function (x) { seiten[x.id] = x; });
          ok(d.seiten.length === 3, 'die App fuehrt ' + d.seiten.length + ' Seiten: ' +
             d.seiten.map(function (x) { return x.id; }).join('|'));

          log.push('--- Inhalt und Schlagworte');
          /* Achtung App-Feld gegen Tiddler-Feld: die Seite in der App
             heisst content, im Tiddler heisst es text. */
          ok(seiten.k1.content.indexOf('(wiki:Dritte)') > 0,
             'der wiki:-Link im Inhalt zeigt auf den Seitennamen: ' + JSON.stringify(seiten.k1.content));
          ok(JSON.stringify(seiten.k1.tags) === '["mit leerzeichen","emoji 🎉"]',
             'Schlagworte aus [[..]]: ' + JSON.stringify(seiten.k1.tags));
          ok(JSON.stringify(seiten.k3.tags) === '["doppelt"]',
             'doppelte Schlagworte einmal: ' + JSON.stringify(seiten.k3.tags));
          ok(seiten.k1.title === 'Ärzte & Söhne 🎉', 'der Tiddler-Titel ist der Name: ' + seiten.k1.title);
          ok(seiten.k1.id === 'k1', 'die Kennung kommt aus sw-id: ' + seiten.k1.id);
          ok(!('caption' in seiten.k1), 'kein caption-Feld mehr');

          log.push('--- Zeitstempel');
          ok(seiten.k1.created === '2026-07-04T12:34:56.789Z',
             'created aus 17 Stellen: ' + seiten.k1.created);
          ok(seiten.k1.updated === '2026-07-04T12:34:56.789Z',
             'modified aus 17 Stellen: ' + seiten.k1.updated);
          ok(seiten.k4.created === '', 'eine Zeit mit 14 Stellen wird nicht gelesen: ' + JSON.stringify(seiten.k4.created));

          log.push('--- Beim Schreiben: nichts zerstoeren, nichts erfinden');

          /* Einmal speichern: die Seite mit Umlauten und Schlagworten,
             damit am Anfragetext zu sehen ist, was hinausgeht. */
          function speichern(name, text, fertig) {
            all('.toc-menu .toc-item-title').filter(function (t) { return t.textContent.trim() === name; })[0].click();
            setTimeout(function () {
              all('.footer .btn').filter(function (b) { return /Bearbeiten|Edit/.test(b.textContent); })[0].click();
              setTimeout(function () {
                if (window.__ed) window.__ed.setMarkdown(text);
                setTimeout(function () {
                  all('.footer .btn').filter(function (b) { return /Speichern|Save/.test(b.textContent); })[0].click();
                  setTimeout(fertig, 1200);
                }, 700);
              }, 2800);
            }, 900);
          }

          speichern('Ärzte & Söhne 🎉', '# Ä\n\n[[k2]] und [Text](wiki:k3) - neu.', function () {
            /* Und die Seite mit der unbekannten Zeit: der Wert im
               Tiddler muss unangetastet bleiben. */
            speichern('Ohne Millisekunden', 'Ohne Millisekunden\n\nNeu.', function () { ende(); });
          });
        });
      }, 2500);
    })();
    </script>
"""


# ---------------------------------------------------------------- Teil 10
# Umbenennen: der Tiddler wandert, der alte wird geloescht, und die
# Verweise der anderen Seiten werden mitgezogen und gespeichert
teil10 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function knopf(re) { return all('.footer .btn').filter(function (b) { return re.test(b.textContent); })[0]; }
      function ende() { log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN')); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });
      window.addEventListener('unhandledrejection', function (e) {
        ok(false, 'Fehler in einer Zusage: ' + (e.reason && e.reason.message ? e.reason.message : e.reason));
      });

      setTimeout(function () {
        ok(q('.content-title') && q('.content-title').textContent.trim() === 'Alpha',
           'geoeffnet ist Alpha');
        log.push('--- Alpha umbenennen');
        knopf(/Bearbeiten|Edit/).click();
        setTimeout(function () {
          q('.title-editor').value = 'Alpha zwei';
          q('.title-editor').dispatchEvent(new Event('input', { bubbles: true }));
          setTimeout(function () {
            knopf(/Speichern|Save/).click();
            setTimeout(function () {
              ok(q('.content-title') && q('.content-title').textContent.trim() === 'Alpha zwei',
                 'im Bild heisst sie jetzt: ' + (q('.content-title') ? q('.content-title').textContent.trim() : '-'));
              log.push('--- Der Text der anderen Seite');
              all('.toc-menu .toc-item-title').filter(function (t) { return t.textContent.trim() === 'Beta'; })[0].click();
              setTimeout(function () {
                var text = q('.preview').textContent;
                ok(text.indexOf('Alpha zwei') >= 0, 'der Verweis zeigt auf den neuen Namen: ' + JSON.stringify(text.slice(0, 120)));
                ok(text.indexOf('[[Alpha]]') < 0, 'der alte Name ist weg');
                ende();
              }, 900);
            }, 1500);
          }, 700);
        }, 2800);
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
    print()
    text8, ruf8 = lauf('_mws_ausfall', teil8, '/wiki/kaputt')
    print()
    text9, ruf9 = lauf('_mws_kraus', teil9, '/wiki/kraus')
    print()
    text10, ruf10 = lauf('_mws_umbenannt', teil10, '/wiki/umbenannt')
    print()
    text11, ruf11 = lauf('_mws_sackgasse', teil11, '/wiki/sackgasse')
    print()
    text12, ruf12 = lauf('_mws_sackgasse_wieder', teil12, '/wiki/sackgasse')
    print()
    # ---- Der Kopf ist Pflicht: ohne ihn 400 INVALID_X_REQUESTED_WITH
    import urllib.request, urllib.error
    def roh_ruf(op, nutzlast, mit_kopf):
        anfrage = urllib.request.Request(
            basis + '/recipe/alpha/batch/' + op,
            data=json.dumps(nutzlast).encode('utf-8'),
            headers=dict([('Content-Type', 'application/json')] +
                        ([('X-Requested-With', 'fetch')] if mit_kopf else [])),
            method='PUT')
        try:
            with urllib.request.urlopen(anfrage, timeout=10) as antwort:
                return antwort.status, json.loads(antwort.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode('utf-8'))

    code_ohne, koerper_ohne = roh_ruf('list', {}, False)
    code_mit, _ = roh_ruf('list', {}, True)
    print('ohne X-Requested-With: %s %s' % (code_ohne, koerper_ohne.get('error')))
    print('mit  X-Requested-With: %s' % code_mit)

    # ---- Was beim Speichern wirklich rausgeht
    gesendet = {}
    for a in ruf1 + ruf2 + ruf5 + ruf9:
        if a.get('op') == 'save':
            for t in (a['nutzlast'].get('tiddlers') or []):
                gesendet[t.get('title')] = t
    k1 = gesendet.get('Ärzte & Söhne 🎉') or {}
    k4 = gesendet.get('Ohne Millisekunden') or {}
    print('--- Was beim Speichern rausgeht (Tiddler k1) ---')
    print('title ist der Name der Seite: %r' % k1.get('title'))
    print('sw-id traegt die Kennung: %r' % k1.get('sw-id'))
    print('kein caption mehr: %s' % ('caption' not in k1))
    print('tags als Listenformat, kein JSON-Array: %r' % k1.get('tags'))
    print('created 17 Stellen: %r' % k1.get('created'))
    print('unbekannte Zeit unangetastet (k4): %r' % k4.get('created'))

    # ---- Zeitstempel: 17 Stellen hin und zurueck, ohne Verlust
    alpha = wikis['alpha'].tiddler.get('Alpha', {})
    print('created unveraendert: %s (17 Stellen: %s)' % (alpha.get('created'),
                                                         len(str(alpha.get('created'))) == 17))
    print('modified 17 Stellen: %s' % (len(str(alpha.get('modified'))) == 17))
    # Der Weg ist in beiden Richtungen geschlossen und an der App geprueft:
    # der Test weiter oben hat 20260203100000000 als
    # 2026-02-03T10:00:00.000Z gelesen, und hier kommt der unveraenderte
    # 17-Steller wieder heraus. Beides ist dieselbe Zahl.
    print('Zeitweg hin und zurueck geschlossen: %s'
          % (alpha.get('created') == ALPHA['created']))

finally:
    beenden(server)

# ------------------------------------------------------------------ Auswertung
ok = fail = 0
for t in (text1, text2, text3, text4, text5, text6, text7, text8, text9,
              text10, text11, text12):
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
print('Reihenfolge geschrieben (Seiten): %s'
      % sorted(set(str((a['nutzlast']['tiddlers'][0] or {}).get('reihenfolge'))
                  for a in saves if (a['nutzlast'].get('tiddlers') or [{}])[0])))
alle_rufe = (ruf1 + ruf2 + ruf3 + ruf4 + ruf5 + ruf6 + ruf7 + ruf8 + ruf9
            + ruf10 + ruf11 + ruf12)
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
alpha = wiki.get('Alpha', {})
print('Tiddler "Alpha": sw-id=%r  tags=%r  modified=%r  caption-da=%r'
       % (alpha.get('sw-id'), alpha.get('tags'), alpha.get('modified'), 'caption' in alpha))
print('--- Umbenennen: was der Server bekommen hat ---')
umb_saves = [a for a in ruf10 if a.get('op') == 'save']
umb_del = [a for a in ruf10 if a.get('op') == 'delete']
print('gespeicherte Tiddler: %s' % [(a['nutzlast']['tiddlers'][0].get('title'),
                                       a['nutzlast']['tiddlers'][0].get('sw-id'))
                                      for a in umb_saves])
print('geloeschte Titel: %s' % [a['nutzlast'].get('titles') for a in umb_del])
print('im Wiki danach: %s' % sorted(k for k in wikis['umbenannt'].tiddler if k[:2] != '$:'))
print('--- Aus der Sackgasse ---')
sg_saves = [a for a in ruf11 if a.get('op') == 'save']
print('gespeicherte Tiddler: %s' % [(a['nutzlast']['tiddlers'][0].get('title'),
                                       a['nutzlast']['tiddlers'][0].get('sw-id'))
                                      for a in sg_saves])
print('Startseite gesetzt: %s' % [a['nutzlast']['tiddlers'][0].get('text') for a in sg_saves
                                  if a['nutzlast']['tiddlers'][0].get('title') == '$:/DefaultTiddlers'])
print('im Wiki danach: %s' % sorted(k for k in wikis['sackgasse'].tiddler if k[:2] != '$:'))
print('Schreibversuch im Wiki ohne Schivrecht: %s'
      % ([('%s -> %s' % (a.get('op'), a.get('antwort'))) for a in ruf3 if a.get('weg') == 'POST']
         or 'keiner'))

print()
print('GESAMT: %d bestanden, %d fehlgeschlagen' % (ok, fail))
sys.exit(1 if fail else 0)