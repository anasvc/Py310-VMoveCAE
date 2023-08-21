#!/usr/bin/env python

"""
ZetCode wxPython tutorial

In this example, we create a simple
wx.ListCtrl widget.

author: Jan Bodnar
website: www.zetcode.com
last modified: July 2020
"""

import wx

data = [('Jessica Alba', 'Pomona', '1981'), ('Sigourney Weaver', 'New York', '1949'),
  ('Angelina Jolie', 'los angeles', '1975'), ('Natalie Portman', 'Jerusalem', '1981'),
  ('Rachel Weiss', 'London', '1971'), ('Scarlett Johansson', 'New York', '1984' )]


class Example(wx.Frame):

    def __init__(self, *args, **kw):
        super(Example, self).__init__(*args, **kw)

        self.InitUI()

    def InitUI(self):

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        panel = wx.Panel(self)

        self.list = wx.ListCtrl(panel, wx.ID_ANY, style=wx.LC_REPORT)
        self.list.EnableCheckBoxes()
        # self.list.CheckItem(self.list)
        # self.list.EnableCheckBoxes()
        self.list.InsertColumn(0, 'name', width=140)
        self.list.InsertColumn(1, 'place', width=130)
        self.list.InsertColumn(2, 'year', wx.LIST_FORMAT_RIGHT, 90)

        idx = 0

        for i in data:

            index = self.list.InsertItem(idx, i[0])
            check = self.list.SetItem(index, 1, i[1])
            item = self.list.SetItem(index, 2, i[2])
            self.list.CheckItem(index)
            self.list.Bind(wx.EVT_LIST_ITEM_CHECKED, self.on_instances_check)
            self.list.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self.on_instances_uncheck)
            idx += 1

        hbox.Add(self.list, 1, wx.EXPAND)
        panel.SetSizer(hbox)

        self.SetTitle('Actresses')
        self.Centre()
        
    def on_instances_check(self, event):
        print('check')
        # event.Skip()
    def on_instances_uncheck(self, event):
        print('uncheck')
        # event.Skip()

def main():

    app = wx.App()
    ex = Example(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()