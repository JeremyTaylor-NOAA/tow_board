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

class Epaper:
    def __init__(self):
        logging.info("Tow board display init.....")
        self.epd = epd3in52.EPD()
        logging.info("init and Clear")
        self.epd.init()
        self.epd.display_NUM(self.epd.WHITE)
        self.epd.lut_GC()
        self.epd.refresh()
        self.epd.send_command(0x50)
        self.epd.send_data(0x17)
        time.sleep(2)
        self.Himage = Image.new('1', (self.epd.height, self.epd.width), 255)  # 255: clear the frame
        self.draw = ImageDraw.Draw(self.Himage)
        self.msg = dict(
            current_1="",
            x_1=10,
            y_1=0,
            font_1=ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 44),
            update_1=False,
            current_2="",
            x_2=10,
            y_2=60,
            font_2=ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 44),
            update_2=False,
            current_3="",
            x_3=10,
            y_3=120,
            font_3=ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 44),
            update_3=False
        )
        self.depth_m=0
        self.depth_font=ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        self.depth_x=self.epd.height - 120
        self.depth_y=self.epd.width - 45
        self.depth_header="Depth:"
        self.now = datetime.datetime.now()
        self.start_time = self.now
        self.mission_length_secs = 1 * 60
        self.track_time = self.now - self.start_time
        self.time_x = 100 #100
        self.time_y = self.epd.width - 45
        self.time_font=ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
  
    def shutdown(self):
        # logging.info("Goto Sleep...")
        # self.epd.sleep()
        logging.info("Shuting down e-paper...")
        epd3in52.epdconfig.module_exit(cleanup=True)

    def new_msg(self, msg = "", pos = 1):
        logging.info(f"New message: {msg}, pos:{pos}")
        self.draw.text((self.msg[f"x_{pos}"], self.msg[f"y_{pos}"]), self.msg[f"current_{pos}"], font = self.msg[f"font_{pos}"], fill = 1)
        self.draw.text((self.msg[f"x_{pos}"], self.msg[f"y_{pos}"]), msg, font = self.msg[f"font_{pos}"], fill = 0)
        self.msg[f"current_{pos}"]=msg

    def update_message(self):
        logging.info(f"Updateing message..Screen!")
        self.epd.display(self.epd.getbuffer(self.Himage))
#        self.epd.lut_GC()
        self.epd.lut_DU()
        self.epd.refresh()

    def draw_heart(self,x, y, size, color):
        
        logging.info(f"Drawing heart...")
        # Left curve
        self.draw.arc((x, y - (size/2), x + size, y + (size/2)), 180, 360, fill=color)
        self.draw.pieslice((x, y - (size/2), x + size, y + (size/2)), 180, 360, fill=color)
        # Right curve
        self.draw.arc((x + size, y - (size/2), x + 2 * size, y + (size/2)), 180, 360, fill=color)
        self.draw.pieslice((x + size, y - (size/2), x + 2 * size, y + (size/2)), 180, 360, fill=color)
        # Bottom triangle
        self.draw.polygon([(x, y), (x + size, y + size), (x + 2 * size, y)], fill=color)

    def update_depth(self,new_depth):
        logging.info(f"Updating depth: {new_depth}")
        self.draw.text((self.depth_x, self.depth_y), f"{self.depth_header} {self.depth_m}", font = self.depth_font, fill = 1)
        self.draw.text((self.depth_x, self.depth_y), f"{self.depth_header} {new_depth}", font = self.depth_font, fill = 0)
        self.depth_m = new_depth
   
    def update_time(self):
        logging.info(f"Updating time....")
        # Calculate hours, minutes, seconds from the timedelta object
        hours, remainder = divmod(self.track_time.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_time_difference = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        # self.draw.text((self.time_x, self.time_y), f"{self.now.strftime('%H:%M:%S')}", font = self.time_font, fill = 1)
        self.draw.text((self.time_x, self.time_y), f"{formatted_time_difference}", font = self.time_font, fill = 1)
        # self.now = datetime.datetime.now()
        self.track_time = datetime.datetime.now() - self.start_time
        # Calculate hours, minutes, seconds from the timedelta object
        hours, remainder = divmod(self.track_time.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_time_difference = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        # self.draw.text((self.time_x, self.time_y), f"{self.now.strftime('%H:%M:%S')}", font = self.time_font, fill = 0)
        self.draw.text((self.time_x, self.time_y), f"{formatted_time_difference}", font = self.time_font, fill = 0)

    def map_value(self, value, from_min, from_max, to_min, to_max):
        """Maps a value from one range to another."""
        return int((value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min)

    def update_track(self):
        logging.info(f"Updating track....")
        # difference = self.now-self.start_time
        # difference = int(self.track_time.total_seconds())
        # difference_in_secs = int(difference.total_seconds())
        # goto_length = self.map_value(difference_in_secs,0,self.mission_length_secs,0,self.epd.height - 20 - 20)
        goto_length = self.map_value(int(self.track_time.total_seconds()),0,self.mission_length_secs,0,self.epd.height - 20 - 20)
        # print(f"diff: {difference_in_secs}, {self.epd.height - 20 - 20}, {goto_length}, {int(self.track_time.total_seconds())}")
        print(f"diff: {int(self.track_time.total_seconds())}, {self.epd.height - 20 - 20}, {goto_length}, {int(self.track_time.total_seconds())}")
        self.draw.rectangle((20, self.epd.width - 15, self.epd.height - 20, self.epd.width - 5), outline = 0)
        # if difference_in_secs < self.mission_length_secs:
        if int(self.track_time.total_seconds()) < self.mission_length_secs:
            self.draw.rectangle((20, self.epd.width - 15, 20 + goto_length, self.epd.width - 5), fill = 0)
        else: 
            self.draw.rectangle((20, self.epd.width - 15, 340, self.epd.width - 5), fill = 0)

    def update_all(self):
        self.update_time()
        self.update_track()
        self.update_message()
            

test = Epaper()
test.update_time()
test.new_msg("Are you OK?",1)
test.new_msg("1. YES  2. NO",2)
test.new_msg("Waiting......",3)
test.draw_heart(6, test.epd.width - 35, 15, 0)
test.update_depth(30)
test.update_track()
test.update_message()
time.sleep(5)
test.update_time()
test.new_msg("Sounds good!",2)
test.new_msg("Message received.",3)
test.draw_heart(6, test.epd.width - 35, 15, 1)
test.update_depth(35)
test.update_track()
test.update_message()
time.sleep(5)
test.draw_heart(6, test.epd.width - 35, 15, 0)

for i in range(10):
    test.update_all()
    time.sleep(5)


test.shutdown()
exit()

print(f"Opps!")
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
