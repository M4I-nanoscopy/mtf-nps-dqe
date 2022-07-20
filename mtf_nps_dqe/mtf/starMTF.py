import argparse
import sys
import numpy as np


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('FILE', default=None, help="Input MTF .npz file")
    parser.add_argument('--output', type=str, required=False, help='Output file (.star)')

    settings = parser.parse_args()

    return settings


def star_mtf(filename):
    r = "data_mtf\n"
    r += "loop_\n"
    r += "_rlnResolutionInversePixel\n"
    r += "_rlnMtfValue\n"
    r += "0 1\n"

    with np.load(filename) as data:
        mtf = data['mtf']
        # measureMTF stores the frequency as fraction of Nyquist. Relion wants 1/pixel, so divide frequency by 2.
        w = data['w'] / 2

        for idx, fr in enumerate(w[w <= 0.5]):
            r += "%.6f %.6f\n" % (fr, mtf[idx])

    return r


def main():
    config = parse_arguments()

    star = star_mtf(config.FILE)

    if config.output is not None:
        with open(config.output, "w") as f:
            f.write(star)
    else:
        print(star)

    return 0


if __name__ == "__main__":
    sys.exit(main())

