# Änderungen

Nach Tag, das Neueste zuerst. Wo eine Überschrift eine Prüfungszahl nennt, ist
das der Stand der Suite nach diesem Schritt (`python3 tests/alle.py`).

Die Oberfläche nennt seit **v0.1.0** ihre Version: Sie steht in
`<meta name="mws-shell-version" content="v0.1.33">` im Kopf von
`simplewiki.html`, und MWS zeigt sie statt der reinen Release-Nummer — in der
Verwaltung und im Update-Hinweis. Bei jeder Oberflächenänderung wird diese
Version erhöht (die `<meta>`-Zeile ist die eine Stelle, die mitwächst). Datierte
Einträge bleiben zusätzlich, weil ein Tag sich nie streiten muss.

---

## 2026-10-13

---

## 2026-10-13

### v0.1.33 — Markdown hin und zurück — 1085 Prüfungen

Die offene Seite lässt sich jetzt als `.md`-Datei sichern: der Knopf 📝
steht in der Werkzeugleiste neben dem Drucker. Der Inhalt ist schon
Markdown, hier wird nichts umgewandelt; den Titel traegt der Dateiname
(Zeichen, die kein Dateisystem mag, werden zu `-`). Umgekehrt liest der
Einstellungen-Dialog unter „Daten" eine oder mehrere `.md`-Dateien ein:
der Dateiname ohne Endung wird der Titel, ein doppelter Name wird
eindeutig (`Notiz` wird zu `Notiz 2`), Verweise im Text werden notiert.
Anders als beim Laden einer Wiki-Datei wird dabei nichts ersetzt - die
neuen Seiten kommen dazu.

Geprueft in einem Entwicklungsstand: im Browser die Seite `Alpha` ueber
den Werkzeugleisten-Knopf gesichert (`Alpha.md`, Inhalt unveraendert),
eine Seite mit Schraegstrich im Titel gesichert (`Bericht - 2026.md`),
zwei `.md`-Dateien eingelesen und gesehen, dass `Notiz` und `Alpha 2` im
Verzeichnis stehen, der Hinweis die Zahl nennt und Inhalt wie Verweis im
Browserspeicher liegen; am Server dieselben Schritte, und die neue Seite
kommt als Tiddler an. `tests/t_markdown.py` prueft alle drei Wege.

### v0.1.32 — eine Werkzeugleiste unter dem Kopf — 1066 Prüfungen

Unter der Kopfzeile liegt jetzt eine zweite Zeile mit den Werkzeugen, die
nicht in jeden Kopf gehören: **Wortzahl und Lesezeit** der offenen Seite, der
**ablenkungsfreie Modus** (⛶) und der **Druck genau dieser Seite**. Die Leiste
ist standardmäßig aus und wird im Einstellungen-Dialog unter „Werkzeugleiste
anzeigen" eingeschaltet.

Der Schalter ist eine Einstellung wie die Farbe und kein Inhalt: im Browser
steht er in `localStorage` (`simplewiki_toolbar`), am Server als Feld
`toolbar` am Tiddler der Startseite, und in der Austauschform als `toolbar`
oben. Ein fehlendes Feld heißt aus. Ältere Fassungen lassen den unbekannten
Schlüssel unberührt, deshalb bleibt `version` bei 1. Das neue Feld am Tiddler
und der neue Schlüssel im Austausch sind mit MWS-wikiwise abgesprochen; das
entsprechende `.tid`-Feld und die Vorlage dort ziehen nach.

Die Wortzahl zählt den Fließtext — Codeblöcke sind vorher ausgeblendet, die
Ziele von Verweisen zählen nicht mit. Aus ihr folgt die Lesezeit mit 200
Wörtern je Minute, aufgerundet und mindestens eine Minute. Der ablenkungsfreie
Modus blendet Kopfzeile, Leiste und Verzeichnis aus; ein schwebender Knopf oben
rechts oder **Escape** holt zurück, gespeichert wird nichts. Der Druck der
offenen Seite ist die Gegenprobe zum Fluss: der `beforeprint`-Zuhörer schaltet
hier bewusst nicht in den Fluss um, denn wer diese Taste drückt, meint genau
diese eine Seite und nicht das ganze Wiki.

`tests/t_werkzeug.py` prüft alle drei Wege (Browser, Startseiten-Tiddler,
JSON) und den Druck. Das neue Feld am Tiddler und der neue Schlüssel im
Austausch tragen `toolbar` als Namen.

## 2026-10-12

### v0.1.31 — zugeklappt bleibt nichts vom Inhaltsverzeichnis stehen — 1040 Prüfungen

Beim Einklappen des Verzeichnisses blieben die ersten Buchstaben der
Überschrift „Inhaltsverzeichnis" am linken Rand stehen. Die Spalte fährt auf
Breite 0, aber die Kopfzeile darin ist ein Flex-Kind und bleibt so breit wie
die Spalte **plus ihre seitliche Polsterung** — bei `padding: 14px 20px` also
40px, und darin standen die ersten drei Buchstaben. Zugeklappt legt die
Kopfzeile ihre seitliche Polsterung jetzt ab (und die Liste ebenso); der
`overflow` kappt dann wirklich bei 0. Offen ist alles unverändert. Die CSS-Regel
prüft `t_menue.py`.

## 2026-10-11

### Die Buchhaltung prüft sich selbst — 1040 Prüfungen

`tests/t_buchhaltung.py` ist neu: eine Prüfung ohne Browser, die die
Buchhaltung nachliest, statt sie herzustellen. Sie vergleicht die
Strukturtafel der README mit `simplewiki.html`, die Fassung im
`<meta>`-Kopf und im README-Beispiel mit der obersten `### vX.Y.Z`-Überschrift
des CHANGELOG und die Zahl der Testdateien in README und AGENTS mit
`REIHENFOLGE` in `alle.py`. Die Prüfungszahl selbst wird dabei nicht erzwungen
— sie steht erst nach einem vollen Durchgang fest, und ein Test soll nicht
scheitern, solange `buchhaltung.py` noch nicht nachgetragen hat. Die README
nennt dafür keine Zahl mehr, die sich nicht zählen lässt: aus „rund 78
Browserläufe pro Suite-Lauf" ist der Hinweis auf die beiden Drucktests
geblieben, die Chromium ein zweites Mal starten.

### Die Buchhaltung der Zahlen an einer Stelle — 1030 Prüfungen

Dieselben Zahlen stehen an mehreren Orten und mussten bisher von Hand
mitgezogen werden: die Fassung in der `<meta>`-Zeile von `simplewiki.html`, in
`README.md` und im Kopf des CHANGELOG, die Prüfungszahl in der obersten
CHANGELOG-Überschrift, Testdateien und Prüfungen in `README.md` und `AGENTS.md`
und die Strukturtafel mit Länge und Zeilenspannen. Genau dort hat es zuletzt
gehakt: die README nannte noch 30 Testdateien und 933 Prüfungen, AGENTS 33.

`tests/buchhaltung.py` stellt sie jetzt an einer Stelle her. Es liest den
Aufbau aus `simplewiki.html` selbst — die Länge und die Grenzen der Teile an
ihren Merkmalen, nicht gezählt von Hand —, die Fassung aus der obersten
`### vX.Y.Z`-Überschrift des CHANGELOG und die Prüfungszahl aus dem letzten
vollen Durchgang, den `alle.py` in `tests/_kopien/letzter_lauf.json` ablegt:

```bash
python3 tests/alle.py             # erst grün werden
python3 tests/buchhaltung.py      # dann buchhalten
python3 tests/buchhaltung.py --check   # nur melden (Endcode 1 = veraltet)
```

Ein gefilterter Lauf (`alle.py fluss`) schreibt keinen Bericht — eine halbe
Suite darf keine ganze Zahl setzen. Stimmt die Zahl der Dateien im Bericht
nicht mehr mit der Suite überein, warnt das Skript. Die Prüfungszahlen älterer
Überschriften bleiben stehen: das ist die Geschichte, nicht der Stand. Nur die
oberste Überschrift bekommt die geltende Zahl.

### Die Testsuite läuft jetzt gleichzeitig — 1030 Prüfungen

`tests/alle.py` hat die 34 Dateien bisher nacheinander gestartet; ein Lauf
dauerte gut zehn Minuten. Jetzt laufen sie gleichzeitig: die Zahl der
Prozessoren gibt die Voreinstellung, `-j N` stellt sie ein, `-j 1` ist der alte
Lauf. Ein Test ist ein eigener Prozess mit eigener Kopie und eigenem
Browserfenster, deshalb stören sie sich nicht; der Bericht steht weiter in
fester Reihenfolge da, oben nur die Fortschrittszeilen mit der Dauer je Datei.
Auf vier Prozessoren fällt ein Lauf damit von gut zehn Minuten auf etwa
zweieinhalb. Geändert hat sich nur das Testwerkzeug; `simplewiki.html` bleibt
unberührt, die Shell-Version steigt nicht.

### v0.1.30 — das Inhaltsverzeichnis ist nur so breit wie nötig — 1030 Prüfungen

Die Spalte links nahm feste `--toc-breite` (360px, in schmalen Fenstern 300px)
und ließ kurze Verzeichnisse mit viel leerem Raum stehen. Jetzt gilt
`width: fit-content`: das Menü ist so breit wie sein längster Eintrag, sehr
lange Titel werden weiterhin bei `--toc-breite` gekappt. Damit das Fähnchen
mitwandert, sitzt es jetzt im Menü selbst an der Innenkante (`left: 100%`)
statt an einer festen Zahl am Textkörper; `overflow: hidden` wandert von der
Spalte in ihre beiden Kinder, damit beim Auf- und Zuklappen nichts quillt.
Nebenbei sind die Menüzeilen etwas enger gerückt (Polsterung am Eintrag
entfernt, die leere Stern-Spalte nachgezogen) - eine Handkorrektur, die so
bleiben soll. Geändert hat sich nur das SimpleWiki; der Austausch mit MWS
bleibt unberührt. Version v0.1.29 → v0.1.30.

### v0.1.29 — der Zeilenabstand in der Seitenansicht kleiner — 1029 Prüfungen

Der Zeilenabstand in `.preview` war `1.8`; er ist auf `1.5` gesenkt. Das
macht die Seiten lesbarer, ohne dass die Abstände zwischen Absätzen zu eng
werden. Geändert hat sich nur das SimpleWiki; der Austausch mit MWS bleibt
unberührt. Version v0.1.28 → v0.1.29.

### v0.1.28 — einfache Zeilenumbrüche bleiben erhalten — 1029 Prüfungen

Im Text einer Seite machte marked aus einem einzelnen Zeilenumbruch bisher ein
Leerzeichen, deshalb liefen Zeilen wie "Name: Test" und "Anschrift: Test" nach
dem Speichern zu "Name: Test Anschrift: Test" zusammen. Jetzt wird mit
`{ breaks: true }` beim Rendern aus jedem einfachen Zeilenumbruch ein `<br>`,
zwei aufeinanderfolgende Umbrüche bleiben zwei Absätze. Der Editor liefert
nach wie vor die normale Markdown-Struktur, und die Umwandlung gilt nur bei
der Anzeige. Geändert hat sich nur das SimpleWiki; der Austausch mit MWS bleibt
unberührt. Version v0.1.27 → v0.1.28.

### v0.1.27 — der Fuss in den Einstellungen nennt Name und Version — 1025 Prüfungen

Ganz unten im Einstellungen-Panel steht jetzt eine Zeile: der Titelblock des
Kopfes (`<div class="kopf-titel">`, also 📚 plus Wiki-Name und, wenn es ihn
gibt, der Untertitel) und daneben die Version der Oberfläche, klein wie ein
Hinweis. Die Version ist ein Verweis und führt zu
<https://github.com/heino17/>. Die Nummer selbst wird nicht im Fuss gepflegt,
sondern aus `<meta name="mws-shell-version">` gelesen — die eine Stelle, an der
die Version steht, bleibt die eine Stelle. Der Fuss hängt als eigener Streifen
unter dem rollenden Inhalt des Panels und bleibt deshalb beim Scrollen stehen.
Geändert hat sich nur das SimpleWiki; der Austausch mit MWS bleibt unberührt.
Version v0.1.26 → v0.1.27.

### v0.1.26 — die Überschriften haben eigene Farben — 1021 Prüfungen

