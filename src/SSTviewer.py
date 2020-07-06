#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 09.01.2020 16:16 CET

@author: zocker_160
"""

import sys
import lib
import importlib
import webbrowser
from io import BytesIO
from lib.SST import SST as EEsst
from lib.TGA import TGA
from lib.DDS import DDSReader

importlib.reload(lib)

import tkinter as GUI
#from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk


version = "0.3"

# if image has multiple resolutions, then only show the first 3
tile_show_limit = 5

### setup GUI window
window = GUI.Tk()
window.title("Empire Earth: SST viewer")
# window.configure(bg="#1e1e1e") # this looks like shit!

### GUI functions
def show_about():
    #infowindow = GUI.Toplevel()
    #infowindow.title("About SSTviewer")
    #infowindow.geometry("400x200")

    #text = GUI.Text(infowindow)

    info = ''
    info += "SST Viewer for Empire Earth made by zocker_160\n"
    info += "version %s" % version
    info += "\n"
    info += "if you have any issue, pls feel free to report it:"
    info += "https://github.com/EE-modders/SST-tool/issues"
    info += "\n"
    info += "----------------------------------------------\n"
    info += "\n"
    info += "USAGE: SSTviewer <inputfile> or Drag&Drop the image onto the executable"
    info += "\n"

    #text.insert(GUI.INSERT, info)
    #text.insert(GUI.END, "2020")
    #text.pack()
    
    #infowindow.mainloop()
    messagebox.showinfo("SSTviewer for Empire Earth", info)    

def show_help():
    webbrowser.open_new_tab("https://github.com")

def select_file():
    filename = askopenfilename(
        filetypes=(("SST file", "*.sst"), ("All Files", "*.*")),
        title="Select a SST image file"
    )
    if filename: load_image(filename)

def load_image(filename: str):
    image_clearall()
    SST = EEsst()
    SST.read_from_file(filename)

    if SST.header["revision"] == b'\x00':
        EEImage = TGA(tga_binary=SST.ImageBody)
    elif SST.header["revision"] == b'\x01':
        EEImage = DDSReader(dds_binary=SST.ImageBody)

    Imageparts = EEImage.get_Image_parts()

    if SST.header["resolutions"] > 1: Imageparts = Imageparts[:tile_show_limit]

    ww = max(SST.header["x-res"] * 1.05, 450)
    wh = SST.header["y-res"] * max(SST.header["tiles"], min(SST.header["resolutions"], tile_show_limit)) * 1.3
    width = SST.header["x-res"]
    height = SST.header["y-res"]
    xLen, yLen, xPos, yPos = calc_winsize(xLen=ww, yLen=wh)

    #window.geometry("%dx%d+%d+%d" % (xLen, yLen, xPos, yPos)) # TODO make window resize more optimized

    for i, IMGpart in enumerate(Imageparts):
        image_normal = Image.open(BytesIO(IMGpart))        
        #load = load.resize((width, height))
        image_alpha = image_normal.split()[-1]
        render = ImageTk.PhotoImage(image_normal)
        a_render = ImageTk.PhotoImage(image_alpha)
        print(render)
        panels[i].configure(image=render, bd=5, relief="ridge")
        panels[i].image = render
        a_panels[i].configure(image=a_render, bd=5, relief="ridge")
        a_panels[i].image = a_render

        descr[i].configure(text="%dx%d" % (render.width(), render.height()))
        a_descr[i].configure(text="alpha mask")
        #panel = GUI.Label(window, image=ImageTk.PhotoImage(load), text="PAACKIT")
        #panel.grid(row=i)
        

def calc_winsize(xLen=800, yLen=600):
    xPos = window.winfo_screenwidth()/2 - xLen/2
    yPos = window.winfo_screenmmheight()/2 + yLen/2
    return xLen, yLen, xPos, yPos

def image_clearall():
    # TODO: replace this fucking magic number
    for i in range(10):
        panels[i].configure(bd=0)
        panels[i].image = None

        a_panels[i].configure(bd=0)
        a_panels[i].image = None

        descr[i].configure(text="")
        a_descr[i].configure(text="")

def test():
    ### open image in case CLI parameter given
    if len(sys.argv) > 1:    
        if sys.argv[1].split('.')[-1] != "sst":        
            messagebox.showerror("ERROR", "unsupported file format! Only SST allowed")
            window.quit()
        else:
            itest = load_image(sys.argv[1])
            itest = ImageTk.PhotoImage(data=itest)

            newp = GUI.Label(image=itest)
            newp.image = itest
            newp.pack()            

### setup GUI
xLen, yLen, x, y = calc_winsize()
window.geometry("%dx%d+%d+%d" % (xLen, yLen, x, y))

menubar = GUI.Menu(window, borderwidth=5, relief="groove", activebackground="#ffffff", activeforeground="#000000")

filemenu = GUI.Menu(menubar, tearoff=0, activebackground="#ffffff", activeforeground="#000000")
filemenu.add_command(label="Open", command=select_file)
filemenu.add_command(label="Exit", foreground="#ff0000", activeforeground="#ff0000", command=window.quit)

helpmenu = GUI.Menu(menubar, tearoff=0, activebackground="#ffffff", activeforeground="#000000")
helpmenu.add_command(label="Online Help", command=show_help)
helpmenu.add_command(label="About", command=show_about)

menubar.add_cascade(label="File", menu=filemenu)
menubar.add_cascade(label="Help", menu=helpmenu)
menubar.add_separator()
menubar.add_checkbutton(label="show alpha channel", state="disabled", onvalue=True, offvalue=False, command=test)

window.config(menu=menubar)

### make pictures scrollable TODO
#container = ttk.Frame(window)
#container.pack()
#scrollframe = ttk.Scrollbar(container, orient="vertical")
scrollframe = window

panels = list()
a_panels = list()
descr = list()
a_descr = list()
# TODO: replace this fucking magic number
for i in range(10):
    panels.append(GUI.Label(scrollframe))
    a_panels.append(GUI.Label(scrollframe, borderwidth=5))
    descr.append(GUI.Label(scrollframe))
    a_descr.append(GUI.Label(scrollframe))
    panels[-1].grid(row=(i*2), column=0, padx=5)
    a_panels[-1].grid(row=(i*2), column=1)
    descr[-1].grid(row=(i*2+1), column=0)
    a_descr[-1].grid(row=(i*2+1), column=1)
    #panels[-1].pack()
    #descr[-1].pack()


### load image when given as CLI parameter
if len(sys.argv) > 1:
    load_image(sys.argv[1])



window.mainloop()

"""
def old():
    window.geometry("%dx%d" % (width, height * max([ SST.header["tiles"], SST.header["resolutions"] ])))
    #root.resizable(0, 0)

    # Image load
    render = list()
    for i, image in enumerate(Imageparts):
        load = Image.open(BytesIO(image))
        load = load.resize((width, height))
        render.append(ImageTk.PhotoImage(load))

        panel = GUI.Label(window, image=render[i])


        panel.pack(fill=GUI.BOTH, expand=GUI.YES)

    # open GUI
    window.mainloop()
"""    