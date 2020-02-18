#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 09.01.2020 16:16 CET

@author: zocker_160
"""

import sys
import importlib
import lib
from io import BytesIO
from lib.SST import SST
from lib.TGA import TGA

importlib.reload(lib)

import tkinter
from tkinter import messagebox
from PIL import Image, ImageTk

version = "0.1"

root = tkinter.Tk()
root.title("Empire Earth: SST image viewer")

if len(sys.argv) <= 1:
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

    root.withdraw()
    messagebox.showinfo("SSTviewer for Empire Earth", info, )
    sys.exit()

if sys.argv[1].split('.')[-1] != "sst":
    root.withdraw()
    messagebox.showerror("ERROR", "unsupported file format! Only SST allowed")
    sys.exit()
else:    
    SST = SST()
    SST.read_from_file(sys.argv[1])
    TGA = TGA(SST.TGAbody)
    TGA_Images = TGA.get_TGA_parts_3()

    width = SST.header["x-res"]
    height = SST.header["y-res"]
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    root.geometry("%dx%d+%d+%d" % (width, height * max([ SST.header["tiles"], SST.header["resolutions"] ]), x, y))
    #root.resizable(0, 0)

    # Image load
    render = list()
    for i, tgaimage in enumerate(TGA_Images):
        load = Image.open(BytesIO(tgaimage))
        load = load.resize((width, height))
        render.append(ImageTk.PhotoImage(load))

        panel = tkinter.Label(root, image=render[i])
        panel.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    # open GUI
    root.mainloop()
