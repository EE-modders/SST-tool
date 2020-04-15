#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 05.01.2020 19:01 CET

@author: zocker_160
"""

import sys
import importlib
import lib
from lib.SST import SST
from lib.TGA import TGA

importlib.reload(lib)

version = "0.8"

magic_number_compressed = b'PK01' # this is the magic number for all compressed files
confirm = True
short_output = False

print("### SST Converter for Empire Earth made by zocker_160")
print("### version %s" % version)
print("###")
print("### if you have any issue, pls feel free to report it:")
print("### https://github.com/EE-modders/SST-tool/issues")
print("###")
print("###----------------------------------------------\n")

def show_help():
    print("USAGE: SSTtool [options] <inputfile1> <inputfile2> ... <inputfileN>")
    # TODO: "--info" (show header information only)
    print("important: if you want to convert multiple TGAs you can also just drag and drop them all at once onto the executable")
    print()
    print("possible options:")
    print("-h, --help, -v\tshow this help / version information")
    print("-nc\t\t\"no confirm\" disables all confirmation questions\n\t\tuseful for batch conversion")
    print("-so\t\t\"short output\" doesn't add \"_NEW_\" to the output SST file")
    if confirm: input("press Enter to close........")
    sys.exit()

def show_exit():
    input("\npress Enter to close.......\n")
    sys.exit()

if len(sys.argv) <= 1:
    show_help()

parameter_list = list()

for i, arg in enumerate(sys.argv):
    if arg == "-h" or arg == "--help" or arg == "-v":
        confirm = False
        show_help()
    if arg == "-nc":
        confirm = False
        parameter_list.append(i)        
    if arg == "-so":
        short_output = True
        parameter_list.append(i)        

# remove commandline parameters
parameter_list.sort(reverse=True)
for param in parameter_list:
    sys.argv.pop(param)

try:
    filename = sys.argv[1]
except IndexError:
    print("ERROR: no file(s) specified!")
    show_exit()

try:
    with open(filename, 'rb') as sstfile:
        print("analysing %s......" % filename)
        if sstfile.read(4) == magic_number_compressed:
            print("\nyou need to decompress the file first!\n")
            show_exit()
except EnvironmentError:
    print("File \"%s\" not found!" % filename)
    show_exit()

# check if input file was TGA or SST file
if filename.split('.')[-1] == "sst":
    print("found SST file - will convert to TGA.....")

    SST = SST()
    SST.read_from_file(filename)

    TGA = TGA(tga_binary=SST.TGAbody)
    tiles_mult = SST.header["resolutions"] * SST.header["tiles"]

    tgafilename = filename.split('.')[0] + ".tga"

    if tiles_mult < 1:
        print("there is something wrong with your file! | Error code: res %s; tiles %s" % (SST.header["resolutions"], SST.header["tiles"]))
    else:        
        print("converting......\n")
        print(SST)

    if tiles_mult == 1:
        with open(tgafilename, 'wb') as tgafile:
            tgafile.write(SST.TGAbody)
    else:
        print("found more than one tile (according to header):")
        #print("number of different resolutions: %d" % SST.header["resolutions"])
        #print("number of different image tiles: %d" % SST.header["tiles"])
        print("total number of tiles: %d" % tiles_mult)
        if confirm:
            response = input("continue? (y/n) ")
        else:
            response = "y"
        if response != "y": show_exit()
        
        global TGA_images
        TGA_images = TGA.get_TGA_parts_3()

        num_images = len(TGA_images)

        print("\nactually found number of images: %d \n" % num_images)
        for i in range(num_images):
            if num_images > 1:
                if SST.header["tiles"] > 1:                
                    TGA.write_TGA(TGA_images[i], filename.split('.')[0] + "_" + str(i+1) + "-" + str(num_images) + ".tga")
                elif SST.header["resolutions"] > 1:
                    TGA.write_TGA(TGA_images[i], filename.split('.')[0] + "_" + str(i+1) + "-" + str(num_images) + "_RES_" + ".tga")
            else:
                TGA.write_TGA(TGA_images[i], filename.split('.')[0] + ".tga")
            

elif filename.split('.')[-1] == "tga":
    print("found TGA file - will convert to SST.....\n")
    num_images = len(sys.argv) - 1

    if num_images == 1:
        print("creating SST........")
        with open(filename, 'rb') as tgafile:
            tga_bin = tgafile.read()

        orgTGA = TGA(tga_binary=tga_bin)
        orgTGA.cleanup()
        newSST = SST(1, num_tiles=1, x_res=orgTGA.xRes, y_res=orgTGA.yRes, TGAbody=orgTGA.tga_bin)
        if short_output:
            newSST.write_to_file(filename.split('.')[0])
        else:
            newSST.write_to_file(filename.split('.')[0] + "_NEW")
    else:        
        filenames = sys.argv
        filenames.pop(0)
        tga_bin = b''

        print("following %d images as input:" % num_images )
        print("watch out for the right order!!\n")

        for i in range(num_images):
            print("%d: %s" % (i+1, filenames[i]))
        print()
        if confirm:
            response = input("is that correct? (y/n) ")
        else:
            response = "y"
        if response != "y": show_exit()

        print("bundling TGA images........")

        for j in range(num_images):
            with open(filenames[j], 'rb') as tgafile:
                tmpTGA = TGA(tgafile.read())
                tmpTGA.cleanup()
                tga_bin += tmpTGA.tga_bin
                tga_bin += b'\x00'

        print("creating SST file........")
        orgTGA = TGA(tga_binary=tga_bin)
        newSST = SST(1, num_tiles=num_images, x_res=orgTGA.xRes, y_res=orgTGA.yRes, TGAbody=orgTGA.tga_bin)
        if short_output:
            newSST.write_to_file(filename.split('.')[0])
        else:
            newSST.write_to_file(filename.split('.')[0] + "_NEW")

else:
    print("ERROR: unknown file format! Only TGA and SST are supported \n")
    show_exit()

print("done!")

if confirm: input("press Enter to close.......")
