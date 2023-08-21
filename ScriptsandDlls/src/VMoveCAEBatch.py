#!/usr/bin/python

import sys, os, locale
import os.path
import re
import platform
#import distutils
#from distutils.util import strtobool
from str2bool import str2bool
from glob import glob
if platform.python_version() > '2.5':
    import xml.etree.ElementTree as et
else:
    import elementtree.ElementTree as et

import ErrNum
import Version
import Common
import CaeEngine
from ConfigFileReader import ConfigFileReader
from InpFileReader import InpFileReader, InpFileError
import time
import errno
import fnmatch

#----------------------------------------------------------------------------

def IsInCheckedNames(name, name_list):
    new_name = name
    if name.lower() == 'Displacement - Vibration mode'.lower():
        new_name = 'Displacement'

    new_name_lower = new_name.lower()
    new_name_stripped_lower = new_name.strip().lower()
    for elem in name_list:
        elem_lower = elem.lower()
        if elem_lower == new_name_lower:
            return True
        if elem.strip().lower() == new_name_stripped_lower:
            return True
        if fnmatch.fnmatch(new_name, elem):
            return True
        if fnmatch.fnmatch(new_name_lower, elem_lower):
            return True

    sp_list = name.split(',')
    if len(sp_list) == 1:
        return False

    sp_ind = 0
    for ind in range(len(name_list)):
        if name_list[ind].lower() == sp_list[sp_ind].lower():
            sp_ind = sp_ind + 1
        elif 0 != sp_ind:
            sp_ind = 0

    if sp_ind == len(sp_list):
        return True

    return False

#----------------------------------------------------------------------------

THRESH_MAX_NUM = 2
THRESH_MIN_NUM = 3

#----------------------------------------------------------------------------

def GetDerivedDetails(name):
    name = name.strip()
    dt_name = name
    dt_thres = (100, THRESH_MAX_NUM)
    r1 = re.compile('([a-z\d\-_\s]+)(%\d*(?:max|min))?', re.IGNORECASE)
    m1 = r1.match(name)
    if m1:
        g1 = m1.groups()
        if len(g1) > 1:
            dt_name = g1[0]
            if g1[1] != None:
                r2 = re.compile('%(\d*)(max|min)', re.IGNORECASE)
                m2 = r2.match(g1[1])
                g2 = m2.groups()
                if g2[1].lower() == 'min':
                    dt_thres = (int(g2[0]), THRESH_MIN_NUM)
                else:
                    dt_thres = (int(g2[0]), THRESH_MAX_NUM)

    return dt_name, dt_thres

#----------------------------------------------------------------------------
OPT_DICT = {
    'norot': 1024,
}

def extract_name_options(name_orig):
    name = name_orig
    addtl_flags = 0
    opt_list = []
    
    if name[-2:] == '##':
        fpos = name.find('##')
        if fpos != -1:
            opt_list = [OPT_DICT[opt_name] for opt_name in name[fpos+2:-2].split(':')]
            name = name[:fpos].strip()
    
    for opt in opt_list:
        addtl_flags = addtl_flags | opt

    return name, addtl_flags
#----------------------------------------------------------------------------
def MatchResultName(name, elem, res_type, rd_prop_list):
    if elem.lower() == name.lower():
        rd_prop_list.append([0, -1, 0, 100, THRESH_MAX_NUM])
        return
    
    esl = elem.strip().lower()
    nnsl = name.strip().lower()

    esl, rflags = extract_name_options(esl)

    if fnmatch.fnmatch(nnsl, esl):
        rd_prop_list.append([rflags, -1, 0, 100, THRESH_MAX_NUM])
        return

    #if not esl.startswith(nnsl) and not esl.startswith('element ' + nnsl) and not esl.startswith('elemental ' + nnsl):
    #    return

    avg_type_vals = [(' [avg]', 1), (' [max]', 2), 
                    (' [min]', 3), ('[geoavg]', 4)]
    avg_type_num = 0
    if esl.endswith(']'):
        for avg_type_pair in avg_type_vals:
            if esl.endswith(avg_type_pair[0]):
                avg_type_num = avg_type_pair[1]
                avg_type_pos = esl.find(avg_type_pair[0])
                esl = esl[0:avg_type_pos]
                break

    dt_num = -1
    dt_pos = esl.find(" - ")
    dt_thres = (100, THRESH_MAX_NUM)
    if dt_pos != -1:
        res_name = esl[0:dt_pos].strip()
        dt_name = esl[dt_pos + len(" - "):].strip()
        dt_name, dt_thres = GetDerivedDetails(dt_name)
        dt_num = GetDerivedTypeNum(res_type, dt_name)
        if dt_num != 0:
            esl = res_name
        else:
            dt_num = -1

    if esl == nnsl:
        rd_prop_list.append([rflags, dt_num, avg_type_num, dt_thres[0], dt_thres[1]])
        return

    '''
    if esl == "node " + nnsl or esl == "nodal " + nnsl or esl == nnsl + " node" or esl == nnsl + " nodal":
        rd_prop_list.append([256|rflags, dt_num, avg_type_num, dt_thres[0], dt_thres[1]])
        return

    if esl == "element " + nnsl or esl == "elemental " + nnsl or esl == nnsl + " element" or esl == nnsl + " elemental":
        rd_prop_list.append([512|rflags, dt_num, avg_type_num, dt_thres[0], dt_thres[1]])
        return
    '''

    pref_masks = {
            'element': 512,
            'elemental': 512,
            'node': 256,
            'nodal': 256,
    }

    for retype, mask in pref_masks.items():
        prefix = retype + ' '
        suffix = ' ' + retype
        if esl.startswith(prefix):
            esl2 = esl[len(prefix):]
            if fnmatch.fnmatch(nnsl, esl2):
                rd_prop_list.append([mask|rflags, dt_num, avg_type_num, dt_thres[0], dt_thres[1]])
        if esl.endswith(suffix):
            esl2 = esl[:len(prefix)]
            if fnmatch.fnmatch(nnsl, esl2):
                rd_prop_list.append([mask|rflags, dt_num, avg_type_num, dt_thres[0], dt_thres[1]])

#----------------------------------------------------------------------------

def IsInCheckedResultNames(name, res_type, rd_prop_list, name_list):
    if not name_list:
        return False

    new_name = name
    if name.lower() == 'Displacement - Vibration mode'.lower():
        new_name = 'Displacement'

    sp_list = name.split(',')
    # for results with "," in its name
    if len(sp_list) > 1:
        st_ind = 0
        for ind in range(len(name_list)):
            if name_list[ind].lower().endswith(sp_list[0].lower()):
                concat_name = ', '.join(name_list[ind:ind + len(sp_list)])
                MatchResultName(new_name, concat_name, res_type, rd_prop_list)

    for elem in name_list:
        MatchResultName(new_name, elem, res_type, rd_prop_list)

    if rd_prop_list:
        return True

    return False

#----------------------------------------------------------------------------
def IsInCheckedPartIds(pid, part_list):
    for elem in part_list:
        prange = elem.split('-')
        if len(prange) == 1:
            try:
                if pid == int(elem):
                    return True
                else:
                    continue
            except ValueError:
                continue

        low = None
        high = None
        try:
            low = int(prange[0])
        except ValueError:
            pass
        try:
            high = int(prange[1])
        except ValueError:
            pass

        if low and high:
            if low <= pid and high >= pid:
                return True
            if low >= pid and high <= pid:
                return True

        elif low:
            if low <= pid:
                return True

        elif high:
            if high >= pid:
                return True

    return False

#----------------------------------------------------------------------------

LAST_FRAME_CHAR = '_'

#----------------------------------------------------------------------------

def IsInInstanceVals(inst, vals, last_step = None, last_frames = None):
    if last_step != None:
        if last_frames != None:
            if(vals[0] == LAST_FRAME_CHAR and vals[1] == LAST_FRAME_CHAR):
                return inst[0] == last_step and inst[1] == last_frames.get(last_step, '')
            elif not vals[0] and vals[1] == LAST_FRAME_CHAR:
                return inst[1] == last_frames.get(inst[0], '')
            elif vals[0] == LAST_FRAME_CHAR and not vals[1]:
                return inst[0] == last_step
            elif vals[1] == LAST_FRAME_CHAR:
                return inst[0] == vals[0] and inst[1] == last_frames.get(inst[0], '')
            elif vals[0] == LAST_FRAME_CHAR:
                return inst[0] == last_step
        elif vals[0] == LAST_FRAME_CHAR:
            return inst[0] == last_step and (inst[1] == vals[1] or not
                    inst[1])
    if not vals[0] or inst[0] == vals[0]:
        if not inst[1]:
            return True
        if not vals[1] or inst[1] == vals[1]:
            return True
    return False

#----------------------------------------------------------------------------

def IsInInstanceRange(inst, lows, highs, last_step = None, last_frames = None):
    if last_step != None and highs[0] == LAST_FRAME_CHAR:
        highs[0] = last_step

    if last_step != None:
        if last_frames != None:
            if(lows[1] == LAST_FRAME_CHAR and highs[1] == LAST_FRAME_CHAR):
                if not lows[0]:
                    iinst0 = int(inst[0])
                    ihigh0 = int(highs[0])
                    return (iinst0 <= ihigh0) and (
                            inst[1] == '' or inst[1] == last_frames[inst[0]])
                elif not highs[0]:
                    iinst0 = int(inst[0])
                    ilow0 = int(lows[0])
                    return (iinst0 >= ilow0) and (
                            inst[1] == '' or inst[1] == last_frames[inst[0]])
                else:
                    iinst0 = int(inst[0])
                    ilow0 = int(lows[0])
                    ihigh0 = int(highs[0])
                    return (iinst0 >= ilow0 and iinst0 <= ihigh0) and (
                            inst[1] == '' or inst[1] == last_frames[inst[0]])
            if(lows[0] == LAST_FRAME_CHAR and highs[0] == LAST_FRAME_CHAR):
                if not lows[1]:
                    iinst1 = int(inst[1])
                    ihigh1 = int(highs[1])
                    return (inst[0] == last_step) and (iinst1 <= ihigh1)
                elif not highs[1]:
                    iinst1 = int(inst[1])
                    ilow1 = int(lows[1])
                    return (inst[0] == last_step) and (iinst1 >= ilow1)
                else:
                    iinst1 = int(inst[1])
                    ilow1 = int(lows[1])
                    ihigh1 = int(highs[1])
                    return (inst[0] == last_step) and (iinst1 >= ilow1 and iinst1 <= ihigh1)
        elif highs[0] == LAST_FRAME_CHAR:
            iinst0 = int(inst[0])
            ilow0 = int(lows[0])
            return iinst0 >= ilow0
    if (not lows[0] or int(inst[0]) >= int(lows[0])) and (not highs[0] or int(inst[0]) <= int(highs[0])):
        if not inst[1]:
            return True
        if inst[1] and (not lows[1] or int(inst[1]) >= int(lows[1])) and (not highs[1] or int(inst[1]) <= int(highs[1])):
            return True
    return False

#----------------------------------------------------------------------------
def IsInCheckedInstances(res_name, inst_list, last_step = None, last_frames = None):
    slist = res_name.split(':')
    if len(slist) < 2:
        return True

    inst= slist[1:]
    if len(inst) == 1:
        inst.append('')

    for elem in inst_list:
        vals = []
        lows = []
        highs = []
        irange = elem.split('-')
        if len(irange) == 1:
            vals = elem.split(':')
        if len(irange) > 1:
            lows = irange[0].split(':')
            highs = irange[1].split(':')

        if len(vals) == 1:
            vals.append('')
        if len(lows) == 1:
            lows.append('')
        if len(highs) == 1:
            highs.append('')

        if vals:
            rv = IsInInstanceVals(inst, vals, last_step, last_frames)
        elif lows and highs:
            try:
                rv = IsInInstanceRange(inst, lows, highs, last_step, last_frames)
            except (ValueError, KeyError):
                rv = None

        if rv:
            return rv

    return False

