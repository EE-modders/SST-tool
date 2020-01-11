#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 05.01.2020 21:50 CET

@author: zocker_160
"""
import sys
from io import BytesIO

class TGA:
    def __init__(self, tga_binary = b''):
        self.tga_bin = tga_binary
        self.tga_header_length = 18
        self.TGAheader = self.get_header()
        self.xRes, self.yRes, self.BitDepth, self.Type = self.get_TGA_info(self.TGAheader)

        if self.Type != 2:
            input("ERROR: This type (%d) of TGA is not supported: pls deactivate RLE compression\n" % self.Type)
            sys.exit()
        self.tga_bin = self.cleanup()

    def get_header(self):
        tga = BytesIO(self.tga_bin)    
        return tga.read(self.tga_header_length)

    ### this function is not in use anymore, use the new one instead
    def get_TGA_parts(self, binary_tga_blob, number_of_tiles: int):
        tga_blob = BytesIO(binary_tga_blob)

        self.TGAheader = tga_blob.read(self.tga_header_length)
        # This code assumes,that all TGA-tiles have the same TGA-header        
        header = list()
        header.append(0)

        for _ in range(number_of_tiles-1):
            next_header = tga_blob.read(-1).find(self.TGAheader)
            if next_header == -1:
                input("Critical Error: Number of tiles does not match the one specified in the SST file!\n")
                sys.exit()
            header.append(next_header)
            tga_blob.seek(next_header+self.tga_header_length)
        
        header.append(header[-1]) # add one additional field so len(header) = number_of_tiles + 1
        TGA_images = [0] * number_of_tiles

        for i in range(number_of_tiles):            
            tga_blob.seek(header[i])
            diff = header[i+1] - header[i]
            if diff == 0:
                TGA_images[i] = tga_blob.read(-1)
            else:                
                TGA_images[i] = tga_blob.read(diff)

        return TGA_images

    ### this function doesn't work on all files either, see comment below
    def get_TGA_parts_2(self, binary_tga_blob):
        tga_blob = BytesIO(binary_tga_blob)

        self.TGAheader = tga_blob.read(self.tga_header_length)
        # This code assumes, that all TGA-tiles have the same TGA-header
        ### which is sadly NOT the way SST work, different headers inside the same file are possible!

        TGA_images = list()
        next_header = 0

        while True:
            tga_blob.seek(self.tga_header_length)
            next_header = tga_blob.read(-1).find(self.TGAheader)
            print(next_header)

            tga_blob.seek(0)
            if next_header == -1:
                TGA_images.append(tga_blob.read(-1))
                break
            else:
                TGA_images.append(tga_blob.read(next_header+self.tga_header_length))
                tga_blob = BytesIO(tga_blob.read(-1))

        return TGA_images
    
    def get_TGA_parts_3(self):
        """Function, that returns all TGA images in the binary blob"""
        tga_blob = BytesIO(self.tga_bin)

        TGA_images = list()

        while True:
            tmp_blob = b''
            
            TGAHeader = tga_blob.read(self.tga_header_length)
            #print(TGAHeader)
            if TGAHeader == b'':
                break
            tmp_blob += TGAHeader
            TGAbody = tga_blob.read(self.get_TGA_body_length(TGAHeader))
            tmp_blob += TGAbody

            TGA_images.append(tmp_blob)

        return TGA_images

    def get_TGA_body_length(self, tga_header_blob):
        """Calculates the length of the TGA binary data with the information in the TGA header"""
        X, Y, BIT = self.get_TGA_info(tga_header_blob)
        length = (X * Y * BIT) / 8 + 1
        #print(int(length))
        return int(length)

    def get_TGA_info(self, tga_blob):
        """Retuns Type, xRes, yRes and BitDepth of the TGA file"""
        handle = BytesIO(tga_blob)
        read_int_buff = lambda x: int.from_bytes(header.read(x), byteorder='little', signed=False)

        header = handle.read(self.tga_header_length)
        if header == b'':
            return 0,0,0,0

        header = BytesIO(header)
        header.seek(12)
        xRes = read_int_buff(2)
        yRes = read_int_buff(2)
        Bit = read_int_buff(1)

        return xRes, yRes, Bit, tgaType

    def write_TGA(self, tga_binary, filename: str):
        with open(filename, 'wb') as tgafile:
            tgafile.write(tga_binary)
    