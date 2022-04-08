import argparse
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

    parser.add_argument('--input', nargs='+', type=str, required=True, help='Input measured DQE curves (can be multiple)')
    parser.add_argument('--published', default=False, action='store_true', help='Also plot published DQE curves')

    return parser.parse_args()


def theoretical_dqe(w):
    with np.errstate(divide='ignore', invalid='ignore'):
        return sinc_squared(np.math.pi * w / 2)


def sinc_squared(w):
    return (np.sin(w) ** 2) / (w ** 2)


def load_dqe(f):
    d = np.load(f)
    return d['w'], d['dqe'], d['label']


def load_published_csv(f, column, delimiter=','):
    d = pandas.read_csv(f, delimiter=delimiter)

    return d['x'], d[column]


config = parse_arguments()

for dqe_input_f in config.input:
    w, dqe, label = load_dqe(dqe_input_f)

    plt.plot(w, dqe, label=label)

w_calc = np.arange(0, 1.1, 0.01)
plt.plot(w_calc, theoretical_dqe(w_calc), '--', color='Black', label='Theoretical')

if config.published:
    w, dqe = load_published_csv('data/published/FEI-fIII.csv', "Falcon III EC", ' ')
    plt.plot(w, dqe, label='Published Falcon III EC (300 kV)')

    w, dqe = load_published_csv('data/published/FEI-fIII.csv', "Falcon III", ' ')
    plt.plot(w, dqe, label='Published Falcon III int (300 kV)')

plt.legend()
plt.xlim([0, 1.0])
plt.ylim([0, 1.0])
plt.xlabel("Spatial frequency (fraction of Nyquist)")
plt.title("DQE")
plt.grid()
plt.gca().set_aspect('equal', adjustable='box')
plt.show()