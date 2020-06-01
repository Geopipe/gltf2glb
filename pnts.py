#!/usr/bin/env python

#--------------------------------------------
# b3dm.py: Component of GLTF to GLB converter
# (c) 2016 Geopipe, Inc.
# All rights reserved. See LICENSE.
#--------------------------------------------

import struct
from batchtable import BatchTable
from featuretable import FeatureTable

PNTS_MAGIC = 'pnts'
PNTS_VERSION = 1
PNTS_HEADER_LEN = 28

class PNTS:
	def __init__(self):
		self.batch_table = BatchTable()
		self.feature_table = FeatureTable()

	def loadJSONBatch(self, data_in, object_wise = True):
		self.batch_table.loadJSONBatch(data_in, object_wise)

	def loadJSONFeature(self, data_in, object_wise = True):
		self.feature_table.loadJSONBatch(data_in, object_wise)

	def writeBinary(self, num_batch_features = 0, num_feature_features = 0):

		# Add the required field BATCH_LENGTH to the feature table,
		# as well as any other required globals
		num_batch_features = max(num_batch_features, self.batch_table.getNumFeatures())
		self.feature_table.addGlobal('BATCH_LENGTH', num_batch_features)
		num_feature_features = max(num_feature_features, self.feature_table.getNumFeatures())

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

		return output

	def writeHeader(self, gltf_bin, num_feature_features, num_batch_features):
		len_feature_json = len(self.feature_table.getFeatureJSON())
		len_feature_bin  = len(self.feature_table.getFeatureBin())
		len_batch_json   = len(self.batch_table.getBatchJSON())
		len_batch_bin    = len(self.batch_table.getBatchBin())

		length = PNTS_HEADER_LEN + \
		         len_feature_json + len_feature_bin + \
		         len_batch_json   + len_batch_bin + \
		         len(gltf_bin)
	
		output = bytearray()
		output.extend(PNTS_MAGIC)
		output.extend(struct.pack('<I', PNTS_VERSION))
		output.extend(struct.pack('<I', length))
		output.extend(struct.pack('<I', len_feature_json))
		output.extend(struct.pack('<I', len_feature_bin))
		output.extend(struct.pack('<I', len_batch_json))
		output.extend(struct.pack('<I', len_batch_bin))
	
		# Sanity check
		if (len(output) != PNTS_HEADER_LEN):
			raise ValueError("Incorrect pnts header length")
	
		return output

	def readBinary(self, data):
		self.offset = 0
		self.readHeader(data)			 # What it says on the tin

		# Now grab the feature table, batch table, and GLB
		self.feature_json = self.unpackString(data, self.len_feature_json)
		self.feature_bin =  self.unpackString(data, self.len_feature_bin)
		self.batch_json = self.unpackString(data, self.len_batch_json)
		self.batch_bin = self.unpackString(data, self.len_batch_bin)

	def readHeader(self, data):
		self.magic = self.unpack('4s', data)
		self.version = self.unpack('<I', data)

		if self.magic != PNTS_MAGIC or self.version > PNTS_VERSION:
			raise IOError("Unrecognized magic %s or bad version %d" % (self.magic, self.version))

		self.length           = self.unpack('<I', data)
		self.len_feature_json = self.unpack('<I', data)
		self.len_feature_bin  = self.unpack('<I', data)
		self.len_batch_json   = self.unpack('<I', data)
		self.len_batch_bin    = self.unpack('<I', data)

	def unpackString(self, data, length):
		self.offset += length
		return data[self.offset - length : self.offset]

	def unpack(self, fmt, data):
		calc_len = struct.calcsize(fmt)
		self.offset += calc_len
		return struct.unpack(fmt, data[self.offset - calc_len : self.offset])[0]

def main():
	raise NotImplementedError("This file cannot be used directly!")

if __name__ == "__main__":
	main()
