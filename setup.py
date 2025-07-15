from pathlib import Path
from setuptools import setup, find_packages

# Read version from package
from standdown import __version__

setup(
    name='standdown',
    version=__version__,
    author='Jovan Lukovic',
    description='Minimal CLI and server for asynchronous standups',
    long_description=Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    license='AGPL-3.0-or-later',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'uvicorn',
        'SQLAlchemy',
        'colorama',
    ],
    entry_points={
        'console_scripts': [
            'standdown=standdown.__main__:main',
            'sd=standdown.__main__:main',
        ]
    },
)