In der eigenen Farbwelt („eigene Farben") gibt es jetzt drei neue Zeilen für die
Überschriften: H1, H2 und H3. Man wählt also für jede Ebene eine eigene Farbe,
statt sie der Textfarbe zu überlassen. Die H2-Farbe färbt zusätzlich den Namen
im Fluss-Kopf (`<h2 class="content-title">` und `.fluss-titel-knopf`) — wer die
H2-Farbe ändert, sieht sie an beiden Stellen. Die neuen Farbnamen `h1-color`,
`h2-color` und `h3-color` setzt nur die eigene Farbwelt; die festen Farbwelten
lassen sie leer, deshalb bleibt deren Aussehen unverändert (der Fluss-Knopf
behält weiterhin seine Akzentfarbe). Ohne eigene Farbwahl zeigt das Feld die
Textfarbe als Vorschau, nicht Schwarz. Die drei Namen sind optional und dürfen
fehlen — der Austausch mit MWS bleibt unberührt, es wächst nur die Zahl der
Einträge in `eigeneFarben` (Farben 15 → 18). Geändert hat sich nur das
SimpleWiki. Version v0.1.25 → v0.1.26.

### v0.1.25 — der Untertitel rückt unter den Namen — 1016 Prüfungen

Der Untertitel aus `$:/SiteSubtitle` stand bündig links im Kopf, also unter dem
Buch-Emoji 📚 statt unter dem Wiki-Namen. Jetzt trägt `.header .kopf-untertitel`
`padding-left: 30px` und steht damit unter dem Namen. Bewusst ein fester Wert
statt `2vw`: Die Einrückung bleibt so auf jedem Fenster gleich groß. Geändert
hat sich nur das SimpleWiki — der Austausch mit MWS bleibt unberührt. Version
v0.1.24 → v0.1.25.

### v0.1.24 — der Kopf zeigt auch den Untertitel — 1016 Prüfungen

Neben dem Anzeigenamen (`displayName`) kennt die MWS-Verwaltung jetzt ein Feld
„Untertitel". Der Server legt ihn als Tiddler `$:/SiteSubtitle` ab — genauso wie
`$:/SiteTitle` für den Namen. SimpleWiki liest ihn beim Laden ein (`wikiUntertitel`)
und schreibt ihn als kleine, gedämpfte Zeile direkt unter den Wiki-Namen im Kopf.
Fehlt er, bleibt der Kopf wie vorher; im Browser ohne Server erscheint keine
Zeile. Geändert hat sich nur das SimpleWiki — der Austausch mit MWS bleibt
unberührt. Der Test `t_mwsmode.py` hält im ersten Teil fest, dass gegen
`/wiki/alpha` unter „Alpha-Wiki" die Zeile „Klein und fein" steht. Version
v0.1.23 → v0.1.24.

### v0.1.23 — der Kopf zeigt den Namen des Wikis — 1015 Prüfungen

Oben in der Oberfläche stand fest „📚 SimpleWiki", gleich in welchem Wiki man
war. Im MWS-Betrieb gibt sich jede Wiki aber einen Anzeigenamen — genau das,
was die Verwaltung im Feld `displayName` führt. Der Server legt ihn längst als
Tiddler `$:/SiteTitle` ab, und SimpleWiki las ihn auch schon ein (`wikiTitel`),
nur benutzte es ihn nirgends. Jetzt steht er in der Überschrift: Aus
`<h1>📚 SimpleWiki</h1>` wird `📚 <Name>`. Im Browser, wo es keinen Server und
damit keinen Anzeigenamen gibt, bleibt es beim festen „SimpleWiki"; ebenso,
wenn der Anzeigename leer ist. Geändert hat sich nur das SimpleWiki — der
Austausch mit MWS bleibt unberührt. Der Test `t_mwsmode.py` hält im ersten Teil
fest, dass der Kopf gegen `/wiki/alpha` „Alpha-Wiki" zeigt. Version v0.1.22 →
v0.1.23.

### v0.1.22 — der Knopf heißt jetzt Speichern — 1014 Prüfungen

Im Verlinken-Fenster hieß der linke Knopf „Schließen". Das stimmte zwar — ein
Klick nimmt die Auswahl mit und schließt —, aber es las sich, als müsse man
noch woanders bestätigen; der „Anlegen und verlinken"-Knopf daneben ist
absichtlich so lange aus, bis ein neuer Name im Feld steht, und so sah es aus,
als sei gar kein Abschluss möglich. Der Knopf heißt jetzt „Speichern". Geändert
hat sich nur die Beschriftung, in allen acht Sprachen (`linkSave`); das
Verhalten bleibt, wie es in v0.1.21 beschrieben steht. Der Test `t_link4.py`
prüft die Beschriftung mit.

### v0.1.21 — das Verlinken-Fenster bleibt offen — 1013 Prüfungen

Bisher schloss sich das Fenster „Seite verlinken", sobald man eine Seite
anklickte. Wer drei Seiten verknüpfen wollte, öffnete es dreimal. Jetzt bleibt
es stehen, während man Seiten an- und abwählt, und die Häkchen zeigen den
Stand. Geschlossen wird es erst über die Knöpfe unten — „Schließen" und
„Anlegen und verlinken". Auch ein Klick auf den Hintergrund lässt es offen;
das ist die Entscheidung, denn das Fenster gehört zum Verknüpfen, das man
meist mehrfach tut. Bricht man das Bearbeiten ab, schließt es sich mit.

Der Test `t_link4.py` hält beides fest: Nach dem Anklicken einer Seite ist das
Fenster noch da, und über den Knopf geht es wieder zu. Version v0.1.20 →
v0.1.21.

### v0.1.20 — die eigene Farbwelt zum Bearbeiten — 1012 Prüfungen

Die Farbwelten waren bisher fertig: Man wählte eine aus, und in hell wie dunkel
sah sie so aus, wie sie gebaut war. Jetzt kommt eine neunte Welt dazu, die
**Eigene**, und sie lässt sich einstellen. Im Einstellungen-Dialog erscheint bei
ihr ein Editor: Oben steht ein Feld mit allen vorhandenen Welten und daneben
**Übernehmen** — damit wird die gewählte Welt geklont, heller und dunkler Zweig
zugleich. Darunter stehen die neunzehn Farbvariablen, nach Flächen, Text,
Rahmen, Kästen und Textur gruppiert. Ein Klick auf Hell oder Dunkel schaltet
nicht nur die angezeigten Werte um, sondern gleich das Erscheinungsbild, sodass
jede Änderung sofort dort zu sehen ist, wo sie hingehört. Ein **Zurücksetzen**
verwirft die eigene Welt wieder.

Die meisten Werte haben einen Farbwähler. Die vier durchsichtigen Farben
(`--overlay-bg`, `--shadow-color`, `--textur-kopf`, `--textur-inhalt`) bekommen
stattdessen ein Textfeld, weil ein Farbwähler keine Transparenz kennt. Fehlt ein
eigener Wert, bleibt der der geklonten Welt stehen — niemand muss alle neunzehn
füllen. Ungültige Eingaben werden nicht übernommen, damit ein halb getipptes
`rgba(...)` die Oberfläche nicht unlesbar macht.

Gespeichert wird die eigene Welt als Objekt aus `basis`, `hell` und `dunkel`:
im Browser unter `simplewiki_eigene_farben`, am Server als Feld `eigeneFarben`
am Startseiten-Tiddler (als JSON-Zeichenkette), und in der gesicherten Datei in
der Dateninsel. Wer eine Datei weitergibt, nimmt seine Farben mit; das
Austauschformat bekommt dafür ein Feld mehr. Beim Setzen half ein Fehler, den
erst der Test zeigte: `MwsStore.laden` gab die eigenen Farben nicht mit zurück,
sodass die eigene Welt am Server leer ankam. Das Zurücksetzen löscht das Feld
am Tiddler wieder, statt den alten Wert stehen zu lassen.

Der neue `t_farbwelt.py` prüft in achtundzwanzig Schritten das Klonen, das
Ändern einer Farbe, den dunklen Zweig, den Export und das Behalten im Browser
wie am Server (Feld gelesen und im Speicherbefehl wiedererkannt). Dazu wachsen
die bestehenden Tests mit: `t_palette.py` erwartet die neunte Welt,
`t_speicher.py` den Vertragspunkt `eigeneFarbenSetzen`, `t_leerwiki.py` sieben
statt sechs Felder in der Dateninsel. Version v0.1.19 → v0.1.20. Die Suite (1012
Prüfungen, 33 Testdateien) ist grün.

### v0.1.19 — vier Farbwelten aus TiddlyWiki — 984 Prüfungen

SimpleWiki kannte bisher vier Stimmungen (Pergament, Nord, Wacholder, Sol).
Dazu kommen vier Farbwelten, die aus den TiddlyWiki-Paletten stammen, die in
den Wikis auf diesem Server liegen: **Flexoki**, **Vanille**, **Wüste** und
**Dämmerung**. Flexoki führt beide Zweige schon mit (FlexokiLight und
FlexokiDark); Vanille, Wüste und Dämmerung bringen nur eine Seite mit — Vanilla
und DesertSand sind hell, Twilight ist dunkel —, und die fehlende Gegenseite
wurde aus dem Ton der vorhandenen Palette abgeleitet, damit jede Welt sich rund
anfühlt.

Jede Farbwelt steht in beiden Modi: `body.pal-<welt>` im hellen,
`body.dark-mode.pal-<welt>` im dunklen Erscheinungsbild. Die Variablen sind
dieselben wie bei den vorhandenen Welten (`--bg-primary` bis `--textur-inhalt`),
sodass auch die Texturen der TiddlyWiki-Oberfläche mitwandern. Die Farbcodes
sind aus den Paletten übernommen, wo es sie gab (Flexoki aus dem Rezeptbuch,
Vanilla, DesertSand und Twilight aus dem TiddlyWiki-Kern), und sonst aus dem
jeweiligen Welt-eigenen Ton gebildet — hell für Flächen, dunkler bzw. heller für
Hover und Aktiv.

Die Auswahl steht im Einstellungen-Dialog, jetzt mit acht Einträgen; die
Beschriftungen liegen in allen acht Sprachen vor (deutsch Flexoki, Vanille,
Wüste, Dämmerung; englisch Flexoki, Vanilla, Desert, Twilight). `t_palette.py`
prüft die acht Namen in der Auswahlliste und je Welt Farbe, Zweig und den
Wechsel zwischen hell und dunkel; `t_textur.py` erwartet die doppelte Zahl der
Textur-Variablen (acht Welten mal zwei Modi). Version v0.1.18 → v0.1.19. Die
Suite (984 Prüfungen, 32 Testdateien) ist grün.

### v0.1.18 — ein Bild bleibt ein Bild, auch nach leeren Absätzen — 964 Prüfungen

Im WYSIWYG-Editor schreibt Toast UI jeden leeren Absatz als eigene
`<br>`-Zeile ins Markdown. Standen mehrere solcher Zeilen zwischen zwei
Absätzen und folgte darauf ein Bild, zeigte die Seite statt des Bildes den
rohen Markdown-Text: `1. Zeile...` und darunter `2\. Zeile
![](data:image/jpeg;base64,...)`. Der Grund sitzt bei `marked`: Eine Zeile,
die nur aus einem Tag besteht (wie `<br>`), beginnt einen rohen HTML-Block,
der erst an der nächsten Leerzeile endet. Die Zeile danach gehörte damit zum
HTML und wurde nicht mehr als Markdown gelesen — das Bild blieb Text, und die
Escapes `1\.` und `2\.` blieben stehen.

Die Lösung ist eine Vorbereitung vor dem Rendern: `brAbsaetzeTrennen` setzt
hinter eine Folge allein stehender `<br>`-Zeilen eine Leerzeile, wenn Inhalt
folgt. Damit endet der HTML-Block, und der nächste Absatz wird wieder als
Markdown gelesen. Der Schritt läuft in `ersetzeWikiSyntax` auf dem Text, in
dem Codeblöcke schon ausgeblendet sind, und rührt eine `<br>`-Folge nur an,
wenn sie am Blockanfang steht — innerhalb eines eigenen HTML-Blocks bleibt
alles, wie es ist. Gespeichert wird nichts anders; die Anzeige bessert sich,
das Austauschformat bleibt unberührt.

Der Test `t_bild.py` hält beide Wege fest: die gerenderte Seite mit genau
diesem Editor-Markdown und die Runde durch den echten Editor (öffnen,
speichern, wieder lesen). Ohne die Vorbereitung schlägt er mit genau dem
geschilderten Text fehl. Version v0.1.17 → v0.1.18. Die Suite (964 Prüfungen,
32 Testdateien) ist grün.

### v0.1.17 — ein zweiter Klick klappt die Ebene wieder zu — 954 Prüfungen

Im Verzeichnis öffnete ein Klick auf eine Elternseite deren nächste Ebene,
aber ein zweiter Klick auf dieselbe Zeile tat nichts: Wer die Ebene wieder
schließen wollte, musste den Zähler oder den Pfeil links treffen. Jetzt
schaltet ein Klick auf die Zeile das Auf- und Zuklappen um. Klickt man
„1. Hauptseite" an, öffnet sie sich und zeigt ihre Unter-Seiten; klickt man
sie noch einmal an, verschwinden sie wieder. Es gilt für jede Seite, die
einen Zähler trägt — also für jede mit Kindern; ohne Kinder bleibt es beim
bloßen Öffnen.

Die Zeile bekommt dafür einen eigenen Handler `tocZeileKlick`, der zuerst
die Seite öffnet und dann, wenn die Ebene schon offen war, wieder zuklappt.
`selectPage` bleibt unverändert: Ein Verweis im Text oder ein Klick im Fluss
öffnet eine zugeklappte Elternseite weiterhin, ohne eine offene zuzumachen.
Der Pfeil und der Zähler klappen wie bisher, und `@click.stop` hält sie
davon ab, zusätzlich die Zeile auszulösen. `t_klapp.py` prüft in Teil 1 den
zweiten Klick: Nach dem Öffnen von „Haupt" und „Unter1" schließt ein erneuter
Klick auf „Haupt" beide Unterebenen, während die Seite geöffnet bleibt.
Version v0.1.16 → v0.1.17. Die Suite (954 Prüfungen, 31 Testdateien) ist grün.

---

## 2026-10-10

### v0.1.16 — Auswahl wie im Sprachmenü der Verwaltung — 952 Prüfungen

Das Locale-Menü der MWS-Verwaltung (`hero-locale-menu`) führt seine
Sprachen in einer festen Reihenfolge und beschriftet jede mit Flagge und
Namen. Die Auswahl unter den Einstellungen soll genauso aussehen, damit
niemand zwei Listen nebeneinander vergleichen muss. Deshalb steht die
Reihenfolge jetzt in `SIMPLEWIKI_LANG_REIHENFOLGE` — `en, de, ru, es,
fr, ja, ko, zh-cn`, dieselbe wie `supportedLocales` —, und `languages()`
sortiert nicht mehr selbst; die Hauptsprache steht nicht länger vorn,
Englisch beginnt. Jede Sprache trägt als `name` dieselbe Beschriftung wie
`localeLabels` der Verwaltung: `🇺🇸 American`, `🇩🇪 Deutsch`, `🇷🇺 Русский`,
`🇪🇸 Español`, `🇫🇷 Français`, `🇯🇵 日本語`, `🇰🇷 한국어`, `🇨🇳 中文`. Der Vertrag
im Kopf nennt die Codes in derselben Reihenfolge. Sprachen, die nicht in
der Reihenfolge stehen, hängen sich hinten an, statt zu verschwinden. Die
Beschriftungen kommen aus der Verwaltung, nicht aus der Wiki: der Eintrag
heißt „🇺🇸 American", wie im Server, und nicht „English". Beide Listen
zeigen damit dasselbe. Der Test `t_sprachen.py` hält Reihenfolge und
Beschriftung fest. Version v0.1.15 → v0.1.16. Die Suite (952 Prüfungen,
31 Testdateien) ist grün.

### v0.1.15 — Sprachcode wie in der Verwaltung — 953 Prüfungen

Der Code für vereinfachtes Chinesisch hieß in v0.1.14 `zh_CN`. Die
MWS-Verwaltung führt dieselbe Sprache als `zh-cn`; zwei Schreibweisen für
eine Sache sind genau die Art Stolperstein, über die man später rätselt.
Der Code heißt jetzt `zh-cn` — dieselbe Schreibweise wie im Server und
durchgehend klein wie `de`, `en`, `ru`, `es`, `fr`, `ja` und `ko`. Am
Inhalt der Übersetzung ändert das nichts, nur am gespeicherten Wert. Eine
Wiki, die noch `zh_CN` als `sprache` trägt, fällt auf Deutsch zurück; im
Austauschvertrag im Kopf von `simplewiki.html` steht die neue Liste. Der
Test `t_sprachen.py` prüft weiterhin alle acht Sprachen. Version
v0.1.14 → v0.1.15. Die Suite (953 Prüfungen, 31 Testdateien) ist grün.

### v0.1.14 — Sechs weitere Sprachen — 953 Prüfungen

SimpleWiki sprach bisher Deutsch und Englisch. Jetzt kommen Russisch,
Spanisch, Französisch, Japanisch, Koreanisch und vereinfachtes Chinesisch
dazu — als vollwertige Übersetzungen der 121 Texte. Die Auswahl unter den
Einstellungen füllt sich aus `SIMPLEWIKI_LANGS`; sie musste dafür nicht
angefasst werden. Eine Sprache hinzufügen heißt von nun an: einen Eintrag
unter `SIMPLEWIKI_LANGS` mit `name` und `translations`. Jede Sprache trägt
dieselben Schlüssel; fehlt einer, greift Deutsch als Hauptsprache. Der Code
für vereinfachtes Chinesisch heißt `zh_CN`, wie er in der Datei steht;
das ist derselbe Inhalt, den die MWS-Verwaltung als `zh-cn` führt — die
Schreibweise folgt hier dem Sprachcode, nicht der Verwaltung. Der
Austauschvertrag im Kopf von `simplewiki.html` nennt jetzt die ganze
Codeliste statt nur `"de"` und `"en"`; der Feldname `sprache` und das
Format selbst bleiben unverändert, der Server sieht nur weitere erlaubte
Werte. Neuer Test `t_sprachen.py` (20 Prüfungen): alle acht Sprachen
stehen im Dropdown, jede nennt sich selbst, jede übersetzt die Kopfzeile
des Einstellungen-Panels, und jede wird als `simplewiki_lang` gemerkt.
Version v0.1.13 → v0.1.14. Die Suite (953 Prüfungen, 31 Testdateien) ist
grün.

### v0.1.13 — Die Suche findet auch Schlagworte — 933 Prüfungen

Die Suche im Kopf fand bisher Titel und Inhalt; ein Schlagwort musste man
kennen und anklicken, statt es finden zu können. Jetzt durchsucht sie
`filteredPages` auch die Schlagworte einer Seite — dieselbe Stelle im
Programm, dieselbe Trefferliste, keine neue Bedienung: wer zu einem
Schlagwort sucht, sieht die Seiten, die es tragen, ihr Titel folgt
trotzdem nur dem Titel. Ein Schlagwort ist ein Wort an der Seite, kein
Unterscheidungszeichen, und es gehört deshalb zur Suche. Fremde Dateien
können `tags` ganz weglassen; die Suche prüft deshalb zuerst, ob das Feld
überhaupt ein Array ist, und wertet es sonst nicht aus. Version
v0.1.12 → v0.1.13. In `t_suite.py` trägt die Seite «Leer» jetzt das
Schlagwort «markiert» — Titel und Inhalt sagen es nirgends, und vier neue
Proben stellen fest, dass die Suche «markiert» genau diese Seite liefert.
Die Suite (933 Prüfungen, 30 Testdateien) ist grün.

### v0.1.12 — Der Fingerabdruck der Datei — 929 Prüfungen

Doppelgeklickte Dateien sind alle derselben Herkunft: `file://` teilt sich
einen Browserspeicher. Bisher gewann immer, was im Browser lag — und so
zeigte eine frisch geladene Datei ewig den Stand einer anderen, bis man den
Speicher leerte. Jetzt stellt die App beim Öffnen den Fingerabdruck ihres
Datenblocks fest (FNV-1a über den Text und seine Länge) und merkt ihn sich
als `simplewiki_digest` im Browserspeicher. Öffnet man dieselbe Datei noch
einmal, gleicht der Fingerabdruck dem gemerkten: der Stand im Browser
gewinnt weiter, eigene Änderungen bleiben, nichts verdoppelt sich. Liegt
aber eine andere Datei vor — auch eine neuere Fassung derselben — laufen
die Fingerabdrücke auseinander, und der Inhalt der Datei ersetzt den
sonstigen Browserstand, ohne dass jemand erst den Speicher leeren muss.
Einen Fingerabdruck gibt es nur, wo der Datenblock Seiten trägt; ein leerer
Datenblock und eine leere Seite lassen alles beim Alten. Im MWS-Betrieb
ändern sich die Regeln nicht: dort entscheidet weiterhin der Server.
Version v0.1.11 → v0.1.12. Neuer Test `t_finger.py`: er öffnet zwei
verschiedene Dateien abwechselnd viermal in ein und demselben Chromium-
profil und stellt fest, dass die andere Datei gewinnt und die gleiche den
Stand behält — 18 Prüfungen. Die Suite (929 Prüfungen, 30 Testdateien) ist
grün; die drei Stellen, an denen ein Test Browserstand vor einem Datenblock
erwartet (`t_abnahme`, `t_mwsdatei`, `t_mwsmode`), merken sich die offene
Datei über `mkcopy.digest_seed()` selbst als dieselbe Datei.

## 2026-10-09

### v0.1.11 — Der Schlagwort-Filter im Fluss-Kopf — 911 Prüfungen

Der Fluss ließ sich bisher nur über das Register filtern. Jetzt steht im
Fluss-Kopf, links neben «Drucken», eine Auswahlliste aller vergebenen
Schlagworte: ein Schlagwort darin zeigt nur dessen Seiten, «Alle
Schlagworte» wieder die ganze Wiki. Sie ersetzt das Etikett mit dem × aus
v0.1.10 — dieselbe Sache, nur an einer Stelle statt an zweien: die
Auswahlliste tut beides, wählen und den Zustand anzeigen. Kommt man über
«Alle im Fluss» aus dem Register, steht die Liste schon auf dem richtigen
Schlagwort. Beim Drucken fällt der ganze Fluss-Kopf weg, der Filter also
mit ihm — auf dem Papier steht nur, was er ausgewählt hat. Version
v0.1.10 → v0.1.11. Geprüft in `t_tags.py` (fünfter Lauf jetzt 16 Proben,
55 insgesamt) und über die volle Suite (911 Prüfungen); `t_fluss.py`
bestätigt, dass neben «Drucken» weiter nur dieser eine Knopf steht.

### v0.1.10 — Vom Schlagwort in den Fluss — 909 Prüfungen

Im Register eines Schlagworts stand bisher nur die Liste der Seiten. Wer
sie alle lesen wollte, klickte eine nach der anderen an. Jetzt steht dort
der Knopf «Alle im Fluss»: er schließt das Register und öffnet den Fluss,
die Lesesicht mit allen Seiten hintereinander — aber nur mit denen, die
das Schlagwort tragen. Im Fluss-Kopf steht das Schlagwort als Etikett mit
einem ×; ein Klick darauf löst den Filter und zeigt wieder die ganze
Wiki, ohne den Fluss zu verlassen. Die Zahl daneben nennt Schlagwort und
Menge. Der Fluss-Knopf im Kopf zeigt weiterhin immer die ganze Wiki und
räumt einen stehengebliebenen Filter weg; die Suche wird beim Sprung vom
Schlagwort fallen gelassen, sonst blendete sie Seiten aus, die
dazugehören. Nichts davon ist ein zweiter Fluss: es ist derselbe, nur
gefiltert, mit Drucken und Scrollen wie gehabt. Version v0.1.9 → v0.1.10.
Neu prüfen es 15 Proben im fünften Lauf von `t_tags.py` (53 Proben
insgesamt); die gefilterte Zahl und das Weglassen der Fußzeile inklusive.
Geprüft über die volle Suite (909 Prüfungen) und in MWS
(`provision-simplewiki`).

### v0.1.9 — Schlagworte werden sichtbar und anklickbar — 894 Prüfungen

TiddlyWiki kennt Schlagworte, SimpleWiki trug sie bisher nur im Feld
`page.tags` spazieren — zu sehen war nichts. Jetzt steht unter jedem
Seitentitel eine Zeile mit Schlagwort-Pillen. Ein Klick auf eine Pille
öffnet das Register: ein Fenster, das alle Seiten mit diesem Schlagwort
auflistet, mit der Zahl davor, und der Klick auf einen Eintrag führt
direkt dorthin. Im Bearbeiten ist dieselbe Zeile ein Feld: Vorhandene
Schlagworte stehen als Pille mit einem × zum Entfernen da, ein neues
entsteht durch Tippen und Enter — mehrere auf einmal gehen, durch Komma
getrennt. Ein Klick ins Feld listet die Schlagworte auf, die im Wiki schon
vergeben sind und dieser Seite noch fehlen; Tippen schränkt die Liste ein,
ein Klick oder Pfeil und Enter nimmt eines davon, danach bleibt die Liste
offen für weitere. Gesichert landen sie in `page.tags` und gehen damit
unverändert durch den Austausch mit MWS; am Verweisgraphen ändert das
nichts, Schlagworte sind Etiketten, keine Verweise. Ein Schlagwort mit
eckigen Klammern wird abgelehnt und der Grund gesagt, statt es still zu
verlieren: die Klammern sind das Listenformat selbst. Neu prüfen es 38
Proben in `t_tags.py` (Ansicht, Register, Bearbeiten, Vorschlagsliste,
Ablehnung, englische Oberfläche). Version v0.1.8 → v0.1.9. Geprüft über
die volle Suite (894 Prüfungen) und in MWS (`provision-simplewiki`).

### v0.1.8 — «+» und wieder Abbrechen — 856 Prüfungen

Der Knopf «+ Neue Seite» legt sofort eine Seite an — auch dann, wenn man
es sich dann anders überlegt und «Abbrechen» klickt. Die leere Seite blieb
stehen und musste extra gelöscht werden. Jetzt lebt jede eben angelegte
Seite erst auf Widerruf: Wer «Abbrechen» klickt, bekommt sie ersatzlos
zurückgenommen — aus der Liste, aus dem Speicher und vom Server —, und
der Blick kehrt zu der Seite zurück, auf der man vorher war. Dasselbe
gilt, wenn man die neue Seite verlässt, ohne zu sichern, etwa durch das
Anklicken einer anderen Zeile. Erst «Sichern» macht die Seite dauerhaft;
wer sie danach bearbeitet und abbricht, behält sie. Dazu ist das Löschen
in eine gemeinsame Methode `seiteEntfernen` gewandert, die die
Löschbestätigung und die Rücknahme benutzen, mit demselben
Kinder-Rücken-Eine-Ebene-Hoch und demselben Server-Löschen. Neu
prüfen es zehn Proben in `t_abbrechen.py`: Abbrechen nimmt zurück,
Wegklicken nimmt zurück, Sichern macht dauerhaft. Version v0.1.7 →
v0.1.8. Geprüft über die volle Suite (856 Prüfungen) und in MWS
(`provision-simplewiki`).

### v0.1.7 — von Anfang an zugeklappt — 839 Prüfungen

Das Verzeichnis kam aufgeklappt und merkte sich pro Browser, was
zuklappt war. Jetzt ist es andersherum: Beim Neuladen steht nur die
oberste Ebene, jede Elternseite ist zugeklappt, und der Unterbaum öffnet
sich erst am Zähler, mit Pfeil rechts oder durch Anklicken der
Elternseite. Das Aufgeklappte ist dann nur eine Anzeige-Sache dieser
Sitzung — gemerkt wird nichts mehr, auch nichts in localStorage (der
alte Schlüssel `simplewiki_zugeklappt` ist ersatzlos aus der Datei
gefallen). Eine jede Ebene klappt für sich: Wer die oberste öffnet,
sieht deren Kinder und findet dort wieder Zähler für deren eigene
Unterbäume. Die Suche hebt jede Deckung auf: Treffer bleiben sichtbar,
egal in welcher Tiefe sie stehen. Version v0.1.6 → v0.1.7. Geprüft über
die volle Suite (839 Prüfungen, neu daran sind drei zum
Standard-zugeklappt und zum Abschieben der Deckung durch die Suche in
`t_klapp.py`) und in MWS (`provision-simplewiki`).

### v0.1.6 — der Titel ist im Bearbeiten ein Feld — 836 Prüfungen

Das Titelfeld im Bearbeiten war ein solches ohne Rahmen: Es sah aus wie
die eingegossene Überschrift der Ansicht und sagte nicht, dass hier
etwas zu ändern ist. Jetzt ist es als Eingabefeld erkennbar — mit Rahmen
und Rundung wie die Suche, einem Stift ✏️ davor und einem Ring, wenn der
Fokus im Feld steht. Nichts daran ist neue Technik, nur das Aussehen;
die Farben nehmen die Farbwelt mit, hell wie dunkel. Version v0.1.5 →
v0.1.6. Geprüft über die volle Suite (836 Prüfungen, die Umbenenn- und
Bearbeiten-Proben in `t_anmeldung.py`, `t_abnahme.py`, `t_mwsmode.py`,
`t_hierarchie.py` laufen unverändert) und in MWS (`provision-simplewiki`).

### v0.1.5 — der Unterbaum verschwindet hinter einem Zähler — 836 Prüfungen

Eine Elternseite im Inhaltsverzeichnis kann jetzt ihre Unter-Seiten
verbergen: wer viele Seiten hat, sieht auf einen Blick die oberste Ebene
und klappt den Unterbaum auf, wenn er hinein will. Der Zähler ▼ steht
nur an Zeilen mit Kindern; zuklappen geht am Zähler oder mit Pfeil links,
aufklappen am Zähler, mit Pfeil rechts oder einfach durch Anklicken der
Seite. Der zugeklappte Unterbaum bleibt beim Ziehen ein Block: Er zieht
als Ganzes mit, und „dahinter“ heißt weiterhin hinter dem ganzen
Unterbaum.

Das ist ein Anzeige-Ding des Browsers und kein Feld der Seite: Es steht
in keinem Austauschformat (die Version bleibt 1), gemerkt wird es nur im
lokalen Speicher unter `simplewiki_zugeklappt`, und nur das Zuklappen.
Beim Suchen gilt die Deckung nicht — ein Treffer muss sichtbar sein,
auch wenn seine Elternseite zugeklappt ist. Version v0.1.4 → v0.1.5.
Geprüft über die volle Suite (836 Prüfungen, davon 27 im neuen Prüfblatt
`t_klapp.py`) und in MWS (`provision-simplewiki`).

### v0.1.4 — eine neue Seite kommt unten ins Verzeichnis — 809 Prüfungen

Eine neue Seite landete bisher oben im Inhaltsverzeichnis: Sie wurde vorn
angehängt und drängte die Startseite und alles andere nach unten — mit
jeder Seite wuchs die Liste nach oben. Jetzt kommt sie unten an, egal ob
sie über den Knopf „+ Neue Seite“, über einen Verweis auf eine noch
fehlende Seite oder über den Verlinken-Dialog entsteht. Die Reihenfolge
bleibt die übliche: Sie steht in der Datei und hält einem Neuladen und dem
Austausch stand. Version v0.1.3 → v0.1.4. Geprüft über die volle Suite
(809 Prüfungen, zwei Prüfblätter erwarten jetzt die neue Seite hinten).

### v0.1.3 — eine Seite kann unter einer anderen stehen — 808 Prüfungen

Das Inhaltsverzeichnis war eine flache Liste: Reihenfolge ja, Gliederung
nein. Jetzt kann eine Seite eine Elternseite haben, beliebig tief. Gesagt
wird es über das bekannte Feld `eltern`, das den Titel der Elternseite
nennt — an derselben Stelle, an der Verweise den Titel nennen, zieht es
beim Umbenennen mit. Die Datei bleibt eine flache Liste in
Tiefensuche-Reihenfolge: Die Elternseite steht direkt vor ihrem Unterbaum,
und der Unterbaum zieht immer mit — beim Ziehen, beim Ein- und Ausrücken,
beim Versetzen, beim Löschen.

Ziehen hat jetzt drei Zonen je Zeile: oben legt davor, unten dahinter —
hinter meint hier hinter dem ganzen Unterbaum, nicht hinter der einen Zeile —
und die Mitte macht die Zeile zur Elternseite. Beim Tastaturweg tut dieselbe
Dreiteilung: Alt + ↑/↓ tauscht nur mit Nachbarn auf derselben Ebene, Alt + → rückt
unter die Zeile davor ein, Alt + ← rückt eine Ebene aus. Wer sucht, lässt
nichts verschieben.

Eine Kopie erbt die Elternseite und steht direkt hinter dem Unterbaum der
Vorlage statt vorn in der Liste; das Löschen einer Seite mit Kindern stuft
die Kinder eine Ebene hoch und sagt es vor dem Bestätigen („die Unter-Seite
rückt eine Ebene hoch“, Deutsch und Englisch). Das Austauschformat bleibt
Version 1: ein bekanntes Feld kommt hinzu, nichts ändert sich, fremde Felder
bleiben erhalten. Version v0.1.2 → v0.1.3. Geprüft über die volle Suite
(808 Prüfungen, davon 56 in drei neuen Prüfblättern zur Verschachtelung)
und in MWS (`provision-simplewiki`).

### v0.1.2 — der Update-Hinweis wohnt im Einstellungen-Dialog — 751 Prüfungen

Der Hinweis auf die neue Oberfläche war ein Geschwister von `#app`: ein
eigenes Skript hängte ihn von außen in die Seite — mit eigener Sprache,
eigenem Stil, eigenem Zug auf die Konfig-Tiddler. Die alte Begründung, ein
Kind würde Vue bei der nächsten Aktualisierung selbst wieder entfernen,
war richtig für eine schwebende Meldung — aber der Hinweis hat jetzt ein
Zuhause, das die App selbst baut: Ein Punkt am Zahnrad (⚙️) kündigt eine
bereitliegende Version an, und im Einstellungen-Dialog steht die Meldung
mit dem Knopf „Übernehmen“. Als Kind der App spricht der Hinweis dieselbe
Sprache wie sie (auch nach dem Umschalten), zeichnet mit denselben
Variablen und verschwindet mit `v-if="shellUpdate"` spurlos — die zwei
Gerüste oben und unten sind keins mehr.

Aufgeben heißt jetzt etwas anderes als vorher: Der Hinweis merkt sich die
**angebotene** Version, nicht die gelieferte. „Beim nächsten Update
erinnern“ legt einen Schlüssel für die angebotene Nummer — ein neues
Angebot bekommt einen neuen Schlüssel und meldet sich wieder; „In einem
Monat erinnern“ legt einen Stichtag, nach dem derselbe Hinweis zurückkehrt.
Und der Knopf „Übernehmen“ sagt vor dem Klick, was keiner vorher nachlesen
musste: Die Inhalte des Wikis werden bei dem Update nicht verändert
(als Tipp am Knopf, in Deutsch und Englisch).

Version v0.1.1 → v0.1.2. Geprüft über die volle Suite (751 Prüfungen) und
in MWS (`provision-simplewiki`, Update-Hinweis im Dialog vor und nach dem
Übernehmen).

### v0.1.1 — der Willkommensgruß ist persönlich — 751 Prüfungen

Die erste Wiki begrüßte allgemein — die App wusste es doch besser. Die
Begrüßung redet die Leserin jetzt an, wo immer einer frischen, leeren Wiki
etwas entgegensteht: „Willkommen in Deinem SimpleWiki! 🎉“ (englisch
„Welcome to your SimpleWiki! 🎉“). Version v0.1.0 → v0.1.1. Geprüft über
die volle Suite (751 Prüfungen).

## 2026-10-08

### v0.1.0 — die Oberfläche nennt ihre Version — 751 Prüfungen

Bisher erzählten die zählenden Versionsnummern (Release 6, 10 …), *wie oft*
die Schale gespeichert wurde, nicht, *was* sie ist. Jetzt trägt die Datei
eine menschenlesbare Version über denselben Weg, den MWS dafür vorsieht:

    <meta name="mws-shell-version" content="v0.1.0">

`provision-simplewiki` liest den Wert beim Provisionieren aus dem HTML
(`extractShellLabel`) und trägt ihn als Label der neuen Version ein; die
MWS-Verwaltung zeigt ihn in den Schalen-Feldern der Wiki, und der
Update-Hinweis nennt ihn statt der Nummer: „Diese Wiki läuft auf v0.1.0. Zum
Übernehmen bereit steht v0.1.1.“ Wer die Bezeichnung weglässt, bekommt die
Nummer — nichts Neues geht kaputt.

Der Hinweis selbst blieb unverändert: Er vergleicht weiterhin die
Release-Nummern, die der Server liefert, und fällt nur bei der *Anzeige* auf
die Bezeichnung um, wenn sie vorhanden ist (`shell-release-label` bzw.
`-latest`). Geprüft über die volle Suite (751 Prüfungen) und in MWS
(`provision-simplewiki`, Update-Hinweis vor und nach dem Übernehmen).

### Die Wiki nimmt eine neue Oberfläche — der Update-Hinweis — 751 Prüfungen

MWS meldet einer Wiki, auf welcher Template-Version ihre Oberfläche steht und
ob eine neuere bereitliegt — ein Separatum, das Schale und Inhalt getrennt
hält. Bisher konnte die Schale diese Nachricht nirgends zeigen, weil eine
statische Datei von nichts weiß. Jetzt fragt sie: Bei der Politik **notify**
mit bereitliegender neuerer Version erscheint über der Wiki ein Hinweis mit
einem Knopf **„Übernehmen“**, der `PUT /recipe/<name>/shell/update` aufruft
(eine eigene Route in `RecipeRoutes.ts`, nur für Besitzerin und
Administratoren — dieselbe Tür wie hinter den Wiki-Einstellungen). Der Server
verschiebt den Pin auf die neueste Version, kompiliert die Wiki neu, und die
Wiki lädt sich selbst neu.

Wer den Hinweis sieht, ist bewusst eng gehalten: **die Besitzerin und die
Administratoren**, und sonst niemand. Schreibrecht genügt nicht. Eine
Oberfläche übernehmen ist eine Eigentumsentscheidung, und wer nur mitschreibt,
soll sich nicht plötzlich in einem anderen Haus wiederfinden. Die App
entscheidet das mit den beiden Stücken, die sie ohnehin hat: die Besitzerin
steht im Tiddler `$:/config/multiwikiclient/owner`, wer heute angemeldet ist,
sagt `/status` mit `isAdmin` und `username`.

Gelesen wird alles, ohne neue Verantwortung einzuführen: die Politik und die
Versionsnummern räumt dieser Hinweis aus **denselben Konfig-Tiddlern** ab, in
denen die App sie bereits findet (`shell-policy`, `shell-release`,
`shell-latest-release` samt Labels; der Server schreibt sie in
`RecipeIndexSender`). Nur die Identität wird nachgefragt — ein Status-Aufruf
pro Seite, und nur, wenn die Konfiguration überhaupt einen Hinweis in
Betracht zieht. Ein Wiki ohne Versionsbetrachtung bleibt ohne jede weitere
Frage, und damit bleiben auch alle bestehenden Prüfungen unberührt.

Der Hinweis ist ein **Geschwister der App**, kein Kind von `#app`: Vue kennt
nur die Kinder, die es selbst gerendert hat, und hätte ein später
eingehängtes Kind bei der nächsten Aktualisierung wieder entfernt. Ein
Geschwister überlappt sich mit nichts. Gefüllt wird er über `textContent`
(nichts Fremdes wird je als Markup ausgegeben), er bezieht
seine Farben aus denselben Variablen wie die App und spricht beide Sprachen
über das `lang`-Attribut, das die App beim Sprachwechsel selbst setzt.

**Weggedrückt** wird der Hinweis je **Version**: Der Schlüssel
(`simplewiki_update_<gelieferte Version>`) trägt die Version, die gerade
läuft — beim nächsten Release ist es ein neuer Schlüssel, und erst nach dem
Übernehmen ist der Hinweis für die neue Version wirklich weg. Der Knopf
„Übernehmen“ ist während des Aufrufs deaktiviert; schlägt der Aufruf fehl,
steht der Fehler im Hinweis und der Knopf wird wieder frei. In den
Konfig-Tiddlern fehlt aktuell das Feld „gibt es ein Update überhaupt“ — die
Schale vergleicht Version gegen Version. Das ist ein reines Rechnen mit den
Zahlen, die der Server selbst schreibt, also keine dritte Quelle.

Da die Suite nur mit einem echten Browser läuft, ist der Hinweis nicht Teil
der vorhandenen Prüfungen, und eine Frage für später, weil sie dem MWS gehört
(mündliche Verabredung, nicht dieser Code): `tests/mwsserver.py` ist eine
Testfigur des Vertrags im Kopf. Soll sie mitlernen, dass `/status` unter
`shell` Auskunft gibt und `PUT /shell/update` den Pin bewegt, damit der
Hinweis gegen die Testfigur belegt wird — wie der Serverhinweis in
`t_mwsmode.py` Teil 11? Und wie sollte der Knopf benannt sein, wenn er in
anderen Sprachen als Deutsch und Englisch gebraucht wird?

## 2026-10-07

### Der Serverhinweis lässt sich für die Session wegklicken — 751 Prüfungen

Wer die Wiki vom MWS bekam, sah dauerhaft die Zeile „☁ Die Seiten liegen auf
dem Server…“. Sie wiederholte, was ohnehin jeder Blick auf die Adresszeile
sagt. Jetzt hat sie ein **×** oben rechts: Ein Klick blendet sie weich aus,
und für den Rest der Session bleibt sie weg. Wer die Wiki neu öffnet, sieht
sie wieder.

Gemerkt wird das in **`sessionStorage`**, nicht in `localStorage`: Eine neue
Session ist ein neuer Besuch, und der Hinweis soll jede Sitzung begrüßen,
nicht eine dauerhafte persönliche Einstellung überschreiben.

Getrennt ist das **Ausblenden** vom **Verschwinden**: Die Klasse
`mws-hinweis-blendet` fährt die CSS-Transition (0,3 s, leichte Bewegung nach
oben), und erst ein Timer von 350 ms entfernt danach das Element. Wenn der
Timer entscheidet und nicht das `transitionend`, hängt nichts an der
Animationsuhr des Browsers — die läuft unter Virtual-Time-Budget nicht mit
den Timern des Testskripts mit (siehe `tests/README.md`). Der erste Entwurf
war ein Vue-`<transition>` und fiel genau dort durch: in der Suite war das
Element nach dem Klick noch da.

Geprüft wird das in `tests/t_mwsmode.py` Teil 11: Das X ist da, nach dem
Klick ist der Hinweis weg, und `sessionStorage` merkt es sich.

### Die Farbwelten — 748 Prüfungen

Bisher hatte ein Wiki eine Farbe, und die war Hell/Dunkel. Wer eine
andere Farbstimmung wollte, konnte nur dunkler werden. Das hielt
zwei Dinge in einer Zeile, die nichts miteinander zu tun haben: die
**Farbwelt** (die Stimmung) und die **Helligkeit** darin. Der
Mond/Sonne-Knopf im Kopf bleibt die Helligkeit; die Welt wird im
Einstellungen-Dialog gewählt.

Es gibt vier Welten: **Pergament, Nord, Wacholder, Sol**. Pergament
ist die Basis: fehlt jede Angabe, gilt es, und eine Wiki, die nie
eine Palette gesetzt hat, sieht genau so aus wie vorher. Die drei
weiteren kommen als Klasse am `body` (`pal-nord`, `pal-wacholder`,
`pal-sol`), und jede hat einen hellen und einen dunklen Zweig. Die
Textur (das Punktraster) ist je Welt neu gesetzt — die hellen Werte
von Pergament gehören nicht in eine andere Welt hinein, denn eine
CSS-Variable löst ihre Verweise an der Stelle auf, wo sie deklariert
wird (siehe der Fallstrick in `t_textur.py`).

Der Austausch ist mitgedeckt: Das Feld **`palette`** reist auf dem
Startseiten-Tiddler wie `sprache` und `thema`, und es steht in der
gesicherten Datei. `thema` sagt weiterhin nur Hell/Dunkel — wer nur
heller oder dunkler schaltet, fasst die Palette nicht an. Gültige
Werte sind die vier Welten oben; alles andere zählt wie ein leeres
Feld.

Geprüft wird das mit `tests/t_palette.py`: Auswahl und Namen im
Dialog, die Klasse am `body`, die gezeichnete Tinte je Welt und je
Modus, der Wechsel am Server und sein Weg auf den Tiddler, und die
Farbwelt im Export. Der Kopien-Bauer der Tests (`mkcopy`) setzt den
localStorage-Schlüssel `simplewiki_palette` in jeder Kopie mit
zurück, damit ein Lauf nicht in den nächsten leuchtet.

Der Vertrag ist betroffen (neues Feld im Austausch, neuer
Speicherschlüssel), deshalb wurde vorher rückgefragt. Entscheidungen:
Die Palette sitzt auf dem Startseiten-Tiddler wie `sprache` und
`thema`; die Auswahl steht im Einstellungen-Dialog neben der Sprache;
alle vier Welten werden gebaut. Die Farben der drei neuen Welten
nehmen ihre Idee aus dem TW-Sortiment, sind aber nicht abgeschrieben
(Nord-Frost, Flexoki-Oliv, Solarized-Blau).

---

## 2026-10-05

### Der Ladevorgang im Test kam manchmal gar nicht an — 721 Prüfungen

Der Gesamtlauf meldete einmal **710 statt 721**, und der Verursacher war
nicht die Textur: `t_file.py` prüfte an einem der drei Läufe, ob nach dem
Wieder-Einlesen ein Hinweis mit der Seitenzahl erschienen ist. Dieser Lauf
scheiterte.

Die Meldung war bis dahin `Hinweis nennt die Seitenzahl: KEINER` und sonst
nichts. Das ist die schlechteste Form einer Fehlermeldung: Sie sagt nicht,
ob **nichts kam** oder ob **etwas kam und nicht aufgefangen wurde** —
beides sieht gleich aus, und die beiden Fälle haben nichts miteinander zu
tun. In der Meldung steht jetzt, wie viele Runden liefen, ob es das
Dateifeld gab und was in dem Augenblick am Schirm war:

```
FAIL Hinweis nennt die Seitenzahl: KEINER [Runden 91, Dateifeld da, jetzt am Schirm: nichts]
```

Das ist die Antwort: **neunzig Runden, Dateifeld vorhanden, nichts
erschienen.** Der Vorgang lief also überhaupt nicht an.

**Und warum?** Der Test hatte das Dateifeld **einmal** geholt, zu Beginn.
Vue baut den Einstellungsbereich bei Bedarf neu auf; danach hängt der
Befehl an einem Element, das niemand mehr liest. Am Element sieht man das
nicht — es ist ein `<input type="file">` wie jedes andere, es hat sogar
die Datei bekommen, und `dispatchEvent` meldet keinen Fehler. Der Befehl
geht ins Leere und das Ergebnis ist ein Bildschirm, auf dem sich nichts
bewegt.

Meine erste Antwort darauf war falsch und das ist der Teil, der
dokumentiert gehört: Ich habe das `change`-Ereignis **wiederholt** —
an dasselbe Feld. Damit ist garantiert wieder nichts passiert. Ich habe die
Zeichenkette mit den richtigen Buchstaben und dem falschen Gedanken
geschrieben. Gemessen habe ich es erst, als die Wiederholung **nicht**
geholfen hat: gleiches Bild, neunzig Runden, nichts am Schirm. Der Test
liest das Element jetzt **bei jedem Versuch neu**.

Ausserdem: die Notiz der Wiederholung in `tests/_hilfe.py` stand auch dann
da, wenn der zweite Lauf **genauso gescheitert** war — sie sagte
„beim ersten Lauf unter Last gescheitert" und meinte das Gegenteil von dem,
was zwei Zeilen darunter stand. Sie erscheint jetzt nur noch, wenn der
zweite Lauf wirklich grün war.

Und eine Frage für später, weil sie nicht meine ist: die beiden Prüfungen
daneben — *Reihenfolge nach dem Laden* und *und gleich gespeichert* — können
**heute nicht fehlschlagen**. Die Startkopie enthält genau dieselben drei
Seiten in derselben Reihenfolge, die hinterher geprüft werden. Der Weg
hin und zurück ist also an diesen zwei Stellen nicht belegt; belegt ist er
erst durch den Hinweis und durch `t_export.py`. Soll die zurückgeladene
Datei **etwas anderes** enthalten als die gespeicherte, damit der
Rundweg nachweisen kann, dass wirklich geladen und nicht nur nichts
schiefgegangen ist?

### Die Textur war im dunklen Modus unsichtbar — 721 Prüfungen

Der Nutzer hat gemerkt, dass ein Ändern von `--textur-inhalt` unter
`body.dark-mode` **nichts bewirkt**, und nachgesehen. Gemessen:

```
hell    --textur-bild am html  = radial-gradient(rgba( 61, 47, 31, 0.05)
dunkel  --textur-inhalt am body = rgba(245,240,225, 0.05)     <- richtig
dunkel  --textur-bild am html  = radial-gradient(rgba( 61, 47, 31, 0.05)  <- trotzdem die Tinte
```

Die Textur wurde im Dunklen mit **dunkler Tinte auf dunklem Grund**
gezeichnet. Sie war nicht kaputt, sie war unsichtbar — und eine Änderung am
Wert tat nichts, weil der Wert gar nicht dort ankam.

**Die Ursache ist eine CSS-Eigenheit, die man nicht sieht.** Eine Custom
Property löst ihre `var()`-Verweise **dort auf, wo sie deklariert ist**, und
gibt das Ergebnis als fertigen String weiter. `--textur-bild` stand am `:root`
und trug deshalb den **hellen** Wert in den dunklen Modus hinein. Der Kopf
hat es richtig gemacht — er schreibt `var(--textur-kopf)` direkt in seine
Regel — deshalb war die Schraffur im Dunklen sichtbar und das Punktraster
nicht.

Der Muster-Umweg ist raus. Das Muster steht jetzt an seinen beiden Benutzern,
die **Farbe** davor. Was sich je Modus ändert, ist damit an genau zwei
Stellen: hell und dunkel. Der Kommentar am Raster erklärt, warum.

Das war die dritte Falle in diesem Durchgang, und wieder eine, die man nur am
Bild sieht. `tests/t_textur.py` prüft jetzt, was der Nutzer geprüft hat:
**der Wert, der an `body` steht, muss in der fertigen Farbe wiederzuerkennen
sein** — in beiden Modi, bei Text und Verzeichnis, und die Deckkraft
einzeln, weil er an *der* gedreht hat. Am zurückgebauten Fehler
nachgewiesen: die Prüfung meldet genau das, was im Bild zu sehen war.

Und noch eine Sache, die der Test **nicht** behauptet: die Deckkraft der
Schraffur. Bei einem wiederholten Verlauf liest der Browser einen
gemittelten Wert zurück (0.045 ergibt 0.043) — das ist eine Eigenschaft der
Anzeige, nicht der Absicht, und man kann sie nicht sinnvoll vergleichen. Die
Farbkanäle werden verglichen, die Deckkraft nur beim Punktraster, wo der
Fleck ein echter Stopp ist.

**708 → 721 Prüfungen**, 24 Testdateien.

### Tiefe: Schatten unter dem Kopf, Schraffur im Kopf und Punktraster im Text — 708 Prüfungen

Drei Dinge, die die Oberfläche von „flach" zu „mit Tiefe" holen. Alle drei
sind eine einzige Sache: Licht von oben.

- **Der Kopf bekommt einen Schatten** (`0 3px 10px`). Er liegt über dem Text
  und soll sich auch so fühlen, statt eine Linie über einer Fläche zu sein.
  Der Schatten hängt am Kopf, nicht am Inhalt — er wandert mit.
- **Der Kopf bekommt eine Schraffur**: feine Linien im 45-Grad-Winkel, alle
  7 Pixel.
- **Der Textbereich und das Verzeichnis bekommen dasselbe Punktraster**, alle
  14 Pixel.

Warum ausgerechnet Punkte hinter dem Text und keine Linien: schräge Linien
hinter laufendem Text flimmern, Punkte nicht. Der Kopf hat keine langen
Zeilen und darf darum schraffiert sein.

**Das Punktraster stand zuerst bei 0.028 und war zu schwach** — der Nutzer hat
es „fast nicht gesehen" und auf **0.05** gesetzt, also so stark wie die
Schraffur. Das war nicht gerechnet, sondern angesehen; die Zahl im Kommentar
sagte vorher „noch feiner" und war damit ebenfalls falsch.

Das Muster selbst steht jetzt an **einer** Stelle (`--textur-bild`) und wird von
beiden Benutzern geholt. Sonst läuft hier eine Zahl und dort eine andere, und
wer die eine ändert, merkt von der anderen nichts.

**Was nicht stimmt, ist hier benannt:** die Punktreihen treffen sich über die
Kante zwischen Verzeichnis und Text, die Spalten nicht — der Text beginnt um
die Breite des Verzeichnisses seitlich, und die ist kein Vielfaches der
Rasterweite. Bei dieser Stärke sieht man es nicht.

Im Dunklen wird dasselbe Muster mit **Licht** gezeichnet statt mit Tinte: ein
heller Strich auf hellem Grund wäre im Hellen ein dunkler.

Und auf Papier kommt nichts davon: `t_fluss.py` prüft jetzt, dass die Druckregel
Textur und Schatten abschaltet. Aus einem Punktraster werden im Druck vier
Graustufen, und den Schmutzfleck hat niemand bestellt.

**Und dabei ist ein Test zweimal rotgelaufen, der nichts mit der Textur zu
tun hatte.** `t_file.py` wartete nach dem Einlesen auf *irgendeinen* Hinweis —
und der erste kam vom Sichern zwei Schritte vorher und nennt keine
Seitenzahl. Der Test las einen Hinweis, den er nie geprüft hatte, und meldete
zu Unrecht rot. Er wartet jetzt auf **den** Hinweis, den er behauptet: auf
*irgendeine* Änderung zu warten ist nicht dasselbe wie auf das Gesuchte.

**705 → 708 Prüfungen**, 23 Testdateien.

### Der Fuß des Verzeichnisses ist weg — 705 Prüfungen

Der Hinweis auf die Reihenfolge stand als Zeile unter der Liste, mit einer
Trennlinie darüber. Er steht jetzt **am Griff**, wo er hingehört: `⠿ tragen,
Alt + ↑/↓, oder mit einem Klick ansehen` — man braucht ihn nur, wenn man
anfasst, und dann ist er genau dort. Bei einer laufenden Suche nennt der
Tooltip den anderen Weg.

Damit ist `.toc-footer` ganz weg, mit ihm seine CSS-Regeln und sein Eintrag
in der Druckliste. `.toc-hint` ebenfalls — es gab nichts mehr, wofür es
galt.

**Und ein Fehler von mir, den der Nutzer im Bildschirm gefunden hat.** Beim
Einfügen der Suchfeld-Liste hatte ich **zwei Kommentar-Anfänge und ein
Ende** geschrieben. Der mittlere Absatz stand als **Text in der Kopfzeile** —
zwischen Titel und Suchfeld, in jedem Fenster. Kein Test hat es gesehen: die
Knöpfe waren alle da, die Reihenfolge stimmte, nur der Raum dazwischen war
voller Text.

Deshalb prüft `t_kopf.py` jetzt den **ganzen Text** des Kopfs gegen das, was
auf seinen Knöpfen steht. Ein Kommentar, der zu früh oder zu spät
geschlossen wird, fällt damit auf — und nicht erst beim Ansehen. Am
kaputten Stand nachgewiesen: die Prüfung meldet genau das, was der Nutzer
gesehen hat.

**704 → 705 Prüfungen**, 23 Testdateien.

### Das rechte Verzeichnis ist weg, die Suche steht unter dem Feld — 703 Prüfungen

Das Panel rechts und der Knopf ☰ im Kopf sind entfernt. Was bleibt, ist
**ein** Inhaltsverzeichnis: die Spalte links.

Das war nur möglich, weil vorher zwei Orte dasselbe zeigten — und weil die
Suche in dem einen stand, den man erst aufmachen musste. Jetzt steht sie da,
wo man ohnehin hinsieht.

**Die Treffer kommen direkt unter das Suchfeld.** Sie hängen an einem Rahmen,
der das Feld und den Knopf zum Leeren umfasst, und sind so breit wie dieser
Rahmen. Sie erscheinen nur, wenn wirklich etwas gesucht wird — ein Feld, das
beim Lesen im Weg hängt, ist ein Fehler.

- **Die Auswahl räumt die Suche weg.** Hielt man sie fest, bliebe das
  Verzeichnis auf die Treffer gefiltert und man sähe die übrigen Seiten
  nicht mehr — obwohl man gerade in einer davon liest.
- **Escape nimmt sie zuerst**, denn sie liegt über allem, und die Panels sind
  danach ohnehin zu. Suche geht vor Panels.
- Die Liste steht **nicht** im Druck, wie alles Bedienende dort.
- Das Verzeichnis links filtert **weiterhin** mit — das war schon so und
  wird von mehreren Tests geprüft. Die Liste unter dem Feld ist der
  zusätzliche Weg, und der einzige, der noch da ist, wenn das Verzeichnis
  zugeklappt ist: auf einem schmalen Fenster ist es das immer.

Der **Hinweis auf die Reihenfolge** ist aus dem Fuß des rechten Panels in
den Fuß des Menüs gewandert — er gehört zu den Zeilen mit den Griffen, und
die stehen links.

Mitgegangen: `showToc`, `openToc`, `onSearchInput`, die CSS für `.menu-toggle`
und für das zweite Suchfeld im Panel, und der Knopf für die Seitenzahl.

**Und eine Ungleichmäßigkeit, die dabei auffiel.** Der Abstand zwischen den
Knöpfen im Kopf wird jetzt an den anderen Knöpfen **gemessen** statt
festgeschrieben — und der Fluss-Knopf hatte einen eigenen Abstand von 2
Pixeln, ein Rest aus der Zeit, als er allein im Kopf stand. Alle anderen
Abstände kommen aus der Gruppe. Der Rest ist weg.

Ein Fehler war meiner: beim Ausreißen des Panels habe ich die **Hinweiszeile
mitgenommen**, die zwischen Panel und Verweis-Panel stand. 23 Prüfungen
meldeten daraufhin „kein Hinweis" — so viele, dass es eindeutig war.

Zwei Prüfungen kamen dafür dazu: die Trefferliste hängt unter dem Suchbereich
und ist genauso breit — vorher stand nirgends, dass „darunter" eine
Forderung war, sondern nur, dass sie irgendwo sichtbar ist.

**700 → 703 Prüfungen**, 23 Testdateien.

### `AGENTS.md`: was beim nächsten Mal wieder gewusst sein muss — und ein Knopf mit einem Zeichen

**`AGENTS.md` ist neu.** Sie sammelt das, was eine neue Sitzung nicht weiß
und nicht raten sollte:

- **vorher fragen**, wenn etwas mit dem MWS zu tun hat — der Austausch ist
  freigegeben, optische Änderungen auch, der Rest nicht
- **provisionieren** nach jeder Änderung, sonst sieht man nichts davon
- **nicht pushen**; committen ja, sobald ein Vorgang fertig ist
- **der Nutzer ist die Augen**: keine Screenshots, um eine Änderung zu
  prüfen. Statt eines Bildes die Zahl messen oder den Test schreiben, der
  sie festhält. Ausgenommen nur, wenn ein Aufbau-Problem die Ursache nicht
  erkennen lässt und kein Test es fassen kann
- **drei Fallen**, die in dieser Suite schon zugeschlagen sind: Headless
  nimmt kein Fenster unter 500 Pixeln; eine Position nach einer Transition
  ist dem Zufall überlassen; Headless-Chromium ist ein Snap und darf weder
  `/tmp` lesen noch dorthin schreiben
- **wie der Nutzer arbeitet**: er benennt Änderungen am Ergebnis, sagt nicht
  wie, und meldet sich, wenn etwas nicht passt

**Und der Knopf für eine neue Seite trägt jetzt nur noch ➕**, der Hinweis
drauf bleibt. Mit dem Wort waren es 116 Pixel, mit dem Zeichen 48 — der Kopf
passt dadurch bei 780 Pixeln wieder in **eine** Zeile, wo er vorher umbrach.

Dabei kam eine Ursache heraus, die nicht am Knopf lag: `.menu-toggle` trug
`margin-left: auto` und schob damit den ganzen Leerraum vor sich her. Der
Knopf für eine neue Seite — als erster in der Reihe — blieb allein beim
Suchfeld liegen, **372 Pixel** vor ☰. Die Knöpfe des Kopfs liegen jetzt in
einer Gruppe `.kopf-werkzeuge`, die den Leerraum gemeinsam schluckt. Der
Abstand zwischen ➕ und ☰ ist derselbe wie zwischen allen anderen.

Acht Tests suchten den Knopf **nach dem Text**. Mit einem Zeichen finden sie
ihn nicht mehr, und vier davon prüften „der Knopf ist weg" — die hätten
künftig **immer** bestanden. Sie suchen jetzt nach `.kopf-neu`, und der Name
steht als `title` und `aria-label` daran.

Und noch einmal die Transition, zum dritten Mal an derselben Stelle: der
Test maß die Breite der Spalte 900 ms nach dem Aufklappen. Beim vorigen Lauf
war die Fahrt schon fertig, beim ersten nicht. Der Test prüft jetzt den
Zustand und die CSS-Regel.

**700 → 701 Prüfungen**, 23 Testdateien.

### „Neue Seite" wandert in den Kopf, links neben das Verzeichnis — 700 Prüfungen

Eine Seite anlegen ist eine Tat, kein Ort. Der Knopf stand zwischen zwei
Zeilen, die man sich sonst ansieht, und er stand an der einen Stelle, an der
man ihn am wenigsten vermutet.

Er steht jetzt im Kopf, links von ☰, und im Fuß des Verzeichnisses steht
nur noch der Hinweis auf die Reihenfolge.

- Wie die anderen Schreibknöpfe **verschwindet er, wer nicht schreiben darf** —
  `t_anmeldung.py` prüft das am echten Server und war das ohnehin die
  Bedingung
- auf schmalen Fenstern **klappt der Text ein** und es bleibt ein „+", wie
  beim Fluss-Knopf daneben
- im Fuß des Verzeichnisses ist der untere Rand des Hinweises weg, der
  gehörte zum Knopf daneben

**Und zwei Fehler, die ich beim Umbau selbst gemacht habe.** Beide wären
ohne die Tests in die Wiki gegangen:

1. Das Plus stand doppelt da: „+ + Neue Seite". `t('newPage')` enthält es
   schon. Ein Test prüft die Zeichenkette nicht — dafür ist er nicht da.
   Bei der Messung stand es da.
2. `@click="createNewPage; closeAllPanels()"` — **ohne** Klammern ist in Vue
   eine Methode, die man ansieht und dann wegwirft. Aufgerufen wurde nichts,
   der Knopf tat gar nichts, und `t_mws.py` meldete nüchtern
   „erste neue Seite heisst Alpha". Jetzt mit Klammern.

`tests/t_kopf.py` prüft die Reihenfolge der Kopf-Knöpfe mit — sie ist jetzt
`neu toc fluss refs settings thema` — und dass der Knopf links neben dem
Verzeichnis sitzt. `t_fluss.py` prüft, dass im Verzeichnis kein Knopf mehr
steht, nur noch der Hinweis.

Eine Prüfung habe ich gleich mitgezogen, weil sie an der Headerhöhe hing:
`t_menue.py` verlangte „mehr als 400 Pixel hoch". Mit dem sechsten Knopf im
Kopf bricht der Kopf in eine zweite Zeile um, die Spalte wird 378 Pixel
hoch, und die Prüfung wird rot — an einem Umbau, den sie nicht meint.
Sie prüft jetzt „reicht bis zum Fuß". Eine feste Pixelzahl in einem Test
gilt immer nur für die Kopie des Tages.

**693 → 700 Prüfungen**, 23 Testdateien.

### Die Panels werden nicht mehr neben das Fenster geparkt, sondern auf seine Kante — 693 Prüfungen

Im Gerätemodus von Chrome (Galaxy S20 Ultra, 412 Pixel) war rechts ein
Streifen des Einstellungs-Panels zu sehen, **ohne dass jemand es geöffnet
hatte**. Das war seit dem ersten Tag so und stand seit zwei Tagen als
Beobachtung dabei — nicht, weil es harmlos war, sondern weil ich es nicht
zu Ende angesehen hatte.

Die Ursache ist eine Zahl im Stylesheet. Die Panels parkten mit
`right: -360px`: so weit rechts, wie sie breit sind. Das stimmt, solange sie
breit sind — und unterhalb von 768 Pixeln macht eine Media Query daraus
300 Pixel. Der Versatz blieb 360. Auf einem schmalen Fenster standen die
Panel damit 60 Pixel **im** Bild statt genau daneben.

Geparkt wird jetzt mit `translateX(100%)` — mit dem eigenen Maß des Panels.
Das hängt an keiner Zahl und damit an keiner Breite, und es gilt für jedes
Fenster, auch für eines, das morgen noch schmaler wird.

`tests/t_panels.py` prüft die Massgabe so, dass sie am alten Gesetz
gescheitert wäre: nicht „das Panel ist nicht zu sehen" (das galt vorher
auch), sondern „das Panel steht **genau** auf der Kante". Bei 500 Pixeln ist
das der Unterschied zwischen 765 und 780 — 15 Pixel, die Breite einer
Bildlaufleiste. Ein Panel steht an `right: 0` am Rand des **Layouts**, und
dort sitzt die Bildlaufleiste daneben, nicht darüber; `window.innerWidth`
zählt sie mit. Beides ist richtig, und man darf sie nicht verwechseln.

