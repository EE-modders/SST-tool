#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 05.01.2020 19:47 CET

@author: zocker_160

This is the main lib for SST files from Empire Earth
"""

class SST:
    def __init__(self, num_res=0, num_tiles=0, x_res=0, y_res=0, TGAbody=b''):
        self.header = {
            "first": b'\x00',
            "resolutions": num_res,
            "tiles": num_tiles,
            "placeholder": b'\x00\x00\x00',
            "x-res": x_res,
            "y-res": y_res,    
            "delimiter": b'\x00'
        }
        self.TGAbody = TGAbody

    def read_from_file(self, filename: str):
        with open(filename, 'rb') as sstfile:

            read_int_buff = lambda x: int.from_bytes(sstfile.read(x), byteorder="little", signed=False)

            print("parsing......")

            self.header["first"] = sstfile.read(1)
            self.header["resolutions"] = read_int_buff(1)
            self.header["tiles"] = read_int_buff(1)
            self.header["placeholder"] = sstfile.read(3)
            self.header["x-res"] = read_int_buff(4)
            self.header["y-res"] = read_int_buff(4)
            self.header["delimiter"] = sstfile.read(1)

            self.TGAbody = sstfile.read(-1)

    def write_to_file(self, filename: str):
        outputfile = filename

        with open(outputfile, 'wb') as sstfile:
            print("writing %s.......\n" % outputfile)

            sstfile.write(self.get_header_bytes() + self.TGAbody)


    def get_header_bytes(self):
        result = b''
        #print(self.header)
        result += self.header["first"]
        result += self.header["resolutions"].to_bytes(1, byteorder='little', signed=False) 
        result += self.header["tiles"].to_bytes(1, byteorder='little', signed=False)
        result += self.header["placeholder"]
        result += self.header["x-res"].to_bytes(4, byteorder='little', signed=False)
        result += self.header["y-res"].to_bytes(4, byteorder='little', signed=False)
        result += self.header["delimiter"]
        #print(result)
        return result

    def __str__(self):
        output = "SST Header: \n"

        header_tmp = self.header
        header_tmp.pop('first')
        header_tmp.pop('placeholder')        
        header_tmp.pop('delimiter')

        for key, value in header_tmp.items():
            output += "%s: %s \n" % (key, value)
        output += "\n"

        return output
