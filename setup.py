try:
    from setuptools import setup
    print "using setuptools"
except ImportError:
    from distutils.core import setup
    print "using setup from distutil"

config = {
    'name': 'glyxtoolms',
    'description': 'glyxtoolms - python tools for glycopeptide analysis with OpenMS',
    'long_description': """ glyXtoolMS provides a) scripts for glycopeptide analysis 
 within the OpenMS proteomics framework (using the TOPPAS pipeline 
 engine) and a visulization / evaluation tool for further manual analysis of the results. 
 Source code available under https://github.com/glyXera/glyXtoolMS""",
    'license': 'GPL-3.0',
    'version': '0.1.3',
    'author': 'Markus Pioch',
    'author_email': 'pioch@mpi-magdeburg.mpg.de',
    'python_requires':'>=2.6, <3',
    'install_requires': ['numpy','pyopenms','lxml','canvasvg','configparser','pyperclip','xlwt'],
    'packages': ['glyxtoolms', 'glyxtoolms.gui'],
    'package_data':{'glyxtoolms.gui': ['resources/*.gif','resources/isotope_confidence.pickle']},
    'data_files':[('TOPP',["TOPP/ConsensusSearch.py",
                           "TOPP/ConsensusSearch.ttd",
                           "TOPP/FeatureExtractor.py",
                           "TOPP/FeatureExtractor.ttd",
                           "TOPP/FeatureFinderMS.py",
                           "TOPP/FeatureFinderMS.ttd",
                           "TOPP/FileBuilder.py",
                           "TOPP/FileBuilder.ttd",
                           "TOPP/GlycanBuilder.py",
                           "TOPP/GlycanBuilder.ttd",
                           "TOPP/GlycoDomainViewer.py",
                           "TOPP/GlycoDomainViewer.ttd",
                           "TOPP/GlycoIdentificationScore.py",
                           "TOPP/GlycoIdentificationScore.ttd",
                           "TOPP/GlycopeptideDigest.py",
                           "TOPP/GlycopeptideDigest.ttd",
                           "TOPP/GlycopeptideMatcher.py",
                           "TOPP/GlycopeptideMatcher.ttd",
                           "TOPP/GlycopeptideTable.py",
                           "TOPP/GlycopeptideTable.ttd",
                           "TOPP/glyxFilter.py",
                           "TOPP/glyxFilter.ttd",
                           "TOPP/glyxReporter.py",
                           "TOPP/glyxReporter.ttd",
                           "TOPP/PeptideFilter.py",
                           "TOPP/PeptideFilter.ttd"]),
                    ('docs',['docs/glyXtoolMS Usermanual.pdf']),
                ],
    'scripts': [],
    'entry_points': {
        'gui_scripts': [
            'glyxtoolms = glyxtoolms.gui.__main__:main']
                    },
    'keywords': 'glycan glycopeptide glycoproteomics openms analysis'
}

setup(**config)
