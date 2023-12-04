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
    package_data={'': ['resources/*', 'py.typed']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'write_file=dlis_writer.writer.write_dlis_file:main',
            'generate_synthetic_file=dlis_writer.writer.write_synthetic_dlis_file:main',
            'generate_synthetic_data=dlis_writer.writer.synthetic_data_generator:main',
            'make_config_from_file=dlis_writer.writer.config:main',
            'compare_files=dlis_writer.writer.dlis_file_comparator:main'
        ]
    }
)
