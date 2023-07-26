#!/usr/bin/env python
#----------------------------------------------------------------------------
# Name:         vcapp.py
# Purpose:      Simple framework for running individual VCollab applications
#
# Author:       Mohan Varma
#
# Created:      25-July-2008
# Copyright:    (c) 2008 by Visual Collaboration Technologies Inc.
# Licence:      VCollab license
#----------------------------------------------------------------------------

"""
Error Codes from VMoveCAE
"""

import sys,os
import errno

NO_ERROR=0
UNKNOWN_ERROR=1
FILE_ACCESS_ERROR=2
FORMAT_ERROR=3
VERSION_ERROR=4
LICENSE_ERROR=5
MEMORY_ALLOCATION_ERROR=6
ZERO_ELEMENT_MODEL=7
NOT_IMPLEMENTED=8
INVALID_ARGUMENTS=9
