import numpy as np
import pickle
from matplotlib import pyplot as plt

f = file("out.pickle","r")
x = pickle.load(f)
f.close() 

for spec in x:
    plt.plot(spec[:,0],spec[:,1],color="red")
#plt.show()


#for arr in x:
#    print (max(arr[:,0])-min(arr[:,0]))/float(arr.shape[0])
#    print arr.shape[0],min(arr[:,0]),max(arr[:,0])



#arr = x[0]

#arr.sort()


numbers = 2000000
base = np.linspace(350,2009.6,num=numbers)
summ = np.zeros_like(base)

for arr in x:
    xp = arr[:,0]
    fp = arr[:,1]
    z = np.interp(base, xp, fp)
    summ += z
    #plt.plot(xp,fp,color="blue")
    #plt.plot(base,z,color="red")
    
#plt.plot(base,summ,color="blue")
#plt.show()
#np.interp(
