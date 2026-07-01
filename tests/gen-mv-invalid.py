#!/usr/bin/env python3
"""Generate crafted Silicon Graphics Movie files with bogus size fields."""
import struct
import sys

def write_huge_nb_frames(path):
    """Version-2 MOVI with an absurd nb_frames used for index allocation."""
    data = bytearray()
    data += b'MOVI'
    data += struct.pack('>H', 2)           # version
    data += b'\x00' * 10                   # padding
    data += struct.pack('>d', 30.0)        # fps
    data += struct.pack('>H', 2)           # MOVIE_SILENT
    data += b'\x00' * 2
    data += struct.pack('>I', 0x10000000)  # nb_frames (bogus, > MV_MAX_FRAMES)
    data += struct.pack('>I', 1)           # compression MVC1
    data += struct.pack('>I', 64)          # width
    data += struct.pack('>I', 64)          # height
    data += b'\x00' * 12
    data += b'\x00' * 24                   # skipped audio metadata
    data += b'\x00' * 0x80                 # title
    data += b'\x00' * 0x100                # comment
    data += b'\x00' * 0x80
    # deliberately omit the (huge) index table
    open(path, 'wb').write(data)

def write_huge_var_size(path):
    """Version-0/3 MOVI with a table entry size that would over-allocate."""
    data = bytearray()
    data += b'MOVI'
    data += struct.pack('>H', 0)           # version major
    data += struct.pack('>H', 3)           # version minor marker
    data += b'\x00' * 4
    # global variable table
    data += b'\x00' * 4
    data += struct.pack('>I', 1)           # one entry
    data += b'\x00' * 4
    name = b'__NUM_I_TRACKS'
    data += name + b'\x00' * (16 - len(name))
    data += struct.pack('>I', 0x7FFFFFF0)  # bogus size for allocation
    open(path, 'wb').write(data)

def write_huge_packet_size(path):
    """Version-2 MOVI with one frame whose index size exceeds AVIndexEntry."""
    data = bytearray()
    data += b'MOVI'
    data += struct.pack('>H', 2)
    data += b'\x00' * 10
    data += struct.pack('>d', 30.0)
    data += struct.pack('>H', 2)           # silent
    data += b'\x00' * 2
    data += struct.pack('>I', 1)           # one frame
    data += struct.pack('>I', 1)           # MVC1
    data += struct.pack('>I', 64)
    data += struct.pack('>I', 64)
    data += b'\x00' * 12
    data += b'\x00' * 24
    data += b'\x00' * 0x80
    data += b'\x00' * 0x100
    data += b'\x00' * 0x80
    # index: pos, asize, vsize, 8 pad  — vsize is the bogus packet size
    data += struct.pack('>I', 0)           # pos
    data += struct.pack('>I', 0)           # asize
    data += struct.pack('>I', 0xFFFFFFFF)  # vsize (becomes negative as int)
    data += b'\x00' * 8
    open(path, 'wb').write(data)

def main():
    if len(sys.argv) != 3:
        print(f'usage: {sys.argv[0]} <kind> <output>', file=sys.stderr)
        sys.exit(2)
    kind, path = sys.argv[1], sys.argv[2]
    {
        'huge-nb-frames': write_huge_nb_frames,
        'huge-var-size': write_huge_var_size,
        'huge-packet-size': write_huge_packet_size,
    }[kind](path)

if __name__ == '__main__':
    main()
