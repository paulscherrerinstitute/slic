from setuptools import setup, find_packages

setup(
    name="slic",
    version="0.2.0",
    url="https://gitea.psi.ch/slic/slic",
    description="SwissFEL Library for Instrument Control",
    author="Paul Scherrer Institute",
    packages=find_packages(),
    package_data={"slic.ai": ["*.md"]}
)


