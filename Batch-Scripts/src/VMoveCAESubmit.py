#!/usr/bin/python

from __future__ import print_function
import sys
import os
import logging
import vt100
import ErrNum
from ColorLogFormatter import ColorFormatter
from VMoveParam import Param
import CaeEngine
import Common
import VMoveCAEBatch as vmbatch
CPP_LIB = __import__(Common.GetCaeEngineName())

#----------------------------------------------------------------------------

def create_logger(name):
    vt100.enable_vt100_support()
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    lh = logging.StreamHandler()
    lh.setLevel(logging.DEBUG)
    lh.setFormatter(ColorFormatter())
    logger.addHandler(lh)

    return logger, lh

#----------------------------------------------------------------------------

def args_from_params(params):
    option_list = []
    file_list = []
    return option_list, file_list

#----------------------------------------------------------------------------

def run_vmovecaebatch(file_list, option_list):
    os.environ["ABQ_CRTMALLOC"]="1"
    engine = CaeEngine.getEngine()
    tmpdir = Common.TempFolder()
    tmpdir.create()

    try:
        tmpdir.clearOld(5)
    except Exception:
        pass

    option_dict = {}
    for option in option_list:
        option = option.lstrip('-')
        key_pair = option.split('=')
        if len(key_pair) > 1:
            option_dict[key_pair[0]] = key_pair[1]
        else:
            option_dict[key_pair[0]] = ''

    engine.SetTempFileFolder(tmpdir.getPath())
    tr_file = os.path.join(tmpdir.getPath(), 'vmovecae_trace.log')
    pi_file = os.path.join(tmpdir.getPath(), 'progress_file.log')
    if 'log-file-path' in option_dict:
        tr_file = option_dict['log-file-path']

    engine.SetLogFile(tr_file)
    #engine.SetPIFile(pi_file)
    #engine.retainFiles([tr_file, ou_file, er_file])
    tmpdir.retainFiles([tr_file])

    retval = vmbatch.VMoveCAEBatch(engine, tmpdir, option_list, file_list)
    tmpdir.destroy()
    return retval


#----------------------------------------------------------------------------

def main(argv):
    if len(argv) < 2:
        print('\nUsage: VMoveSubmit' + ' <input_file>')
        return ErrNum.INVALID_ARGUMENTS

    fp = argv[1]
    opt = []
    if len(argv) > 2:
        opt.extend(argv[2:])

    #LOGGER_NAME = __name__
    LOGGER_NAME = 'VMoveCAESubmit'
    logger, lh = create_logger(LOGGER_NAME)

    param = Param(LOGGER_NAME)
    logger.setLevel(logging.WARNING)
    param.read_from(fp)

    logger.setLevel(logging.INFO)
    status = param.validate(warn_is_error=True)
    if not status:
        print('Error: Exiting application ...', file=sys.stderr)
        return ErrNum.INVALID_ARGUMENTS


    file_list = param.extract_files()
    option_list = param.extract_options()
    retain_intermediate = param.extract_retain_intermediate()
    merge_case = False
    if isinstance(file_list, tuple):
        merge_case = True

    if merge_case:
        file_args_list = [[argv[0]] + fl for fl in file_list[0]]
    else:
        file_args_list = [argv[0]] + file_list

    if '--print-args' in opt:
        print(file_args_list, option_list)

    if '--dont-run' in opt:
        return 0
    else:
        if merge_case:
            for fl in file_args_list:
                if '--print-args' in opt:
                    print(fl, option_list)
                rv  = run_vmovecaebatch(fl, option_list)
                if rv:
                    return rv
            ignore_duplicate_results = False
            add_file_suffix_to_instance_name = True
            auto_rename_instance = True
            engine = CaeEngine.getEngine()
            if '--print-args' in opt:
                print(file_list[2], file_list[1],
                    ignore_duplicate_results,
                    add_file_suffix_to_instance_name,
                    auto_rename_instance)
            rv = CPP_LIB.merge_as_instances(file_list[2], file_list[1],
                    ignore_duplicate_results,
                    add_file_suffix_to_instance_name,
                    auto_rename_instance)
            if rv:
                return rv
            if not retain_intermediate:
                logger.info('Deleting intermediate CAX files ...')
                for f in file_list[2]:
                    fabs = os.path.abspath(f)
                    if os.path.isfile(fabs):
                        os.remove(fabs)
            return True
        else:
            return run_vmovecaebatch(file_args_list, option_list)
#----------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main(sys.argv))

