#!/usr/bin/python

import sys
import os
import wx
# import CustomListCtrlMixins as listmix
from wx.lib.mixins.listctrl import  ListCtrlAutoWidthMixin,TextEditMixin
from wx.lib.embeddedimage import PyEmbeddedImage
from bisect import bisect

"""
Description
===========

Events
======

TriCheckListCtrl supports the events related to the checkbutton-type items:

  - EVT_LIST_ITEM_CHECKING: an item is being checked;
  - EVT_LIST_ITEM_CHECKED: an item has been checked.
"""

#----------------------------------------------------------------------------

# wxEVT_LIST_ITEM_CHECKING = wx.NewEventType()
wxEVT_LIST_ITEM_CHECKED = wx.NewEventType()

# EVT_LIST_ITEM_CHECKING = wx.PyEventBinder(wxEVT_LIST_ITEM_CHECKING, 1)
EVT_LIST_ITEM_CHECKED = wx.PyEventBinder(wxEVT_LIST_ITEM_CHECKED, 1)

#----------------------------------------------------------------------------

Checked = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAABHNCSVQICAgIfAhkiAAAAKlJ"
    "REFUKJFjlAls+M9AImBhYGBgODYxFi7AyMjEwMQEwczMzAxMTMxwmomJiUEzrp+BCdkEQhqY"
    "mCDKmYjRYLDBCCrHjNBESAMDAwPcNrgmmAarXXZYNcDUMDIyompiZoZYbbrVAkPDjYjrDIyM"
    "jKg2wUyGAVwaGBlRnAdx0oWAcyjxga4BxXnIwXol5BJODWh+QsQDExMzXg0YoQfTjE8DAwMD"
    "AyM5aQ8AoE8ebApv5jgAAAAASUVORK5CYII=")

NotChecked = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAYAAABy6+R8AAAABHNCSVQICAgIfAhkiAAAAG1J"
    "REFUKJGd0sENgDAIBdDPhzHcwGk8eXUU757cyM30UKOlF38lIU0ID5IGG6b1RGcEABzb/BRI"
    "3ulwD7g7IspLOsZlB+sJX4As7ewBpL9IBWmTChqkgYRU0CANmFVIBWaWN6kgfYQKAMD+3N4F"
    "sAcJ4jYyX4sAAAAASUVORK5CYII=")

PartChecked = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAAA0AAAANCAIAAAD9iXMrAAAAA3NCSVQICAjb4U/gAAABL0lE"
    "QVQokVWRsYoUURBF77lVr2e2V+ioQwMD/RoD0dVfMTAR/BPBDxD8I0PFQWV0Zqf7lcE47lpQ"
    "UMGhuJfDw+dvr7cD6P4g/l1VOtwueb0d3r9+Oo2bXgIb20SEHRERGT/2x2dvPiRoGjfTg2G/"
    "HEo9IsK2scmMaTtmpq2U1Ev75fDx86fdaZfRwIiuPo/zi8c31FBSSgJL/dtp9/X2S/MgAVrU"
    "HdHVE3PmjB3R3JqHFoMkENWbE7AtKaVLeCwZpL/bz6UBSYkUEWEw9yAE4DtOkh02XeuihW4k"
    "wVLrWuv54YWLiPS8ne1MJwi81jpfzemkJCmFWsa0HW+evFq1cjFTquY2DdPhuAqySt/3R0dW"
    "tfTGNgAIKO1/n37+OlYvHr18d7VpSCX9L/nO77L2Pz0qYJIOsf9MAAAAAElFTkSuQmCC")

#----------------------------------------------------------------------------

TriState_NotChecked = 0          # check button, not checked
TriState_PartChecked = 1         # tri-state check button, defined for 
TriState_Checked = 2             # check button,     checked

#----------------------------------------------------------------------------
class TriCheckListBox(wx.ListCtrl, ListCtrlAutoWidthMixin,TextEditMixin):

    def __init__(self, parent, id = wx.ID_ANY, 
                    pos=wx.DefaultPosition, size=wx.DefaultSize, 
                    style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_EDIT_LABELS):
        wx.ListCtrl.__init__(self,parent=parent, id=id, pos=pos, size=size, style=style)

        self.Populate()


    def Populate(self):
        il = wx.ImageList(13, 13)
        il.Add(NotChecked.GetBitmap())
        il.Add(PartChecked.GetBitmap())
        il.Add(Checked.GetBitmap())
        self.AssignImageList(il, wx.IMAGE_LIST_SMALL)

        info = wx.ListItem()
        info.m_mask = wx.LIST_MASK_IMAGE|wx.LIST_MASK_DATA;

        info.m_image = -1
        info.m_format = 0
        info.m_text = 'Check Status'
        self.InsertColumn(0, info)

        info.m_mask = wx.LIST_MASK_TEXT|wx.LIST_MASK_FORMAT;
        info.m_text = 'Label'
        self.InsertColumn(1, info)

        self.SetColumnWidth(0,20)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)

    



