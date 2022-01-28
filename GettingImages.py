# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 16:55:00 2019

@author: Harshil
"""
from __future__ import print_function
from __future__ import division
import cv2 as cv
import numpy as np
import argparse
from tkinter import Tk,Canvas

from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk

'''
window = Tk()
window.geometry('1000x1000')
window.title('ImageLabeler')
canvas= Canvas(window,height=1000, width=1000)
canvas.grid(row=0,column=0, columnspan=8)
 '''

img=askopenfilename()

'''
img1=img
b,g,r=cv.split(img1)
img1=cv.merge((r,g,b))
im1 = Image.fromarray(img1) 
imgtk1 = ImageTk.PhotoImage(image=im1)
canvas.create_image(0,0, image=imgtk1,anchor="nw")

img2=cv.cvtColor(img, cv.COLOR_BGR2HSV)
im2 = Image.fromarray(img2)
imgtk2 = ImageTk.PhotoImage(image=im2)
canvas.create_image(500,500,image=imgtk2,anchor="nw")

img3=img2

'''

def Hist_and_Backproj(val):
    
    bins = val
    histSize = max(bins, 2)
    ranges = [0, 180] # hue_range
    
    
    hist = cv.calcHist([hue], [0], None, [histSize], ranges, accumulate=False)
    cv.normalize(hist, hist, alpha=0, beta=255, norm_type=cv.NORM_MINMAX)
    
    
    backproj = cv.calcBackProject([hue], [0], hist, ranges, scale=1)
    
    
    cv.imshow('BackProj', backproj)
    
    
    w = 400
    h = 400
    bin_w = int(round(w / histSize))
    histImg = np.zeros((h, w, 3), dtype=np.uint8)
    for i in range(bins):
        cv.rectangle(histImg, (i*bin_w, h), ( (i+1)*bin_w, h - int(round( hist[i]*h/255.0 )) ), (0, 0, 255), cv.FILLED)
    cv.imshow('Histogram', histImg)
    

src = cv.imread(img)

hsv = cv.cvtColor(src, cv.COLOR_BGR2HSV)
ch = (0, 0)
hue = np.empty(hsv.shape, hsv.dtype)
cv.mixChannels([hsv], [hue], ch)
window_image = 'Source image'
cv.namedWindow(window_image)
bins = 25
cv.createTrackbar('* Hue  bins: ', window_image, bins, 180, Hist_and_Backproj )
Hist_and_Backproj(bins)
cv.imshow(window_image, src)
cv.waitKey()


