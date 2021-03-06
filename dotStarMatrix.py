import board
#import adafruit_dotstar as dotstar
import neopixel
from PIL import Image,ImageDraw,ImageFont
import cv2

from time import sleep, time


width = 32
height = 8 
fps = 24

def writeFrame(dots, image):
    for x in range(0,width):
        for y in range(0,height):
            if(x%2==1):  
                dots[x*height+(7-y)] = image[y][x]    
            else:
                dots[x*height+y] = image[y][x] 
    dots.show()       

    

class DotStarMatrix:

    def __init__(self, width, height, syncPin, dataPin, brightness):
        self.width = width
        self.height = height
        ORDER = neopixel.GRB
        self.pannelNumber = 2
        self.line = 2
        self.scrollOffset = 10
        

        self.dots = neopixel.NeoPixel(
            board.D21, width*height*self.pannelNumber*self.line, brightness=brightness, auto_write=False, pixel_order=ORDER
        ) 
        #dotstar.DotStar(syncPin, dataPin, width*height, brightness=brightness, auto_write=False)

    def clear(self):
        self.dots.fill(0)
        self.dots.show()
    
    def writePilImage(self, image):
        pix = image.load()
        for x in range(0,self.width):
            for y in range(0,self.height):
                try:
                    if(x%2==1):  
                        self.dots[x*self.height+((self.height-1)-y)] = pix[x,y]    
                    else:
                        self.dots[x*self.height+y] = pix[x,y]
                except:
                    self.dots[x*self.height+y] = (0,0,0)
        self.dots.show() 

    def writePilImage(self, image, pannel, line):
        pix = image.load()
        for x in range(0,self.width):
            for y in range(0,self.height):
                try:
                    if(x%2==1):  
                        self.dots[(
                            (line*self.pannelNumber*self.height*self.width)+
                            (pannel*self.height*self.width)+
                            x*self.height
                            +((self.height-1)-y))] = pix[x,y]    
                    else:
                        self.dots[(
                            (line*self.pannelNumber*self.height*self.width)+
                            (pannel*self.height*self.width)+
                            x*self.height+y)] = pix[x,y]
                except:
                    self.dots[(
                        (line*self.pannelNumber*self.height*self.width)+
                        (pannel*self.height*self.width)
                        +x*self.height+y)] = (0,0,0)
        self.dots.show() 
        
    def writeOpenCVFrame(self, frame):
        for x in range(0,self.width):
            for y in range(0,self.height):
                if(x%2==1):  
                    self.dots[x*self.height+((self.height-1)-y)]  = frame[y][x]    
                else:
                    self.dots[x*self.height+y] = frame[y][x] 
        self.dots.show()   
        
    def writeMovie(self, path):
        vidcap = cv2.VideoCapture(path)
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        success,frame = vidcap.read()
        lastTime = 0

        while success:   
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            while(time()-lastTime<1/fps):
                time()
            self.writeOpenCVFrame(frame)
            lastTime = time()
            success,frame = vidcap.read()            
    
    def writeImageFromPath(self, path):
        im = Image.open(path) # Can be many different formats.
        self.writePilImage(im)   
        
    def scrollText(self, text, font, color, scrollDelay):
        sizeTxt = font.getsize(text)
        mask = font.getmask(text, "1")
        mask.save_ppm("temp.ppm")
        mask = Image.open("temp.ppm")

        for i in range(0, sizeTxt[0]*-1-2, -1):
            picture = Image.new("RGB", (self.width, self.height))
            pictureMask = Image.new("L", (self.width, self.height))
            picture1 = Image.new("RGB", (self.width, self.height),color)
            pictureMask.paste(mask,(i,0))
            picture.paste(picture1,(0,0),pictureMask)
            print("one")

            self.writePilImage(picture)
            

            sleep(scrollDelay)
    def resetScroll(self):
        self.scrollOffset = 10
        
    def scrollTextWithPicture(self, text, font, color, scrollDelay, path, scroll, line):
        im = Image.open(path)
        pix = im.load()

        if text == None:
            text = " "
                    
        sizeTxt = font.getsize(text)
        maskImagingCore = font.getmask(text, "1")

        mask = Image.new("L", maskImagingCore.size)

        for x in range(0, maskImagingCore.size[0]):
            for y in range(0, maskImagingCore.size[1]):
                coord = (x,y)
                mask.putpixel(coord,maskImagingCore.getpixel(coord))
        
        if sizeTxt[0] > 64-6 and scroll == True:

            #for i in range(0, sizeTxt[0]*-1-2, -1):
            #    picture = Image.new("RGB", (self.width, self.height))
            #    pictureMask = Image.new("L", (self.width, self.height))
            #    picture1 = Image.new("RGB", (self.width, self.height),color)
            #    pictureMask.paste(mask,(i,0))
            #    picture.paste(picture1,(6,0),pictureMask)
            #    picture.paste(im,(0,0))
            #    print("one")
            #    self.writePilImage(picture)
            #    sleep(scrollDelay)

            if self.scrollOffset > 0:
                innerScrollOffset = 0
            else:
                innerScrollOffset = self.scrollOffset

            for i in range(0,self.pannelNumber):
                picture = Image.new("RGB", (self.width, self.height))
                pictureMask = Image.new("L", (self.width, self.height))
                picture1 = Image.new("RGB", (self.width, self.height),color)
                
                if(i == 0):
                    pictureMask.paste(mask,(6+innerScrollOffset,0))
                else:
                    pictureMask.paste(mask,(-32+6+innerScrollOffset,0))             
                
                picture.paste(picture1,(0,0),pictureMask)

                if(i == 0):
                    picture.paste(im,(0,0))
                
                self.writePilImage(picture, i, line)
            
            self.scrollOffset -= 1
            if self.scrollOffset < sizeTxt[0]*-1-2:
                self.scrollOffset = 10

        else:
            for i in range(0,self.pannelNumber):
                picture = Image.new("RGB", (self.width, self.height))
                pictureMask = Image.new("L", (self.width, self.height))
                picture1 = Image.new("RGB", (self.width, self.height),color)
                
                if(i == 0):
                    pictureMask.paste(mask,(6,0))
                else:
                    pictureMask.paste(mask,(-32+6,0))             
                
                picture.paste(picture1,(0,0),pictureMask)

                if(i == 0):
                    picture.paste(im,(0,0))
                
                self.writePilImage(picture, i, line)
                
            

    
    


