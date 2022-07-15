#!/usr/bin/env/python
# -*- coding: cp1252 -*-
"""Installation script for cartolidar
# -*- coding: UTF-8 -*-
"""

import os
import sys
import re
import codecs

import setuptools
# from setuptools import find_packages
# from setuptools import setup

# Ver https://bernat.tech/posts/pep-517-518/
# Ver https://packaging.python.org/guides/distributing-packages-using-setuptools/
# Ver https://github.com/pypa/sampleproject

packages=setuptools.find_packages()
print('\npackages encontrados:', packages)

# Ver https://docs.python.org/3/distutils/setupscript.html

# # Por ahora no uso versioneer
# #   Ver https://pypi.org/project/versioneer/
# # ensure the current directory is on sys.path so versioneer can be imported
# # when pip uses PEP 517/518 build rules.
# # https://github.com/python-versioneer/python-versioneer/issues/193
# sys.path.append(os.path.dirname(__file__))
# import versioneer

# Ver https://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package
VERSIONFILE = 'cartolidar/_version.py'
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))
print('version:', verstr)

rutaTrabajo = sys.prefix
HERE = os.path.abspath(os.path.dirname(__file__))
print('rutaTrabajo:', rutaTrabajo)
print('HERE:       ', HERE)

utf8Ok = True
try:
    f = codecs.open('README.md', encoding='utf-8', errors='strict')
    for line in f:
        pass
except UnicodeDecodeError:
    utf8Ok = False
ansiOk = True
try:
    f = codecs.open('README.md', encoding='windows-1250', errors='strict')
    for line in f:
        pass
except UnicodeDecodeError:
    ansiOk = False

if utf8Ok:
    myCode = 'utf-8'
else:
    myCode = 'windows-1250'

with open(os.path.join(HERE, 'README.md'), encoding=myCode) as fid:
    README = fid.read()

INSTALL_REQUIRES = [
    'gdal >= 3.0.2',
    'numpy >= 1.19.1',
    'scipy >= 1.4.1',
    'psutil >= 5.7.0',
	'dbfread >= 2.0.7',
	'pytest >= 7.1.2',
    'numba == 0.53.0',
	# 'TensorFlow >= 2.3.0',
	# 'keras >= 2.4.3',
	# 'pandas>= 1.0.5',
	# 'h5py >= 2.10.0',
	# 'matplotlib >= 3.2.2',
	# 'PIL >= 7.2.0',
	# 'numba >= 0.50.1',
	# 'graphviz >= 0.11.1',
	# 'openpyxl >= 3.0.5',
]

datapath1 = os.path.abspath('cartolidar/data')
datapath2 = os.path.abspath('cartolidar/data/asc')
datapath3 = os.path.abspath('cartolidar/data/ext')
datapath4 = os.path.abspath('cartolidar/data/ext/io')
datapath5 = os.path.abspath('cartolidar/data/mfe')
datapath6 = os.path.abspath('cartolidar/data/ref')
# print('Elementos en {}:\n\t{}'.format(HERE, os.listdir(HERE)))
# print('Elementos en {}:\n\t{}'.format(os.path.join(HERE, 'cartolidar'), os.listdir(os.path.join(HERE, 'cartolidar'))))
# print('Elementos en {}:\n\t{}'.format(os.path.abspath('cartolidar'), os.listdir('cartolidar')))
# print('NO se buscan los data_files en:', os.path.join(HERE, 'cartolidar/data'))
print('\nSI se buscan los data_files en: {}:\n\t {}'.format(datapath1, os.listdir(datapath1)))
print('SI se buscan los data_files en: {}:\n\t {}'.format(datapath2, os.listdir(datapath2)))
print('SI se buscan los data_files en: {}:\n\t {}'.format(datapath3, os.listdir(datapath3)))
print('SI se buscan los data_files en: {}:\n\t {}'.format(datapath4, os.listdir(datapath4)))
print('SI se buscan los data_files en: {}:\n\t {}'.format(datapath5, os.listdir(datapath5)))
print('SI se buscan los data_files en: {}:\n\t {}'.format(datapath6, os.listdir(datapath6)))

# No creo directorio data dentro de la ruta del proyecto:
# datapath2 = os.path.join('cartolidar', 'cartolidar/data')
# try:
    # print('Data_files en {}: {}'.format(os.path.abspath('cartolidar/data'), os.listdir('cartolidar/data'))
# except OSError as my_error:
    # print('type(my_error):', type(my_error))    # the exception instance
    # print('my_error.args: ', my_error.args)     # arguments stored in .args
    # print('my_error:      ', my_error)
    # print('No existe la ruta: {}'.format(os.path.abspath('cartolidar/data'))

# get all data dirs in the datasets module
data_files = []
for item in os.listdir(datapath1):
    # print('item1:', os.path.abspath(os.path.join(datapath1, item)), os.path.isdir(os.path.join(datapath1, item)))
    if not item.startswith('__'):
        if os.path.isdir(os.path.join(datapath1, item)):
            data_files.append(os.path.join(datapath1, item, '*.*'))
            # print('\t->', os.path.join(datapath1, item, '*.*'))
        elif item.endswith('.zip'):
            data_files.append(os.path.join(datapath1, item))
            # print('\t->', os.path.join(datapath1, item))
# print('data_files1:', data_files)
for item in os.listdir(datapath2):
    # print('item2:', os.path.abspath(os.path.join(datapath2, item)), os.path.isdir(os.path.join(datapath2, item)))
    if not item.startswith('__'):
        if os.path.isdir(os.path.join(datapath2, item)):
            data_files.append(os.path.join(datapath2, item, '*.*'))
            # print('\t->', os.path.join(datapath2, item, '*.*'))
        elif item.endswith('.zip'):
            data_files.append(os.path.join(datapath2, item))
            # print('\t->', os.path.join(datapath2, item))
