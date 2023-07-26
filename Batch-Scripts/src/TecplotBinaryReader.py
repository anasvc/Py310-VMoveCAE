#!/usr/bin/python

import sys
import struct

#----------------------------------------------------------------------------

BYTE_ORDER_NATIVE = 0
BYTE_ORDER_LITTLE_ENDIAN = 1
BYTE_ORDER_BIG_ENDIAN = 2

#----------------------------------------------------------------------------

FILE_TYPE_FULL = 0
FILE_TYPE_GRID = 1
FILE_TYPE_SOLUTION = 2

#----------------------------------------------------------------------------

class TecplotBinaryReader():

    def __init__(self, file_path):
        self.file_path = file_path
        self.file = None
        self.version_name = None
        self.version_number = None
        self.byte_order = BYTE_ORDER_NATIVE
        self.formatter_prefix = ''
        self.int_formatter = 'i'

    def read_int_bytes(self):
        return self.file.read(4)

    def read_int(self):
        v = self.read_int_bytes()
        return struct.unpack(self.int_formatter, v)[0]

    def read_string(self):
        str = ''
        next_int = self.read_int()
        while next_int != 0:
            str = str + chr(next_int)
            next_int = self.read_int()

        return str

    def read_file_type(self):
        self.file_type = FILE_TYPE_FULL
        if self.version_number >= 110:
            #pos = self.file.tell() 
            self.file_type = self.read_int()
            #if self.file_type != FILE_TYPE_FULL and self.file_type != FILE_TYPE_GRID and self.file_type != FILE_TYPE_SOLUTION:
                #self.file_type = FILE_TYPE_FULL
            #self.file.seek(pos)

    def read(self):
        self.file = open(self.file_path, 'rb')
        self.version_name = self.file.read(8).rstrip()
        num_str = self.version_name[5:]
        self.version_number = int(num_str)

        int_1 = self.read_int_bytes()
        if struct.unpack('i', int_1)[0] != 1:
            if struct.unpack('<i', int_1)[0] == 1:
                self.byte_order = BYTE_ORDER_LITTLE_ENDIAN
                self.formatter_prefix = '<'
            elif struct.unpack('>i', int_1)[0] == 1:
                self.byte_order = BYTE_ORDER_BIG_ENDIAN
                self.formatter_prefix = '>'
        self.int_formatter = self.formatter_prefix + 'i'

        self.read_file_type()

        self.title = self.read_string().rstrip()
        self.number_of_variables = self.read_int()
        self.variables = []
        for num in range(self.number_of_variables):
            self.variables.append(self.read_string().rstrip())

    def close():
        self.file.close()

    def __del__(self):
        pass # do nothing

#----------------------------------------------------------------------------

def main(argv):
    file_path = None
    if len(argv) > 1:
        file_path = argv[1]
    if not file_path:
        return 2

    plt = TecplotBinaryReader(file_path)
    plt.read()

    print 'Version             : \'%d\'' % plt.version_number
    print 'Title               : \'%s\'' % plt.title
    print 'Number of Variables : \'%d\'' % plt.number_of_variables
    print 'Variables           : '
    for i in range(plt.number_of_variables):
        print '                      \'%s\'' % plt.variables[i]

#----------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main(sys.argv))

