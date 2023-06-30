#!/usr/bin/env python
#----------------------------------------------------------------------------
# Name:         Extractor.py
# Purpose:      Extracts contents from compressed files
#
# Author:       Mohan Varma
#
# Created:      20-Sept-2010
# Copyright:    (c) 2010 by Visual Collaboration Technologies Inc.
# Licence:      VCollab license
#----------------------------------------------------------------------------

"""
This program will load a archive or compressed file and extracts its contents. 
"""
import os, sys
import zipfile, tarfile
import gzip, bz2
import fnmatch
import subprocess
import shutil
import time

#----------------------------------------------------------------------------

class Settings:
  
    def __init__(self):
        self.cache_to_local_folder = False

    def enableLocalCaching(self, onoff):
        self.cache_to_local_folder = onoff

    def isLocalCachingEnabled(self):
        return self.cache_to_local_folder

#----------------------------------------------------------------------------

settings = Settings()

#----------------------------------------------------------------------------

class ExtractorBase:

    def __init__(self):
        self.in_file = None
        self.file_contents = None

    def open(self, in_path):
        if self.in_file:
            self.in_file.close()

    def contents(self):
        return self.file_contents

    def close(self):
        if self.in_file:
            self.in_file.close()

        self.in_file = None
        self.file_contents = None

#----------------------------------------------------------------------------

class Uncompressor(ExtractorBase):

    def __init__(self, open_method, block_size):
        ExtractorBase.__init__(self)
        self.open_method = open_method
        self.open_mode = 'rb'
        self.block_size = block_size

    def open(self, in_path):
        ExtractorBase.open(self, in_path)
        self.in_file = self.open_method(in_path, self.open_mode)
        self.file_contents = [os.path.splitext(os.path.basename(in_path))[0]]

    def extract(self, out_folder):
        out_path = out_folder + os.sep + self.file_contents[0]
        out_file = open(out_path, 'wb')
        while True:
            data = self.in_file.read(self.block_size)
            if data:
                out_file.write(data)
            else:
                break;
        return out_path

#----------------------------------------------------------------------------

class Unpacker(ExtractorBase):

    def __init__(self, open_method, contents_method, open_mode = ''):
        ExtractorBase.__init__(self)
        self.open_method = open_method
        self.open_mode = 'r'
        if open_mode:
            self.open_mode = ('r:' + open_mode)
        self.contents_method = contents_method
        self.files_to_extract = None

    def open(self, in_path):
        ExtractorBase.open(self, in_path)
        self.in_file = self.open_method(in_path, self.open_mode)
        self.file_contents = getattr(self.in_file, self.contents_method)()

    def extract(self, out_folder):
        self.in_file.extractall(out_folder, self.files_to_extract)
        return [(out_folder + os.sep + name) for name in self.file_contents]

#----------------------------------------------------------------------------

class UncompressExecutor(ExtractorBase):

    def __init__(self, exe_path):
        ExtractorBase.__init__(self)
        self.exe_path = exe_path
        self.in_path = None

    def open(self, in_path):
        ExtractorBase.open(self, in_path)
        if os.access(in_path, os.R_OK) and os.path.isfile(in_path):
            self.in_path = in_path
        self.file_contents = [os.path.splitext(os.path.basename(in_path))[0]]

    def extract(self, out_folder):
        out_path = out_folder + os.sep + self.file_contents[0]
        retcode = subprocess.call([self.exe_path, self.in_path, out_path])
        if retcode:
            return None
        else:
            return out_path

#----------------------------------------------------------------------------

class FemunzipExecutor(ExtractorBase):

    def __init__(self, exe_path):
        ExtractorBase.__init__(self)
        self.exe_path = exe_path
        self.in_path = None

    def open(self, in_path):
        ExtractorBase.open(self, in_path)
        if os.access(in_path, os.R_OK) and os.path.isfile(in_path):
            self.in_path = in_path
        self.file_contents = ['d3plot']

    def extract(self, out_folder):
        out_path = out_folder + os.sep + self.file_contents[0]
        if not self.exe_path:
            raise RuntimeError('Unable to locate femunzip unexecutable')
        print ('Using Femunzip to extract files ...')
        retcode = subprocess.call([self.exe_path, "-I", self.in_path, "-O", out_path])
        if retcode:
            print ('Using Femunzip to extract files ... failed')
            return None
        else:
            print ('Using Femunzip to extract files ... done')
            return out_path

