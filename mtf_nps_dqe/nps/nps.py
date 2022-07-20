import argparse
import os.path

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    "font.size": 12,
    "font.family": 'Arial',
    "svg.fonttype": 'none',
    "lines.linewidth" : 3
})


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('--input', nargs='+', type=str, required=True, help='Input measured NPS curves (can be multiple)')
    parser.add_argument('--output', type=str, required=False, help='Output image file (SVG) to store to')

    return parser.parse_args()


def load_nps(f):
    d = np.load(f)
    return d['w'], d['nps']


config = parse_arguments()
plt.figure(figsize=(7, 7))

for input_f in config.input:
    w, nps = load_nps(input_f)

    plt.plot(w, nps, label=os.path.basename(input_f))


plt.legend(loc='lower left')
plt.xlim([0, 1.0])
plt.ylim([0, 1.1])
plt.xlabel("Spatial frequency (fraction of Nyquist)")
plt.title("NPS")
plt.grid()
plt.gca().set_aspect('equal', adjustable='box')

if config.output is not None:
    plt.tight_layout()
    plt.savefig(config.output, dpi=300, bbox_inches='tight', pad_inches=0.1)
else:
    plt.show()
