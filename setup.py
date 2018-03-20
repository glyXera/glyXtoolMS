try:
    from setuptools import setup
    print "using setuptools"
except ImportError:
    from distutils.core import setup
    print "using setup from distutil"

config = {
    'description': 'glyxtoolms - python tools for glycopeptide analysis with OpenMS',
    'author': 'Markus Pioch',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'pioch@mpu-magdeburg.mpg.de',
    'version': '0.1',
    'install_requires': ['numpy','pyopenms','lxml','canvasvg','configparser','pyperclip','xlwt'],
    'packages': ['glyxtoolms'],
    'scripts': [],
    'name': 'glyxtoolms',
    'entry_points': {
        'gui_scripts': [
            'glyxtoolms = glyxtoolms.gui.__main__:main']
                    }
}

setup(**config)
