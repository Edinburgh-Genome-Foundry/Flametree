import ez_setup

ez_setup.use_setuptools()

from setuptools import setup, find_packages

exec(open("flametree/version.py").read())  # loads __version__

setup(
    name="flametree",
    version=__version__,
    author="Zulko",
    description="Python file and zip operations made easy",
    url="https://github.com/Edinburgh-Genome-Foundry/Flametree",
    long_description=open("pypi-readme.rst").read(),
    license="MIT",
    keywords="file system, zip, archive, file, directory",
    packages=find_packages(exclude="docs"),
)
