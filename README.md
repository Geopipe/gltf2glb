# gltf2glb
Tools to manipulate GLTF/GLB-containing files such as .b3dm, .i3dm, .pnts, and .cmpt.

Created by Christopher Mitchell, Ph.D. et alia of Geopipe, Inc.

This project was initially intended to provide a GLTF-to-GLB packer, inspired by
the desire to use https://github.com/Qantas94Heavy/binary-gltf-util without running Javascript
as a server-side language. It has evolved to remove its first component (gltf2glb.py), instead
providing the tools shown below to pack and unpack GLTF/GLB files into and out of other containers.

Usage
-----

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
(c) 2016-2021 Geopipe, Inc. and licensed under the BSD 3-Clause license. See LICENSE.