#----------------------------------------------------------------------------
def get_bool_val(opdict, opt):
    if opt in opdict:
        #return strtobool(opdict.get(opt, 'False'))
        #str2bool
        return str2bool(opdict.get(opt, 'False'))
    else:
        return None

#----------------------------------------------------------------------------
def SelectListedParts(trans_dict, opdict, disable_odb_system_sets):
    part_list = trans_dict['Parts'][0]
    part_dict = trans_dict['Parts'][1]

    tpart_ids = [str.strip() for str in opdict.get('--part-ids', '').split(',') if str]
    fpart_ids = [str.strip() for str in opdict.get('--filter-part-ids', '').split(',') if str]

    tparts = [str.strip() for str in opdict.get('--parts', '').split(',') if str]
    fparts = [str.strip() for str in opdict.get('--filter-parts', '').split(',') if str]

    if disable_odb_system_sets:
        fparts.append(' ALL ELEMENTS')
        fparts.append('WarnElem*')

    for part_id, part_name in part_list:
        if IsInCheckedNames(part_name, tparts):
            tpart_ids.append(repr(part_id))
        if IsInCheckedNames(part_name, fparts):
            fpart_ids.append(repr(part_id))

    if tpart_ids:
        fpart_ids = None

    if not tpart_ids and not fpart_ids:
        for part_id in part_dict.keys():
            part_dict[part_id] = True
        return

    if tpart_ids:
        # Check selected
        for part_id in part_dict.keys():
            if IsInCheckedPartIds(part_id, tpart_ids):
                part_dict[part_id] = True
            else:
                part_dict[part_id] = False
        return

    if fpart_ids:
        # Uncheck selected
        for part_id in part_dict.keys():
            if IsInCheckedPartIds(part_id, fpart_ids):
                part_dict[part_id] = False
            else:
                part_dict[part_id] = True
        return

#----------------------------------------------------------------------------
def UpdateResultMultiTypes(res_list):
    index = 0
    while index < len(res_list):
        res_prop = res_list[index]
        rd_prop_list = res_prop[12]
        num_rd_prop = len(rd_prop_list)
        if num_rd_prop > 1:
            for new_rd in rd_prop_list[1:]:
                new_res_prop = res_prop[:]
                new_res_prop[7] = new_rd[0]
                new_res_prop[8] = new_rd[1]
                new_res_prop[9] = new_rd[2]
                new_res_prop[10] = new_rd[3]
                new_res_prop[11] = new_rd[4]
                index = index + 1
                res_list.insert(index, new_res_prop)
        index = index + 1

#----------------------------------------------------------------------------

def compute_last_step_frames(res_list):
    last_step = None
    last_frames = None
    last_step_int = None
    last_frames_int = None
    for res_prop in res_list:
        res_name = res_prop[1]
        elem = res_name.split(':')
        if len(elem) <= 1:
            continue

        sstep = None
        sframe = None

        if len(elem) > 1:
            try:
                iv = int(elem[1])
                sstep = elem[1]
            except ValueError:
                pass

        if len(elem) > 2:
            try:
                iv = int(elem[2])
                if sstep is None:
                    sstep = elem[2]
                else:
                    sframe = elem[2]
            except ValueError:
                sstep = None

        if sstep is not None:
            istep = int(sstep)
            if last_step_int is None:
                last_step = sstep
                last_step_int = istep
            elif istep > last_step_int: 
                last_step = sstep
                last_step_int = istep
        if sframe is not None:
            iframe = int(sframe)
            if last_frames is None:
                last_frames = {sstep: sframe}
                last_frames_int = {istep: iframe}
            elif istep not in last_frames_int:
                last_frames[sstep] = sframe
                last_frames_int[istep] = iframe
            elif iframe > last_frames_int[istep]:
                last_frames[sstep] = sframe
                last_frames_int[istep] = iframe

    return last_step, last_frames

#----------------------------------------------------------------------------
def SelectListedResults(trans_dict, opdict):
    res_list = trans_dict['Result Instances'][0]
    res_dict = trans_dict['Result Instances'][1]

    # Select all result instances by default
    for rindex in res_dict.keys():
        res_dict[rindex] = True

    default_result_translation = get_bool_val(opdict,
            '--default-result-translation')
    tresults =[str.strip() for str in opdict.get('--results', '').split(',') if str] 
    fresults = [str.strip() for str in opdict.get('--filter-results', '').split(',') if str]

    tinstances = [str.strip() for str in opdict.get('--instances', '').split(',') if str]
    finstances = [str.strip() for str in opdict.get('--filter-instances', '').split(',') if str]
    tnresults =[str.strip() for str in opdict.get('--nodal-results', '').split(',') if str] 
    if len(tnresults) == 0:
        tnresults =[str.strip() for str in opdict.get('--node-results', '').split(',') if str] 
    teresults =[str.strip() for str in opdict.get('--element-results', '').split(',') if str] 

    tlayers = [str.strip() for str in opdict.get('--sections', '').split(',') if str]

    layer_vals = {  'Top': 1, 'Bottom': 2, 'Mid': 4, 
                    'Maximum': 8, 'Average': 16, 'Minimum': 32 }
    layer_aggr_val = 0
    for layer_name in tlayers:
        if layer_name in layer_vals:
            layer_aggr_val = layer_aggr_val | layer_vals[layer_name]
    if layer_aggr_val:
        trans_dict['Result Layers'] = layer_aggr_val

    last_step, last_frames = compute_last_step_frames(res_list)
    for res_prop in res_list:
        res_no_sec_name = res_prop[4]
        res_res_type = res_prop[3]
        #rd_prop = [0, -1]
        rd_prop_list = []
        if res_no_sec_name.find(" (All Sections)") != -1 and res_no_sec_name not in tnresults and res_no_sec_name not in teresults:
            res_no_sec_name = res_no_sec_name.replace(" (All Sections)", "")
        if res_no_sec_name.find(" (Centroidal)") != -1 and res_no_sec_name not in tnresults and res_no_sec_name not in teresults:
            res_no_sec_name = res_no_sec_name.replace(" (Centroidal)", "")
        if res_no_sec_name.find(" [Real]") != -1 and res_no_sec_name not in tnresults and res_no_sec_name not in teresults:
            res_no_sec_name = res_no_sec_name.replace(" [Real]", "")
        if res_no_sec_name.find(" [Imaginary]") != -1 and res_no_sec_name not in tnresults and res_no_sec_name not in teresults:
            res_no_sec_name = res_no_sec_name.replace(" [Imaginary]", "")
        if IsInCheckedResultNames(res_no_sec_name, res_res_type, rd_prop_list, tnresults) and rd_prop_list:
            rd_prop = rd_prop_list[0]
            res_dict[res_prop[2]] = True
            res_prop[7] = 256
            res_prop[8] = rd_prop[1]
            res_prop[9] = rd_prop[2]
            res_prop[10] = rd_prop[3]
            res_prop[11] = rd_prop[4]
            res_prop[12] = rd_prop_list
        elif IsInCheckedResultNames(res_no_sec_name, res_res_type, rd_prop_list, teresults) and rd_prop_list:
            rd_prop = rd_prop_list[0]
            res_dict[res_prop[2]] = True
            res_prop[7] = 512
            res_prop[8] = rd_prop[1]
            res_prop[9] = rd_prop[2]
            res_prop[10] = rd_prop[3]
            res_prop[11] = rd_prop[4]
            res_prop[12] = rd_prop_list

    if tresults:
        fresults = None
    if tinstances:
        finstances = None

    if not tresults:
        for res_prop in res_list:
            res_dict[res_prop[2]] = True
        if tinstances:
            for res_prop in res_list:
                if not IsInCheckedInstances(res_prop[1], tinstances, last_step, last_frames):
                    res_dict[res_prop[2]] = False
        if finstances:
            for res_prop in res_list:
                if IsInCheckedInstances(res_prop[1], finstances, last_step, last_frames):
                    res_dict[res_prop[2]] = False
        if fresults:
            for res_prop in res_list:
                res_no_sec_name = res_prop[4]
                res_res_type = res_prop[3]
                if res_no_sec_name.find(" (All Sections)") != -1 and res_no_sec_name not in fresults:
                    res_no_sec_name = res_no_sec_name.replace(" (All Sections)", "")
                if res_no_sec_name.find(" (Centroidal)") != -1 and res_no_sec_name not in fresults:
                    res_no_sec_name = res_no_sec_name.replace(" (Centroidal)", "")
                if res_no_sec_name.find(" [Real]") != -1 and res_no_sec_name not in fresults:
                    res_no_sec_name = res_no_sec_name.replace(" [Real]", "")
                if res_no_sec_name.find(" [Imaginary]") != -1 and res_no_sec_name not in fresults:
                    res_no_sec_name = res_no_sec_name.replace(" [Imaginary]", "")
                rd_prop_list = []
                if IsInCheckedResultNames(res_no_sec_name, res_res_type, rd_prop_list, fresults) and rd_prop_list:
                    res_dict[res_prop[2]] = False
        return

    default_status = False
    if default_result_translation:
        default_status = True

    for res_prop in res_list:
        res_dict[res_prop[2]] = default_status

    if tinstances and default_status:
        for res_prop in res_list:
            if not IsInCheckedInstances(res_prop[1], tinstances, last_step, last_frames):
                res_dict[res_prop[2]] = False
    if finstances and default_status:
        for res_prop in res_list:
            if IsInCheckedInstances(res_prop[1], finstances, last_step, last_frames):
                res_dict[res_prop[2]] = False

    # tresults is True
    for res_prop in res_list:
        res_no_sec_name = res_prop[4]
        res_res_type = res_prop[3]
        if res_no_sec_name.find(" (All Sections)") != -1 and res_no_sec_name not in tresults:
            res_no_sec_name = res_no_sec_name.replace(" (All Sections)", "")
        if res_no_sec_name.find(" (Centroidal)") != -1 and res_no_sec_name not in tresults:
            res_no_sec_name = res_no_sec_name.replace(" (Centroidal)", "")
        if res_no_sec_name.find(" [Real]") != -1 and res_no_sec_name not in tresults:
            res_no_sec_name = res_no_sec_name.replace(" [Real]", "")
        if res_no_sec_name.find(" [Imaginary]") != -1 and res_no_sec_name not in tresults:
            res_no_sec_name = res_no_sec_name.replace(" [Imaginary]", "")
        # Check if selected
        #rd_prop = [0, -1, 0]
        rd_prop_list = []
        if IsInCheckedResultNames(res_no_sec_name, res_res_type, rd_prop_list, tresults) and rd_prop_list:
            rd_prop = rd_prop_list[0]
            #print res_no_sec_name, res_res_type, rd_prop[1], rd_prop[0], tresults
            if tinstances: 
                if IsInCheckedInstances(res_prop[1], tinstances, last_step, last_frames):
                    res_dict[res_prop[2]] = True
                    res_prop[7] = rd_prop[0]
                    res_prop[8] = rd_prop[1]
                    res_prop[9] = rd_prop[2]
                    res_prop[10] = rd_prop[3]
                    res_prop[11] = rd_prop[4]
                    res_prop[12] = rd_prop_list
                else:
                    res_dict[res_prop[2]] = False
            elif finstances:
                if not IsInCheckedInstances(res_prop[1], finstances, last_step, last_frames):
                    res_dict[res_prop[2]] = True
                    res_prop[7] = rd_prop[0]
                    res_prop[8] = rd_prop[1]
                    res_prop[9] = rd_prop[2]
                    res_prop[10] = rd_prop[3]
                    res_prop[11] = rd_prop[4]
                    res_prop[12] = rd_prop_list
                else:
                    res_dict[res_prop[2]] = False
            else:
                res_dict[res_prop[2]] = True
                res_prop[7] = rd_prop[0]
                res_prop[8] = rd_prop[1]
                res_prop[9] = rd_prop[2]
                res_prop[10] = rd_prop[3]
                res_prop[11] = rd_prop[4]
                res_prop[12] = rd_prop_list
    UpdateResultMultiTypes(res_list)

