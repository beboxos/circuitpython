```
 ╔══════════════════════════════════════════════════════════════╗
 ║                                                              ║
 ║        ██████╗  █████╗ ███████╗██╗ ██████╗                  ║
 ║        ██╔══██╗██╔══██╗██╔════╝██║██╔════╝                  ║
 ║        ██████╔╝███████║███████╗██║██║                        ║
 ║        ██╔══██╗██╔══██║╚════██║██║██║                        ║
 ║        ██████╔╝██║  ██║███████║██║╚██████╗                  ║
 ║        ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝                  ║
 ║                                                              ║
 ║          ██████╗ ██╗   ██╗████████╗██╗  ██╗ ██████╗ ███╗    ║
 ║          ██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║  ██║██╔═══██╗████╗   ║
 ║          ██████╔╝ ╚████╔╝    ██║   ███████║██║   ██║██╔██╗  ║
 ║          ██╔═══╝   ╚██╔╝     ██║   ██╔══██║██║   ██║██║╚██╗ ║
 ║          ██║        ██║      ██║   ██║  ██║╚██████╔╝██║ ╚██╗║
 ║          ╚═╝        ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝║
 ║                                                              ║
 ║                M A N U E L   U T I L I S A T E U R          ║
 ║                        Version 0.04                          ║
 ║                                                              ║
 ║          Pour Adafruit PyPortal Titano — CircuitPython       ║
 ║                  avec clavier M5Stack CardKB                 ║
 ║                                                              ║
 ║                   par @beboxos  (2021-2026)                  ║
 ╚══════════════════════════════════════════════════════════════╝
```

---

## TABLE DES MATIÈRES

```
  1. INTRODUCTION ................................................  3
  2. INSTALLATION DU MATÉRIEL ...................................  4
  3. PREMIERS PAS ...............................................  5
  4. LE CLAVIER .................................................  6
  5. RÉFÉRENCE DES COMMANDES
       5.1  Commandes programme (LIST, RUN, NEW) ...............  8
       5.2  Édition des lignes (N, DEL, RENUM) .................  10
       5.3  Commandes fichiers (SAVE, LOAD, CAT) ................  12
       5.4  Commandes répertoire (DIR, CD, MKDIR, RMDIR) ........  14
       5.5  Opérations sur fichiers (RM, CP, MV) ................  16
       5.6  Commandes système (MEM, DF, VER, CLS, RESET, EXIT) .  18
       5.7  Exécution directe de Python .........................  20
  6. PROGRAMMES D'EXEMPLE .......................................  21
  7. MESSAGES D'ERREUR .........................................  24
  8. ANNEXE — COMPATIBILITÉ CIRCUITPYTHON ......................  25
```

---

# 1. INTRODUCTION

```
  ┌─────────────────────────────────────────────────────────────┐
  │  BIENVENUE DANS BASICPYTHON !                               │
  │                                                             │
  │  BasicPython vous ramène la joie de la programmation       │
  │  directe et immédiate — depuis votre appareil lui-même,    │
  │  sans avoir besoin d'un ordinateur.                        │
  │                                                             │
  │  Tapez une commande. Voyez le résultat. Écrivez un         │
  │  programme ligne par ligne. Exécutez-le. Sauvegardez-le.   │
  │  Reprenez-le plus tard.                                     │
  │                                                             │
  │  C'est l'esprit des micro-ordinateurs des années 1980,     │
  │  réincarné dans un appareil CircuitPython que vous pouvez  │
  │  tenir dans la paume de la main.                           │
  └─────────────────────────────────────────────────────────────┘
```

BasicPython est un shell Python interactif pour appareils CircuitPython, conçu pour fonctionner entièrement sans ordinateur. Il s'inspire du projet original `basicpython` de Scott Shawcroft, porté et enrichi pour l'Adafruit PyPortal Titano par @beboxos.

Vous pouvez :
- Écrire et exécuter des programmes Python ligne par ligne (style BASIC)
- Gérer fichiers et répertoires sur la mémoire flash de l'appareil
- Évaluer des expressions Python directement
- Vérifier l'utilisation de la mémoire RAM et du disque flash
- Le tout depuis un minuscule clavier I2C, sans câble USB

---

# 2. INSTALLATION DU MATÉRIEL

