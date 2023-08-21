#!/usr/bin/env python
# Copyright (C) 2018 Visual Collaboration Technologies Inc.
# All Rights Reserved.
#
# This file is a property of Visual Collaboration Technologies Inc.
# Unauthorized access, reproduction or redistribution of any kind is prohibited.

import sys
import os
import re
import logging
import itertools
import string
from distutils.util import strtobool
from constants import Const
import InterfaceInfo


class Pattern(Const):
    SECTION_PREFIX = r'^\*\s*'
    DATA_PREFIX = r'^-\s*'
    CONTINUATION_PREFIX = r'^,\s*'
    COMMENT_PREFIX = r'^#\s*'
    ASCII_CHAR = r'[ -~]'

    FILE_EXPR_CHAR = r'[\w\s+\-\*\.\/\\:]'
    WORD = '("[^"]+"|{}+)'.format(FILE_EXPR_CHAR)
    NAME = WORD
    KEY = WORD
    VALUE = WORD
    KEY_SEP = r'\s*,\s*'

    #ATTRIBUTE = '{0}={1}|{0}'.format(KEY, VALUE)
    ATTRIBUTE = '{}(?:={})?'.format(KEY, VALUE)
    NAME_ATTRIBUTE = ATTRIBUTE
    SUB_ATTRIBUTES = '{}{}'.format(KEY_SEP, ATTRIBUTE)
    PROPERTY = '{}(?:{})*'.format(NAME_ATTRIBUTE, SUB_ATTRIBUTES)

    SECTION = '{}{}$'.format(SECTION_PREFIX, PROPERTY)
    DATA = '{}{}$'.format(DATA_PREFIX, PROPERTY)
    CONTINUATION = SUB_ATTRIBUTES
    COMMENT = '{}.*$'.format(COMMENT_PREFIX)

RegEx = type(
    'RegEx', (), {
        p: re.compile(getattr(Pattern, p))
         for p in [
            'SECTION_PREFIX', 'DATA_PREFIX',
            'CONTINUATION_PREFIX', 'COMMENT_PREFIX',
            'NAME', 'KEY', 'VALUE', 'ATTRIBUTE',
            'NAME_ATTRIBUTE', 'SUB_ATTRIBUTES', 'PROPERTY',
            'SECTION', 'DATA',
            'CONTINUATION', 'COMMENT',
        ]
    })

def create_options_type(name, members):
    return type(name, (), dict({
        k: k
        for k in members
        }, members=members))

Section = create_options_type('Section', [
            'FILES', 'PARTS', 'RESULTS', 'STEPS'
        ])


Option = create_options_type('Option', [
            'TYPE', 'CONTENT', 'FOLDER', 'MERGE_TYPE',
            'RETAIN_INTERMEDIATE',
            'OPTIONS', 'UNSPECIFIED', 'DEFAULT',
            'GROUPING',
            'TRANSLATE', 'FILTER',
            'SOURCE', 'POSITION', 'DERIVED', 'MAPTYPE',
            'THRESHOLD', 'BTR_TYPE', 'COORDSYS', 'SECTION',
            'STEP', 'INCREMENT',
        ])


FileType = create_options_type('FileType', [
            'ABAQUS_ODB', 'ABAQUS_INP',
            'ANSYS_RST', 
            'FEMFAT_DMA',
            'VCOLLAB_CAX', 'VMOVE_LOG',
        ])


FileContent = create_options_type('FileContent', [
            'MODEL', 'RESULTS', 'ENTITY_SETS', 'PART_NAMES',
            'CAX', 'LOG',
        ])


LoadOption = create_options_type('LoadOption', [
            'FAST_LOAD', 'ZERO_FRAMES', 'MID_NODES',
            'NO_AVERAGING_ACROSS_REGIONS',
            'ENHANCED_MARC_FEATURES', 'MARC_NO_RIGID_SURFACES',
        ])


ResultSource = create_options_type('ResultSource', [
            'U', 'S', 'E', 'PE', 'PEEQ', 'LE', 'THE',
            'NT', 'NT11', 'NT12', 'AC_YIELD', 'VEEQ',
            'CPRES', 'CNORMF', 'CSHEAR1', 'CSHEAR2', 'CSHEARF',
            'COPEN', 'CSLIP1', 'CSLIP2',
        ])


PositionType = create_options_type('PositionType', ['N', 'E'])


BtrType = create_options_type('BtrType', [
            'max', 'min',
        ])


MergeType = create_options_type('MergeType', [ 
            'STEPS', 'INSTANCES',
        ])


RESULT_SECTION_NAME_MAP = {
        'TOP': 'Top',
        'BOTTOM': 'Bottom',
        'MAX': 'Maximum',
        'MIN': 'Minimum',
        'AVG': 'Average',
}


DTYPE_NAME_MAP = {
    'VON_MISES': 'Von Mises',
    'MAX_PRINCIPAL': 'Maximum Principal',
    'MID_PRINCIPAL': 'Middle Principal',
    'MIN_PRINCIPAL': 'Minimum Principal',
    'XX': 'XX',
    'YY': 'YY',
    'ZZ': 'ZZ',
    'XY': 'XY',
    'YZ': 'YZ',
    'ZX': 'ZX',
    'XZ': 'ZX',
    'X': 'X',
    'Y': 'Y',
    'Z': 'Z',
    'MAGNITUDE': 'Magnitude',
    'RESULTANT': 'Magnitude',
}


