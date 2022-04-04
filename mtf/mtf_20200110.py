import csv
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm

plt.rcParams.update({
    "font.size": 12,
    "font.family": 'sans-serif',
    "svg.fonttype": 'none',
    "lines.linewidth": 3
})

energy = sys.argv[1]


def theoretical_mtf():
    x = np.arange(0.0001, 1, 0.01)

    y = np.sin(np.pi * x) / (np.pi * x)

    return x, y


def plot_mtf(filename, label, fmt, color, freq=1):
    with np.load(filename) as data:
        mtf = data['mtf']
        u = data['u']

        u = u * freq

        plt.plot(u, mtf[1], label=label, color=color, dashes=fmt)

        plt.fill_between(u, mtf[0], mtf[2], color=color, alpha=0.1, rasterized=True)


def plot_published_mtf(filename, column_x, column_y, freq, label, fmt, color):
    with open(filename, 'r') as csvfile:
        # Skip header
        next(csvfile, None)

        d = list(csv.reader(csvfile, delimiter=' '))

        x = list()
        y = list()

        for row in d:
            x.append(float(row[column_x]))
            y.append(float(row[column_y]))

        u = np.array(x) * freq

        plt.plot(u, np.array(y), label=label, color=color, dashes=fmt)


# Setup
plt.figure(figsize=(7, 7))
plt.ylim((0, 1.0))
plt.xlim((0, 0.5))
plt.grid()
plt.ylabel('MTF')

# Colors
color = cm.Set1(np.linspace(0, 1, 8))

# Plots
x, y = theoretical_mtf()
plt.plot(x, y, '--', label="Ideal", color='black')

plot_mtf('data/mtf/erik_frodjh_20200110/timepix-' + energy + 'kv-clusters.npz', 'Unprocessed', (None, None), 'black')
# plot_mtf('data/mtf/erik_frodjh_20200110/timepix-'+energy+'kv-random.npz', 'Random', (2,2), color[0])
# plot_mtf('data/mtf/erik_frodjh_20200110/timepix-'+energy+'kv-centroid.npz', 'Centroid', (5,2), color[1])
# plot_mtf('data/mtf/erik_frodjh_20200110/timepix-'+energy+'kv-highest_toa.npz', 'Highest-ToA', (5,2), color[2])
# plot_mtf('data/mtf/erik_frodjh_20200110/timepix-'+energy+'kv-highest_tot.npz', 'Highest-ToT', (5,2), color[3])
plot_mtf('data/mtf/erik_frodjh_20200110/timepix-' + energy + 'kv-cnn-tot.npz', 'CNN ToT', (None, None), color[4])
plot_mtf('data/mtf/erik_frodjh_20200110/timepix-' + energy + 'kv-cnn-tottoa.npz', 'CNN ToT+ToA', (None, None), color[5])
plot_mtf('data/mtf/erik_frodjh_20200110/timepix-' + energy + 'kv-cnn-tot-sr.npz', 'CNN ToT Super Resolution', (1, 1),
         color[7], freq=2)

plot_published_mtf('data/published/mtf_f3ec_200kv.star', 0, 1, 1, "Published Falcon III EC (200 kV)", (1, 1), color[0])
# plot_published_mtf('data/published/mtf_f3ec_300kv.star', 0, 1, 1, "Published Falcon III EC (300 kV)", (1,1), color[1])

plt.legend(loc='lower left')

plt.xticks([0, 0.1, 0.2, 0.3, 0.4, 0.5], [0, 0.2, 0.4, 0.6, 0.8, 1])
plt.xlabel("Spatial Frequency (fraction of Nyquist)")
# plt.xlabel(r'Spatial Frequency (1/$\omega$)')

# Create secondary axis for fraction of Nyquist
# axes2 = axes1.twiny()
# axes2.set_xticks([0, 0.1, 0.2, 0.3, 0.4, 0.5])
# axes2.set_label(r'Spatial Frequency (1/$\omega$)')

if len(sys.argv) > 2:
    plt.savefig(sys.argv[2], bbox_inches='tight', pad_inches=0.1)

plt.show()
