from setuptools import setup, find_packages

setup(
    name='dashup',          # name which is available if installed
    version='0.1.0',
    packages=find_packages(),
    install_requires = [
        'toml',
        'requests',
        'argparse',
        'netifaces'
    ],
    entry_points = {
        'console_scripts': [
            'dashup = dashup.main:main'
        ]
    }
)