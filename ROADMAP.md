# Feuille de route — propositions d'évolution (2026)

Ce document liste ce qui a été fait lors de la remise à neuf d'octobre 2026, puis les
améliorations proposées projet par projet, classées par priorité :
🔴 important · 🟠 utile · 🟢 bonus.

---

## Ce qui a été fait (refresh 2026)

| Domaine | Changement |
|---|---|
| Dépôt | `LICENSE` (MIT), `.gitignore`, suppression des `.DS_Store` et `boot_out.txt`, README pour chaque projet, README racine refait avec tableau d'état |
| Bibliothèques | Les `.mpy` Adafruit (formats v3/v5, incompatibles avec CircuitPython 9/10) ont été retirés : chaque projet a un `requirements.txt` pour `circup` |
| Modules perso | Le layout AZERTY (`keyboard_layout_fr.py`) et `adafruit_ducky` modifié (devenu `ducky_bebox.py`) sont sortis du paquet `adafruit_hid` et renommés : `circup update` ne peut plus les écraser |
| API CP 9/10 | `display.show()` → `display.root_group`, `displayio.FourWire` → `fourwire.FourWire` (avec repli CP 8), suppression de `max_size` / `max_glyphs` (22 fichiers) |
| Réglages | `secrets.py` → `settings.toml` (modèles fournis, sans vraies valeurs) |
| Images | Photos redimensionnées (−8 Mo) et **métadonnées GPS supprimées** de 2 photos du Seeed XIAO |
| BasicPython | v0.05 : console USB si pas de CardKB, `edit`, `auto`, `ins`, `find`, `vars`, `history`, `time`, `run <fichier>`, écho des expressions, `input()`, Ctrl+C, confirmation avant perte, traceback — manuels EN/FR mis à jour |
| Launcher PyPortal | v2.0 : `supervisor.set_next_code_file()` (fini `exec()` + NVM), retour auto au menu, dossier `/apps`, pages Préc./Suiv., exclusions via `settings.toml` |
| T-Embed | Minuteur v2.0 : pause/reprise, appui long = annuler, anneau de LED + barre de progression, luminosité DotStar corrigée (0–1), `board.DISPLAY` natif |
| Challenger 2040 | Démo Wi-Fi réelle via `adafruit_espatcontrol` (scan + connexion) |
| MagTag météo | Passage à l'API OpenWeather One Call 3.0 (la 2.5 a été arrêtée en 2024) |
| DuckyPad | 16 blocs copiés-collés remplacés par une boucle |

> ⚠️ Tout le code a été vérifié (syntaxe, et BasicPython testé sur PC avec des modules simulés),
> mais **pas sur les cartes**. À tester en priorité : launcher, T-Embed, Challenger.

---

## BasicPython (PyPortal Titano / Wio Terminal)

- 🔴 **Rendre CIRCUITPY inscriptible** depuis BasicPython : fournir un `boot.py` qui fait
  `storage.remount("/", readonly=False)` quand un bouton est maintenu (sinon `save` échoue
  quand le PC est branché).
- 🟠 **Vrai mode BASIC** : `GOTO`/`GOSUB` simulés, `PRINT`, `INPUT`, `REM`, `FOR..NEXT` traduits
  en Python à la volée. Un « BASIC 80's » complet est faisable avec un petit traducteur.
- 🟠 **Éditeur plein écran** (type `nano`) sur l'écran de la Titano : `edit fichier.py`.
- 🟠 **Coloration** : numéros de ligne et mots-clés en couleur (séquences ANSI).
- 🟢 **Autocomplétion** avec la touche Tab (noms de commandes et de variables).
- 🟢 **`autoexec.py`** chargé et lancé au démarrage, comme sur les micro-ordinateurs.
- 🟢 Commandes `wifi` / `get <url>` sur les cartes avec Wi-Fi (Titano + ESP32 co-processeur).
- 🟢 Commandes `beep`, `color`, `plot x,y` pour faire des démos graphiques comme en 1985.

## CircuitPython Launcher (PyPortal Titano)