**Und dabei kam heraus, dass diese Suite seit langem lügt.** Chromium nimmt
kein Fenster unter 500 Pixeln:

```
--window-size=320   ->  innerWidth=500
--window-size=380   ->  innerWidth=500
--window-size=412   ->  innerWidth=500
```

`t_kopf.py` und `t_menue.py` wollten **380 Pixel** und haben **500**
gemessen. Beide fragten `innerWidth <= 560` — und 500 erfüllt das. Zwei Tests
waren grün und prüften etwas anderes als behauptet: das ist die Lehre aus
`tests/README.md`, eine Ebene tiefer, weil man sich das Fenster hier nicht
aussuchen konnte, ohne es zu bemerken.

Zwei Hebel wurden versucht und bringen nichts:
`--force-device-scale-factor` ändert `innerWidth` nicht, und die Wiki in
einen 380 Pixel breiten Rahmen zu setzen bringt nichts, weil dessen Timer
unter `--virtual-time-budget` nicht laufen. Einen Test, der so nicht
läuft, habe ich deshalb **nicht** geschrieben — lieber keiner als einer, der
nur so aussieht.

Was bleibt: Beide Tests **sagen es jetzt im Bildschirm**, statt eine Zahl zu
behaupten, und die Tatsache steht in `tests/README.md`. Das eigentliche
Verhalten bei 412 Pixeln muss auf einem Bildschirm geprüft werden — im
Gerätemodus von Chrome, wie es der Nutzer getan hat. Was sich prüfen lässt,
ist getestet: die Panels stehen bei **jeder** Breite auf der Kante.

