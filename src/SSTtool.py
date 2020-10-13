#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 05.01.2020 19:01 CET

@author: zocker_160
"""

import os
import sys
import importlib
import lib
from lib.SST import SST as SSTi
from lib.TGA import TGA
from lib.DDS import DDSReader

importlib.reload(lib)

version = "0.15"
magic_number_compressed = b'PK01' # this is the magic number for all compressed files
confirm = True
single_res = False
force_overwrite = False

file_ignorelist = ["shortcut to tga source 4-bit.sst"]

print("### SST Converter for Empire Earth made by zocker_160")
print("### version %s" % version)
print("###")
print("### if you have any issue, pls feel free to report it:")
print("### https://github.com/EE-modders/SST-tool/issues")
print("###")
print("###----------------------------------------------\n")

def show_help():
    # TODO: "--info" (show header information only)
    print("USAGE: SSTtool [options] <inputfile1> <inputfile2> ... | <inputfolder>")
    print("or you can just DRAG & DROP the image file or folder onto the executable")
    print("important: if you want to convert multiple TGAs into one SST, you can drop multiple files at once onto the executable")
    print()
    print("possible options:")
    print("-h, --help, -v\tshow this help / version information")    
    print("-nc\t\t\"no confirm\" disables all confirmation questions\n\t\tuseful for batch conversion")
    print("--single\texports only one (the biggest) resolution")
    print("--force\t\tforces to overwrite an existing file")
    if confirm: input("press Enter to close........")
    sys.exit()

def show_exit():
    input("\npress Enter to close.......\n")
    sys.exit()

def main_function_convert_file(filename: str):
    # check for file existence and compression
    try:
        with open(filename, 'rb') as sstfile:
            print("analysing %s......" % filename)
            if sstfile.read(4) == magic_number_compressed:
                print("\nyou need to decompress the file first!\n")
                show_exit()
    except EnvironmentError:
        print("File \"%s\" not found!" % filename)
        show_exit()

    # check if input file is SST or TGA
    if filename.endswith(".sst"):
        print("found SST file - extracting image(s).....")

        SST = SSTi()
        SST.read_from_file(filename)

        tiles_mult = SST.header["resolutions"] * SST.header["tiles"]

        try:        
            Image = SST.unpack()
        except TypeError as e:
            print(str(e))
            show_exit()

        if filename.startswith('..'):
            newfilename = '..' + filename.split('.')[-2]
        else:
            newfilename = filename.split('.')[-2]
        print(newfilename)

        if tiles_mult < 1:
            print("there is something wrong with your file! | Error code: res %s; tiles %s" % (SST.header["resolutions"], SST.header["tiles"]))
        else:        
            print("converting......\n")
            print(SST)

        if tiles_mult == 1:
            Image.write_file(SST.ImageBody, newfilename)
        else:
            print("found more than one image part (according to header):")
            #print("number of different resolutions: %d" % SST.header["resolutions"])
            #print("number of different image tiles: %d" % SST.header["tiles"])
            print("total number of parts: %d" % tiles_mult)
            if confirm:
                response = input("continue? (y/n) ")
            else:
                response = "y"
            if response != "y": show_exit()
            
            Imageparts = Image.get_Image_parts()
            num_images = len(Imageparts)

            print("\nactually found number of images: %d \n" % num_images)
            for i in range(num_images):
                if num_images > 1:
                    if SST.header["tiles"] > 1:                
                        Image.write_file(Imageparts[i], f"{newfilename}_{i+1}-{num_images}")
                    elif SST.header["resolutions"] > 1:
                        Image.write_file(Imageparts[i], f"{newfilename}_{i+1}-{num_images}_RES")
                        if single_res: break
                else:
                    Image.write_file(Imageparts[i], newfilename)

    elif filename.endswith(".tga"):
        print("found TGA file - will convert to SST.....\n")
        num_images = len(sys.argv) - 1

        if num_images == 1:
            print("creating SST........")
            with open(filename, 'rb') as tgafile:
                tga_bin = tgafile.read()

            orgTGA = TGA(tga_binary=tga_bin)
            orgTGA.cleanup()
            newSST = SSTi(1, num_tiles=1, x_res=orgTGA.xRes, y_res=orgTGA.yRes, ImageBody=orgTGA.tga_bin)
            
            newfilename = filename.split('.')[0]
            if os.path.exists(newfilename + '.sst') and not force_overwrite:
                print("This file does already exist! - adding \"_NEW\"")
                newSST.write_to_file(newfilename + "_NEW", add_extention=True)
            else:
                newSST.write_to_file(newfilename, add_extention=True)
        else:        
            filenames = sys.argv
            filenames.pop(0)
            tga_bin = b''
            x_tmp, y_tmp = 0, 0

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
                # on multi tile images, all *have to* have the exact same resolution, you cannot mix resolutions!
                if j == 0:
                    x_tmp, y_tmp = tmpTGA.xRes, tmpTGA.yRes
                else:
                    if x_tmp != tmpTGA.xRes or y_tmp != tmpTGA.yRes:
                        print("ERROR: All tiles have to have the exact same resolution!")
                        show_exit()
                tmpTGA.cleanup()
                tga_bin += tmpTGA.tga_bin
                tga_bin += b'\x00'

            print("creating SST file........")
            orgTGA = TGA(tga_binary=tga_bin)
            newSST = SSTi(1, num_tiles=num_images, x_res=orgTGA.xRes, y_res=orgTGA.yRes, ImageBody=orgTGA.tga_bin)

            newfilename = filename.split('.')[0]
            if os.path.exists(newfilename + '.ssz') and not force_overwrite:
                print("This file does already exist! - adding \"_NEW\"")
                newSST.write_to_file(newfilename + "_NEW", add_extention=True)
            else:
                newSST.write_to_file(newfilename, add_extention=True)

    else:
        print("ERROR: unknown file format! Only TGA and SST are supported \n")
        show_exit()
    
    print("done!")
    if confirm: input("press Enter to close.......")



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
    if arg == "--single":
        single_res = True
        parameter_list.append(i)
    if arg == "--force":
        force_overwrite = True
        parameter_list.append(i)        

# remove commandline parameters
parameter_list.sort(reverse=True)
for param in parameter_list:
    sys.argv.pop(param)

try:
    filename = sys.argv[1]
except IndexError:
    print("ERROR: no file(s) or folder specified!")
    show_exit()
if filename in file_ignorelist:
    print("This file is on the ignorelist!")
    show_exit()

if os.path.isfile(filename):
    main_function_convert_file(filename=filename)
elif os.path.isdir(filename):
    filepath = filename
    confirm = False

    print("Folder found - what do you want to do? \n")
    print("Convert all files")
    print("(1)\tSST -> TGA / JFIF")
    print("(2)\tTGA -> SST")

    selection = input("selection: ")

    if selection == "1":
        filetype = ".sst"
    elif selection == "2":
        filetype = ".tga"
    else:
        show_exit()

    for f in os.listdir(filepath):
        if f.endswith(filetype):  
            print("trying to open", f)
            if not filepath.endswith(os.sep): filepath += os.sep
            main_function_convert_file(filepath + f)
    show_exit()
else:
    print("ERROR: Input is neither file nor folder!")
    show_exit()