- 🟠 **Icônes** : afficher `app.bmp` à côté de `app.py` s'il existe.
- 🟠 Navigation par **boutons physiques** (pour les cartes sans écran tactile).
- 🟢 Applications sur **carte SD** (`/sd/apps`).
- 🟢 Écran « À propos » avec RAM / flash libres et version de CircuitPython.

## BadgerOS (Badger 2040)

- 🔴 **Découper `code.py`** (1 383 lignes) en modules : `ui.py`, `badge.py`, `ebook.py`,
  `hid.py`, `prefs.py`. Moins de RAM utilisée, code beaucoup plus lisible.
- 🔴 Tester sur **CircuitPython 9/10** : le bug de démarrage sur batterie mentionné dans le README
  est peut-être corrigé dans les versions récentes : à vérifier.
- 🟠 Utiliser le **deep sleep** (`alarm.pin.PinAlarm` sur les boutons) : la batterie tient des mois.
- 🟠 Port vers le **Badger 2040 W** (Wi-Fi) : météo, calendrier, synchro des badges.
- 🟢 Mise en page des badges depuis un fichier JSON au lieu de 9 lignes positionnelles.

## T-Embed (ESP32-S3)

- 🟠 **Menu multi-applications** avec la molette : minuteur, chronomètre, Pomodoro, réveil.
- 🟠 Heure réelle via **Wi-Fi + NTP** (`adafruit_ntp`), affichage horloge en veille.
- 🟢 Sauvegarde de la dernière durée dans la NVM.

## Keyboard FeatherWing

- 🔴 Remplacer le menu de boot NVM + `exec()` par `supervisor.set_next_code_file()` (comme le
  launcher PyPortal) : plus fiable et plus simple.
- 🟠 **Porter BasicPython** sur le Keyboard FeatherWing : clavier BBQ10 + écran 320×240, c'est la
  machine idéale pour lui (le pilote clavier est déjà là).
- 🟢 Fusionner `calc.py` / `calculator.py` des deux dossiers (copies quasi identiques).

## MagTag

- 🔴 Même modernisation du **Boot App Selector** (`set_next_code_file()` + `alarm` pour le deep sleep).
- 🟠 Météo : utiliser `adafruit_magtag` en deep sleep entre deux mises à jour (autonomie ×20).

## Seeed XIAO — UART to HID

- 🟠 Protocole simple avec accusé de réception (`OK`/`ERR`) sur l'UART.
- 🟢 Version **XIAO RP2040 / ESP32-S3** avec NeoPixel d'état.

## Pico RGB Keypad — DuckyPad

- 🟠 **Plusieurs pages de macros** (appui long sur une touche = changer de page, couleur par page).
- 🟠 Mode **clavier macro** classique (raccourcis, volume via `ConsumerControl`) en plus de DuckyScript.

## Wio Terminal — SmartTerminal

- 🟠 Partager le **même module clavier** que BasicPython (CardKB + repli USB).
- 🟢 Fusion SmartTerminal + BasicPython : un « mini OS » commun Wio / PyPortal.

## ATMegaZero S2

- 🟢 Même modernisation du BootMenu que le Keyboard FeatherWing.

## Challenger 2040 WiFi

- 🟠 Petit serveur web ou client MQTT de démonstration sur `adafruit_espatcontrol`.

---

## Transverse

- 🔴 **Purger l'historique Git** des anciennes photos qui contenaient la position GPS
  (`Seeed XIAO/UartToHID/images/*.jpg`) avec `git filter-repo`. Cela réécrit l'historique de
  `main` et demande un push forcé, à faire par le propriétaire du dépôt.
- 🟠 **Module commun** `bebox_common` (lecture CardKB/BBQ10, menu, launcher) pour arrêter de
  dupliquer le même code dans 5 projets.
- 🟠 Une **release GitHub** par projet avec un `.zip` prêt à copier sur CIRCUITPY (bibliothèques
  incluses), générée par une GitHub Action à partir des `requirements.txt`.
- 🟢 Captures d'écran / GIF à jour pour T-Embed et BasicPython v0.05.