#----------------------------------------------------------------------------
def SelectListedFeatures(trans_dict, opdict):
    SelectListedCutSections(trans_dict, opdict)
    SelectListedIsoSurfaces(trans_dict, opdict)
    SelectListedFlowLines(trans_dict, opdict)

#----------------------------------------------------------------------------
def SelectListedCutSections(trans_dict, opdict):
    cutsec_list = trans_dict['Cut-Sections'][0]
    cutsec_dict = trans_dict['Cut-Sections'][1]

    tcutsec_eqns = [str.strip() for str in opdict.get('--cut-sections', '').split(',') if str]
    for cutsec_eqn in tcutsec_eqns:
        cutsec_list.append([-1, cutsec_eqn])
        cutsec_dict[cutsec_eqn] = True

#----------------------------------------------------------------------------
def SelectListedIsoSurfaces(trans_dict, opdict):
    isosurf_list = trans_dict['Iso-Surfaces'][0]
    isosurf_dict = trans_dict['Iso-Surfaces'][1]

    results_list = trans_dict['Result Instances'][0]
    results_dict = trans_dict['Result Instances'][1]

    tisosurf_eqns = [str.strip() for str in opdict.get('--iso-surfaces', '').split(',') if str]
    for isosurf_expr in tisosurf_eqns:
        isosurf_label = isosurf_expr
        isosurf_res = None
        isosurf_val = None
        isosurf_status = True

        isosurf_pair = isosurf_expr.split('=',1)
        isosurf_res = isosurf_pair[0].strip()
        isosurf_val = isosurf_pair[1].strip()

        if isosurf_res and isosurf_val:
            for result_prop in results_list:
                isosurf_dt = None
                if isosurf_res == result_prop[4]:
                    pass
                elif isosurf_res.startswith(result_prop[4]):
                    isosurf_dt = isosurf_res[len(result_prop[4]):].strip()
                else:
                  continue

                result_dsname = result_prop[1]
                result_instance_info = result_dsname.split(':')
                result_compname = result_instance_info[0]
                isosurf_eqn = result_compname + '=' + isosurf_val

                isosurf_dtype_num = 0
                if isosurf_dt:
                    isosurf_dtype_num = GetDerivedTypeNum(result_prop[3], isosurf_dt)
                    if isosurf_dtype_num == 0:
                        continue
                isosurf_num = -2 - isosurf_dtype_num
                #print isosurf_num, isosurf_eqn
                if isosurf_eqn not in isosurf_dict:
                        isosurf_list.append([isosurf_num, isosurf_eqn, isosurf_label])
                        isosurf_dict[isosurf_label] = isosurf_status
                break


#----------------------------------------------------------------------------
def SelectListedFlowLines(trans_dict, opdict):
    flowline_list = trans_dict['Flow Lines'][0]
    flowline_dict = trans_dict['Flow Lines'][1]

    parts_list = trans_dict['Parts'][0]
    parts_dict = trans_dict['Parts'][1]
    results_list = trans_dict['Result Instances'][0]
    results_dict = trans_dict['Result Instances'][1]

    tflowline_eqns = [str.strip() for str in re.findall(r'\[.*?\]', opdict.get('--field-lines', '')) if str]
    if not tflowline_eqns:
        tflowline_eqns = [str.strip() for str in re.findall(r'\[.*?\]', opdict.get('--flow-lines', '')) if str]
    for flowline_eqn in tflowline_eqns:
        flst = flowline_eqn.lstrip('[').rstrip(']').split(',')
        if len(flst) < 2:
          continue

        if(flst[1].lstrip().startswith('(') and len(flst) > 4):
            flst_fixed = []
            flst_fixed.append(flst[0])
            flst_fixed.append(flst[1] + ',' + flst[2] + ',' + flst[3])
            flst_fixed.extend(flst[4:])
            flst = flst_fixed

        fline_num = -1
        fline_res= flst[0].strip()
        fline_from = flst[1].strip()
        fline_numlines = 0
        if len(flst) > 2:
          fline_numlines = int(flst[2].strip())
        fline_ts = 0.001
        fline_steps = 200
        fline_freq = 10
        fline_status = True

        if not fline_from or not fline_res:
          continue

        for result_prop in results_list:
            if fline_res == result_prop[4]:
                result_dsname = result_prop[1]
                result_instance_info = result_dsname.split(':')
                result_compname = result_instance_info[0]
                fline_eqn = 'From '
                is_part = False
                for part_prop in parts_list:
                    if part_prop[1] == fline_from:
                        fline_eqn += 'Part id %d' %(part_prop[0])
                        is_part = True
                if not is_part:
                    fline_eqn += 'Point ' + fline_from
                fline_eqn += ' number of lines %d' %(fline_numlines)
                fline_eqn += ' for result ' + result_compname
                if fline_num == -2:
                    fline_eqn += ' time step %f steps %d frequency %d' %(fline_ts, fline_steps, fline_freq)

                if fline_eqn not in flowline_dict:
                    flowline_list.append([fline_num, fline_eqn])
                    flowline_dict[fline_eqn] = fline_status

#----------------------------------------------------------------------------
def GetTransString(model_metadata, results_metadata = None, option_list = None):
    data_tree = None
    data_tree = et.fromstring(model_metadata)

    trans_dict = {'Parts': [[], {}], 
                  'Feature Edges': [[], {}],
                  'Cut-Sections': [[], {}],
                  'Iso-Surfaces': [[], {}],
                  'Flow Lines': [[], {}],
                  'Element Groups' : [[], {}],
                  'Result Instances': [[], {}],
                  'Result Layers': 3,
                  }
    model_file_type = data_tree.get('type', 'Unknown')
    if not option_list:
        if model_file_type == 'Abaqus ODB':
            option_list.append('--filter-parts=""')
        else:
            return ''

    if len(option_list) == 1 and option_list[0].startswith('--model-file-format='):
        return ''
    if len(option_list) == 1 and option_list[0] == '--translate-element-results':
        return ''
    if len(option_list) == 1 and option_list[0] == '--element-nodal-results-to-element-results':
        return ''
    if len(option_list) == 1 and option_list[0] == '--default-element-results':
        return ''
    if len(option_list) == 1 and option_list[0] == '--no-averaging-across-materials':
        return ''

    rstatdict = {}
    GenerateLists(data_tree, trans_dict, rstatdict)
    if results_metadata:
        data_tree = et.fromstring(results_metadata)
        if model_file_type == 'Ansys input' and 'metadata' == data_tree.tag and data_tree.get('type', 'Unknown') == 'ANSYS result':
            trans_dict = {'Parts': [[], {}], 
                  'Feature Edges': [[], {}],
                  'Cut-Sections': [[], {}],
                  'Iso-Surfaces': [[], {}],
                  'Flow Lines': [[], {}],
                  'Element Groups' : [[], {}],
                  'Result Instances': [[], {}],
                  'Result Layers': 3,
                  }
        GenerateLists(data_tree, trans_dict, rstatdict)

    opdict = {}
    for option in option_list:
        if option.find('=') != -1:
            [key, value] = option.split('=',1)
            opdict[key] = value

    disable_odb_system_sets = False
    if model_file_type == 'Abaqus ODB' and '--enable-abaqus-system-sets' not in option_list:
        disable_odb_system_sets = True

    SelectListedParts(trans_dict, opdict, disable_odb_system_sets)
    SelectListedResults(trans_dict, opdict)
    SelectListedFeatures(trans_dict, opdict)

    #print '-------------------------------------------------------------------'
    #print 'Translation Dictionary : '
    #print trans_dict
    #res_list = trans_dict['Result Instances'][0]
    #print res_list
    #res_dict = trans_dict['Result Instances'][1]
    #for item in res_list:
    #    print '\t%30s : %10s' %(item[1], str(res_dict[item[2]]))
    #print '-------------------------------------------------------------------'
    return GenerateTransString(trans_dict)
#----------------------------------------------------------------------------

def EncodedFileName(file_path):
    fpexp = os.path.expanduser(file_path)
    #fn, ext = os.path.splitext(fpexp)
    return fpexp.encode('UTF-8')
    #if(ext.lower() == '.odb'):
    #    return fpexp.encode('UTF-8')
    #else:
    #    return fpexp.encode(locale.getpreferredencoding())
#----------------------------------------------------------------------------

def Utf8String(file_path):
        print(file_path)
        return file_path#.decode(locale.getpreferredencoding())
        
#----------------------------------------------------------------------------
def absFilePath(file_path):
        return Utf8String(os.path.abspath(file_path))

#----------------------------------------------------------------------------
def VMoveCAEBatch(engine, tmpdir, option_list, file_list):
    model_file = None
    results_file = None
    output_file = None
    upgrade_file = None
    conf_file = None
    retval = ErrNum.NO_ERROR

    if '--exclude-geometry' in option_list:
        engine.ExcludeGeometry(True)

    if '--no-averaging-across-materials' in option_list:
        engine.SeparatePartMeshes(True)

    if len(file_list) > 3:
        if file_list[1].lower() == '-upgradeodb':
            model_file = absFilePath(file_list[2])
            upgrade_file = absFilePath(file_list[3])
        elif file_list[1].lower() == '-b':
            conf_file = absFilePath(file_list[2])
            if len(file_list) == 4:
                output_file = absFilePath(file_list[3])
            if len(file_list) == 5:
                model_file = absFilePath(file_list[3])
                output_file = absFilePath(file_list[4])
            if len(file_list) == 6:
                model_file = absFilePath(file_list[3])
                results_file = absFilePath(file_list[4])
                output_file = absFilePath(file_list[5])
        else:
            model_file = absFilePath(file_list[1])
            results_file = []
            for file in file_list[2:-1]:
                results_file.extend(glob(absFilePath(file)))
            #results_file = file_list[2:-1]
            output_file = absFilePath(file_list[-1])
    else:
        if file_list[1].lower() == '-b':
            conf_file = absFilePath(file_list[2])
        else:
            model_file = absFilePath(file_list[1])
            output_file = absFilePath(file_list[2])

    if output_file and output_file.lower() == '*.cax':
        cax_sep_list = [os.path.basename(model_file), model_file]
        while cax_sep_list[1]:
            cax_sep_list = os.path.splitext(cax_sep_list[0])
        output_file = output_file.replace('*', cax_sep_list[0], 1)

    license_status = engine.AcquireLicense()
    if 'True' == license_status:
        engine.LicenseHeartbeatsIdle(False)
        if upgrade_file:
            start = time.process_time()
            engine.UpgradeOdb(EncodedFileName(model_file), EncodedFileName(upgrade_file))
            end = time.process_time()
            print('Time taken for upgrading odb = %s seconds' %(end-start))
        elif conf_file:
            conf_name_ext = os.path.splitext(os.path.basename(conf_file))
            try:
                if len(conf_name_ext) > 1 and conf_name_ext[1].lower() == '.xml':
                    inp_tree = et.parse(conf_file)
                    ProcessXmlConf(engine, inp_tree.getroot(), option_list, model_file, results_file, output_file)
                else:
                    ProcessTextConf(engine, conf_file, option_list, model_file, results_file, output_file)
            except Exception as ex:
                print('Unable to process file "%s".' %(conf_file))
        else:
            retval = Translate(engine, tmpdir, model_file, results_file, output_file, option_list)
            engine.PrintProcessStat()
        
        engine.ReleaseLicense()
    else:
        print('\nVMoveCAE license is not available.\nExiting Application')
        retval = ErrNum.LICENSE_ERROR

    return retval

