from setuptools import setup, find_packages

setup(
    name='standdown',
    version='0.1.0',
    author='Jovan Lukovic',
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
    }
)
