#!/usr/bin/env python

#------------------------------------
# gltf2glb.py: GLTF to GLB converter
# (c) 2016 Geopipe, Inc.
# All rights reserved. See LICENSE.
#------------------------------------

import sys, os
import argparse
import base64
import json
import re
import struct

import b3dm, i3dm

EMBED_ARR = ['textures', 'shaders']
BASE64_REGEXP = re.compile(r'^data:.*?;base64,')

class BodyEncoder:
	""" Encode the binary chunks of the GLB's body """
	def __init__(self, containing_dir):
		self.containing_dir = containing_dir
		self.body_length = 0
		self.body_parts = []

	def addToBody(self, uri, length):
		""" Adds an immediate or external data uri to the GLB's body """
		if uri.startswith('data:'):
			if not BASE64_REGEXP.match(uri):
				raise ValueError("Unsupported data URI")
			uri = BASE64_REGEXP.sub("", uri)
			buf = bytearray(base64.b64decode(uri))
		else:
			with open(os.path.join(self.containing_dir, uri), 'rb') as f:
				buf = bytearray(f.read())

		# Fix length variable and buffer length
		length = min(length, len(buf)) if length is not None else len(buf)
		print("Adding %s (%d of %d)" % (os.path.join(self.containing_dir, uri), length, len(buf)))
		buf = buf[0:length]
	
		# Handle the buffer
		offset = self.body_length
		self.body_parts.append(offset)
		self.body_parts.append(buf)
		length = len(buf)
		self.body_length += length
		return (offset, length)

class GLBEncoder:
	""" Combine a JSON header and a binary body into a GLB with a proper header """
	def __init__(self, header, body):
		self.header = header
		self.body = body

	def export(self, filename):
		""" Export the GLB file """
		with open(filename, 'wb') as f:
			f.write(self.exportString())

	def exportString(self):
		""" Export the GLB data"""
		scene_len = len(self.header)
	
		# As body is 4-byte-aligned, the scene length must be padded to a multiple of 4
		padded_scene_len = (scene_len + 3) & ~3
		padded_body_length = (self.body.body_length + 3) & ~3
	
		# Header is 20 bytes
		body_offset = padded_scene_len + 20
		body_offset_data = body_offset + 8
		file_len = body_offset_data + padded_body_length
	
		# Write the header
		glb_out = bytearray()
		glb_out.extend(struct.pack('>I', 0x676C5446))		# magic number: "glTF"
		glb_out.extend(struct.pack('<I', 2))
		glb_out.extend(struct.pack('<I', file_len))

		# JSON chunk
		glb_out.extend(struct.pack('<I', padded_scene_len))
		glb_out.extend(struct.pack('<I', 0x4E4F534A))
		glb_out.extend(self.header)

		# Add padding
		while len(glb_out) < body_offset:
			glb_out.extend(' ')
	
		# Write the body
		for i in xrange(0, len(self.body.body_parts), 2):
			offset = self.body.body_parts[i]
			contents = self.body.body_parts[i + 1]
			if offset + body_offset != len(glb_out):
				raise IndexError
			glb_out.extend(contents)
			
		while len(glb_out) < file_len:
			glb_out.extend([0])
	
		return glb_out

