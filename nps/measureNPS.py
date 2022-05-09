import argparse
import matplotlib.pyplot as plt
import mrcfile
import numpy as np
import os
from numpy.fft import rfft2, irfft2
from numpy.fft import rfftfreq, fftfreq
from numpy.fft import fft2, fftshift
from scipy.ndimage import gaussian_filter
from scipy.optimize import curve_fit
from skimage.transform import downscale_local_mean

from lib import utils

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('FILE', nargs='?', help="Input image stack of flat fields (MRCs).  If none supplied, a stack will be simulated")
    parser.add_argument('--super_res', default=1, type=int, help='Rescale the frequency of the measured NPS curve by this factor')
    parser.add_argument('--store', type=str, help='Store output measured MTF curve')
    parser.add_argument('--crop', default=0, type=int, help='Crop the image to this (power of 2) size. This helps with NPS(0) estimates.')
    parser.add_argument('--guess', default=False, action='store_true',
                        help='Use guessed NPS(0) opposed to fitted NPS(0). Sometimes the fitting is bad.')

    sim_group = parser.add_argument_group('simulate')
    sim_group.add_argument('--gauss', type=float, default=0, help="Gaussian sigma used for blurring of image")
    sim_group.add_argument('--hann', default=False, action='store_true', help="Apply Hann filter (after fourier binning)")
    sim_group.add_argument('--bw', default=False, action='store_true', help="Apply Butterworth low-pass filter (during fourier binning)")
    sim_group.add_argument('--sim_super_res', type=int, default=1, help="Simulate super res factor")
    sim_group.add_argument('--factor', type=int, default=1, help="Initial upscale factor")
    sim_group.add_argument('--real', default=False, action='store_true', help="Perform operations in real space")

    settings = parser.parse_args()

    return settings


# A logistic function used for fitting NPS(0)
def nps0_fit(x, a, b):
    return a*x/(x+b)


def power_spectrum(d):
    # Take the fourier transform of the image.
    f1 = fft2(d)

    # Now shift the quadrants around so that low spatial frequencies are in
    # the center of the 2D fourier transformed image.
    f2 = fftshift(f1)

    # Take the absolute squared to create a power spectrum
    psd2D = np.abs(f2) ** 2

    return psd2D


def radial_profile(data):
    y, x = np.indices(data.shape)
    center = tuple(int(s / 2) for s in data.shape)
    r = np.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)
    r = r.astype(int)

    tbin = np.bincount(r.ravel(), data.ravel())
    nr = np.bincount(r.ravel())

    return tbin / nr


def calculate_nnps(nps, nps0):
    return np.divide(nps, nps0)


def calculate_nps0(frames, mean):
    r = list()

    # Calculate the bin factors to measure. Do this as power of 2, to
    factors = 2**np.arange(1, np.log2(mean.shape[0]), dtype=int)

    # Limit the bin factors to measure not too small image sizes
    factors = factors[0:-2]

    for frame in frames:
        # Subtract mean from the frame
        f = frame - mean

        for factor in factors:
            # b = 1/factor

            # Bin the frame using the mean of the surrounding pixels
            # binned = downscale_local_mean(f, (factor, factor), cval=np.mean(f))

            # Bin the frame using fourier cropping
            binned = utils.ift(utils.bin_mic_ft(utils.ft(f), 1, 1/(factor*2), mic_freqs=utils.get_mic_freqs(f, 1)))

            # Calculate the variance
            sigma_squared = np.var(binned)

            # McMullan et al. 2009 and Paton et al. 2021
            nps0 = sigma_squared/factor**2

            # print("shape: %s, factor: %d, b: %.2f, var: %s, nps0: %.5f" % (binned.shape, factor, b, sigma_squared, nps0))

            r.append([factor, nps0])

    return np.array(r)


# Read config
config = parse_arguments()

