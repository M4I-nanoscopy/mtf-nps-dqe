import argparse
import math
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize
from matplotlib import patches
from matplotlib.widgets import RectangleSelector
import mrcfile
from scipy.ndimage import binary_dilation, sobel, gaussian_filter
from scipy.special import erfc
from scipy.stats import linregress
from skimage import io
from skimage.filters.thresholding import threshold_mean
from skimage.transform import rotate, downscale_local_mean

from lib import utils


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('FILE', default=None, nargs='?', help="Input image (tif or mrc). If none supplied, an edge will be simulated")
    parser.add_argument('-x', default=None, type=int, help="Starting x coordinate of crop")
    parser.add_argument('-y', default=None, type=int, help="Starting y coordinate of crop")
    parser.add_argument('--width', default=None, type=int, help="Width of crop")
    parser.add_argument('--height', default=None, type=int, help="Height of crop")
    parser.add_argument('--store', type=str, help='Store output measured MTF curve')
    parser.add_argument('--super_res', default=1, type=int, help='Rescale the frequency of the measured MTF curve by this factor')
    parser.add_argument('--rotate', default=0, type=int, help='Number of times to rotate the image clockwise')

    sim_group = parser.add_argument_group('simulate edge parameters')
    sim_group.add_argument('--gauss', type=float, default=0, help="Gaussian sigma used for blurring of image")
    sim_group.add_argument('--hann', default=False, action='store_true', help="Apply Hann filter (after fourier binning)")
    sim_group.add_argument('--bw', default=False, action='store_true', help="Apply Butterworth low-pass filter (during fourier binning)")
    sim_group.add_argument('--sim_super_res', type=int, default=1, help="Simulate super res factor")
    sim_group.add_argument('--factor', type=int, default=1, help="Initial upscale factor")
    sim_group.add_argument('--real', default=False, action='store_true', help="Perform operations in real space")
    sim_group.add_argument('--noise', default=False, action='store_true', help="Add Poission noise to illuminated area")

    settings = parser.parse_args()

    return settings


def rectangle_select_callback(eclick, erelease):
    global config
    # Not entirely pretty
    config.x = int(eclick.xdata)
    config.y = int(eclick.ydata)
    config.width = int(erelease.xdata - eclick.xdata)
    config.height = int(erelease.ydata - eclick.ydata)


# Edge spread function (ESF)
# McMullan et al. 2009 Eq 12
def esf(x, lam, x0):
    with np.errstate(divide='ignore', invalid='ignore'):
        return erfc(-(x - x0) / lam) / 2


# Line spread function (LSF).
# McMullan et al. 2009 Eq 11
def lsf(x, lam, x0):
    return np.exp(-(x - x0) ** 2 / lam ** 2) / (np.pi * lam)


# Modulation transfer function (MTF) for Gaussian
# McMullan et al. 2009 Eq 13
def mtf_g(w, lam):
    return np.exp(-np.pi ** 2 * lam ** 2 * w ** 2 / 4)


# McMullan et al. 2009. Page 1126
def theoretical_mtf(w):
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.sin(np.pi * w / 2) / (np.pi * w / 2)


# McMullan et al. 2009. Eq 14
def mtf(w, lam):
    return theoretical_mtf(w) * mtf_g(w, lam)


# Read config
config = parse_arguments()