Und noch eine Lektion, die dritte in Folge an derselben Stelle: nach dem
Anklicken wird die Lage eines Panels nicht gemessen. Es fährt 300 ms ein,
und unter Virtual Time steht die Fahrt am Anfang. Der Test prüft die Klasse
und die CSS-Regel.

**677 → 693 Prüfungen**, 23 Testdateien.

### Auf einem schmalen Fenster fängt das Verzeichnis zugeklappt an — 677 Prüfungen

Das Verzeichnis stand auch dann offen, wenn es mehr als die Hälfte des
Fensters wegnahm: bei 420 Pixeln waren das 300 Pixel Verzeichnis und 120
Pixel Text.

Ab einer Fensterbreite von **640 Pixeln** fängt es deshalb zugeklappt an.
Die Zahl ist eine Rechnung und keine Empfindung: unterhalb von 768 Pixeln
wird das Verzeichnis 300 Pixel breit, und bliebe es offen, käme der Text auf
weniger als 340 Pixel — schmaler als die Spalte auf einem Telefon. Man kann
es lesen, aber es ist kein Lesen mehr.

Die Grenze steht als `TOC_MENUE_OFFEN_BIS` an **einer** Stelle im Programm,
und `t_menue.py` prüft das nach — die Grenze selbst im Browser, und dass sie
an genau einer Stelle steht und nirgends gespeichert wird, in der Datei.

