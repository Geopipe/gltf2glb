#!/usr/bin/env python

#--------------------------------------------------
# featuretable.py: Component of GLTF to GLB converter
# Currently a placeholder copy of BatchTable
# (c) 2017 - 2019 Geopipe, Inc.
# All rights reserved. See LICENSE.
#--------------------------------------------------

import struct
import json
from batchtable import BatchTable

class FeatureTable(BatchTable):
	def __init__(self):
		BatchTable.__init__(self)
		self.features_global = {}
		self.features_json = bytearray()
		self.features_bin  = bytearray()
		self.num_global_features = 0

	def addGlobal(self, key, value):
		self.features_global[key] = value
		self.num_global_features += 1

	def writeOutput(self):
		data_out = {}
		# TODO: Add proper encoding to JSON + binary, rather than just
		# punting to the naive method
		data_out = self.features_global
		data_out.update(self.batch_in)
		
		self.features_json = bytearray(json.dumps(data_out, separators=(',', ':'), sort_keys=True))
		
		# TODO: Why do we clear these?
		self.batch_in = bytearray()
		self.features_global = bytearray()
		self.num_features = 0
		self.num_global_features = 0

	def finalize(self):
		# Create the actual features JSON (and binary)
		self.writeOutput()

		# Pad with spaces to a multiple of 4 bytes
		padded_features_json_len = len(self.features_json) + 3 & ~3
		self.features_json.extend(' ' * (padded_features_json_len - len(self.features_json)))

		padded_features_bin_len = len(self.features_bin) + 3 & ~3
		self.features_bin.extend(' ' * (padded_features_bin_len - len(self.features_bin)))

	def getFeatureJSON(self):
		return self.features_json

	def getFeatureBin(self):
		return self.features_bin