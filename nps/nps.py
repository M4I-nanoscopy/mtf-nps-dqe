import argparse
import csv
import os.path

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas

plt.rcParams.update({
    "font.size": 12,
    "font.family": 'sans-serif',
    "svg.fonttype": 'none',
    "lines.linewidth" : 3
})

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('--input', nargs='+', type=str, required=True, help='Input measured NPS curves (can be multiple)')

    return parser.parse_args()


def load_nps(f):
    d = np.load(f)
    return d['w'], d['nps']


config = parse_arguments()

for input_f in config.input:
    w, nps = load_nps(input_f)

    plt.plot(w, nps, label=os.path.basename(input_f))


plt.legend()
plt.xlim([0, 1.0])
plt.ylim([0, 1.1])
plt.xlabel("Spatial frequency (fraction of Nyquist)")
plt.title("NPS")
plt.grid()
plt.gca().set_aspect('equal', adjustable='box')
plt.show()