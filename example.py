from dotStarMatrix import DotStarMatrix

from time import sleep
import board
from PIL import ImageFont

font = ImageFont.truetype('../z-arista/Arista2.0 light.ttf', 8)

matix = DotStarMatrix(32, 8, board.D6, board.D5, 1)

#matix.writeImageFromPath("test.png")

sleep(5)

matix.scrollText("hello world", font, (12, 85, 12), 0.05)

#sleep(5)

#matix.writeMovie("test.mp4")

