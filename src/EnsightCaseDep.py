#!/usr/bin/python

# Copyright (C) 2018 Visual Collaboration Technologies Inc.
# All Rights Reserved. 
#
# This file is a property of Visual Collaboration Technologies Inc.
# Unauthorized access, reproduction or redistribution of any kind is prohibited.

import sys
import os
from enum import Enum
import shlex
from FileDepBase import FileInfo as Base


class SectionType(Enum):
    NONE = "NONE"
    FORMAT = "FORMAT"
    GEOMETRY = "GEOMETRY"
    VARIABLE = "VARIABLE"
    TIME = "TIME"
    FILE = "FILE"
    MATERIAL = "MATERIAL"
    SCRIPTS = "SCRIPTS"


def create_variable_vars():
    variable_vars = {'{} per {}'.format('constant', pos): 1
                  for pos in ['case file', 'part', 'part scalar']
    }
    variable_vars.update({'{} per {}'.format(typ, pos) : 1
                   for pos in ['node', 'element']
                   for typ in ['scalar', 'vector', 'tensor symm', 'tensor asym']
    })
    variable_vars.update({'{} per {}'.format(typ, pos) : 1
                   for pos in ['measured node']
                   for typ in ['scalar', 'vector']
    })
    variable_vars.update({'complex {} per {}'.format(typ, pos) : 2
                   for pos in ['node', 'element']
                   for typ in ['scalar', 'vector']
    })
    return variable_vars


section_vars = {
    SectionType.GEOMETRY: ['model', 'measured', 'match', 'boundary',
                             'rigid_body', 'Vector_glyphs'],
    SectionType.VARIABLE: create_variable_vars(),
    SectionType.SCRIPTS: ['metadata'],
    SectionType.MATERIAL: ['material {}'.format(v) for v in ['id per element',
                                         'mixed ids', 'mixed values']],
}

section_num_descr_cols = {
    SectionType.GEOMETRY: 0,
    SectionType.VARIABLE: 1,
    SectionType.SCRIPTS: 0,
    SectionType.MATERIAL: 0,
}


class FileInfo(Base):
    def __init__(self):
        Base.__init__(self)
    
    def read_from(self, fp):
        folder_path = os.path.dirname(os.path.abspath(fp))
        case_file = open(fp, "r")
        active_section = SectionType.NONE
        block_line_num = 0;
        for file_line in case_file.readlines():
            file_line = file_line.rstrip()

            # Skip empty lines
            if len(file_line) == 0:
                continue;

            # Skip comments
            if file_line[0] == '#':
                continue;
                
            flist = []
            if file_line in SectionType.__members__.keys():
                active_section = SectionType(file_line)
            else:
                for stype in [SectionType.GEOMETRY, SectionType.VARIABLE,
                                  SectionType.MATERIAL, SectionType.SCRIPTS]:
                    self._add_var_files(file_line, section_vars[stype],
                                  section_num_descr_cols[stype], flist)

            for fpath in flist:
                self.append(os.path.join(folder_path, fpath))

    def _add_var_files(self, file_line, sec_vars, ndescol, flist):
        VAR_SEP = ':'

        if isinstance(sec_vars, list):
            var_nfiles = {v:1 for v in sec_vars}
        else:
            var_nfiles = sec_vars

        varval = file_line.split(VAR_SEP, 2)
        if varval[0] not in var_nfiles.keys():
            return
        nfiles = var_nfiles[varval[0]]
        if nfiles == 0:
            return
        vl = shlex.split(varval[1], posix=True)
        floc = 0
        # Skip ts and fs
        while vl[floc].isdigit():
            floc += 1
        # Skip description columns
        floc += ndescol
        flist.extend(vl[floc:floc+nfiles])


def main(argv):
    if len(argv) == 0:
        return

    import glob
    # ex: r'F:\Models\Public\Ensight\ensight-samples\*\*.case'
    file_list = argv[1]
    for file_path in glob.glob(file_list):
        print(file_path)
        file_info = FileInfo()
        file_info.read_from(os.path.abspath(file_path))
        print(file_info.list)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