#----------------------------------------------------------------------------

def Translate(engine, tmpdir, model_file, results_file, output_file, option_list = None):
    #sys.stdout = open('vmovecae.log', 'w')
    is_appendable = False
    odb_version = engine.GetAbaqusOdbVersion()
    retval = ErrNum.NO_ERROR

    upgrade_odb_message = '\nVMoveCAE %s supports Abaqus .odb files ' % (Version.VERSION)
    upgrade_odb_message += 'of version ' + odb_version + ' only.\n'
    upgrade_odb_message += 'Input file "'+ model_file
    upgrade_odb_message += '" belongs to a older version.\n'
    upgrade_odb_message += 'Please upgrade to a odb file of version ' 
    upgrade_odb_message += odb_version + ' using \nVMoveCAEBatch.exe -upgradeodb '
    upgrade_odb_message += '<old_version_file> <new_version_file> '

    upgrade_file = os.path.join(tmpdir.getPath(), 
                    os.path.basename(model_file).replace('.odb', '_v'+odb_version+'.odb'))
    upgrading_odb_message = '\nVMoveCAE %s supports Abaqus .odb files ' % (Version.VERSION)
    upgrading_odb_message += 'of version ' + odb_version + ' only.\n'
    upgrading_odb_message += 'Input file "' + model_file
    upgrading_odb_message += '" belongs to a older version.\n'

    tfat_input = False;
    if "extract-tfat-data" in option_list:
        tfat_input = True
        
    model_format_str = None
    ds_dat_file = None
    sets_inp_file = None
    hist_json_file = None
    modal_tables_file = None
    option_dict = {}
    for option in option_list:
        option = option.lstrip('-')
        key_pair = option.split('=')
        if len(key_pair) > 1:
            option_dict[key_pair[0]] = key_pair[1]
        else:
            option_dict[key_pair[0]] = ''
    if 'ansys-input-commands' in option_dict:
        ds_dat_file = option_dict['ansys-input-commands']
    if 'abaqus-input-file' in option_dict:
        sets_inp_file = option_dict['abaqus-input-file']
    if 'lsdyna-input-file' in option_dict:
        sets_inp_file = option_dict['lsdyna-input-file']
    if 'model-file-format' in option_dict:
        model_format_str = option_dict['model-file-format']
    rigid_node_key = 'rigid-rotation-from-node'
    if rigid_node_key in option_dict:
        try:
            rrnid = (int) (option_dict[rigid_node_key])
            option_dict[rigid_node_key] = rrnid
        except ValueError:
            print('Ignoring invalid value for option: ', rigid_node_key)
    enable_rigid_rotation_from_virtual_node = False
    virtual_node_index_for_rigid_rotation = 9000001
    if rigid_node_key in option_dict:
        enable_rigid_rotation_from_virtual_node = True
        virtual_node_index_for_rigid_rotation = option_dict[rigid_node_key]
    hist_json_file_key = 'export-history-data'
    if hist_json_file_key in option_dict:
        hist_json_file = option_dict[hist_json_file_key]
    modal_tables_file_key = 'export-mode-tables'
    if modal_tables_file_key in option_dict:
        modal_tables_file = option_dict[modal_tables_file_key]

    enable_local_cache = False;
    if '--enable-input-files-caching' in option_list:
        enable_local_cache = True
    exfiles = Common.ExtractedFiles(model_file, tmpdir.getPath(), 
                            engine.GetWildCards(engine.MODEL_FILE),
                            enable_local_cache)

    if '--enable-odb-fast-load' in option_list:
        engine.OdbFastLoad(True)
    if '--enable-odb-load-zero-frames' in option_list:
        engine.OdbLoadZeroFrames(True)
    if '--skip-odb-contact-results' in option_list:
        engine.OdbIgnoreContactResults(True)
    if '--enable-odb-internal-sets' in option_list:
        engine.OdbLoadInternalSets(True)
    if '--enable-odb-instance-parts' in option_list:
        engine.OdbLoadInstanceParts(True)
    if '--enable-marc-experimental-features' in option_list:
        engine.MarcExperimentalFeatures(True)
    if '--enable-bdf-sets' in option_list:
        engine.BdfUseSets(True)
    if '--disable-parts' in option_list:
        engine.DisableParts(True)
    if '--enable-bdf-sets' in option_list and '--disable-parts' in option_list:
        engine.UseSetsOrFullMesh(True)
    if '--nodal-averaged-loads' in option_list:
        engine.NodalAveragedLoads(True)
    if '--extract-mode-properties' in option_list:
        engine.ExtractModeProperties(True)

    results_instance_title_key = 'instance-title'
    enable_appending_instances = False
    if results_instance_title_key in option_dict:
        results_instance_title = option_dict[results_instance_title_key]
        engine.SetResultsInstanceTitle(results_instance_title)
        enable_appending_instances = True

    part_grouping_type_key = 'part-grouping'
    if part_grouping_type_key in option_dict:
        part_grouping_type = option_dict[part_grouping_type_key]
        engine.SetPartGroupingType(part_grouping_type)
    else:
        engine.ResetPartGroupingType()

    model_file = exfiles[1][0]
    (fname, fext) = os.path.splitext(model_file)
    fname = fname.lower()
    fext = fext.lower()
    if (fext != '.op2' and fext != '.OP2'):
        enable_rigid_rotation_from_virtual_node = False
    if (fext == '.rst' or fext == '.rth') and ds_dat_file:
        if not os.path.dirname(ds_dat_file):
            ds_dat_file = os.getcwd() + os.sep + ds_dat_file
        start = time.process_time()
        model_meta_data = engine.GetAnsysRstModelMetadata(EncodedFileName(model_file), EncodedFileName(ds_dat_file), None)
        end = time.process_time()
        print('Time taken for loading model = %s seconds' %(end-start))
    elif (fext == '.odb' or fext == '.d3plot' or fname == '.ptf' or fname == 'd3plot') and sets_inp_file:
        if not os.path.dirname(sets_inp_file):
            sets_inp_file = os.getcwd() + os.sep + sets_inp_file
        start = time.process_time()
        model_meta_data = engine.GetModelMetadataWithExtSets(EncodedFileName(model_file), EncodedFileName(sets_inp_file), None)
        end = time.process_time()
        print('Time taken for loading model = %s seconds' %(end-start))
    elif model_format_str:
        start = time.process_time()
        model_meta_data = engine.GetFormatModelMetadata(EncodedFileName(model_file), model_format_str, None)
        end = time.process_time()
        print('Time taken for loading model = %s seconds' %(end-start))
    else:
        #start = time.clock()
        start = time.process_time()
        model_meta_data = engine.GetModelMetadata(EncodedFileName(model_file), None)
        end = time.process_time()
        print('Time taken for loading model = %s seconds' %(end-start))
    data_tree = et.fromstring(model_meta_data)
    if 'updateodb' == data_tree.tag:
        #print upgrade_odb_message
        #return 
        print(upgrading_odb_message)
        start = time.process_time()
        engine.UpgradeOdb(EncodedFileName(model_file), EncodedFileName(upgrade_file))
        end = time.process_time()
        print('Time taken for upgrading odb = %s seconds' %(end-start))
        engine.DestroyDataManager()
        model_file = upgrade_file
        start = time.process_time()
        if sets_inp_file:
            model_meta_data = engine.GetModelMetadataWithExtSets(EncodedFileName(model_file), EncodedFileName(sets_inp_file), None)
        else:
            model_meta_data = engine.GetModelMetadata(EncodedFileName(model_file), None)
        end = time.process_time()
        print('Time taken for loading model = %s seconds' %(end-start))
        data_tree = et.fromstring(model_meta_data)
    
    if 'error' == data_tree.tag:
        msg = data_tree.get('message', 'Error!')
        print(msg)
        if msg == 'File access failure':
            return ErrNum.FILE_ACCESS_ERROR
        elif msg == 'Format not supported':
            return ErrNum.FORMAT_ERROR
        else:
            return ErrNum.UNKNOWN_ERROR
    elif 'metadata' == data_tree.tag:
        if 'true' == data_tree.get('appendable', 'false'):
            is_appendable = True
        else:
            is_appendable = False

    results_meta_data = None

    if results_file:
        if is_appendable:
            if len(results_file) > 1:
                engine.EnableResultsInstanceTitle()
            elif len(results_file) == 1 and enable_appending_instances:
                engine.EnableResultsInstanceTitle()

            for rfu in results_file:
                rf = rfu.encode('UTF-8')
                exfiles = Common.ExtractedFiles(rf, tmpdir.getPath(), 
                        engine.GetWildCards(engine.RESULTS_FILE),
                        enable_local_cache)
                rf = exfiles[1][0]
                start = time.process_time()
                results_meta_data = engine.GetResultsMetadata(rf)
                end = time.process_time()
                print('Time taken for loading results = %s seconds' %(end-start))
        else:
            print("Can't append results to the model.  ") 
            print("Ignoring the results from ", results_file)

    trans_string = GetTransString(model_meta_data, results_meta_data, option_list)

    if enable_rigid_rotation_from_virtual_node:
        engine.SetVirtualRotationNode(virtual_node_index_for_rigid_rotation)

    ignore_midnodes = True
    elem_res_trans = False
    en_to_e_avg = False
    if '--enable-mid-nodes' in option_list:
        ignore_midnodes = False
    if '--disable-mid-nodes' in option_list:
        ignore_midnodes = True
    if '--disable-skinning' in option_list:
        engine.DisableSkinning(True)
    if '--translate-element-results' in option_list:
        elem_res_trans = True
    if '--element-nodal-results-to-element-results' in option_list:
        en_to_e_avg = True
    if '--default-element-results' in option_list:
        elem_res_trans = True
        en_to_e_avg = True

    attributes_dict = {}
    attributes_dict['Model File'] = os.path.basename(model_file)
    attributes_dict['Model File Size'] = engine.GetLinkedFilesSize(model_file)

    if results_file:
        attributes_dict['Results File'] = os.path.basename(results_file[0])
        attributes_dict['Results File Size'] = engine.GetLinkedFilesSize(results_file[0])

    engine.PrintModelInfo()
    print('Translating ', repr(model_file))
    start = time.process_time()

    ofenc = output_file.encode(locale.getpreferredencoding())
    trans_res = engine.Translate(ofenc, trans_string, 
                        ignore_midnodes, elem_res_trans, 
                        en_to_e_avg, attributes_dict,
                        hist_json_file, modal_tables_file)
    end = time.process_time()

    if 'success' == trans_res:
            print('Translated Successfully.')
            print('Time taken for translation = %s seconds' %(end-start))
    else:
        print('Translation Failed.')

    engine.DestroyDataManager()
    return retval
    
#----------------------------------------------------------------------------
def IsValidResultComponentName(compname, contents):
    #if compname in ['X.N', 'THICKNESS.EL']: 
    if compname == 'X.N' and contents == 'Position': 
        return False

    if compname in ['DELETED.E']: 
        return False

    if compname.startswith('ROT_ANG.') and compname.endswith('.EL'):
        return False

    return True

#----------------------------------------------------------------------------