# print('data_files2:', data_files)
for item in os.listdir(datapath3):
    # print('item3:', os.path.abspath(os.path.join(datapath3, item)), os.path.isdir(os.path.join(datapath3, item)))
    if not item.startswith('__'):
        if os.path.isdir(os.path.join(datapath3, item)):
            data_files.append(os.path.join(datapath3, item, '*.*'))
            # print('\t->', os.path.join(datapath3, item, '*.*'))
        elif item.endswith('.zip'):
            data_files.append(os.path.join(datapath3, item))
            # print('\t->', os.path.join(datapath3, item))
print('data_files3:', data_files)
for item in os.listdir(datapath4):
    # print('item4:', os.path.abspath(os.path.join(datapath4, item)), os.path.isdir(os.path.join(datapath4, item)))
    if not item.startswith('__'):
        if os.path.isdir(os.path.join(datapath4, item)):
            data_files.append(os.path.join(datapath4, item, '*.*'))
            # print('\t->', os.path.join(datapath4, item, '*.*'))
        elif item.endswith('.zip'):
            data_files.append(os.path.join(datapath4, item))
            # print('\t->', os.path.join(datapath4, item))
print('data_files4:', data_files)
for item in os.listdir(datapath5):
    # print('item5:', os.path.abspath(os.path.join(datapath5, item)), os.path.isdir(os.path.join(datapath5, item)))
    if not item.startswith('__'):
        if os.path.isdir(os.path.join(datapath5, item)):
            data_files.append(os.path.join(datapath5, item, '*.*'))
            # print('\t->', os.path.join(datapath5, item, '*.*'))
        elif item.endswith('.zip'):
            data_files.append(os.path.join(datapath5, item))
            # print('\t->', os.path.join(datapath5, item))
print('data_files5:', data_files)
for item in os.listdir(datapath6):
    # print('item6:', os.path.abspath(os.path.join(datapath6, item)), os.path.isdir(os.path.join(datapath6, item)))
    if not item.startswith('__'):
        if os.path.isdir(os.path.join(datapath6, item)):
            data_files.append(os.path.join(datapath6, item, '*.*'))
            # print('\t->', os.path.join(datapath6, item, '*.*'))
        elif item.endswith('.zip'):
            data_files.append(os.path.join(datapath6, item))
            # print('\t->', os.path.join(datapath6, item))
print('data_files6:', data_files)

# data_files.append('tests/data/*')

setuptools.setup(
    name='cartolidar',
	# Versions should comply with PEP 440:
    # 	https://www.python.org/dev/peps/pep-0440/
    # version=versioneer.get_version(),
    # version='0.0a4',
    version=verstr,
    description='Lidar data processing tools focused on Spanish PNOA datasets',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/cartolid/cartolidar',
    project_urls={
        "Source": 'https://github.com/cartolid/cartolidar',
		"Bug Reports":  'https://github.com/cartolid/cartolidar/issues',
		"PNOA Lidar data":  'https://centrodedescargas.cnig.es',
    },
    author='Jose Bengoa',
    author_email='cartolidar@gmail.com',
    license='GNU GPLv3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: Spanish',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: GIS',
    ],
	keywords='lidar, forestry, dasometry, dasoLidar, DLV, PNOA, GIS, DEM, DTM, DSM',

    python_requires='>=3.7',
	# Ver https://docs.python.org/3/distutils/setupscript.html#listing-whole-packages
    # Esto da error (creo que solo se necesita si los modulos estan en un subdirectorio tipo "src":
    # packages=setuptools.find_packages(where='cartolidar'),
    # Alternativa (tambien da error):
    # package_dir={'': 'cartolidar'}
    packages=setuptools.find_packages(),
    # Otra alternativa es enumerar los paquetes explicitamente:
    # packages=[
        # 'cartolidar',
        # 'cartolidar.clidtools',
        # 'cartolidar.clidax',
    # ],
    install_requires=INSTALL_REQUIRES,

	# Para ficheros adicionales ver: http://docs.python.org/distutils/setupscript.html#installing-additional-files
    package_data={"": data_files},
    include_package_data=True,

	# Para entry_points ver:
	#	https://setuptools.pypa.io/en/latest/userguide/entry_point.html#dynamic-discovery-of-services-and-plugins
	#	https://docs.pytest.org/en/latest/how-to/writing_plugins.html
	#	https://docs.pytest.org/en/latest/how-to/plugins.html#using-plugins
	# 	https://stackoverflow.com/questions/774824/explain-python-entry-points
	# No lo uso porque no lo tengo bien configurado y me da error al instalar el paquete subido a pypi:
    # entry_points={'console_scripts': ['qlidtwins=cartolidar.qlidtwins']},
    # cmdclass=versioneer.get_cmdclass(),
)


#Para classifiers, ver https://pypi.org/pypi?%3Aaction=list_classifiers

#Aviso obsoleto: para incluir las carpetas auxiliares y otros ficheros uso el MANIFEST.in en lugar de la linea:
#    package_data={'': ['README.md', 'LICENSE', 'clidpar/clidax']},
#Aunque mantengo la linea:
#    include_package_data=True,
#Ver:
# https://stackoverflow.com/questions/1612733/including-non-python-files-with-setup-py
# https://stackoverflow.com/questions/1471994/what-is-setup-py