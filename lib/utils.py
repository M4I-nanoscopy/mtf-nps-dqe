import numpy as np
from scipy.fft import rfft2, irfft2
from scipy.fft import rfftfreq, fftfreq
from scipy.fft import fft2, fftshift
import matplotlib.pyplot as plt


def ft(mic):
    return rfft2(mic)


def ift(mic):
    return irfft2(mic)


# Inspiration for this function from:
# https://github.com/eugenepalovcak/restore
def fourier_crop_bin(mic, factor):
    n_x, n_y = mic.shape
    cutoff = 1/factor
    x, y = np.meshgrid(rfftfreq(n_y), fftfreq(n_x))
    mic_freq = np.sqrt(x**2 + y**2)

    f_h = mic_freq[0]
    f_v = mic_freq[:n_x//2, 0]

    # Calculate the frequency (pixel number) where to cutoff
    c_h = np.searchsorted(f_h, cutoff)
    # TODO: We do not fully understand this division by 2 here
    c_v = np.searchsorted(f_v, cutoff) // 2

    # Combine two parts of the spectrum to form the resulting image
    mic_ft_crop = np.vstack((mic[:c_v, :c_h],
                             mic[n_x - c_v:, :c_h]))

    return mic_ft_crop


def gauss_2d(sigma, x0, y0, X, Y):
    return np.exp(-((X - x0) ** 2 / (2 * sigma ** 2) + ((Y - y0) ** 2 / (2 * sigma ** 2)))) / (sigma**2 * 2 * np.pi)


def psfg_2d(lam, x0, y0, X, Y):
    return np.exp(-((X-x0)**2/(lam**2)+((Y-y0)**2/(lam**2))))/(lam**2 * np.pi)


def get_gaussian_filter(sigma, factor, shape):
    # Calculate the 2D gaussian
    grid_len = shape * factor
    grid = np.arange(0, grid_len, 1)
    grid_x, grid_y = np.meshgrid(grid, grid)
    g = gauss_2d(sigma * factor, (grid_len // 2) - 1, (grid_len // 2) - 1, grid_x, grid_y)

    fg = rfft2(g)

    return np.abs(fg)
