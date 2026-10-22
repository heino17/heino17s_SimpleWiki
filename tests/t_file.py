import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import pruefe
mkcopy.EXTRA_REPLACEMENTS = []

seiten = [
    {"id": "1", "title": "Alpha", "content": "# Alpha\n\nmit </script> und <b>klammern</b>", "links": ["Beta"], "tags": [], "created": "x", "updated": "x"},
    {"id": "2", "title": "Beta", "content": "# Beta", "links": [], "tags": [], "created": "x", "updated": "x"},
    {"id": "3", "title": "Gamma", "content": "# Gamma", "links": [], "tags": [], "created": "x", "updated": "x"},
]

# Lauf 1: sichern – der Datei-Inhalt wird abgefangen, ohne echten Download.
script1 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      /* Knopf im Bereich Wiki-Daten nach Text suchen, statt nach Nummer:
         ein weiterer Knopf soll einen Test nicht umhauen. */
      function knopf(muster) {
        return [].slice.call(document.querySelectorAll('.settings-btn'))
                .filter(function (b) { return new RegExp(muster).test(b.textContent); })[0];
      }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      function head(m) { log.push('--- ' + m); out(); }

      /* Blob und Download abfangen, damit nichts wirklich gespeichert wird. */
      window.__blob = null; window.__name = null;
      var echtesErzeugen = URL.createObjectURL;
      URL.createObjectURL = function (b) { window.__blob = b; return echtesErzeugen.call(URL, b); };
      var echtesKlicken = HTMLAnchorElement.prototype.click;
      HTMLAnchorElement.prototype.click = function () { window.__name = this.download; };
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      /* Was wirklich am Feld ankommt: jeder Wechsel mit seinem Element
         und die gelesenen Dateien. Steht im Fehlerfall in der Meldung -
         ohne diese Zahlen weiss niemand, ob der Wechsel ins Leere ging
         oder der Hinweis nur nicht zu sehen war. */
      window.__changes = []; window.__reads = 0;
      document.addEventListener('change', function (e) {
        window.__changes.push((e.target.isConnected ? 'an' : 'AB') + ':' +
          (e.target.files ? e.target.files.length : '?'));
      }, true);
      var echtesLesen = FileReader.prototype.readAsText;
      FileReader.prototype.readAsText = function () { window.__reads++; return echtesLesen.apply(this, arguments); };

      setTimeout(function () {
        head('Einstellungen');
        q('.settings-toggle').click();
        setTimeout(function () {
          ok(!!q('.settings-panel.open'), 'Einstellungen offen');
          var knoepfe = all('.settings-btn').map(function (b) { return b.textContent.trim(); });
          ok(!!knopf('Als Datei sichern|Save as file'), 'sichern vorhanden');
          ok(!!knopf('JSON'), 'JSON-Knopf vorhanden');
          ok(!!knopf('Datei laden|Load file'), 'laden vorhanden');
          ok(knoepfe.length >= 3, 'Knöpfe im Bereich: ' + knoepfe.join(' / '));
          ok(!!q('input.datei-feld'), 'unsichtbares Dateifeld vorhanden');
          var hinweise = all('.settings-hint').map(function (h) { return h.textContent; }).join(' || ');
          ok(hinweise.indexOf('simplewiki.html') >= 0, 'Hinweis nennt den Dateinamen');
          ok(hinweise.indexOf('Reihenfolge') >= 0, 'Hinweis spricht die Reihenfolge an');

          head('Sichern');
          knopf('Als Datei sichern|Save as file').click();
          setTimeout(function () {
            ok(!!window.__blob, 'eine Datei wurde erzeugt');
            ok(window.__name === 'simplewiki.html', 'Dateiname: ' + window.__name);
            ok(!!q('.hinweis'), 'Hinweis erscheint: ' + (q('.hinweis') ? q('.hinweis').textContent.trim() : '-'));
            window.__blob.text().then(function (text) {
              window.__text = text;
              ok(text.indexOf('<!DOCTYPE html>') === 0, 'beginnt mit doctype');
              ok(text.indexOf('id="simplewiki-daten"') > 0, 'Datenblock vorhanden');
              var treffer = text.match(/<script id="simplewiki-daten"[^>]*>([\s\S]*?)<\/script>/);
              ok(!!treffer, 'Datenblock gefunden');
              var roh = treffer ? treffer[1] : '';
              ok(roh.indexOf('&quot;') < 0 && roh.indexOf('&amp;') < 0, 'Daten sind nicht HTML-maskiert');
              var daten = JSON.parse(roh.replace(/\\u003c/g, '<'));
              ok(daten.version === 1, 'Version: ' + daten.version);
              ok(daten.seiten.length === 3, 'drei Seiten: ' + daten.seiten.map(function (s) { return s.title; }).join('|'));
              ok(daten.seiten[0].title === 'Alpha', 'Reihenfolge erhalten: ' + daten.seiten.map(function (s) { return s.title; }).join('|'));
              ok(daten.startseite === '1', 'Startseite: ' + daten.startseite);
              ok(daten.sprache === 'de', 'Sprache: ' + daten.sprache);
              ok(daten.thema === 'light', 'Farbe: ' + daten.thema);
              var klammer = '<' + '/script>';
              ok(daten.seiten[0].content.indexOf(klammer) >= 0, 'Seiteninhalt mit ' + klammer + ' unversehrt');
              ok(roh.indexOf('\\u003c') >= 0, 'das spitze Zeichen ist im Datenblock escaped');
              ok(text.indexOf('class="header"') > 0, 'Oberflaeche steht in der Datei');
              ok(text.indexOf('class="toc-menu"') > 0, 'Inhaltsverzeichnis steht in der Datei');
              /* Die Bibliotheken stecken jetzt in der Datei. Nachweis ist
                 ihr eigener Versions-Banner - der CDN-Dateiname ist weg.
                 Die Muster entstehen aus Teilstuecken, damit sie nicht
                 selbst im exportierten Text auftauchen und sich treffen. */
              ok(text.indexOf('* vue v3') > 0, 'Vue ist eingebettet');
              ok(text.indexOf('* marked v') > 0, 'marked ist eingebettet');
              ok(text.indexOf('@toast-ui/editor') > 0, 'Editor ist eingebettet');
              var ladeSrc = new RegExp('<' + 'script[^>]+src=', 'i');
              var ladeCss = new RegExp('<' + 'link[^>]+rel=["\']?stylesheet', 'i');
              ok(!ladeSrc.test(text), 'kein Skript wird nachgeladen');
              ok(!ladeCss.test(text), 'kein Stylesheet wird nachgeladen');
              /* zweite Seite der Pruefung: wieder einlesen */
              head('Gesicherte Datei wieder einlesen');
              /* Auch hier auf den Hinweis warten statt auf eine feste
                 Zeit: das Einlesen braucht unter Virtual Time je nach
                 Last eine bis drei Sekunden. */
              var gemeldet = [];
              function merken() {
                var h = q('.hinweis');
                if (h) {
                  var t = h.textContent.trim();
                  if (t && gemeldet[gemeldet.length - 1] !== t) gemeldet.push(t);
                }
              }
              new MutationObserver(merken)
                .observe(document.body, { childList: true, subtree: true, characterData: true });

              var feld = q('input.datei-feld');
              var dt = new DataTransfer();
              /* Zum Einlesen eine schlanke Datei mit denselben Seiten,
                 nicht der 2,2-MB-Export: die Datei wird ueber den
                 FileReader gelesen, und der braucht echte Zeit. Unter
                 Virtual Time laeuft die Uhr des Tests schneller als das
                 Lesen - dann endet die Wartezeit, bevor der Hinweis da
                 ist. (Gemessen: Wechsel an:1, gelesen 1, kein Hinweis.)
                 Dass der volle Export die Seiten richtig traegt, steht
                 oben in seinen eigenen Pruefungen und in t_export.py. */
              var schlank = '<!DOCTYPE html><html><head><meta charset="utf-8">'
                + '<script id="simplewiki-daten" type="application/json">'
                + JSON.stringify(daten).replace(/</g, '\\u003c')
                + '<' + '/script></head><body></body></html>';
              dt.items.add(new File([schlank], 'simplewiki.html', { type: 'text/html' }));
              feld.files = dt.files;
              feld.dispatchEvent(new Event('change', { bubbles: true }));
              var versuche = 0, nachher = 0;
              (function warten() {
                versuche++;
                /* Auch selbst nachsehen, nicht nur dem Beobachter
                   vertrauen: der Hinweis verschwindet nach sechs
                   Sekunden wieder, und unter Virtual Time ist das
                   schnell. Zwischen zwei Beobachter-Meldungen kann er
                   schon wieder weg sein. */
                merken();
                /* Das Dateifeld ist nicht immer das Element, an dem die
                   Oberflaeche gerade haengt: Vue baut den Bereich neu
                   auf, und dann laeuft der Befehl an einem Feld vorbei,
                   das niemand mehr liest. Man sieht das nicht - es
                   kommt schlicht kein Hinweis, und der Test wartet
                   achtzehn Sekunden auf einen, der nicht kommen wird.
                   (Gemessen: 91 Runden, Dateifeld da, nichts am Schirm.)

                   Deshalb wird gemeldet, bis etwas kommt. Dasselbe
                   File zweimal zu laden ist harmlos - es steht danach
                   dasselbe drin.

                   Und jedes Mal das Feld neu suchen. Beim ersten
                   Versuch stand dort das Element, das Vue zuletzt
                   gebaut hat; nach einem Neuaufbau ist es eines, an
                   dem niemand mehr haengt. Ein zweites 'change' auf
                   DASSELBE Element zu schicken ist deshalb genau das
                   Falsche - man sieht am Element nichts, was ihn
                   verraten wuerde, und der Befehl geht ins Leere.

                   Neu gemeldet wird ueber die ganze Wartezeit, nicht
                   nur am Anfang: ein Neuaufbau kommt auch spaeter noch
                   (der Hinweis zum Sichern laeuft nach sechs Sekunden
                   ab und baut den Bereich mit neu). Nach Runde 30 stand
                   der Test sonst vor einem Feld, an dem niemand mehr
                   haengt - 91 Runden ohne Hinweis, und die Seiten waren
                   schon die richtigen, also fiel es nur an dieser einen
                   Pruefung auf. */
                if (versuche % 10 === 0) {
                  var neuFeld = q('input.datei-feld');
                  if (neuFeld) {
                    neuFeld.files = dt.files;
                    neuFeld.dispatchEvent(new Event('change', { bubbles: true }));
                    feld = neuFeld;
                  }
                }
                /* Gewartet wird auf einen Hinweis, der die Seitenzahl
                   nennt, und im schlimmsten Fall auf das Ende der
                   Runden. */
                if ((gemeldet.join(' | ').indexOf('3') >= 0) || versuche > 90) {
                  var titel = all('.toc-menu .toc-item-title').map(function (t) { return t.textContent.trim(); });
                  ok(titel.join('|') === 'Alpha|Beta|Gamma', 'Reihenfolge nach dem Laden: ' + titel.join('|'));
                  ok(JSON.parse(localStorage.getItem('simplewiki_pages')).length === 3, 'und gleich gespeichert');
                  /* Der Beleg steht in der Meldung: wie viele Runden, ob
                     es das Dateifeld gab, und was gerade zu sehen ist.
                     Vorher stand hier nur der Inhalt von 'gemeldet' -
                     und wenn der leer war, sagte die Meldung KEINER und
                     man wusste nicht, ob nichts kam oder nichts
                     aufgefangen wurde. */
                  var jetzt = q('.hinweis');
                  ok(gemeldet.join(' | ').indexOf('3') >= 0, 'Hinweis nennt die Seitenzahl: ' +
                     (gemeldet.join(' | ') || 'KEINER') +
                     ' [Runden ' + versuche + ', Dateifeld ' + (feld ? 'da' : 'fehlt') +
                     ', jetzt am Schirm: ' + (jetzt ? '"' + jetzt.textContent.trim() + '"' : 'nichts') +
                     ', Wechsel ' + window.__changes.join(',') + ', gelesen ' + window.__reads + ']');
                  log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
                  out();
                  return;
                }
                setTimeout(warten, 200);
              })();
            });
          }, 700);
        }, 700);
      }, 1400);
    })();
    </script>