def GenerateLists(metadata_tree, trans_dict, rstatdict = None):
    #for parent in metadata_tree.getiterator():
    for parent in metadata_tree.iter():
        for child in parent:
            if "part" == child.tag:
                part_id = int(child.get('id', '-1'))
                part_name = child.get('name', '')
                #if appending is enabled
                #part_name = part_name + str(part_id)
                if '-1' == part_id:
                    raise Exception("\nERROR: Error in Part Data")
                if '' == part_name:
                    part_name = str(part_id)
                part_info = trans_dict['Parts']
                part_info_list = part_info[0]
                part_info_dict = part_info[1]
                part_info_list.append([part_id, part_name])
                part_info_dict[part_id] = True
            if "result" == child.tag:
                result_index = int(child.get('index', '-999999'))
                result_dsname = child.get('dsname', '')
                result_contents = child.get('contents', '')
                result_fullname = child.get('fullname', result_contents)
                result_displayname = child.get('displayname', result_contents)
                result_model = child.get('model', 0);
                result_datatype = child.get('datatype', 'Scalar')

                result_instance_info = result_dsname.split(':')
                result_compname = result_instance_info[0]

                if rstatdict is None or result_index not in rstatdict:
                    if rstatdict is not None:
                        rstatdict[result_index] = True
                    if IsValidResultComponentName(result_compname, result_contents):
                        result_info = trans_dict['Result Instances']
                        result_info_list = result_info[0]
                        result_info_dict = result_info[1]
                        #result_info_list.append([
                        #    result_index, result_dsname,
                        #    result_fullname, result_datatype,
                        #    result_contents])
                        result_info_list.append([
                            result_index, result_dsname,
                            result_fullname, result_datatype,
                            result_displayname, result_contents,
                            result_model, 0, -1, 0, 100, THRESH_MAX_NUM, []])
                        result_info_dict[result_fullname] = False

    return trans_dict

#----------------------------------------------------------------------------

def GenerateTransString(trans_dict):
    trans_string = ''

    part_info_list = trans_dict['Parts'][0]
    part_info_dict = trans_dict['Parts'][1]
    trans_string += 'Parts\n'
    for part_info in part_info_list:
        part_id = part_info[0]
        part_name = part_info[1]
        if part_info_dict[part_id]:
            trans_string += str(part_id) + '\t'
            trans_string += str(0) + '\t'
            trans_string += str(0) + '\t'
            trans_string += str(part_name) + '\n'

    trans_string += '\nFeature Edges\n'
    fedge_info_list = trans_dict['Feature Edges'][0]
    fedge_info_dict = trans_dict['Feature Edges'][1]
    for fedge_info in fedge_info_list:
        fedge_id = fedge_info[0]
        fedge_name = fedge_info[1]
        if fedge_info_dict[fedge_id]:
            trans_string += str(fedge_id) + '\t'
            trans_string += str(0) + '\t'
            trans_string += str(0) + '\t'
            trans_string += str(fedge_name) + '\n'

    trans_string += '\nCut-Sections\n'
    cutsec_info_list = trans_dict['Cut-Sections'][0]
    cutsec_info_dict = trans_dict['Cut-Sections'][1]
    for cutsec_info in cutsec_info_list:
        cutsec_id = cutsec_info[0]
        cutsec_name = cutsec_info[1]
        if cutsec_info_dict[cutsec_name]:
            trans_string += str(cutsec_id) + '\t'
            trans_string += str(0) + '\t'
            trans_string += str(0) + '\t'
            trans_string += str(cutsec_name) + '\n'

    trans_string += '\nIso-Surfaces\n'
    isosurf_info_list = trans_dict['Iso-Surfaces'][0]
    isosurf_info_dict = trans_dict['Iso-Surfaces'][1]
    for isosurf_info in isosurf_info_list:
        isosurf_id = isosurf_info[0]
        isosurf_eqn = isosurf_info[1]
        isosurf_label = isosurf_info[2]
        if isosurf_info_dict[isosurf_label]:
            trans_string += str(isosurf_id) + '\t'
            trans_string += str(0) + '\t'
            trans_string += str(1) + '\t'
            trans_string += str(isosurf_eqn) + '\t'
            trans_string += str(isosurf_label) + '\n'

    trans_string += '\nFlow Lines\n'
    flowline_info_list = trans_dict['Flow Lines'][0]
    flowline_info_dict = trans_dict['Flow Lines'][1]
    for flowline_info in flowline_info_list:
        flowline_id = flowline_info[0]
        flowline_name = flowline_info[1]
        if flowline_info_dict[flowline_name]:
            trans_string += str(flowline_id) + '\t'
            trans_string += str(0) + '\t'
            trans_string += str(0) + '\t'
            trans_string += str(flowline_name) + '\n'

    trans_string += '\nElement Groups\n'
    egroup_info_list = trans_dict['Element Groups'][0]
    egroup_info_dict = trans_dict['Element Groups'][1]
    for egroup_info in egroup_info_list:
        egroup_id = egroup_info[0]
        egroup_name = egroup_info[1]
        if egroup_info_dict[egroup_name]:
            trans_string += str(egroup_id) + '\t'
            trans_string += str(0) + '\t'
            trans_string += str(0) + '\t'
            trans_string += str(egroup_name) + '\n'


    rl_val = 3
    if 'Result Layers' in trans_dict:
        rl_val = trans_dict['Result Layers']
    trans_string += '\nResult Instances\n'
    result_info_list = trans_dict['Result Instances'][0]
    result_info_dict = trans_dict['Result Instances'][1]
    for result in result_info_list:
        result_index = result[0]
        result_dsname = result[1]
        result_fullname = result[2]
        result_datatype = result[3]
        lib_num = result[6]
        res_mask = result[7]
        dt_type = result[8]
        avg_type = result[9]
        thres_num = result[10]
        thres_type = result[11]
        str_res_mask = None
        if result_fullname.find(" (All Sections)") != -1:
            str_res_mask = str(rl_val | res_mask)
        #elif res_mask != 0:
        else:
            str_res_mask = str(res_mask)
        if result_info_dict[result_fullname]:
            trans_string += str(result_index) + '\t'
            trans_string += lib_num + '\t'
            trans_string += '5\t'
            trans_string += str_res_mask + '\t'
            trans_string += str(dt_type) + '\t'
            trans_string += str(avg_type) + '\t'
            trans_string += str(thres_num) + '\t'
            trans_string += str(thres_type) + '\t'
            trans_string += str(result_dsname) + '\n'

    return trans_string

#----------------------------------------------------------------------------

DerivedTypeSettings = { 'Scalar': [],
                    'Vector': ['X', 'Y', 'Z', 'Magnitude'],
                    'SixDof' : ['TX', 'TY', 'TZ',
                            'RX', 'RY', 'RZ', 'TMag', 'RMag'],
                    'Tensor': ['XX', 'YY', 'ZZ', 'XY', 'YZ', 'ZX',
                            'Mean', 
                            'Von Mises',
                            'Octahedral',
                            'Maximum Principal', 
                            'Middle Principal', 
                            'Minimum Principal', 
                            'Maximum Shear', 
                            'Equal Direct at Maximum Shear', 
                            'Intensity', 
                            'Determinant']}

DerivedTypeAliases = { 
            'Scalar': {},
            'Vector': {
                'x'                 : 'X',
                'translational x'   : 'X',
                'Y'                 : 'Y',
                'translational y'   : 'Y',
                'z'                 : 'Z',
                'translational z'   : 'Z',
                'magnitude'                 : 'Magnitude',
                'mag'                       : 'Magnitude',
                'tmag'                      : 'Magnitude',
                'resultant'                 : 'Magnitude',
                'translational magnitude'   : 'Magnitude',
            },
            'SixDof': {
                'x'                 : 'TX',
                'tx'                : 'TX',
                'translational x'   : 'TX',
                'y'                 : 'TY',
                'ty'                : 'TY',
                'translational y'   : 'TY',
                'z'                 : 'TZ',
                'tz'                : 'TZ',
                'translational z'   : 'TZ',
                'magnitude'                 : 'TMag',
                'mag'                       : 'TMag',
                'tmag'                      : 'TMag',
                'resultant'                 : 'TMag',
                'translational magnitude'   : 'TMag',

                'rx'                    : 'RX',
                'rotational x'          : 'RX',
                'ry'                    : 'RY',
                'rotational y'          : 'RY',
                'rz'                    : 'RZ',
                'rotational z'          : 'RZ',
                'rmag'                  : 'RMag',
                'rotational magnitude'  : 'RMag',
            },
            'Tensor': {
                'x'                 : 'XX',
                'xx'                : 'XX',
                'x component'       : 'XX',
                'y'                 : 'YY',
                'yy'                : 'YY',
                'y component'       : 'YY',
                'z'                 : 'ZZ',
                'zz'                : 'ZZ',
                'z component'       : 'ZZ',
                'xy'                : 'XY',
                'xy shear'          : 'XY',
                'yz'                : 'YZ',
                'yz shear'          : 'YZ',
                'xz'                : 'ZX',
                'xz shear'          : 'ZX',
                'zx'                : 'ZX',
                'zx shear'          : 'ZX',
                'mean'              : 'Mean',
                'von mises'         : 'Von Mises',
                'equivalent'        : 'Von Mises',
                'octahedral'        : 'Octahedral',
                'octahedral shear'  : 'Octahedral',
                'maximum principal' : 'Maximum Principal',
                '1st principal'     : 'Maximum Principal',
                'middle principal'  : 'Middle Principal',
                '2nd principal'     : 'Middle Principal',
                'minimum principal' : 'Minimum Principal',
                '3rd principal'     : 'Minimum Principal',
                'maximum shear'     : 'Maximum Shear',
                'equal direct at maximum shear' : 
                            'Equal Direct at Maximum Shear',
                'intensity'         : 'Intensity',
                'tensor intensity'  : 'Intensity',
                'determinant'       : 'Determinant',
                'tensor determinant': 'Determinant',
             },
        }
#----------------------------------------------------------------------------

def GetDerivedTypeNum(result_type, derived_type):
    dtypes = []
    aliases = {}
    if result_type in DerivedTypeSettings:
        dtypes = DerivedTypeSettings[result_type]
        aliases = DerivedTypeAliases[result_type]

    #if derived_type in dtypes:
    #    return dtypes.index(derived_type) + 1
    dtlower = derived_type.lower()
    if dtlower in aliases:
        return dtypes.index(aliases[dtlower]) + 1
    return 0

#----------------------------------------------------------------------------

def TurnOn(rlist, rdict, rname, anim_type, anim_skip):
    sel_rcomp = None
    sel_instance = None
    for result in rlist:
        if result[2] == rname:
            rdsname = result[1]
            iinfo = rdsname.split(':')
            sel_rcomp = iinfo[0]
            sel_instance = rdsname.replace(sel_rcomp, '')

    for result in rlist:
        rdsname = result[1]
        iinfo = rdsname.split(':')
        rcomp = iinfo[0]
        iname = rdsname.replace(rcomp, '')
        if rcomp == 'D.N' and iname == sel_instance:
            rdict[result[2]] = True

    if anim_type == 'Complex Eigenvector':
        re_name = rname.replace('[Real]', '[Imaginary]')
        im_name = rname.replace('[Imaginary]', '[Real]')
        rdict[re_name] = True
        rdict[im_name] = True

    if anim_type == 'Transient':
        sel_ilist = []
        for ilist in sel_instance.split(':'):
            if ilist:
                sel_ilist.append(int(ilist))

        denom = anim_skip + 1
        for result in rlist:
            rdsname = result[1]
            iinfo = rdsname.split(':')
            rcomp = iinfo[0]
            iname = rdsname.replace(rcomp, '')
            if rcomp == sel_rcomp or rcomp == 'D.N':
                tran_ilist = []
                for ilist in iname.split(':'):
                    if ilist:
                        tran_ilist.append(int(ilist))

                indices = range(min(len(sel_ilist), len(tran_ilist)))
                indices.reverse()
                for index in indices:
                    diff = tran_ilist[index] - sel_ilist[index]
                    if diff > 0 and diff % denom == 0:
                        rdict[result[2]] = True
        
