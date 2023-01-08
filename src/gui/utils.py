import os

_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))


def resource_filepath(filename):
    return os.path.join(_ROOT_PATH, "data", filename)
