#!/usr/bin/env python
#---------------------------------------------------------------------
# packcmpt.py: CMPT file creator, to pack multiple Tile3D files into a
# single package. Component of gltf2glb.
# (c) 2016-2020 Geopipe, Inc.
# All rights reserved. See LICENSE.
#---------------------------------------------------------------------

import sys, os
import argparse
import struct

CMPT_EXT = '.cmpt'
CMPT_MAGIC = 'cmpt'
CMPT_VERSION = 1
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
		self.header.extend(CMPT_MAGIC)							# Magic
		self.header.extend(struct.pack('<I', 1))				# Version
		self.header.extend(struct.pack('<I', CMPT_HEADER_LEN + len(self.body)))
		self.header.extend(struct.pack('<I', self.tile_count))	# Number of tiles

		if len(self.header) != CMPT_HEADER_LEN:
			print("Unexpected header size!")
			raise ArithmeticError

	def export(self, filename):
		self.composeHeader()
		with open(filename, 'wb') as f:
			f.write(self.header)
			f.write(self.body)

class CmptDecoder:
	""" Pack multiple Tile3D file(s) into a single unit """
	def __init__(self):
		self.data = ""
		self.tiles = []

	def add(self, filename = None, data = None):
		if filename:
			with open(filename, 'rb') as f:
				self.data = f.read()
		elif data:
			self.data = data
		else:
			print("Both filename and data cannot be None!")
			raise IOError

	def decode(self):
		# Grab the header
		self.offset = 0;
		magic = self.unpack('4s', self.data)
		version = self.unpack('<I', self.data)

		if magic != CMPT_MAGIC or version > CMPT_VERSION:
			print("Unrecognized magic string %s or bad version %d" % (magic, version))
			raise IOError

		self.length = self.unpack('<I', self.data)
		self.count = self.unpack('<I', self.data)

		# Now grab all the body items
		self.tiles = []
		for i in xrange(self.count):
			start_idx = self.offset

			# All the possible inner tile items have a byte count in the same place.
			inner_magic = self.unpack('4s', self.data)
			if inner_magic not in VALID_INTERIOR_TILES:
				print("Unrecognized interior tile magic %s" % (inner_magic))
			inner_version = self.unpack('<I', self.data)
			inner_length = self.unpack('<I', self.data)

			self.tiles.append({ \
				'magic': inner_magic, \
				'version': inner_version, \
				'length': inner_length, \
				'data': self.data[start_idx : start_idx + inner_length] \
			});
			self.offset = start_idx + inner_length

		del self.data

	def getTiles(self):
		return self.tiles
			
	def unpack(self, fmt, data):
		calc_len = struct.calcsize(fmt)
		self.offset += calc_len
		return struct.unpack(fmt, data[self.offset - calc_len : self.offset])[0]

def main():
	""" Pack one or more i3dm and/or b3dm files into a cmpt"""

	# Parse options and get results
	parser = argparse.ArgumentParser(description='Packs one or more i3dm and/or b3dm files into a cmpt')
	parser.add_argument("-o", "--output", type=str, required='True', \
						help="Output cmpt file")
	parser.add_argument("-u", "--unpack", action='store_true', \
	                    help="Unpack, rather than pack. Give input cmpt file as -o, output dir as input file")
	parser.add_argument('input_files', nargs='*')
	args = parser.parse_args()

	if args.unpack:
		decoder = CmptDecoder()
		decoder.add(filename = args.output)
		decoder.decode()

		tiles = decoder.getTiles()
		idx = 0
		for tile in tiles:
			output_fname = os.path.basename(args.output) + '-' + str(idx) + '.' + tile['magic']
			with open(os.path.join(args.input_files[0], output_fname), 'wb') as f:
				f.write(tile['data'])
	else:
		if not len(args.input_files):
			print("At least one input tile file must be specified!")

		else:
			encoder = CmptEncoder()
			for fname in args.input_files:
				encoder.add(fname)
			encoder.export(args.output + ('' if args.output.endswith(CMPT_EXT) else CMPT_EXT))

if __name__ == "__main__":
	main()
