#!/usr/bin/env python3
#--------------------------------------------------------------------------
# tile3dinfo.py: Parse a CMPT, B3DM, or I3DM file (recursively) and deliver
# information about what it contains. Component of gltf2glb.
# (c) 2016-2021 Geopipe, Inc.
# All rights reserved. See LICENSE.
#--------------------------------------------------------------------------

import sys, os
import argparse
import struct

import packcmpt as cmpt
import packglb
import b3dm
import i3dm

def printFeatureBatch(decoder, s_indent):
    print("%s\tFeature JSON length: %d" % (s_indent, decoder.len_feature_json))
    print("%s\tFeature binary length: %d" % (s_indent, decoder.len_feature_bin))
    print("%s\tBatch JSON length: %d" % (s_indent, decoder.len_batch_json))
    print("%s\tBatch binary length: %d" % (s_indent, decoder.len_batch_bin))
    print("%s\tGLTF binary length: %d" % (s_indent, len(decoder.gltf_bin)))

def parseB3DM(data, indent = 0):
    s_indent = '\t' * indent
    b3dm_decoder = b3dm.B3DM()
    b3dm_decoder.readBinary(data)

    print("%sB3DM File:" % (s_indent))
    printFeatureBatch(b3dm_decoder, s_indent)

def parseI3DM(data, indent = 0):
    s_indent = '\t' * indent
    i3dm_decoder = i3dm.I3DM()
    i3dm_decoder.readBinary(data)

    print("%sI3DM File:" % (s_indent))
    printFeatureBatch(i3dm_decoder, s_indent)

def parseCMPT(data, indent = 0):
    print("%sCMPT File:" % ('\t' * indent))
    decoder = cmpt.CmptDecoder()
    decoder.add(data = data)
    decoder.decode()

    for tile in decoder.getTiles():
        parseFile(tile['data'], indent + 1)

def parseFile(data, indent = 0):
    if len(data) < 4:
        raise ValueError('Binary is fewer than 4 bytes; no magic fits')
    if data[0:4] == cmpt.CMPT_MAGIC:
        parseCMPT(data, indent)
    elif data[0:4] == b3dm.B3DM_MAGIC:
        parseB3DM(data, indent)
    elif data[0:4] == i3dm.I3DM_MAGIC:
        parseI3DM(data, indent)
    else:
        raise ValueError('Unknown magic "%s"' % (data[0:4]))

def main():
    """ Pack one or more i3dm and/or b3dm files into a cmpt"""

    # Parse options and get results
    parser = argparse.ArgumentParser(description='Parses a cmpt, b3dm, i3dm, or glb file, and prints info about it')
    parser.add_argument('input_file')
    args = parser.parse_args()

    with open(args.input_file, 'rb') as f:
        parseFile(f.read(), indent = 0)

if __name__ == '__main__':
    main()
