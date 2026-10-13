import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkcopy
from mkcopy import build
from _hilfe import pruefe
mkcopy.EXTRA_REPLACEMENTS = []
mkcopy.PRE_SCRIPT = ''

# Hinweiskaesten im GitHub-Stil: ein Zitat, dessen erster Absatz mit
# [!NOTE] beginnt (auch [!HINWEIS] und die uebrigen Marken), wird zum
# farbigen Kasten mit Titelzeile. Alles andere Zitat bleibt ein Zitat,
# und eine unbekannte Marke aendert nichts.

inhalt = ("# Hinweise\n\n"
          "> [!NOTE]\n> Das ist ein Hinweis.\n\n"
          "> [!WARNING]\n> Vorsicht.\n\n"
          "> [!HINWEIS]\n> Deutsch auch.\n\n"
          "> Ein gewoehnliches Zitat.\n> Zweite Zeile.\n\n"
          "> [!UNBEKANNT]\n> Bleibt ein Zitat.\n")

pages = [
  {"id":"a","title":"Hinweise","content":inhalt,"links":[],"tags":[],"created":"x","updated":"x"},
]

script = r"""
    <script>
    (function(){
      var log=[], fails=0;
      function q(s){return document.querySelector(s);}
      function all(s){return [].slice.call(document.querySelectorAll(s));}
      function ok(c,m){if(!c)fails++;log.push((c?'OK   ': 'FAIL ')+m);out();}
      function out(){var p=document.getElementById('report');if(!p){p=document.createElement('pre');p.id='report';document.body.appendChild(p);}p.textContent=log.join('\n');}
      function titel(k){var t=k.querySelector('.callout-titel');return t?t.textContent.trim():'';}
      function zitat(teil){return all('.preview blockquote').filter(function(b){return b.textContent.indexOf(teil)>=0;})[0];}
      window.addEventListener('error',function(e){ok(false,'JS-Fehler: '+e.message);});

      setTimeout(function(){
        var kaesten = all('.preview .callout');
        ok(all('.preview blockquote').length===5, 'fuenf Zitate: '+all('.preview blockquote').length);
        ok(kaesten.length === 3, 'drei davon sind Kaesten: '+kaesten.length);
        ok((all('.preview .callout')[0]||{className:''}).className.indexOf('callout-note')>=0,'der erste ist ein Hinweis');
        ok(titel(all('.preview .callout')[0])==='Hinweis','Titel: '+titel(all('.preview .callout')[0]));
        ok(all('.preview .callout')[0].textContent.indexOf('Das ist ein Hinweis.')>=0,'der Text steht im Kasten');
        ok((all('.preview .callout')[1].className||'').indexOf('callout-warning')>=0,'der zweite ist eine Warnung: '+all('.preview .callout')[1].className);
        ok(titel(all('.preview .callout')[1])==='Warnung','Titel: '+titel(all('.preview .callout')[1]));
        ok(titel(all('.preview .callout')[2])==='Hinweis','[!HINWEIS] wird auch zum Hinweis');
        ok(all('.preview .callout').every(function(k){return k.textContent.indexOf('[!')<0;}),'keine Marke steht mehr im Kasten');
        var gewoehnlich=zitat('gewoehnliches');
        ok(!!gewoehnlich && gewoehnlich.className.indexOf('callout')<0,'ein gewoehnliches Zitat bleibt ein Zitat');
        var unbekannt=zitat('UNBEKANNT');
        ok(!!unbekannt && unbekannt.className.indexOf('callout')<0,'eine unbekannte Marke aendert nichts');
        ok(!!unbekannt && unbekannt.textContent.indexOf('[!UNBEKANNT]')>=0,'die Marke bleibt sichtbar');
        log.push(''); log.push('>>> '+(fails?fails+' FEHLGESCHLAGEN':'ALLE '+log.filter(function(l){return /^OK|^FAIL/.test(l);}).length+' BESTANDEN'));
        out();
      },3000);
    })();
    </script>
"""

pruefe(
    build('_callout.html', script, pages, theme='light', lang='de', startpage='a'),
)
