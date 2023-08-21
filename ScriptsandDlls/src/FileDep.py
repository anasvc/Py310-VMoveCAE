#!/usr/bin/python

# Copyright (C) 2018 Visual Collaboration Technologies Inc.
# All Rights Reserved. 
#
# This file is a property of Visual Collaboration Technologies Inc.
# Unauthorized access, reproduction or redistribution of any kind is prohibited.

import os
import sys
from enum import Enum
import CreoStudyDep
import EnsightCaseDep


class FileType(Enum):
    ENSIGHT_CASE = 'ensight_case'
    CREO_STUDY = 'creo_study'


extensions = {
    '.case': FileType.ENSIGHT_CASE,
    '.neu': FileType.CREO_STUDY,
    '.rpt': FileType.CREO_STUDY,
    '.mdb': FileType.CREO_STUDY,
    '.mda': FileType.CREO_STUDY,
}


extractor = {
    FileType.ENSIGHT_CASE: EnsightCaseDep.FileInfo,
    FileType.CREO_STUDY: CreoStudyDep.FileInfo,
}


def detect_file_type(file_path):
    return extensions[os.path.splitext(file_path)[1]]


def file_dependencies(file_path, file_type = None):
    if not file_path:
        return None
    fp = os.path.abspath(file_path)
    ft = file_type

    if ft is None:
        ft = detect_file_type(fp)
    if ft is None:
        return None
    ex = extractor[ft]()
    ex.read_from(fp)
    return ex.rel_path_list()


def main(argv):
    if len(argv) == 0:
        return

    # ex: r'F:\Models\Public\ProMechanica\shaft1\shaft1.rpt'
    file_path = argv[1]
    file_type = None
    if len(argv) > 2:
        file_type = argv[2]
    dep_files = file_dependencies(file_path, file_type)
    print(dep_files)


if __name__ == "__main__":
    sys.exit(main(sys.argv))