#----------------------------------------------------------------------------
def AddXmlConfFeatures(trans_dict, trans_node):
    parts_list = trans_dict['Parts'][0]
    parts_dict = trans_dict['Parts'][1]

    fedge_list = trans_dict['Feature Edges'][0]
    fedge_dict = trans_dict['Feature Edges'][1]
    results_list = trans_dict['Result Instances'][0]
    results_dict = trans_dict['Result Instances'][1]
    cutsec_list = trans_dict['Cut-Sections'][0]
    cutsec_dict = trans_dict['Cut-Sections'][1]
    isosurf_list = trans_dict['Iso-Surfaces'][0]
    isosurf_dict = trans_dict['Iso-Surfaces'][1]
    flowline_list = trans_dict['Flow Lines'][0]
    flowline_dict = trans_dict['Flow Lines'][1]
    egroup_list = trans_dict['Element Groups'][0]
    egroup_dict = trans_dict['Element Groups'][1]

    for item in parts_list:
        fedge_list.append(item)
        fedge_dict[item[0]] = False

    for item_of_trans in trans_node.getchildren():
        if 'feature-edge' != item_of_trans.tag.lower():
            continue

        fe_node = item_of_trans
        fe_id = None
        fe_name = None
        fe_angle = None
        fe_status = True

        for item_of_fe in fe_node.getchildren():
            if 'attribute' != item_of_fe.tag.lower():
                continue

            attr_node = item_of_fe

            key = attr_node.get('key', '')
            val = attr_node.get('value', '')
            if 'id' == key.lower():
                fe_id = val
            if 'name' == key.lower():
                fe_name = val
            if 'angle' == key.lower():
                fe_angle = val
            if 'filter' == key.lower() and 'true' == val.lower():
                fe_status = False
            if 'translate' == key.lower() and 'false' == val.lower():
                fe_status = False

        if fe_id:
            fedge_dict[fe_id] = fe_status

        if fe_name:
            for fe_data in fedge_list:
                if fe_data[1] == fe_name:
                    fedge_dict[fe_data[0]] = fe_status

    for item_of_trans in trans_node.getchildren():
        if 'cut-section' != item_of_trans.tag.lower():
            continue

        cutsec_node = item_of_trans
        cutsec_eqn = None
        cutsec_status = True

        for item_of_cutsec in cutsec_node.getchildren():
            if 'attribute' != item_of_cutsec.tag.lower():
                continue

            attr_node = item_of_cutsec

            key = attr_node.get('key', '')
            val = attr_node.get('value', '')
            if 'plane equation' == key.lower():
                cutsec_eqn = val
            if 'filter' == key.lower() and 'true' == val.lower():
                cutsec_status = False
            if 'translate' == key.lower() and 'false' == val.lower():
                cutsec_status = False
        if cutsec_eqn:
            cutsec_list.append([-1, cutsec_eqn])
            cutsec_dict[cutsec_eqn] = cutsec_status

    for item_of_trans in trans_node.getchildren():
        if 'iso-surface' != item_of_trans.tag.lower():
            continue

        isosurf_node = item_of_trans
        isosurf_res = None
        isosurf_dt = None
        isosurf_val = None
        isosurf_status = True

        for item_of_isosurf in isosurf_node.getchildren():
            if 'attribute' != item_of_isosurf.tag.lower():
                continue

            attr_node = item_of_isosurf

            key = attr_node.get('key', '')
            val = attr_node.get('value', '')
            if 'result' == key.lower():
                isosurf_res = val
            if 'derived type' == key.lower():
                isosurf_dt = val
            if 'value' == key.lower():
                isosurf_val = val
            if 'filter' == key.lower() and 'true' == val.lower():
                isosurf_status = False
            if 'translate' == key.lower() and 'false' == val.lower():
                isosurf_status = False

        isosurf_eqn = None
        if isosurf_res and isosurf_val:
            for result_prop in results_list:
                if isosurf_res == result_prop[4]:
                    result_dsname = result_prop[1]
                    result_instance_info = result_dsname.split(':')
                    result_compname = result_instance_info[0]
                    isosurf_eqn = result_compname + '=' + isosurf_val
                    isosurf_label = isosurf_res + ' - ' + isosurf_dt + ' = ' + isosurf_val
                    isosurf_dtype_num = 0
                    if isosurf_dt:
                        isosurf_dtype_num = GetDerivedTypeNum(result_prop[3], isosurf_dt)
                    isosurf_num = -2 - isosurf_dtype_num
                    if isosurf_eqn not in isosurf_dict:
                        isosurf_list.append([isosurf_num, isosurf_eqn, isosurf_label])
                        isosurf_dict[isosurf_label] = isosurf_status
            break


    for item_of_trans in trans_node.getchildren():
        if 'field-line' != item_of_trans.tag.lower() and 'particle-trace' != item_of_trans.tag.lower():
            continue

        fline_node = item_of_trans
        fline_num = -1
        if 'particle-trace' == fline_node.tag.lower():
            fline_num = -2
        fline_from = None
        fline_numlines = 0
        fline_res= None
        fline_ts = 0.001
        fline_steps = 200
        fline_freq = 10
        fline_status = True

        for item_of_fline in fline_node.getchildren():
            if 'attribute' != item_of_fline.tag.lower():
                continue

            attr_node = item_of_fline

            key = attr_node.get('key', '')
            val = attr_node.get('value', '')
            if 'from' == key.lower():
                fline_from = val
            if 'number of lines' == key.lower():
                fline_numlines = int(val)
            if 'result' == key.lower():
                fline_res = val
            if 'time step' == key.lower():
                fline_ts = float(val)
            if 'number of steps' == key.lower():
                fline_steps = int(val)
            if 'injection frequency' == key.lower():
                fline_freq = int(val)
            if 'filter' == key.lower() and 'true' == val.lower():
                fline_status = False
            if 'translate' == key.lower() and 'false' == val.lower():
                fline_status = False

        if fline_from and fline_res:
            for result_prop in results_list:
                if fline_res == result_prop[4]:
                    result_dsname = result_prop[1]
                    result_instance_info = result_dsname.split(':')
                    result_compname = result_instance_info[0]
                    fline_eqn = 'From '
                    is_part = False
                    for part_prop in parts_list:
                        if part_prop[1] == fline_from:
                            fline_eqn += 'Part id %d' %(part_prop[0])
                            is_part = True
                    if not is_part:
                        fline_eqn += 'Point ' + fline_from
                    fline_eqn += ' number of lines %d' %(fline_numlines)
                    fline_eqn += ' for result ' + result_compname
                    if fline_num == -2:
                        fline_eqn += ' time step %f steps %d frequency %d' %(fline_ts, fline_steps, fline_freq)

                    if fline_eqn not in flowline_dict:
                        flowline_list.append([fline_num, fline_eqn])
                        flowline_dict[fline_eqn] = fline_status

    for item_of_trans in trans_node.getchildren():
        if 'element-group' != item_of_trans.tag.lower():
            continue

        egroup_node = item_of_trans
        egroup_result = None
        egroup_instance = None
        egroup_value = None
        egroup_status = True

        for item_of_egroup in egroup_node.getchildren():
            if 'attribute' != item_of_egroup.tag.lower():
                continue

            attr_node = item_of_egroup

            key = attr_node.get('key', '')
            val = attr_node.get('value', '')
            if 'result' == key.lower():
                egroup_result = val
            if 'instance' == key.lower():
                egroup_instance = val
            if 'value' == key.lower():
                egroup_value = val
            if 'filter' == key.lower() and 'true' == val.lower():
                egroup_status = False
            if 'translate' == key.lower() and 'false' == val.lower():
                egroup_status = False
        if egroup_result and egroup_instance and egroup_value:
            egroup_name = egroup_result
            egroup_instance = egroup_instance.replace(':', 'L', 1).replace(':', 'M', 1)
            egroup_name += ' ' + egroup_instance

            egroup_id = 0
            for result_prop in results_list:
                if egroup_name == result_prop[2]:
                    egroup_id = result_prop[0]

            if egroup_value == 'Any':
                egroup_name += ' Specified'
            if egroup_value == 'Not Specified':
                egroup_name += ' Not Specified'
                egroup_id = -egroup_id

            egroup_list.append([egroup_id, egroup_name])
            egroup_dict[egroup_name] = egroup_status

#----------------------------------------------------------------------------

