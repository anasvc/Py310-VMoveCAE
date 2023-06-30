#!/usr/bin/env python
#----------------------------------------------------------------------------
# Name:         InpFileReader.py
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
import platform
if platform.python_version() > '2.5':
    import xml.etree.ElementTree as et
else:
    import elementtree.ElementTree as et

#----------------------------------------------------------------------------

class InpFileError(Exception):
    '''Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    '''

    def __init__(self, message):
        if platform.python_version() > '2.5':
            self.msg = message
        else:
            self.message = message

    def __str__(self):
        if platform.python_version() > '2.5':
            return repr(self.msg)
        else:
            return repr(self.message)

#----------------------------------------------------------------------------

def ReplaceComments(string, comment_char = '#'):
    if not string:
        return string, None
    
    pos = string.find(comment_char)
    if -1 != pos:
            comment = string[pos:].strip(' \t\n'+comment_char)
            if comment:
                comment = '<!-- ' + comment + ' -->'
            return string[0:pos].strip(), comment

    return string, None
    
#----------------------------------------------------------------------------

def ReplaceHeadings(string, headings):
    if not string:
        return string
    
    string = string.strip()

    if string == '[]' and len(headings):
        last = headings.pop()
        return '</%s>' %(last)

    if not string:
        return string
    
    if string[0] == '[' and string[-1] == ']':
        string = string.lstrip('["').rstrip('"]')
        headings.append(string)
        return '<%s>' %(string)

    return string
    
#----------------------------------------------------------------------------

def ReplacePairs(string, separator = '=', 
                attribute_tag = 'attribute', 
                key_tag = 'key', value_tag = 'value'):
    if not string:
        return string

    string = string.strip()
    pos = string.find(separator)
    if -1 != pos:
        key = string[0:pos].strip(' \t\n"')
        value = string[pos+1:].strip(' \t\n"')
        return '<%s %s="%s" %s="%s" />' %(attribute_tag, key_tag, key, value_tag, value)

    return string
        
#----------------------------------------------------------------------------

class InpFileReader:
    def __init__(self, comment_prefix = '#', separator = '=', 
                    attribute_tag = 'attribute', 
                    key_tag = 'key', value_tag = 'value'):

        self.comment_prefix = comment_prefix
        self.separator = separator
        self.attribute_tag = attribute_tag
        self.key_tag = key_tag
        self.value_tag = value_tag

        self.lines = []
        
    def FromString(self, text):
        self.lines = text.split('\n')

    def ReadFile(self, file_name):
        file = open(file_name, 'r')

        if file:
            self.lines = file.readlines()
            file.close()

    def GetXmlString(self):
        altered_lines = []
        headings = []

        for line in self.lines:
            altered = self.LineToXml(line, headings)
            if altered:
                altered.strip()
                altered_lines.append(altered)

        return '<?xml version="1.0" encoding="iso-8859-1" ?>\n' + '\n'.join(altered_lines)

    def GetXmlTree(self):
        xml_tree = None
        try:
            xml_tree = et.fromstring(self.GetXmlString())
        except Exception as ex:
            raise InpFileError(str(ex))

        return xml_tree

    def LineToXml(self, string, headings):
        if not string:
            return string

        altered, comment = ReplaceComments(string, 
                            comment_char = self.comment_prefix)
        altered = ReplaceHeadings(altered, headings)
        altered = ReplacePairs(altered, separator = self.separator, 
                        attribute_tag = self.attribute_tag,
                        key_tag = self.key_tag, value_tag = self.value_tag)

        if comment:
            altered = altered + comment

        return altered
        
#----------------------------------------------------------------------------

def main(argv):
    if len(argv) < 2:
        argv += ["test.inp"]

    reader = InpFileReader()
    reader.ReadFile(argv[1])
    xml_tree = reader.GetXmlTree()

#----------------------------------------------------------------------------

if __name__ == "__main__":
    main(sys.argv)

