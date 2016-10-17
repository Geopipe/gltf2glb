#!/usr/bin/env python

#--------------------------------------------
# i3dm.py: Component of GLTF to GLB converter
# (c) 2016 Geopipe, Inc.
# All rights reserved. See LICENSE.
#--------------------------------------------

import struct
from batchtable import BatchTable

I3DM_VERSION = 1
I3DM_HEADER_LEN = 24

class I3DM(BatchTable):
	def __init__(self):
		BatchTable.init(self)
		self.gltf_bin = bytearray()
		raise NotImplementedError
