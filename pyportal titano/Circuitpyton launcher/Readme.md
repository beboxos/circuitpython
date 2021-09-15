# Circuitpython Launcher For Pyportal Titano

![Launcher](launcher.png)

Welcome to the Circuitpython launcher section.

This launcher can bring 8 pages of 8 programs, that is 64 entries.<br/>
It builds itself from the files present at the root of CIRCUITPY. <br/>
By default, the files code.py (itself) and secrets.py (no interest) are ignored (and calculator.py because it is a module of calculation for the calculator).<br/>
The limit of the file names is 24 characters (.py included) that is to say 21 characters because it stores in the non-volatile memory (in the 25 first bytes) the file name to be launched at the next reset.

If you want to exclude other files you can always add them in [code.py at line 121](https://github.com/beboxos/circuitpython/blob/a470852d9fb7b90fc01971e96d4b7b3bbc51355a/pyportal%20titano/Circuitpyton%20launcher/code.py#L121).

When you write your application to leave and return to the menu, it is enough to make a reset of your card for that 3 cases:

* press the reset button of your card
* turn off and on the power supply 
* import microcontroller and use the command microcontroller.reset()

You can see the examples I put to see microcontroller.reset() in action.

For some reason I don't get, it happens that some python script doesn't work and I am trying to understand why. <br/>
Several possible reasons: 

* the fact of calling them via the bone with exec(open()) poses a problem (I would have to see if there is a way to pass by an import
* unsupported characters in the file name 

possible / future improvements : 

* take into account the fact of navigating the menu via physical buttons (for devices without touch functions).

* read the files to launch from an SD card (for cards without much memory)

* the possibility to switch to landscape or portrait mode
