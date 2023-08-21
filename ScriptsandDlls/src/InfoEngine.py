'''
Created on Dec 13, 2011

@author: Mohan Varma
'''
import sys,os,time
import glob
import Extractor
import Common

#----------------------------------------------------------------------------

exptime = time.strptime('31-Dec-2009 23:59:59 GMT', '%d-%b-%Y %H:%M:%S GMT')

#----------------------------------------------------------------------------
class InfoEngine(object):
    def __init__(self):
        self.cpp_lib = __import__(Common.GetCaeInfoName())

    def setLogFile(self, file_path):
        self.cpp_lib.SetLogFile(file_path)
    
    def getFileWildCards(self):
        return self.cpp_lib.GetFileWildCards()

    def getInfo(self, options, args):
        return self.cpp_lib.GetCaeFileInfo(options, args)

def getEngine():
    engine = InfoEngine()
    return engine

def getDefaultTempFileName():
    return 'cae_info.log'

if __name__ == '__main__':
    pass
