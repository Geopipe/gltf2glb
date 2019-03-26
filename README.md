# gltf2glb
GLTF to Binary GLTF (GLB) Converter

Created by Christopher Mitchell, Ph.D. et alia of Geopipe, Inc.

This project was inspired by https://github.com/Qantas94Heavy/binary-gltf-utils and started as a direct Javascript-to-Python port with a bunch of bugfixes. It can create both b3dm and i3dm files for Cesium 3D Tiles. It also includes a `packcmpt` tool for combining one or more `i3dm`/`b3dm` models into a single `cmpt` file.

Usage
-----

### gltf2glb ###
```
$ ./gltf2glb.py -h
usage: gltf2glb.py [-h] [-e] [-c] [-i I3DM] [-b B3DM] [-o OUTPUT] filename

Converts GLTF to GLB

positional arguments:
  filename

optional arguments:
  -h, --help                    show this help message and exit
  -e, --embed                   Embed textures or shares into binary GLTF file
  -c, --cesium                  sets the old body buffer name for compatibility with Cesium [UNNECESSARY - DEPRECATED]
  -i I3DM, --i3dm I3DM          Export i3dm, with optional path to JSON instance table data
  -b B3DM, --b3dm B3DM          Export b3dm, with optional path to JSON batch table data
  -o OUTPUT, --output OUTPUT    Optional output path (defaults to the path of the input file
```

### packcmpt ###
```
$ ./packcmpt.py -h
usage: packcmpt.py [-h] -o OUTPUT input_files [input_files ...]

Packs one or more i3dm and/or b3dm files into a cmpt

positional arguments:
  input_files

optional arguments:
  -h, --help                    show this help message and exit
  -o OUTPUT, --output OUTPUT    Output cmpt file
  -u                            Unpack the output CMPT file instead of creating it (incomplete)
```
### i3dm ###
```
$ ./i3dm.py -h
usage: usage: i3dm.py [-h] -i I3DM -g GLB -o OUTPUT

Generate an i3dm file from JSON describing instances, and a GLB to instance

required arguments:
  -i, --i3dm					JSON for instance semantics
  -g, --glb						Path to GLB file to instance
  -o, --output					Path to i3dm file to output

optional arguments:
  -h, --help                    show this help message and exit

License
-------
(c) 2016-2019 Geopipe, Inc. and licensed under the BSD 3-Clause license. See LICENSE.
