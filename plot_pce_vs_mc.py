# import modules
# -------------

# built-in
import matplotlib.pyplot as plt
import numpy as np

# load data
kind = 'u'
if kind == 'n':
    data = np.load("pce_vs_mc_n.npz")
    y_lim = [550, 680]
    a_lim = [0.75, 0.47, 0.23, 0.30]
elif kind == 'u':
    # data = np.load("pce_vs_mc_uni.npz")
    data = np.load("pce_vs_mc_u.npz")
    y_lim = [80, 110]
    a_lim = [0.75, 0.32, 0.23, 0.45]

pt = data['pt']
pt2 = data['pt2']
mu = data['mu']
mu2 = data['mu2']
sigma = data['sigma']
sigma2 = data['sigma2']


# final plot
hf = plt.figure(figsize=(15,6))
plt.subplot(1,2,1)
plt.semilogx(pt2, mu2,'C1-s',ms=5,mfc='none', label='MC')
plt.semilogx(pt, mu,'C0-o', label='PCE')
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.xlabel('number of evaluations', fontsize=16)
plt.ylabel('mean', fontsize=16)
plt.legend(fontsize=16)
plt.tight_layout()

plt.subplot(1,2,2)
plt.semilogx(pt2, sigma2,'C1-s',ms=5,mfc='none', label='MC')
plt.semilogx(pt, sigma,'C0-o', label='PCE')
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.xlabel('number of evaluatins', fontsize=16)
plt.ylabel('standard deviation', fontsize=16)
plt.legend(fontsize=16)
plt.tight_layout()

ax3 = hf.add_axes(a_lim)
ax3.semilogx(pt2, sigma2,'C1-s',ms=5,mfc='none', label='MC')
ax3.semilogx(pt, sigma,'C0-o', label='PCE')
ax3.set_ylim(*y_lim)
ax3.set_xlabel('number of evaluatins')
ax3.set_ylabel('standard deviation')
ax3.set_title('saturation of y-axis in the range {} - {}'.format(*y_lim))

# uncomment next line to save the image
# hf.savefig("pce_vs_mc_" + kind, dpi=300)
plt.ion()
plt.show()

