from setuptools import setup, find_packages
import os
# To use a consistent encoding
from codecs import open

here = os.path.abspath(os.path.dirname(__file__))


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mtf-nps-dqe",
    version="0.9.0",
    packages=find_packages(),
    install_requires=[
        "matplotlib>=3.0.0,<4.0.0",
        "Pillow>9.0.0,<10.0.0",
        "scipy>1.7.0,<2.0.0",
        "numpy>=1.16.0,<2.0.0",
        "tqdm>=4.0.0,<5.0",
        "mrcfile>1.0.0,<2.0.0",
        "scikit-image>0.17<1.0.0"
    ],
    # package_data={ },
    author="Paul van Schayck",
    description="Python scripts for measuring MTF and NPS, and thereby calculating DQE.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/M4I-nanoscopy/mtf-nps-dqe",
    project_urls={
        "Bug Tracker": "https://github.com/M4I-nanoscopy/mtf-nps-dqe/issues",
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
    ],
    entry_points={
        'console_scripts': [
            'measureMTF = mtf.measureMTF:main',
        ], }
)