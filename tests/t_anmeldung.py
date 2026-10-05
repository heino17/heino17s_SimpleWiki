"""Wer hier schreibt - und wer nicht.

Der Server sagt ueber GET /recipe/<name>/status, ob jemand angemeldet
ist, wie er heisst und ob dieser Tab schreiben darf. Die App macht daraus
drei sichtbare Zustaende:

  nicht angemeldet            Kopf sagt es, Hinweis sagt es, Schreibtasten
                              sind weg
  angemeldet, kein Recht     Kopf nennt den Namen, der alte Nur-Lesen-
                              Hinweis steht da, Schreibtasten sind weg
  angemeldet mit Recht       Kopf nennt den Namen, kein Hinweis, alle
                              Schreibtasten da

Und ein vierter Fall, der nur im Betrieb vorkommt: die Sitzung stirbt
zwischen der Statusabfrage und dem naechsten Schreibversuch. Dann muss
die App ohne Neuladen umschalten.

Siehe RecipeRoutes.ts in MWS fuer die echte Route.
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mwsserver import Wiki, starten, beenden, anfragen, leeren
from _hilfe import dumpdom_url, bericht

# ------------------------------------------------------------------ Inhalt
ALPHA = {'title': 'Alpha', 'sw-id': 'a1', 'text': '# Alpha\n\nText.',
         'reihenfolge': '0000'}
BETA = {'title': 'Beta', 'sw-id': 'b2', 'text': '# Beta\n\nNur Inhalt.',
        'reihenfolge': '0001'}
STANDARD = {'title': '$:/DefaultTiddlers', 'text': 'Alpha'}

# Alle drei Wikis haben Seiten - der Unterschied ist nicht der Inhalt,
# sondern die Antwort von /status.
wikis = {
    # 1) Niemand angemeldet: der Server nennt den Platzhalter "(anon)"
    'anonym': Wiki('anonym', [ALPHA, BETA, STANDARD],
                   status={'isLoggedIn': False, 'username': '(anon)',
                           'canUserWrite': False}),
    # 2) Angemeldet, aber die Wiki gehoert jemand anderem
    'gelesen': Wiki('gelesen', [ALPHA, BETA, STANDARD], titel='Gelesene Wiki',
                    status={'isLoggedIn': True, 'username': 'Frau Meyer',
                            'canUserWrite': False}),
    # 3) Angemeldet und zustaendig: alles da
    'schreib': Wiki('schreib', [ALPHA, BETA, STANDARD], titel='Schreibende Wiki',
                    status={'isLoggedIn': True, 'username': 'Frau Meyer',
                            'canUserWrite': True}),
    # 4) Die Sitzung stirbt beim ersten Schreibversuch
    'abgelaufen': Wiki('abgelaufen', [ALPHA, BETA, STANDARD], ablauf=True),
    # 5) Ohne gültige Antwort: der Server bricht die Verbindung ab
    'stumm': Wiki('stumm', [ALPHA, BETA, STANDARD], status_aus=True),
}

# ------------------------------------------------------------------ Test 1
# Nicht angemeldet: Hinweis mit dem richtigen Grund, Schreibtasten weg
anonym = r"""
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
        log.push('--- Niemand ist angemeldet');
        var hinweis = q('.nurlesen-hinweis');
        ok(!!hinweis, 'Hinweis steht da: ' + (hinweis ? hinweis.textContent.trim() : 'KEINER'));
        ok(hinweis && /nicht angemeldet|not logged in/i.test(hinweis.textContent),
           'nennt "nicht angemeldet", nicht nur "kein Schreibrecht": ' + (hinweis ? hinweis.textContent.trim() : '-'));
        var name = q('.benutzer-anzeige');
        ok(!!name && /Nicht angemeldet|Not logged in/i.test(name.textContent),
           'der Kopf sagt es auch: ' + (name ? name.textContent.trim() : 'KEINER'));
        /* Der Platzhalter des Servers "(anon)" ist ein Fuellwert, kein
           Name - er darf nirgends als Name auftauchen. */
        ok(!/\(anon\)/.test(document.body.innerText), 'der Platzhalter "(anon)" steht nirgends');
        ok(!/(👤)/.test(name ? name.textContent : ''), 'kein Namenszeichen ohne Namen');

        log.push('--- Kein Schreibweg, aber Leseweg');
        ok(!bearbeiten(), 'Bearbeiten ist weg');
        ok(!neueSeite(), 'Neue Seite ist weg');
        ok(!!q('.content-title') && q('.content-title').textContent.trim() === 'Alpha',
           'die Startseite laesst sich lesen');
        setTimeout(function () {
          ok(!q('.toc-item-delete'), 'das Loeschkreuz im Verzeichnis ist weg');
          ok(all('.toc-menu .toc-item').length === 2, 'beide Seiten im Verzeichnis: ' + all('.toc-menu .toc-item').length);
          log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
          out();
        }, 500);
        out();
      }, 2500);
    })();
    </script>
