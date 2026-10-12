import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import pruefe
mkcopy.EXTRA_REPLACEMENTS = []
mkcopy.PRE_SCRIPT = ''

# Ein einzelner Zeilenumbruch im Text muss in der Ansicht ein Umbruch
# bleiben. marked macht daraus von Haus aus ein Leerzeichen - dann laufen
# Zeilen wie "Name: x" / "Telefon: y" zu einer einzigen Zeile zusammen.
# Genau so kam es aus dem MWS-Wiki "wiki-admin-2" (Seite "Impressum").
# Der Test haelt fest, dass aus dem einen Umbruch ein <br> wird und dass
# zwei Umbrueche weiterhin zwei Absaetze bleiben.

inhalt = ("Name: Test\nAnschrift: Test\nTelefon: Test\nLand: Test"
          "\n\nZweiter Absatz\n")

pages = [
  {"id":"a","title":"Impressum","content":inhalt,"links":[],"tags":[],"created":"x","updated":"x"},
]

script = r"""
    <script>
    (function(){
      var log=[], fails=0;
      function q(s){return document.querySelector(s);}
      function all(s){return [].slice.call(document.querySelectorAll(s));}
      function out(){var p=document.getElementById('report'); if(!p){p=document.createElement('pre');p.id='report';document.body.appendChild(p);} p.textContent=log.join('\n');}
      function ok(c,m){if(!c)fails++;log.push((c?'OK   ':'FAIL ')+m);out();}
      function head(m){log.push('--- '+m);out();}
      window.addEventListener('error',function(e){ok(false,'JS-Fehler: '+e.message);});
      setTimeout(function(){
        head('Ein einfacher Zeilenumbruch bleibt ein Umbruch');
        var pv=q('.preview');
        ok(!!pv,'die Ansicht ist da');
        ok(all('.preview br').length===3,
           'aus drei einfachen Umbruechen werden drei <br>: '+all('.preview br').length);
        ok(all('.preview p').length===2,
           'zwei Umbrueche bleiben zwei Absaetze: '+all('.preview p').length);
        ok(pv.textContent.indexOf('Name: Test')>=0 && pv.textContent.indexOf('Land: Test')>=0,
           'die Zeilen stehen alle im Text');
        log.push(''); log.push('>>> '+(fails?fails+' FEHLGESCHLAGEN':'ALLE '+log.filter(function(l){return /^OK|^FAIL/.test(l);}).length+' BESTANDEN'));
        out();
      },3000);
    })();
    </script>
"""

pruefe(
    build('_umbruch.html', script, pages, theme='light', lang='de', startpage='a'),
)
