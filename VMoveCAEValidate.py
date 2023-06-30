#!/usr/bin/python

import sys
import logging
import vt100
from ColorLogFormatter import ColorFormatter
from VMoveParam import Param

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

def main(argv):
    option_dict = {}
    for option in argv:
        if option.startswith('-'):
            kv = option.split('=')
            if len(kv) > 1:
                option_dict[kv[0]] = kv[1]
            else:
                option_dict[kv[0]] = None

    file_list = []
    for option in argv:
        if not option.startswith('-'):
            file_list.append(option)

    #LOGGER_NAME = __name__
    LOGGER_NAME = 'VMoveCAEValidate'
    logger, lh = create_logger(LOGGER_NAME)

    if len(file_list) < 1:
        print '\nUsage: VMoveValidate' + ' <input_file>'
        return 4

    fp = file_list[1]

    param = Param(LOGGER_NAME)
    if '-verbose-parse' in option_dict:
        lh.setLevel(logging.DEBUG)
    else:
        lh.setLevel(logging.WARNING)
    param.read_from(fp)

    if '-verbose-validate' in option_dict:
        lh.setLevel(logging.DEBUG)
    else:
        lh.setLevel(logging.INFO)
    if '-file-list' in option_dict:
        status = param.get_file_list()
    else:
        status = param.validate(warn_is_error=False)

#----------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main(sys.argv))

