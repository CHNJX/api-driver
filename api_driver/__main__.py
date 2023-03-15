import sys
from os.path import dirname

sys.path.append(dirname(sys.path[0]))
from api_driver.command import cmd

cmd()