"""


# Lauf 2: eine fremde Datei ohne SimpleWiki und eine kaputte.
script2 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      /* Jeder Hinweis wird notiert, statt auf eine Aenderung zu warten:
         zweimal dieselbe Meldung waere sonst nicht von der vorigen zu
         unterscheiden, und die Wartezeit wird zum Lotteriespiel. */
      var hinweisLog = [];
      new MutationObserver(function () {
        var h = q('.hinweis');
        if (h && h.textContent.trim()) {
          var letzter = hinweisLog[hinweisLog.length - 1];
          if (letzter !== h.textContent.trim() || hinweisLog.length === 0) hinweisLog.push(h.textContent.trim());
          else hinweisLog.push('\u0000' + h.textContent.trim());
        }
      }).observe(document.body, { childList: true, subtree: true, characterData: true });

      function lade(text, dann) {
        var vorher = hinweisLog.length;
        var feld = q('input.datei-feld');
        var dt = new DataTransfer();
        dt.items.add(new File([text], 'fremd.html', { type: 'text/html' }));
        feld.files = dt.files;
        feld.dispatchEvent(new Event('change', { bubbles: true }));
        var versuche = 0;
        (function warten() {
          versuche++;
          if (hinweisLog.length > vorher || versuche > 40) {
            setTimeout(dann, 200);
            return;
          }
          setTimeout(warten, 200);
        })();
      }
      function titel() { return all('.toc-menu .toc-item-title').map(function (t) { return t.textContent.trim(); }); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        q('.settings-toggle').click();
        setTimeout(function () {
          lade('<html><body><h1>Fremde Datei</h1></body></html>', function () {
            var gemeldet = hinweisLog.join(' || ').replace(/\u0000/g, ' || ');
            ok(hinweisLog.length > 0, 'Hinweis bei fremder Datei: ' + gemeldet);
            ok(gemeldet.indexOf('SimpleWiki') >= 0, 'Hinweis erklaert es');
            var vorher2 = hinweisLog.length;
            lade('<scr' + 'ipt id="simplewiki-daten" type="application/json">{kaputt' + String.fromCharCode(60) + '/script>', function () {
              ok(hinweisLog.length > vorher2, 'Hinweis bei kaputtem Inhalt');
              ok(titel().join('|') === 'Alpha|Beta|Gamma', 'Seiten unveraendert: ' + titel().join('|'));
              log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
              out();
            });
          });
        }, 700);
      }, 1400);
    })();
    </script>
"""


