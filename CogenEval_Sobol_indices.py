# import modules
# -------------

# built-in
import csv
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
from progress.bar import Bar
from timeit import default_timer as timer
# user
from cogen_util import find_global_cost
import pce as pce
from pce.quad4pce import columnize

# savedata flag (set to true to save the simulation in npz format)
savedata = False

# PARAMETERS
# ----------
power_graph = True
case_graph=1

# CHP
etae = 0.33
etat = 0.4
Pmin = 600
Pmax = 1000

print("CHP data:\n"
    f"---------\n"
    f"    * etae = {etae}\n"
    f"    * etat = {etat}\n"
    f"    * Pmin = {Pmin} (kW)\n"
    f"    * Pmax = {Pmax} (kW)\n")

Ptmin = Pmin / etae * etat
Ptmax = Pmax / etae * etat

# Boiler
etab = 0.95
Bmax = 3000

print("Boiler data:\n"
    f"------------\n"
    f"    * etab = {etab}\n"
    f"    * Bmax = {Bmax} (kW)\n")

# economic data
cNGd = 0.242 # cost of Natural Gas without tax (euro/SMC)
delta_tax = 0.008
cNGnd = cNGd + delta_tax # cost of Natural Gas with tax (euro/SMC)
Hi = 9.59 # Lower Heating Value (kWh/SMC)
print("Natural gas cost\n"
    f"    * for CHP = {cNGd} (euro/SMC)\n"
    f"    * for boiler = {cNGnd} (euro/SMC)\n"
    f"    * lower heating value = {Hi} (kWh/SMC)\n")

# interval set to 1 hour
# ----------------------
Deltat = 1
print("integration time = {} (h)\n".format(Deltat))


# read csv file containing thermal load Ut (kWt)
# ----------------------------------------------
print("Reading electricity prices from 'cs.csv'")
print("----------------------------------------")
Ut = []
with open('UtAL.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for line_count, row in enumerate(csv_reader):
        if line_count == 0:
            print(f'    * Column names are {", ".join(row)}')
        else:
            Ut.append(float(row[1]))
    print(f'    * processed {line_count} lines.')

fmt = "{:.2f}  {:.2f},  {:.2f}  {:.2f}  {:.2f}\n" * 3 + "{:.2f}  {:.2f},  {:.2f}  {:.2f}  {:.2f}"
print("Ut = [" + fmt.format(*Ut) + "] (kW)\n")
Ut = np.array(Ut)

# read csv file containing electricity prices cs (euro/MWh)
# ---------------------------------------------------------
print("Reading electricity prices from 'cs.csv'")
cs = []
with open('cs.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for line_count, row in enumerate(csv_reader):
        if line_count == 0:
            print(f'    * column names are {", ".join(row)}')
        else:
            cs.append(float(row[1]))
    print(f'    * processed {line_count} lines.')

fmt = "{:.2f}  {:.2f},  {:.2f}  {:.2f}  {:.2f}\n" * 3 + "{:.2f}  {:.2f},  {:.2f}  {:.2f}  {:.2f}"
print("cs = [" + fmt.format(*cs) + "] (euro/MWh)\n")
cs = np.array(cs)

# convert price from euro/MWh to euro/kWh
cskW=[]
for element in cs:
    cskW.append(element/1000)

fmt = "{:.4f}  {:.4f},  {:.4f}  {:.4f}  {:.4f}\n" * 3 + "{:.4f}  {:.4f},  {:.4f}  {:.4f}  {:.4f}"
print("cskW = [" + fmt.format(*cskW) + "] (euro/kWh)\n\n")
cskW = np.array(cskW)


# PCE
# ---

# Wapper
def fun(x, etae=etae, etat=etat, Pmin=Pmin, Pmax=Pmax,
        Ptmin=Ptmin, Ptmax=Ptmax, etab=etab, Bmax=Bmax,cskW=cskW, 
        Hi=Hi, cNGd=cNGd, cNGnd=cNGnd, Deltat=Deltat, Ut=Ut):
    
    
    def inner_fun(xx):
        GlobalCost, _, _, _, _ = find_global_cost(etae, etat, Pmin, Pmax, Ptmin, Ptmax, etab, Bmax, Hi, xx[2]*cskW, xx[0]*cNGd, cNGnd, Deltat, xx[1]*Ut)
        return GlobalCost
    from joblib import Parallel, delayed

    y = Parallel(n_jobs=-1, verbose=0)(map(delayed(inner_fun), x))

    return np.array(y)



# generate PCE
orders = range(2,20,2)
index = [[1], [2], [3], [1,2], [1,3], [2,3], [1,2,3]]
S = np.zeros(( len(index), len(orders)))
kind = 'n'
if kind == 'n':
    distrib = ['n', 'n', 'n']
    param = [[1, 0.05],[1, 0.05],[1, 0.05]]
elif kind == 'u':
    distrib = ['u', 'u', 'u']
    param = [[0.9, 1.1],[0.9, 1.1],[0.9, 1.1]]

mu = []
sigma = []

t1 = timer()
print('Sobol index computation at increasing PCE order:')
with Bar('    * progress: ', max=len(orders), suffix='%(percent)d%%') as bar:
    for k, order in enumerate(orders):
        # generate PCE
        poly = pce.PolyChaos(order, distrib, param)

        # level selected according to simulation PCE vs MC
        if kind == 'u':
            lev = 15
        elif kind == 'n':
            lev = 25
        # compute coefficients
        poly.spectral_projection(fun, lev, verbose='n')
        poly.norm_fit()
        mu.append(poly.mu)
        sigma.append(poly.sigma)
        sobol_index = poly.sobol(index)
        S[:, k] = np.array(sobol_index)
        bar.next()
t2 = timer()
print("    * elapsed time {:.3f} sec\n".format(t2 - t1))

# print first line
first_line = "order & " + " & ".join([str(k) for k in orders]) + " \\\\"
print(first_line)
# print sobol index
for idx, sobol, in zip(index, S):
    format_str = "".join([str(ele) for ele in idx])
    format_str = "S" + format_str
    format_str = format_str  + " & {:.4f}"*len(sobol) + " \\\\"
    print(format_str.format(*sobol))

# final plots
h1 = plt.figure()
plt.plot(range(len(Ut)), Ut, 'C0-o')
plt.xlabel("hour", fontsize=14)
plt.ylabel("Ut (kW)", fontsize=14)
plt.grid()
plt.tight_layout()

h2 = plt.figure()
plt.plot(range(len(cskW)), cskW, 'C0-o')
plt.xlabel("hour", fontsize=14)
plt.ylabel("cskW (euro/kWh)", fontsize=14)
plt.grid()
plt.tight_layout()


h3 = plt.figure(figsize=(11,6))
plt.subplot(1,2,1)
plt.plot(orders, mu,'C0-o', label='PCE')
plt.xlabel('order')
plt.ylabel('mean')
plt.legend()
plt.tight_layout()

plt.subplot(1,2,2)
plt.plot(orders, sigma,'C0-o', label='PCE')
plt.xlabel('order')
plt.ylabel('standard deviation')
plt.legend()
plt.tight_layout()

plt.ion()
plt.show()

# save data reletd to higher degree PCE
if savedata:
    SI = S[:, -1]
    np.savez("sobol_" + kind, sobol_index=SI)


