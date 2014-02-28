try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'glyxsuite - python tools for glycopeptide analysis with openMS',
    'author': 'Markus Pioch',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'My email.',
    'version': '0.1',
    'install_requires': ['pyopenms'],
    'packages': ['glyxsuite'],
    'scripts': [],
    'name': 'glyxsuite'
}

setup(**config)
