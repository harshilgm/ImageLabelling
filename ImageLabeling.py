


import cv2
from PIL import Image, ImageTk
import numpy

import tkinter as tk
from tkinter import Tk, Button, Canvas
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory

from os import listdir
from os.path import join,dirname



window = Tk()
window.geometry('750x600')
window.title('ImageLabeler')
canvas= Canvas(window,height=550, width=750)
canvas.grid(row=0,column=0, columnspan=8)

images=numpy.empty
imagenumber = 0
BoxList=[]
imgfiles = []
imgtk=""
Directory=''
ScaleX=1
ScaleY=1
isIdle=True
running=False



    
    


        
"""Convert the image to (rgb) and make it appear on the screen"""
def ShowImg(img):
    global imgtk
    global ScaleX
    global ScaleY
    canvas.delete("all")
    
    
    w,h = img.shape[:2]
    ScaleX = 750/float(w)
    ScaleY = 550/float(h)
    
    
    b,g,r=cv2.split(img)
    img=cv2.merge((r,g,b))
    img = cv2.resize(img, (750,550), interpolation = cv2.INTER_AREA)
    im = Image.fromarray(img)
    
    imgtk = ImageTk.PhotoImage(image=im)
    canvas.create_image(0,0, image=imgtk,anchor="nw")
    
    
"""Open a single image, and also set the directory to the folder of the image"""  
def OpenImage():

    global imgfiles
    global Directory
    global imagenumber
    global images
    global isIdle
    
    if(isIdle == False):
        return
    isIdle=False
    
    temp = askopenfilename()
    if(temp==''):
        isIdle=True
        return
    filename=temp
    print filename
    Directory=dirname(filename)
    
    imgfiles = [ f for f in listdir(Directory) if f.endswith('.jpg') ]
    
    for f in imgfiles:
        print f
        if filename == f:
            imagenumber=list.index(f)
            
    
    images = numpy.empty(len(imgfiles), dtype=object)
    for n in range(0, len(imgfiles)):
        images[n] = cv2.imread( join(Directory,imgfiles[n]) )
        
        
    filename=cv2.imread(filename)
    ShowImg(filename)
    ReadSaveFile()
    
    isIdle=True
    
    
"""Open a folder of images"""    
def OpenDirectory():

    global imgfiles
    global Directory
    global isIdle
    
    if(isIdle==False):
        return
    isIdle=True
   
    
    temp = askdirectory()
    if(temp==''):
        isIdle=True
        return
    
    Directory=temp
    
    imgfiles = [ f for f in listdir(Directory) if f.endswith('jpg') ]
    global images 
    images = numpy.empty(len(imgfiles), dtype=object)
    for n in range(0, len(imgfiles)):
        images[n] = cv2.imread( join(Directory,imgfiles[n]) )
        
    ShowImg(images[0])
    ReadSaveFile()
    
    isIdle=True
    
"""Go to previous image""" 
def PreviousImg(_event=None):
    
    global imagenumber
    global images
    global isIdle
    global imgfiles
    
    if(imgfiles==[]):
        return
    
    if(isIdle==False):
        return
    isIdle=False
    
    Saving(imgfiles[imagenumber],BoxList,Directory)
    if(imagenumber==0):
        imagenumber=len(images)-1
    else:
        imagenumber=imagenumber-1
   
    ShowImg(images[imagenumber])
    ReadSaveFile()
    
    isIdle=True
 


"""Functino to go to next image"""    
def NextImg(_event=None):
    
    global imagenumber
    global images
    global isIdle
    global imgfiles
    
    if(imgfiles==[]):
        return
    
    if(isIdle==False):
        return
    isIdle=False
    
    Saving(imgfiles[imagenumber],BoxList,Directory)
    
    if(imagenumber==len(images)-1):
        imagenumber=0
    else:   
        imagenumber=imagenumber+1
    
    ShowImg(images[imagenumber])
    ReadSaveFile()
    
    isIdle=True
    
    
