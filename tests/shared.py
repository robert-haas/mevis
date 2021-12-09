import inspect
import os

import mevis as mv


def get_path_of_this_file():
    # https://stackoverflow.com/questions/2632199/how-do-i-get-the-path-of-the-current-executed-file-in-python
    return os.path.abspath(inspect.getsourcefile(lambda _: None))


TESTFILE_DIR = os.path.dirname(get_path_of_this_file())
IN_DIR = os.path.join(TESTFILE_DIR, 'in')


def load_moses_atomspace():
    filename = 'moses.scm'
    filepath = os.path.join(IN_DIR, filename)
    atomspace = mv.load(filepath)
    return atomspace
