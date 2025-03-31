from setuptools import setup, find_packages

version = {}
with open("flametree/version.py") as fp:
    exec(fp.read(), version)

setup(
    name="flametree",
    version=version["__version__"],
    author="Zulko",
    description="Python file and zip operations made easy",
    url="https://github.com/Edinburgh-Genome-Foundry/Flametree",
    long_description=open("pypi-readme.rst").read(),
    license="MIT",
    keywords="file system, zip, archive, file, directory",
    packages=find_packages(exclude="docs"),
)
