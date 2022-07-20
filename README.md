# Measuring/calculating MTF, NPS and DQE

Scripts for measuring MTF and NPS, and thereby calculating DQE. Useful for 
evaluating low-dose cryogenic electron microscopy (cryo-EM) detectors.

### Modulation Transfer Function (MTF)

The MTF is measured using the knife-edge method. The edge spread function (ESF) is measured by determining the edge angle, 
and using this to plot pixels values as function of the distance to the edge. This is fitted to an expression describing 
the ESF. From the fitted parameter the MTF is directly calculated.

### Noise Power Spectrum (NPS) or Wiener Spectrum

The NPS is measured using a series of flat field exposures. Challenging is estimating NPS(0), which can be done 
by looking at the normalized variance of progressively binned flat field exposures. 

### Detective Quantum Efficiency (DQE)

Using the MTF and NPS, the DQE can be calculated. Hereby is DQE(0) (a scaling factor) assumed to be a certain value. 
To actually measure DQE(0) you need an accurate way to measure the true conversion factor (counts out/flux in) of 
the detector. For example by using a Faraday cup, mounted close to the detector.  

## Simulations

Both measureMTF and measureNPS have extensive options to simulate knife edges and flat field noise image stacks. 
It's possible to simulate things like super resolution and gaussian filters. 

## Installation

Requires Python3 >= 3.8

This will create a virtual environment and install directly from GitHub
```bash
python3 -m venv mtf-nps-dqe-venv
source mtf-nps-dqe-venv/bin/activate
pip3 install git+https://github.com/M4I-nanoscopy/mtf-nps-dqe.git#egg=mtf-nps-dqe
```

For development, consider installing with the `-e` flat liek this
```bash
python3 -m venv mtf-nps-dqe-venv
source mtf-nps-dqe-venv/bin/activate
git clone https://github.com/M4I-nanoscopy/mtf-nps-dqe.git
pip3 install -e mtf-nps-dqe/ 
```

In either case, the tools should be available in your PATH with the virtualenv activated.
## Running

### MTF
```bash
usage: measureMTF [-h] [-x X] [-y Y] [--width WIDTH] [--height HEIGHT] [--store STORE] [--super_res SUPER_RES] [--rotate ROTATE] [--gauss GAUSS] [--hann] [--bw] [--sim_super_res SIM_SUPER_RES]
                  [--factor FACTOR] [--real] [--noise]
                  [FILE]

positional arguments:
  FILE                  Input image (tif or mrc). If none supplied, an edge will be simulated

options:
  -h, --help            show this help message and exit
  -x X                  Starting x coordinate of crop
  -y Y                  Starting y coordinate of crop
  --width WIDTH         Width of crop
  --height HEIGHT       Height of crop
  --store STORE         Store output measured MTF curve
  --super_res SUPER_RES
                        Rescale the frequency of the measured MTF curve by this factor
  --rotate ROTATE       Number of times to rotate the image clockwise

simulate edge parameters:
  --gauss GAUSS         Gaussian sigma used for blurring of image
  --hann                Apply Hann filter (after fourier binning)
  --bw                  Apply Butterworth low-pass filter (during fourier binning)
  --sim_super_res SIM_SUPER_RES
                        Simulate super res factor
  --factor FACTOR       Initial upscale factor
  --real                Perform operations in real space
  --noise               Add Poission noise to illuminated area
```
Starting without coordinates will show a dialog to select the area for cropping:

```bash
measureMTF data/edge/simulated/ideal-edge-no-noise.tif
```

To use a simulated edge simply run:
```bash
measureMTF
```

### Plotting MTF

```bash
mtf --published --input data/mtf/*.npz --output mtf.svg 
```


### star MTF file for Relion
You can generate a star file to use the measured MTF in Relion. 

```bash
$ starMTF --help
usage: starMTF [-h] [--output OUTPUT] FILE

positional arguments:
  FILE             Input MTF .npz file

options:
  -h, --help       show this help message and exit
  --output OUTPUT  Output file (.star)
```

