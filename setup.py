from setuptools import setup, find_packages
import codecs
import os
import re

here = os.path.abspath(os.path.dirname(__file__))

def find_version(*file_paths):
    with codecs.open(os.path.join(here, *file_paths), 'r', 'latin1') as f:
        version_file = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name="AbleTable",
    version=find_version('qtjsonschema', '__init__.py'),
    description="AbleTable - the simple, powerful CSV editor.",
    url='https://github.com/abletable/abletable',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],

    keywords='abletable csv pyqt qt numpy',

    packages=find_packages(exclude=["contrib", "docs", "tests*"]),
    install_requires = [
        "pyqt5",
        "click",
        "jsonschema",
    ],
)


