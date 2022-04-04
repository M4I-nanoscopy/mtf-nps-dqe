import csv
import matplotlib.pyplot as plt
import matplotlib

import numpy as np


def theoretical_dqe():
    x = np.arange(0.0001, 1, 0.01)
    y = sinc_squared(np.math.pi * x / 2)

    return x, y


def sinc_squared(x):
    return (np.sin(x) ** 2) / (x ** 2)


def extract(d, column):
    x = list()
    y = list()

    for row in d:
        x.append(float(row[1]))
        y.append(float(row[column]))

    return x, y

def extract_published(d, column):
    x = list()
    y = list()

    for row in d:
        x.append(float(row[0]))
        y.append(float(row[column]))

    return x, y


plt.figure(figsize=(10,10))
plt.axis('equal')
matplotlib.rcParams['lines.linewidth'] = 2

with open('../data/published/FEI-fIII.csv', 'r') as csvfile:
    # Skip header
    next(csvfile, None)

    # Parse CSV
    fIII = list(csv.reader(csvfile, delimiter=' '))

    x, y = extract_published(fIII, 1)
    plt.plot(x, y, label="Published Falcon III EC (300 kV)")

    x, y = extract_published(fIII, 2)
    plt.plot(x, y, label="Published Falcon III Int (300 kV)")
#
#
# with open('../data/McMullan2014.csv', 'r') as csvfile:
#     # Skip header
#     next(csvfile, None)
#
#     McMullan2014 = list(csv.reader(csvfile, delimiter=','))
#
#     x, y = extract(McMullan2014, 1)
#     plt.plot(x, y, label="Gatan K2 Summit EC")
#
#     x, y = extract(McMullan2014, 2)
#     plt.plot(x, y, label="Falcon II")
#
#     x, y = extract(McMullan2014, 3)
#     plt.plot(x, y, label="DE 20")
#
#     x, y = extract(McMullan2014, 4)
#     plt.plot(x, y, label="Film")


with open('../data/FindDQE/ec_alignoff_20181120_100.csv', 'r') as csvfile:
    # Skip header
    next(csvfile, None)

    falcon3 = list(csv.reader(csvfile, delimiter=','))

    x, y = extract(falcon3, 5)
    plt.plot(x, y, label="Experimental Falcon III EC (200 kV)")


with open('../data/FindDQE/int_alignoff.csv', 'r') as csvfile:
    # Skip header
    next(csvfile, None)

    falcon3 = list(csv.reader(csvfile, delimiter=','))

    x, y = extract(falcon3, 5)
    plt.plot(x, y, label="Experimental Falcon III Int (200 kV)")


with open('../data/FindDQE/ec_alignoff_20181218.csv', 'r') as csvfile:
    # Skip header
    next(csvfile, None)

    falcon3 = list(csv.reader(csvfile, delimiter=','))

    x, y = extract(falcon3, 5)
    plt.plot(x, y, label="Experimental Falcon III EC (200 kV) (20181218)")

x, y = theoretical_dqe()
plt.plot(x, y, '--', label="Theoretical", color='black', linewidth=2)

ax = plt.gca()
plt.ylim((0, 2))
plt.xlim((0, 1))
plt.xlabel("Fraction of Nyquist")
plt.ylabel("DQE")
ax.yaxis.grid(True)
plt.legend(frameon=False)
plt.show()
