import wx
import wx.aui
import wx.lib.agw.aui as aui
from gui.etc.constants import Const
from gui.widgets.toolbar import *


class CheckList(wx.CheckListBox):
    def __init__(self, frame):
        super().__init__(frame, id=wx.ID_ANY, pos=wx.DefaultPosition, size=(140, 140),
                         choices=[], style=wx.LB_MULTIPLE)


class AuiManager(wx.aui.AuiManager):
    def __init__(self, frame):
        self.frame = frame
        super().__init__(frame, aui.AUI_MGR_DEFAULT | aui.AUI_MGR_TRANSPARENT_DRAG)
        self.SetManagedWindow(frame)

    def update_manager_for_toolbars(self, tool_bar, toolbar_name, position):
        self.AddPane(tool_bar, wx.aui.AuiPaneInfo().Name(toolbar_name).Caption(toolbar_name).
                     ToolbarPane().Top().Position(position).RightDockable(False))
        self.Update()

    def update_manger_for_tree_panels(self, customctrl, name, caption, layer):
        self.AddPane(customctrl, wx.aui.AuiPaneInfo().
                     Name(name).
                     Caption(caption).
                     Center().Layer(layer).
                     MaximizeButton(True).MinimizeButton(True).
                     CloseButton(False))
        self.Update()

    def add_instance_panel(self):
        self.instance_listbox = CheckList(self.frame)
        self.AddPane(self.instance_listbox, wx.aui.AuiPaneInfo().
                     Name(Const.INSTANCE_LIST).
                     Caption(Const.INSTANCE_LIST).
                     Bottom().Position(0).
                     MaximizeButton(True).MinimizeButton(True))
        self.GetPane(Const.INSTANCE_LIST).Hide()
        self.Update()

    def add_space_to_sizer(self, sizer, nsapces=1):
        for i in range(nsapces):
            sizer.AddStretchSpacer()

    def add_cutsection_panel(self):
        cutsect_panel = wx.Panel(self.frame, wx.ID_ANY,
                                 wx.DefaultPosition, wx.DefaultSize,
                                 wx.TAB_TRAVERSAL)
        static_text = wx.StaticText(cutsect_panel, wx.ID_ANY,
                                    Const.PLANE_EQUATION)
        self.cut_textctrl = wx.TextCtrl(cutsect_panel, wx.ID_ANY, 'X=0')
        self.Id_Cut_Add = wx.NewIdRef()
        self.Id_Cut_Apply = wx.NewIdRef()
        add_button = wx.Button(
            cutsect_panel, self.Id_Cut_Add, Const.ADD, size=(90, 25))
        self.cut_apply_button = wx.Button(
            cutsect_panel, self.Id_Cut_Apply, Const.APPLY, size=(90, 25))
        self.cut_apply_button.Enable(False)
        sizer = wx.GridSizer(4, 4, 10, 5)
        self.add_space_to_sizer(sizer, 5)
        sizer.Add(static_text, 0, wx.ALL, 5)
        sizer.Add(self.cut_textctrl, 0, wx.ALL, 5)
        self.add_space_to_sizer(sizer, 2)
        sizer.Add(add_button, 0, wx.ALL, 5)
        sizer.Add(self.cut_apply_button, 0, wx.ALL, 5)
        self.add_space_to_sizer(sizer, 5)
        cutsect_panel.SetAutoLayout(True)
        cutsect_panel.SetSizer(sizer)
        sizer.Fit(cutsect_panel)
        sizer.SetSizeHints(cutsect_panel)
        self.AddPane(cutsect_panel, wx.aui.AuiPaneInfo().
                     Name(Const.CUT_SECTION).Caption(Const.CUT_SECTION).
                     Bottom().Position(0).
                     MaximizeButton(True).MinimizeButton(True))
        self.GetPane(Const.CUT_SECTION).Hide()
        self.Update()

    def add_isosurface_panel(self):
        isosurf_panel = wx.Panel(
            self.frame, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.iso_static_text = wx.StaticText(isosurf_panel, wx.ID_ANY,
                                             'Displacement - Resultant = ',
                                             size=wx.Size(200, 30))
        self.iso_textctrl = wx.TextCtrl(isosurf_panel, wx.ID_ANY, '0')
        self.Id_Iso_Add = wx.NewIdRef()
        self.Id_Iso_Apply = wx.NewIdRef()
        add_button = wx.Button(isosurf_panel, self.Id_Iso_Add, Const.ADD, size=(90, 25))
        self.iso_apply_button = wx.Button(
            isosurf_panel, self.Id_Iso_Apply, Const.APPLY, size=(90, 25))
        self.iso_apply_button.Enable(False)
        #sizer = wx.FlexGridSizer(4, 4, 10, 5)
        sizer = wx.GridSizer(4, 4, 10, 5)
        self.add_space_to_sizer(sizer, 5)
        sizer.Add(self.iso_static_text, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        sizer.Add(self.iso_textctrl, 0, wx.ALL | wx.ALIGN_LEFT, 5)
        self.add_space_to_sizer(sizer, 2)
        sizer.Add(add_button, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        sizer.Add(self.iso_apply_button, 0, wx.ALL | wx.ALIGN_LEFT, 5)
        self.add_space_to_sizer(sizer, 5)
        isosurf_panel.SetAutoLayout(True)
        isosurf_panel.SetSizer(sizer)
        sizer.Fit(isosurf_panel)
        sizer.SetSizeHints(isosurf_panel)
        self.AddPane(isosurf_panel, wx.aui.AuiPaneInfo().
                     Name(Const.ISO_SURFACE).Caption(Const.ISO_SURFACE).
                     Bottom().Position(0).
                     MaximizeButton(True).MinimizeButton(True))
        self.GetPane(Const.ISO_SURFACE).Hide()
        self.Update()

    def add_flowline_panel(self):
        flowline_panel = wx.Panel(self.frame, wx.ID_ANY,
                                  wx.DefaultPosition, wx.DefaultSize,
                                  wx.TAB_TRAVERSAL)
        self.Id_StreamRadio = wx.NewIdRef()
        self.Id_FlowLineRadio = wx.NewIdRef()
        self.streamline_button = wx.RadioButton(flowline_panel, self.Id_StreamRadio,
                                                'Streamline', style=wx.RB_GROUP)
        self.flowline_button = wx.RadioButton(flowline_panel, self.Id_FlowLineRadio,
                                              'Particle trace')
        starting_static_text = wx.StaticText(flowline_panel, wx.ID_ANY,
                                             'Starting Points')
        self.starting_textctrl = wx.TextCtrl(flowline_panel, wx.ID_ANY,
                                             '(0.0011, 0.1895, 0.1027)')
        starting_numlines_text = wx.StaticText(flowline_panel, wx.ID_ANY,
                                               'Number of Lines')
        self.starting_numlines = wx.TextCtrl(flowline_panel, wx.ID_ANY,
                                             '0')
        self.timestep_static_text = wx.StaticText(flowline_panel, wx.ID_ANY,
                                                  'Time Step')
        self.timestep_textctrl = wx.TextCtrl(flowline_panel, wx.ID_ANY,
                                             '0.001')
        self.steps_static_text = wx.StaticText(flowline_panel, wx.ID_ANY,
                                               'Number of Steps')
        self.steps_textctrl = wx.TextCtrl(flowline_panel, wx.ID_ANY,
                                          '50')
        self.injection_static_text = wx.StaticText(flowline_panel, wx.ID_ANY,
                                                   'Injection Frequency')
        self.injection_textctrl = wx.TextCtrl(flowline_panel, wx.ID_ANY,
                                              '10')
        self.Id_FlowLine_Add = wx.NewIdRef()
        self.Id_FlowLine_Apply = wx.NewIdRef()
        add_button = wx.Button(flowline_panel, self.Id_FlowLine_Add, Const.ADD, size=(90, 25))
        self.flowline_apply_button = wx.Button(
            flowline_panel, self.Id_FlowLine_Apply, Const.APPLY, size=(90, 25))
        self.flowline_apply_button.Enable(False)
        sizer = wx.GridSizer(9, 4, 10, 5)
        self.add_space_to_sizer(sizer, 5)
        sizer.Add(self.streamline_button, 0, wx.ALL, 5)
        sizer.Add(self.flowline_button, 0, wx.ALL, 5)
        self.add_space_to_sizer(sizer, 2)
        sizer.Add(starting_static_text, 0, wx.ALL, 5)
        sizer.Add(self.starting_textctrl, 0, wx.ALL, 5)
        self.add_space_to_sizer(sizer, 2)
        sizer.Add(starting_numlines_text, 0, wx.ALL, 5)
        sizer.Add(self.starting_numlines, 0, wx.ALL, 5)
        self.add_space_to_sizer(sizer, 2)
        sizer.Add(self.timestep_static_text, 0, wx.ALL, 5)
        sizer.Add(self.timestep_textctrl, 0, wx.ALL, 5)
        self.add_space_to_sizer(sizer, 2)
        sizer.Add(self.steps_static_text, 0, wx.ALL, 5)
        sizer.Add(self.steps_textctrl, 0, wx.ALL, 5)
        self.add_space_to_sizer(sizer, 2)
        sizer.Add(self.injection_static_text, 0, wx.ALL, 5)
        sizer.Add(self.injection_textctrl, 0, wx.ALL, 5)
        self.add_space_to_sizer(sizer, 2)
        sizer.Add(add_button, 0, wx.ALL, 5)
        sizer.Add(self.flowline_apply_button, 0, wx.ALL, 5)
        self.add_space_to_sizer(sizer, 5)
        flowline_panel.SetAutoLayout(True)
        flowline_panel.SetSizer(sizer)
        sizer.Fit(flowline_panel)
        sizer.SetSizeHints(flowline_panel)
        self.flowlines_radio(False)
        self.AddPane(flowline_panel, wx.aui.AuiPaneInfo().
                     Name(Const.FLOW_LINES).Caption(Const.FLOW_LINES).
                     Bottom().Position(0).
                     MaximizeButton(True).MinimizeButton(True))
        self.GetPane(Const.FLOW_LINES).Hide()
        self.Update()

    def flowlines_radio(self, state):
        self.timestep_static_text.Enable(state)
        self.timestep_textctrl.Enable(state)
        self.steps_static_text.Enable(state)
        self.steps_textctrl.Enable(state)
        self.injection_static_text.Enable(state)
        self.injection_textctrl.Enable(state)

    def add_attributes_panel(self):
        attributes_panel = wx.Panel(self.frame, wx.ID_ANY,
                                    wx.DefaultPosition, wx.DefaultSize,
                                    wx.TAB_TRAVERSAL)
        self.attributes_dict = {}
        self.attributes_listbox = wx.ListBox(attributes_panel, id=wx.ID_ANY,
                                             style=wx.LB_SINGLE | wx.LB_SORT)
        #self.attributes_listbox.Bind(wx.EVT_LISTBOX, self.select_attribute)
        name_text = wx.StaticText(attributes_panel, wx.ID_ANY, Const.NAME)
        self.attr_name_textctrl = wx.TextCtrl(attributes_panel, wx.ID_ANY,
                                              size=wx.Size(160, -1))
        value_text = wx.StaticText(attributes_panel, wx.ID_ANY, Const.VALUE)
        self.attr_value_textctrl = wx.TextCtrl(attributes_panel, wx.ID_ANY,
                                               size=wx.Size(160, -1))
        self.Id_Attr_Add = wx.NewIdRef()
        attr_add_button = wx.Button(attributes_panel, self.Id_Attr_Add, Const.ADD, size=(90, 25))
        self.Id_Attr_Apply = wx.NewIdRef()
        self.attr_apply_button = wx.Button(attributes_panel,
                                           self.Id_Attr_Apply, Const.APPLY, size=(90, 25))
        self.attr_apply_button.Enable(False)
        self.Id_Attr_Delete = wx.NewIdRef()
        self.attr_delete_button = wx.Button(attributes_panel,
                                            self.Id_Attr_Delete, Const.DELETE, size=(90, 25))
        self.attr_delete_button.Enable(False)
        prop_fields_sizer = wx.FlexGridSizer(2, 2, 10, 5)
        prop_fields_sizer.Add(name_text, 0, wx.ALL, 5)
        prop_fields_sizer.Add(self.attr_name_textctrl,
                              0, wx.EXPAND | wx.ALL, 5)
        prop_fields_sizer.Add(value_text, 0, wx.ALL, 5)
        prop_fields_sizer.Add(self.attr_value_textctrl,
                              0, wx.EXPAND | wx.ALL, 5)
        prop_buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        prop_buttons_sizer.Add(attr_add_button, 0, wx.ALL, 5)
        prop_buttons_sizer.Add(self.attr_delete_button, 0, wx.ALL, 5)
        prop_buttons_sizer.Add(self.attr_apply_button, 0, wx.ALL, 5)
        prop_sizer = wx.BoxSizer(wx.HORIZONTAL)
        prop_sizer.Add(prop_fields_sizer, 0, wx.ALL, 5)
        prop_sizer.Add(prop_buttons_sizer, 0, wx.ALL, 5)
        lbox = wx.StaticBox(attributes_panel, -1, Const.ADDED_ATTRIBUTES, size = (165, 150))
        lbox_sizer = wx.StaticBoxSizer(lbox, wx.VERTICAL)
        lbox_sizer.Add(self.attributes_listbox, 1, wx.EXPAND | wx.ALL, 5)
        pbox = wx.StaticBox(attributes_panel, -1, Const.ATTRIBUTE_PROPERTIES)
        pbox_sizer = wx.StaticBoxSizer(pbox, wx.VERTICAL)
        pbox_sizer.Add(prop_sizer, 1, wx.EXPAND | wx.ALL, 5)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(40)
        sizer.Add(pbox_sizer, 1, wx.EXPAND | wx.ALL, 5)
        sizer.AddSpacer(60)
        sizer.Add(lbox_sizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.AddSpacer(40)
        attributes_panel.SetAutoLayout(True)
        attributes_panel.SetSizer(sizer)
        sizer.Fit(attributes_panel)
        sizer.SetSizeHints(attributes_panel)
        self.AddPane(attributes_panel, wx.aui.AuiPaneInfo().
                     Name(Const.ATTRIBUTES).Caption(Const.ATTRIBUTES).
                     Bottom().Position(0).
                     MaximizeButton(True).MinimizeButton(True))
        self.GetPane(Const.ATTRIBUTES).Hide()
        self.Update()

    def add_layers_panel(self):
        layers_panel = wx.Panel(self.frame, wx.ID_ANY, 
            wx.DefaultPosition, wx.DefaultSize, 
            wx.TAB_TRAVERSAL)
        self.layer_objects = [ 
                        {Const.LABEL:Const.TOP_SEC, Const.VALUE: 1, Const.CB: None },
                        {Const.LABEL:Const.BOTTOM_SEC, Const.VALUE: 2, Const.CB: None },
                        {Const.LABEL:Const.MID_SEC, Const.VALUE: 4, Const.CB: None },
                        {Const.LABEL:Const.MAXIMUM, Const.VALUE: 8, Const.CB: None },
                        {Const.LABEL:Const.AVERAGE, Const.VALUE: 16, Const.CB: None },
                        {Const.LABEL:Const.MINIMUM, Const.VALUE: 32, Const.CB: None } ]
        for item in self.layer_objects:
            item[Const.CB] = wx.CheckBox(layers_panel, -1, item[Const.LABEL])
        self.Id_Layers_Apply = wx.NewIdRef()
        self.layers_apply_button = wx.Button(layers_panel, 
                        self.Id_Layers_Apply, Const.APPLY, size = (90, 150))
        cb_sizer = wx.GridSizer(2, 3, 5, 5)
        for item in self.layer_objects:
            cb_sizer.Add(item[Const.CB], 1, wx.EXPAND|wx.ALL, 5)
        lay_box = wx.StaticBox(layers_panel, -1, Const.SEC_AND_LAYERS)
        lay_sizer = wx.StaticBoxSizer(lay_box, wx.VERTICAL)
        lay_sizer.Add(cb_sizer, 1, wx.EXPAND|wx.ALL, 5);
        type_options = [Const.DEFAULT, Const.NODAL, Const.ELEMENTAL];
        self.type_rb = wx.RadioBox(layers_panel, -1, Const.RESULT_TYPE, 
                wx.DefaultPosition, wx.DefaultSize, type_options, 
                3, wx.RA_SPECIFY_ROWS)
        self.type_rb.SetMinSize(wx.Size(150, 80))
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.type_rb, 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(lay_sizer, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(self.layers_apply_button, 0, wx.EXPAND|wx.ALL, 5)
        layers_panel.SetAutoLayout(True)
        layers_panel.SetSizer(sizer)
        sizer.Fit(layers_panel)
        sizer.SetSizeHints(layers_panel)
        self.AddPane(layers_panel, wx.aui.AuiPaneInfo().
                        Name(Const.LAYERS).Caption(Const.RESULT_PROPERTIES).
                        Bottom().Position(0).
                        MaximizeButton(True).MinimizeButton(True))
        self.GetPane(Const.LAYERS).Hide()
        self.Update()

    def add_additional_panels(self):
        self.add_instance_panel()
        self.add_cutsection_panel()
        self.add_isosurface_panel()
        self.add_flowline_panel()
        self.add_attributes_panel()
        self.add_layers_panel()