if config.FILE is None:
    print("INFO: No image supplied, simulating flat fields")
    factor = config.factor
    super_res = config.sim_super_res
    org_shape = 512
    shape = 512 * factor
    gauss = config.gauss

    # Keep illumination constant, when changing factor
    ill = 100 / factor**2
    ill_noise = 10/factor**2

    # Simulate flat fields
    frames = np.random.normal(ill, ill_noise, (100, shape, shape)).astype(np.uint8)

    # Do operations in real space or fourier space
    if config.real:
        if config.gauss > 0:
            frames = gaussian_filter(frames, (0, gauss * factor, gauss * factor))

        # Bin
        if config.factor > 1:
            frames = downscale_local_mean(frames, (0, factor // super_res, factor // super_res))
    else:
        # FFT
        ft_frames = utils.ft(frames)

        # Gaussian filter
        if gauss > 0:
            fg = utils.get_gaussian_filter(gauss * factor, shape)
            # Yes, this multiplies all frames with the Gaussian filter
            ft_frames = ft_frames * fg

        # Fourier crop (bin)
        if config.factor > 1:
            mic_freqs = utils.get_mic_freqs(frames[0], 1 / factor)
            ft_frames = utils.bin_mic_ft(ft_frames, 1 / factor, super_res / 2, mic_freqs=mic_freqs, lp=config.bw)

        if config.hann:
            fh = utils.get_hann_filter(org_shape*super_res)
            ft_frames = ft_frames * fh

        # Inverse FFT
        frames = utils.ift(ft_frames)

    # Calculate the mean of all pixels
    mean = np.mean(frames, axis=0)

    config.FILE = "Simulated (real:{}, gauss:{}, hann:{}, bw:{}, sim_super_res:{}, factor:{})".format(
        config.real,
        config.gauss,
        config.hann,
        config.bw,
        config.sim_super_res,
        config.factor,
    )
else:
    # TODO: Support reading a tif stack
    with mrcfile.open(config.FILE, mode='r') as f:
        if config.crop > 0:
            frames = f.data[1:-1, 0:config.crop, 0:config.crop]
        else:
            frames = f.data[1:-1]

        # Calculate the mean of all pixels
        mean = np.mean(frames, axis=0)

ps = np.zeros_like(mean)
for frame in frames:
    # Calculate the power spectrum of the frame minus the mean of the frames
    sub = power_spectrum(frame-mean)
    ps += sub

# Calculate the 2D NPS by taking the average of all individual NPS, and dividing by the number of pixels
# Paton 2021 et al. (eq 2)
nps = ps/len(frames)/(mean.shape[0]*mean.shape[1])
nps_1d = radial_profile(nps)

# Calculate NPS(0) as function of the binning factor
nps0_meas = calculate_nps0(frames, mean)

# Make an initial guess for the fitting, by taking the first 10% of the data as NPS(0)
# Skip the 0 frequency here, as it may contain a large peak which throws off the guessing.
nps0_g = np.mean(nps_1d[1:int(len(nps_1d)*0.1)])
print("Guessed NPS(0): %0.2f" % nps0_g)
fit_guess = [nps0_g, 1]
fit_bounds = ([nps0_g - nps0_g*0.5, 0], [nps0_g + nps0_g*0.5, np.inf])
print(fit_bounds)

# Fit
fit, pcov = curve_fit(nps0_fit, nps0_meas[:, 0], nps0_meas[:, 1], maxfev=100000, p0=fit_guess, bounds=fit_bounds)
nps0_f = fit[0]
x_fit = np.arange(0, np.max(nps0_meas[:, 0])+1)
print("Fitted NPS(0): %0.2f" % nps0_f)

# Used fitted NPS(0)
if config.guess:
    nps0 = nps0_g
else:
    nps0 = nps0_f

# Normalize the NPS using the selected NPS(0)
nnps = calculate_nnps(nps, nps0)

# Take the radial profile to create a 1D NPS
nnps_1d = radial_profile(nnps)

# Calculate nyquist frequency from the image shape
nyquist = mean.shape[0]/2
max_x = np.sqrt((nnps.shape[0]/2)**2 + (nnps.shape[0]/2)**2)
w = np.linspace(0, max_x/nyquist, len(nnps_1d))

if config.super_res > 1:
    print("Applying super res scaling to final curve")
    w = w * config.super_res

# Figures
fig, ((ax0, ax1, ax2), (ax3, ax4, ax5)) = plt.subplots(2, 3)
fig.suptitle(config.FILE)

# Individual frame
im = ax0.imshow(frames[0])
fig.colorbar(im, ax=ax0, orientation='vertical')
ax0.set_title("First frame")

# Subtraction
im = ax1.imshow(frames[0] - mean)
fig.colorbar(im, ax=ax1, orientation='vertical')
ax1.set_title("First frame minus mean of frames")

# Power spectrum
im = ax2.imshow(nps)
fig.colorbar(im, ax=ax2, orientation='vertical')
ax2.set_title("Noise Power Spectrum (NPSdig)")

# Calculating NPS(0)
ax3.scatter(nps0_meas[:, 0], nps0_meas[:, 1], label='Measured')
ax3.hlines(y=nps0_g, xmin=0, xmax=np.max(nps0_meas[:, 0]), color='r', label='NPS(0) (10%)')
ax3.hlines(y=nps0_f, xmin=0, xmax=np.max(nps0_meas[:, 0]), color='orange', label='NPS(0) (fitted)')
ax3.plot(x_fit, nps0_fit(x_fit, *fit), color='orange', label='%.02f*x/(x+%0.2f)' % (fit[0], fit[1]))
ax3.set_ylim(0)
ax3.set_xlabel("Factor")
ax3.set_ylabel("NPS(0)")
ax3.legend(loc='lower right')
ax3.set_title("Estimating NPS(0)")

im = ax4.imshow(nnps, vmax=1)
fig.colorbar(im, ax=ax4, orientation='vertical')
ax4.set_title("Normalised 2D noise power spectrum")

# Normalised NPS
ax5.plot(w, nnps_1d, label=os.path.basename(config.FILE))
ax5.set_xlim([0, 1])
ax5.set_ylim([0, 1.1])
ax5.set_xlabel("Spatial frequency (fraction of Nyquist)")
ax5.set_ylabel("Normalised noise power spectrum")
ax5.set_title("Normalised 1D noise power spectrum")
ax5.set_aspect('equal', adjustable='box')
ax5.grid()

plt.show()

if config.store is not None:
    np.savez(config.store, w=w, nps=nnps_1d)


# TODO: This is not a very clean way around the fact that this script should be refactored
def main():
    pass


if __name__ == "main":
    main()
