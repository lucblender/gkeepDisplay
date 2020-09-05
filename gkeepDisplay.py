from os import system, name 
import credential
import gkeepapi
from time import sleep
from enum import Enum

import RPi.GPIO as GPIO
import signal
import sys

from dotStarMatrix import DotStarMatrix

from time import sleep
import board
from PIL import ImageFont

font = ImageFont.truetype('../fontTest/pixelFJ8pt1__.TTF', 8)
matrix = DotStarMatrix(32, 8, board.D6, board.D5, 1)

class TaskLine:
    def __init__(self, text, checked, selected, indented):
        self.text = text
        self.checked = checked
        self.selected = selected
        self.indented = indented
        
        if self.checked:        
            self.picturePath = "ticked.png"
        else:
            self.picturePath = "unticked.png"
        
    def toString(self):
        if self.text == None:
            return ""
            
        notePrint = ""
        if self.selected:
            notePrint += "> "
        
        if self.indented:
            notePrint += "\t"
        if self.checked :
            notePrint += 'x '
        else:
            notePrint += 'o '
            
        if "http" in self.text:
            notePrint += "_website url_"        
        else:        
            notePrint += self.text
        return notePrint

class State(Enum):     
    MAINITEMS = 0    
    SUBITEMS = 1   

state = State.MAINITEMS

SELECT_BUTTON = 14
SELECT_LED = 15

DEVELOP_BUTTON = 18
DEVELOP_LED = 23

DOWN_BUTTON = 24
DOWN_LED = 25

UP_BUTTON = 8
UP_LED = 7

LINE_DISPLAY = 2


indexItem = 0
subIndexItem = 0

keep = gkeepapi.Keep()
keep.login(credential.mail, credential.password)
gnote = keep.get(credential.noteUUID)

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

def clear():   
    if name == 'nt': 
        _ = system('cls')   
    else: 
        _ = system('clear') 
        
def callback_select(channel):
    sleep(0.1)
    if(GPIO.input(channel)):
        global state
        global indexItem
        global subIndexItem
        global keep
        GPIO.output(SELECT_LED, GPIO.HIGH)
        sleep(0.1)
        GPIO.output(SELECT_LED, GPIO.LOW)
        if state == State.MAINITEMS:
            item = getUnIndented(gnote.items)[indexItem]
            item.checked = not item.checked
            for subitem in item.subitems:
                subitem.checked = item.checked 
            keep.sync()
            clear()
            printItems(getUnIndented(gnote.items))
        elif state == State.SUBITEMS:  
            item = gnote.items[indexItem+subIndexItem]
            item.checked = not item.checked
            keep.sync()
            clear()      
            printItems(getSubitems(getUnIndented(gnote.items),indexItem))
    

def callback_develop(channel):
    sleep(0.1)
    if(GPIO.input(channel)):
        global state
        global indexItem
        global subIndexItem
        clear()
        if state == State.MAINITEMS:
            state = State.SUBITEMS
            GPIO.output(DEVELOP_LED, GPIO.HIGH)     
            subIndexItem = 0        
            printItems(getSubitems(getUnIndented(gnote.items),indexItem))
        elif state == State.SUBITEMS:
            state = State.MAINITEMS
            GPIO.output(DEVELOP_LED, GPIO.LOW)   
            printItems(getUnIndented(gnote.items))

def callback_up(channel):
    sleep(0.1)
    if(GPIO.input(channel)):
        global indexItem
        global subIndexItem
        global gnote
        global state
        GPIO.output(UP_LED, GPIO.HIGH)
        sleep(0.1)
        GPIO.output(UP_LED, GPIO.LOW)    
        
        if state == State.MAINITEMS:
            if indexItem < len(getUnIndented(gnote.items)) - 1:
                indexItem += 1
            clear()
            printItems(getUnIndented(gnote.items))
        elif state == State.SUBITEMS:  
            if subIndexItem < len(getSubitems(getUnIndented(gnote.items),indexItem)) - 1:
                subIndexItem += 1
            clear()      
            printItems(getSubitems(getUnIndented(gnote.items),indexItem))

def callback_down(channel):
    sleep(0.1)
    if(GPIO.input(channel)):
        global indexItem
        global subIndexItem
        global gnote
        global state
        GPIO.output(DOWN_LED, GPIO.HIGH)
        sleep(0.1)
        GPIO.output(DOWN_LED, GPIO.LOW)
        
        if state == State.MAINITEMS:
            if indexItem != 0:
                indexItem -= 1
            clear()
            printItems(getUnIndented(gnote.items))     
        elif state == State.SUBITEMS:  
            if subIndexItem != 0:
                subIndexItem -= 1
            clear()      
            printItems(getSubitems(getUnIndented(gnote.items),indexItem))
    
 


def printItems(items):    
    global state    
    global indexItem    
    global subIndexItem
    global LINE_DISPLAY
    
    global matrix
    global font
        
    i = 0
    lines = []
    
    if state == State.MAINITEMS:
        index = indexItem                
    else:  
        index = subIndexItem
    
    for item in items:
        selected = False
        if i == index:
            selected = True
        lines.append(TaskLine(item.text, item.checked, selected, item.indented))
        i += 1
        
    while(len(lines)<LINE_DISPLAY):
        lines.append(TaskLine(None, False, False, False))
    
    if index+LINE_DISPLAY > len(lines):
        to_draw = lines[len(lines)-LINE_DISPLAY:len(lines)]
    else:
        to_draw = lines[index:index+LINE_DISPLAY]
        
    for line in to_draw:
        print(line.toString())

    index = 0

    for line in to_draw:
        
        if line.selected:
            color = (12, 85, 12)
        else:
            color = (3, 21, 3)

        matrix.scrollTextWithPicture(line.text, font, color , 0.05, line.picturePath, False, index)
        index += 1
        
def getSubitems(items, index):
    return [items[index]] + items[index].subitems
    

def getUnIndented(items):
    toReturn = []
    
    for item in items:
        if not item.indented:
            toReturn.append(item)
    
    return toReturn


if __name__ == '__main__':

    GPIO.setmode(GPIO.BCM)

    GPIO.setup(SELECT_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(DEVELOP_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(UP_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(DOWN_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)


    GPIO.setup(SELECT_LED, GPIO.OUT)
    GPIO.setup(DEVELOP_LED, GPIO.OUT)
    GPIO.setup(UP_LED, GPIO.OUT)
    GPIO.setup(DOWN_LED, GPIO.OUT)

    GPIO.output(SELECT_LED, GPIO.LOW)
    GPIO.output(DEVELOP_LED, GPIO.LOW)
    GPIO.output(UP_LED, GPIO.LOW)
    GPIO.output(DOWN_LED, GPIO.LOW)

    GPIO.add_event_detect(SELECT_BUTTON, GPIO.RISING, callback=callback_select, bouncetime=300)
    GPIO.add_event_detect(DEVELOP_BUTTON, GPIO.RISING, callback=callback_develop, bouncetime=300)
    GPIO.add_event_detect(UP_BUTTON, GPIO.RISING, callback=callback_up, bouncetime=300)
    GPIO.add_event_detect(DOWN_BUTTON, GPIO.RISING, callback=callback_down, bouncetime=300)
    
    signal.signal(signal.SIGINT, signal_handler)
    clear()
    printItems(getUnIndented(gnote.items))
     
    signal.pause()