def ProcessXmlConf(engine, root, option_list, model_cfile=None, results_cfile=None, output_cfile=None):
    for item_of_root in root.getchildren():
        if 'translation' != item_of_root.tag.lower():
            continue

        trans_node = item_of_root
        model_file = None
        results_file = None
        output_file = None
        for item_of_trans in trans_node.getchildren():
            if 'attribute' != item_of_trans.tag.lower():
                continue

            attr_node = item_of_trans
            key = attr_node.get('key', '')
            val = attr_node.get('value', '')
            if 'model file' == key.lower():
                model_file = val.encode('utf-8')
            if 'results file' == key.lower():
                results_file = val.encode('utf-8')
            if 'output file' == key.lower():
                output_file = val.encode('utf-8')

        if model_cfile:
            model_file = model_cfile
        if output_cfile:
            output_file = output_cfile
        if results_cfile:
            results_file = results_cfile

        print('Model File = ', repr(model_file))
        print('Results File = ',  repr(results_file))
        print('Output File = ', repr(output_file))

        if not model_file or not output_file:
            continue

        is_appendable = False
        start = time.process_time()
        meta_data = engine.GetModelMetadata(EncodedFileName(model_file), None)
        end = time.process_time()
        print('Time taken for loading model = %s seconds' %(end-start))
        data_tree = et.fromstring(meta_data)
        if 'error' == data_tree.tag:
            msg = data_tree.get('message', 'Error!')
            print(msg)
            if msg == 'File access failure':
                return ErrNum.FILE_ACCESS_ERROR
            elif msg == 'Format not supported':
                return ErrNum.FORMAT_ERROR
            else:
                return ErrNum.UNKNOWN_ERROR
        elif 'updateodb' == data_tree.tag:
            odb_version = engine.GetAbaqusOdbVersion()
            upgrade_file = model_file.replace('.odb', '_v'+odb_version+'.odb')
            upgrading_odb_message = '\nVMoveCAE %s supports Abaqus .odb files ' % (Version.VERSION)
            upgrading_odb_message += 'of version ' + odb_version + ' only.\n'
            upgrading_odb_message += 'Input file ', model_file 
            upgrading_odb_message += ' belongs to a older version.\n'
            print(upgrading_odb_message)
            engine.DestroyDataManager()
            start = time.process_time()
            engine.UpgradeOdb(EncodedFileName(model_file), EncodedFileName(upgrade_file))
            end = time.process_time()
            print('Time taken for upgrading odb = %s seconds' %(end-start))
            engine.DestroyDataManager()
            model_file = upgrade_file
            start = time.process_time()
            meta_data = engine.GetModelMetadata(EncodedFileName(model_file), None)
            end = time.process_time()
            print('Time taken for loading model = %s seconds' %(end-start))
            data_tree = et.fromstring(meta_data)
        elif 'metadata' == data_tree.tag:
            if 'true' == data_tree.get('appendable', 'false'):
                is_appendable = True
            else:
                is_appendable = False

        trans_dict = {'Parts': [[], {}], 
                  'Feature Edges': [[], {}],
                  'Cut-Sections': [[], {}],
                  'Iso-Surfaces': [[], {}],
                  'Flow Lines': [[], {}],
                  'Element Groups' : [[], {}],
                  'Result Instances': [[], {}] 
                  }
        GenerateLists(data_tree, trans_dict)

        #import pdb; pdb.set_trace()
        results_meta_data = None
        if results_file:
            if is_appendable:
                start = time.process_time()
                results_meta_data = engine.GetResultsMetadata(EncodedFileName(results_file))
                end = time.process_time()
                print('Time taken for loading results = %s seconds' %(end-start))
                results_data_tree = et.fromstring(results_meta_data)
                GenerateLists(results_data_tree, trans_dict)
            else:
                print("Can't append results to the model.  ") 
                print("Ignoring the results from " + results_file)

        parts_list = trans_dict['Parts'][0]
        parts_dict = trans_dict['Parts'][1]

        results_list = trans_dict['Result Instances'][0]
        results_dict = trans_dict['Result Instances'][1]

        # Turn on All Results By Default
        for result_id in results_dict.keys():
            results_dict[result_id] = True

        filter_parts = False
        filter_results = False

        for item_of_trans in trans_node.getchildren():
            if 'defaults' != item_of_trans.tag.lower():
                continue

            def_node = item_of_trans
            for item_of_defs in def_node.getchildren():
                if 'attribute' != item_of_defs.tag.lower():
                    continue

                attr_node = item_of_defs
                key = attr_node.get('key', '')
                val = attr_node.get('value', '')
                if 'parts' == key.lower():
                    if 'filter' == val.lower():
                        filter_parts = True
                    if 'translate' == val.lower():
                        filter_parts = False
                if 'results' == key.lower():
                    if 'filter' == val.lower():
                        filter_results = True
                    if 'translate' == val.lower():
                        filter_results = False

        if filter_parts:
            for part_id in parts_dict.keys():
                parts_dict[part_id] = False

        if filter_results:
            for result_id in results_dict.keys():
                results_dict[result_id] = False

        tpart_ids = []
        tparts = []
        fpart_ids = []
        fparts = []
        last_step = None
        last_frames = None
        for item_of_trans in trans_node.getchildren():
            if 'part' != item_of_trans.tag.lower():
                continue

            part_node = item_of_trans
            part_id = None
            part_name = None
            part_status = True

            for item_of_part in part_node.getchildren():
                if 'attribute' != item_of_part.tag.lower():
                    continue

                attr_node = item_of_part

                key = attr_node.get('key', '')
                val = attr_node.get('value', '')
                if 'id' == key.lower():
                    part_id = val
                if 'name' == key.lower():
                    part_name = val
                if 'filter' == key.lower() and 'true' == val.lower():
                    part_status = False
                if 'translate' == key.lower() and 'false' == val.lower():
                    part_status = False

            if part_id:
                if part_status:
                    tpart_ids.append(part_id)
                else:
                    fpart_ids.append(part_id)

            if part_name:
                if part_status:
                    tparts.append(part_name)
                else:
                    fparts.append(part_name)

        for part_id, part_name in parts_list:
            if IsInCheckedNames(part_name, tparts):
                tpart_ids.append(repr(part_id))
            if IsInCheckedNames(part_name, fparts):
                fpart_ids.append(repr(part_id))

        if tpart_ids:
            for part_id in parts_dict.keys():
                if IsInCheckedPartIds(part_id, tpart_ids):
                    parts_dict[part_id] = True

        if fpart_ids:
            for part_id in parts_dict.keys():
                if IsInCheckedPartIds(part_id, fpart_ids):
                    parts_dict[part_id] = False

        for item_of_trans in trans_node.getchildren():
            if 'result' != item_of_trans.tag.lower():
                continue

            res_node = item_of_trans
            res_name = None
            res_instances = None
            res_status = True

            for item_of_res in res_node.getchildren():
                if 'attribute' != item_of_res.tag.lower():
                    continue

                attr_node = item_of_res

                key = attr_node.get('key', '')
                val = attr_node.get('value', '')
                if 'name' == key.lower():
                    res_name = val
                if 'instances' == key.lower():
                    res_instances = val
                if 'filter' == key.lower() and 'true' == val.lower():
                    res_status = False
                if 'translate' == key.lower() and 'false' == val.lower():
                    res_status = False

            if res_name:
                for result_prop in results_list:
                    if IsInCheckedNames(result_prop[4], res_name.split(',')) or (res_name.lower() == 'temperature' and result_prop[1].startswith("TEMP.N")):
                        if res_instances: 
                            if IsInCheckedInstances(result_prop[1], res_instances.split(','), last_step, last_frames):
                                results_dict[result_prop[2]] = res_status
                        else:
                            results_dict[result_prop[2]] = res_status

        for item_of_trans in trans_node.getchildren():
            if 'instance' != item_of_trans.tag.lower():
                continue

            inst_node = item_of_trans
            inst_id = None
            inst_res = None
            inst_status = True

            for item_of_inst in inst_node.getchildren():
                if 'attribute' != item_of_inst.tag.lower():
                    continue

                attr_node = item_of_inst

                key = attr_node.get('key', '')
                val = attr_node.get('value', '')
                if 'id' == key.lower():
                    inst_id = val
                if 'results' == key.lower():
                    inst_res = val
                if 'filter' == key.lower() and 'true' == val.lower():
                    inst_status = False
                if 'translate' == key.lower() and 'false' == val.lower():
                    inst_status = False

            if inst_id:
                for result_prop in results_list:
                    if IsInCheckedInstances(result_prop[1], inst_id.split(','), last_step, last_frames):
                        if inst_res: 
                            if IsInCheckedNames(result_prop[4], [inst_res]):
                                results_dict[result_prop[2]] = inst_status
                        else:
                            results_dict[result_prop[2]] = inst_status

        AddXmlConfFeatures(trans_dict, trans_node)
        trans_string = GenerateTransString(trans_dict)

        ignore_midnodes = True
        elem_res_trans = False
        en_to_e_avg = False
        for item_of_trans in trans_node.getchildren():
            if 'preferences' != item_of_trans.tag.lower():
                continue

            pref_node = item_of_trans

            for item_of_pref in pref_node.getchildren():
                if 'attribute' != item_of_pref.tag.lower():
                    continue

                attr_node = item_of_pref

                key = attr_node.get('key', '')
                val = attr_node.get('value', '')
                if 'mid-nodes'.lower() == key.lower() and 'turn on' == val.lower():
                    ignore_midnodes = False
                if 'all-nodes'.lower() == key.lower() and 'turn on' == val.lower():
                    engine.DisableSkinning(True)

        if '--enable-mid-nodes' in option_list:
            ignore_midnodes = False
        if '--disable-mid-nodes' in option_list:
            ignore_midnodes = True
        if '--disable-skinning' in option_list:
            engine.DisableSkinning(True)
        if '--translate-element-results' in option_list:
            elem_res_trans = True
        if '--element-nodal-results-to-element-results' in option_list:
            en_to_e_avg = True
        if '--default-element-results' in option_list:
            elem_res_trans = True
            en_to_e_avg = True

        save_tfat_input = False
        if '--extract-tfat-data' in option_list:
            save_tfat_input = True

        attributes_dict = {}
        attributes_dict['Model File'] = os.path.basename(model_file)
        attributes_dict['Model File Size'] = engine.GetLinkedFilesSize(model_file)

        if results_file:
            attributes_dict['Results File'] = os.path.basename(results_file)
            attributes_dict['Results File Size'] = engine.GetLinkedFilesSize(results_file)

        engine.PrintModelInfo()
        print('Translating ', repr(model_file))

        ofenc = output_file.encode(locale.getpreferredencoding())
        start = time.process_time()
        if save_tfat_input:
            trans_res = engine.GenerateTfatInput(ofenc, trans_string, ignore_midnodes);
        else:
            trans_res = engine.Translate(ofenc, trans_string, 
                            ignore_midnodes, elem_res_trans, 
                            en_to_e_avg, attributes_dict, None, None)
        end = time.process_time()
        if 'success' == trans_res:
            print('Translated Successfully.')
            print('Time taken for translation = %s seconds' %(end-start))
        else:
            print('Translation Failed.')

        engine.DestroyDataManager()
#----------------------------------------------------------------------------

def ProcessTextConf(engine, conf_file, option_list, model_cfile=None, results_cfile=None, output_cfile=None):
    reader = InpFileReader()
    reader.ReadFile(conf_file)
    try:
        #print reader.GetXmlString()
        #return
        root = reader.GetXmlTree()
        return ProcessXmlConf(engine, root, option_list, model_cfile, results_cfile, output_cfile)
    except InpFileError as ex:
        return ProcessOldConf(engine, conf_file, option_list)

#----------------------------------------------------------------------------

