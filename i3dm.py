#!/usr/bin/env python3

#--------------------------------------------------------
# i3dm.py: Component of GLTF to GLB converter
# (c) 2016 - 2019 Geopipe, Inc.
# All rights reserved. See LICENSE.
#
# Source spec: see
# https://github.com/AnalyticalGraphicsInc/3d-tiles/tree/
#       master/specification/TileFormats/Instanced3DModel
# - Feature table: contains the actual information about
#   the instances to be created.
# - Batch table: may contain information about separate
#   units that can be declaratively styled within the
#   single model that is instanced, but we expect this to
#   be used in a relative minority of the use cases.
#---------------------------------------------------------

import struct
import argparse
import json

from batchtable import BatchTable
from featuretable import InstanceFeatureTable

I3DM_MAGIC = 'i3dm'
I3DM_VERSION = 1
I3DM_HEADER_LEN = 32

I3DM_SEMANTICS = {
	'POSITION' : 'f32',
	'NORMAL_UP' : 'f32',
	'NORMAL_RIGHT' : 'f32',
	'SCALE' : 'f32',
	'SCALE_NON_UNIFORM' : 'f32',
	'POSITION_QUANTIZED' : 'u16',
	'NORMAL_UP_OCT32P' : 'u16',
	'NORMAL_RIGHT_OCT32P' : 'u16',
	'BATCH_ID' : 'u16'
}

class I3DM(object):
	def __init__(self):
		self.batch_table = BatchTable()
		self.feature_table = InstanceFeatureTable(I3DM_SEMANTICS)
		self.gltf_bin = bytearray()

	def loadJSONBatch(self, data_in, object_wise = True):
		self.batch_table.loadJSONBatch(data_in, object_wise)

	def loadJSONInstances(self, i3dm_json, object_wise = True):
		self.loadJSONFeatures(i3dm_json, object_wise)

	def loadJSONFeatures(self, data_in, object_wise = True):
		self.feature_table.loadJSONBatch(data_in, object_wise)

	# If embed_gltf is false, gltf_bin is a URI string instead of GLTF data
	def writeBinary(self, gltf_bin, embed_gltf = True, num_batches = 0, num_feature_features = 0):
		self.embed_gltf = embed_gltf

		# Add the required field BATCH_LENGTH to the feature table,
		# as well as any other required globals
		num_batch_features = max(num_batches, self.batch_table.getNumFeatures())
		self.feature_table.addGlobal('BATCH_LENGTH', num_batch_features)
		num_feature_features = max(num_feature_features, self.feature_table.getNumFeatures())
		self.feature_table.addGlobal('INSTANCES_LENGTH', num_feature_features)

		self.batch_table.finalize()
		self.feature_table.finalize()

		# Generate the header
		output = self.writeHeader(gltf_bin, num_batch_features, num_feature_features)

		# Add the feature table JSON to the output
		feature_json = self.feature_table.getFeatureJSON()
		output.extend(feature_json)

		# Add the feature table binary to the output
		feature_bin  = self.feature_table.getFeatureBin()
		output.extend(feature_bin)

		# Add the batch table JSON to the output
		batch_json = self.batch_table.getBatchJSON()
		output.extend(batch_json)

		# Add the batch table binary to the output
		batch_bin  = self.batch_table.getBatchBin()
		output.extend(batch_bin)

		# Add the GLTF model body to the output
		output.extend(gltf_bin)

		return output

	# If embed_gltf is false, gltf_bin is a URI string instead of GLTF data
	def writeHeader(self, gltf_bin, num_batch_features, num_feature_features):
		len_feature_json = len(self.feature_table.getFeatureJSON())
		len_feature_bin  = len(self.feature_table.getFeatureBin())
		len_batch_json   = len(self.batch_table.getBatchJSON())
		len_batch_bin    = len(self.batch_table.getBatchBin())

		length = I3DM_HEADER_LEN + \
		         len_feature_json + len_feature_bin + \
		         len_batch_json   + len_batch_bin + \
		         len(gltf_bin)
	
		output = bytearray()
		output.extend(I3DM_MAGIC)
		output.extend(struct.pack('<I', I3DM_VERSION))
		output.extend(struct.pack('<I', length))
		output.extend(struct.pack('<I', len_feature_json))
		output.extend(struct.pack('<I', len_feature_bin))
		output.extend(struct.pack('<I', len_batch_json))
		output.extend(struct.pack('<I', len_batch_bin))
		output.extend(struct.pack('<I', 1 if self.embed_gltf else 0))
	
		# Sanity check
		if (len(output) != I3DM_HEADER_LEN):
			raise ValueError("Incorrect i3dm header length")
	
		return output

	def readBinary(self, data):
		self.offset = 0
		self.readHeader(data)			 # What it says on the tin

		# Now grab the feature table, batch table, and GLB
		self.feature_json = self.unpackString(data, self.len_feature_json)
		self.feature_bin  = self.unpackString(data, self.len_feature_bin)
		self.batch_json = self.unpackString(data, self.len_batch_json)
		self.batch_bin  = self.unpackString(data, self.len_batch_bin)

		self.gltf_bin = self.unpackString(data, self.length - self.offset)

	def readHeader(self, data):
		self.magic = self.unpack('4s', data)
		self.version = self.unpack('<I', data)

		if self.magic != I3DM_MAGIC or self.version > I3DM_VERSION:
			raise IOError("Unrecognized magic %s or bad version %d" % (self.magic, self.version))

		self.length           = self.unpack('<I', data)
		self.len_feature_json = self.unpack('<I', data)
		self.len_feature_bin  = self.unpack('<I', data)
		self.len_batch_json   = self.unpack('<I', data)
		self.len_batch_bin    = self.unpack('<I', data)
		self.embed_gltf       = self.unpack('<I', data)

	def getGLTFBin(self):
		return self.gltf_bin

	def unpackString(self, data, length):
		self.offset += length
		return data[self.offset - length : self.offset]

	def unpack(self, fmt, data):
		calc_len = struct.calcsize(fmt)
		self.offset += calc_len
		return struct.unpack(fmt, data[self.offset - calc_len : self.offset])[0]

