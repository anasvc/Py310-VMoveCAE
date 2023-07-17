import os, sys
import glob
import pefile

#----------------------------------------------------------------------------

def main(argv):
    option_list = []
    print argv
    for option in argv:
        if option.startswith('--'):
            option_list.append(option)

    file_list = []
    #for option in argv:
    #    if not option.startswith('--'):
    #        file_list.append(option)

    opdict = {}
    for option in option_list:
        if option.find('=') != -1:
            [key, value] = option.split('=')
            opdict[key] = value
        
    arch = opdict.get('--arch', 'win32')
    folder = opdict.get('--folder', None)
    if folder:
        file_list = file_list + glob.glob(folder + os.sep + '*')

    arch = arch.lower()
    arch_dict = { 'win32': 'IMAGE_FILE_MACHINE_I386', 
                         'x64': 'IMAGE_FILE_MACHINE_AMD64' 
                       }

    arch = arch_dict[arch]
    machine_num_dict = dict(pefile.machine_types)

    machine_num = machine_num_dict['IMAGE_FILE_MACHINE_UNKNOWN']
    machine_num = machine_num_dict.get(arch, machine_num)

    for file in file_list:
        print 'Testing ' + file + ' ... '
        try:
            pe = pefile.PE(file, fast_load=True)
            if pe.FILE_HEADER.Machine == machine_num:
                print '\t\t\t\t Passed'
            else:
                print '\t\t\t\t Failed'
        except pefile.PEFormatError, ex:
                print '\t\t\t\t Unsupported'

#----------------------------------------------------------------------------

if __name__ == "__main__":
    main(sys.argv)

