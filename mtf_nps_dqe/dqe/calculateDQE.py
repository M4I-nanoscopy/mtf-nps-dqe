import argparse
import os.path

import matplotlib.pyplot as plt
import numpy as np


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('--mtf', type=str, required=True, help='Input measured MTF curve (.npz file)')
    parser.add_argument('--nps', type=str, required=True, help='Input measured NPS curve (.npz file)')
    parser.add_argument('--dqe0', type=float, default=0.95, help='Assumed DQE(0)')
    parser.add_argument('--store', default=None, type=str, help='Store output measured DQE curve')
    parser.add_argument('--name', type=str, help='Label to store with measured DQE curve (default basename of file)')

    settings = parser.parse_args()

    return settings


def theoretical_dqe(w):
    with np.errstate(divide='ignore', invalid='ignore'):
        return sinc_squared(np.math.pi * w / 2)


def sinc_squared(w):
    return (np.sin(w) ** 2) / (w ** 2)


config = parse_arguments()

if not config.name:
    if config.store:
        name = os.path.basename(config.store)
    else:
        name = "MTF: %s, NPS: %s" % (os.path.basename(config.mtf), os.path.basename(config.nps))
else:
    name = config.name

# Load data
mtf = np.load(config.mtf)
nps = np.load(config.nps)
mtf_freq_w = mtf['w']
mtf_meas = mtf['mtf']
nps_freq_w = nps['w']
nps_meas = nps['nps']


# Interpolate the MTF to match the frequency of the NPS measurement
mtf_meas_inter = np.interp(nps_freq_w, mtf_freq_w, mtf_meas)

# Calculate DQE
dqe_meas = np.divide(np.square(mtf_meas_inter), nps_meas) * config.dqe0
mtf_squared = np.square(mtf_meas_inter)

plt.plot(nps_freq_w, nps_meas, label='NPS')
plt.plot(nps_freq_w, mtf_meas_inter, label='MTF')
plt.plot(nps_freq_w, dqe_meas, label='DQE')
plt.plot(nps_freq_w, mtf_squared, label='MTF^2')
plt.plot(nps_freq_w, theoretical_dqe(nps_freq_w), '--', color='black', label='Theoretical DQE')

plt.legend()
plt.xlim([0, 1.0])
plt.ylim([0, 1.1])
plt.xlabel("Spatial frequency (fraction of Nyquist)")
plt.title(name)
plt.grid()
plt.gca().set_aspect('equal', adjustable='box')
plt.show()

if config.store is not None:
    np.savez(config.store, w=nps_freq_w, dqe=dqe_meas, label=name)


# TODO: This is not a very clean way around the fact that this script should be refactored
def main():
    pass


if __name__ == "__main__":
    main()