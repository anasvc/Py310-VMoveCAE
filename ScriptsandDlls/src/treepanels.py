import wx
# import wx.lib.agw.customtreectrl as ct
import numpy as np
import CustomTreeCtrl as ct

class CustomTreeCtrl:
    # def __init__(self):
    #     # super().__init__(frame, -1, wx.DefaultPosition, wx.DefaultSize, style=0,
    #     #                  agwStyle=wx.TR_DEFAULT_STYLE |
    #     #                  wx.TR_HAS_BUTTONS |
    #     #                  ct.TR_MULTIPLE)
        

    def check_for_other_children_check(self, tree_item):
        parent = tree_item.GetParent()
        if parent:
            child, cookie = self.GetFirstChild(parent)
            if(child):
                if not self.IsItemChecked(child):
                    self.SetItem3StateValue(
                        parent, wx.CHK_UNDETERMINED)
                    self.Refresh()
                    self.set_parent_undetermined(parent)
                    return
            while(child):
                child, cookie = self.GetNextChild(parent, cookie)
                if(child):
                    if not self.IsItemChecked(child):
                        self.SetItem3StateValue(
                            parent, wx.CHK_UNDETERMINED)
                        self.Refresh()
                        self.set_parent_undetermined(parent)
                        return
            self.SetItem3StateValue(parent, wx.CHK_CHECKED)
            self.Refresh()
            self.check_for_other_children_check(parent)

    def check_for_other_children_uncheck(self, tree_item):
        parent = tree_item.GetParent()
        if parent:
            child, cookie = self.GetFirstChild(parent)
            if(child):
                if self.IsItemChecked(child):
                    self.SetItem3StateValue(
                        parent, wx.CHK_UNDETERMINED)
                    self.Refresh()
                    self.set_parent_undetermined(parent)
                    return
            while(child):
                child, cookie = self.GetNextChild(parent, cookie)
                if(child):
                    if self.IsItemChecked(child):
                        self.SetItem3StateValue(
                            parent, wx.CHK_UNDETERMINED)
                        self.Refresh()
                        self.set_parent_undetermined(parent)
                        return
            self.SetItem3StateValue(parent, wx.CHK_UNCHECKED)
            self.Refresh()
            self.check_for_other_children_uncheck(parent)

    def set_parent_undetermined(self, tree_item):
        parent = tree_item.GetParent()
        if parent:
            self.SetItem3StateValue(
                parent, wx.CHK_UNDETERMINED)
            self.Refresh()
            self.set_parent_undetermined(parent)

    def all_check_in_tree(self, status):
        self.CheckItem(self.root, status)