"""Algorithm portion that finds the object in next frame and draws the boxes"""    
def Tracking():
    
    global BoxList
    global imagenumber
    global ScaleX,ScaleY
    global isIdle
    global images
    global imgfiles
    global running
    
    
    
    
    

    Saving(imgfiles[imagenumber],BoxList,Directory)
    
    frame= images[imagenumber]
    imagenumber=imagenumber+1
    if(imagenumber>=len(images)):
        imagenumber=imagenumber-1
        isIdle=True
        return
    Nextframe=images[imagenumber]
    ShowImg(images[imagenumber])
    # setup initial location of window
  
    
    for Box in BoxList:
        
        c = int(round(Box.x1/ScaleX)) 
        w = int(round((Box.x2-Box.x1)/ScaleX))
        r = int(round(Box.y1/ScaleY))
        h = int(round((Box.y2-Box.y1)/ScaleY))
        
        track_window = (c,r,w,h)
        
        # set up the ROI for tracking
        roi = frame[r:r+h, c:c+w]
        print(roi)
        hsv_roi =  cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_roi, numpy.array((0., 60.,32.)), numpy.array((180.,255.,255.)))
        roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
        cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)
        # Setup the termin==[=ation criteria, either 10 iteration or move by atleast 1 pt
        term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 0, 0 ) 
        hsv = cv2.cvtColor(Nextframe, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv],[0],roi_hist,[0,180],1)
        # apply meanshift to get the new location
        ret, track_window = cv2.meanShift(dst, track_window, term_crit)
        # Draw it on image
        x,y,w,h = track_window
        
        Box.x1=x*ScaleX
        Box.y1=y*ScaleY
        Box.x2=(x+w)*ScaleX
        Box.y2=(y+h)*ScaleY
        Box.ImgRect=canvas.create_rectangle(x*ScaleX,y*ScaleY,(x+w)*ScaleX,(y+h)*ScaleY,outline="green",width=2)
        Box.ImgLabel=canvas.create_text(Box.x2,Box.y2,text=Box.LabelName,fill="green",anchor="nw")
        
        if running==True:
            window.after(500,Tracking)
   
   
"""Starts the automated process"""
def PlayButton(_event=None):
    global running
   
    if(running==False):
        Play.config(text="Pause")
        running=True
        window.after(500,Tracking)
    else:
        Play.config(text="Play")
        running=False
        window.mainloop()
   
    
"""Saves the image and its labels"""
def SaveButton(_event=None):
    global Directory
    global imgfiles
    global BoxList
    global imagenumber
    global isIdle
    
    if(isIdle==False):
        return
    isIdle=False
    
    Saving(imgfiles[imagenumber],BoxList,Directory)
    
    isIdle=True

"""Function for letting the user create a label (One thing that is not fixed is if the second point has coordinates that are lower values than the first point)"""
def CreateRect(_event=None):
    global BoxList
    global isIdle
    global imgfiles
    
    if(imgfiles==[]):
        return
    if(isIdle==False):
        return
    isIdle=False
    
    BoxList.append(Box('',0,0,0,0,False))
    
    isIdle=True

  
class Box:
    
    var=tk.IntVar()
    x1=0
    y1=0
    x2=0
    y2=0
    e=""
    ImgRect=''
    LabelName=''
    ImgLabel=''
    
    def __init__(self,label,x1,y1,x2,y2,hasSave):
        
        if(hasSave == False):
            window.config(cursor='crosshair')
            canvas.bind("<Button-1>",self.getposition1)
            canvas.wait_variable(self.var)
            canvas.bind("<Button-1>",self.getposition2)
            canvas.wait_variable(self.var)
            self.ImgRect=canvas.create_rectangle(self.x1,self.y1,self.x2,self.y2,outline="green",width=2)
            self.EnterLabel()
            window.config(cursor='')
        else:
            self.x1=x1
            self.y1=y1
            self.x2=x2
            self.y2=y2
            self.LabelName=label
            self.ImgRect=canvas.create_rectangle(self.x1,self.y1,self.x2,self.y2,outline="green",width=2)
            self.ImgLabel=canvas.create_text(self.x2,self.y2,text=self.LabelName,fill="green",anchor="nw")
    
    def getposition1(self,event):
        
        self.x1= event.x
        self.y1= event.y
        self.var.set(1)
    
    def getposition2(self,event):
        
        self.x2=event.x
        self.y2=event.y
        self.var.set(2)
    
    def EnterLabel(self):
        global window
        LabelWin=Tk()
        Winx=window.winfo_x()+self.x2
        Winy=window.winfo_y()+self.y2
        
        LabelWin.geometry("175x50+%d+%d"%(Winx,Winy))
        
        self.e=tk.Entry(LabelWin)
        LabelOK= Button(LabelWin,text="Ok",command=self.setLabel,height=2,width=3)
        LabelWin.bind('<Return>',self.setLabel)
        self.e.grid(row=0,column=0)
        LabelOK.grid(row=0,column=1)
        
        canvas.wait_variable(self.var)
        LabelWin.destroy()
    
    def setLabel(self,_event=None):
        self.LabelName = self.e.get()
        self.ImgLabel=canvas.create_text(self.x2,self.y2,text=self.LabelName,fill="green",anchor="nw")
        
        
        self.var.set(3)
    
    
"""Deletes a Label"""                
def DeleteRect(_event=None):
    global isIdle
    global BoxList
    
    if(BoxList==[]):
        return
    
    if(isIdle==False):
        return
    isIdle=False
    

    Delete()
    
    isIdle=True
           
