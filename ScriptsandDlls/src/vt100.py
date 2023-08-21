#!/usr/bin/env python

# Copyright (C) 2018 Visual Collaboration Technologies Inc.
# All Rights Reserved. 
#
# Thils file is a property of Visual Collaboration Technologis Inc.
# Unauthorized access, reproduction or redistribution of any kind is prohibited.

import platform

################################################################################
def enable_vt100_support():
    """
    Enabled VT100 terminal supporting ASCII escape codes.
    This code is a copy of a patch submitted to Python. Please look at the
    folowing web page.
    https://bugs.python.org/issue29059
    """

    if platform.system().lower() != 'windows':
        return

    from ctypes import windll, c_int, byref
    stdout_handle = windll.kernel32.GetStdHandle(c_int(-11))
    mode = c_int(0)
    windll.kernel32.GetConsoleMode(c_int(stdout_handle), byref(mode))
    mode = c_int(mode.value | 4)
    windll.kernel32.SetConsoleMode(c_int(stdout_handle), mode)

################################################################################

def test():
    pass

################################################################################

if __name__ == "__main__":
    test()

