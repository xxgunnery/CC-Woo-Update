#import matplotlib.pyplot as plt
#import numpy as np

'''

MUST BE AT 110% ZOOM ON EDGE BROWSER FOR THIS TO WORK

'''


import cv2 as cv
import pyautogui as bot
import pytesseract as tess
import csv

########## CONFIGURE EXTRA RESOURCES ################

### Interval between pyautogui commands is .4 seconds
bot.PAUSE =  0.25

### pytesseract required code
tess.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
from PIL import Image

######################################################   BEGIN CODE   ###################################################################

### JOB WIDE VARIABLE DEFINITIONS
productCodesCOMP = []

imLocations = ['Images/topRef.png', 'Images/midRef.png', 'Images/bottomRefChange.png']
sXVals= [-200, 205, -81]
yCalc = -23 - 450
sYVals = [40, 100, yCalc]
scrollLength = [0, -200, -275]
scrollInit = "FALSE"

def editProducts(idsCSV, stockCSV, priceCSV, scroll):
    refImage = cv.imread('Images/numPagesRef.png')
    refPoint = bot.locateCenterOnScreen(refImage)
    if refPoint is None:
        refImage = cv.imread('Images/numPagesRef2.png')
        refPoint = bot.locateCenterOnScreen(refImage)

    ### Calculate the location of the first variation based on the top page reference
    startPointX = refPoint[0] + 15
    startPointY = refPoint[1] - 30

    boxLength = 60
    boxWidth = 30

    ### Take screenshot of WooCommerce screen.
    bot.screenshot("Images/numPages.PNG", region=(startPointX, startPointY, boxWidth, boxLength) ) # Region =  Left, Top, Width, Height
    im1 = cv.imread("Images/numPages.PNG")

    gray_image = cv.cvtColor(im1, cv.COLOR_BGR2GRAY)
    threshold_img = cv.threshold(gray_image, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)[1]

    #cv.imshow('Result', threshold_img)
    #cv.waitKey(0)

    numPagesBoxes = tess.image_to_boxes(threshold_img)

    numPages = 0
    lastCharCheck = ""
    count = 0
    for box in numPagesBoxes.splitlines():
        if(lastCharCheck == "f"):
            numPages = int(box[0])
            break
        if(box[0] == 'f'):
            lastCharCheck = "f"

    #num = 0
    #while(num < 1):
    num = 0
    while(num < numPages):

        if(num > 0):
            bot.scroll(475)
        
        bot.move(20, 20, 0.5)

        scNum = 0
        scTot = len(imLocations)
        while(scNum < scTot):
            if(scroll == "TRUE"):
                bot.scroll(scrollLength[scNum])
            scroll = "FALSE"

            imLoc = imLocations[scNum]
            sX = sXVals[scNum]
            sY = sYVals[scNum]

            print(imLoc)
            print(scNum)

            if(imLoc == 'Images/topRef.png'):
                ### Find reference on screen for top of page
                refImage = cv.imread(imLoc)
                refPoint = bot.locateCenterOnScreen(refImage)
                if refPoint is None:
                    refImage = cv.imread('Images/topRef2.png')
                    refPoint = bot.locateCenterOnScreen(refImage)
                    print(refPoint)
            elif(imLoc == 'Images/bottomRefChange.png'):
                ### Find reference on screen for top of page
                refImage = cv.imread(imLoc)
                refPoint = bot.locateCenterOnScreen(refImage)
                if refPoint is None:
                    refImage = cv.imread('Images/bottomRefNone.png')
                    refPoint = bot.locateCenterOnScreen(refImage)
                    if refPoint is None:
                        refImage = cv.imread('Images/bottomRefAlt3.png')
                        refPoint = bot.locateCenterOnScreen(refImage)
            else:
                refImage = cv.imread(imLoc)
                refPoint = bot.locateCenterOnScreen(refImage)

            ### Calculate the location of the first variation based on the top page reference
            startPointX = refPoint[0] + sX
            startPointY = refPoint[1] + sY

            boxLength = 450
            boxWidth = 52

            ### Take screenshot of WooCommerce screen.
            bot.screenshot("Images/workingShot.PNG", region=(startPointX, startPointY, boxWidth, boxLength) ) # Region =  Left, Top, Width, Height
            im1 = cv.imread("Images/workingShot.PNG")
            #cv.imshow('Result', im1)
            #cv.waitKey(0)

            ### Convert screenshot to tesseract boxes
            boxes = tess.image_to_boxes(im1)

            productCode = ""     # String representing the product code seamed together by loop
            productCodes = []    # List of all product codes
            absY = []            # List of absolute Y coordinates for each variation
            absX = []            # List of absolute X coordinates for each variation

            ### Extract the product codes from the screenshot by stitching together pytesseract boxes
            count = 0
            for box in boxes.splitlines():
                box = box.split(' ')
                char = box[0]
                productCode += char

                # Increase the count by 1 to show list position
                count += 1

                # If count is 1, then it is the first number in the item code. Take the x,y position. If it is 6, then reset count to 0 so that we can find the first number in the new item code.
                if(count == 1):
                    x, y = int(box[1]), int(box[2])
                    absX.append(startPointX + boxWidth + x)
                    absY.append(startPointY + boxLength - y)
                elif(count == 6):
                    count = 0
                    productCodes.append(productCode)
                    productCode = ""
            print("       ")
            print("ALL PRODUCT CODES SELECTED FOR " + imLoc)
            print(productCodes)
            print("       ")

            numVariations = len(productCodes)
            index = numVariations - 1

            i = 0
            while i < numVariations:

                ### Obtain index of the first product needed to update pricing and stock value with the new values
                currentCode = productCodes[i]
                if(currentCode in productCodesCSV):
                    csvIndex = productCodesCSV.index(currentCode)
                else:
                    scNum = scTot
                    break

                price = productPriceCSV[csvIndex]
                stock = productStockCSV[csvIndex]
                if(stock == "In Stock"):
                    moveDown = 40
                else:
                    moveDown = 65

                ### Move to the first box and expand it
                bot.moveTo(absX[i] + 700, absY[i], .25)
                bot.click()

                ### Move to price box and set price
                priceImage = cv.imread('Images/pricePic.png')
                pricePoint = bot.locateCenterOnScreen(priceImage)
                bot.moveTo(pricePoint[0], pricePoint[1] + 36, .25)
                bot.click()
                bot.typewrite(["backspace", "backspace", "backspace", "backspace", "backspace", "backspace"])
                bot.typewrite(price)
                
                ### Move to Stock box and set in stock/out of stock
                stockImage = cv.imread('Images/stockPic.png')
                stockPoint = bot.locateCenterOnScreen(stockImage)

                if(absY[i] > 600):
                    #print("Y POSITION WHEN EXITED FOR " + imLoc)
                    #print(absY[i])
                    #print("       ")

                    if(absY[i] < 630):
                        bot.moveTo(stockPoint[0], stockPoint[1] + 25, .1)
                        bot.click()
                        bot.move(0, moveDown, .1)
                        bot.click()
                    else:
                        if(stock == "In Stock"):
                            moveDown = 65
                        else:
                            moveDown = 40

                        bot.moveTo(stockPoint[0], stockPoint[1] + 25, .1)
                        bot.click()
                        bot.move(0, -moveDown, .1)
                        bot.click()

                    ### Close down the box
                    bot.moveTo(absX[i] + 700, absY[i], .25)
                    bot.click()
                    bot.move(0, 20, .25)
                    productCodesCOMP.append(currentCode)

                    i = numVariations
                    scroll = "TRUE"

                    #print("ALL PRODUCT CODES COMPLETED FOR " + imLoc)
                    #print(productCodesCOMP)
                    #print("       ")
                    #print("----------")
                    #print("----------")
                else:
                    bot.moveTo(stockPoint[0], stockPoint[1] + 25, .1)
                    bot.click()
                    bot.move(0, moveDown, .1)
                    bot.click()

                    ### Close down the box
                    bot.moveTo(absX[i] + 700, absY[i], .25)
                    bot.click()

                    productCodesCOMP.append(currentCode)
                    if(currentCode == productCodes[index]):
                        i = numVariations
                        bot.move(0, 20, .25)
                    else:
                        i += 1

            scNum += 1

        ### Find save button and then save changes
        ref1 = 'Images/bottomRefChange.png'
        ref2 = 'Images/bottomRefNone.png'
        ref3 = 'Images/refImg3.png'

        refImage = cv.imread(ref1)
        refPoint = bot.locateCenterOnScreen(refImage)
        if(refPoint is None):
            refImage = cv.imread(ref3)
            refPoint = bot.locateCenterOnScreen(refImage)
            if(refPoint is None):
                refImage = cv.imread(ref2)
                refPoint = bot.locateCenterOnScreen(refImage)
                bot.moveTo(refPoint[0], refPoint[1], .25)
                bot.click()
            else:
                bot.moveTo(refPoint[0], refPoint[1], .25)
                bot.click()
        else:
            bot.moveTo(refPoint[0], refPoint[1], .25)
            bot.click()

        refImage = cv.imread('Images/nextArrow.png')
        refPoint = bot.locateCenterOnScreen(refImage)
        if(not (refPoint is None)):
            bot.moveTo(refPoint[0], refPoint[1], 10)
            bot.click()
        
        print("----------")
        print("       ")
        print("ALL PRODUCT CODES COMPLETED:")
        print(productCodesCOMP)
        print("       ")
        print("----------")

        num += 1
        

productCodesCSV = []      # List to hold product codes in CSV file
productStockCSV = []      # List to hold stock in CSV file
productPriceCSV = []      # List to hold prices in CSV file

fileList = ['CSVs/WooUpdate - RegBB.csv', 'CSVs/WooUpdate - IncBB.csv', 'CSVs/WooUpdate - DryBB.csv']

with open(fileList[2]) as f:
    data = csv.reader(f)
    for row in data:
        if(row[0] != "ID"):
            productCodesCSV.append(row[0])
        if(row[4] != "In Stock?"):
            productStockCSV.append(row[4])
        if(row[5] != "Price"):
            productPriceCSV.append(row[5])

editProducts(productCodesCSV, productStockCSV, productPriceCSV, scrollInit)

print("Complete!!!!!!")




