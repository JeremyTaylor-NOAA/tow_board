#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import datetime
import random
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

print(f"picdir: {picdir}")
print(f"libdir: {libdir}")
#exit()

import logging
from waveshare_epd import epd3in52
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

# Define the heart shape
def draw_heart(draw, x, y, size, color):
    # Left curve
    draw.arc((x, y - (size/2), x + size, y + (size/2)), 180, 360, fill=color)
    draw.pieslice((x, y - (size/2), x + size, y + (size/2)), 180, 360, fill=color)
    # Right curve
    draw.arc((x + size, y - (size/2), x + 2 * size, y + (size/2)), 180, 360, fill=color)
    draw.pieslice((x + size, y - (size/2), x + 2 * size, y + (size/2)), 180, 360, fill=color)
    # Bottom triangle
    draw.polygon([(x, y), (x + size, y + size), (x + 2 * size, y)], fill=color)

def map_value(value, from_min, from_max, to_min, to_max):
    """Maps a value from one range to another."""
    return int((value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min)

try:
    logging.info("Tow board display")
    
    epd = epd3in52.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.display_NUM(epd.WHITE)
    epd.lut_GC()
    epd.refresh()

    epd.send_command(0x50)
    epd.send_data(0x17)
    time.sleep(2)
    
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font44 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 44)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    font40 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 40)
    font60 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 60)
    
    # Drawing on the Horizontal image
    Depth_header = "Depth:"
    Depth_reading = 31
    now = datetime.datetime.now()
    start_time = now
    mission_length_secs = 1 * 60
    incoming_message = "Are you OK?"
    options = "1. YES  2. NO"
    responce = "Acknowledged!"
    responce = "NO...Ending dive!"
    responce = "YES...Just checking!"

    logging.info("1.Drawing on the Horizontal image...")
    Himage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    draw.text((epd.height - 120, epd.width - 45), f"{Depth_header} {Depth_reading}", font = font24, fill = 0)
    draw_heart(draw, 6, epd.width - 35, 15, 0)

    draw.text((10, 0), incoming_message, font = font44, fill = 0)
    draw.text((10, 60), options, font = font44, fill = 0)
    draw.text((100, epd.width - 45), f"{now.strftime('%H:%M:%S')}", font = font24, fill = 0)

    draw.rectangle((20, epd.width - 15, epd.height - 20, epd.width - 5), outline = 0)
    epd.display(epd.getbuffer(Himage))
    epd.lut_GC()
    epd.refresh()
    time.sleep(1)
    


    print("Quick refresh is supported, but the refresh effect is not good, but it is not recommended")
#    Himage = Image.open(os.path.join(picdir, '3in52-2.bmp'))
    for i in range(15):
        
        #erase previous draw
        draw.text((100, epd.width - 45), f"{now.strftime('%H:%M:%S')}", font = font24, fill = 1)
        draw_heart(draw, 6, epd.width - 35, 15, 1)
        draw.text((epd.height - 120, epd.width - 45), f"{Depth_header} {Depth_reading}", font = font24, fill = 1)
#        epd.display(epd.getbuffer(Himage))
#        epd.lut_DU()
#        epd.refresh()
 
        draw.text((10, 120), responce, font = font40, fill = 0)

        if random.randint(1, 2) == 1:
            Depth_reading -= 1
        else:
            Depth_reading += 1
        now = datetime.datetime.now()
        draw_heart(draw, 6, epd.width - 35, 15, 0)
        draw.text((100, epd.width - 45), f"{now.strftime('%H:%M:%S')}", font = font24, fill = 0)
        difference = now-start_time
        difference_in_secs = int(difference.total_seconds())
        goto_length = map_value(difference_in_secs,0,mission_length_secs,0,epd.height - 20 - 20)
        print(f"diff: {difference_in_secs}, {epd.height - 20 - 20}, {goto_length}")
        draw.text((epd.height - 120, epd.width - 45), f"{Depth_header} {Depth_reading}", font = font24, fill = 0)
        if difference_in_secs < mission_length_secs:
            draw.rectangle((20, epd.width - 15, 20 + goto_length, epd.width - 5), fill = 0)
        else: 
            draw.rectangle((20, epd.width - 15, 340, epd.width - 5), fill = 0)

        epd.display(epd.getbuffer(Himage))
        epd.lut_DU()
        epd.refresh()
#        epd.sleep()
        time.sleep(4)

    # Himage = Image.open(os.path.join(picdir, '3in52-3.bmp'))
    # epd.display(epd.getbuffer(Himage))
    # epd.lut_DU()
    # epd.refresh()
    # time.sleep(2)


#    logging.info("Clear...")
#    epd.Clear()
    
    logging.info("Goto Sleep...")
    epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd3in52.epdconfig.module_exit(cleanup=True)
    exit()
