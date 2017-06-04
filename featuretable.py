#!/usr/bin/env python

#--------------------------------------------------
# featuretable.py: Component of GLTF to GLB converter
# Currently a placeholder copy of BatchTable
# (c) 2017 Geopipe, Inc.
# All rights reserved. See LICENSE.
#--------------------------------------------------

import struct
import json
from batchtable import BatchTable

class FeatureTable(BatchTable):
	def __init__(self):
		BatchTable.__init__(self)
