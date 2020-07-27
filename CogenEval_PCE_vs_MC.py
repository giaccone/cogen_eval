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

# CHP data
# --------
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

# Boiler data
# -----------
etab = 0.95
Bmax = 3000
print("Boiler data:\n"
    f"------------\n"
    f"    * etab = {etab}\n"
    f"    * Bmax = {Bmax} (kW)\n")

# economic data
# -------------
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
print("Reading thermal load from 'Ut.csv'")
print("---------------------------------")
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
print("----------------------------------------")
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

fmt = "{:.2f}  {:.2f},  {:.2f}  {:.2f}  {:.2f}\n" * 3 + "{:.2f}  {:.2f},  {:.2f}  {:.2f}  {:.2f}"
print("cs = [" + fmt.format(*cskW) + "] (euro/kWh)\n\n")
cskW = np.array(cskW)



# PCE
# ---

# Wapper to main function
def fun(x, etae=etae, etat=etat, Pmin=Pmin, Pmax=Pmax,
        Ptmin=Ptmin, Ptmax=Ptmax, etab=etab, Bmax=Bmax,cskW=cskW, 
        Hi=Hi, cNGd=cNGd, cNGnd=cNGnd, Deltat=Deltat, Ut=Ut):
    
    
    def inner_fun(xx):
        GlobalCost, _, _, _, _ = find_global_cost(etae, etat, Pmin, Pmax, Ptmin, Ptmax, etab, Bmax, Hi, xx[2]*cskW, xx[0]*cNGd, cNGnd, Deltat, xx[1]*Ut)
        return GlobalCost
    from joblib import Parallel, delayed

    y = Parallel(n_jobs=20, verbose=0)(map(delayed(inner_fun), x))

    return np.array(y)

# generate PCE
order = 10
kind = 'n'
if kind == 'n':
    distrib = ['n', 'n', 'n']
    # param = [[1, 0.5],[1, 0.5],[1, 0.5]]
    param = [[1, 0.1],[1, 0.1],[1, 0.1]]
elif kind == 'u':
    distrib = ['u', 'u', 'u']
    # param = [[0.5, 1.5],[0.5, 1.5],[0.5, 1.5]]
    param = [[0.9, 1.1],[0.9, 1.1],[0.9, 1.1]]


pt = []
mu = []
sigma = []
if kind == 'u':
    levels = range(2, 16)
elif kind == 'n':
    levels = range(2,26)

t1 = timer()
print('Polynomial Chaos Expansion (PCE):')
with Bar('    * progress: ', max=len(levels), suffix='%(percent)d%%') as bar:
    for level in levels:
        poly = pce.PolyChaos(order, distrib, param)

        poly.spectral_projection(fun, level, verbose='n')
        poly.norm_fit()

        pt.append(poly.grid.unique_x.shape[0])
        mu.append(poly.mu)
        sigma.append(poly.sigma)
        bar.next()
t2 = timer()
print("    * elapsed time {:.3f} sec\n".format(t2 - t1))

# import sys
# sys.exit()

# MC
# ---
npt = [5] + list(range(10,310,10))
pt2 = []
mu2 = []
sigma2 = []

print('Monte Carlo (MC):')
with Bar('    * progress: ', max=len(npt), suffix='%(percent)d%%') as bar:
    for n in npt:
        if kind == 'n':
            var1 = np.random.normal(param[0][0], param[0][1], n)
            var2 = np.random.normal(param[1][0], param[1][1], n)
            var3 = np.random.normal(param[2][0], param[2][1], n)
        elif kind == 'u':
            var1 = np.random.uniform(param[0][0], param[0][1], n)
            var2 = np.random.uniform(param[1][0], param[1][1], n)
            var3 = np.random.uniform(param[2][0], param[2][1], n)

        Q = np.concatenate(columnize(*np.meshgrid(var1, var2, var3)), axis=1)
        y = fun(Q)

        MCmu, MCsigma = norm.fit(y)
        pt2.append(y.shape[0])
        mu2.append(MCmu)
        sigma2.append(MCsigma)
        bar.next()
t2 = timer()
print("    * elapsed time {:.3f} sec\n".format(t2 - t1))


# final plot
hf = plt.figure(figsize=(11,6))
plt.subplot(1,2,1)
plt.semilogx(pt, mu,'C0-o', label='PCE')
plt.semilogx(pt2, mu2,'C1-s',ms=5,mfc='none', label='MC')
plt.xlabel('number of evaluations')
plt.ylabel('mean')
plt.legend()
plt.tight_layout()

plt.subplot(1,2,2)
plt.semilogx(pt, sigma,'C0-o', label='PCE')
plt.semilogx(pt2, sigma2,'C1-s',ms=5,mfc='none', label='MC')
plt.xlabel('number of evaluations')
plt.ylabel('standard deviation')
plt.legend()
plt.tight_layout()

plt.ion()
plt.show()

if savedata:
    np.savez("pce_vs_mc_" + kind, pt=pt, pt2=pt2, mu=mu, mu2=mu2, sigma=sigma, sigma2=sigma2)