def main():
	""" Generates an i3dm file from a glb plus JSON"""

	# Parse options and get results
	parser = argparse.ArgumentParser(description='Converts GLTF to GLB')
	parser.add_argument("-i", "--i3dm", type=str, required=True, \
	                    help="Export i3dm, with required path to input JSON instance table data. Supports only embedded GLBs")
	parser.add_argument("-b", "--batch", type=str, required=False, \
	                    help="Optional path to batch table JSON")
	parser.add_argument("-g", "--glb", type=str, required=True, \
	                    help="GLB file to instance and embed in/link from the output i3dm file")
	parser.add_argument("-e", "--embed", action="store_true", \
	                    help="Specify to embed the GLB file instead of referencing it")
	parser.add_argument("-o", "--output", required=True, \
	                    help="Output i3dm path")
	args = parser.parse_args()
	
	i3dm_encoder = I3DM()
	if not(len(args.i3dm)):
		raise ValueError("-i/--i3dm requires a JSON instance table")
	else:
		with open(args.i3dm, 'r') as f:
			i3dm_json = json.loads(f.read())
		i3dm_encoder.loadJSONInstances(i3dm_json)
		if len(args.batch):
			with open(args.batch, 'r') as f:
				batch_json = json.loads(f.read())
			i3dm_encoder.loadJSONBatch(batch_json, False)

	with open(args.output, 'wb') as f:
		if args.embed:
			with open(args.glb, 'rb') as glb:
				f.write(i3dm_encoder.writeBinary(glb.read(), True))		# Second arg: embed gltf
		else:
			while len(args.glb) % 8:
				args.glb += ' '
			f.write(i3dm_encoder.writeBinary(args.glb, False))

if __name__ == "__main__":
	main()