"""

# ------------------------------------------------------------------ Test 2
# Angemeldet, aber kein Schreibrecht: der Name steht da, der alte Hinweis
gelesen = r"""
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
        log.push('--- Angemeldet, aber kein Schreibrecht');
        var name = q('.benutzer-anzeige');
        ok(!!name && /Frau Meyer/.test(name.textContent),
           'der Name steht im Kopf: ' + (name ? name.textContent.trim() : 'KEINER'));
        ok(name && !name.classList.contains('ist-anonym'), 'und nicht als "anonym" markiert');
        var hinweis = q('.nurlesen-hinweis');
        ok(!!hinweis, 'Hinweis steht da: ' + (hinweis ? hinweis.textContent.trim() : 'KEINER'));
        /* Hier ist der Grund ein fehlendes Schreibrecht - nicht die
           fehlende Anmeldung. Genau darum sind es zwei Texte. */
        ok(hinweis && !/nicht angemeldet|not logged in/i.test(hinweis.textContent),
           'der Hinweis spricht nicht von Anmeldung: ' + (hinweis ? hinweis.textContent.trim() : '-'));
        ok(hinweis && /nicht geschrieben|cannot be written/.test(hinweis.textContent),
           'sondern vom fehlenden Schreibrecht');
        ok(!bearbeiten(), 'Bearbeiten ist weg');
        ok(!neueSeite(), 'Neue Seite ist weg');
        log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }, 2500);
    })();
    </script>
"""

# ------------------------------------------------------------------ Test 3
# Angemeldet mit Recht: nichts ausgeblendet, und es laesst sich wirklich
# schreiben - der Zustand darf nicht nur hübsch aussehen
schreiben = r"""
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
        log.push('--- Angemeldet mit Schreibrecht');
        var name = q('.benutzer-anzeige');
        ok(!!name && /Frau Meyer/.test(name.textContent), 'der Name steht im Kopf');
        ok(!q('.nurlesen-hinweis'), 'kein Nur-Lesen-Hinweis');
        ok(!!bearbeiten(), 'Bearbeiten ist da');
        ok(!!bearbeiten() && bearbeiten().disabled === false, 'und nicht abgeschaltet');
        ok(!!neueSeite(), 'Neue Seite ist da');

        log.push('--- Und geschrieben wird wirklich');
        neueSeite().click();
        setTimeout(function () {
          var feld = q('.title-editor');
          ok(!!feld, 'der Titelfeld ist da');
          if (feld) { feld.value = 'Gamma'; feld.dispatchEvent(new Event('input', { bubbles: true })); }
          var knopf = all('.footer .btn').filter(function (b) { return /Speichern|Save/.test(b.textContent); })[0];
          ok(!!knopf, 'der Speichern-Knopf ist da');
          if (knopf) knopf.click();
          setTimeout(function () {
            setTimeout(function () {
              var titel = all('.toc-menu .toc-item-title').map(function (t) { return t.textContent.trim(); });
              ok(titel.indexOf('Gamma') >= 0, 'die neue Seite steht im Verzeichnis: ' + titel.join('|'));
              log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
              out();
            }, 500);
          }, 1400);
        }, 700);
      }, 2500);
    })();
    </script>
