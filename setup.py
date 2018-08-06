from setuptools import setup

setup(
    name = 'jenky',
    version = '0.1.0',
    packages = ['jenky'],
    entry_points = {
        'console_scripts': [
            'jenky = jenky.__init__:main'
        ]
    })
