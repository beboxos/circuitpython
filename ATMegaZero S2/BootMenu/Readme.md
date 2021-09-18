<h1>Boot Menu Application Laucher</h1>

![imame](./pic.png)

Here is my very simple Application launcher in circuitpython inspired from my launcher for PyPortal Titano.
This boot menu can easyly ported to other car, il only need at least 2 buttons (up/down and both are used to validate).
in the code you can adjust parameters for your device :
* maxlines
* mawcols
* item per page

All is automatised, script scan root of the card for .py files and build a menu to choose the file tu run on next reset, then reset the card.
I added an hardware test file to test buttons etc of [Adafruit Mini PiTFT 1.13"(240x135)](https://www.adafruit.com/product/4393)

if case stl interest you, you can find it [on my Thingiverse](https://www.thingiverse.com/thing:4967980) case is designed for [UPS-Lite](https://fr.aliexpress.com/item/1005002389127372.html) + [ATMegaZero S2](https://atmegazero.com/#/atmegazero_esp32s2_overview) + [Adafruit Mini PiTFT 1.13"(240x135)](https://www.adafruit.com/product/4393)
