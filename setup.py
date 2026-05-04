from setuptools import setup, find_packages

setup(
    name='mypylib',
    version='0.1.0',
    description='Custom library for general python processes and plotting',
    author='Logan Halstrom',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        # Add other dependencies here
    ],
)
