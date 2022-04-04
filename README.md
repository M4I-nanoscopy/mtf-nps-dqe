# Measuring/calculating MTF, NPS and DQE

Scripts for measuring MTF and NPS, and thereby calculating DQE. Useful for 
evaluating low-dose cryogenic electron microscopy detectors.

### Modulation Transfer Function (MTF)

The MTF is measured using the knife-edge method. The edge spread function (ESF) is measured by determining the edge angle, 
and using this to plot pixels values as function of the distance to the edge. This is fitted to a expression describing 
the ESF. From the fitted parameter the MTF is directly calculated.

### Noise Power Spectrum (NPS) or Wiener Spectrum

The NPS is measured using a series of flat field exposures. Challenging is estim

### Detective Quantum Efficiency (DQE)

Using the MTF and NPS, the DQE can be calculated. Hereby is DQE(0) (a scaling factor) assumed to be a certain value. 
To actually measure DQE(0) you need an accurate way to measure the conversion factor (counts out/flux in) of the detector. 

## Installation

Requires Python3 > 3.7

In a Python3 virtualenv install the requirements.
```bash
python3 -m venv dqe-mtf-venv
source dqe-mtf-venv/bin/activate
pip3 install -r requirements.txt
```

## Running

### MTF
```bash
$ python3 mtf/measureMTF.py --help
usage: measureMTF.py [-h] [-x X] [-y Y] [--width WIDTH] [--height HEIGHT] [--store STORE] [--super_res SUPER_RES] [--rotate ROTATE] [FILE]

positional arguments:
  FILE                  Input image (tif). If none supplied, an edge will be simulated

optional arguments:
  -h, --help            show this help message and exit
  -x X                  Starting x coordinate of crop
  -y Y                  Starting y coordinate of crop
  --width WIDTH         Width of crop
  --height HEIGHT       Height of crop
  --store STORE         Store output measured MTF curve
  --super_res SUPER_RES
                        Rescale the frequency of the measured MTF curve by this factor
  --rotate ROTATE       Number of times to rotate the image clockwise
```
Starting without coordinates will show a dialog to select the area for cropping. Starting without

```bash
python3 mtf/measureMTF.py data/edge/image.tif
```

To run a simulated edge simple use

```bash
python3 mtf/measureMTF.py
```

### Plotting MTF

```bash
python3 mtf/mtf.py --input data/mtf/*.npz
```


### NPS
```bash
$ python3 nps/measureNPS.py --help
usage: measureNPS.py [-h] [--super_res SUPER_RES] [--store STORE] [FILE]

positional arguments:
  FILE                  Input image stack of flat fields (mrcs).

optional arguments:
  -h, --help            show this help message and exit
  --super_res SUPER_RES
                        Rescale the frequency of the measured NPS curve by this factor
  --store STORE         Store output measured MTF curve
```

### DQE
```bash
$ python3 dqe/calculateDQE.py --help
usage: calculateDQE.py [-h] --mtf MTF --nps NPS [--dqe0 DQE0] [--store STORE] [--name NAME]

optional arguments:
  -h, --help     show this help message and exit
  --mtf MTF      Input measured MTF curve
  --nps NPS      Input measured NPS curve
  --dqe0 DQE0    Assumed DQE(0)
  --store STORE  Store output measured DQE curve
  --name NAME    Label to store with measured DQE curve (default basename of file)
```