```
  Matériel nécessaire :
  ┌──────────────────────────────────────────────────────────┐
  │  ● Adafruit PyPortal Titano                              │
  │    (compatible aussi : Seeed WIO Terminal)               │
  │                                                          │
  │  ● M5Stack CardKB — clavier I2C (adresse 0x5F = 95)     │
  │                                                          │
  │  ● CircuitPython 7.x ou 8.x                             │
  └──────────────────────────────────────────────────────────┘

  Câblage :
  ┌──────────────┬──────────────┐
  │  Broche CardKB  │  PyPortal    │
  ├──────────────┬──────────────┤
  │  SDA         │  board.SDA   │
  │  SCL         │  board.SCL   │
  │  GND         │  GND         │
  │  VCC         │  3.3V        │
  └──────────────┴──────────────┘

  ! IMPORTANT : Le CardKB DOIT être détecté à l'adresse I2C 95
                (0x5F). S'il n'est pas trouvé, BasicPython
                affiche une erreur et s'arrête.
                Vérifiez le câblage si cela se produit.
```

**Installation :**

1. Copiez `basicpython.py` à la racine de votre lecteur CIRCUITPY.
2. Pour l'exécuter au démarrage, renommez-le `code.py`.
3. Pour le lancer manuellement depuis le REPL :
   ```
   >>> import basicpython
   ```

---

# 3. PREMIERS PAS

Au démarrage de BasicPython, vous verrez :

