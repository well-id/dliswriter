from setuptools import setup, find_packages
from pathlib import Path


with open(Path(__file__).parent/"README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='dlis-writer',
    version='0.0.1',
    python_requires='>=3.10',
    packages=find_packages(),
    url='https://github.com/well-id/dlis-writer',
    license='',
    author='WellID',
    author_email='dominika.dlugosz@wellid.no',
    description='Create DLIS format files for well data.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    package_data={'': ['tests/resources/*']},
    include_package_data=True
)
