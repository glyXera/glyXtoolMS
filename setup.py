try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

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
    'name': 'glyxtoolms'
}

setup(**config)