MAPTYPE_SUFFIX_MAP = {
    'MAX': ' [max]',
    'MIN': ' [min]',
    'AVG': ' [avg]',
    'GEOAVG': ' [geoavg]',
}


COORDSYS_SUFFIX_MAP = {
    'LOCAL': ' ##NOROT##',
}

LOAD_OPTION_ARG_MAP = {
    LoadOption.FAST_LOAD: '--enable-odb-fast-load',
    LoadOption.ZERO_FRAMES: '--enable-odb-load-zero-frames',
    LoadOption.MID_NODES: '--enable-mid-nodes',
    LoadOption.NO_AVERAGING_ACROSS_REGIONS: '--no-averaging-across-materials',
    LoadOption.ENHANCED_MARC_FEATURES: '--enable-marc-experimental-features',
}

INVERSE_OPTION_DICT = {
    LoadOption.MARC_NO_RIGID_SURFACES: LoadOption.ENHANCED_MARC_FEATURES,
}


STRIP_CHARS = string.whitespace + '"'
def stripped(v):
    return v.strip(STRIP_CHARS) if v else v

class Property:
    NAME_KEY = '_NAME_'

    def __init__(self, name=None, value=None):
        self.name_val = stripped(name)
        self.name_key = stripped(name.upper())

        self.attributes = {
                Property.NAME_KEY: self.name_val,
                self.name_key: stripped(value),
        }
        self.children = []

    def read_attributes(self, attrs_str):
        while True:
            m = RegEx.SUB_ATTRIBUTES.match(attrs_str)
            if not m:
                break
            key = m.group(1).upper()
            value = m.group(2)
            self.attributes[stripped(key)] = stripped(value)
            attrs_str = RegEx.SUB_ATTRIBUTES.sub('', attrs_str, 1)

    @staticmethod
    def generate_from(line):
        m = RegEx.NAME_ATTRIBUTE.match(line)
        name = m.group(1)
        value = m.group(2)
        attrs_str = RegEx.NAME_ATTRIBUTE.sub('', line, 1)
        prop = Property(name, value)
        prop.read_attributes(attrs_str)
        return prop

SECTION_SEP = '#'*78

