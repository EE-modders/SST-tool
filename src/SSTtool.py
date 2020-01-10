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

version = "0.4 beta"

print("### SST Converter for Empire Earth made by zocker_160")
print("### version %s" % version)
print("###")
print("### if you have any issue, pls feel free to report it:")
print("### https://github.com/EE-modders/SST-tool/issues")
print("###")
print("###----------------------------------------------\n")

if len(sys.argv) <= 1:
    print("USAGE: SSTtool <inputfile1> <inputfile2> <inputfile3> ... <inputfileN>")
    # TODO: implement "-h", "--silent" (for no promt / bash convert), "--info" (show header information only)
    print("important: if you want to convert multiple TGAs you can also just drag and drop them all at once onto the executable")
    print()
    input("press Enter to close.......")
    sys.exit()

magic_number_compressed = b'PK01' # this is the magic number for all compressed files
filename = sys.argv[1]

with open(filename, 'rb') as sstfile:
    global TGAbody
    
    print("analysing %s......" % filename)
    if sstfile.read(4) == magic_number_compressed:
        print()
        print("you need to decompress the file first!")
        print()

        input("press Enter to close.......")
        sys.exit()

# check if input was TGA or SST file
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
        response = input("continue? (y/n) ")
        if response != "y":        
            input("\nEXIT - press Enter.......\n")            
            sys.exit()
        
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
        newSST = SST(1, num_tiles=1, x_res=orgTGA.xRes, y_res=orgTGA.yRes, TGAbody=orgTGA.tga_bin)
        newSST.write_to_file(filename.split('.')[0] + "_NEW.sst")
    else:        
        filenames = sys.argv
        filenames.pop(0)
        tga_bin = b''

        print("following %d images as input:" % num_images )
        print("watch out for the right order!!\n")

        for i in range(num_images):
            print("%d: %s" % (i+1, filenames[i]))
        print()
        response = input("is that correct? (y/n) ")
        if response != "y":
            input("\nEXIT - press Enter.......\n")            
            sys.exit()

        print("bundling TGA images........")

        for j in range(num_images):
            with open(filenames[j], 'rb') as tgafile:
                tga_bin += tgafile.read()

        print("creating SST file........")
        orgTGA = TGA(tga_binary=tga_bin)
        newSST = SST(1, num_tiles=num_images, x_res=orgTGA.xRes, y_res=orgTGA.yRes, TGAbody=orgTGA.tga_bin)
        newSST.write_to_file(filename.split('.')[0] + "_TEST.sst")

    #response = input("how many tiles / images will the SST texture contain? ")
    #tga_bin = b''
    #try:
    #    response = int(response)
    #except ValueError:
    #    print("ERROR: invalid value!")
    #    sys.exit()
    #
    #if response == 1:
    #    print("creating SST........")
    #    with open(filename, 'rb') as tgafile:
    #        tga_bin = tgafile.read()
    #    
    #    orgTGA = TGA(tga_binary=tga_bin)
    #    newSST = SST(1, num_tiles=1, x_res=orgTGA.xRes, y_res=orgTGA.yRes, TGAbody=orgTGA.tga_bin)
    #    newSST.write_to_file(filename.split('.')[0] + "_TEST.sst")
    #elif response > 1:
    #    print("enter multi image mode.........")        
    #    with open(filename, 'rb') as tgafile:
    #        tga_bin = tgafile.read()
    #    
    #    for i in range(response-1):
    #        newfilename = input("Please input TGA image (%d/%d) " % (i+2, response))
    #        with open(newfilename, 'rb') as tgafile:
    #            tga_bin += tgafile.read()
    #
    #    print("bundling TGA images........")
    #    orgTGA = TGA(tga_binary=tga_bin)
    #    newSST = SST(1, num_tiles=response, x_res=orgTGA.xRes, y_res=orgTGA.yRes, TGAbody=orgTGA.tga_bin)
    #    newSST.write_to_file(filename.split('.')[0] + "_TEST.sst")

else:
    print("ERROR: unknown file format! Only TGA and SST are supported \n")
    input("press Enter to close.......")



print("done!")

input("press Enter to close.......")