**Nur beim Start.** Wer das Verzeichnis zuklappt, hat das so entschieden, und
das gilt auch, wenn das Fenster danach schrumpft. Ein Menü, das sich beim
Ziehen selbst umstellt, ist eines, dem man nicht traut.

Nachgemessen: 600 Pixel → zu, 660 Pixel → offen mit 300 Pixel Spalte,
900 Pixel → offen mit 360 Pixel.

**669 → 677 Prüfungen.**

### Drei Zeilen raus: das Menü gehört zur Seite und nicht in eine Karte — 669 Prüfungen

Drei Angaben, die das Menü wie eine Karte aussehen ließen, sind weg.

- `background: var(--bg-secondary)` an `.toc-menu` — das Menü bekommt keinen
  eigenen Grund mehr. Es hat denselben wie die Seite, und das ist der ganze
  Punkt: es ist ein Teil der Seite, kein Kasten daneben.
- `border-right: 1px solid var(--border-color)` an `.toc-menu` — keine
  Trennlinie. Die Kante zwischen Verzeichnis und Infall sagt das Fähnchen,
  und die steht genau dort.
- `border-bottom: 1px solid var(--border-color)` an `.side-header` — auch
  keine Linie unter „Inhaltsverzeichnis".

Dazu eine vierte, die niemand verlangt hat und die von selbst mitfällt: der
Menükopf hatte `background: var(--bg-primary)`. Den gab es nur, um die
vorherige Kartenfarbe wieder zu überschreiben. Ohne Karte ist er nichts, was
man sehen könnte.

