import board
import terminalio
import displayio
import vectorio
from adafruit_display_text import label

display = board.DISPLAY

# Set text, font, and color
title = "HELLO WORLD"
subtitle = "From CircuitPython"
font = terminalio.FONT
color = 0x000000

# Set the palette for the background color
palette = displayio.Palette(1)
palette[0] = 0xFFFFFF

# Add a background rectangle
rectangle = vectorio.Rectangle(pixel_shader=palette, width=display.width + 1, height=display.height, x=0, y=0)

# Create the title and subtitle labels
title_label = label.Label(font, text=title, color=color, scale=4)
subtitle_label = label.Label(font, text=subtitle, color=color, scale=2)

# Set the label locations
title_label.x = 20
title_label.y = 45

subtitle_label.x = 40
subtitle_label.y = 90

# Create the display group and append objects to it
group = displayio.Group()
group.append(rectangle)
group.append(title_label)
group.append(subtitle_label)

# Show the group and refresh the screen to see the result
display.show(group)
display.refresh()

# Loop forever so you can enjoy your message
while True:
    pass
