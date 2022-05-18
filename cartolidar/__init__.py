import sys

__version__ = '0.0a2'
if '-vvv' in sys.argv:
    __verbose__ = 3
elif '-vv' in sys.argv:
    __verbose__ = 2
elif '-v' in sys.argv or '--verbose' in sys.argv:
    __verbose__ = 1
else:
    __verbose__ = 0
if __verbose__ > 2:
    print(f'cartolidar.__init__-> __name__:     <{__name__}>')
    print(f'cartolidar.__init__-> __package__ : <{__package__ }>')

# from cartolidar import clidtools
# from cartolidar import clidax
# from cartolidar.clidtools.clidtwins import DasoLidarSource
# from . import clidtools
# from . import clidax
# from clidtools.clidtwins import DasoLidarSource
# __all__ = [
#     'clidtools',
#     'clidax',
#     'DasoLidarSource',
# ]
