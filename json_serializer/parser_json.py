from . import exception_objects as excp

import json
import inspect
import copy
import types

__built_in_types_encode__ = {list().__class__: "_encode_list",
                             tuple().__class__: "_encode_tuple",
                             dict().__class__: "_encode_dict",
                             set().__class__: "_encode_set",
                             frozenset().__class__: "_encode_frozenset"}

__built_in_types_decode__ = {str(list().__class__): "_decode_list",
                             str(tuple().__class__): "_decode_tuple",
                             str(dict().__class__): "_decode_dict",
                             str(set().__class__): "_decode_set",
                             str(frozenset().__class__): "_decode_frozenset"}


def set_type(cls):
    if not cls.startswith("<class"):
        raise ValueError("Not a class string")
    cls = cls.replace("'", "")
    cls = cls.replace("<class ", "")
    cls = cls.replace(">", "")
    module_name = cls.split('.')[0]
    for subname in cls.split('.')[1:-1]:
        module_name += '.' + subname
    cls_name = cls.split('.')[-1]
    return getattr(__import__(module_name, fromlist=[""]), cls_name)


def readfile(file_path):
    f_json = open(file_path, 'r')
    str_json = json.load(f_json)
    f_json.close()
    result = decode(str_json)
    return result


def writefile(file_path, obj):
    str_json = encode(obj)
    f_json = open(file_path, 'w')
    json.dump(str_json, fp=f_json, sort_keys=True, indent=4)
    f_json.close()
    return


def decode(input_json, *args):
    if args:
        input_obj = args[0]
    else:
        input_obj = 'None'
    if not isinstance(input_json, dict):
        result = input_json
        return result
    result = copy.deepcopy(input_obj)
    for key in input_json.keys():
        func_name = __built_in_types_decode__.get(key)
        if func_name:
            result = globals()[func_name](input_json[key])
            return result
        func_name = excp.__exceptions_decode__.get(key)
        if func_name:
            result = getattr(excp, func_name)(input_json[key])
            return result
        try:
            cls = set_type(key)
            cls = cls()
            result = decode(input_json[key], cls)
        except ValueError:
            if isinstance(getattr(input_obj, key), property):
                continue
            if isinstance(getattr(input_obj, key), types.FunctionType):
                continue
            setattr(result, key, decode(input_json[key], getattr(input_obj, key)))
    return result


def encode(input_obj, set_class=True):
    func_name = __built_in_types_encode__.get(input_obj.__class__)
    if func_name:
        result = globals()[func_name](input_obj)
        return result
    func_name = excp.__exceptions_encode__.get(input_obj.__class__)
    if func_name:
        result = getattr(excp, func_name)(input_obj)
        return result
    class_dict = inspect.getmembers(input_obj)
    result = dict()
    for attr in class_dict:
        attr_tmp = [attr[0], attr[1]]
        try:
            try:
                if isinstance(getattr(type(input_obj), attr_tmp[0]), property):
                    continue
            except AttributeError:
                pass
            if isinstance(getattr(input_obj, attr_tmp[0]), types.FunctionType):
                continue
            if isinstance(attr[1], types.BuiltinFunctionType):
                continue
            if isinstance(attr[1], types.BuiltinMethodType):
                continue
            if isinstance(attr[1], types.MethodType):
                continue
            if isinstance(attr[1], types.GetSetDescriptorType):
                continue
            if isinstance(attr[1], types.MemberDescriptorType):
                continue
            if attr_tmp[0].startswith('__') and \
                    attr_tmp[0].endswith('__') and \
                    not attr_tmp[0] == '__class__':
                continue
            try:
                json.dumps(attr_tmp[1])
            except TypeError:
                if attr_tmp[0] == '__class__' and not set_class:
                    continue
                if attr_tmp[0] == '__class__' and set_class:
                    attr_tmp[0] = str(attr_tmp[1])
                    attr_tmp[1] = encode(input_obj, set_class=False)
                    result.update({attr_tmp[0]: attr_tmp[1]})
                    break
                attr_tmp[1] = encode(attr_tmp[1])
            result.update({attr_tmp[0]: attr_tmp[1]})
        except AttributeError:
            continue
    return result


def _encode_list(input_list):
    result = dict()
    key = str(list().__class__)
    value = list()
    for input_cur in input_list:
        value.append(encode(input_cur))
    result.update({key: value})
    return result


def _decode_list(input_json):
    result = list()
    for input_cur in input_json:
        result.append(decode(input_cur))
    return result


def _encode_tuple(input_tuple):
    result = dict()
    key = str(tuple().__class__)
    value = list()
    for input_cur in input_tuple:
        value.append(encode(input_cur))
    result.update({key: value})
    return result


def _decode_tuple(input_json):
    value_tmp = list()
    for input_cur in input_json:
        value_tmp.append(decode(input_cur))
    result = tuple(value_tmp)
    return result


def _encode_dict(input_dict):
    result = dict()
    key = str(dict().__class__)
    encoded_dict = dict()
    for key in input_dict.keys():
        value_tmp = encode(input_dict[key])
        key_tmp = encode(key)
        encoded_dict.update({key_tmp: value_tmp})
    result.update({key: encoded_dict})
    return result


def _decode_dict(input_json):
    result = dict()
    for key in input_json.keys():
        value_tmp = decode(input_json[key])
        key_tmp = decode(key)
        result.update({key_tmp: value_tmp})
    return result


def _encode_set(input_set):
    result = dict()
    key = str(set().__class__)
    value = list()
    for input_cur in input_set:
        value.append(encode(input_cur))
    result.update({key: value})
    return result


def _decode_set(input_json):
    value_tmp = list()
    for input_cur in input_json:
        value_tmp.append(decode(input_cur))
    result = set(value_tmp)
    return result


def _encode_frozenset(input_frozenset):
    result = dict()
    key = str(frozenset().__class__)
    value = list()
    for input_cur in input_frozenset:
        value.append(encode(input_cur))
    result.update({key: value})
    return result


def _decode_frozenset(input_json):
    value_tmp = list()
    for input_cur in input_json:
        value_tmp.append(decode(input_cur))
    result = frozenset(value_tmp)
    return result
