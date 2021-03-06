# Copyright (C) 2010-2017 The Free Software Foundation, Inc.
#
# This file is part of mailman.client.
#
# mailman.client is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# mailman.client is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mailman.client.  If not, see <http://www.gnu.org/licenses/>.

from setup_helpers import description, get_version, require_python
from setuptools import setup, find_packages


require_python(0x20600f0)
__version__ = get_version('src/mailmanclient/constants.py')


setup(
    name='mailmanclient',
    version=__version__,
    packages=find_packages('src'),
    description='mailmanclient -- python library for Mailman REST API',
    long_description=description('README.rst'),
    package_dir={'': 'src'},
    include_package_data=True,
    maintainer='Barry Warsaw',
    maintainer_email='barry@list.org',
    license='LGPLv3',
    url='https://www.list.org/',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)', # noqa
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP ',
    ],
    install_requires=[
        'httplib2',
        'six',
        ],
    )
