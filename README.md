# gltf2glb
GLTF to Binary GLTF (GLB) Converter

Created by Christopher Mitchell, Ph.D. et alia of Geopipe, Inc.

This project was inspired by https://github.com/Qantas94Heavy/binary-gltf-utils and started as a direct Javascript-to-Python port with a bunch of bugfixes. It will also soon implement `b3dm` and `i3dm` headers for Cesium 3D Tiles.

Usage:
------
    ./gltf2glb.py [-e|--embed] [-c|--cesium] input_file
`-e|--embed`: Embed shaders and textures in the GLB file, even if not already embedded.
`-c|--cesium`: Use the binary buffer name `KHR_binary_glTF` for compatibility with Cesium.

License:
--------
(c) 2016 Geopipe, Inc. and licensed under the BSD 3-Clause license. See LICENSE.