class PartTree:
    def __init__(self,vmovecae):
        self.vmovecae = vmovecae
        self.part_tree = ct.CustomTreeCtrl(self.vmovecae, -1, wx.DefaultPosition, wx.DefaultSize, style=0,
                         agwStyle=wx.TR_DEFAULT_STYLE |
                         wx.TR_HAS_BUTTONS |
                         ct.TR_MULTIPLE)
        # self.frame = self.vmovecae.frame
        # self.grping_tree = None
        # self.name = 'Part Selection Pane'
        # self.label = 'Geometry and Features'
        # self.position = 0
        # self.manager = self.vmovecae.manager

    def update(self, part_tree):
        self.DeleteAllItems()
        self.branches = []
        self.grping_tree = part_tree
        if self.grping_tree is None:
            return 
        root_row = self.grping_tree[self.grping_tree['parent_id'] == 0]
        self.root = self.AddRoot(
            root_row['name'][0].decode("utf-8"), ct_type=1)
        self.SetItem3State(self.root, True)
        self.SetItem3StateValue(self.root, wx.CHK_CHECKED)
        branches_rows = self.grping_tree[self.grping_tree['parent_id']
                                         == root_row['id']]
        for i, branch in enumerate(branches_rows):
            leaves_rows = self.grping_tree[self.grping_tree['parent_id']
                                           == branch['id']]
            self.branches.append(self.AppendItem(
                self.root, branch['name'].decode("utf-8"), ct_type=1))
            self.SetItem3State(self.branches[i], True)
            self.SetItem3StateValue(self.branches[i], wx.CHK_CHECKED)
            for leaf_row in leaves_rows:
                leaf = self.AppendItem(
                    self.branches[i], leaf_row['name'].decode("utf-8"), ct_type=1)
                self.SetItem3State(leaf, True)
                self.SetItem3StateValue(leaf, wx.CHK_CHECKED)
        self.ExpandAll()
        self.Bind(ct.EVT_TREE_ITEM_CHECKED, self.on_treeitem_check)

    def on_treeitem_check(self, event):
        print("Somebody checked something")
        tree_item = event.GetItem()
        if tree_item.IsChecked() == wx.CHK_CHECKED:
            self.CheckChilds(tree_item, True)
            self.check_for_other_children_check(tree_item)
        elif tree_item.IsChecked() == wx.CHK_UNDETERMINED:
            self.SetItem3StateValue(
                tree_item, wx.CHK_UNCHECKED)
            self.CheckChilds(tree_item, False)
            self.check_for_other_children_uncheck(tree_item)
        elif tree_item.IsChecked() == wx.CHK_UNCHECKED:
            self.CheckChilds(tree_item, False)
        self.Refresh()

    def all_selection_in_tree(self, status):
        for branch in self.branches:
            child, cookie = self.GetFirstChild(branch)
            if(child):
                self.SelectItem(child, status)
            while(child):
                child, cookie = self.GetNextChild(branch, cookie)
                if(child):
                    self.SelectItem(child, status)

    def invert_selection_in_tree(self):
        for branch in self.branches:
            child, cookie = self.GetFirstChild(branch)
            if(child):
                self.ToggleItemSelection(child)
            while(child):
                child, cookie = self.GetNextChild(branch, cookie)
                if(child):
                    self.ToggleItemSelection(child)

    def checked_selection_in_tree(self, status):
        for branch in self.branches:
            child, cookie = self.GetFirstChild(branch)
            if(child):
                if(self.IsItemChecked(child)):
                    self.SelectItem(child, status)
            while(child):
                child, cookie = self.GetNextChild(branch, cookie)
                if(child):
                    if(self.IsItemChecked(child)):
                        self.SelectItem(child, status)

    def unchecked_selection_in_tree(self, status):
        for branch in self.branches:
            child, cookie = self.GetFirstChild(branch)
            if(child):
                if not self.IsItemChecked(child):
                    self.SelectItem(child, status)
            while(child):
                child, cookie = self.GetNextChild(branch, cookie)
                if(child):
                    if not self.IsItemChecked(child):
                        self.SelectItem(child, status)

    def selected_selection_in_tree(self, status):
        if not status:
            for branch in self.branches:
                child, cookie = self.GetFirstChild(branch)
                if(child):
                    if self.IsSelected(child):
                        self.SelectItem(child)
                while(child):
                    child, cookie = self.GetNextChild(branch, cookie)
                    if(child):
                        if self.IsSelected(child):
                            self.SelectItem(child)
        self.manager.Update()

    def deselected_selection_in_tree(self):
        for branch in self.branches:
            child, cookie = self.GetFirstChild(branch)
            if(child):
                if not self.IsSelected(child):
                    self.SelectItem(child, select=True)
            while(child):
                child, cookie = self.GetNextChild(branch, cookie)
                if(child):
                    if not self.IsSelected(child):
                        self.SelectItem(child, select=True)

    def invert_check_in_tree(self):
        for branch in self.branches:
            child, cookie = self.GetFirstChild(branch)
            if(child):
                if self.IsItemChecked(child):
                    self.CheckItem(child, checked=False)
                else:
                    self.CheckItem(child, checked=True)
            while(child):
                child, cookie = self.GetNextChild(branch, cookie)
                if(child):
                    if self.IsItemChecked(child):
                        self.CheckItem(child, checked=False)
                    else:
                        self.CheckItem(child, checked=True)

    def checked_check_in_tree(self, status):
        for branch in self.branches:
            child, cookie = self.GetFirstChild(branch)
            if(child):
                if self.IsItemChecked(child):
                    self.CheckItem(child, status)
            while(child):
                child, cookie = self.GetNextChild(branch, cookie)
                if(child):
                    if self.IsItemChecked(child):
                        self.CheckItem(child, status)

    def unchecked_check_in_tree(self, status):
        for branch in self.branches:
            child, cookie = self.GetFirstChild(branch)
            if(child):
                if not self.IsItemChecked(child):
                    self.CheckItem(child, status)
            while(child):
                child, cookie = self.GetNextChild(branch, cookie)
                if(child):
                    if not self.IsItemChecked(child):
                        self.CheckItem(child, status)

    def selected_ckeck_in_tree(self, status):
        for branch in self.branches:
            child, cookie = self.GetFirstChild(branch)
            if(child):
                if child.IsSelected():
                    self.CheckItem(child, status)
            while(child):
                child, cookie = self.GetNextChild(branch, cookie)
                if(child):
                    if child.IsSelected():
                        self.CheckItem(child, status)

    def deselected_check_in_tree(self, status):
        for branch in self.branches:
            child, cookie = self.GetFirstChild(branch)
            if(child):
                if not child.IsSelected():
                    self.CheckItem(child, status)
            while(child):
                child, cookie = self.GetNextChild(branch, cookie)
                if(child):
                    if not child.IsSelected():
                        self.CheckItem(child, status)

    def get_updated_table(self):
        if self.grping_tree is None:
                return None
        if not self.root.IsChecked():
            self.grping_tree['check_box'] = False
            return self.grping_tree
        for i, branch in enumerate(self.branches):
            if not branch.IsChecked():
                self.grping_tree['check_box'][self.grping_tree['name']
                                              == branch.GetText().encode("utf-8")] = False
                self.grping_tree['check_box'][self.grping_tree['parent_id']
                                              == i+2] = False
                continue
            leaves = branch.GetChildren()
            for leaf in leaves:
                if not leaf.IsChecked():
                    self.grping_tree['check_box'][self.grping_tree['name']
                                                  == leaf.GetText().encode("utf-8")] = False
        return self.grping_tree


