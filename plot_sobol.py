# import modules
# --------------
import numpy as np
import matplotlib.pyplot as plt

# load sobol data from simulations
data = np.load("sobol_u.npz")
sobol_uni = data["sobol_index"]
data = np.load("sobol_n.npz")
sobol_norm = data["sobol_index"]

# make plot
index = np.arange(len(sobol_norm))

hf = plt.figure(figsize=(8,5))
p1 = plt.bar(index - 0.35/2, sobol_uni, 0.35, label='uniform')
p2 = plt.bar(index + 0.35/2, sobol_norm, 0.35, label='normal')
plt.grid()
plt.ylabel("Sobol' indices", fontsize=18)
plt.xticks(index, ('$S_1$', '$S_2$', '$S_3$',
                   '$S_{12}$', '$S_{13}$', '$S_{23}$', '$S_{123}$'),fontsize=14)
plt.yticks(fontsize=16)
plt.legend(fontsize=16)
plt.tight_layout()

# uncomment next line to save the image
# hf.savefig("sobol_comparison", dpi=300)
plt.ion()
plt.show()