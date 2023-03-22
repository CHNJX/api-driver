# -*- coding:utf-8 -*-
# @Time     :2023/1/30 6:32 下午
# @Author   :CHNJX
# @File     :loader_swagger.py
# @Desc     :
import json
from os import path, listdir
from os.path import isdir

import six
import yaml


def get_loader(filename):
    if filename.endswith(('.json', '.yml', '.yaml')):
        loader = json.load if filename.endswith('.json') else yaml.load
    else:
        with open(filename, 'r', 'utf-8') as f:
            contents = f.read().strip()
            loader = json.load if contents[0] in ['{', '['] else yaml.load
    return loader


def modify_spec_data(field, spec_data, data):
    if not isinstance(spec_data, dict) or not isinstance(data, dict):
        return None
    for k, v in data.items():
        if k in spec_data[field]:
            spec_data[field][k].update(v)
        else:
            spec_data[field][k] = v


def get_ref_filepath(filename, ref_file):
    ref_file = path.normpath(path.join(path.dirname(filename), ref_file))
    return ref_file


def load_file(filename, spec_data):
    loader = get_loader(filename)
    with open(filename, 'r', encoding='utf-8') as f:
        data = loader(f) if filename.endswith('.json') else loader(f, yaml.Loader)
        spec_data.update(data)
        for field, values in six.iteritems(data):
            if field not in ['definitions', 'parameters', 'paths'] or not isinstance(values, dict):
                continue
            for _field, value in six.iteritems(values):
                if _field == '$ref' and value.endswith('.yml'):
                    _filepath = get_ref_filepath(filename, value)
                    field_data = load_swagger(_filepath)
                    spec_data[field] = field_data
                elif '$ref' in value:
                    v = value.pop('$ref', '')
                    if not v:
                        continue
                    _filepath = get_ref_filepath(filename, v)
                    field_data = load_swagger(_filepath)
                    modify_spec_data(field, spec_data, field_data)


def load_swagger(filename):
    spec_data = {}
    files = listdir(filename) if isdir(filename) else [filename]
    for f in files:
        if f != filename:
            f = filename + '/' + f
        load_file(f, spec_data)
    return spec_data
