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
    'version': '0.1.5.3',
    'author': 'Markus Pioch',
    'author_email': 'pioch@mpi-magdeburg.mpg.de',
    'python_requires':'>=2.6, <3',
    'install_requires': ['numpy','pyopenms','lxml','canvasvg','configparser','pyperclip','xlwt'],
    'packages': ['glyxtoolms', 'glyxtoolms.gui','glyxtoolms.TOPP'],
    'package_data':{'glyxtoolms.gui': ['resources/*.gif','resources/isotope_confidence.pickle'],
                    'glyxtoolms.TOPP': ['ConsensusSearch.py',
                        'ConsensusSearch.ttd',
                        'FeatureExtractor.py',
                        'FeatureExtractor.ttd',
                        'FeatureFinderMS.py',
                        'FeatureFinderMS.ttd',
                        'FileBuilder.py',
                        'FileBuilder.ttd',
                        'FragmentationTypeExtractor.py',
                        'FragmentationTypeExtractor.ttd',
                        'FragmentationTypeFilesplitter.py',
                        'FragmentationTypeFilesplitter.ttd',
                        'FragmentCheck.py',
                        'FragmentCheck.ttd',
                        'GlycanBuilder.py',
                        'GlycanBuilder.ttd',
                        'GlycanScorer.py',
                        'GlycanScorer.ttd',
                        'GlycoDomainViewer.py',
                        'GlycoDomainViewer.ttd',
                        'GlycoIdentificationScore.py',
                        'GlycoIdentificationScore.ttd',
                        'GlycopeptideDigest.py',
                        'GlycopeptideDigest.ttd',
                        'GlycopeptideMatcher.py',
                        'GlycopeptideMatcher.ttd',
                        'GlycopeptideTable.py',
                        'GlycopeptideTable.ttd',
                        'glyxFilter.py',
                        'glyxFilter.ttd',
                        'glyxReporter.py',
                        'glyxReporter.ttd',
                        'HexNAcRatio.py',
                        'HexNAcRatio.ttd',
                        'HGIReporter.py',
                        'HGIReporter.ttd',
                        'IdentificationDiscriminator.py',
                        'IdentificationDiscriminator.ttd',
                        'IdentificationMerger.py',
                        'IdentificationMerger.ttd',
                        'IdentificationTransfer.py',
                        'IdentificationTransfer.ttd',
                        'OxoniumFilter.py',
                        'OxoniumFilter.ttd',
                        'PdfReporter.py',
                        'PdfReporter.ttd',
                        'PeptideFilter.py',
                        'PeptideFilter.ttd',
                        'PeptideScorer.py',
                        'PeptideScorer.ttd',
                        'RemoveFeatures.py',
                        'RemoveFeatures.ttd',
                        'RobustPeakPicker.py',
                        'RobustPeakPicker.ttd'] },
    'scripts': [],
    'entry_points': {
        'gui_scripts': [
            'glyxtoolms = glyxtoolms.gui.__main__:main']
                    },
    'keywords': 'glycan glycopeptide glycoproteomics openms analysis',
    'include_package_data':True
}

setup(**config)
