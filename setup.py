import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

install_requires = [
    'mistune>=3.0.1',
    'allianceauth>=4.0.0',
    'allianceauth-app-utils',
]

setup(
    name='aa-simplewiki',
    version='2.1.0',
    packages=find_packages(),
    include_package_data=True,
    exclude_package_data={'': ['images']},
    license='GNU General Public License v3 (GPLv3)',
    description='Alliance Auth Wiki Plugin',
    install_requires=install_requires,
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/meowosaurus/aa-simplewiki',
    author='Meowosaurus',
    author_email='info@bjsonnen.de',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)