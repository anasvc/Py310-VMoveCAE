#!/usr/bin/python

# Copyright (C) 2018 Visual Collaboration Technologies Inc.
# All Rights Reserved. 
#
# This file is a property of Visual Collaboration Technologies Inc.
# Unauthorized access, reproduction or redistribution of any kind is prohibited.

import sys
import os
from enum import IntEnum
import re


class BlockType:
    NONE, OVERVIEW, RUN_SETTINGS, DESIGN_STUDY, USAGE_STATS, SUMMARY, END = range(7)


class RptFile:
    BLOCK_SEP = '------------------------------------------------------------'
    NUM_LOAD_SETS_LINE_RE = r'^(   Number of Load Sets: )(\d*)$'
    NUM_MODES_LINE_RE = r'^(   Number of Modes: )(\d*)$'

    def __init__(self):
        self.study_name = None
        self.study_folder = None
        self.analysis_name = None
        self.analysis_folder = None
        self.num_steps = None

    def read_from(self, fp):
        self.read_file(fp)
        self.infer_from_path(fp)
        
    def infer_from_path(self, fp):
        self.study_folder = os.path.dirname(fp)
        self.study_name = os.path.splitext(os.path.basename(fp))[0]
        self.analysis_folder = os.path.join(self.study_folder, self.analysis_name)

    def read_file(self, fp):
        file = open(fp, "r")
        block_type = BlockType.NONE
        block_line_num = 0;
        for line in file.readlines():
            line = line.rstrip()
            if line == RptFile.BLOCK_SEP:
                block_type = block_type + 1
                block_line_num = 0;
                if block_type == BlockType.END:
                    return
            elif block_type == BlockType.DESIGN_STUDY:
                if block_line_num == 4:
                    self.analysis_name = re.findall(r'\"(.+?)\"', line)[0]
                    if not self.analysis_name:
                        raise RuntimeError('Unable to identify analysis name')
                elif block_line_num > 4 and self.num_steps is None:
                    ls_match = re.match(RptFile.NUM_LOAD_SETS_LINE_RE, line)
                    ms_match = re.match(RptFile.NUM_MODES_LINE_RE, line)
                    if ls_match:
                        self.num_steps = int(ls_match.group(2))
                    if ms_match:
                        self.num_steps = int(ms_match.group(2))
            block_line_num += 1


def main(argv):
    if len(argv) == 0:
        return

    # ex: r'F:\Models\Public\ProMechanica\shaft1\shaft1.rpt'
    file_path = argv[1]
    rpt_file = RptFile()
    rpt_file.read_from(os.path.abspath(file_path))
    print(rpt_file.study_name, rpt_file.study_folder)
    print(rpt_file.analysis_name, rpt_file.analysis_folder)
    print(rpt_file.num_steps)


if __name__ == "__main__":
    sys.exit(main(sys.argv))

