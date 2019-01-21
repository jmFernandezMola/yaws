#!/usr/bin/env python

from PIL import ImageFont
import sys

import inkyphat
import time


def plotData(text):
    inkyphat.set_colour("black")
    font_file = inkyphat.fonts.FredokaOne
    top = 0
    left = 0

#clean!
    for x in range(inkyphat.WIDTH):
        for y in range(inkyphat.HEIGHT):
            inkyphat.putpixel((x, y), inkyphat.WHITE)
#    inkyphat.show()

    bigTitle = "Last data aquired"
    font = inkyphat.ImageFont.truetype(font_file, 18)
    width, height = font.getsize(bigTitle)
    inkyphat.text((0, top), bigTitle, 1, font=font)
    top += (height/2) + 1
    index = 0;
    for items in text:
        font = inkyphat.ImageFont.truetype(font_file, 14)
        width, height = font.getsize(items)
        if (index%3) == 0:
	    top += height + 1
	    left = 0
	    left_offset = width + 2
	else:
	    left = left_offset 
	    left_offset = left + width + 2
 	inkyphat.text((left, top), items, 1, font=font)
	index += 1
    
    font = inkyphat.ImageFont.truetype(font_file, 12)
    timeNow = time.strftime('%d/%m/%Y %H:%M')
    width, height = font.getsize(timeNow)
    inkyphat.text(( inkyphat.WIDTH - width, inkyphat.HEIGHT - height), timeNow, 1, font=font)
    inkyphat.show()