`.side-header` ist eine gemeinsame Klasse — sie hängt auch am Verzeichnis-
und Verweis- und Einstellungs-Panel rechts. Die drei Panels verlieren ihre
Trennlinie unter der Überschrift mit. Das ist die Kehrseite und vermutlich
genau richtig: es sind dieselben Panels, und eins sah aus wie die anderen.

Im Hellen wie im Dunklen nachgesehen und am PDF gegengeprüft. 669 Prüfungen.

### Das Menü ist eine Spalte, kein Overlay — 669 Prüfungen

Der erste Versuch legte sich vor den Inhalt. Zwei Beschwerden kamen zurück:
das Menü verdeckte die Kopfzeile, und es drängte nichts zur Seite.

Eine Overfläche kann das nicht. Sie liegt über allem und wird nur
dazugestellt — und wenn daneben nichts Platz ist, verschwindet Inhalt
hinter ihr, statt zur Seite zu rücken.

Also ist es jetzt eine **Spalte im Aufbau**. Der Körper der Wiki ist eine
Zeile aus zwei Teilen: links das Verzeichnis, rechts der Inhalt. Das Menü
ist ein Flex-Kind und nicht mehr `position: fixed`. Damit kommt von selbst,
was gefordert war:

- es **beginnt unter der Kopfzeile** — die ist ein eigenes Flex-Kind über
  der Zeile, und ihre Höhe ist ihr eigener, nicht unsere
