# glyXtoolMS

glyXtoolMS is a (semi-) automated software for the targeted analysis of glycopeptide mass spectrometry data, based on OpenMS

## Getting Started

### Prerequisites

In order to run glyXtoolMS a python 2.7.x envirunment and OpenMS have to be installed. 

#### OpenMS
For installation of OpenMS visit https://www.openms.de/ and follow the download/install or build instructions for your operating system.
After installation the following tools should be available: TOPPAS and TOPPView. 

#### Python
To run glyXtoolMS, a python 2.7 installation is required, together with the package manager pip. The use of a virtual environment like virtualenvwrapper is recommended, to handle p

Install python 2.7 from [https://www.python.org/](https://www.python.org/). The package manager for python will then be installed, too. To check this, open a console and type the command “pip”. If it has not been installed, follow the installation instructions on [https://pip.pypa.io/en/stable/installing/#do-i-need-to-install-pip](https://pip.pypa.io/en/stable/installing/#do-i-need-to-install-pip).

The use of a virtual environment is recommended, in case multiple python installations with different package setups are installed on the computer. For the installation of virtualenvwrapper, please refer to [https://virtualenvwrapper.readthedocs.io/en/latest/](https://virtualenvwrapper.readthedocs.io/en/latest/)

Virtualenvwrapper can be installed via pip:

> pip install virtualenvwrapper

afterwards a new environment can be created using:

> mkvirtualenv \<envname\>

switch into the environment using:

> workon \<envname\>

#### glyXtoolMS
glyXtoolMS can then be installed using pip:

> pip install glyXtoolMS

The dependencies canvasvg, configparser, lxml ,numpy,pyopenms, pyperclip, and xlwt should then be automatically downloaded and installed.

alternatively the .egg or .wheel can be downloaded from [https://test.pypi.org/project/glyxtoolms/](https://test.pypi.org/project/glyxtoolms/)

or build manually from [www.github.com/mpioch/glyXtoolMS](http://www.github.com/mpioch/glyXtoolMS)

After the installation of glyXtoolMS, the glyXtoolMS Evaluator should be acessable via the console command:

> glyxtoolms

To complete the installation of TOPAS/glyXtoolMS the path to the OpenMS installation will be requested during the first run of glyXtoolMS and the necessary TOPPAS scripts will be copied to the OpenMS installation. Within this window, also newly downloaded TOPPAS workflows can be adapted to the new OpenMS script path.

## Analysing the Example data sets
An example data set can be downloaded from PRIDE via https://www.ebi.ac.uk/pride/archive/projects/PXD009716 containing an human IgG and human fibrinogen mass spectrometry file, the N-glycan database, the FASTA files, the TOPPAS workflow,s and the resulting analysis files. The procedure for handling and analyzing the data file is detailed within the documentation.

## Authors

* **Markus Pioch** - *Initial work* - [mpioch](https://github.com/mpioch)
* **Dr. Erdmann Rapp** 

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* Alexander Behne
* Terry Nguyen-Khuong
* Stackoverflow


 

