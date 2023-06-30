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
This program will load and run one of the individual VCollab applications in 
this directory within its own frame window.  Just specify the application name
on the command line.
"""

import sys, os, platform, time
import glob
#import xml.etree.ElementTree as et  # python 2.5
#import elementtree.ElementTree as et
if platform.python_version() < '2.7':
    import xml.parsers.expat
import platform, locale
if platform.python_version() > '2.5':
    import xml.etree.ElementTree as et
else:
    import elementtree.ElementTree as et
import Extractor
import Common
import InterfaceInfo

#----------------------------------------------------------------------------

exptime = time.strptime('31-Dec-2009 23:59:59 GMT', '%d-%b-%Y %H:%M:%S GMT')

#----------------------------------------------------------------------------

def GetArchitecture():
        osname = platform.system()
        ostype = platform.architecture()[0]
        uname = platform.uname()

        arch = None
        if 'Windows' == osname:
            arch = 'win'
        elif 'Linux' == osname:
            arch = 'linux'
        else:
            raise Exception('\nUnknown Operating System.')
        if '32bit' == ostype:
            arch += '32'
        elif '64bit' == ostype:
            arch += '64'
        else:
            raise Exception('\nUnknown Operating System.')

        return arch

#----------------------------------------------------------------------------

def GetLibraryName():
    cpplibs = { 'win32' : '_CaeEngineWrap_Win32_Release',
                'win64' : '_CaeEngineWrap_x64_Release' };
    return cpplibs.get(GetArchitecture(), '_CaeEngineWrap')

#----------------------------------------------------------------------------

def TempDir():
    dir = os.environ.get('VCOLLAB_TEMP_PATH')
    if not dir:
        arch = GetArchitecture()
        if arch in ['win32', 'win64']:
            dir = os.environ.get('TEMP')
            #dir = os.path.expanduser('~')
        else:
            dir = os.path.expanduser('/tmp')
    if dir:
        dir = dir + os.sep + 'VMoveCAE-run-' + \
                            time.strftime("%Y-%m-%d-%H-%M-%S") + "-" + \
                            repr(os.getpid())
        if not os.path.exists(dir):
            os.makedirs(dir)

    return dir

#----------------------------------------------------------------------------
def ExtractedFile(in_path, out_folder, wildcard):
    extractor = Extractor.get_extractor(in_path)
    pchecker = Extractor.PatternChecker(wildcard.split('|')[1].split(';'))
    if extractor:
        res = Extractor.extract(extractor, in_path, out_folder, pchecker.check)
        if len(res[1]):
            return res[1][0] 

    return in_path

#----------------------------------------------------------------------------

def PyStrToCharPtr(str):
    cptr = str

    try:
        cptr = str.encode('ascii')
    except Exception as ex:
        cptr = str.encode('utf-8')
    except Exception as ex:
        cptr = str.encode(locale.getpreferredencoding())
    except Exception as ex:
        cptr = str.encode(os.environ.get('VCOLLAB_LOCALE'))
    except Exception as ex:
        cptr = str

    return cptr

#----------------------------------------------------------------------------

class CaeEngine:

    def __init__(self):
        self.MODEL_FILE   = 0
        self.RESULTS_FILE = 1
        self.OUTPUT_FILE  = 2

        self.datamgr = 0
        self.transseq = 0
        self.exclude_geometry = False
        self.indep_mesh_sets = False
        self.odb_fast_load = False
        self.odb_load_zero_frames = False
        self.odb_ignore_contact_results = False
        self.odb_load_internal_sets = False
        self.odb_load_instance_parts = False
        self.marc_experimental_features = False
        self.bdf_use_sets = False
        self.disable_parts = False
        self.use_sets_or_full_mesh = False
        self.disable_skinning = False
        self.cpp_lib = __import__(Common.GetCaeEngineName())
        self.tmp_folder = ''
        self.pi_file = ''
        self.part_grouping_type = ''
        self.nodal_averaged_loads = False
        self.results_instance_title = ''
        self.extract_mode_properties = False

    def SetTempFileFolder(self, folderName):
        self.tmp_folder = folderName

    def SetLogFile(self, fileName):
        self.cpp_lib.SetLogFile(fileName)

    def SetPIFile(self, fileName):
        self.pi_file = fileName

    def GetPIFile(self):
        return self.pi_file

    def SetPartGroupingType(self, part_grouping_type):
        if part_grouping_type in self.GetInterfaceInfo().enabled_grouping_types:
            self.part_grouping_type = part_grouping_type
        else:
            print ("Invalid part grouping type \"" + part_grouping_type + "\".")
            print ("Using default grouping ...")
            self.part_grouping_type = ''

    def ResetPartGroupingType(self):
        self.part_grouping_type = ''

    def DefaultResultsInstanceTitle(self):
        return 'L'

    def SetResultsInstanceTitle(self, results_instance_title):
        self.results_instance_title = results_instance_title

    def ResetResultsInstanceTitle(self):
        self.results_instance_title = ''

    def EnableResultsInstanceTitle(self):
        if not self.results_instance_title:
            print ('Setting default instance title for additional results files')
            self.SetResultsInstanceTitle(self.DefaultResultsInstanceTitle())
        print ('Using instance title -', self.results_instance_title)

        self.cpp_lib.setAdditionalResultsInstanceTitle(
                                    self.results_instance_title.decode())

    def AcquireLicense(self):
        arch=GetArchitecture()
        cpplibs = { 'win32' : '_CaeEngineWrap_Win32_Release',
                    'win64' : '_CaeEngineWrap_x64_Release' };
        self.cpp_lib = __import__(cpplibs.get(arch, '_CaeEngineWrap'));

        if arch in ['win32', 'win64', 'linux64']:
            return self.cpp_lib.acquireLicense();
        else:
            if time.gmtime() < exptime:
                return 'True'
            else:
                return 'False'

    def ReleaseLicense(self):
        return self.cpp_lib.releaseLicense();

    def LicenseHeartbeatsIdle(self, onoff):
        return self.cpp_lib.licenseHeartbeatsIdle(onoff);

    def CurrentLicenseStatus(self):
        return self.cpp_lib.currentLicenseStatus();

    def GetCeid(self):
        return self.cpp_lib.getCeid()

    def GetRootName(self):
        return "VMoveCAE"

    def GetWildCards(self, filetype):
        return self.cpp_lib.getWildCards(filetype)

    def Do(self, command):
        if "Create new data engine" == command:
            return "Bracket2"
        if "Get part list from data engine Bracket2" == command:
            return "Object 1\nObject 2\nObject 3"
        if "Get result list from data engine Bracket2" == command:
            return "Reaction Force\nDisplacement\nStress\nPressure"

    def GetAbaqusOdbVersion(self):
        return self.cpp_lib.getAbaqusOdbVersion()

    def GetGroupingType(self, model_file, interface_grouping):
        grouping_type = self.part_grouping_type
        if grouping_type:
            return grouping_type

        if interface_grouping:
            
            model_file_type = self.cpp_lib.modelFileType(model_file.decode())
            
            if model_file_type and model_file_type in interface_grouping:
                return interface_grouping[model_file_type]

        return self.GetInterfaceInfo().GetGroupingDefault()

    def GetFormatModelMetadata(self, model_file, file_format, interface_grouping):
        grouping_type = self.GetGroupingType(model_file, interface_grouping)
        self.cpp_lib.clearSettings()
        self.cpp_lib.odbFastLoad(self.odb_fast_load)
        self.cpp_lib.odbZerothFrame(self.odb_load_zero_frames)
        #self.cpp_lib.dontHandleOdbContactResults(self.odb_ignore_contact_results)
        self.cpp_lib.odbLoadInternalSets(self.odb_load_internal_sets)
        self.cpp_lib.odbLoadInstanceParts(self.odb_load_instance_parts)
        self.cpp_lib.enableMarcExperimentalFeatures(self.marc_experimental_features)
        self.cpp_lib.nodalAveragePressureLoads(self.nodal_averaged_loads)
        self.cpp_lib.useBdfSets(self.bdf_use_sets)
        self.cpp_lib.dontDivideIntoParts(self.disable_parts)
        self.cpp_lib.useSetsOrFullMesh(self.use_sets_or_full_mesh)
        #self.cpp_lib.extractModeProperties(self.extract_mode_properties)
        return self.cpp_lib.getFormatModelMetadataPartType(model_file, file_format,
                grouping_type)

    def GetModelMetadata(self, model_file, interface_grouping):
        grouping_type = self.GetGroupingType(model_file, interface_grouping)
        self.cpp_lib.clearSettings()
        self.cpp_lib.odbFastLoad(self.odb_fast_load)
        self.cpp_lib.odbZerothFrame(self.odb_load_zero_frames)
        #self.cpp_lib.dontHandleOdbContactResults(self.odb_ignore_contact_results)
        self.cpp_lib.odbLoadInternalSets(self.odb_load_internal_sets)
        self.cpp_lib.odbLoadInstanceParts(self.odb_load_instance_parts)
        self.cpp_lib.enableMarcExperimentalFeatures(self.marc_experimental_features)
        self.cpp_lib.nodalAveragePressureLoads(self.nodal_averaged_loads)
        self.cpp_lib.useBdfSets(self.bdf_use_sets)
        self.cpp_lib.dontDivideIntoParts(self.disable_parts)
        self.cpp_lib.useSetsOrFullMesh(self.use_sets_or_full_mesh)
        #self.cpp_lib.extractModeProperties(self.extract_mode_properties)
        if not isinstance(model_file, str):
            model_file = model_file.decode()
        if not isinstance(grouping_type, str):
            grouping_type = grouping_type.decode()    
        return self.cpp_lib.getModelMetadataPartType(model_file,grouping_type)#.decode(),
                #grouping_type)#.decode())

    def GetResultsMetadata(self, results_file):
        return self.cpp_lib.getResultsMetadata(results_file.decode())

    def GetAnsysRstModelMetadata(self, model_file, ds_dat_file, interface_grouping):
        grouping_type = self.GetGroupingType(model_file, interface_grouping)
        return self.cpp_lib.getAnsysRstModelMetadataPartType(model_file, 
                ds_dat_file, grouping_type)

    def GetModelMetadataWithExtSets(self, model_file, sets_inp_file, interface_grouping):
        self.cpp_lib.odbFastLoad(self.odb_fast_load)
        self.cpp_lib.odbZerothFrame(self.odb_load_zero_frames)
        #self.cpp_lib.dontHandleOdbContactResults(self.odb_ignore_contact_results)
        self.cpp_lib.odbLoadInternalSets(self.odb_load_internal_sets)
        self.cpp_lib.odbLoadInstanceParts(self.odb_load_instance_parts)
        grouping_type = self.GetGroupingType(model_file, interface_grouping)
        return self.cpp_lib.getModelMetadataPartTypeFromSetsFile(model_file, sets_inp_file, grouping_type)

    def PrintModelInfo(self):
        self.cpp_lib.printModelInfo()

    def PrintProcessStat(self):
        self.cpp_lib.printProcessStat()

    def GetAllTransString(self):
        return self.cpp_lib.getAllTransString()

    def DestroyDataManager(self):
        self.cpp_lib.destroyDataManager()

    def GetGlobalDomainExtent(self):
        return self.cpp_lib.computeGlobalDomainExtent()

    def ExcludeGeometry(self, yesno):
        self.exclude_geometry = yesno

    def DisableSkinning(self, yesno):
        self.disable_skinning = yesno

    def SeparatePartMeshes(self, yesno):
        self.indep_mesh_sets = yesno

    def OdbFastLoad(self, yesno):
        self.odb_fast_load = yesno

    def OdbLoadZeroFrames(self, yesno):
        self.odb_load_zero_frames = yesno

    def OdbIgnoreContactResults(self, yesno):
        self.odb_ignore_contact_results = yesno

    def OdbLoadInternalSets(self, yesno):
        self.odb_load_internal_sets = yesno

    def OdbLoadInstanceParts(self, yesno):
        self.odb_load_instance_parts = yesno

    def MarcExperimentalFeatures(self, yesno):
        self.marc_experimental_features = yesno

    def BdfUseSets(self, yesno):
        self.bdf_use_sets = yesno

    def DisableParts(self, yesno):
        self.disable_parts = yesno

    def UseSetsOrFullMesh(self, yesno):
        self.use_sets_or_full_mesh = yesno

    def SetVirtualRotationNode(self, nindex):
        self.cpp_lib.useVirtualRotationNode(nindex);

    def NodalAveragedLoads(self, yesno):
        self.nodal_averaged_loads = yesno

    def ExtractModeProperties(self, yesno):
        self.extract_mode_properties = yesno

    def GetSizeStr(self, size):
        mbdenom = 1024 * 1024
        kbdenom = 1024
        if size / mbdenom > 1:
            return '%.2f MB' % (size/mbdenom)
        elif size / kbdenom > 1:
            return '%.2f KB' % (size/kbdenom)
        else:
            return '%.2f B' % size

    def GetLinkedFilesSize(self, fname):
        
        fname = fname.decode()
        if fname.endswith('d3plot'):
            size = 0.0
            flist = glob.glob(fname + "*")
            for f in flist:
                added = f.replace(fname, '')
                if not added.strip('0123456789'):
                    size += os.path.getsize(f)
            return self.GetSizeStr(size)
        else:
            return self.GetSizeStr(os.path.getsize(fname))
        
    def UpgradeOdb(self, old_ver, new_ver):
            print ("Upgrading from " + old_ver.decode() + " to " + new_ver.decode())
            return self.cpp_lib.upgradeOdb(old_ver.decode(), new_ver.decode())

    def Process(self, engine_root):
        if self.GetRootName() == engine_root.tag:
            for parent in engine_root.getiterator():
                if "true" == parent.get("update"):
                    for child in parent:
                        if "true" == child.get("update"):
                            if "model" == child.tag: 
                                self.AddPartList(parent)
                                self.AddResultList(parent)
    
    def GenerateTfatInput(self, filename, trans_string, ignore_midnodes):
        trans_flags = 0
        if ignore_midnodes:
            trans_flags = trans_flags | 0x01
        if self.disable_skinning:
            trans_flags = trans_flags | 0x20
        tr_output = self.cpp_lib.saveTfat(filename, trans_string, trans_flags)
        return tr_output
 
    def Translate(self, filename, trans_string, ignore_midnodes, elem_res_tran, en_to_e_avg, attributes_dict, hist_json_file, modal_tables_file):
        #try:
        #    file = open('e:\\temp\\vcollab-temp\\trans_params.txt', 'w')
        #    file.write(trans_string)
        #    file.close()
        #except os.error, msg:
        #    print msg
        #return

        if self.tmp_folder:
            self.cpp_lib.setTempFileFolderIfEmpty(self.tmp_folder)
        for k, v in attributes_dict.items():
            try:
                if isinstance(k, str):
                    k = PyStrToCharPtr(k)
                if  isinstance(v, str):
                    v = PyStrToCharPtr(v)
                self.cpp_lib.addAttribute(k.decode(), v.decode())
            except Exception as ex:
                print (ex)

        if self.pi_file:
            self.cpp_lib.setPIFile(self.pi_file)
        trans_flags = 0
        if ignore_midnodes:
            trans_flags = trans_flags | 0x01
        if elem_res_tran:
            trans_flags = trans_flags | 0x02
        if en_to_e_avg:
            trans_flags = trans_flags | 0x04
        if self.indep_mesh_sets:
            trans_flags = trans_flags | 0x08
        if self.exclude_geometry:
            trans_flags = trans_flags | 0x10
        if self.disable_skinning:
            trans_flags = trans_flags | 0x20
        
        tr_output = self.cpp_lib.saveCax(filename.decode(), trans_string.decode(), trans_flags)
       
        if self.pi_file:
            self.cpp_lib.closePIFile()
        ht_output = ''
        if hist_json_file:
            ht_output = self.cpp_lib.exportHistoryDataToJson(hist_json_file)
        mt_output = ''
        if modal_tables_file:
            mt_output = self.cpp_lib.exportModalTables(modal_tables_file)

        return tr_output 
 
    def TranslateInThread(self, filename, trans_string, ignore_midnodes, elem_res_tran, en_to_e_avg, attributes_dict, hist_json_file, modal_tables_file):
        #try:
        #    file = open('e:\\temp\\vcollab-temp\\trans_params.txt', 'w')
        #    file.write(trans_string)
        #    file.close()
        #except os.error, msg:
        #    print msg
        #return

        if self.tmp_folder:
            self.cpp_lib.setTempFileFolderIfEmpty(self.tmp_folder)
        for k, v in attributes_dict.items():
            try:
                kenc = PyStrToCharPtr(k)
                venc = PyStrToCharPtr(v)
                self.cpp_lib.addAttribute(kenc, venc)
            except Exception as ex:
                print (ex)

        if self.pi_file:
            self.cpp_lib.setPIFile(self.pi_file)
        trans_flags = 0
        if ignore_midnodes:
            trans_flags = trans_flags | 0x01
        if elem_res_tran:
            trans_flags = trans_flags | 0x02
        if en_to_e_avg:
            trans_flags = trans_flags | 0x04
        if self.indep_mesh_sets:
            trans_flags = trans_flags | 0x08
        if self.exclude_geometry:
            trans_flags = trans_flags | 0x10
        if self.disable_skinning:
            trans_flags = trans_flags | 0x20
   
        tr_output = self.cpp_lib.saveCaxInThread(filename.decode(), trans_string.decode(), trans_flags)
        if self.pi_file:
            self.cpp_lib.closePIFile()
        ht_output = ''
        if hist_json_file:
            ht_output = self.cpp_lib.exportHistoryDataToJson(hist_json_file)
        mt_output = ''
        if modal_tables_file:
            mt_output = self.cpp_lib.exportHistoryDataToJson(modal_tables_file)
        return tr_output
 
    def GetInterfaceInfo(self):
        interface_info = InterfaceInfo.InterfaceInfo()
        return interface_info

    def mergeInstanceCaxFiles(self, in_files, out_file,
                    ignore_duplicate_results,
                    add_file_suffix_to_instance_name,
                    auto_rename_instance):
        return cpp_lib.merge_as_instances(in_files, out_file,
            ignore_duplicate_results, add_file_suffix_to_instance_name,
            auto_rename_instance)

#----------------------------------------------------------------------------

def getEngine():
    engine = CaeEngine()
    return engine

#----------------------------------------------------------------------------

def main():
    print("Nothing")

#----------------------------------------------------------------------------

if __name__ == '__main__':
    main()
