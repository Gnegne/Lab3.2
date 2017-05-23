"""Tipo roba."""

import sys, os
folder = os.path.realpath('..')
sys.path.append(os.path.join(os.path.realpath('..\..'), '0_Valerio_Utilities', 'Python'))
import numpy as np, matplotlib.pyplot as plt, matplotlib as mpl
from lab import *
from iandons import *

# ******* mpl setup
mpl.rcParams['errorbar.capsize'] = 0
mpl.rcParams['xtick.direction'] = 'in'
mpl.rcParams['ytick.direction'] = 'in'
mpl.rcParams['xtick.top'] = True
mpl.rcParams['ytick.right'] = True
mpl.rcParams['lines.linewidth'] = 1.0

# passabanda
filename = "dati_passabanda.txt"
rawdata = np.loadtxt(os.path.join(folder, 'Data', filename)).T

f = rawdata[0] * 1e3
df = f / 1e3
g = rawdata[2] / rawdata[1]
g = 20*np.log10(g)
dg = np.sqrt(mme(rawdata[1], 'volt', 'oscil')**2 / rawdata[1]**2 + mme(rawdata[2], 'volt', 'oscil')**2 / rawdata[2]**2)*20*np.log10(np.e)


def bandgain(w, a, w0, l):
	return a * w / np.sqrt((w**2 - w0**2)**2 + w**2 * w0**2 / l**2)


def bandpass(w, a, w0, l):
	return np.log10(bandgain(w, a, w0, l)) * 20


def _dband(w, a, w0, l):
	return -a * (w - w0**2/w) * (1 + w0**2/w**2) / ((w**2 - w0**2)**2/w**2 + w0**2 / l**2)**(3/2)


bandpass.deriv = lambda w, a, w0, l: 20 * np.log10(np.e) * _dband(w, a, w0, l) / bandgain(w, a, w0, l)
bandpass.pars = [1e3, 6e3, 10]

w = DataHolder(f, g, df, dg)
w.x.type = 'log'
<<<<<<< HEAD
w.fit_generic(bandpass)
w.draw(bandpass, resid=True)
=======
#w.draw()
>>>>>>> 853ec9dd963da0a5968350c086321daea26c56c9

# *** amplificazioni ***
amplis = [[], [], []]
errs = [[], [], []]
freq = 1e3
idx = [
	['', 1, 2],
	['', 1, 2],
	[1, 2, 3]
]
names = ['preamp', 'preampb', 'postampo']
parter = .987/1031
perror = mme(987, 'ohm')**2/987**2 + mme(1031e3, 'ohm')**2/1031e3**2

for j in range(3):
	name = names[j]
	for i in idx[j]:
		f = createwave(pars=[freq*2*np.pi, 1, 0, 0])
		h = createwave(pars=[freq*2*np.pi, 1, 0, 0])
		filo = '{}{}.csv'.format(name, i)
		a, b = data_from_oscill(os.path.join(folder, 'Data', filo))
		a.fit_generic(f, verbose=False)
		b.fit_generic(h, verbose=False)
		if j == 0:
			G = np.abs(h.pars[1]/f.pars[1]/parter)
			e = f.cov[1, 1]/f.pars[1]**2 + h.cov[1, 1]/h.pars[1]**2 + perror
		elif j == 1:
			G = np.abs(f.pars[1]/h.pars[1])
			e = f.cov[1, 1]/f.pars[1]**2 + h.cov[1, 1]/h.pars[1]**2
		else:
			G = np.abs(h.pars[1]/f.pars[1])
			e = f.cov[1, 1]/f.pars[1]**2 + h.cov[1, 1]/h.pars[1]**2
		e = G * np.sqrt(e)
		amplis[j].append(G)
		errs[j].append(e)

amplis = np.array(amplis)
errs = np.array(errs)
print('Preamp stadio a:', *xe(amplis[0], errs[0]))
print('Preamp stadio b:', *xe(amplis[1], errs[1]))
print('Postamp:', *xe(amplis[2], errs[2]), '\n')

# rumore
filename = "dati_rummore.txt"
rawdata = np.loadtxt(os.path.join(folder, 'Data', filename)).T

r = rawdata[0] * 1e3
n = rawdata[1]
dn = rawdata[2]
dr = mme(r, 'ohm')


def noiso(R, Vn, Rt, Rn):
	return Vn * np.sqrt(1 + R/Rt + (R/Rn)**2)


noiso.deriv = lambda R, Vn, Rt, Rn: Vn/(2 * np.sqrt(1 + R/Rt + (R/Rn)**2)) * (1/Rt + 2*R/Rn**2)
noiso.pars = [1, 1e3, 1e3]

kb = DataHolder(r, n, dr, dn)
kb.fit_generic(noiso)
#kb.draw(noiso, resid=True)

print(fit_norm_cov(noiso.cov))
Vn, Rt, Rn = noiso.pars

Atot = 1e5
band = 1e3
boltzmann = Vn**2 / (4 * Rt * 300 * Atot**2 * band)
print(boltzmann)

plt.show()
