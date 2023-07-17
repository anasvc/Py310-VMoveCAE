from distutils.core import setup
import py2exe
import sys
import glob
import os

import platform
import Version
import Common

# If run without args, build executables, in quiet mode.
if len(sys.argv) == 1:
    sys.argv.append("py2exe")
    sys.argv.append("-q")

#
# The following will copy the MSVC run time dll's
# (msvcm90.dll, msvcp90.dll and msvcr90.dll) and
# the Microsoft.VC90.CRT.manifest which I keep in the
# "Py26MSdlls" folder to the dist folder
#
# depending on wx widgets you use, you might need to add
# gdiplus.dll to the above collection

#py26MSdll = glob.glob(r"x86_Microsoft.VC90.CRT\*.*")

# following works from Windows XP +
# if you need to deploy to older MS Win versions then I found that on Win2K
# it will also work if the files are put into the application folder without
# using a sub-folder.
#data_files = [("Microsoft.VC90.CRT", py26MSdll),
#               ("lib\Microsoft.VC90.CRT", py26MSdll),
#              ]
class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)

        # for the versioninfo resources
        self.comments = "Release"
        #self.comments = "Beta"
        arch = Common.GetArchitecture()
        suite_ver = Version.VERSION
        if arch in ['win64', 'linux64']:
            self.comments += ", 64-bit"
        self.internal_name = ''
        self.version = "2.1.223.331"
        self.company_name = "Visual Collaboration Technologies Inc."
        self.copyright = "Copyright (C) 2008-2023"
        self.name = "VMoveCAE %s" % (suite_ver)
        self.special_build_description = ''

VMoveCAEApp = Target(
    # used for the versioninfo resource
    description = "VMoveCAE Translator",

    # what to build
    script = "VMoveCAE.py",
    icon_resources = [(1, 'VMoveCAE.ico')])

VMoveCAEBatch = Target(
    # used for the versioninfo resource
    description = "VMoveCAE Batch Translator",

    # what to build
    script = "VMoveCAEBatch.py",
    icon_resources = [(1, 'VMoveCAE.ico')])

CaeInfo = Target(
    # used for the versioninfo resource
    description = "CaeInfo Metadata Extractor",

    # what to build
    script = "CaeInfo.py",
    icon_resources = [(1, 'VMoveCAE.ico')])

VMoveCAEValidate = Target(
    # used for the versioninfo resource
    description = "VMoveCAE Input Validator",

    # what to build
    script = "VMoveCAEValidate.py")

VMoveCAESubmit = Target(
    # used for the versioninfo resource
    description = "VMoveCAE Batch Submit Application",

    # what to build
    script = "VMoveCAESubmit.py")

