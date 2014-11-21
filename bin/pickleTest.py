
import pyopenms
exp = pyopenms.MSExperiment()

"""
from multiprocessing import Pipe
i,o = Pipe()
i.send(exp)
x = o.recv()
x.size()
"""

import json

f = file("test.pickle","w")

json.dump(exp,f)

f.close()
