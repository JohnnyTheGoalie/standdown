from setuptools import setup

setup(
    name='standdown',
    version='0.1.0',
    author='Jovan Lukovic',
    packages=['standdown'],
    entry_points={
        "console_scripts": [
            "standdown=standdown.__main__:main",
            "sd=standdown.__main__:main",
        ]
    }
)