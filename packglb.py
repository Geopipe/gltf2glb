#!/usr/bin/env python3

#------------------------------------
# packglb.py: GLB to I3DM/B3DM converter
# (c) 2018 Geopipe, Inc.
# All rights reserved. See LICENSE.
#------------------------------------

import sys, os
import argparse
import base64
import json
import re
import struct

import b3dm, i3dm

def main():
	""" Convert GLTF to GLB, with optional additional I3DM or B3DM encoding"""

	# Parse options and get results
	parser = argparse.ArgumentParser(description='Converts GLTF to GLB')
	parser.add_argument("-i", "--i3dm", type=str, \
	                    help="Export i3dm, with required path to input JSON instance table data. Supports only embedded GLTFs")
	parser.add_argument("-b", "--b3dm", type=str, \
	                    help="Export b3dm, with optional path to input JSON batch table data")
        parser.add_argument("--objectwise", action='store_true', \
                            help="If b3dm is specified and this is set, assume list of dicts. Defaults otherwise to dict of lists")
	parser.add_argument("-o", "--output", required=False, default=None, \
	                    help="Optional output path (defaults to the path of the input file")
	parser.add_argument("-u", "--unpack", action='store_true', \
	                    help="Unpack rather than create b3dm file")
	parser.add_argument("filename")
	args = parser.parse_args()

	if args.b3dm and args.unpack and args.filename:
		b3dm_decoder = b3dm.B3DM()
		with open(args.filename, 'rb') as f:
			data = f.read()
			b3dm_decoder.readBinary(data)
		with open(args.filename + '.glb', 'wb') as f:
			output_data = b3dm_decoder.getGLTFBin()
			f.write(output_data)
		sys.exit(0)

	# Make sure the input file is *.glb
	if not args.filename.endswith('.glb'):
		print("Failed to create packed binary GLB file: input is not *.glb")
		sys.exit(-1)

	with open(args.filename, 'r') as f:
		glb = f.read()

	if args.b3dm != None:
		ext = 'b3dm'
	elif args.i3dm != None:
		ext = 'i3dm'
	else:
		ext = 'glb'

	fname_out = os.path.splitext(os.path.basename(args.filename))[0] + '.' + ext
	if None != args.output:
		if "" == os.path.basename(args.output):
			fname_out = os.path.join(fname_out, fname_out)
		else:
			fname_out = args.output
	else:
		fname_out = os.path.join(os.path.dirname(args.filename), fname_out)

	if args.b3dm != None:
		b3dm_encoder = b3dm.B3DM()
		if len(args.b3dm):
			with open(args.b3dm, 'r') as f:
				b3dm_json = json.loads(f.read())
				#print b3dm_json
				b3dm_encoder.loadJSONBatch(b3dm_json, args.objectwise)

		with open(fname_out, 'w') as f:
			f.write(b3dm_encoder.writeBinary(glb))

	elif args.i3dm != None:
		i3dm_encoder = i3dm.I3DM()
		if not(len(args.i3dm)):
			raise ValueError("-i/--i3dm requires a JSON instance table")
		else:
			with open(args.i3dm, 'r') as f:
				i3dm_json = json.loads(f.read())
			i3dm_encoder.loadJSONInstances(i3dm_json, False)

		with open(fname_out, 'w') as f:
			f.write(i3dm_encoder.writeBinary(glb, True))		# Second arg: embed gltf

	else:
		# This is kinda pointless
		with open(fname_out, 'w') as f:
			f.write(glb)

if __name__ == "__main__":
	main()
