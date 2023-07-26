#!/usr/bin/env python

import os, sys

class InterfaceInfo:

    def __init__(self):
        # interfaces
        self.INTERFACE_ANSYS_CDB    = 'ansys_cdb'
        self.INTERFACE_ANSYS_RST    = 'ansys_rst'
        self.INTERFACE_NASTRAN_BDF  = 'nastran_bdf'
        self.INTERFACE_NASTRAN_OP2  = 'nastran_op2'
        self.INTERFACE_NASTRAN_XDB  = 'nastran_xdb'
        self.INTERFACE_NASTRAN_H5   = 'nastran_h5'
        self.INTERFACE_ABAQUS_INP   = 'abaqus_inp'
        self.INTERFACE_ABAQUS_ODB   = 'abaqus_odb'
        self.INTERFACE_ABAQUS_FIL   = 'abaqus_fil'
        self.INTERFACE_DYNA_KEY     = 'dyna_key'
        self.INTERFACE_DYNA_D3PLOT  = 'dyna_d3plot'
        self.INTERFACE_MARC_POST    = 'marc_post'
        self.INTERFACE_FLUENT_CAS   = 'fluent_cas'
        self.INTERFACE_CFX_RES      = 'cfx_res'

        self.interfaces = [
                self.INTERFACE_ANSYS_CDB,
                self.INTERFACE_ANSYS_RST,
                self.INTERFACE_NASTRAN_BDF,
                self.INTERFACE_NASTRAN_OP2,
                self.INTERFACE_NASTRAN_XDB,
                self.INTERFACE_NASTRAN_H5,
                self.INTERFACE_ABAQUS_INP,
                self.INTERFACE_ABAQUS_ODB,
                self.INTERFACE_ABAQUS_FIL,
                self.INTERFACE_DYNA_KEY,
                self.INTERFACE_DYNA_D3PLOT,
                self.INTERFACE_MARC_POST,
                self.INTERFACE_FLUENT_CAS,
                self.INTERFACE_CFX_RES,
        ]

        self.interface_labels = {}
        self.interface_labels[self.INTERFACE_ANSYS_CDB]    = 'Ansys .cdb files'
        self.interface_labels[self.INTERFACE_ANSYS_RST]    = 'Ansys .rst, .rth and .rfl files'
        self.interface_labels[self.INTERFACE_NASTRAN_BDF]  = 'Nastran .bdf and .dat files'
        self.interface_labels[self.INTERFACE_NASTRAN_OP2]  = 'Nastran .op2 files'
        self.interface_labels[self.INTERFACE_NASTRAN_XDB]  = 'Nastran .xdb files'
        self.interface_labels[self.INTERFACE_NASTRAN_H5]   = 'Nastran .h5 files'
        self.interface_labels[self.INTERFACE_ABAQUS_INP]   = 'Abaqus .inp files'
        self.interface_labels[self.INTERFACE_ABAQUS_ODB]   = 'Abaqus .odb files'
        self.interface_labels[self.INTERFACE_ABAQUS_FIL]   = 'Abaqus .fil files'
        self.interface_labels[self.INTERFACE_DYNA_KEY]     = 'LS-Dyna .k and .key files'
        self.interface_labels[self.INTERFACE_DYNA_D3PLOT]  = 'LS-Dyna d3plot and .plt files'
        self.interface_labels[self.INTERFACE_MARC_POST]    = 'MSC.Marc .t16 and .t19 files'
        self.interface_labels[self.INTERFACE_FLUENT_CAS]   = 'Fluent .msh and .cas files'
        self.interface_labels[self.INTERFACE_CFX_RES]      = 'CFX .res files'

        # grouping types
        self.GROUPING_DEFAULT               = 'default'
        self.GROUPING_PART_ID               = 'part-id'
        self.GROUPING_PROPERTY_ID           = 'property-id'
        self.GROUPING_MATERIAL_ID           = 'material-id'
        self.GROUPING_ELEMENT_SET           = 'element-set' 
        self.GROUPING_FACE_SET              = 'face-set'
        self.GROUPING_ELEMENT_AND_FACE_SETS = 'element-and-face-sets' 
        self.GROUPING_ELEMENT_TYPE_NUMBER   = 'element-type-number'
        self.GROUPING_FEA_TYPE              = 'fea-type'
        self.GROUPING_NO_PARTS              = 'no-parts'
        self.GROUPING_ANSA_PARTS            = 'ansa-part'
        self.GROUPING_HM_COMPONENTS         = 'hypermesh-components'

        self.grouping_types = [
                self.GROUPING_DEFAULT,
                self.GROUPING_PART_ID,
                self.GROUPING_PROPERTY_ID,
                self.GROUPING_MATERIAL_ID,
                self.GROUPING_ELEMENT_SET,
                self.GROUPING_FACE_SET,
                self.GROUPING_ELEMENT_AND_FACE_SETS,
                self.GROUPING_ELEMENT_TYPE_NUMBER,
                self.GROUPING_FEA_TYPE,
                self.GROUPING_NO_PARTS,
                self.GROUPING_ANSA_PARTS,
                self.GROUPING_HM_COMPONENTS,
        ]

        self.grouping_type_labels = {}
        self.grouping_type_labels[self.GROUPING_DEFAULT]              = 'Default'
        self.grouping_type_labels[self.GROUPING_PART_ID]              = 'Part Id'
        self.grouping_type_labels[self.GROUPING_PROPERTY_ID]          = 'Property Id'
        self.grouping_type_labels[self.GROUPING_MATERIAL_ID]          = 'Material Id'
        self.grouping_type_labels[self.GROUPING_ELEMENT_SET]          = 'Element Set' 
        self.grouping_type_labels[self.GROUPING_FACE_SET]             = 'Face Set' 
        self.grouping_type_labels[self.GROUPING_ELEMENT_AND_FACE_SETS]= 'Element and Face Sets' 
        self.grouping_type_labels[self.GROUPING_ELEMENT_TYPE_NUMBER]  = 'Element Type Number'
        self.grouping_type_labels[self.GROUPING_FEA_TYPE]             = 'Fea Type'
        self.grouping_type_labels[self.GROUPING_NO_PARTS]             = 'No Parts'
        self.grouping_type_labels[self.GROUPING_ANSA_PARTS]           = 'ANSA Parts'
        self.grouping_type_labels[self.GROUPING_HM_COMPONENTS]        = 'HyperMesh Components'

        self.enabled_grouping_option_interfaces = [
                self.INTERFACE_ANSYS_CDB,
                self.INTERFACE_ANSYS_RST,
                self.INTERFACE_NASTRAN_BDF,
                self.INTERFACE_NASTRAN_OP2,
                self.INTERFACE_NASTRAN_XDB,
                self.INTERFACE_NASTRAN_H5,
                self.INTERFACE_ABAQUS_INP,
                self.INTERFACE_ABAQUS_ODB,
                self.INTERFACE_ABAQUS_FIL,
                self.INTERFACE_DYNA_KEY,
                self.INTERFACE_DYNA_D3PLOT,
                self.INTERFACE_MARC_POST,
        ]

        self.enabled_grouping_types = [
                self.GROUPING_DEFAULT,
                #self.GROUPING_PART_ID,
                self.GROUPING_PROPERTY_ID,
                self.GROUPING_MATERIAL_ID,
                self.GROUPING_ELEMENT_SET,
                self.GROUPING_FACE_SET,
                self.GROUPING_ELEMENT_AND_FACE_SETS,
                self.GROUPING_ELEMENT_TYPE_NUMBER,
                self.GROUPING_NO_PARTS,
                self.GROUPING_ANSA_PARTS,
                self.GROUPING_HM_COMPONENTS,
        ]

    def GetGroupingDefault(self):
        return self.GROUPING_DEFAULT