class Param:
    def __init__(self, logger_name=__name__):
        self._initialize()
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)

    def _initialize(self):
        self.props = {}
        self.active_section = None
        self.errors_in_reading = False
        self.abaqus_inp_as_esets_file = None

    def clear(self):
        self._initialize()

    def _read_from(self, input_file_path):
        last_prop = None
        with open(input_file_path, 'r') as fh:
            line_num = 0
            for line in fh.readlines():
                line_num += 1
                line.strip()
                last_prop = self._process_param_line(line, line_num, last_prop)

    def read_from(self, input_file_path):
        self.logger.debug(SECTION_SEP)
        self.logger.debug('Reading file "{}" ...'.format(input_file_path))
        self.logger.debug(SECTION_SEP)
        try:
            self._read_from(input_file_path)
        except IOError:
            self.logger.error('Unable to read from "{}"'.format(input_file_path))
        self.logger.debug(SECTION_SEP)
        self.logger.debug('Reading file "{}" ... done'.format(input_file_path))
        self.logger.debug(SECTION_SEP)

    def _process_section(self, line):
        prop = Property.generate_from(line)
        self.logger.debug('{:<8}{}, {}'.format(
                    ' ', prop.name_key, prop.attributes))
        if prop.name_key in self.props:
            raise RuntimeError(
                    'Multiple entries for section "{}" exist.'.format(name))
        self.active_section = prop.name_key
        self.props[self.active_section] = prop
        #self.props[self.active_section] = prop.attributes
        return prop

    def _process_data(self, line):
        prop = Property.generate_from(line)
        self.logger.debug('{:<8}{}, {}'.format(' ', prop.name_key, prop.attributes))
        self.props[self.active_section].children.append(prop)
        #self.props[self.active_section + "." + prop.name_key] = prop.attributes
        return prop

    def _process_continuation(self, line, prop):
        prop.read_attributes(line)
        self.logger.debug('{:<8}{}, {}'.format(' ', prop.name_key, prop.attributes))
        return prop


    def _process_param_line(self, line, line_num, last_prop):
        if not line:
            return
        line = line.strip()

        msg0 = '{:5}:'.format(line_num)
        if RegEx.SECTION_PREFIX.match(line):
            if RegEx.SECTION.match(line):
                self.logger.debug('{} Processing section line'.format(msg0))
                last_prop = self._process_section(RegEx.SECTION_PREFIX.sub('', line))
            else:
                self.logger.error('{} Invalid section line format'.format(msg0))
                self.errors_in_reading = True
        elif RegEx.DATA_PREFIX.match(line):
            if RegEx.DATA.match(line):
                self.logger.debug('{} Processing data line'.format(msg0))
                last_prop = self._process_data(RegEx.DATA_PREFIX.sub('', line))
            else:
                self.logger.error('{} Invalid data line format'.format(msg0))
                self.errors_in_reading = True
        elif RegEx.CONTINUATION_PREFIX.match(line):
            if RegEx.CONTINUATION.match(line):
                self.logger.debug('{} Processing continuation line'.format(msg0))
                last_prop = self._process_continuation(line, last_prop)
            else:
                self.logger.error('{} Invalid continuation line format'.format(msg0))
                self.errors_in_reading = True
        elif RegEx.COMMENT_PREFIX.match(line):
            self.logger.debug('{} Ignoring comment line'.format(msg0))
        else:
            self.logger.info('{} Unknown line type. Ignoring'.format(msg0))
        return last_prop

    def validate_type_file_path(self, fname, base_folder, ftype):
        fp = fname
        if base_folder is not None and not os.path.isabs(fname):
            fp = os.path.join(base_folder, fname)

        self.logger.info('{} file path = {}'.format(ftype, fp))

        if not os.path.exists(fp):
            self.logger.warning("File doesn't exist. Please ensure that file exists before running the job.")
            return False
        return True

    def validate_file_options(self, options):
        if options is None:
            return
        if len(options) == 0:
            return
        option_list = options.strip('"').split(', ')
        for opt in option_list:
            if (opt not in LOAD_OPTION_ARG_MAP.keys()) and (opt not in INVERSE_OPTION_DICT.keys()):
                self.logger.warning("Unknown file option - {}.".format(opt))

    def identify_file_type(self, file_name):
        fpl = file_name.lower()
        if fpl.endswith('.odb'):
            return FileType.ABAQUS_ODB
        elif fpl.endswith('.inp'):
            return FileType.ABAQUS_INP
        elif fpl.endswith('.dma'):
            return FileType.FEMFAT_DMA
        elif fpl.endswith('.univ'):
            return FileType.FEMFAT_DMA
        elif fpl.endswith('.cax'):
            return FileType.VCOLLAB_CAX
        elif fpl.endswith('.log'):
            return FileType.VMOVE_LOG
        else:
            return None

    def identify_file_content(self, file_type):
        return {
                FileType.ABAQUS_ODB: ', '.join([
                    FileContent.MODEL,
                    FileContent.RESULTS]),
                FileType.ABAQUS_INP: FileContent.ENTITY_SETS if self.abaqus_inp_as_esets_file else FileContent.MODEL,
                FileType.FEMFAT_DMA: FileContent.RESULTS,
                FileType.VCOLLAB_CAX: FileContent.CAX,
                FileType.VMOVE_LOG: FileContent.LOG,
        }.get(file_type, None)


    def validate_files(self, warn_is_error=False):
        retval = True
        if Section.FILES not in self.props:
            self.logger.error('FILES section ... Not Found.')
            retval = False
            return retval

        self.logger.info('FILES section ... Found.')
        merge_type = self.props[Section.FILES].attributes.get(Option.MERGE_TYPE, None)
        if merge_type is not None:
            merge_type = merge_type.upper()
        content_file, base_folder = self.generate_file_content_list()

        files = self.props[Section.FILES].children
        for idx, child in enumerate(files):
            file_name = child.name_val
            file_name_upper = child.name_key
            file_type = child.attributes.get(Option.TYPE, None)
            if file_type is None:
                file_type = self.identify_file_type(file_name_upper)
                if file_type is None:
                    self.logger.error('Unable to identify type of file "{}"'.format(file_name))
                    continue
                else:
                    self.logger.info('Type of file "{}" is identified as {}'.format(file_name, file_type))
            else:
                file_type = file_type.upper()

            file_content = child.attributes.get(Option.CONTENT, None)
            if file_content is None:
                file_content = self.identify_file_content(file_type)
                if file_content is None:
                    self.logger.error('Unable to identify content of file "{}"'.format(file_name))
                    continue
                else:
                    self.logger.info('Content of file "{}" is identified as {}'.format(file_name, file_content))
            else:
                file_content = file_content.upper()

            file_content = file_content.strip('"').split(', ')
            for ct in file_content:
                if ct not in FileContent.members:
                    self.logger.error('Invalid file content type "{}" for file "{}"'.format(ct, file_name))

            if (file_type != FileType.VCOLLAB_CAX and
                    file_type != FileType.VMOVE_LOG):
                rv = self.validate_type_file_path(file_name, base_folder, file_type)
                if not rv:
                    if warn_is_error:
                        retval = rv

            file_options = child.attributes.get(Option.OPTIONS, None)
            self.validate_file_options(file_options)

        nmodels = len(content_file[FileContent.MODEL])
        if nmodels == 0:
            self.logger.error('Model file not specified.')
            retval = False
        if nmodels > 1:
            if merge_type is None:
                self.logger.error('Multiple model files specified, '
                                  'but merge type is not specified.')
                retval = False
            elif (merge_type == MergeType.STEPS or merge_type == MergeType.INSTANCES):
                self.logger.info('Multiple model files specified.')
                self.logger.info('Merge type is specified as STEPS.')
                self.logger.info('Please ensure that the input models have '
                    'same mesh, properties, element and face sets.')

        if merge_type not in [None, MergeType.STEPS, MergeType.INSTANCES]:
            self.logger.error('Invalid value {} for {} attribute'.format(
                    merge_type, Option.MERGE_TYPE))
            retval = False

        if Option.RETAIN_INTERMEDIATE in self.props[Section.FILES].attributes:
            retain_str = self.props[Section.FILES].attributes.get(
                    Option.RETAIN_INTERMEDIATE, None)
            if retain_str is not None:
                try:
                    ret_flag = strtobool(retain_str)
                except ValueError as err:
                    self.logger.error(
                        'Invalid value {} for {} attribute'.format(
                            retain_str, Option.RETAIN_INTERMEDIATE))
                    retval = False

        return retval

    def valid_default_action(self, attr):
        retval = True
        default_action = attr.get(Option.UNSPECIFIED, None)
        if default_action is None:
            default_action = attr.get(Option.DEFAULT, None)
        if default_action is not None:
            default_action = default_action.upper()
            if (default_action != Option.TRANSLATE and
                    default_action != Option.FILTER):
                self.logger.error('Unknown default action "{}"'.format(default_action))
                retval = False
        return default_action, retval

    def validate_parts(self):
        retval = True
        iinfo = InterfaceInfo.InterfaceInfo()
        if Section.PARTS in self.props:
            self.logger.info('PARTS section ... Found.')
            attr = self.props[Section.PARTS].attributes
            if Option.GROUPING in attr:
                pgtype = attr[Option.GROUPING].lower()
                if pgtype in iinfo.enabled_grouping_types:
                    self.logger.info('Part Grouping set to "{}"'.format(pgtype))
                else:
                    self.logger.error('Unknown part grouping type "{}"'.format(pgtype))
                    retval = False
            children = self.props[Section.PARTS].children

            parts_to_filter = []
            parts_to_trans = []
            for pdata in children:
                if Option.FILTER in pdata.attributes:
                    parts_to_filter.append(pdata.name_key.strip('"'))
                elif Option.TRANSLATE in pdata.attributes:
                    parts_to_trans.append(pdata.name_key.strip('"'))
                else:
                    parts_to_trans.append(pdata.name_key.strip('"'))
            if len(parts_to_filter) != 0:
                self.logger.info('Parts to filter: ')
                for p in parts_to_filter:
                    self.logger.info('    "{}"'.format(p))
            if len(parts_to_trans) != 0:
                self.logger.info('Parts to translate: ')
                for p in parts_to_trans:
                    self.logger.info('    "{}"'.format(p))
            if len(parts_to_filter) != 0 and len(parts_to_trans) != 0:
                self.logger.warning('Parts found for both filtering as well as translation.')
                self.logger.warning('Parts for filtering will be ignored.')

        else:
            self.logger.debug('PARTS section ... Not Found.')

        return retval

    def identify_result_name(self, res_source):
        return {
                ResultSource.U: 'Displacement',
                ResultSource.S: 'Stress',
                ResultSource.E: 'Strain',
                ResultSource.PE: 'Plastic Strain',
                ResultSource.PEEQ: 'Equivalent Plastic Strain',
                ResultSource.LE: 'Logarithic Strain',
                ResultSource.THE: 'Thermal Strain',
                ResultSource.NT: 'Temperature',
                ResultSource.NT11: 'Temperature',
                ResultSource.NT12: 'NT12 Temperature',
                ResultSource.AC_YIELD: 'AC YIELD',
                ResultSource.VEEQ: 'VEEQ',
                ResultSource.CPRES: 'Contact Pressure',
                ResultSource.CNORMF: 'Contact, Normal Force',
                ResultSource.CSHEAR1: 'Contact, X Component Traction',
                ResultSource.CSHEAR2: 'Contact, Y Component Traction',
                ResultSource.CSHEARF: 'Contact, Shear Force',
                ResultSource.COPEN: 'Contact, Normal Gap',
                ResultSource.CSLIP1: 'Contact, X Component Gap',
                ResultSource.CSLIP2: 'Contact, Y Component Gap',
        }.get(res_source, res_source)

    def get_file_list(self):
        files = self.props[Section.FILES].children
        for idx, child in enumerate(files):
            file_name = child.name_val
            file_name_upper = child.name_key
            file_type = child.attributes.get(Option.TYPE, None)
            if file_type is None:
                file_type = self.identify_file_type(file_name_upper)

    def validate_result_attributes(self, dtype, rpos, maptype,
            coordsys, threshold, btr_type, sec_type):
        retval = True
        if dtype is not None:
            dt_name = DTYPE_NAME_MAP.get(dtype, None)
            if dt_name is None:
                self.logger.error('Unknown derived type "{}"'.format(dtype))
                retval = False

        if rpos is not None and rpos not in PositionType.__dict__.keys():
            self.logger.error('Unknown result position "{}"'.format(rpos))
            retval = False

        if maptype is not None:
            map_type_name = MAPTYPE_SUFFIX_MAP.get(maptype, None)
            if map_type_name is None:
                self.logger.error('Unknown mapping type "{}"'.format(maptype))
                retval = False

        if coordsys is not None and coordsys not in COORDSYS_SUFFIX_MAP.keys():
            self.logger.error('Unknown coordinate system type "{}"'.format(coordsys))
            retval = False

        if threshold is not None:
            try:
                threshold_int = int(threshold)
                if threshold_int > 100 or threshold_int <= 0:
                    self.logger.error('Invalid averaging threshold value: {}'.format(threshold))
                    retval = False

            except ValueError as err:
                self.logger.error('Invalid averaging threshold value: {}'.format(threshold))
                retval = False

        if btr_type is not None and btr_type not in BtrType.__dict__.keys():
            self.logger.error('Invalid beyond threshold result type: {}'.format(btr_type))
            retval = False

        if sec_type is not None:
            slist = sec_type.strip('"').split(', ')
            for sv in slist:
                if sv.startswith('_') or sv not in RESULT_SECTION_NAME_MAP.keys():
                    self.logger.error('Unknown section type "{}"'.format(sv))
                    retval = False

        return retval

    def validate_results(self):
        retval = True
        if Section.RESULTS in self.props:
            self.logger.info('RESULTS section ... Found.')
            attr = self.props[Section.RESULTS].attributes
            default_action, dastat = self.valid_default_action(attr)
            if dastat is False:
                retval = False
            children = self.props[Section.RESULTS].children

            results_to_filter = []
            results_to_trans = []
            for res in children:
                rname = res.name_key
                rsource = res.attributes.get(Option.SOURCE, None)
                if rsource is not None:
                    res_source = rsource.upper()
                    res_name = rname
                else:
                    res_source = rname
                    res_name = self.identify_result_name(res_source)
                    if res_name is None:
                        self.logger.warning('Unable to identify result "{}" source'.format(res_source))
                    else:
                        self.logger.info('Result "{}" name is identified as "{}"'.format(res_source, res_name))

                dtype = res.attributes.get(Option.DERIVED, None)
                if dtype is not None:
                    dtype = dtype.upper()
                rpos = res.attributes.get(Option.POSITION, None)
                if rpos is not None:
                    rpos = rpos.upper()
                maptype = res.attributes.get(Option.MAPTYPE, None)
                if maptype is not None:
                    maptype = maptype.upper()
                coordsys = res.attributes.get(Option.COORDSYS, None)
                if coordsys is not None:
                    coordsys = coordsys.upper()
                threshold = res.attributes.get(Option.THRESHOLD, None)
                btr_type = res.attributes.get(Option.BTR_TYPE, None)
                if btr_type is not None:
                    btr_type = btr_type.lower()
                sec_type = res.attributes.get(Option.SECTION, None)
                if sec_type is not None:
                    sec_type = sec_type.upper()

                rv = self.validate_result_attributes(dtype, rpos, maptype,
                        coordsys, threshold, btr_type, sec_type)
                if rv is False:
                    retval = rv

                if Option.FILTER in res.attributes:
                    results_to_filter.append((res.name_key.strip('"'), res_source, res_name))
                elif Option.TRANSLATE in res.attributes:
                    results_to_trans.append((res.name_key.strip('"'), res_source, res_name))
                elif default_action == Option.FILTER:
                    results_to_filter.append((res.name_key.strip('"'), res_source, res_name))
                else:
                    results_to_trans.append((res.name_key.strip('"'), res_source, res_name))

            if len(results_to_filter) != 0:
                self.logger.info('Results to filter: ')
                for r in results_to_filter:
                    self.logger.info('    {} - "{}"'.format(r[1], r[2]))
            if len(results_to_trans) != 0:
                self.logger.info('Results to translate: ')
                for r in results_to_trans:
                    self.logger.info('    {} - "{}"'.format(r[1], r[2]))
            if len(results_to_filter) != 0 and len(results_to_trans) != 0:
                self.logger.warning('Results found for both filtering as well as translation.')
                self.logger.warning('Results for filtering will be ignored.')
        else:
            self.logger.debug('RESULTS section ... Not Found.')

        return retval

    def validate_step_range(self, sval):
        if sval.lower() == 'all':
            return True
        sval = sval.split(':')
        if len(sval) > 3:
            self.logger.error('Invalid range {}'.format(sval))
            return False
        for numstr in sval:
            try:
                num = int(numstr)
                if num < 0 and num != -1:
                    self.logger.error('Negative step/increment value {} is not supported'.format(num))
                    return False
                else:
                    return True
            except ValueError as err:
                self.logger.error('Invalid step/increment: {}'.format(numstr))
                return False
        return True

    def validate_steps(self):
        retval = True
        if Section.STEPS in self.props:
            self.logger.info('STEPS section ... Found.')
            attr = self.props[Section.STEPS].attributes
            children = self.props[Section.STEPS].children

            steps_to_filter = []
            steps_to_trans = []
            for stp in children:
                sname = stp.name_key
                sstep = stp.attributes.get(Option.STEP, None)
                sincr = stp.attributes.get(Option.INCREMENT, None)
                if sstep is None and sname is not None:
                    sstep = sname.strip('"')

                if not sstep:
                    self.logger.error('Unable to identify step number')

                rv = self.validate_step_range(sstep)
                if rv is False:
                    retval = rv
                if sincr is not None:
                    rv = self.validate_step_range(sincr)
                    if rv is False:
                        retval = rv
                else:
                    sincr = 'ALL'

                if Option.FILTER in stp.attributes:
                    steps_to_filter.append((sstep, sincr))
                elif Option.TRANSLATE in stp.attributes:
                    steps_to_trans.append((sstep, sincr))
                else:
                    steps_to_trans.append((sstep, sincr))
            if len(steps_to_filter) != 0:
                self.logger.info('Steps to filter: ')
                for s in steps_to_filter:
                    self.logger.info(' Step: {}, Increment: {}'.format(
                                        s[0], s[1]))
            if len(steps_to_trans) != 0:
                self.logger.info('Steps to translate: ')
                for s in steps_to_trans:
                    self.logger.info(' Step: {}, Increment: {}'.format(
                                        s[0], s[1]))
            if len(steps_to_filter) != 0 and len(steps_to_trans) != 0:
                self.logger.warning('Steps found for both filtering as well as translation.')
                self.logger.warning('Steps for filtering will be ignored.')
        else:
            self.logger.debug('STEPS section ... Not Found.')

        return retval

    def validate(self, warn_is_error=False):
        self.logger.debug(SECTION_SEP)
        self.logger.debug('Validating Input Parameters ... ')
        self.logger.debug(SECTION_SEP)

        if self.errors_in_reading:
            self.logger.error('Errors encountered while reading parameters file')
            return False

        retval = True
        rv = self.validate_files(warn_is_error)
        if not rv:
            retval = rv
        rv = self.validate_parts()
        if not rv:
            retval = rv
        rv = self.validate_results()
        if not rv:
            retval = rv
        rv = self.validate_steps()
        if not rv:
            retval = rv

        self.logger.debug(SECTION_SEP)
        self.logger.debug('Validating Input Parameters ... done')
        self.logger.debug(SECTION_SEP)

        if retval:
            self.logger.info('Validation successful.')
        else:
            self.logger.error('Validation failed.')
        return retval

    def set_settings(self):
        if self.abaqus_inp_as_esets_file is not None:
            return

        merge_type = self.props[Section.FILES].attributes.get(Option.MERGE_TYPE, None)
        if merge_type is not None:
            return

        files = self.props[Section.FILES].children
        ftlist = []
        for idx, child in enumerate(files):
            file_name = child.name_val
            file_name_upper = child.name_key
            file_type = child.attributes.get(Option.TYPE, None)
            if file_type is None:
                file_type = self.identify_file_type(file_name_upper)
            else:
                file_type = file_type.upper()
            ftlist.append(file_type)

        if FileType.ABAQUS_ODB in ftlist:
            self.abaqus_inp_as_esets_file = True
        else:
            self.abaqus_inp_as_esets_file = False

    def generate_file_content_list(self):
        base_folder = self.props[Section.FILES].attributes.get(Option.FOLDER, None)
        if base_folder:
            base_folder = base_folder.strip('"')

        self.set_settings()
        merge_type = self.props[Section.FILES].attributes.get(Option.MERGE_TYPE, None)
        if merge_type is not None:
            merge_type = merge_type.upper()

        content_file = {
                FileContent.MODEL: [],
                FileContent.ENTITY_SETS: [],
                FileContent.RESULTS: [],
                FileContent.CAX: [],
                FileContent.LOG: [],
        }
        files = self.props[Section.FILES].children
        for idx, child in enumerate(files):
            file_name = child.name_val
            file_name_upper = child.name_key
            file_type = child.attributes.get(Option.TYPE, None)
            file_content = child.attributes.get(Option.CONTENT, None)
            if file_type is None:
                file_type = self.identify_file_type(file_name_upper)
            else:
                file_type = file_type.upper()

            if file_content is None:
                file_content = self.identify_file_content(file_type)
            else:
                file_content = file_content.upper()

            file_content = file_content.strip('"').split(', ')
            for ct in file_content:
                if ct == 'MODEL':
                    content_file[FileContent.MODEL].append((file_name, idx))
                elif ct == 'ENTITY_SETS':
                    content_file[FileContent.ENTITY_SETS].append((file_name, idx))
                elif ct == 'RESULTS':
                    content_file[FileContent.RESULTS].append((file_name, idx))
                elif ct == 'CAX':
                    content_file[FileContent.CAX].append((file_name, idx))
                elif ct == 'LOG':
                    content_file[FileContent.LOG].append((file_name, idx))
                else:
                    self.logger.error('Invalid file content type for file "{}"'.format(file_name))

        return content_file, base_folder


    def extract_files(self):
        content_file, base_folder = self.generate_file_content_list()
        model_file, model_file_idx = content_file[FileContent.MODEL][0]

        cax_file = None
        if len(content_file[FileContent.CAX]) != 0:
            cax_file, cax_file_idx = content_file[FileContent.CAX][0]
        else:
            pre, ext = os.path.splitext(model_file)
            cax_file = pre + '.cax'

        res_file = []
        for idx, (rfile, rfile_idx) in enumerate(content_file[FileContent.RESULTS]):
            if rfile_idx == model_file_idx:
                continue
            if base_folder is not None and not os.path.isabs(rfile):
                res_file.append(os.path.join(base_folder, rfile))
            else:
                res_file.append(rfile)

        if base_folder is not None:
            if not os.path.isabs(model_file):
                model_file = os.path.join(base_folder, model_file)
            if not os.path.isabs(cax_file):
                cax_file = os.path.join(base_folder, cax_file)

        if len(content_file[FileContent.MODEL]) > 1:
            num_files = len(self.props[Section.FILES].children)
            model_file_ranges = [mfile[1] for mfile in content_file[FileContent.MODEL]]
            model_file_ranges.append(num_files)
            file_model_index_dict = {ridx: idx
                    for idx in range(len(model_file_ranges)-1)
                    for ridx in range(model_file_ranges[idx], model_file_ranges[idx+1])}
            file_lists = [[mfile[0]] for mfile in content_file[FileContent.MODEL]]
            for idx, (rfile, rfile_idx) in enumerate(content_file[FileContent.RESULTS]):
                model_idx = file_model_index_dict[rfile_idx]
                if rfile_idx == model_file_ranges[model_idx]:
                    continue
                file_lists[model_idx].append(rfile)
            cax_list = []
            for idx in range(len(content_file[FileContent.MODEL])):
                file_lists[idx].append(cax_file + str(idx))
                cax_list.append(cax_file + str(idx))
            return (file_lists, cax_file, cax_list)
        else:
            file_list = []
            file_list.append(model_file)
            file_list.extend(res_file)
            file_list.append(cax_file)
            return file_list

    def get_result_argname(self, res_name, rpos, maptype,
                coordsys, dtype, threshold, btr_type):
        res_name = res_name.strip('"')
        if rpos == PositionType.E:
            res_name = 'Element {}'.format(res_name)
        else:
            if rpos is not None and rpos != PositionType.N:
                self.logger.error('Ignoring unknown position type "{}"'.format(
                                rpos))

        map_suf = MAPTYPE_SUFFIX_MAP.get(maptype, '')

        opt_suf = ''
        opt_suf += COORDSYS_SUFFIX_MAP.get(coordsys, '')

        if dtype is None:
            return '{}{}{}'.format(res_name, map_suf, opt_suf)

        dt_name = DTYPE_NAME_MAP.get(dtype, None)
        if dt_name is None:
            self.logger.error('Ignoring unknown derived type "{}"'.format(
                                dtype))
            return '{}{}{}'.format(res_name, map_suf, opt_suf)

        if threshold is not None:
            if btr_type is not None:
                dt_name += '%{}{}'.format(threshold, btr_type)
            else:
                dt_name += '%{}{}'.format(threshold, BtrType.max)

        return res_name + ' - {}{}{}'.format(dt_name, map_suf, opt_suf)

    def extract_step_range(self, sval):
        if sval is None or sval.lower() == 'all':
            return ['']
        svec = []

        sval = sval.split(':')
        sval = [v if v != '-1' else '_' for v in sval]
        if len(sval) == 1:
            return sval
        elif len(sval) == 2:
            return [(sval[0], sval[1])]
        elif len(sval) == 3:
            ival = map(int, sval)
            return map(str, range(*[ival[0], ival[1]+1, ival[2]]))

    def create_step_arg(self, sstep, sincr):
        sstrlist = []
        for sv in itertools.product(sstep, sincr):
            sstr = ''
            if isinstance(sv[0], tuple):
                if isinstance(sv[1], tuple):
                    sstr = '{}:{}-{}:{}'.format(
                            sv[0][0], sv[1][0], sv[0][1], sv[1][1])
                else:
                    sstr = '{}:{}-{}:{}'.format(
                            sv[0][0], sv[1], sv[0][1], sv[1])
            else:
                if isinstance(sv[1], tuple):
                    sstr = '{}:{}-{}:{}'.format(
                            sv[0], sv[1][0], sv[0], sv[1][1])
                else:
                    sstr = '{}:{}'.format(sv[0], sv[1])
            sstrlist.append(sstr)
        return sstrlist

    def update_section_list(self, sec_type, sec_dict):
        if sec_type is None:
            return
        if len(sec_type) == 0:
            return
        slist = sec_type.strip('"').split(', ')
        for opt in slist:
            if opt in RESULT_SECTION_NAME_MAP.keys() and not opt.startswith('_'):
                sec_dict[RESULT_SECTION_NAME_MAP[opt]] = True

    def add_sections_argument(self, sec_list, option_list):
        if not sec_list:
            return

        option_list.append('--sections={}'.format(','.join(sec_list)))

    def extract_options(self):
        option_list = []

        content_file, base_folder = self.generate_file_content_list()
        cax_file = None
        if len(content_file[FileContent.CAX]) != 0:
            cax_file, cax_file_idx = content_file[FileContent.CAX][0]
            cax_file_attrs = self.props[Section.FILES].children[cax_file_idx].attributes
            cax_file_options = cax_file_attrs.get(Option.OPTIONS, None)
            if cax_file_options is not None:
                cax_file_options = cax_file_options.upper()
                foptlst = cax_file_options.strip('"').split(', ')
                for opt in foptlst:
                    for choice in [LoadOption.MID_NODES,
                            LoadOption.NO_AVERAGING_ACROSS_REGIONS]:
                        if opt == choice:
                            option_list.append(LOAD_OPTION_ARG_MAP[choice])

        model_file, model_file_idx = content_file[FileContent.MODEL][0]
        model_file_attrs = self.props[Section.FILES].children[model_file_idx].attributes
        model_file_options = model_file_attrs.get(Option.OPTIONS, None)
        if model_file_options is not None:
            model_file_options = model_file_options.upper()
            foptlst = model_file_options.strip('"').split(', ')
            for opt in foptlst:
                for choice in LOAD_OPTION_ARG_MAP.keys():
                    if opt == choice:
                        option_list.append(LOAD_OPTION_ARG_MAP[choice])
            for k, v in INVERSE_OPTION_DICT.items():
                if ((v not in foptlst) and (k not in foptlst)):
                    option_list.append(LOAD_OPTION_ARG_MAP[v])
        else:
            for v in INVERSE_OPTION_DICT.values():
                option_list.append(LOAD_OPTION_ARG_MAP[v])

        esets_file = None
        if len(content_file[FileContent.ENTITY_SETS]) != 0:
            esets_file, esets_file_idx = content_file[FileContent.ENTITY_SETS][0]
            if base_folder is not None:
                if not os.path.isabs(esets_file):
                    esets_file = os.path.join(base_folder, esets_file)
        if esets_file is not None:
            option_list.append('--abaqus-input-file={}'.format(esets_file))

        default_part_translation = None
        default_result_translation = None
        default_step_translation = None

        if Section.PARTS in self.props:
            attr = self.props[Section.PARTS].attributes
            if Option.GROUPING in attr:
                pgtype = attr[Option.GROUPING].lower()
                option_list.append('--part-grouping={}'.format(pgtype))
            plist = self.props[Section.PARTS].children

            parts_to_filter = []
            parts_to_trans = []
            for pdata in plist:
                pname = pdata.name_key
                if Option.FILTER in pdata.attributes:
                    parts_to_filter.append(pname.strip('"'))
                elif Option.TRANSLATE in pdata.attributes:
                    parts_to_trans.append(pname.strip('"'))
                else:
                    parts_to_trans.append(pname.strip('"'))
            if len(parts_to_filter) != 0:
                option_list.append('--filter-parts={}'.format(','.join(parts_to_filter)))
            if len(parts_to_trans) != 0:
                option_list.append('--parts={}'.format(','.join(parts_to_trans)))

        sec_dict = {v:False for k, v in RESULT_SECTION_NAME_MAP.items()}

        if Section.RESULTS in self.props:
            attr = self.props[Section.RESULTS].attributes
            default_action = attr.get(Option.UNSPECIFIED, None)
            if default_action is None:
                default_action = attr.get(Option.DEFAULT, None)
            if default_action is not None:
                default_action = default_action.upper()
                default_result_translation = False if default_action == Option.FILTER else True
            rlist = self.props[Section.RESULTS].children

            results_to_filter = []
            results_to_trans = []
            for res in rlist:
                rname = res.name_key
                rsource = res.attributes.get(Option.SOURCE, None)
                if rsource is not None:
                    res_source = rsource.upper()
                    res_name = rname
                else:
                    res_source = rname
                    res_name = self.identify_result_name(res_source)
                dtype = res.attributes.get(Option.DERIVED, None)
                if dtype is not None:
                    dtype = dtype.upper()
                rpos = res.attributes.get(Option.POSITION, None)
                if rpos is not None:
                    rpos = rpos.upper()
                maptype = res.attributes.get(Option.MAPTYPE, None)
                if maptype is not None:
                    maptype = maptype.upper()
                coordsys = res.attributes.get(Option.COORDSYS, None)
                if coordsys is not None:
                    coordsys = coordsys.upper()
                threshold = res.attributes.get(Option.THRESHOLD, None)
                btr_type = res.attributes.get(Option.BTR_TYPE, None)
                if btr_type is not None:
                    btr_type = btr_type.lower()
                sec_type = res.attributes.get(Option.SECTION, None)
                if sec_type is not None:
                    sec_type = sec_type.upper()
                self.update_section_list(sec_type, sec_dict)

                dt_name = self.get_result_argname(res_name, rpos, maptype,
                        coordsys, dtype, threshold, btr_type)
                if Option.FILTER in res.attributes:
                    results_to_filter.append(dt_name)
                elif Option.TRANSLATE in res.attributes:
                    results_to_trans.append(dt_name)
                else:
                    results_to_trans.append(dt_name)
            if len(results_to_filter) != 0:
                option_list.append('--filter-results={}'.format(','.join(results_to_filter)))
            if len(results_to_trans) != 0:
                option_list.append('--results={}'.format(','.join(results_to_trans)))

        sec_list = [k for k, v in sec_dict.items() if v]
        if sec_list:
            self.add_sections_argument(sec_list, option_list)

        if Section.STEPS in self.props:
            attr = self.props[Section.STEPS].attributes
            slist = self.props[Section.STEPS].children

            steps_to_filter = []
            steps_to_trans = []
            for stp in slist:
                sname = stp.name_key
                sstep = stp.attributes.get(Option.STEP, None)
                sincr = stp.attributes.get(Option.INCREMENT, None)
                if sstep is None and sname is not None:
                    sstep = sname.strip('"')

                if not sstep:
                    self.logger.error('Unable to identify step number')

                sstep = self.extract_step_range(sstep)
                sincr = self.extract_step_range(sincr)
                sarg = ','.join(self.create_step_arg(sstep, sincr))

                if Option.FILTER in stp.attributes:
                    steps_to_filter.append(sarg)
                elif Option.TRANSLATE in stp.attributes:
                    steps_to_trans.append(sarg)
                else:
                    steps_to_trans.append(sarg)
            if len(steps_to_filter) != 0:
                option_list.append('--filter-instances={}'.format(','.join(steps_to_filter)))
            if len(steps_to_trans) != 0:
                option_list.append('--instances={}'.format(','.join(steps_to_trans)))

        if default_result_translation is not None:
            self.logger.info('Translation for unspecified results is set to "{}"'.format(default_result_translation))
            option_list.append('--default-result-translation={}'.format(default_result_translation))
        if content_file[FileContent.LOG]:
            log_file, log_file_idx = content_file[FileContent.LOG][0]
            option_list.append('--log-file-path={}'.format(log_file))
        return option_list

    def extract_retain_intermediate(self):
        has_option = Option.RETAIN_INTERMEDIATE in self.props[Section.FILES].attributes
        if not has_option:
            return False

        flag = self.props[Section.FILES].attributes.get(
                    Option.RETAIN_INTERMEDIATE, None)
        if flag is None:
            self.logger.info('Result intermediate files is set to true')
            return True
        else:
            flag = strtobool(flag)
            if flag:
                self.logger.info('Result intermediate files is set to true')
            return flag
