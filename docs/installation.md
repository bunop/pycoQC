# Installation

## Create a clean virtual environment (optional but recommended)

Ideally, before installation, create a clean **python3.12+** virtual environment to deploy the package.
Older versions of Python are not supported by this release: use pycoQC 2.5.2 with Python 3.6 to 3.11.
For example one can use conda or virtualenvwrapper.

With [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html):

```bash
mkvirtualenv pycoQC -p python3.12
workon pycoQC
```

With [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html):

```bash
conda create -n pycoQC python=3.12
conda activate pycoQC
```

## Dependencies

pycoQC relies on a few robustly maintained third party libraries listed below. The correct versions of the packages are installed together with the software when using pip.

* numpy>=2.5
* scipy>=1.18
* pandas>=3.1
* plotly>=7.2
* jinja2>=3.1
* markupsafe>=3.0
* h5py>=3.16
* tqdm>=4.70
* pysam>=0.24

## Option 1: Installation with pip from pypi

Install or upgrade the package with pip from pypi

```bash
pip install pycoQC
```

You can also update to **unstable** development version from test.pypi repository

```bash
pip install --index-url https://test.pypi.org/simple/ pycoQC -U
```

## Option 2: Installation with conda from Anacounda cloud

**If you want to be sure to get the last version don't forget to add my channel and to specify the last version number**

```bash
# First installation
conda install -c aleg -c anaconda -c bioconda -c conda-forge pycoqc=[VERSION]
```

You can also get the **unstable** development version from my dev channel

```bash
conda install -c aleg_dev -c anaconda -c bioconda -c conda-forge pycoqc=[VERSION]
```

## Option 3: Installation with pip from Github

To get the last stable (master) or bleeding edge (dev) version

```bash
# First installation
pip install git+https://github.com/a-slide/pycoQC.git

# First installation bleeding edge
pip install git+https://github.com/a-slide/pycoQC.git@dev

# Update to last version
pip install git+https://github.com/a-slide/pycoQC.git --upgrade
```

## Option 4: Clone the repository and install locally in develop mode

With this option, the package will be locally installed in *editable* or *develop mode*. This allows the package to be both installed and editable in project form. This is the recommended option if you wish to modify the code and/or participate to the development of the package (see [contribution guidelines](contributing.md)).

```bash
# Clone stable repo locally
git clone https://github.com/a-slide/pycoQC.git

# bleeding edge branch
git clone --branch dev https://github.com/a-slide/pycoQC.git

# Enter in repo directory
cd pycoQC

# Make setup.py executable
chmod u+x setup.py

# Install with pip3
pip3 install -e ./
```
