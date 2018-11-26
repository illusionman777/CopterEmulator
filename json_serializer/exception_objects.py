import numpy as py
import pyquaternion as pyqn


__exceptions_encode__ = {type(py.array([])): "encode_ndarray",
                         type(py.matrix([])): "encode_matrix",
                         type(pyqn.Quaternion()): "encode_quaternion"}

__exceptions_decode__ = {str(type(py.array([]))): "decode_ndarray",
                         str(type(py.matrix([]))): "decode_matrix",
                         str(type(pyqn.Quaternion())): "decode_quaternion"}


def encode_ndarray(input_array):
    result = dict()
    key = str(type(py.array([])))
    value = input_array.tolist()
    result.update({key: value})
    return result


def decode_ndarray(input_json):
    result = py.array(input_json)
    return result


def encode_matrix(input_matrix):
    result = dict()
    key = str(type(py.matrix([])))
    value = input_matrix.tolist()
    result.update({key: value})
    return result


def decode_matrix(input_json):
    result = py.matrix(input_json)
    return result


def encode_quaternion(input_quaternion):
    result = dict()
    key = str(type(pyqn.Quaternion()))
    value = input_quaternion.elements.tolist()
    result.update({key: value})
    return result


def decode_quaternion(input_json):
    result = pyqn.Quaternion(input_json)
    return result
