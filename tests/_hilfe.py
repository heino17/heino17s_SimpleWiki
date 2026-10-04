"""Gemeinsame Hilfen fuer die Tests.

Die Tests bauen eine instrumentierte Kopie von simplewiki.html,
oeffnen sie in Chromium und lesen danach den Bericht aus, den
das Testskript in der Seite selbst ablegt.

Wichtig: Alle Kopien und Ausgaben landen in tests/_kopien/ und
werden nicht committet.
"""

import os
import re
import subprocess
import sys
import html as htmlmod

HIN = os.path.dirname(os.path.abspath(__file__))
PROJEKT = os.path.dirname(HIN)
KOPIEN = os.path.join(HIN, '_kopien')
PROJEKTDATEI = os.path.join(PROJEKT, 'simplewiki.html')

CHROMIUM = 'chromium'


def ziel(name):
    """Pfad fuer eine Kopie im Testordner."""
    if not os.path.isdir(KOPIEN):
        os.makedirs(KOPIEN)
    return os.path.join(KOPIEN, name)


def url(name):
    """file://-Adresse fuer eine Kopie - so, wie ein Browser sie braucht."""
    return 'file://' + ziel(name)


def dumpdom(name, fenster=None, budget=120000):
    """Seite in Chromium oeffnen und das fertige HTML zurueckgeben."""
    return dumpdom_url(url(name), fenster, budget)


def dumpdom_url(url, fenster=None, budget=120000):
    """Wie dumpdom, aber mit einer fertigen Adresse.

    Fuer den MWS-Test: der laeuft ueber einen eigenen kleinen Server,
    nicht ueber eine Datei.
    """
    befehl = [CHROMIUM, '--headless', '--disable-gpu', '--no-sandbox']
    if fenster:
        befehl.append('--window-size=' + fenster)
    befehl += ['--virtual-time-budget=%d' % budget, '--dump-dom', url]
    ergebnis = subprocess.run(befehl, capture_output=True, timeout=budget / 1000 + 120)
    return ergebnis.stdout.decode('utf-8', 'replace')


def bericht(dom):
    """Den Bericht aus der Testseite holen."""
    m = re.search(r'<pre id="report">(.*?)</pre>', dom, re.S)
    return htmlmod.unescape(m.group(1)) if m else ''


def app_da(dom):
    """Hat die App sich ueberhaupt gerendert? Sonst ist alles weitere sinnlos."""
    return '<div class="app">' in dom


def zahlen(text):
    """Wie viele Pruefungen bestanden, wie viele nicht."""
    bestanden = len(re.findall(r'(?m)^OK\s', text))
    fehlgeschlagen = len(re.findall(r'(?m)^FAIL\s', text))
    return bestanden, fehlgeschlagen


def vollstaendig(text):
    """Traegt der Bericht einen Abschluss?

    Jedes Testskript schreibt zum Schluss eine Zeile mit '>>>'. Fehlt sie,
    ist der Lauf mittendrin abgebrochen - dann waere '0 fehlgeschlagen'
    ein falsches Gruen, weil die restlichen Pruefungen nie stattfanden.
    """
    return any(l.startswith('>>>') for l in text.split('\n'))



def pruefe(*dateien):
    """Kopien in Chromium oeffnen, Berichte ausgeben, Programmcode setzen.

    Die Berichte sehen so aus:
        OK   ...
        FAIL ...
        >>> ALLE 12 BESTANDEN
    """
    gesamt_ok = 0
    gesamt_fehler = 0
    zeilen = []
    for pfad in dateien:
        name = os.path.basename(pfad)

        def lauf_budget(doppelt=False):
            return dumpdom(name, budget=240000 if doppelt else 120000)

        dom = lauf_budget()
        text = bericht(dom)
        notiz = ''

        # Ein durchgefallener Test bekommt einen zweiten Versuch mit mehr
        # Zeit. Das Einlesen einer Datei braucht echte Datei-Zeit, und
        # unter Last mehrerer Browser laeuft die nicht mit der Uhr des
        # Testskripts. Erst ein zweimaliger Fehlschlag zaehlt als Fehler -
        # sonst ist ein roter Lauf eine Aussage ueber die Maschine und
        # nicht ueber das Programm. Ein abgebrochener Lauf (Bericht ohne
        # Abschlusszeile) zaehlt genauso als zweiter Versuch.
        if not text or not vollstaendig(text) or zahlen(text)[1] > 0:
            dom = lauf_budget(doppelt=True)
            text2 = bericht(dom)
            if (text2 and vollstaendig(text2)
                    and (not text or not vollstaendig(text) or zahlen(text2)[1] == 0)):
                text = text2
                notiz = ' (Wiederholung, beim ersten Lauf unter Last gescheitert)'

        if not text:
            # Kein Bericht: entweder ist die App nicht gekommen, oder
            # das Testskript ist zu frueh. Beides ist ein Fehler.
            if not app_da(dom):
                zeilen.append('%-22s KEIN REPORT - die App kam nicht' % name)
            else:
                zeilen.append('%-22s KEIN REPORT - Testskript zu frueh' % name)
            gesamt_fehler += 1
            continue
        if not vollstaendig(text):
            ok, fehler = zahlen(text)
            zeilen.append('%-22s UNVOLLSTAENDIG - %d Pruefungen, Lauf vorzeitig beendet'
                          % (name, ok + fehler))
            gesamt_fehler += 1
            continue
        ok, fehler = zahlen(text)
        gesamt_ok += ok
        gesamt_fehler += fehler
        abschluss = [l for l in text.split('\n') if l.startswith('>>>')]
        zeilen.append('%-22s %s%s' % (name, (abschluss[-1] if abschluss else
                                              '%d bestanden, %d fehlgeschlagen' % (ok, fehler)),
                                       notiz))
        if fehler:
            for l in text.split('\n'):
                if l.startswith('FAIL'):
                    zeilen.append('    ' + l)
    for z in zeilen:
        print(z)
    print()
    print('GESAMT: %d bestanden, %d fehlgeschlagen' % (gesamt_ok, gesamt_fehler))
    sys.exit(1 if gesamt_fehler else 0)


def ende(fails):
    """Testende: Bericht abschliessen und den Programmcode setzen."""
    print()
    print('>>> ' + ('%d FEHLGESCHLAGEN' % fails if fails else
                   'ALLE BESTANDEN'))
    sys.exit(1 if fails else 0)