class Delete:           
    global BoxList
    var = tk.IntVar()
    
    mousex=0
    mousey=0
    
    def __init__(self):
        loop=0
        window.config(cursor='X_cursor')
        while(loop==0):
            
        
            canvas.bind("<Button-1>",self.getposition)
            canvas.wait_variable(self.var)
            for Box in BoxList:
                if(Box.x1<=self.mousex<=Box.x2 and Box.y1<=self.mousey<=Box.y2):
                    canvas.delete(Box.ImgRect)
                    canvas.delete(Box.ImgLabel)
                    BoxList.remove(Box)
                    loop=1
                
        
        
        window.config(cursor='')
        window.update()
        
    def getposition(self,event):
        self.mousex= event.x
        self.mousey= event.y
        self.var.set(1)
        

def Saving(imgfile,BoxList,SaveDir):
    global ScaleX,ScaleY

    imgfile=imgfile.replace('.jpg','')
    completeName= join(SaveDir,imgfile+'.txt')
    print completeName
    f = open(completeName, 'w')
    
    f.write('<imagename>'+completeName+'</imagename> \n')
    
    
    for Box in BoxList:
        f.write('<object> \n')
        f.write('  <label>'+Box.LabelName+'</label> \n')
        f.write('  <box> \n')
        f.write('    <xmin>'+str(round(Box.x1/ScaleX))+'</xmin> \n')
        f.write('    <ymin>'+str(round(Box.y1/ScaleY))+'</ymin> \n')
        f.write('    <xmax>'+str(round(Box.x2/ScaleX))+'</xmax> \n')
        f.write('    <ymax>'+str(round(Box.y2/ScaleY))+'</ymax> \n')
        f.write('  </box> \n')
        f.write('</object> \n\n')
        
    f.close()
     
"""Used when opening an image with saved labels"""    
def ReadSaveFile():
    global BoxList
    global imgfiles
    global imagenumber
    global Directory
    global ScaleX
    global ScaleY
    hasSave = False
    
    savefiles = [ f for f in listdir(Directory) if f.endswith('txt') ]
    imgname=imgfiles[imagenumber]
    imgname=imgname.replace('.jpg','.txt')
    for files in savefiles:
        
        if imgname in files:
            hasSave = True
            
   
    if(hasSave == False):
        return
    
    BoxList=[]
    SaveFileName=join(Directory,imgname)
    SaveFileName=SaveFileName.replace('jpg','txt')
   
    
    f = open(SaveFileName, "r")
    f.seek(0)
    
    data=''
    copy=False
    for line in f:
        print line
        if line.strip() == "<object>":
            copy = True
        elif line.strip() == "</object>":
            copy = False
            label=data[data.find("<label>")+7:data.find("</label>")]
            xmin=data[data.find("<xmin>")+6:data.find("</xmin>")]
            ymin=data[data.find("<ymin>")+6:data.find("</ymin>")]
            xmax=data[data.find("<xmax>")+6:data.find("</xmax>")]
            ymax=data[data.find("<ymax>")+6:data.find("</ymax>")]
            print data
            BoxList.append(Box(label,int(float(xmin))*ScaleX,int(float(ymin))*ScaleY,int(float(xmax))*ScaleX,int(float(ymax))*ScaleY,True))
            data=''

        elif copy:
            data=data+line
    
    


            
OpenImg = Button(window, text="OpenImg", command=OpenImage, height=2,width=10)
OpenDir = Button(window, text="OpenDir",command=OpenDirectory,height=2, width=10)
Save = Button(window, text="Save",command=SaveButton,height=2, width=10)
Previous = Button(window, text="Previous",command=PreviousImg,height=2, width=10)
Next = Button(window, text="Next",command=NextImg,height=2, width=10)
Play = Button(window, text="Play",command=PlayButton,height=2, width=10)
CreateBox = Button(window, text="Create Box",command=CreateRect,height=2, width=10)
DeleteBox = Button(window, text="Delete Box",command=DeleteRect,height=2,width=10)

window.bind('<space>',PlayButton)
window.bind('w',CreateRect)
window.bind('a',PreviousImg)
window.bind('d',NextImg)
window.bind('s',SaveButton)
window.bind('q',DeleteRect)

OpenImg.grid(row=1,column=0,sticky="nsew")
OpenDir.grid(row=1,column=1,sticky="nsew")
Save.grid(row=1,column=2,sticky="nsew")
CreateBox.grid(row=1,column=3,sticky="nsew")
DeleteBox.grid(row=1,column=4,sticky="nsew")
Previous.grid(row=1,column=5,sticky="nsew")
Play.grid(row=1,column=6,sticky="nsew")
Next.grid(row=1,column=7,sticky="nsew")

window.mainloop()        

        
    


     