"""

# ------------------------------------------------------------------ Test 4
# Die Sitzung stirbt im Betrieb. Ohne Neuladen muss die App umschalten -
# und zwar vom "kein Schreibrecht" zum "nicht angemeldet".
abgelaufen = r"""
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
        log.push('--- Vorher: alles da, der Name steht da');
        ok(!!bearbeiten(), 'Bearbeiten ist da');
        ok(!q('.nurlesen-hinweis'), 'kein Hinweis');

        log.push('--- Die Sitzung stirbt beim ersten Schreibversuch');
        /* Die Farbe zu wechseln geht auch ohne Seitenrechte - und genau
           da faellt der Server mit 403. */
        q('.theme-toggle').click();
        setTimeout(function () {
          ok(!bearbeiten(), 'Bearbeiten ist nach dem 403 weg');
          ok(!neueSeite(), 'Neue Seite ist nach dem 403 weg');
          var name = q('.benutzer-anzeige');
          ok(!!name && /nicht angemeldet|Not logged in/i.test(name.textContent),
             'der Kopf sagt jetzt "nicht angemeldet": ' + (name ? name.textContent.trim() : 'KEINER'));
          var hinweis = q('.nurlesen-hinweis');
          ok(!!hinweis && /nicht angemeldet|not logged in/i.test(hinweis.textContent),
             'der Hinweis nennt den neuen Grund: ' + (hinweis ? hinweis.textContent.trim() : '-'));

          log.push('--- Und die Knöpfe kommen auch nicht von selbst zurueck');
          /* Ein zweiter Schreibversuch kann nicht stattfinden - es gibt
             keinen Knopf mehr. Genau darum wird hier nichts geklickt. */
          setTimeout(function () {
            ok(!q('.toc-item-delete'), 'das Loeschkreuz bleibt weg');
            log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
            out();
          }, 500);
          out();
        }, 1600);
      }, 2500);
    })();
    </script>
"""

# ------------------------------------------------------------------ Test 5
# Ein Server, der auf /status nicht antwortet, ist kein Rechteproblem:
# die App darf sich nichts vormachen, aber auch nichts wegnehmen.
stumm = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function bearbeiten() { return all('.footer .btn').filter(function (b) { return /Bearbeiten|Edit/.test(b.textContent); })[0]; }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        log.push('--- /status antwortet gar nicht');
        ok(!q('.nurlesen-hinweis'), 'kein Hinweis aus dem Nichts');
        ok(!q('.benutzer-anzeige'), 'und keine Namensanzeige aus dem Nichts');
        ok(!!bearbeiten() && bearbeiten().disabled === false,
           'Bearbeiten bleibt moeglich - ein Ausfall ist kein Rechteproblem');
        ok(!!q('.content-title'), 'die Seite laesst sich lesen');
        log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
        out();
      }, 2500);
    })();
    </script>
"""


def lauf(name, skript, pfad):
    leeren()
    wikis[pfad.strip('/').split('/')[-1]].skript = skript
    dom = dumpdom_url(basis + pfad + '/', None, budget=120000)
    text = bericht(dom)
    print('%-22s %s' % (name, text.split('\n')[-1] if text else 'KEIN REPORT'))
    for l in [l for l in text.split('\n') if l.startswith('FAIL')]:
        print('    ' + l)
    return text, anfragen()


# ------------------------------------------------------------------ Start
print('=== Anmeldung und Schreibrechte gegen den Testserver ===')
try:
    server, thread, port = starten(wikis)
    basis = 'http://127.0.0.1:%d' % port

    text1, ruf1 = lauf('_anm_anonym', anonym, '/wiki/anonym')
    print()
    text2, ruf2 = lauf('_anm_gelesen', gelesen, '/wiki/gelesen')
    print()
    text3, ruf3 = lauf('_anm_schreiben', schreiben, '/wiki/schreib')
    print()
    text4, ruf4 = lauf('_anm_abgelaufen', abgelaufen, '/wiki/abgelaufen')
    print()
    text5, ruf5 = lauf('_anm_stumm', stumm, '/wiki/stumm')

finally:
    beenden(server)

# ------------------------------------------------------------------ Auswertung
ok = fail = 0
for t in (text1, text2, text3, text4, text5):
    ok += len(re.findall(r'(?m)^OK\s', t))
    fail += len(re.findall(r'(?m)^FAIL\s', t))

print()
print('=== Der Weg, den die App geht ===')
for name, ruf in (('anonym', ruf1), ('gelesen', ruf2), ('schreib', ruf3),
                  ('abgelaufen', ruf4), ('stumm', ruf5)):
    status_rufe = [a for a in ruf if '/status' in (a.get('pfad') or '')]
    saves = [a for a in ruf if a.get('op') == 'save']
    kopf = ('ja' if status_rufe and all(a.get('xhr') == 'fetch' for a in status_rufe)
            else ('nein' if status_rufe else 'kein Aufruf'))
    # Beim abgerissenen Server sind es zwei: Chromium wiederholt ein GET,
    # das auf einer geliehenen Verbindung ohne Antwort blieb. Die App
    # sieht davon nur das Scheitern.
    print('%-11s /status: %d (Kopf: %s), save: %d'
          % (name, len(status_rufe), kopf, len(saves)))

print()
print('GESAMT: %d bestanden, %d fehlgeschlagen' % (ok, fail))
sys.exit(1 if fail else 0)