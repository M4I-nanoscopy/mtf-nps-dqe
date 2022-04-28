import numpy as np
from scipy.fft import rfft2, irfft2, rfftfreq, fftfreq, fft2, fftshift
import matplotlib.pyplot as plt


def ft(mic):
    return rfft2(mic, workers=1)


def ift(mic):
    return irfft2(mic, workers=1)


# Inspiration for fourier cropping function from:
# https://github.com/eugenepalovcak/restore
def bin_mic(mic_ft, apix, cutoff, mic_freqs=None, lp=True, bwo=5):
    """ Bins a micrograph by Fourier cropping
    Optionally applies a Butterworth low-pass filter"""
    if mic_freqs is not None:
        f = mic_freqs
    else:
        f = get_mic_freqs(mic, apix)

    if lp:
        mic_ft *=  1./ (1.+ ( f/ cutoff )**(2*bwo))
    mic_bin = fourier_crop(mic_ft, f, cutoff)

    return mic_bin

def fourier_crop(mic_ft, mic_freqs, cutoff):
    """Extract the portion of the real FT lower than a cutoff frequency"""
    n_x, n_y = mic_ft.shape

    f_h = mic_freqs[0]
    f_v = mic_freqs[:n_x // 2, 0]

    c_h = np.searchsorted(f_h, cutoff)
    c_v = np.searchsorted(f_v, cutoff)

    mic_ft_crop = np.vstack((mic_ft[:c_v, :c_h],
                             mic_ft[n_x - c_v:, :c_h]))
    return mic_ft_crop

def get_mic_freqs(mic, apix, angles=False):
    """Returns array of effective spatial frequencies for a real 2D FFT.
    If angles is True, returns the array of the angles w.r.t. the X-axis
    """
    n_x, n_y = mic.shape
    x,y =  np.meshgrid(rfftfreq(n_y,d=apix), fftfreq(n_x,d=apix))
    s = np.sqrt(x**2 + y**2)

    if angles:
        a = np.arctan2(y,x)
        return s,a
    else:
        return s

def gauss_2d(sigma, x0, y0, X, Y):
    return np.exp(-((X - x0) ** 2 / (2 * sigma ** 2) + ((Y - y0) ** 2 / (2 * sigma ** 2)))) / (sigma**2 * 2 * np.pi)


def psfg_2d(lam, x0, y0, X, Y):
    return np.exp(-((X-x0)**2/(lam**2)+((Y-y0)**2/(lam**2))))/(lam**2 * np.pi)

def get_gaussian_filter(sigma, grid_len):
    # Calculate the 2D gaussian
    grid = np.arange(0, grid_len, 1)
    grid_x, grid_y = np.meshgrid(grid, grid)
    g = gauss_2d(sigma, (grid_len // 2) - 1, (grid_len // 2) - 1, grid_x, grid_y)

    fg = rfft2(g)

    return np.abs(fg)

def get_hann_filter(grid_len):
    window1d = np.abs(np.hanning(grid_len))
    window2d = fftshift(np.sqrt(np.outer(window1d, window1d)))
    window2d_half = window2d[0:grid_len, 0:grid_len//2]

    return window2d_half