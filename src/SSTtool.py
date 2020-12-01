#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 05.01.2020 19:01 CET

@author: zocker_160
"""

import os
import sys
import argparse

if __name__ == "__main__":
    import importlib
    import lib

    from lib.SST import SST as SSTi
    from lib.TGA import TGA
    from lib.DDS import DDSReader

    importlib.reload(lib)
else:
    from .lib.SST import SST as SSTi
    from .lib.TGA import TGA
    from .lib.DDS import DDSReader


version = "0.17"
magic_number_compressed = b'PK01' # this is the magic number for all compressed files

file_ignorelist = ["shortcut to tga source 4-bit.sst"]

fromCLI = False  # this is true, when function is called from CLI and not from another python module

print("### SST Converter for Empire Earth made by zocker_160")
print("### version %s" % version)
print("###")
print("### if you have any issue, pls feel free to report it:")
print("### https://github.com/EE-modders/SST-tool/issues")
print("###")
print("###----------------------------------------------\n")


def _convert_files(files: list, confirm: bool, force_overwrite: bool, single_res: bool, outputlocation=""):
    # add os.sep when outputlocation is set
    if outputlocation: outputlocation += os.sep

    for i, file in enumerate(files):
        # check for file existence and compression
        try:
            with open(file, 'rb') as sstfile:
                print("analysing %s......" % file)
                if sstfile.read(4) == magic_number_compressed:
                    raise RuntimeError("\nyou need to decompress the file first!\n")
        except EnvironmentError:
            raise FileNotFoundError("File \"%s\" not found!" % file)

        # check if file is in ignorelist
        if file in file_ignorelist:
            print("This file is on the ignorelist! Skipping...")
            continue

        # check if input file is SST or TGA
        if file.endswith(".sst"):
            print("found SST file - extracting image(s).....")

            SST = SSTi()
            SST.read_from_file(file)

            tiles_mult = SST.header["resolutions"] * SST.header["tiles"]

            try:
                Image = SST.unpack()
            except TypeError as e:
                raise

            if file.startswith('..'):
                newfilename = '..' + file.split('.')[-2]
            else:
                newfilename = file.split('.')[-2]
            print(newfilename)

            if tiles_mult < 1:
                raise TypeError("there is something wrong with your file! | Error code: res %s; tiles %s" % (SST.header["resolutions"], SST.header["tiles"]))
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
                if response != "y": raise KeyboardInterrupt("aborted by user...")

                Imageparts = Image.get_Image_parts()
                num_images = len(Imageparts)

                print("\nactually found number of images: %d \n" % num_images)
                for i in range(num_images):
                    if num_images > 1:
                        if SST.header["tiles"] > 1:                
                            Image.write_file(Imageparts[i], outputlocation + f"{newfilename}_{i+1}-{num_images}")
                        elif SST.header["resolutions"] > 1:
                            Image.write_file(Imageparts[i], outputlocation + f"{newfilename}_{i+1}-{num_images}_RES")
                            if single_res: break
                    else:
                        Image.write_file(Imageparts[i], outputlocation + newfilename)

        elif file.endswith(".tga"):
            print("found TGA file - will convert to SST.....\n")

            # check if this item is the first of the input list
            if i == 0 and len(files) > 1:
                # convert all images into one SST with multiple tiles
                tga_bin = b''
                x_tmp, y_tmp = 0, 0

                if fromCLI:
                    print("following %d images as input:" % len(files) )
                    print("watch out for the right order!!\n")

                    for y, fl in enumerate(files):
                        print("%d: %s" % (y+1, fl))
                    print()
                    if confirm:
                        response = input("is that correct? (y/n) ")
                    else:
                        response = "y"
                    if response != "y": raise KeyboardInterrupt("aborted by user...")

                print("bundling TGA images........")

                for z, f in enumerate(files):
                    with open(f, 'rb') as tgafile:
                        tmpTGA = TGA(tgafile.read())
                    # on multi tile images, all *have to* have the exact same resolution, you cannot mix resolutions!
                    if z == 0:
                        x_tmp, y_tmp = tmpTGA.xRes, tmpTGA.yRes
                    else:
                        if x_tmp != tmpTGA.xRes or y_tmp != tmpTGA.yRes:
                            raise TypeError("ERROR: All tiles have to have the exact same resolution!")
                    tmpTGA.cleanup()
                    tga_bin += tmpTGA.tga_bin
                    tga_bin += b'\x00'

                print("creating SST file........")
                orgTGA = TGA(tga_binary=tga_bin)
                newSST = SSTi(1, num_tiles=len(files), x_res=orgTGA.xRes, y_res=orgTGA.yRes, ImageBody=orgTGA.tga_bin)

                newfilename = file.split('.')[0]
                if os.path.exists(newfilename + '.sst') and not force_overwrite:
                    print("This file does already exist! - adding \"_NEW\"")
                    newSST.write_to_file(outputlocation + newfilename + "_NEW", add_extention=True)
                else:
                    newSST.write_to_file(outputlocation + newfilename, add_extention=True)

                # break out of the main loop
                break
            else:
                # convert just this one file
                print("creating SST........")

                with open(file, 'rb') as tgafile:
                    tga_bin = tgafile.read()

                orgTGA = TGA(tga_binary=tga_bin)
                orgTGA.cleanup()
                newSST = SSTi(1, num_tiles=1, x_res=orgTGA.xRes, y_res=orgTGA.yRes, ImageBody=orgTGA.tga_bin)
                
                newfilename = file.split('.')[0]
                if os.path.exists(newfilename + '.sst') and not force_overwrite:
                    print("This file does already exist! - adding \"_NEW\"")
                    newSST.write_to_file(outputlocation + newfilename + "_NEW", add_extention=True)
                else:
                    newSST.write_to_file(outputlocation + newfilename, add_extention=True)
        else:
            raise TypeError("ERROR: unknown file format! Only TGA and SST are supported \n")
        
    print("done!")


def main(inputfiles: list, selection: str, confirm=False, overwrite=False, single_res=False):

    firstfile = inputfiles[0]

    if os.path.isfile(firstfile):
        _convert_files(inputfiles, confirm=confirm, force_overwrite=overwrite, single_res=single_res)
    elif os.path.isdir(firstfile):
        filepath = firstfile
        if not filepath.endswith(os.sep): filepath += os.sep
        filelist = list()

        if fromCLI and not selection:
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
            raise TypeError("ERROR: Invalid selection!")

        for f in os.listdir(filepath):
            if f.endswith(filetype):
                print("found file:", f)
                filelist.append(filepath + f)

        _convert_files(filelist, confirm=confirm, force_overwrite=overwrite, single_res=single_res)
    else:
        raise TypeError("ERROR: Input is neither file nor folder!")


def cli_params():
    parser = argparse.ArgumentParser(description="SST Converter for Empire Earth made by zocker_160")

    parser.add_argument("INPUT", nargs='+', help="input file(s) or folder")

    parser.add_argument("-nc", dest="confirm", action="store_false", help="disable all confirm messages")
    parser.add_argument("-s", "--single", dest="single_res", action="store_true", help="export only one (the biggest) resolution")
    parser.add_argument("-f", "--force", dest="force_overwrite", action="store_true", help="forces to overwrite existing files without asking")
    parser.add_argument("-v", "--version", action="version", version=version)

    return parser.parse_args()


if __name__ == "__main__":
    # in need to do this because fucking Windows users think that the software "does not work" otherwise......
    if len(sys.argv) <= 1:
        print("Please use Drag&Drop or the commandline interface!")
        input("\npress Enter to close.......\n")
        sys.exit()

    CLI = cli_params()

    print(CLI)

    fromCLI = True

    try:
        main(
            inputfiles=CLI.INPUT,
            selection=None,
            confirm=CLI.confirm,
            overwrite=CLI.force_overwrite,
            single_res=CLI.single_res
        )
    except KeyboardInterrupt as ke:
        print(ke.args[0])
    except Exception as e:
        print(str(e))
    finally:
        input("\npress Enter to close.......\n")
        sys.exit()
