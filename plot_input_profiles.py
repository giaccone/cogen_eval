# import modules
# -------------

# built-in
import csv
import matplotlib.pyplot as plt
import numpy as np

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



# final plots
h1 = plt.figure(figsize=(8,5))
plt.plot(range(len(Ut)), Ut, 'C0-o')
plt.xlabel("hour", fontsize=18)
plt.ylabel("$U_t$ (kW)", fontsize=18)
plt.xlim(0, 23)
plt.ylim(0, 2500)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.grid()
plt.tight_layout()

h2 = plt.figure(figsize=(8,5))
plt.plot(range(len(cs)), cs, 'C0-o')
plt.xlabel("hour", fontsize=18)
plt.ylabel("$c_s$ (euro/MWh)", fontsize=18)
plt.xlim(0, 23)
plt.ylim(0, 120)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.grid()
plt.tight_layout()

# uncomment next two lines to save the images
# h1.savefig("Ut", dpi=300)
# h2.savefig("cs", dpi=300)
plt.ion()
plt.show()