def main():
	""" Convert GLTF to GLB"""

	# Parse options and get results
	parser = argparse.ArgumentParser(description='Converts GLTF to GLB')
	parser.add_argument("-e", "--embed", action="store_true", \
						help="Embed textures or shares into binary GLTF file")
	parser.add_argument("-c", "--cesium", action="store_true", \
						help="sets the old body buffer name for compatibility with Cesium [UNNECESSARY - DEPRECATED]")
	parser.add_argument("-i", "--i3dm", type=str, \
	                    help="Export i3dm, with optional path to JSON instance table data")
	parser.add_argument("-b", "--b3dm", type=str, \
	                    help="Export b3dm, with optional path to JSON batch table data")
	parser.add_argument("-o", "--output", required=False, default=None,
	                    help="Optional output path (defaults to the path of the input file")
	parser.add_argument("filename")
	args = parser.parse_args()

	embed = {}
	if args.embed:
		for t in EMBED_ARR:
			embed[t] = True

	# Make sure the input file is *.gltf
	if not args.filename.endswith('.gltf'):
		print("Failed to create binary GLTF file: input is not *.gltf")
		sys.exit(-1)

	with open(args.filename, 'rb') as f:
		gltf = f.read()
	gltf = gltf.decode('utf-8')
	scene = json.loads(gltf)

	# Set up body_encoder
	body_encoder = BodyEncoder(containing_dir = os.path.dirname(args.filename))

	# Iterate the buffers in the scene:
	for buf_id, buf in enumerate(scene["buffers"]):
		buf_type = buf.get("type",None)
		if buf_type and buf_type != 'arraybuffer':
			raise TypeError("Buffer type %s not supported: %s" % (buf_type, buf_id))

		try:
			length = buf["byteLength"]
		except:
			length = None

		offset, length = body_encoder.addToBody(buf["uri"], length)
		
		try:
			buf["extras"]
		except KeyError:
			buf["extras"] = {}
		buf["extras"]["byteOffset"] = offset

	# Iterate over the bufferViews to
	# move buffers into the single GLB buffer body
	for bufview_id, bufview in enumerate(scene["bufferViews"]):
		buf_id = bufview["buffer"]
		try:
			referenced_buf = scene["buffers"][buf_id]
		except KeyError:
			raise KeyError("Buffer ID reference not found: %s" % (buf_id))

		scene["bufferViews"][bufview_id]["buffer"] = 0
		try:
			scene["bufferViews"][bufview_id]["byteOffset"] += referenced_buf["extras"]["byteOffset"]
		except KeyError:
			scene["bufferViews"][bufview_id]["byteOffset"] = referenced_buf["extras"]["byteOffset"]

	# Iterate over the shaders
	if 'shaders' in embed and 'shaders' in scene:
		for shader_id, shader in scene["shaders"].iteritems():
			uri = shader["uri"]
			del scene["shaders"][shader_id]["uri"]

			offset, length = body_encoder.addToBody(uri, None)

			scene["bufferViews"].append({'buffer': 0, 'byteLength': length, 'byteOffset': offset})
			scene["shaders"][shader_id]["bufferView"] = len(scene["bufferViews"])-1

	# Iterate over images
	if 'textures' in embed and 'images' in scene:
		for image_id, image in enumerate(scene["images"]):
			uri = image["uri"]
			del scene["images"][image_id]["uri"]

			offset, length = body_encoder.addToBody(uri, None)
			
			scene["bufferViews"].append({'buffer': 0, 'byteLength': length, 'byteOffset': offset})
			scene["images"][image_id]["bufferView"] = len(scene["bufferViews"])-1
			scene["images"][image_id]["mimeType"] = "image/png"

	scene["buffers"] = [{'byteLength': body_encoder.body_length}];

	new_scene_str = bytearray(json.dumps(scene, separators=(',', ':'), sort_keys=True))
	encoder = GLBEncoder(new_scene_str, body_encoder)
	if args.b3dm != None:
		ext = 'b3dm'
	elif args.i3dm != None:
		ext = 'i3dm'
	else:
		ext = 'glb'
	#print("Exporting %s" % (ext))

	fname_out = os.path.splitext(os.path.basename(args.filename))[0] + '.' + ext
	if None != args.output:
		if "" == os.path.basename(args.output):
			fname_out = os.path.join(fname_out, fname_out)
		else:
			fname_out = args.output
	else:
		fname_out = os.path.join(os.path.dirname(args.filename), fname_out)

	if args.b3dm != None:
		glb = encoder.exportString()
		b3dm_encoder = b3dm.B3DM()
		if len(args.b3dm):
			with open(args.b3dm, 'rb') as f:
				b3dm_json = json.loads(f.read())
				print b3dm_json
				b3dm_encoder.loadJSONBatch(b3dm_json)

		with open(fname_out, 'wb') as f:
			f.write(b3dm_encoder.writeBinary(glb))
	elif args.i3dm != None:
		raise NotImplementedError
	else:
		encoder.export(fname_out)

if __name__ == "__main__":
	main()