- es **drängt den Inhalt nach rechts** — es nimmt Platz im Aufbau, statt zu
  überdecken. Wer es zuklappt, gibt den Platz wieder her, und der Text rückt
  nach links
- es **verdeckt nichts** — kein Punkt, kein Absatz, keine Taste liegt
  hinter ihm

Dazu die Kleinarbeiten, die ein Umbau mit sich bringt:

- `min-width: 0` an der Inhaltsspalte. Ohne das weigert sich ein Flex-Kind,
  schmaler zu werden als sein Inhalt, und die Spalte bliebe breit.
- `min-height: 0` am Körper, damit der Rollbalken im Fluss greift
- `max-width: 85%` am Menü und `min(var(--toc-breite), 85%)` am Fähnchen:
  auf einem 320-Pixel-Fenster soll nicht die ganze Wiki unter dem Verzeichnis
  verschwinden
- Der Körper steht im Druck mit auf `display: block` und
  `height: auto`, sonst sähe das Papier eine Zeile mit zwei Spalten

**Und ein Fehler, den erst die zweite Liste aufgedeckt hat.** `onZeileKeydown`
nahm die Zeile, auf der der Fokus landen soll, aus dem **ganzen Dokument**:
`document.querySelectorAll('.toc-item')[ziel]`. Mit einer Liste stimmt das.
Mit zweien liegen sie nebeneinander, und nach einem Alt+Pfeil im Panel rechts
sprang der Fokus in die Liste links — man drückt an einer Stelle und tippt an
einer anderen. Die Zeile hält sich jetzt ihre Liste, aus der sie gedrückt
wurde, und `t_menue.py` prüft das für beide.

**Und noch eine Lektion, die ich mir gerade selbst gegeben hatte.** Der erste
Versuch des Tests maß die Breite der Spalte kurz nach dem Zuklappen — genau
die Sache, vor der die Lehre in `tests/README.md` warnt. Zweimal rot, ohne
dass etwas kaputt war. Der Test prüft jetzt den Zustand und die CSS-Regel,
nicht die Mitte einer 250-ms-Fahrt.

**660 → 669 Prüfungen.** Am PDF gegengeprüft: keine Kopfzeile, kein Fähnchen,
keine Taste — und der Text steht am linken Rand.

### Das Inhaltsverzeichnis wird ein Menü, und das Löschkreuz verschwindet — 660 Prüfungen

Zwei optische Änderungen, beide in `simplewiki.html`.

**1. Kein Löschkreuz mehr im Verzeichnis.** Es stand eine Zeile entfernt vom
Löschen einer ganzen Seite, mit einem Dialog dazwischen, der nach einem
Versehen trotzdem wegklickt. Gelöscht wird jetzt nur noch dort, wo man es
gerade tut: im Editor, neben Bearbeiten und Speichern, mit Abbrechen daneben.

**2. Das Verzeichnis steht links als Menü.** Vorher musste man es erst über
☰ aufmachen — ein Verzeichnis, das man sich suchen muss, ist keines. Es ist
jetzt beim Öffnen da und fährt am **Fähnchen** an der Innenkante weg und
wieder heran. Kein Overlay: es dunkelt nichts ab, ein Klick daneben wirft es
nicht zu, und wenn man darin eine Seite wählt, bleibt es offen. Ein Menü
verhält sich so.

Das Panel rechts (☰) bleibt, wie es war, mit allem was darin war — die Liste
steht jetzt an zwei Orten. Das ist gewollt: das Menü ist der bequeme Weg,
das Panel rechts der Ort, an dem die Suche steht.

- dieselbe Breite wie das Panel rechts, an einer Stelle als `--toc-breite`
  festgelegt, damit Menü und Fähnchen nicht auseinanderlaufen können; das
  Fähnchen rechnet sogar in sehr schmalen Fenstern mit (`min(…, 90vw)`)
- `side-panel` bleibt dran — damit erbt das Menü die Druckregel und
  verschwindet auf Papier, wie die anderen Panels
- Fähnchen mit `title`, `aria-label` und `aria-expanded`, beide Richtungen
  übersetzt (deutsch und englisch)
- Der Zustand gilt nur für dieses eine Fenster. Er wird nicht gemerkt: wer es
  zuklappt, will es auch beim nächsten Mal aufgeklappt haben.

`tests/t_menue.py` prüft das nach — und steckt dabei zweimal den Finger in
eine Wunde, die schon im Haus war:

> **Eine Position nach einer Animation ist dem Zufall überlassen.** Die
> Transition fährt 300 ms, und unter Virtual Time läuft die Animationsuhr
> nicht zuverlässig mit den Timern des Testskripts. Der erste Versuch des
> Tests hat genau daran zweimal rot gemeldet, ohne dass etwas kaputt war.
> Gemessen wird jetzt nur dort, wo noch nichts gefahren ist; die *Wirkung* des
> Zustands wird an der Klasse und an der CSS-Regel geprüft.

Weil die Liste nun zweimal im Dokument steht, zählt in den Tests jedes
`.toc-item` doppelt. Wo ein Test zählt oder vergleicht, schreibt er jetzt
`.toc-panel` davor — das Panel rechts, der Ort, den diese Tests seit jeher
beschreiben. Zwei Löschtests gingen vorher über das Kreuz im Verzeichnis und
löschen jetzt über den Editor; im Zuge dessen kam ein Fehler in `t_suite.py`
zum Vorschein, wo beim Umbau zwei Klammern zu viel geschlossen waren — der
Test meldete daraufhin „KEIN REPORT" statt einer Zahl.

**621 → 660 Prüfungen.**

### Tests, die nicht liefen — 621 Prüfungen statt 539

Drei Dateien haben der Suite Arbeit gemeldet, die sie nicht geleistet haben.
Drei Fehler derselben Art, alle gefunden beim Nachsehen auf eine Zahl, die
nicht aufging.

**Ein Test, der nie läuft, ist grün.** `pruefe()` beendet das Skript. In
`t_kopf.py` stand der Aufruf für die Kopie mit dem schmalen Fenster **hinter**
dem `sys.exit` — die Prüfungen liefen, ihre sechs Ergebnisse waren aber weder in
der Zahl noch im Exitcode. `_kopf2.html` konnte nicht mehr rot werden.

**Und derselbe Fehler ein drittes Mal, mit mehr Schaden.** In `t_leerwiki.py`
stand `pruefe(kopie1, kopie2)` hinter demselben `sys.exit`: **Teil 1 lief nie** —
die 13 Prüfungen für die oberen Fremdfelder (`autor`, `herkunft`, `exportdatum`),
also genau der Weg, den ein Kind geht, wenn es ein fremdes JSON einliest und
zurückgibt.

**Eine Prüfung ohne Zahl ist eine Prüfung ohne Wirkung.** `alle.py` zählt nur,
was als `GESAMT: N bestanden, M fehlgeschlagen` dasteht. Drei Skripte zählten
ihre Fehler, meldeten aber keine bestandenen Prüfungen und trugen deshalb zur
Gesamtzahl **null** bei — bei laufenden Prüfungen.

Dazu eine Kleinheit in `t_abnahme.py`: `melde()` hat einen durchgefallenen
Abnahmepunkt **sowohl als bestanden als auch als fehlgeschlagen** gezählt.

Behoben:

- `pruefe()` kann jetzt ein Fenster je Kopie bekommen (`fenster=`) und Fehler
  aus den vorangegangenen Teilen eines Skripts mitrechnen (`schon_fehler=`) —
  damit wieder ein Aufruf am Ende alles zusammenführt, statt am Skript-Ende
  zu stehen und dort zu sterben
- `_kopf2.html` und `_weg1.html` laufen durch denselben Weg wie der Rest und
  zählen mit
- `t_export.py` und `t_fluss.py` melden eine `GESAMT:`-Zeile
- in `t_kopf.py` stand `>>> 0 FEHLGESCHLAGEN || ALLE BESTANDEN` — `0` ist in
  JavaScript ein wahrer String, der Ausweichzweig griff nie

Geprüft, dass es wirkt: ein absichtlich scheiternder Test mit schmalem Fenster
macht den Lauf rot und nennt die Prüfung.

**539 → 621 Prüfungen.** Die 82 dazugekommenen sind keine neuen Prüfungen,
sondern längst vorhandene, die nie stattgefunden haben.

### `README.md` und `CHANGELOG.md`

Was fehlte, ist jetzt da.

- **`README.md`** — was das ist, wie man loslegt, wie `simplewiki.html`
  aufgebaut ist (mit Zeilennummern), die zwei Betriebsarten, das
  Austauschformat, der Provisionier-Schritt, die Tests, die eingebetteten
  Bibliotheken mit Lizenz und Version, und die Grenzen, die Absicht sind.
- **`CHANGELOG.md`** — alles, was seit der ersten Fassung gebaut wurde, nach
  Tag, mit der Prüfungszahl des damaligen Stands. Nachgeschrieben aus den
  Commit-Nachrichten, nicht erfunden.
- **`tests/README.md`** nachgezogen: die vier Testdateien fehlten in der
  Übersicht, `pdfinfo`/`pdftotext` fehlten als Abhängigkeit, und der Satz
  „ein Test steht nicht in `alle.py`“ leading zu einem Missverständnis.

Suite zur Zeit des Schreibens: **621 Prüfungen, 0 fehlgeschlagen**, 21
Testdateien.

### Anmelden führt zurück in die Wiki, aus der man kam — 539 Prüfungen

Der Anmelde-Link trägt den Weg, von dem man kommt, als `redirect`-Parameter mit:
`/login?redirect=/wiki/<name>`. Ohne das schickt MWS nach dem Anmelden auf die
Startseite, also auf eine Liste von Konten — wer in einer Wiki auf „Anmelden“
klickt, will danach wieder in dieser Wiki sein und nicht auf einer.

Nimmt der Server den Parameter nicht, ist das **kein Fehler**: man landet auf
der Startseite, also auf dem Weg von vorher.

### Anmelden und abmelden — 538 Prüfungen

- **Anmelden ist ein Link**, kein Knopf mit Rumpeln: es ist ein Link auf
  `/login` mit `title`, damit mittlere Maustaste, Tab und der Link im
  Statusfenster alle so tun, wie man es erwartet.
- **Abmelden geht von hier aus** (`⎋` neben dem Namen), weil es nichts zu
  beweisen gibt: es muss nur eine Sitzung ungültig gemacht werden. Danach wird
  `/status` neu geholt, und was der Server sagt, entscheidet — nicht, was
  gerade noch angezeigt war. Stimmt der Kopf also auch dann, wenn die Sitzung
  schon vorher abgelaufen war.
- **Scheitert das Abmelden, wird es gesagt** — und nichts angezeigt, was nicht
  wahr ist. Eine Abmeldung, die nicht stattgefunden hat, darf nicht aussehen
  wie eine.
- **Kein Passwortfeld in der Wiki.** MWS prüft es mit OPAQUE; die Bibliothek
  dafür lädt diese Wiki bewusst nicht (siehe *Grenzen* in der `README.md`).
- Jeder Schritt bekam einen **eigenen Server**: die Sitzung gehört dem Server,
  nicht dem Browserfenster.

### Merksatz: nach jeder Änderung provisionieren

```bash
npm start provision-simplewiki <pfad>/simplewiki.html
```

Die Wiki liest ihre Schale **aus dem Store**, nicht aus `simplewiki.html`. Ein
Neustart des Servers ändert daran nichts — der Server liest dieselbe alte
Schale aus demselben Store.

Genau das ist an diesem Tag passiert: eine Änderung war Stunden fertig und
getestet (495 Prüfungen grün, der Live-Check gegen das echte MWS ebenfalls) —
und in der laufenden Instanz war **nichts davon zu sehen**. Der Beutel des
Templates war vom Vorabend, die neue Datei nirgends eingelesen. `live_mws.py`
macht den Schritt von selbst, deshalb sah sein Lauf gut aus; der Test allein
hätte aber nicht geholfen.

Der Satz steht jetzt im README, gleich vor der Beschreibung des Live-Checks —
weil man genau dort sucht, wenn die Wiki im Browser anders aussieht als im
Test.

### Anmeldung: der Name steht im Kopf, Schreibtasten nur mit Recht — 495 Prüfungen

Gefragt war die erste Frage schlicht: **unter welchem Namen bin ich
angemeldet**. Die App wusste es nicht. Sie wusste nur, dass ihr ein
Schreibversuch mit 403 beantwortet wurde, und bis dahin standen alle Tasten da,
nur grau.

- `GET /recipe/<name>/status` wird beim Start geholt und beantwortet vier
  Zustände: **niemand angemeldet**, **angemeldet ohne Recht**, **angemeldet mit
  Recht**, **Sitzung abgelaufen**.
- Die **Schreibknöpfe sind nicht abgeschaltet, sondern weg.** Wer nicht schreiben
  darf, soll gar nicht erst auf einen Knopf zeigen, der ohnehin nichts tut.
- Ein **Ausfall ist kein Rechteproblem**: antwortet der Server nicht, wird
  nichts erfunden — kein Nur-Lesen-Zustand, keine verlorenen Knöpfe.
- Läuft die Sitzung **mitten drin** ab, schaltet die App beim nächsten
  Schreibversuch um, ohne Neuladen.

---

## 2026-10-04

### B3: aus der leeren Wiki gibt es jetzt einen Ausgang — 455 Prüfungen

