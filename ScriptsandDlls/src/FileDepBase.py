#!/usr/bin/python

# Copyright (C) 2018 Visual Collaboration Technologies Inc.
# All Rights Reserved. 
#
# This file is a property of Visual Collaboration Technologies Inc.
# Unauthorized access, reproduction or redistribution of any kind is prohibited.

import os


class FileInfo:
    def __init__(self):
        self.list = []

    def append(self, fp):
        self.list.append(str(fp))

    def extend(self, fps):
        [self.list.append(str(fp)) for fp in fps]

    @staticmethod
    def norm_path(fp):
        return os.path.relpath(fp).replace('\\', '/').replace('*', '?').replace('#', '?')

    def rel_path_list(self):
        return [FileInfo.norm_path(f) for f in self.list]
