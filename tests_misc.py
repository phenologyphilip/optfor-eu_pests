"""
Testing basic Python code before implementing it in grown-up scripts
"""
import numpy as np

eft1_x = np.empty

print("eft1_x, when initialised:",eft1_x)

eft1_x = np.append(eft1_x,2)

print("eft1_x, after 1 append:",eft1_x)

eft1_x = np.append(eft1_x,3)

print("eft1_x, after 2 appends:",eft1_x)

eft1_x = np.delete(eft1_x,0)

print("eft1_x, after deleting 1:",eft1_x)

placeholder = np.array([1,2,3])

np.savetxt("testing.txt", placeholder)