Die leere Wiki war eine Sackgasse: nirgends war ein Ausgang. Der Leerzustand
bekommt jetzt einen Knopf, der die erste Seite anlegt und den Editor öffnet.
Wer nicht schreiben darf, bekommt ihn nicht zu sehen.

### B2: der Tiddler heißt wie die Seite — 445 Prüfungen

Ein Tiddler heißt nach seinem Inhalt, wie es die TiddlyWiki-Konvention vorgibt —
der Vertrag im Kopf der Wiki wurde entsprechend festgeschrieben. Die stabile
Kennung wandert als Feld `sw-id` mit, damit die Seite beim Umbenennen dieselbe
bleibt; ein Tiddler ohne `sw-id` — von MWS oder von einem Menschen angelegt —
liefert seine Kennung aus dem Titel.

Ergänzung an der Oberfläche: ein Feld `reihenfolge`, vierstellig. TiddlyWiki
kennt keine Reihenfolge von Tiddlern, SimpleWiki schon — ohne dieses Feld wäre
sie nach dem Neuladen weg.

### B1: der Marker existiert jetzt wirklich — 435 Prüfungen

Der Punkt im Dokument, hinter dem MWS seine Tiddler einsetzt, stand als
Zeichenfolge **im Kommentar**, der ihn erklärt. MWS sucht wörtlich und nimmt
den ersten Fundort im Dokument — auch einen in einem Kommentar. Die Wiki
stünde schön und leer da, und jede Eingabe landete im Browser und wäre beim
nächsten Aufruf weg. Der Text kommt jetzt genau einmal vor, auf den Roh-Bytes.

### Abnahme: die fünf Punkte als nachlesbarer Test — 430 Prüfungen

Aus der Abnahme wurde `tests/t_abnahme.py`. Fünf Punkte, jeder mit benannten
Prüfungen:

1. **kein Nachladen** — kein `<script src>`, kein `<link rel=stylesheet>`, kein
   `@import`, keine `http(s)://`-Referenz, jede `url()` in den `<style>`-Blöcken
   ist `data:`
2. **die Suite ist grün** — das macht `tests/alle.py`, nicht diese Datei
3. **Doppelklick ohne Netz** — der alte `localStorage`-Zustand schlägt den
   Dateiinhalt
4. **mit injiziertem Store erscheint der Inhalt in der Oberfläche**
5. **eine Änderung ist nach Neuladen wieder da**

### Tests für die MWS-Auswahl und die Verweise — 413 Prüfungen

- **`tests/mwsfixture.py`** baut eine Datei, die so aussieht, als käme sie vom
  MWS: der Marker an die echte Head-Grenze, Testskripte wie `mkcopy` es für
  Dateikopien macht. `mwsserver.py` benutzt dieselbe Funktion — es gibt also
  nur noch **eine** Stelle, die weiß, wie ein Server auszusehen hat. Die
  Fixture wird **erzeugt und nicht gespeichert**: eine mitgecheckte Kopie von
  `simplewiki.html` wäre bei der nächsten Änderung still veraltet, und niemand
  merkt es, bis ein Test etwas anderes prüft als gedacht.
- **`tests/t_mwsdatei.py`** prüft die Auswahl am Marker in vier Durchgängen:
  Marker mit Inhalt (Server liefert), Marker leer (Browser liefert — auch wenn
  die Datei vom Server kommt), gar kein Marker (die gewöhnliche Datei) und
  Schreiben aus einer Datei.
- Der letzte Fall ist der ehrliche: aus einem Doppelklick heraus gibt es keinen
  Server, also schlägt der Schreibversuch fehl. Wichtig ist nur, dass er
  **sichtbar** scheitert — und dass nicht so getan wird, als wäre die Wiki nur
  lesbar.
- Dabei kam ein Fehler heraus, der nichts mit MWS zu tun hatte und deshalb
  lange unentdeckt war: **marked lässt eine URL mit Leerzeichen nicht als Link
  gelten.** `[Text](wiki:Zweite Seite)` blieb reiner Text, der Verweiszähler
  erkannte dieselbe Stelle aber sehr wohl. Die App widersprach sich selbst: im
  Verweispanel stand der Link, in der Seite stand Text. `ersetzeWikiSyntax()`
  zieht jetzt auch die schon geschriebene Form durchs properpe Verfahren und
  macht daraus `encodeURIComponent`. Da der Schritt nur beim Anzeigen läuft,
  wird am Text nichts geändert, der zum Server geht.
- **Drei Versuche statt zwei**, bevor ein Test als gescheitert gilt. Die Suite
  arbeitet dutzende Browserläufe ab, und zweimal unter Last durchfallen war
  häufig genug, dass ein roter Lauf nichts mehr bedeutet hätte.

### Tiddler und Seite: das Mapping an seinen Ecken geprüft — 394 Prüfungen

Zeitstempel mit 17 Stellen, Tags mit Leerzeichen und Emoji, doppelte Tags,
Tiddler ohne `sw-id`, Systemtiddler, `created` von einem 14-stelligen Wert, das
app-Feld `content` gegen das Tiddler-Feld `text`.

### MWS-Schnittstelle: Fehler sichtbar, `list` und `read` — 380 Prüfungen

Antwortet der Server mit 500, steht der Grund im Hinweis — und es wird **kein
Nur-Lesen-Zustand erfunden**. „Ein Ausfall ist kein Rechteproblem.“

### Speicher: eine Abstraktion, zwei Ausprägungen — 368 Prüfungen

`laden`, `uebernehmen`, `seiteSichern`, `seiteLoeschen`, `startseiteSetzen`,
`themaSetzen`, `spracheSetzen` — sieben Methoden, die der Rest des Programms
kennt und der Rest nicht unterscheidet. Zwei Ausprägungen: `LocalStore` und
`MwsStore`. Geprüft wird nicht nur, dass beide sie haben, sondern dass die
laufende App sie wirklich benutzt.

### MWS-Betrieb: Seiten liegen auf dem Server — 338 Prüfungen

Zwölf Wiki-Zustände gegen einen Testserver: Reihenfolge aus dem Store, Tiddler
ohne Kennung, Startseite aus `$:/DefaultTiddlers`, Dunkelmodus und Sprache aus
den Feldern der Startseite, 403 bei fehlendem Schreibrecht, Store leer →
Browser gewinnt, Server kaputt → Hinweis statt Rechtebehauptung.

### Bibliotheken einbetten: kein CDN mehr — 302 Prüfungen

Vue, marked und TOAST UI stecken fest in der Datei statt von einem CDN zu
kommen. Eine strikte Content-Security-Policy erlaubt nur `self`, und eine Wiki
soll auch ohne Netz laufen.

### Aus dem Inhaltsverzeichnis: nur noch der Druck-Knopf

Im Fluss bleiben Kopfzeile, Suche und Einstellungen stehen; im
Inhaltsverzeichnis verschwindet der Fluss-Knopf, damit er nicht an zwei Orten
auftaucht. Abstand zu den Seitenrändern, wie man ihn beim Lesen erwartet.

### Fluss-Knopf in den Kopf

Der Fluss wird aus dem Inhaltsverzeichnis in die **Kopfzeile** verschoben: ein
Knopf, eine Wirkung, und er ist auch erreichbar, wenn das Inhaltsverzeichnis
zu ist. Geprüft wird auch die **Reihenfolge der Knöpfe im Kopf**
(`toc · fluss · refs · settings · thema`) und dass alles davon in einem Fenster
mit 380 Pixeln Breite noch passt.

### Exportweg fertig: Fremdangaben oben, leere Vorlage, Vertrag

- **Fremdangaben** auf der obersten Ebene (`autor`, `herkunft`, `exportdatum`)
  überstehen einen Hin-und-Her-Weg.
- **Leere Vorlage** (`simplewiki-leer.html`) zum Füllen für ein anderes
  Programm — nicht zum Laden: eine Datei ohne Seiten wird abgelehnt, sonst
  ersetzt ein missglückter Export die ganze Wiki.
- **Fremde JSON-Datei laden** und als Wiki-Datei weitergeben.

### Lesebreite in der Seitenansicht wie im Fluss

Die Textspalte war nur im Fluss begrenzt (860px); die normale Seitenansicht
lief über die volle Fensterbreite. Jetzt ist **beide gleich breit**, damit eine
Seite und ihre Nachbarin im Fluss gleich aussehen.

- `--spaltenbreite` als CSS-Angabe an genau einer Stelle, damit die beiden
  Ansichten nicht auseinanderlaufen können
- die Begrenzung sitzt auf den **Kindern** von `.content-body` und nicht auf
  `.content-body` selbst: der Scrollbalken bleibt am Fensterrand statt bei der
  Spalte zu stehen
- seitliches Polster im Fluss gestrichen — es hat den Text dort noch 40px
  schmaler gemacht, deshalb passten die Breiten trotz gleicher Zahl nicht
  wirklich zusammen

**Gemessen statt geschätzt:** 860px in beiden Ansichten.

Dabei kam ein Nebenschaden heraus, den ein bloßes Anschauen nicht gezeigt
hätte: die Kopfzeile ist ein Flex-Kind und schrumpfte mit den automatischen
Rändern auf 57px — der Trennstrich unter dem Titel war nur noch kurz. Sie
bekommt jetzt `width: 100%`.

### Austausch mit MWS: JSON, Version, fremde Felder

Das Austauschformat steht jetzt im Kopf der Datei, als Kommentar, der
beides ist: die Doku und der Vertrag. Drei Zusagen, die ein Test prüft —
JSON und HTML gleichwertig, fremde Felder bleiben, zu neue Dateien werden ganz
abgelehnt.

Zwei Entscheidungen, die nicht in der Vorgabe standen: eine Datei **ohne
Seiten** wird abgelehnt statt als leeres Wiki übernommen, und beim **Anlegen**
wird ein vergebener Name still eindeutig gemacht, beim **Umbenennen** wird
abgelehnt und der Name genannt.

### Fluss: scrollbar und Druck über mehrere Seiten

Der Fluss ließ sich in einem kurzen Fenster nicht scrollen, und der Druck
verlor alles nach Bildschirmhöhe. Beides fiel nur auf, weil der Test mit einem
Fenster von 900×420 Pixeln und absichtlich langen Seiten prüft — und weil am
Ende nicht nur „sieht vollständig aus“ steht, sondern der letzte Satz der
letzten Seite wirklich im ausgelesenen PDF.

### Sichern: die Datei behält ihre Oberfläche

Die gesicherte Datei ist dieselbe Datei: dieselbe Oberfläche, dieselben
eingebetteten Bibliotheken, nur die Dateninsel ist gefüllt. Ein
`<script>` im Seiteninhalt übersteht das als `</script` in der Datei.

### Reihenfolge per Ziehen ändern und das Wiki als Datei sichern

Griff ⠿ zum Ziehen, **Alt + Pfeiltaste** als zweiter Weg für die Tastatur, und
ein Hinweis, der beide nennt. Während der Suche ist die Reihenfolge gesperrt —
und der Hinweis sagt, warum.

### Verweise als eigenes Panel

Rück- und Ausgehende mit Zähler im Kopf, mit `→` und `←`, fehlende Ziele als
`?` mit der Möglichkeit, sie anzulegen. Der Zustand (offen oder zu) überlebt
das Neuladen.

### TiddlyWiki-Syntax `[[Seite]]` und `[[Text|Seite]]` verlinken

Innerhalb von Code ist `[[…]]` kein Verweis, sondern Beispieltext.

### Tests ins Projekt holen, bevor `/tmp` sie wegwischt

Die 224 Prüfungen lagen in `/tmp/opencode` — beim nächsten Neustart wären sie
weg, und gerade **sie** haben mehr gerettet als meine Vorsicht. Sie liegen jetzt
unter `tests/` und werden mitversioniert.

```bash
python3 tests/alle.py          # alles
python3 tests/alle.py fluss    # nur ein Teil
python3 tests/t_order.py       # ein einzelner Test
```

Endecode 0 heißt: alles bestanden.

- Pfade sind relativ, der Ordner darf liegen, wo er will
- Kopien, PDFs und Bilder landen in `tests/_kopien/` und werden nicht committet
- `mkcopy.py` setzt `localStorage` vollständig zurück; vorher schleppte ein
  Testlauf seinen Zustand in den nächsten — daher kam das Verweis-Panel
  manchmal schon offen herein
- README mit der Übersicht und zwei Lehren aus den Tests

Zwei Fehler beim Umstellen gefunden und behoben: durch das Zusammenfassen der
`build`-Aufrufe kam die Zustandsvorgabe auch in die erste Kopie, und eine
Prüfung erwartete noch „nichts gespeichert“, obwohl der Seed inzwischen
bewusst einen Wert schreibt.

---

## 2026-10-03

### Seiten duplizieren

Der ⧉-Knopf legt eine Kopie mit eigenem Namen an. Sie bekommt **eigene
Kennung, eigene Verknüpfungen** — ein Link in der Kopie zu entfernen fasst die
Vorlage nicht an.

### Seiten verlinken: Verknüpfungen und Rückverweise

Der Verweis auf eine andere Seite steckt in den **Seiten-Metadaten**
(`page.links`), nicht im Markdown-Text: die direkte Schreiboperation in den
Toast-Editor scheitert unter `file://` mit
`RangeError: Applying a mismatched transaction`.

- Link-Dialog im Bearbeitungsmodus: Seiten verknüpfen und lösen, nicht
  vorhandene Seiten werden dabei angelegt
- Abschnitt „Verlinkt auf“ mit den Zielen und „Verlinkt von“ mit den
  Rückverweisen
- der Leer-Zustand hängt an `v-if="!currentPage"` und wird deshalb **nur**
  gezeigt, wenn es wirklich keine Seite gibt

### SimpleWiki: erste Fassung als einzelne HTML-Datei

Oberfläche, Editor, Markdown, Speicher im Browser und alle Bibliotheken in
**einer** Datei. Kein Server, kein Build, keine Installation: wer die Datei
doppelklickt, hat ein Wiki; wer sie weiterreicht, gibt ein Wiki weiter.