#----------------------------------------------------------------------------

block_size = 50 * 1024 * 1024

#----------------------------------------------------------------------------

class CachedFile(ExtractorBase):

    def __init__(self, level = 0):
        ExtractorBase.__init__(self)
        self.in_file = None
        self.level = level
        self.src_tree = None
        self.out_path = None

    def path_of_level(self, in_path, level):
        return os.path.realpath(os.path.join(in_path, *[os.pardir for i in range(level)]))

    def open(self, in_path):
        ExtractorBase.open(self, in_path)
        self.src_tree = self.path_of_level(in_path, self.level)
        self.out_path = os.path.relpath(in_path, self.path_of_level(in_path, self.level + 1))
        self.file_contents = [self.out_path]

    def extract(self, out_folder):
        try:
            dst = os.path.join(out_folder, os.path.basename(self.src_tree))
            out_path = os.path.join(out_folder, self.out_path)
            if self.level == 0:
                start = time.process_time()
                print ('Copying file \"', self.src_tree, '\" to \"', dst, '\" ...')
                shutil.copyfile(self.src_tree, dst)
                end = time.process_time()
                print ('Time taken for copying = %s seconds' %(end-start))
                return out_path
            else:
                print ('Copying folder \"', self.src_tree, '\" to \"', dst, '\" ...')
                start = time.process_time()
                shutil.copytree(self.src_tree, dst)
                end = time.process_time()
                print ('Time taken for copying = %s seconds' %(end-start))
                return out_path
        except IOError:
            if self.level == 0:
                print ('Copying failed.')
            else:
                print ('Copying folder \"', self.src_tree, '\" to \"', dst, '\" ... failed')
            return None

#----------------------------------------------------------------------------

extractors = None

#----------------------------------------------------------------------------

def get_femzip_dyna_path():
    use_femunzip_key = 'VMOVECAE_USE_FEMUNZIP'
    use_femunzip_value = os.environ.get(use_femunzip_key)
    femunzip_path_key = 'VMOVECAE_FEMUNZIP_DYNA_PATH'
    femunzip_path = os.environ.get(femunzip_path_key)

    if not use_femunzip_value:
        return None
    if use_femunzip_value != '1':
        return None
    if not femunzip_path:
        return None
    if not os.path.isfile(femunzip_path):
        return None
    if not os.access(femunzip_path, os.X_OK):
        return None

    return femunzip_path

#----------------------------------------------------------------------------

femunzip_path = get_femzip_dyna_path()
if femunzip_path:
    extractors = [
        {'extractor': Unpacker(zipfile.ZipFile, 'namelist'), 
                    'default_extension': '.zip'},
        {'extractor': Unpacker(tarfile.open, 'getnames'), 
                    'default_extension': '.tar'},
        {'extractor': Unpacker(tarfile.open, 'getnames', 'gz'), 
                    'default_extension': '.tgz'},
        {'extractor': Unpacker(tarfile.open, 'getnames', 'gz'), 
                    'default_extension': '.tar.gz'},
        {'extractor': Unpacker(tarfile.open, 'getnames', 'bz2'), 
                    'default_extension': '.tar.bz2'},
        {'extractor': Uncompressor(gzip.GzipFile, block_size), 
                    'default_extension': '.gzclock'},
        {'extractor': Uncompressor(bz2.BZ2File, block_size), 
                    'default_extension': '.bz2'},
        {'extractor': FemunzipExecutor(femunzip_path), 
                    'default_pattern': ['*.fz', 'Zd3plot*']},
    ]