if config.FILE is None:
    print("INFO: No image supplied, simulating ideal edge")
    factor = config.factor
    super_res = config.sim_super_res
    org_shape = 512
    shape = 512 * factor
    gauss = config.gauss

    im = np.zeros((shape, shape))

    # Keep illumination constant, when changing factor
    ill = 100 / factor**2
    ill_noise = 10/factor**2

    # Add illuminated area
    if config.noise:
        im[0:shape, shape // 2:shape] = np.random.normal(ill, ill_noise, (shape, shape//2))
    else:
        im[0:shape, shape//2:shape] = ill

    # Rotate image
    im = rotate(im, 7, mode='constant', cval=0)

    # Do operations in real space or fourier space
    if config.real:
        if config.gauss > 0:
            im = gaussian_filter(im, gauss * factor)

        # Bin
        if config.factor > 1:
            im = downscale_local_mean(im, factor // super_res)
    else:
        # FFT
        fim = utils.ft(im)

        # Gaussian filter
        if gauss > 0:
            fg = utils.get_gaussian_filter(gauss * factor, shape)
            fim = fim*fg

        # Fourier crop (bin)
        if config.factor > 1:
            fim = utils.bin_mic_ft(fim, 1 / factor, super_res / 2, mic_freqs=utils.get_mic_freqs(im, 1 / factor), lp=config.bw)

        if config.hann:
            fh = utils.get_hann_filter(org_shape*super_res)
            fim = fim*fh

        # Inverse FFT
        im = utils.ift(fim)

    # Supply defaults
    config.FILE = "Simulated (real:{}, gauss:{}, hann:{}, bw:{}, sim_super_res:{}, factor:{}, noise:{})".format(
        config.real,
        config.gauss,
        config.hann,
        config.bw,
        config.sim_super_res,
        config.factor,
        config.noise
    )
    config.x = 128 * super_res
    config.y = 128 * super_res
    config.width = 256 * super_res
    config.height = 256 * super_res
else:
    ext = os.path.splitext(config.FILE)[1]

    if ext == '.tif' or ext == '.tiff':
        # Read image
        im = np.array(io.imread(config.FILE))
    elif ext == '.mrc' or ext == '.mrcs':
        with mrcfile.open(config.FILE, mode='r') as f:
            if f.is_image_stack():
                print("WARNING: Image stack, only reading first frame.")
                im = f.data[0]
            else:
                im = f.data
    else:
        print('ERROR: Unsupported file extension (only TIF or MRC)')
        sys.exit(1)

    if config.rotate > 0:
        im = np.rot90(im, config.rotate)

if config.x is None or config.y is None or config.width is None or config.height is None:
    plt.imshow(im, origin='lower')
    r = RectangleSelector(plt.gca(), rectangle_select_callback, interactive=True)
    plt.title("Select the area with edge to crop. Then close this window.")
    plt.show()
    print(config)

# Calculate the crop shape
crop_x = config.x
crop_y = config.y
crop_h = config.height
crop_w = config.width

# Take the crop of the image
area = np.s_[crop_y:crop_y + crop_h, crop_x:crop_x + crop_w]
crop = im[area]

# Threshold the image to a binary
try:
    thresh = threshold_mean(crop)
    binary = crop > thresh
except RuntimeError:
    # This can happen if the image is already binary
    print("WARNING: Could not threshold the original image. Image already binary? Trying with original image.")
    binary = crop

# Binary dilate to fill holes (should only be dead pixels).
# Doing two iteration to also account for the bigger dead pixels of super res
rec = binary_dilation(binary, iterations=2)

# Calculate sobel filter
# http://scikit-image.org/docs/dev/auto_examples/edges/plot_edge_filter.html#sphx-glr-auto-examples-edges-plot-edge-filter-py
sob = sobel(rec)

# Store final image to take crop of and perform linear regression
final_crop = sob

# Extract line fragment as x and y coordinates
line_idx = np.flatnonzero(final_crop)
line_y, line_x = np.unravel_index(line_idx, final_crop.shape)

# Linear regression
slope, intercept, r_value, p_value, std_err = linregress(line_x, line_y)
print("R-squared-value: %f" % r_value ** 2)
print("Slope: %f (%0.10f degrees)" % (slope, math.degrees(math.atan(slope))))
print("Intercept: %f" % intercept)

# Show total edge fit
edge_x_vals = np.arange(0, crop_w)
edge_y_vals = intercept + slope * edge_x_vals

# Linearize crop
values = np.reshape(crop, crop_h * crop_w)

# Calculate distance matrix towards the slope
# https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
distance = np.zeros((crop_h, crop_w))
column = np.arange(0, crop_w) + 0.5
for y in range(crop_h):
    distance[y, :] = (slope * column - (y + 0.5) + intercept) / np.sqrt(slope ** 2 + 1)

# Sort values according to distance to slope
distances = np.reshape(distance, crop_h * crop_w)
indexes = np.argsort(distances)

# Invert the slope if black and white are reversed
sign = 1
if np.average(values[indexes[:10]]) > np.average(values[indexes[-10:]]):
    sign = -1

# Take the values according to the distance sorted indexes. This gives the ESF
values = values[indexes]
distances = sign * distances[indexes]

# Flip if black and white are reversed
if distances[0] > distances[-1]:
    distances = np.flip(distances)
    values = np.flip(values)

# Normalize the ESF by taking values far away from the edge. Also correct for dark noise
flat_mean = np.mean(values[distances > 10])
print("Mean count: %.2f" % flat_mean)
dark_mean = np.mean(values[distances < -10])
print("Mean dark count: %.2f" % dark_mean)

# Normalize
esf_meas = (values - dark_mean) / (flat_mean - dark_mean)

# Fit the measured ESF to the theoretical ESF
try:
    fit, pcov = scipy.optimize.curve_fit(esf, distances, esf_meas, maxfev=10000)
    # Calculate one standard deviation error on the parameters
    perr = np.sqrt(np.diag(pcov))
except RuntimeError as e:
    print("ERROR: Could not fit ESF. Message: '%s'" % e.__str__())
    sys.exit(1)

# Print fits
print("Lambda (fit): %.05f±%.02f" % (fit[0], perr[0]))
print("x0 (fit): %.02f±%.02f" % (fit[1], perr[1]))

# Calculate fitted ESF
x_fit = np.linspace(-10, 10, 1000)
esf_fit = esf(x_fit, *fit)

# Line spread function (LSF)
lsf_fit_meas = np.diff(esf_fit, prepend=0)
lsf_meas_meas = np.diff(esf_meas, prepend=0)

# Fitted LSF
lsf_fit = lsf(x_fit, *fit)

# Modulation transfer function (Normalised with the sum of the LSF)
# mtf_meas = 1/np.sum(lsf_fit_meas) * np.abs(np.fft.fft(lsf_fit_meas))
# mtf_meas_w = np.linspace(0, 100, len(mtf_meas))

# Fitted MTF
# Overshooting 1, to make sure the value 1 is also included
mtf_calc_w = np.arange(0, 1.1, 0.01)
mtf_calc = mtf_g(mtf_calc_w, fit[0])

# Print half and nyquist values
print("MTF(0.25 Nyquist): %0.3f" % mtf_g(0.25, fit[0]))
print("MTF(0.5 Nyquist): %0.3f" % mtf_g(0.5, fit[0]))
print("MTF(1 Nyquist):   %0.3f" % mtf_g(1.0, fit[0]))

if config.super_res > 1:
    print("Applying super res scaling to final curve")
    mtf_calc_w = mtf_calc_w * config.super_res

# Figure
fig, ((ax0, ax1, ax2), (ax3, ax4, ax5), (ax6, ax7, ax8)) = plt.subplots(3, 3)
fig.suptitle(config.FILE)

# Show image
ax0.set_title("Full image")
ax0.imshow(im, origin='lower')
c = patches.Rectangle((config.x, config.y), config.width, config.height, linewidth=1, edgecolor='r', facecolor='none')
ax0.add_patch(c)

# Crop
ax1.set_title("Crop")
ax1.imshow(crop, origin='lower')
ax1.plot(edge_x_vals, edge_y_vals, '--', color='orange')
ax1.set_xlim(0, crop_w)
ax1.set_ylim(0, crop_h)

# Distance
ax2.set_title("Distance")
ax2.imshow(distance, origin='lower')
ax2.plot(edge_x_vals, edge_y_vals, '--', color='orange')
ax2.set_xlim(0, crop_w)
ax2.set_ylim(0, crop_h)

ax3.set_title("Edge spread function (normalised)")
# ax3.plot(distances, esf_meas, color='blue', label='Measured')
ax3.scatter(distances, esf_meas, color='blue', label='Measured', s=1)
ax3.plot(x_fit, esf_fit, color='orange', label='erfc(-x/(%.02f±%.02f))/2' % (fit[0], perr[0]))
ax3.plot(x_fit, esf(x_fit, 0.00001, fit[1]), '--', color='black', label='erfc(-x/(0.0))/2')
ax3.set_xlim(fit[1] - 4, fit[1] + 4)
ax3.legend(loc='lower right')

ax4.set_title("Line spread function (normalised)")
# ax4.scatter(x_fit, lsf_meas_meas/np.max(lsf_meas_meas), label='Numeric diff ESF')
# ax4.scatter(x_fit, lsf_fit_meas / np.max(lsf_fit_meas), label='Numeric diff ESFfit')
ax4.set_xlim(fit[1] - 4, fit[1] + 4)
ax4.plot(x_fit, lsf_fit / np.max(lsf_fit), color='orange', label='exp(-x^2/(%.02f±%.02f)^2)' % (fit[0], perr[0]))
ax4.legend(loc='lower left')

ax5.set_title("Modulation transfer function")
ax5.set_xlim(0, 1.0)
ax5.set_ylim(0, 1.0)
ax5.plot(mtf_calc_w, mtf(mtf_calc_w, 0), '--', label='MTF(λ=0)', color='black')
ax5.plot(mtf_calc_w, mtf_calc, color='orange', label='MTFg(λ=%.02f±%.02f)' % (fit[0], perr[0]))
ax5.fill_between(mtf_calc_w, mtf_g(mtf_calc_w,  fit[0] - perr[0]), mtf_g(mtf_calc_w, fit[0] + perr[0]),
                 facecolor='orange', alpha=0.5)
ax5.legend(loc='lower left')
ax5.grid()

ax6.set_title("Raw edge spread function")
ax6.scatter(distances, values, s=1)

plt.show()

if config.store is not None:
    np.savez(config.store, w=mtf_calc_w, mtf=mtf_calc)


# TODO: This is not a very clean way around the fact that this script should be refactored
def main():
    pass


if __name__ == "__main__":
    main()
