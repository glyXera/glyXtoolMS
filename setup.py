try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'glyxtoolms - python tools for glycopeptide analysis with OpenMS',
    'author': 'Markus Pioch',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'My email.',
    'version': '0.1',
    'install_requires': ['pyopenms'],
    'packages': ['glyxtoolms'],
    'scripts': [],
    'name': 'glyxtoolms'
}

setup(**config)