else:
    extractors = [
        {'extractor': Unpacker(zipfile.ZipFile, 'namelist'), 
                    'default_extension': '.zip'},
        {'extractor': Unpacker(tarfile.open, 'getnames'), 
                    'default_extension': '.tar'},
        {'extractor': Unpacker(tarfile.open, 'getnames', 'gz'), 
                    'default_extension': '.tgz'},
        {'extractor': Unpacker(tarfile.open, 'getnames', 'gz'), 
                    'default_extension': '.tar.gz'},
        {'extractor': Unpacker(tarfile.open, 'getnames', 'bz2'), 
                    'default_extension': '.tar.bz2'},
        {'extractor': Uncompressor(gzip.GzipFile, block_size), 
                    'default_extension': '.gz'},
        {'extractor': Uncompressor(bz2.BZ2File, block_size), 
                    'default_extension': '.bz2'},
    ]

#----------------------------------------------------------------------------

def get_extractor(in_path, root_level_getter = None):
    for item in extractors:
        if 'default_extension' in item:
            if in_path.endswith(item['default_extension']):
                return item['extractor']
        else:
            if 'default_pattern' in item:
                patterns = item.get('default_pattern')
                (file_folder, file_name) = os.path.split(in_path)
                for pattern in patterns:
                    if fnmatch.fnmatch(file_name, pattern):
                        return item['extractor']

    if settings.isLocalCachingEnabled():
        if root_level_getter:
            return CachedFile(root_level_getter.get(in_path))
        else:
            return CachedFile()

    return None

#---------------------------------------------------------------------------

def extract(extractor, in_path, out_folder, checker = None):
    #usable = lambda path: True if not checker or checker(path) else False
    extractor.open(in_path)
    contents = extractor.contents()
    #usable_contents = [name for name in contents if usable(name)]
    usable_contents = [name for name in contents if not checker or checker(name)]
    #usable_contents = [name for name in contents if usable(name)]
    #extracted = None if contents and not usable_contents \
    #                 else extractor.extract(out_folder)
    extracted = None
    if not contents or usable_contents:
        extracted = extractor.extract(out_folder)
    extractor.close()
    if not extracted:
        return None
    elif isinstance(extracted, list):
        #return extracted, [path for path in extracted if usable(path)]
        return extracted, [path for path in extracted if not checker or checker(path)]
    elif not checker or checker(extracted):
        return [extracted], [extracted]
    else:
        return None

#----------------------------------------------------------------------------
class Matcher:

    def __init__(self, patterns):
        self.patterns = patterns

    def check(self, path):
        #return True if not self.patterns or [ptrn for ptrn in self.patterns 
        #                if fnmatch.fnmatch(path, ptrn)] else False
        if not self.patterns:
            return True
        if [ptrn for ptrn in self.patterns if fnmatch.fnmatch(path, ptrn)]:
            return True
        return False

#----------------------------------------------------------------------------

class DefaultRootFolderLevel:

    def __init__(self):
        self.file_extn_dict = { '.d3plot': 1, '.ptf': 1, '.case': 1, '.neu': 2, }
        self.file_name_dict = { 'd3plot': 1, 'controlDict': 2, }

    def get(self, file_path):
        [name, ext] = os.path.splitext(os.path.basename(file_path))
        if ext:
            return self.file_extn_dict.get(ext, 0)
        else:
            return self.file_name_dict.get(name, 0)

#----------------------------------------------------------------------------

default_root_folder_level = DefaultRootFolderLevel()

#----------------------------------------------------------------------------

def main(argv):
    if len(argv) < 2:
        print ('usage: ' + argv[0] + ' <archive_file>')
        return

    settings.enableLocalCaching(True)
    pchecker = Matcher(['*d3plot', '*.op2', '*.rst', '*.ptf', '*controlDict'])
    out_folder = 'f:\\temp\\vctemp\\extract-test\\out'
    in_file = argv[1]
    extractor = get_extractor(in_file, default_root_folder_level)
    valid_out_file = extract(extractor, in_file, out_folder, pchecker.check)
    print (valid_out_file)

#----------------------------------------------------------------------------

if __name__ == "__main__":
    main(sys.argv)

