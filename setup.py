#!python3
# -*- coding: utf-8 -*-

from setuptools import setup

# Define package info
with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name = 'pycoQC',
    description = 'PycoQC computes metrics and generates interactive QC plots for Oxford Nanopore technologies sequencing data',
    version = '3.0.0',
    long_description = long_description,
    long_description_content_type='text/markdown',
    url = 'https://github.com/a-slide/pycoQC',
    author = 'Adrien Leger & Tommaso Leonardi',
    author_email = 'aleg@ebi.ac.uk',
    license = 'GPLv3',
    python_requires ='>=3.12',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14'],
    install_requires = [
        'numpy>=2.5,<3',
        'scipy>=1.18,<2',
        'pandas>=3.1,<4',
        'plotly>=7.2,<8',
        'jinja2>=3.1,<4',
        'markupsafe>=3.0,<4',
        'h5py>=3.16,<4',
        'tqdm>=4.70,<5',
        'pysam>=0.24,<1'],
    extras_require = {'test': ['pytest>=8']},
    packages = ['pycoQC'],
    package_dir = {'pycoQC': 'pycoQC'},
    package_data = {'pycoQC': ['templates/*']},
    entry_points = {
        'console_scripts': [
            'pycoQC=pycoQC.__main__:main_pycoQC',
            'Fast5_to_seq_summary=pycoQC.__main__:main_Fast5_to_seq_summary',
            'Barcode_split=pycoQC.__main__:main_Barcode_split']}
)