def ProcessOldConf(engine, oldconf_file, option_list):
    reader = ConfigFileReader()
    vars = reader.ReadFile(oldconf_file)

    tr_num = 0
    model_file = None
    results_file = None
    output_file = None
    tran_prefix = None
    res_prefix = None
    while True:
        model_file = ''
        results_file = ''
        output_file = ''

        tran_prefix = '\035VMoveCAEInput\035Translation %d\035' % (tr_num)
        mf_name = tran_prefix + 'Model File'
        rf_name = tran_prefix + 'Results File'
        of_name = tran_prefix + 'Output File'

        if mf_name in vars:
            model_file = vars[mf_name]
        if rf_name in vars:
            results_file = vars[rf_name]
        if of_name in vars:
            output_file = vars[of_name]
            output_file = output_file.replace('.vcz', '.cax')

        if not model_file or not output_file:
            break;

        is_appendable = False
        start = time.process_time()
        meta_data = engine.GetModelMetadata(EncodedFileName(model_file), None)
        end = time.process_time()
        print('Time taken for loading model = %s seconds' %(end-start))
        data_tree = et.fromstring(meta_data)
        if 'error' == data_tree.tag:
            msg = data_tree.get('message', 'Error!')
            print(msg)
            if msg == 'File access failure':
                return ErrNum.FILE_ACCESS_ERROR
            elif msg == 'Format not supported':
                return ErrNum.FORMAT_ERROR
            else:
                return ErrNum.UNKNOWN_ERROR
        if 'updateodb' == data_tree.tag:
            print(upgrade_odb_message)
            return ErrNum.VERSION_ERROR
        elif 'metadata' == data_tree.tag:
            if 'true' == data_tree.get('appendable', 'false'):
                is_appendable = True
            else:
                is_appendable = False

        trans_dict = {'Parts': [[], {}], 
                      'Feature Edges': [[], {}],
                      'Cut-Sections': [[], {}],
                      'Iso-Surfaces': [[], {}],
                      'Flow Lines': [[], {}],
                      'Element Groups' : [[], {}],
                      'Result Instances': [[], {}]
                      }
        GenerateLists(data_tree, trans_dict)
        results_meta_data = None
        if results_file:
            if is_appendable:
                start = time.process_time()
                results_meta_data = engine.GetResultsMetadata(EncodedFileName(results_file))
                end = time.process_time()
                print('Time taken for loading results = %s seconds' %(end-start))
            else:
                print("Can't append results to the model.  ")
                print("Ignoring the results from " + results_file)

        parts_list = trans_dict['Parts'][0]
        parts_dict = trans_dict['Parts'][1]
        parts_off_label = tran_prefix + 'Parts\035Turn Off';
        if parts_off_label in vars:
            splitter = re.compile(r'[ ,\t]')
            parts_to_turn_off = splitter.split(vars[parts_off_label])
            for part in parts_to_turn_off:
                if part:
                    parts_dict[int(part)] = False
                    
        anim_prefix = tran_prefix + 'Animation\035' 
        anim_type_label = anim_prefix + 'Type'
        anim_frames_label = anim_prefix + 'Frames'
        anim_fringe_label = anim_prefix + 'Fringe'
        anim_skip_label = anim_prefix + 'Skip'

        anim_type = ''
        if anim_type_label in vars:
            anim_type = vars[anim_type_label]

        if not anim_type in ['0 to 1', '-1 to 1', 'Transient', 'Complex Eigenvector']:
            anim_type = ''

        anim_skip = 0
        if anim_type == 'Transient':
            if anim_skip_label in vars:
                anim_skip = int(vars[anim_skip_label])
        
        results_list = trans_dict['Result Instances'][0]
        results_dict = trans_dict['Result Instances'][1]
        res_num = 0

        while True:
            res_prefix = tran_prefix + 'Result %d\035' % (res_num) 
            res_label = res_prefix + 'Name'
            if res_label in vars:
                result_fullname = vars[res_label]
                if result_fullname in results_dict:
                    results_dict[result_fullname] = True
                    TurnOn(results_list, results_dict, result_fullname, anim_type, anim_skip)
            else:
                break
            
            res_num += 1

        parts_list = trans_dict['Parts'][0]
        parts_dict = trans_dict['Parts'][1]
        results_list = trans_dict['Result Instances'][0]
        results_dict = trans_dict['Result Instances'][1]

        feature_edges_label = tran_prefix + 'Feature Edges'
        if feature_edges_label in vars:
            feature_edges_onoff = vars[feature_edges_label]
            if feature_edges_onoff.lower() == 'on':
                for item in trans_dict['Parts'][0]:
                    trans_dict['Feature Edges'][0].append(item)
                    trans_dict['Feature Edges'][1][item[0]] = trans_dict['Parts'][1][item[0]]


        cutsec_num = 0
        cutsec_list = trans_dict['Cut-Sections'][0]
        cutsec_dict = trans_dict['Cut-Sections'][1]
        while True:
            cutsec_prefix = tran_prefix + 'Cut Section %d\035' % (cutsec_num) 
            cutsec_axis_label = cutsec_prefix + 'Axis'
            cutsec_value_label = cutsec_prefix + 'Value'
            if cutsec_axis_label in vars and cutsec_value_label in vars:
                cutsec_axis = vars[cutsec_axis_label]
                cutsec_value = vars[cutsec_value_label]
                cutsec_eqn = cutsec_axis + '=' + cutsec_value
                cutsec_list.append([-1, cutsec_eqn])
                cutsec_dict[cutsec_eqn] = True
            else:
                break
            
            cutsec_num += 1

        isosurf_num = 0
        isosurf_list = trans_dict['Iso-Surfaces'][0]
        isosurf_dict = trans_dict['Iso-Surfaces'][1]
        while True:
            isosurf_prefix = tran_prefix + 'Iso Surface %d\035' % (isosurf_num) 
            isosurf_res_label = isosurf_prefix + 'Result'
            isosurf_dtype_label = isosurf_prefix + 'Derived Type'
            isosurf_value_label = isosurf_prefix + 'Value'
            if isosurf_res_label in vars and isosurf_value_label in vars:
                isosurf_res = vars[isosurf_res_label]
                isosurf_value = vars[isosurf_value_label]
                isosurf_dtype = ''
                if isosurf_dtype_label in vars:
                    isosurf_dtype = vars[isosurf_dtype_label]
                
                result_fullname = isosurf_res
                for result in results_list:
                    if result_fullname == result[2]:
                        result_dsname = result[1]
                        result_instance_info = result_dsname.split(':')
                        result_compname = result_instance_info[0]
                        isosurf_eqn = result_compname + '=' + isosurf_value
                        isosurf_dtype_num = 0
                        if isosurf_dtype:
                            isosurf_dtype_num = GetDerivedTypeNum(result[3], isosurf_dtype)
                        isosurf_dtype_num = -2 - isosurf_dtype_num
                        isosurf_label = isosurf_eqn
                        isosurf_list.append([isosurf_dtype_num, isosurf_eqn, isosurf_label])
                        isosurf_dict[isosurf_label] = True
            else:
                break
            
            isosurf_num += 1

        flowline_num = 0
        flowline_list = trans_dict['Flow Lines'][0]
        flowline_dict = trans_dict['Flow Lines'][1]
        while True:
            flowline_prefix = tran_prefix + 'Flow Line %d\035' % (flowline_num) 
            flowline_res_label = flowline_prefix + 'Result'
            flowline_type_label = flowline_prefix + 'Type'
            flowline_stpt_label = flowline_prefix + 'Starting Point'
            flowline_pid_label = flowline_prefix + 'Part Id'
            flowline_pname_label = flowline_prefix + 'Part Name'
            flowline_nsteps_label = flowline_prefix + 'Steps'
            flowline_scale_label = flowline_prefix + 'Scale Factor'
            flowline_tstep_label = flowline_prefix + 'Time Step'
            flowline_freq_label = flowline_prefix + 'Injection Frequency'

            if not flowline_res_label in vars:
                break;

            flowline_res_fullname = vars[flowline_res_label]
            flowline_res_compname = ''
            for result in results_list:
                if flowline_res_fullname == result[2]:
                    result_dsname = result[1]
                    result_instance_info = result_dsname.split(':')
                    flowline_res_compname = result_instance_info[0]

            if not flowline_res_compname:
                break;

            flowline_from = ''
            if flowline_stpt_label in vars:
                flowline_from = 'From Point ' + vars[flowline_stpt_label]
            elif flowline_pid_label in vars:
                flowline_from = 'From Part id ' + vars[flowline_pid_label]
            elif flowline_pname_label in vars:
                flowline_part_name = vars[flowline_pname_label]
                for part_info in parts_list:
                    if part_info[1] == flowline_part_name:
                        flowline_from = 'From Part id ' + str(part_info[0])
            else:
                break
            
            if not flowline_from:
                break

            flowline_type = 'Streamline'
            if flowline_type_label in vars:
                if vars[flowline_type_label].lower() == 'pathline':
                    flowline_type = 'Pathline'

            if flowline_type == 'Streamline':
                flowline_eqn = flowline_from + ' for result ' + flowline_res_compname
                flowline_list.append([-2, flowline_eqn])
                flowline_dict[flowline_eqn] = True

            if flowline_type == 'Pathline':
                flowline_tstep = 1e-3
                if flowline_tstep_label in vars:
                    flowline_tstep = float(vars[flowline_tstep_label])

                flowline_nsteps = 50
                if flowline_nsteps_label in vars:
                    flowline_nsteps = int(vars[flowline_nsteps_label])

                flowline_scale = 1
                if flowline_scale_label in vars:
                    flowline_scale = int(vars[flowline_scale_label])

                flowline_freq = 10
                if flowline_freq_label in vars:
                    flowline_freq = int(vars[flowline_freq_label])

                flowline_eqn = flowline_from + ' for result ' + flowline_res_compname + ' time step ' + str(flowline_tstep) + ' steps ' + str(flowline_nsteps) + ' frequency ' + str(flowline_freq)

                flowline_list.append([-2, flowline_eqn])
                flowline_dict[flowline_eqn] = True
            
            flowline_num += 1

        trans_string = GenerateTransString(trans_dict)

        ignore_midnodes = True
        elem_res_trans = False
        en_to_e_avg = False
        if '--enable-mid-nodes' in option_list:
            ignore_midnodes = False
        if '--disable-mid-nodes' in option_list:
            ignore_midnodes = True
        if '--disable-skinning' in option_list:
            engine.DisableSkinning(True)
        if '--translate-element-results' in option_list:
            elem_res_trans = True
        if '--element-nodal-results-to-element-results' in option_list:
            en_to_e_avg = True
        if '--default-element-results' in option_list:
            elem_res_trans = True
            en_to_e_avg = True


        attributes_dict = {}
        attributes_dict['Model File'] = os.path.basename(model_file)
        attributes_dict['Model File Size'] = engine.GetLinkedFilesSize(model_file)

        if results_file:
            attributes_dict['Results File'] = os.path.basename(results_file)
            attributes_dict['Results File Size'] = engine.GetLinkedFilesSize(results_file)

        engine.PrintModelInfo()
        print('Translating ', repr(model_file))
        start = time.process_time()
        ofenc = output_file.encode(locale.getpreferredencoding())
        trans_res = engine.Translate(ofenc, trans_string, 
                            ignore_midnodes, elem_res_trans, 
                            en_to_e_avg, attributes_dict, None, None)
        end = time.process_time()
        if 'success' == trans_res:
            print('Translated Successfully.')
            print('Time taken for translation = %s seconds' %(end-start))
        else:
            print('Translation Failed.')

        engine.DestroyDataManager()
        tr_num += 1
    
#----------------------------------------------------------------------------

def main(argv):
    option_list = []
    for option in argv:
        if option.startswith('--'):
            option_list.append(option)

    file_list = []
    for option in argv:
        if not option.startswith('--'):
            file_list.append(option)

    if len(file_list) < 3:
        print('\nUsage: VMoveCAEBatch' + ' <input_cae_file> <output_cax_file>')
        return 4

    option_dict = {}
    for option in option_list:
        option = option.lstrip('-')
        key_pair = option.split('=')
        if len(key_pair) > 1:
            option_dict[key_pair[0]] = key_pair[1]
        else:
            option_dict[key_pair[0]] = ''

    #if "--debug" in option_list:
    #    import pdb
    #    pdb.set_trace()

    os.environ["ABQ_CRTMALLOC"]="1"
    engine = CaeEngine.getEngine()
    tmpdir = Common.TempFolder()
    tmpdir.create()

    if 'clear-log-cache' not in option_dict:
        option_dict['clear-log-cache'] = 'on'

    if option_dict['clear-log-cache'].lower() == 'on':
        try:
            tmpdir.clearOld(5)
        except Exception:
            pass
    engine.SetTempFileFolder(tmpdir.getPath())
    tr_file = os.path.join(tmpdir.getPath(), 'vmovecae_trace.log')
    pi_file = os.path.join(tmpdir.getPath(), 'progress_file.log')
    if 'log-file-path' in option_dict:
        tr_file = option_dict['log-file-path']
    engine.SetLogFile(tr_file)
    #engine.SetPIFile(pi_file)
    #engine.retainFiles([tr_file, ou_file, er_file])
    tmpdir.retainFiles([tr_file])

    #license_status = engine.AcquireLicense()
    #if license_status:
    #    VMoveCAEBatch(engine, tmpdir, option_list, file_list)
    #engine.ReleaseLicense()
    retval = VMoveCAEBatch(engine, tmpdir, option_list, file_list)
    tmpdir.destroy()
    return retval

#----------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main(sys.argv))
    # argg = [ "VMoveCAEBatch.exe",r"D:\odb-test-data\1-1-SimpleBeam_v2020_v2022_v2023.odb", r"D:\odb-test-data\1-1-SimpleBeam_v2020_v2022_v2023.cax"]
    # "--filter-results", “Von Mises Stress”
    # argg = [ "VMoveCAEBatch.exe","--filter-results=", "Von Mises Stress", r"D:\odb-test-data\1-1-SimpleBeam_v2020_v2022_v2023.odb", r"D:\odb-test-data\1-1-SimpleBeam_v2020_v2022_v2023.cax"]
    # argg = [ "VMoveCAEBatch.exe","--","filter-results","=", "Stress", r"D:\odb-test-data\1-1-SimpleBeam_v2020_v2022_v2023.odb", r"D:\odb-test-data\1-1-SimpleBeam_v2020_v2022_v2023.cax"]

    # sys.exit(main(argg))