```
  ***********************************************************
  *  ___            _      ___  _  _  _    _                *
  * | _ ) __ _  ___(_) __ | _ \| || || |_ | |_   ___  _ _   *
  * | _ \/ _` |(_-/| |/ _||  _/ \_.  ||  _||   \ / _ \| ' \  *
  * |___/\__/_|/__/|_|\__||_|   |__/  \__||_||_|\___/|_||_| *
  ***********************************************************
  v0.04 for CircuitPython devices with CardKB i2c

  Enter !help for command list

  READY.
  >>>
```

L'invite `READY.` signifie que le système attend votre saisie.  
L'invite `>>>` seule (sans READY.) apparaît lorsque vous entrez des lignes de programme.

**Votre première commande — essayez ceci :**

```
  READY.
  >>> print("Bonjour depuis BasicPython !")
  Bonjour depuis BasicPython !

  READY.
  >>>
```

**Pour afficher l'aide à tout moment, tapez :**

```
  READY.
  >>> !help
```

---

# 4. LE CLAVIER

BasicPython utilise le clavier **M5Stack CardKB** via I2C.

```
  ┌─────────────────────────────────────────────────────────────┐
  │  Touche          Action                                     │
  ├─────────────────────────────────────────────────────────────┤
  │  ENTRÉE          Valider la saisie en cours                 │
  │  RETOUR ARR.     Supprimer le caractère avant le curseur    │
  │  ← (gauche)      Déplacer le curseur d'un caractère à gauche│
  │  → (droite)      Déplacer le curseur d'un caractère à droite│
  │  ↑ (haut)        Rappeler la commande précédente            │
  │  ↓ (bas)         Rappeler la commande suivante              │
  └─────────────────────────────────────────────────────────────┘
```

**Historique des commandes :** Chaque ligne saisie est mémorisée. Utilisez les flèches HAUT et BAS pour naviguer dans vos saisies précédentes. Fonctionne aussi bien pour les commandes que pour les lignes de programme.

**Édition en ligne :** Les flèches GAUCHE et DROITE permettent de se déplacer dans la ligne en cours pour corriger une faute sans tout retaper.

---

# 5. RÉFÉRENCE DES COMMANDES

---

## 5.1 — COMMANDES PROGRAMME

---

### LIST

**Syntaxe :** `LIST`

Affiche toutes les lignes non vides du programme en cours, avec leurs numéros.

```
  READY.
  >>> LIST
  10 for i in range(3):
  20   print(i)

  READY.
  >>>
```

Si le programme est vide :

```
  READY.
  >>> LIST
  (program is empty)
```

**Voir aussi :** RUN, NEW

---

### RUN

**Syntaxe :** `RUN`

Exécute le programme en cours. Toutes les lignes sont assemblées dans l'ordre et transmises à la fonction `exec()` de Python.

```
  READY.
  >>> RUN
  0
  1
  2

  READY.
  >>>
```

En cas d'erreur pendant l'exécution, le message d'erreur est affiché et le programme s'arrête :

```
  READY.
  >>> RUN
  Runtime error: ZeroDivisionError: division by zero
```

> **REMARQUE :** Les variables créées lors de `RUN` sont isolées de l'espace de noms de l'exécution directe. Utilisez l'évaluation directe pour les tests rapides, et `RUN` pour le code structuré.

**Voir aussi :** LIST, NEW

---

### NEW

**Syntaxe :** `NEW`

Efface le programme en cours ET réinitialise toutes les variables de l'espace de noms d'exécution directe.

```
  READY.
  >>> NEW
  Program cleared.

  READY.
  >>>
```

> **ATTENTION :** Aucune confirmation n'est demandée. Assurez-vous d'avoir sauvegardé votre programme avec `SAVE` avant d'utiliser `NEW`.

**Voir aussi :** SAVE, LIST

---

## 5.2 — ÉDITION DES LIGNES

---

### Saisie d'une ligne de programme

**Syntaxe :** `N <code Python>`

Où `N` est un numéro de ligne (entier >= 1).

Assigne `<code Python>` à la ligne N. Si des lignes intermédiaires n'existent pas encore, elles sont créées vides.

```
  >>> 10 x = 42
  >>> 20 print("La réponse est", x)
  >>> LIST
  10 x = 42
  20 print("La réponse est", x)
```

Une ligne peut être réécrite en ressaisissant le même numéro :

```
  >>> 10 x = 100
  >>> LIST
  10 x = 100
  20 print("La réponse est", x)
```

> **ASTUCE :** Utilisez des multiples de 10 pour numéroter vos lignes (10, 20, 30...) afin de pouvoir en insérer entre elles plus tard (par exemple la ligne 15).

---

### Suppression d'une ligne (style BASIC)

**Syntaxe :** `N`

Saisissez un numéro de ligne SANS code après. La ligne est supprimée.

```
  >>> 20
  Line 20 deleted.
  >>> LIST
  10 x = 100
```

---

### DEL

**Syntaxe :** `DEL N`

Supprime la ligne N. Équivalent à saisir `N` seul.

```
  READY.
  >>> DEL 10
  Line 10 deleted.
```

Si le numéro de ligne est hors de portée :

```
  READY.
  >>> DEL 99
  Line out of range (1 - 20)
```

**Voir aussi :** RENUM

---

### RENUM

**Syntaxe :** `RENUM`

Supprime toutes les lignes vides/supprimées du programme et renumérote les lignes restantes à partir de 1. Le programme est ensuite listé.

```
  READY.
  >>> RENUM
  Compacted to 3 lines:
  1 x = 42
  2 y = x * 2
  3 print(x, y)
```

> **REMARQUE :** Après RENUM, tous vos numéros de lignes changent. Utilisez RENUM avant une sauvegarde finale avec SAVE.

**Voir aussi :** DEL, LIST

---

## 5.3 — COMMANDES FICHIERS

---

### SAVE

**Syntaxe :** `SAVE <nom_de_fichier>`

Sauvegarde le programme en cours (lignes non vides uniquement) dans un fichier sur la mémoire flash.

```
  READY.
  >>> SAVE /monprog.py
  Saved: /monprog.py
```

Si le nom de fichier est absent :

```
  Usage: save <filename>
```

> **REMARQUE :** Si le fichier existe déjà, il sera écrasé sans avertissement.

**Voir aussi :** LOAD, NEW

---

### LOAD

**Syntaxe :** `LOAD <nom_de_fichier>`

Charge un fichier Python depuis la mémoire flash dans le buffer du programme. Le programme précédent est remplacé.

```
  READY.
  >>> LOAD /monprog.py
  Loaded: /monprog.py - 3 lines
```

Après le chargement, utilisez `LIST` pour voir le programme et `RUN` pour l'exécuter.

> **REMARQUE :** LOAD ne lance PAS le programme automatiquement.

**Voir aussi :** SAVE, LIST, RUN

---

### CAT

**Syntaxe :** `CAT <nom_de_fichier>`

Affiche le contenu d'un fichier à l'écran. Fonctionne avec les fichiers Python, les fichiers texte et les fichiers de configuration.

```
  READY.
  >>> CAT /boot_out.txt
  Adafruit CircuitPython 8.0.5 on 2023-03-31;
  Adafruit PyPortal Titano with samd51j20
  Board ID: pyportal_titano
```

**Voir aussi :** DIR, LOAD

---

## 5.4 — COMMANDES RÉPERTOIRE

---

### DIR

**Syntaxe :** `DIR [chemin]`

Liste le contenu d'un répertoire. Sans argument, liste `/` (racine).  
Les répertoires sont affichés entre `[crochets]`. Les fichiers sont affichés avec leur taille en octets.

```
  READY.
  >>> DIR
  Directory: /
  --------------------------------
  [lib]
  [sd]
  boot_out.txt              312 B
  code.py                  8192 B
  monprog.py                128 B
  settings.toml              64 B
  --------------------------------
  2 dir(s), 4 file(s)
```

Lister un sous-répertoire :

```
  READY.
  >>> DIR /lib
  Directory: /lib
  --------------------------------
  [adafruit_bus_device]
  adafruit_display_text      4096 B
  --------------------------------
  1 dir(s), 1 file(s)
```

**Voir aussi :** CD, MKDIR, RM

---

### CD

**Syntaxe :** `CD [chemin]`

Change le répertoire courant. Sans argument, affiche le répertoire actuel.

```
  READY.
  >>> CD /projets
  /projets

  READY.
  >>> CD
  /projets
```

Retour à la racine :

```
  READY.
  >>> CD /
  /
```

**Voir aussi :** DIR, MKDIR

---

### MKDIR

**Syntaxe :** `MKDIR <nom_répertoire>`

Crée un nouveau répertoire.

```
  READY.
  >>> MKDIR /projets
  Created: /projets

  READY.
  >>> MKDIR /projets/demos
  Created: /projets/demos
```

**Voir aussi :** RMDIR, DIR, CD

---

### RMDIR

**Syntaxe :** `RMDIR <nom_répertoire>`

Supprime un répertoire **vide**. Le répertoire ne doit contenir aucun fichier.

```
  READY.
  >>> RMDIR /projets/demos
  Removed dir: /projets/demos
```

Si le répertoire n'est pas vide :

```
  Error: [Errno 39] Directory not empty
```

**Voir aussi :** MKDIR, RM

---

## 5.5 — OPÉRATIONS SUR FICHIERS

---

### RM

**Syntaxe :** `RM <nom_de_fichier>`

Supprime définitivement un fichier de la mémoire flash.

```
  READY.
  >>> RM /vieux_test.py
  Removed: /vieux_test.py
```

> **ATTENTION :** La suppression est immédiate et permanente. Il n'y a pas de corbeille.

**Voir aussi :** CP, MV, DIR

---

### CP

**Syntaxe :** `CP <source> <destination>`

Copie un fichier. La copie s'effectue par blocs de 512 octets pour préserver la RAM.

```
  READY.
  >>> CP /monprog.py /sauvegarde/monprog_bak.py
  Copied: /monprog.py -> /sauvegarde/monprog_bak.py
```

> **REMARQUE :** Le répertoire de destination doit déjà exister.

**Voir aussi :** MV, RM, MKDIR

---

### MV

**Syntaxe :** `MV <source> <destination>`

Renomme ou déplace un fichier.

```
  READY.
  >>> MV /test.py /projets/test_v2.py
  Moved: /test.py -> /projets/test_v2.py
```

> **REMARQUE :** MV peut déplacer un fichier d'un répertoire à un autre, à condition que les deux soient sur le même système de fichiers (flash). Il ne peut pas déplacer entre la flash et une carte SD. Utilisez `CP` + `RM` dans ce cas.

**Voir aussi :** CP, RM

---

## 5.6 — COMMANDES SYSTÈME

---

### MEM

**Syntaxe :** `MEM`

Lance le ramasse-miettes et affiche l'utilisation de la RAM.

```
  READY.
  >>> MEM
  RAM free :  163840 B ( 160 KB)
  RAM used :   28672 B (  28 KB)
  RAM total: 192512 B ( 188 KB)
```

> **ASTUCE :** Exécutez `MEM` avant de charger une grande bibliothèque ou un programme gourmand en mémoire.

**Voir aussi :** DF, VER

---

### DF

**Syntaxe :** `DF`

Affiche l'espace disque de la mémoire flash (total, utilisé, libre).

```
  READY.
  >>> DF
  Disk total: 8126464 B ( 7936 KB)
  Disk used :  524288 B (  512 KB)
  Disk free : 7602176 B ( 7424 KB)
```

> **REMARQUE :** Utilise `os.statvfs("/")` en interne.

**Voir aussi :** MEM, DIR

---

### VER

**Syntaxe :** `VER`

Affiche la version de CircuitPython, le nom de la carte, la fréquence et la température du processeur.

```
  READY.
  >>> VER
  System  : samd51
  Release : 8.0.5
  Version : 8.0.5 on 2023-03-31
  Machine : Adafruit PyPortal Titano with samd51j20
  CPU freq: 120 MHz
  CPU temp: 43.7 C
```

> **REMARQUE :** La température du CPU peut retourner `None` sur certaines cartes. Dans ce cas, la ligne n'est simplement pas affichée.

**Voir aussi :** MEM

---

### CLS

**Syntaxe :** `CLS`

Efface l'écran.

```
  READY.
  >>> CLS
```

L'écran est effacé et le curseur revient en haut à gauche (séquence d'échappement ANSI).

---

### RESET

**Syntaxe :** `RESET`

Redémarre l'appareil. Équivalent à appuyer sur le bouton de reset matériel.

```
  READY.
  >>> RESET
```

> **ATTENTION :** Si l'appareil est connecté à un ordinateur via USB au moment du reset, une corruption du système de fichiers peut survenir. Déconnectez le câble USB ou éjectez le lecteur au préalable.

---

### EXIT

**Syntaxe :** `EXIT`

Quitte BasicPython et retourne au REPL CircuitPython.

```
  READY.
  >>> EXIT
  >>>
```

---

## 5.7 — EXÉCUTION DIRECTE DE PYTHON

Toute saisie qui n'est pas une commande reconnue et ne commence pas par un numéro de ligne est évaluée directement comme code Python.

```
  READY.
  >>> 2 + 2
  4

  READY.
  >>> import math
  READY.
  >>> math.sqrt(144)
  12.0

  READY.
  >>> [x**2 for x in range(6)]
  [0, 1, 4, 9, 16, 25]
```

Les variables et les imports sont conservés pendant toute la session dans un espace de noms partagé. Utilisez `NEW` pour les réinitialiser.

```
  READY.
  >>> nom = "PyPortal"
  READY.
  >>> print("Bonjour depuis", nom)
  Bonjour depuis PyPortal
```

---

# 6. PROGRAMMES D'EXEMPLE

---

## Programme 1 — Bonjour, Monde !

```
  10 print("*" * 32)
  20 print("*  Bonjour depuis BasicPython !  *")
  30 print("*" * 32)
```

**Pour l'essayer :**
```
  >>> 10 print("*" * 32)
  >>> 20 print("*  Bonjour depuis BasicPython !  *")
  >>> 30 print("*" * 32)
  >>> RUN
  ********************************
  *  Bonjour depuis BasicPython !  *
  ********************************
```

---

## Programme 2 — Compte à rebours

```
  10 import time
  20 for i in range(10, 0, -1):
  30   print(i)
  40   time.sleep(1)
  50 print("DECOLLAGE !")
```

**Pour l'essayer :**
```
  >>> NEW
  >>> 10 import time
  >>> 20 for i in range(10, 0, -1):
  >>> 30   print(i)
  >>> 40   time.sleep(1)
  >>> 50 print("DECOLLAGE !")
  >>> RUN
  10
  9
  ...
  1
  DECOLLAGE !
```

---

## Programme 3 — Tableau de bord système

```
  10 import os, gc
  20 gc.collect()
  30 st = os.statvfs("/")
  40 libre_ko = (st[3] * st[0]) // 1024
  50 ram_ko   = gc.mem_free() // 1024
  60 print("Flash libre :", libre_ko, "Ko")
  70 print("RAM libre   :", ram_ko,   "Ko")
  80 u = os.uname()
  90 print("Carte       :", u.machine)
```

---

## Programme 4 — Clignotement de la LED intégrée

```
  10 import board, digitalio, time
  20 led = digitalio.DigitalInOut(board.LED)
  30 led.direction = digitalio.Direction.OUTPUT
  40 for i in range(10):
  50   led.value = True
  60   time.sleep(0.5)
  70   led.value = False
  80   time.sleep(0.5)
  90 print("Termine !")
```

---

## Programme 5 — Sauvegarder une note dans la flash

```
  10 note = "Penser a mettre a jour le firmware !"
  20 with open("/note.txt", "w") as f:
  30   f.write(note)
  40 print("Note sauvegardee.")
```

Après exécution, relisez-la avec :
```
  READY.
  >>> CAT /note.txt
  Penser a mettre a jour le firmware !
```

---

## Programme 6 — Générateur de table de multiplication

```
  10 print("Table de multiplication")
  20 print("-" * 40)
  30 for i in range(1, 11):
  40   ligne = ""
  50   for j in range(1, 11):
  60     ligne += str(i*j).rjust(4)
  70   print(ligne)
```

---

# 7. MESSAGES D'ERREUR

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  Message d'erreur                 Cause                          │
  ├──────────────────────────────────────────────────────────────────┤
  │  Runtime error: <msg>             Exception pendant RUN          │
  │  Error: <msg>                     Exception pendant une commande  │
  │  Save error: <msg>                Impossible d'écrire (disque ?) │
  │  Load error: <msg>                Fichier introuvable            │
  │  Line must be >= 1                Numéro de ligne < 1 saisi      │
  │  Line out of range (1 - N)        DEL avec un numéro invalide    │
  │  Usage: <commande> <args>         Mauvaise syntaxe d'une commande│
  │  !!! CardKB not found             CardKB absent à l'adresse 95   │
  └──────────────────────────────────────────────────────────────────┘
```

---

# 8. ANNEXE — COMPATIBILITÉ CIRCUITPYTHON

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  Module          Fonction utilisée      Disponible en CP         │
  ├──────────────────────────────────────────────────────────────────┤
  │  os              chdir, getcwd          7.x, 8.x ✓               │
  │  os              mkdir, rmdir           7.x, 8.x ✓               │
  │  os              remove, rename         7.x, 8.x ✓               │
  │  os              stat, listdir          7.x, 8.x ✓               │
  │  os              statvfs                7.x, 8.x ✓               │
  │  os              uname                  7.x, 8.x ✓               │
  │  gc              collect, mem_free      7.x, 8.x ✓               │
  │  gc              mem_alloc              7.x, 8.x ✓               │
  │  microcontroller cpu.frequency          7.x, 8.x ✓               │
  │  microcontroller cpu.temperature        7.x, 8.x ✓ (peut = None) │
  │  microcontroller reset()               7.x, 8.x ✓               │
  │  busio           I2C                    7.x, 8.x ✓               │
  └──────────────────────────────────────────────────────────────────┘
```

> Les littéraux numériques avec underscore (ex. `1_000_000`) ne sont supportés
> qu'à partir de CircuitPython 7.2. BasicPython v0.04 utilise `1000000` pour
> la compatibilité avec toutes les versions CircuitPython 7.x.

---

## HISTORIQUE DES VERSIONS

```
  v0.01  oct. 2021  Portage initial sur PyPortal Titano
  v0.02  oct. 2021  Compatibilité WIO Terminal
  v0.03  oct. 2021  Touches fléchées : ↑↓ historique, ←→ édition
  v0.04  mai  2026  Corrections de bugs :
                      - cd : os.chdir() au lieu de os.getcwd(path)
                      - dir : ne plante plus sans argument
                      - backspace / insert en ligne réécrit
                      - _is_dir() via os.listdir() (plus robuste)
                      - ver : utilise os.uname() pour infos précises
                      - cpu.temperature : gère le retour None
                    Nouvelles commandes :
                      new, cat, mkdir, rmdir, cp, mv, del, renum,
                      mem, df, ver
                    Helpers ANSI extraits
                    Manuel utilisateur complet (EN + FR)
```

---

```
  ┌───────────────────────────────────────────────────────────┐
  │  BasicPython v0.04 — (c) 2021-2026 @beboxos              │
  │  Basé sur le travail original de Scott Shawcroft         │
  │  https://github.com/tannewt/basicpython                  │
  │  https://twitter.com/beboxos                             │
  └───────────────────────────────────────────────────────────┘
```