# Lauf 3: frischer Browser, Inhalt steckt nur in der Datei.
datei_daten = {
    "version": 1,
    "seiten": [
        {"id": "a", "title": "Aus der Datei", "content": "# Aus der Datei\n\nReihenfolge: 1, 2, 3", "links": [], "tags": [], "created": "x", "updated": "x"},
        {"id": "b", "title": "Zweite", "content": "# Zweite", "links": [], "tags": [], "created": "x", "updated": "x"},
        {"id": "c", "title": "Dritte", "content": "# Dritte", "links": [], "tags": [], "created": "x", "updated": "x"},
    ],
    "startseite": "c",
    "sprache": "en",
    "thema": "dark",
}
script3 = r"""
    <script>
    (function () {
      var log = [], fails = 0;
      function q(s) { return document.querySelector(s); }
      function all(s) { return [].slice.call(document.querySelectorAll(s)); }
      function out() { var p = document.getElementById('report'); if (!p) { p = document.createElement('pre'); p.id = 'report'; document.body.appendChild(p); } p.textContent = log.join('\n'); }
      function ok(c, m) { if (!c) fails++; log.push((c ? 'OK   ': 'FAIL ') + m); out(); }
      window.addEventListener('error', function (e) { ok(false, 'JS-Fehler: ' + e.message); });

      setTimeout(function () {
        ok(q('.content-title').textContent.trim() === 'Dritte', 'Startseite aus der Datei: ' + q('.content-title').textContent.trim());
        ok(!!q('.header .search-box') && !!q('.kopf-neu'), 'Kopfzeile da: Suchfeld und neue Seite');
        setTimeout(function () {
          var titel = all('.toc-menu .toc-item-title').map(function (t) { return t.textContent.trim(); });
          ok(titel.join('|') === 'Aus der Datei|Zweite|Dritte', 'Reihenfolge aus der Datei: ' + titel.join('|'));
          ok(!!q('.toc-menu .toc-item.active .toc-item-title') || all('.toc-menu .toc-item')[2].className.indexOf('active') >= 0, 'Dritte ist markiert');
          ok(document.body.className.indexOf('dark') >= 0, 'dunkle Farbe aus der Datei');
          ok(q('.settings-toggle').getAttribute('title') === 'Settings', 'englische Oberflaeche: ' + q('.settings-toggle').getAttribute('title'));
          ok(JSON.parse(localStorage.getItem('simplewiki_pages')).length === 3, 'und gleich in den Browser uebernommen');
          log.push(''); log.push('>>> ' + (fails ? fails + ' FEHLGESCHLAGEN' : 'ALLE ' + log.filter(function (l) { return /^OK|^FAIL/.test(l); }).length + ' BESTANDEN'));
          out();
        }, 700);
      }, 1400);
    })();
    </script>
"""

pruefe(
    build('_datei1.html', script1, seiten),
    build('_datei2.html', script2, seiten),
    build('_datei3.html', script3, [], seed=False, daten=datei_daten)
)