sys_dll_list = [ 
    'msvcp90.dll', 
    'msvcp100.dll',
    'kernel32.dll',
    'user32.dll',
    'comdlg32.dll',
    'ole32.dll',
    'oleaut32.dll',
    'ws2_32.dll',
    'netapi32.dll',
    'psapi.dll',
    'advapi32.dll',
    'api-ms-win-core-string-l1-1-0.dll',
    'api-ms-win-core-memory-l1-1-2.dll',
    'api-ms-win-core-file-l1-2-1.dll',
    'api-ms-win-core-libraryloader-l1-2-2.dll',
    'api-ms-win-core-registry-l1-1-0.dll',
    'api-ms-win-core-string-l2-1-0.dll',
    'api-ms-win-core-profile-l1-1-0.dll',
    'api-ms-win-core-string-obsolete-l1-1-0.dll',
    'api-ms-win-core-debug-l1-1-1.dll',
    'api-ms-win-core-localization-obsolete-l1-3-0.dll',
    'api-ms-win-core-sidebyside-l1-1-0.dll',
    'api-ms-win-core-processthreads-l1-1-2.dll',
    'api-ms-win-core-kernel32-legacy-l1-1-1.dll',
    'api-ms-win-core-handle-l1-1-0.dll',
    'api-ms-win-core-timezone-l1-1-0.dll',
    'api-ms-win-core-processenvironment-l1-2-0.dll',
    'api-ms-win-core-util-l1-1-0.dll',
    'api-ms-win-core-atoms-l1-1-0.dll',
    'api-ms-win-core-winrt-error-l1-1-1.dll',
    'api-ms-win-security-base-l1-2-0.dll',
    'api-ms-win-core-heap-l2-1-0.dll',
    'api-ms-win-core-delayload-l1-1-1.dll',
    'api-ms-win-core-rtlsupport-l1-2-0.dll',
    'api-ms-win-core-libraryloader-l1-2-0.dll',
    'api-ms-win-core-localization-l1-2-1.dll',
    'api-ms-win-core-sysinfo-l1-2-1.dll',
    'api-ms-win-core-synch-l1-2-0.dll',
    'api-ms-win-core-errorhandling-l1-1-1.dll',
    'api-ms-win-core-shlwapi-obsolete-l1-2-0.dll',
    'api-ms-win-core-heap-l1-2-0.dll',
    'api-ms-win-core-crt-l1-1-0.dll',
    'api-ms-win-core-crt-l2-1-0.dll',
    'api-ms-win-core-heap-obsolete-l1-1-0.dll',
    'api-ms-win-core-io-l1-1-1.dll',
    'api-ms-win-service-management-l1-1-0.dll',
    'api-ms-win-core-libraryloader-l1-2-1.dll',
    'api-ms-win-security-base-l1-1-0.dll',
    'api-ms-win-core-localization-obsolete-l1-2-0.dll',
    'api-ms-win-core-delayload-l1-1-0.dll',
    'api-ms-win-core-kernel32-legacy-l1-1-0.dll',
    'api-ms-win-core-winrt-error-l1-1-0.dll',
    'api-ms-win-core-shlwapi-obsolete-l1-1-0.dll',
    'api-ms-win-core-io-l1-1-0.dll',
    'api-ms-win-core-threadpool-l1-2-0.dll',
    'api-ms-win-core-rtlsupport-l1-1-0.dll',
    'api-ms-win-core-heap-l1-1-0.dll',
    'api-ms-win-core-localization-l1-2-0.dll',
    'api-ms-win-core-memory-l1-1-0.dll',
    'api-ms-win-core-file-l1-1-0.dll',
    'api-ms-win-core-processenvironment-l1-1-0.dll',
    'api-ms-win-core-processthreads-l1-1-0.dll',
    'api-ms-win-core-errorhandling-l1-1-0.dll',
    'api-ms-win-core-synch-l1-1-0.dll',
    'api-ms-win-core-debug-l1-1-0.dll',
    'api-ms-win-core-sysinfo-l1-1-0.dll',
    'api-ms-win-downlevel-kernel32-l1-1-0.dll',
    'api-ms-win-crt-heap-l1-1-0.dll',
    'api-ms-win-crt-string-l1-1-0.dll',
    'api-ms-win-crt-runtime-l1-1-0.dll',
    'api-ms-win-crt-stdio-l1-1-0.dll',
    'api-ms-win-crt-convert-l1-1-0.dll',
    'api-ms-win-crt-filesystem-l1-1-0.dll',
    'api-ms-win-crt-math-l1-1-0.dll',
    'api-ms-win-crt-utility-l1-1-0.dll',
    'api-ms-win-crt-environment-l1-1-0.dll',
    'api-ms-win-crt-time-l1-1-0.dll',
    'api-ms-win-crt-locale-l1-1-0.dll',
    'api-ms-win-core-apiquery-l1-1-0.dll',
    'lapi.dll',
    ]

#setup( data_files = data_files, 
setup(
        windows=[VMoveCAEApp], console=[
            VMoveCAEBatch, CaeInfo,
            VMoveCAEValidate, VMoveCAESubmit,
        ],
        options = {"py2exe": {"compressed":1, 
            "optimize":2, 
            "dll_excludes": sys_dll_list,
            "packages":["VMoveCAE", "VMoveCAEBatch",
                        "VMoveCAESubmit",
                        "CaeEngine",
                        Common.GetCaeEngineName(),
                        "CaeInfo", "InfoEngine", 
                        Common.GetCaeInfoName(),
                        Version.GetEngineName(),
                        "VMoveCAEValidate",
                        ]}})

