#!/usr/bin/python

# Copyright (C) 2018 Visual Collaboration Technologies Inc.
# All Rights Reserved. 
#
# This file is a property of Visual Collaboration Technologies Inc.
# Unauthorized access, reproduction or redistribution of any kind is prohibited.

import os
import sys
from enum import IntEnum
from FileDepBase import FileInfo as Base
from RptFileDep import RptFile


class FileType(IntEnum):
    NEU, RPT, MDB, MDA, PNU, TER = range(6)
    

file_extension = { v: '.{}'.format(k.lower()) for k, v in FileType.__members__.items() }


class FileInfo(Base, RptFile):
    def __init__(self):
        Base.__init__(self)
        RptFile.__init__(self)
    
    def read_from(self, fp):
        fbase, extn = os.path.splitext(fp)
        if extn == file_extension[FileType.NEU]:
            self.init_from_neu(fp)
        elif extn == file_extension[FileType.RPT]:
            RptFile.read_from(self, fp)
        elif extn == file_extension[FileType.MDB]:
            RptFile.read_from(self, fbase + file_extension[FileType.RPT])
        elif extn == file_extension[FileType.MDA]:
            RptFile.read_from(self, fbase + file_extension[FileType.RPT])
        self.add_dep_files()
        
    def init_from_neu(self, fp):
        self.analysis_folder = os.path.dirname(fp)
        #self.study_name = os.path.splitext(os.path.basename(self.analysis_folder))[0]
        self.study_name = os.path.splitext(os.path.basename(fp))[0]
        self.analysis_name = os.path.splitext(os.path.basename(self.analysis_folder))[0]
        self.study_folder = os.path.dirname(self.analysis_folder)
        
    def add_dep_files(self):
        study_folder = os.path.relpath(self.study_folder)
        analysis_folder = os.path.relpath(self.analysis_folder)
        for ftype in [FileType.RPT, FileType.PNU]:
            self.append(os.path.join(study_folder,
                                self.study_name + file_extension[ftype]))
        for ftype in [FileType.NEU, FileType.TER]:
            self.append(os.path.join(analysis_folder,
                                self.study_name + file_extension[ftype]))
        for ftype in ['d', 's', 'r']:
            self.append(os.path.join(analysis_folder, 
                                self.study_name + '.{}##'.format(ftype)))


def main(argv):
    if len(argv) == 0:
        return

    # ex: r'F:\Models\Public\ProMechanica\shaft1\shaft1.rpt'
    # ex: r'F:\Models\Public\ProMechanica\shaft1\anlys1\shaft1.neu'
    # ex: r'F:\Models\Public\ProMechanica\shaft1\shaft1.mdb'
    # ex: r'F:\Models\Public\ProMechanica\shaft1\shaft1.mda'
    file_path = argv[1]
    file_info = FileInfo()
    file_info.read_from(os.path.abspath(file_path))
    print(file_info.study_name, file_info.study_folder)
    print(file_info.analysis_name, file_info.analysis_folder)
    print(file_info.num_steps)
    print(file_info.list)


if __name__ == "__main__":
    sys.exit(main(sys.argv))

