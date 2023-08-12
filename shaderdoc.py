#!/usr/bin/env python3

import json
import argparse
from typing import TypedDict, List
from io import TextIOWrapper
import re
import os

omitted_example = ['$flags', '$flags_defined', '$flags2', '$flags_defined2']
omitted = ['$flags_defined', '$flags_defined2']

# Internal shaders that shouldn't be documented
omitted_shaders = [
    'blurfilter.*', 'bufferclearobeystencil.*', 'debug.*',
    'depthwrite', 'downsample.*', 'fillrate', 'panorama.*',
    'particlesphere.*', 'writestencil.*', 'writez', 'showz',
    'yuvtorgb'
]

class ShaderParamType(TypedDict):
    name: str
    desc: str
    type: str
    default: str

class ShaderType(TypedDict):
    name: str
    params: List[ShaderParamType]


class Shader:
    def __init__(self, desc: ShaderType):
        self.params = desc['params']
        self.name = desc['name']
    

    def _emit_param(self, param: ShaderParamType, stream: TextIOWrapper) -> None:
        if param['name'] in omitted:
            return
        stream.write(f'### `{param["name"].lower()}` \\<{param["type"]}\\>\n\n')
        stream.write(f'Default: `{param["default"]}`\n\n')
        stream.write(f'{param["desc"]}\n\n')
        

    def _emit_example(self, stream: TextIOWrapper) -> None:
        stream.write(f'```\n{self.name}\n{{\n')
        for p in self.params:
            if p['name'] in omitted_example:
                continue
            stream.write(f'\t{p["name"].lower():20} "{p["default"]}"\n')
        stream.write("}\n```\n\n")


    def _emit_params(self, stream: TextIOWrapper) -> None:
        for param in self.params:
            self._emit_param(param, stream)
        

    def emit_docs(self, stream: TextIOWrapper) -> None:
        stream.write(f'---\nlayout: default\ntitle: {self.name}\nparent: Shaders\n---\n\n')
        stream.write(f'# {self.name}\n\n## Parameters\n\n')
        self._emit_params(stream)
        stream.write('## Example\n\n')
        self._emit_example(stream)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', required=True, help='File to generate off of')
    parser.add_argument('-o', required=True, help='Directory to output data to')
    args = parser.parse_args()

    j = {}
    with open(args.i, 'rb') as fp:
        j = json.load(fp)
    
    try:
        os.makedirs(args.o)
    except:
        pass

    shaders = []
    for s in j:
        if any([re.match(x, s['name'].lower()) for x in omitted_shaders]):
            print(f'Skipping {s["name"]}')
            continue
        shader = Shader(s)
        with open(f'{args.o}/{shader.name}.md', 'w') as fp:
            shader.emit_docs(fp)
