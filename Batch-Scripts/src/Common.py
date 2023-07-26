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
this directory within its own frame window.  Just specify the application name
on the command line.
"""

import sys,os,time
import platform
import glob
import Extractor
import shutil
import Version
if platform.python_version() < '2.4':
    from Compat import sorted

#----------------------------------------------------------------------------

def GetArchitecture():
    osname = platform.system()
    ostype = platform.architecture()[0]
    uname = platform.uname()

    arch = None
    if 'Windows' == osname:
        arch = 'win'
    elif 'Linux' == osname:
        arch = 'linux'
    else:
        raise Exception('\nUnknown Operating System.')
    if '32bit' == ostype:
        arch += '32'
    elif '64bit' == ostype:
        arch += '64'
    else:
        raise Exception('\nUnknown Operating System.')

    return arch

#----------------------------------------------------------------------------

def GetCaeEngineName():
    cpplibs = { 'win32' : '_CaeEngineWrap_Win32_Release',
                'win64' : '_CaeEngineWrap_x64_Release' };
    return cpplibs.get(GetArchitecture(), '_CaeEngineWrap')

#----------------------------------------------------------------------------

def GetCaeInfoName():
    cpplibs = { 'win32' : '_CaeInfoWrap_Win32_Release',
                'win64' : '_CaeInfoWrap_x64_Release' };
    return cpplibs.get(GetArchitecture(), '_CaeInfoWrap')

#----------------------------------------------------------------------------

class TempFolder:
    def __init__(self):
        self.temp_folder = None
        self.files_to_retain = []

    def getTempRoot(self):
        temp_folder = os.environ.get('VCOLLAB_TEMP_PATH')

        if not temp_folder:
            arch = GetArchitecture()
            if arch in ['win32', 'win64']:
                temp_folder = os.environ.get('TEMP')
                #dir = os.path.expanduser('~')
            else:
                temp_folder = os.path.expanduser('/tmp')

        if not temp_folder:
            temp_folder = os.getcwd()

        return temp_folder

    def create(self):
        if self.temp_folder:
            return

        self.temp_folder = self.getTempRoot()
        if self.temp_folder:
            #folder_name = Version.app_name('VMoveCAE') + '-run-' + time.strftime("%Y-%m-%d-%H-%M-%S") + '-' + repr(os.getpid())
            folder_name = "test"
            self.temp_folder = os.path.join(self.temp_folder, folder_name)
                        

        if self.temp_folder:
            try:
                os.mkdir(self.temp_folder)
            except OSError:
                pass
        else:
            self.temp_folder = None

    def retainFiles(self, files):
        if isinstance(files, list):
            self.files_to_retain.extend(files);
        else:
            self.files_to_retain.append(files);

    def clearOld(self, num_to_retain):
        tmp_root = self.getTempRoot()
        cur_time = time.time()
        if self.temp_folder:
            tmp_root = os.path.abspath(os.path.join(self.temp_folder, os.pardir))
        tmp_list = glob.glob(tmp_root + os.sep + 'VMoveCAE-run-*-*-*-*-*-*-*')
        if self.temp_folder:
            tmp_list.remove(self.temp_folder)
        tmp_slist = sorted(tmp_list, key=os.path.getmtime)
        tmp_slist.reverse()
        del tmp_slist[0:num_to_retain]
        for folder_path in tmp_slist:
            if os.path.isdir(folder_path) and not os.path.islink(folder_path):
                sec_old = cur_time - os.path.getmtime(folder_path)
                days_old = sec_old / 86400
                if days_old > 2:
                  shutil.rmtree(folder_path)
    
    def destroy(self):
        if not self.temp_folder:
            return

        print ('Deleting temporary files ...')
        for item in os.listdir(self.temp_folder):
            file_path = os.path.join(self.temp_folder, item)
            if os.path.isdir(file_path) and not os.path.islink(file_path):
                shutil.rmtree(file_path)
            elif file_path not in self.files_to_retain:
                try:
                    os.unlink(file_path)
                except Exception as e:
                    pass
        
        self.temp_folder = None

    def getPath(self):
        return self.temp_folder

#----------------------------------------------------------------------------

def ExtractedFiles(in_path, out_folder, wildcard, use_local_cache = False):
    Extractor.settings.enableLocalCaching(use_local_cache)
    wcards = [item for item in wildcard.split('|')[1].split(';') \
                                if not Extractor.get_extractor(item)]
    extractor = Extractor.get_extractor(in_path, Extractor.default_root_folder_level)
    matcher = Extractor.Matcher(wcards)

    if extractor:
        return Extractor.extract(extractor, in_path, out_folder, matcher.check)

    return [in_path], [in_path]

#----------------------------------------------------------------------------

def GetSizeRepr(self, size):
    mbdenom = 1024 * 1024
    kbdenom = 1024
    if size / mbdenom > 1:
        return '%.2f MB' % (size/mbdenom)
    elif size / kbdenom > 1:
        return '%.2f KB' % (size/kbdenom)
    else:
        return '%.2f B' % size

#----------------------------------------------------------------------------

def GetExtendedFilesSize(self, fname, endswith):
    if fname.endswith(endswith):
        size = 0.0
        flist = glob.glob(fname + "*")
        for f in flist:
            added = f.replace(fname, '')
            if not added.strip('0123456789'):
                size += os.path.getsize(f)
        return GetSizeRepr(size)
    else:
        return GetSizeRepr(os.path.getsize(fname))
        
#----------------------------------------------------------------------------

def main(argv):
    print (GetArchitecture())
    print (GetCaeEngineName())
    #print GetTempFolder()

#----------------------------------------------------------------------------

if __name__ == '__main__':
    main(sys.argv)
