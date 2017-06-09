#!/usr/bin/env python

#------------------------------------
# packcmpt.py: CMPT file creator, to
# pack multiple Tile3D files into a
# single package.
# Component of gltf2glb
# (c) 2016-2017 Geopipe, Inc.
# All rights reserved. See LICENSE.
#------------------------------------

import sys, os
import argparse
import struct

CMPT_EXT = '.cmpt'
CMPT_HEADER_LEN = 16
VALID_INTERIOR_TILES = ['b3dm', 'i3dm', 'cmpt']

class CmptEncoder:
	""" Pack multiple Tile3D file(s) into a single unit """
	def __init__(self):
		self.header = bytearray()
		self.body = bytearray()
		self.tile_count = 0

	def add(self, filename):
		with open(filename, 'r') as f:
			content = f.read()

		# All interior tiles have a four-character extension
		_, ext = os.path.splitext(filename)		# Get the extension
		ext = ext[1:]							# Remove the .
		if len(ext) != 4:
			print("Invalid extension ('%s') for file '%s'" % (ext, filename))
			raise NameError

		# Make sure it's a known extension
		if ext not in VALID_INTERIOR_TILES:
			print("Extension '%s' ('%s') not recognized as valid tile type" % (ext, filename))
			raise NameError

		self.body.extend(content)							# Tile contents

		self.tile_count += 1

	def composeHeader(self):
		self.header.extend('cmpt')								# Magic
		self.header.extend(struct.pack('<I', 1))				# Version
		self.header.extend(struct.pack('<I', CMPT_HEADER_LEN + len(self.body)))
		self.header.extend(struct.pack('<I', self.tile_count))	# Number of tiles

		if len(self.header) != CMPT_HEADER_LEN:
			print("Unexpected header size!")
			raise ArithmeticError

	def export(self, filename):
		self.composeHeader()
		with open(filename, 'w') as f:
			f.write(self.header)
			f.write(self.body)

def main():
	""" Pack one or more i3dm and/or b3dm files into a cmpt"""

	# Parse options and get results
	parser = argparse.ArgumentParser(description='Packs one or more i3dm and/or b3dm files into a cmpt')
	parser.add_argument("-o", "--output", type=str, required='True', \
						help="Output cmpt file")
	parser.add_argument('input_files', nargs='+')
	args = parser.parse_args()

	encoder = CmptEncoder()
	for fname in args.input_files:
		encoder.add(fname)
	encoder.export(args.output + ('' if args.output.endswith(CMPT_EXT) else CMPT_EXT))

if __name__ == "__main__":
	main()