### NPS
```bash
$ usage: measureNPS [-h] [--super_res SUPER_RES] [--store STORE] [--crop CROP] [--guess] [--gauss GAUSS] [--hann] [--bw] [--sim_super_res SIM_SUPER_RES] [--factor FACTOR] [--real] [FILE]

positional arguments:
  FILE                  Input image stack of flat fields (MRCs). If none supplied, a stack will be simulated

options:
  -h, --help            show this help message and exit
  --super_res SUPER_RES
                        Rescale the frequency of the measured NPS curve by this factor
  --store STORE         Store output measured MTF curve
  --crop CROP           Crop the image to this (power of 2) size. This helps with NPS(0) estimates.
  --guess               Use guessed NPS(0) opposed to fitted NPS(0). Sometimes the fitting is bad.

simulate:
  --gauss GAUSS         Gaussian sigma used for blurring of image
  --hann                Apply Hann filter (after fourier binning)
  --bw                  Apply Butterworth low-pass filter (during fourier binning)
  --sim_super_res SIM_SUPER_RES
                        Simulate super res factor
  --factor FACTOR       Initial upscale factor
  --real                Perform operations in real space
```

To use a simulated image stack simple run:
```bash
$ measureNPS
```

### Plotting NPS

```bash
nps --input data/nps/*.npz --output nps.svg 
```

### DQE
```bash
$ usage: calculateDQE [-h] --mtf MTF --nps NPS [--dqe0 DQE0] [--store STORE] [--name NAME]

options:
  -h, --help     show this help message and exit
  --mtf MTF      Input measured MTF curve (.npz file)
  --nps NPS      Input measured NPS curve (.npz file)
  --dqe0 DQE0    Assumed DQE(0)
  --store STORE  Store output measured DQE curve (.npz file)
  --name NAME    Label to store with measured DQE curve (default basename of file)
```

### Plotting DQE

```bash
dqe --published --input data/dqe/*.npz --output dqe.svg 
```

## References

MTF and NPS measurements and calculation methods were primarily based on these two papers:

* G. McMullan, S. Chen, R. Henderson, A. R. Faruqi, Detective quantum efficiency of electron area detectors in electron microscopy. Ultramicroscopy. 109, 1126–1143 (2009). https://doi.org/10.1016/j.ultramic.2009.04.002
* K. A. Paton, M. C. Veale, X. Mu, C. S. Allen, D. Maneuski, C. Kübel, V. O’Shea, A. I. Kirkland, D. McGrouther, Quantifying the performance of a hybrid pixel detector with GaAs:Cr sensor for transmission electron microscopy. Ultramicroscopy. 227, 113298 (2021). https://doi.org/10.1016/j.ultramic.2021.113298

Additional inspiration on how to measure the edge spread function from a slanted edge was also from:

* https://github.com/u-onder/mtf.py

### Published MTF and DQE curves

MTF curves are from Relion STAR files:

https://github.com/3dem/relion/tree/ver3.1/data

DQE curves for Falcon3 at 300 kV are extracted from here:

* M. Kuijper, G. van Hoften, B. Janssen, R. Geurink, S. D. Carlo, M. Vos, G. van Duinen, B. van Haeringen, M. Storms, FEI’s direct electron detector developments: Embarking on a revolution in cryo-TEM. J Struct Biol. 192, 179–187 (2015). https://doi.org/10.1016/j.jsb.2015.09.014
* G. McMullan, A. R. Faruqi, D. Clare, R. Henderson, Comparison of optimal performance at 300keV of three direct electron detectors for use in low dose electron microscopy. Ultramicroscopy. 147, 156–163 (2014). https://doi.org/10.1016/j.ultramic.2014.08.002

## TODOs
Making these scripts into a package was mostly an afterthought. Some things need still to be fixed as a result.

* Refactor all scripts to truly run from main(), this now done with a hack in setup.py
  * This currently causes all exceptions to occur during library loading
* Better script names for plotting

## Authors

* Paul van Schayck - p.vanschayck@maastrichtuniversity.nl
* Yue Zhang - yue.zhang@maastrichtuniveristy.nl
* Raimond Ravelli - rbg.ravelli@maastrichtuniversity.nl (corresponding)

## Copyright

Maastricht University

## License

MIT license