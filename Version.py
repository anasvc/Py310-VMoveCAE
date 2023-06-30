#!/usr/bin/env python
#----------------------------------------------------------------------------
# Name:         VctUtil.py
# Purpose:      Simple framework for running individual VCollab applications
#
# Author:       Mohan Varma
#
# Created:      25-July-2008
# Copyright:    (c) 2008 by Visual Collaboration Technologies Inc.
# Licence:      VCollab license
#----------------------------------------------------------------------------

"""
This program will load and run one of the individual VCollab applications in 
this directory within its own frame window. Just specify the application name
on the command line.
"""

import sys
#---------------------------------------------------------------------------
import os 

os.add_dll_directory(os.path.abspath("dll/odbapi/2022x"))
os.add_dll_directory(os.path.abspath("dll/zlib"))
os.add_dll_directory(os.path.abspath("dll/hdf5"))
os.add_dll_directory(os.path.abspath("dll/ccmio"))
os.add_dll_directory(os.path.abspath("dll/cgns"))
os.add_dll_directory(os.path.abspath("dll/license"))
# #os.add_dll_directory("D:/VMoveCAE-Classic/dependencies/python310")
# D:/VMoveCAE-Classic-2/VMoveCAE-Classic-Workshop

# os.add_dll_directory("./vki-devtools/dependencies/odbapi/windows/bin")
# os.add_dll_directory("./vki-devtools/dependencies/zlib/windows/bin")
# os.add_dll_directory("./vki-devtools/dependencies/hdf5/windows/bin")
# os.add_dll_directory("./vki-devtools/dependencies/libccmio/windows/x64/bin")
# os.add_dll_directory("./vki-devtools/dependencies/cgns/windows/bin")
# os.add_dll_directory("./license/bin")
# #----------------------------------------------------------------------------

def GetEngineName():
    return '_SuiteVersionWrap_x64_Release'
    

#----------------------------------------------------------------------------
#version_cpp_lib = __import__(GetEngineName())

#engine_cpp_lib = __import__('_CaeEngineWrap_x64_Release')
import _CaeEngineWrap_x64_Release as engine_cpp_lib

#----------------------------------------------------------------------------

#VERSION = version_cpp_lib.getSuiteVersion()
VERSION = "19.0"
        
#----------------------------------------------------------------------------

def app_name(base_name):
    #return version_cpp_lib.getApplicationName(base_name)
    return base_name.encode() #version_cpp_lib.getApplicationName(base_name)

#----------------------------------------------------------------------------

def app_name_ver(base_name):
    return '%s %s' % (app_name(base_name).decode(), VERSION)

#----------------------------------------------------------------------------

def main(argv):
    print(VERSION)

#----------------------------------------------------------------------------

if __name__ == '__main__':
    main(sys.argv)
