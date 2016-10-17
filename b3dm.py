#!/usr/bin/env python

#--------------------------------------------
# b3dm.py: Component of GLTF to GLB converter
# (c) 2016 Geopipe, Inc.
# All rights reserved. See LICENSE.
#--------------------------------------------

import struct
from batchtable import BatchTable

B3DM_VERSION = 1
B3DM_HEADER_LEN = 24

class B3DM(BatchTable):
	def __init__(self):
		BatchTable.__init__(self)
		self.gltf_bin = bytearray()

	def writeBinary(self, gltf_bin, num_features = 0):
		self.finalize()

		# Generate the header
		num_features = max(num_features, self.getNumFeatures())
		output = self.writeHeader(gltf_bin, num_features)

		# Add the batch table JSON to the output
		batch_json = self.getBatchJSON()
		output.extend(batch_json)

		# Add the batch table binary to the output
		batch_bin  = self.getBatchBin()
		output.extend(batch_bin)

		# Add the GLTF model body to the output
		output.extend(gltf_bin)

		return output

	def writeHeader(self, gltf_bin, num_features):
		batch_json = self.getBatchJSON()
		batch_bin  = self.getBatchBin()

		length = B3DM_HEADER_LEN + len(batch_json) + \
		         len(batch_bin) + len(gltf_bin)
	
		output = bytearray()
		output.extend("b3dm")
		output.extend(struct.pack('<I', B3DM_VERSION))
		output.extend(struct.pack('<I', length))
		output.extend(struct.pack('<I', len(self.batch_json)))
		output.extend(struct.pack('<I', len(self.batch_bin)))
		output.extend(struct.pack('<I', num_features))
	
		# Sanity check
		if (len(output) != B3DM_HEADER_LEN):
			raise ValueError("Incorrect b3dm header length")
	
		return output
