#!/usr/bin/python

import sys
from os import path
import os
import locale
import Common
import InfoEngine
import ErrNum
from FileDep import file_dependencies

#----------------------------------------------------------------------------

def EncodedFileName(fp):
    file_path = Utf8String(os.path.abspath(fp))
    fn, ext = os.path.splitext(file_path)
    if(ext.lower() == '.odb'):
        return file_path.encode('UTF-8')
    else:
        return file_path.encode(locale.getpreferredencoding())
#----------------------------------------------------------------------------

def Utf8String(file_path):
        return file_path.decode(locale.getpreferredencoding())
        
#----------------------------------------------------------------------------

def print_minerva_filedeps(ofp, dep_files, error_msg):
    if not ofp:
        ofp = 'minerva-dependency.xml'
    with open(ofp, 'w') as of:
        of.writelines([
            '<?xml version="1.0" encoding="utf-8"?>\n',
            '<ansysMinerva:dependencies\n',
            '    xmlns:ansysMinerva="https://www.ansys.com/minerva/dependency">\n',
        ])
        for file in dep_files:
            of.writelines([
                '  <dependency>\n',
                '    <relativePath> {} </relativePath>\n'.format(file),
                '  </dependency>\n',
            ])
        if error_msg is not None:
            of.writelines([
                '  <error>\n'
                '    {}\n'.format(error_msg),
                '  </error>\n',
            ])
        of.write('</ansysMinerva:dependencies>\n')


#----------------------------------------------------------------------------

def export_minerva_filedeps(input_file_path, output_file_path,
                            file_type = None):
    dep_files = []
    retval = 0
    error_msg = None
    try:
        dep_files = file_dependencies(input_file_path, file_type)
    except IOError as ex:
        error_msg = 'File I/O error'
        retval = ErrNum.FILE_ACCESS_ERROR
    except KeyError as ex:
        error_msg = 'Unknown file type'
        retval = ErrNum.FORMAT_ERROR
    except Exception as ex:
        error_msg = str(ex)
        retval = 1
    print_minerva_filedeps(output_file_path, dep_files, error_msg)
    return retval

#----------------------------------------------------------------------------
def invoke_caeinfo(options, args):
    if len(args) < 2:
        print('\nUsage: CaeInfo' + ' [options] <model_file> [results_file]')
        return

    os.environ["ABQ_CRTMALLOC"]="1"

    tmpdir = Common.TempFolder()
    tmpdir.create()
    try:
        self.tmpdir.clearOld(5)
    except Exception:
        pass
    tr_file = path.join(tmpdir.getPath(),
                        InfoEngine.getDefaultTempFileName())

    engine = InfoEngine.getEngine()
    engine.setLogFile(tr_file)
    tmpdir.retainFiles([tr_file])

    model_file = EncodedFileName(args[1])
    wild_cards = engine.getFileWildCards()
    exfiles = Common.ExtractedFiles(model_file, tmpdir.getPath(), wild_cards)

    model_file = exfiles[1][0]
    args[1] = model_file

    if len(args) > 2:
        results_file = EncodedFileName(args[2])
        exfiles = Common.ExtractedFiles(results_file, tmpdir.getPath(), wild_cards)
        results_file = exfiles[1][0]
        args[2] = results_file

    asm_dep = False
    ofp = None
    for opt in options:
        if opt == '--ekm-asm-dep':
            asm_dep = True
        if opt.startswith('--output='):
            ofp = opt
            ofp = ofp.split('=',1)[1]

    if asm_dep:
        retval = export_minerva_filedeps(args[1], ofp)
    else:
        retval = engine.getInfo(options, args[1:])
    tmpdir.destroy()
    return retval
    
def cmd_args(argv):
    options = []
    for option in argv:
        if option.startswith('--'):
            options.append(option)

    out_file = None
    out_next = False
    args = []
    for option in argv:
        if out_next:
            out_file = option
            out_next = False
        elif option == '-o':
            out_next = True
        else:
            if not option.startswith('--'):
                args.append(option)

    has_out = False
    for option in options:
        if option.startswith('--output='):
            has_out = True
    if out_file and not has_out:
        options.append('--output={}'.format(out_file))

    return options, args

def main(argv):
    options, args = cmd_args(argv)
    print(options)
    print(args)
    return invoke_caeinfo(options, args)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