class ResultTree(CustomTreeCtrl):
    def __init__(self, frame):
        super().__init__(frame)
        self.frame = frame
        self.result_tree = None
        self.name = 'Result Selection Pane'
        self.label = 'Results and Properties'
        self.position = 1
        self.instance_listbox = self.frame.aui_manager.instance_listbox
        self.manager = self.frame.aui_manager

    def update(self, result_tree):
        self.instance_listbox.Bind(
            wx.EVT_CHECKLISTBOX, self.on_instances_check)
        self.DeleteAllItems()
        self.branches = []
        self.result_tree = result_tree
        if self.result_tree is None:
            return 
        root_row = self.result_tree[self.result_tree['parent_id'] == 0]
        self.root = self.AddRoot(
            root_row['result_name'][0].decode("utf-8"), ct_type=1)
        self.SetItem3State(self.root, True)
        self.SetItem3StateValue(self.root, wx.CHK_CHECKED)
        branches_rows = self.result_tree[self.result_tree['parent_id']
                                         == root_row['id']]
        for i, branch in enumerate(branches_rows):
            leaves_rows = self.result_tree[self.result_tree['parent_id']
                                           == branch['id']]
            self.branches.append(self.AppendItem(
                self.root, branch['result_name'].decode("utf-8"), ct_type=1))
            self.SetItem3State(self.branches[i], True)
            self.SetItem3StateValue(self.branches[i], wx.CHK_CHECKED)
            for leaf_row in leaves_rows:
                leaf = self.AppendItem(
                    self.branches[i], leaf_row['result_name'].decode("utf-8"), ct_type=1)
                self.SetItem3State(leaf, True)
                self.SetItem3StateValue(leaf, wx.CHK_CHECKED)
        self.Expand(self.root)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_treeitem_selection)
        self.Bind(ct.EVT_TREE_ITEM_CHECKED, self.on_treeitem_check)

    def on_treeitem_check(self, event):
        tree_item = event.GetItem()
        parent = tree_item.GetParent()
        if parent != None:
            if parent.GetText() != 'Results':
                if parent.IsChecked():
                    self.CheckChilds(parent, checked=True)
                    return
                else:
                    self.CheckChilds(parent, checked=False)
                    return
        if tree_item.IsChecked() == wx.CHK_CHECKED:
            self.CheckChilds(tree_item, True)
            self.check_for_other_children_check(tree_item)
        elif tree_item.IsChecked() == wx.CHK_UNDETERMINED:
            self.SetItem3StateValue(
                tree_item, wx.CHK_UNCHECKED)
            self.CheckChilds(tree_item, False)
            self.CheckChilds(tree_item, False)
            self.check_for_other_children_uncheck(tree_item)
        elif tree_item.IsChecked() == wx.CHK_UNCHECKED:
            self.CheckChilds(tree_item, False)
        self.Refresh()

    def on_treeitem_selection(self, event):
        cb = event.GetItem()
        pane = self.manager.GetPane('Instance List')
        name = self.GetItemText(cb)
        pos = np.where(
            self.result_tree['result_name'] == name.encode("utf-8"))[0]
        self.data = self.result_tree[pos]['data'][0]
        if self.data is None:
            pane.Hide()
            self.manager.Update()
            return
        substep = self.data["frame"]
        instances_list = [f'L{l}M{substep[i]}' for i,
                          l in enumerate(self.data['step']) if l != 0]
        check_these = np.where(self.data['check_box'])[0]
        if instances_list:
            self.instance_listbox.Clear()
            self.instance_listbox.Set(instances_list)
            if len(check_these) != 0:
                self.instance_listbox.SetCheckedItems(
                    check_these)
            pane.Show()
        else:
            pane.Hide()
        self.manager.Update()

    def on_instances_check(self, event):
        cb = event.GetSelection()
        self.data['check_box'][cb] = self.instance_listbox.IsChecked(
            cb)

    def all_selection_in_tree(self, status):
        for branch in self.branches:
            self.SelectItem(branch, status)

    def invert_selection_in_tree(self):
        for branch in self.branches:
            self.ToggleItemSelection(branch)

    def checked_selection_in_tree(self, status):
        for branch in self.branches:
            if self.IsItemChecked(branch):
                self.SelectItem(branch, status)

    def unchecked_selection_in_tree(self, status):
        for branch in self.branches:
            if not self.IsItemChecked(branch):
                self.SelectItem(branch, status)

    def selected_selection_in_tree(self, status):
        if not status:
            for branch in self.branches:
                if self.IsSelected(branch):
                    self.SelectItem(branch)

    def deselected_selection_in_tree(self, status):
        for branch in self.branches:
            if not self.IsSelected(branch):
                self.SelectItem(branch, status)

    def all_selection_in_instances(self, status):
        if not status:
            for i in range(len(self.data)):
                self.instance_listbox.Deselect(i)
        else:
            for i in range(len(self.data)):
                self.instance_listbox.SetSelection(i)

    def invert_selection_in_instances(self):
        selected_list = self.instance_listbox.GetSelections()
        for i in range(len(self.data)):
            if i in selected_list:
                self.instance_listbox.Deselect(i)
            else:
                self.instance_listbox.SetSelection(i)

    def checked_selection_in_instances(self, status):
        checked_items = self.instance_listbox.GetCheckedItems()
        if status:
            for item in checked_items:
                self.instance_listbox.SetSelection(item)
        else:
            for item in checked_items:
                self.instance_listbox.Deselect(item)

    def unchecked_selection_in_instances(self, status):
        if status:
            for i in range(len(self.data)):
                if not self.instance_listbox.IsChecked(i):
                    self.instance_listbox.SetSelection(i)
        else:
            for i in range(len(self.data)):
                if not self.instance_listbox.IsChecked(i):
                    self.instance_listbox.Deselect(i)

    def deselected_selection_in_instances(self):
        for i in range(len(self.data)):
            if not self.instance_listbox.IsSelected(i):
                self.instance_listbox.SetSelection(i)

    def selected_selection_in_instances(self, status):
        if not status:
            for i in range(len(self.data)):
                if self.instance_listbox.IsSelected(i):
                    self.instance_listbox.Deselect(i)

    def invert_check_in_tree(self):
        for branch in self.branches:
            if self.IsItemChecked(branch):
                self.CheckItem(branch, checked=False)
            else:
                self.CheckItem(branch, checked=True)

    def checked_check_in_tree(self, status):
        for branch in self.branches:
            if self.IsItemChecked(branch):
                self.CheckItem(branch, status)

    def unchecked_check_in_tree(self, status):
        for branch in self.branches:
            if not self.IsItemChecked(branch):
                self.CheckItem(branch, status)

    def selected_ckeck_in_tree(self, status):
        for branch in self.branches:
            if branch.IsSelected():
                self.CheckItem(branch, status)

    def deselected_check_in_tree(self, status):
        for branch in self.branches:
            if not branch.IsSelected():
                self.CheckItem(branch, status)

    def all_check_in_instances(self, status):
        for i in range(len(self.data)):
            self.instance_listbox.Check(i, status)
        self.data['check_box'] = status

    def invert_check_in_instances(self):
        for i in range(len(self.data)):
            if self.instance_listbox.IsChecked(i):
                self.instance_listbox.Check(i, False)
                self.data['check_box'][i] = False
            else:
                self.instance_listbox.Check(i, True)
                self.data['check_box'][i] = True

    def checked_check_in_instances(self, status):
        for i in range(len(self.data)):
            if self.instance_listbox.IsChecked(i):
                self.instance_listbox.Check(i, status)
                self.data['check_box'][i] = status

    def unchecked_check_in_instances(self, status):
        for i in range(len(self.data)):
            if not self.instance_listbox.IsChecked(i):
                self.instance_listbox.Check(i, status)
                self.data['check_box'][i] = status

    def selected_check_in_instances(self, status):
        for i in range(len(self.data)):
            if self.instance_listbox.IsSelected(i):
                self.instance_listbox.Check(i, status)
                self.data['check_box'][i] = status

    def deselected_check_in_instances(self, status):
        for i in range(len(self.data)):
            if not self.instance_listbox.IsSelected(i):
                self.instance_listbox.Check(i, status)
                self.data['check_box'][i] = status

    def checkall_and_expand(self):
        self.part_tree.ExpandAll()
        self.part_tree.CheckItem(self.root, checked=True)

    def get_updated_table(self):
        if self.result_tree is None:
            return None
        if not self.root.IsChecked():
            self.result_tree['check_box'] = False
            return self.result_tree
        for i, branch in enumerate(self.branches):
            if not branch.IsChecked():
                self.result_tree['check_box'][self.result_tree['result_name']
                                              == branch.GetText().encode("utf-8")] = False
        return self.result_tree
