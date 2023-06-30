#!/usr/bin/env python
#----------------------------------------------------------------------------
# Name:         ConfigFileReader.py
# Purpose:      Loads the input files of VMoveCAE 2006 
#
# Author:       Mohan Varma
#
# Created:      30-March-2009
# Copyright:    (c) 2009 by Visual Collaboration Technologies Inc.
# Licence:      VCollab license
#----------------------------------------------------------------------------

"""
This program will load and run one of the individual VCollab applications in 
this directory within its own frame window.  Just specify the application name
on the command line.
"""

import sys, os
from DictKeyIc import DictKeyIc
#----------------------------------------------------------------------------

#DictKeyIc = dict
class ConfigFileReader:
    def __init__(self, comment_prefix = '#', separator = '=', delimiter = '\035'):

        self.comment_prefix = comment_prefix
        self.separator = separator
        self.delimiter = delimiter

        self.headings = []
        self.pairs = DictKeyIc()
        
    def ReadFile(self, file_name):
        file = open(file_name, 'r')

        if file:
            self.headings = []
            self.pairs = DictKeyIc()

            lines = file.readlines()

            for line in lines:
                line = line.strip()
                line = self.StripComments(line)
                line = self.ExtractHeading(line)
                self.ExtractPair(line)

            file.close()

        return self.pairs

    def StripComments(self, string):
        if not string:
            return string

        pos = string.find(self.comment_prefix)
        if -1 != pos:
            single = string.count("'", 0, pos)
            double = string.count('"', 0, pos)
            if single % 2 or double % 2:
                return string
            string = string[0:pos]
            string = string.strip()

        return string

    def ExtractHeading(self, string):
        if not string:
            return string
        
        if string == '[]' and len(self.headings):
            self.headings.pop()
            return ''

        if string[0] == '[' and string[-1] == ']':
            string = string.lstrip('[').rstrip(']').lstrip('"').rstrip('"')
            self.headings.append(string)
            return ''

        return string
        
    def ExtractPair(self, string):
        if not string:
            return string

        pos = string.find(self.separator)
        if -1 != pos:
            key = string[0:pos].strip().lstrip('"').rstrip('"')
            value = string[pos+1:].strip().lstrip('"').rstrip('"')
            key = self.delimiter + self.delimiter.join(self.headings) + self.delimiter + key
            self.pairs[key] = value
            return ''

        return ''
        

#----------------------------------------------------------------------------

def main(argv):
    if len(argv) < 2:
        argv += ["inputs.txt"]

    reader = ConfigFileReader()
    reader.ReadFile(argv[1])

#----------------------------------------------------------------------------

if __name__ == "__main__":
    main(sys.argv)

