import argparse
import csv
import os.path

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas

plt.rcParams.update({
    "font.size": 12,
    "font.family": 'Arial',
    "svg.fonttype": 'none',
    "lines.linewidth" : 3
})


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('--input', nargs='+', type=str, required=False, help='Input measured MTF curves (can be multiple)')
    parser.add_argument('--published', default=False, action='store_true', help='Also plot published MTF curves')
    parser.add_argument('--output', type=str, required=False, help='Output image file (SVG) to store to')

    return parser.parse_args()


# McMullan et al. 2009. Page 1126
def theoretical_mtf(w):
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.sin(np.pi * w / 2) / (np.pi * w / 2)


def load_mtf(f):
    d = np.load(f)
    return d['w'], d['mtf']


def load_published_star(f):
    path = os.path.dirname(os.path.realpath(__file__))
    d = pandas.read_csv(path + "/published/" + f, delimiter=' ')

    # Relion stores MTF as 1/pixel, and not as fraction of Nyquist
    w_relion = d['_rlnResolutionInversePixel'] * 2

    return w_relion, d['_rlnMtfValue']


config = parse_arguments()
plt.figure(figsize=(7, 7))

if config.input is not None:
    for input_f in config.input:
        w, mtf = load_mtf(input_f)

        plt.plot(w, mtf, label=os.path.basename(input_f))

w_calc = np.arange(0, 1.1, 0.01)
plt.plot(w_calc, theoretical_mtf(w_calc), '--', color='Black', label='Theoretical')

if config.published:
    w, mtf = load_published_star('mtf_f3ec_200kv.star')
    plt.plot(w, mtf, label='Published Falcon III EC (200 kV)')

    w, mtf = load_published_star('mtf_f3ec_300kv.star')
    plt.plot(w, mtf, label='Published Falcon III EC (300 kV)')

    w, mtf = load_published_star('falconIII200_int.star')
    plt.plot(w, mtf, label='Published Falcon III int (200 kV)')

plt.legend(loc='lower left')
plt.xlim([0, 1.0])
plt.ylim([0, 1.1])
plt.xlabel("Spatial frequency (fraction of Nyquist)")
plt.title("MTF")
plt.grid()
plt.gca().set_aspect('equal', adjustable='box')

if config.output is not None:
    plt.tight_layout()
    plt.savefig(config.output, dpi=300, bbox_inches='tight', pad_inches=0.1)
else:
    plt.show()


# TODO: This is not a very clean way around the fact that this script should be refactored
def main():
    pass


if __name__ == "__main__":
    main()
