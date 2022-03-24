<h1>Pimoroni Badger2040 </h1>

BadgerOS port (and enhancement) to CircuitPython from the original Pimoroni MicroPython version.<cr/>
<cr/>
The question is, why?<cr/>

Micropython is great but not friendly to the public. CircuitPython is better for that:<cr/>

Mount the device as a USB drive, then you can manage it by just dragging and dropping files (eg a badge text file).<cr/>

video démo on youtube : [clic on this link ](https://www.youtube.com/watch?v=mA5UjWe_tYo "clic on this link ")

[usefull electronic sheme](https://cdn.shopify.com/s/files/1/0174/1800/files/badger_2040_schematic.pdf?v=1645702148)

![anim](pics/badgeranim.gif)

## Update March 24, 2022:

Version 1.0 .
From now on, you don't need to edit the keyboard language in the code, everything is done from the "prefs" menu where you can choose the French AZERTY (PC only) or US (QWERTY) layout.

Added icons in the top bar that indicate which layout is active (US or FR) as well as whether the device is connected to the USB or not (to avoid slowdowns when not connected to the usb, the test is done at boot time and when you go to the Keyb menu)

the batteries level and voltages are working.

Note (following an issue): to start the badge in battery mode (issue related to circuitpython for the moment may be repaired in future releases) you must press for about 10 to 20 seconds on one of the five buttons (the LED flashes 3 times, then once after). On battery if you press reset the badge does not restart and remains in standby, so it must be restarted with the button as I just described.

## Update March 22, 2022:

Added QRcode functions on badges. When displaying a badge, press the bottom arrow to replace the photo with a QRcode (.vcf format) compatible with all mobiles. Look at the example text files to see the format, but the new format is (one field per line):

- company
- name
- detail1_title
- detail1_text
- detail2_title
- detail2_text
- Work phone number
- Cell phone number
- email
- Web site link

If you have no information to input, leave the line blank.

Other addition (Beta): battery voltage in the bar. In the next update, the battery logo will be updated. I still have to find the high and low limits of the battery, but as the epaper does not consume almost anything, it may take me a while.

Added at 11 o'clock: bug fixes, and battery level beta version shows correct icon value and voltage in top bar.

## Update March 21, 2022:

A big thank you to Chris Parrott for his help. We can now set the 3V3 (GPIO10) pin to high. 
Fixed a bug where the HID was crashing at boot if not connected to the USB (logical). Now during boot we test if connected or not to the USB to disable the HID features (to reactivate reboot).

Warning: on battery power, press a button for about 20 sec to wake up the badge to put it in standby and save battery. Press reset. The badge will wake up by itself if you connect it to USB.

## Update March 17, 2022:

The code has been rewritten to take into account the use of Adafruit DisplayIO libraries (with management of texts, 4-bit black & white BMP images, and also shapes). For the moment I haven't activated the battery display (I have a problem on my badger, it doesn't seem to work on battery and I haven't found yet why (maybe my device has a defect).

## TODO: 

Management of the battery level. (beta version 22.03.2022)

~~the "info" part~~ : done 17.03.2022<cr/>

The "prefs" part to set (in the non volatile memory) the HID parameters for the moment hard-coded in the code with `layout = fr` or `layout = us`.<cr/>

Code the list function as in the original Micropython version.<cr/>

------------

# User's Manual : 

## # Create a badge:

It's quite simple in the "badges" folder just create a text file (with Notepad for example) for the structure. Look at the `empty.txt` file in this directory but it gives this (one information per line):

- company
- name
- detail1_title
- detail1_text
- detail2_title
- detail2_text
- Work phone number (only showed in Qrcode)
- Cell phone number (only showed in Qrcode)
- email             (only showed in Qrcode)
- Web site link     (only showed in Qrcode)

And for the photo, from, for example, the freeware app "[paint.net](https://www.getpaint.net/download.html "paint.net")" you have to make a 104x128-pixel image and save it in 4-bit BMP format.
 
## # Create a HID/rubber ducky command

This function allows your Badger2040 to behave like a keyboard and send text keystrokes when connected to a computer (useful in pentesting campaigns for red teams, but we'll come back to this a little bit later).

For more information about rubber ducky scripts, [click on this link.](https://docs.hak5.org/usb-rubber-ducky-1/the-ducky-script-language/ducky-script-quick-reference "click on this link.")

To make your own, nothing simpler: in a text editor create a text file in the "hid" directory and at the next reset it will appear in the available scripts. Press the button to launch the script.

A "hidden" hid function is present: at boot time if you hold one of the 5 buttons (a, b, c, up, down) before changing the display (which allows to keep the display unchanged) it will execute at the root the corresponding script when you release the button (the led stays on and turns off once the script is executed).

Button-Script equivalence:

- button a -> run a.txt
- button b -> run b.txt
- button c -> run c.txt
- button up -> run up.txt
- button down -> runs down.txt

The program executes them in this order. If you are fast enough you can execute for example a then c then down (it allows to prepare several fights).

Once executed the badge will wait for a button press to continue to the Launcher (the LED flashes while waiting). That allows you to disconnect the badge without the display being changed (useful within the framework of a red team intrusion: the badge continues to display an identity for example). It is more discrete and easy to pass as innocuous than a USB key rubber ducky.

## # Display an image 

Nothing could be simpler: copy in the "images" directory your images, 296x128 pixels in 4-bit BMP format (black and white). At the next reset they will be available in the menu.

## # Ebook function (.txt reader)

Simply copy your .txt file to the ebook directory and at the next reset it will be available in the menu.
