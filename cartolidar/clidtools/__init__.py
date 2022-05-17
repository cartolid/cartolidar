print(f'clidtools.__init__-> __name__:     <{__name__}>')
print(f'clidtools.__init__-> __package__ : <{__package__ }>')
# from cartolidar.clidtools.clidtwins_config import GLO # GLO es una variable publica del modulo clidtwins_config
# from cartolidar.clidtools.clidtwins import DasoLidarSource # DasoLidarSource es la clase principal del modulo clidtwins
# from cartolidar.clidtools.clidtwins import mostrarListaDrivers # mostrarListaDrivers es una funcion del modulo clidtwins
# __all__ = [
#     'GLO',
#     'DasoLidarSource',
#     'mostrarListaDrivers'
# ]

from .clidtwins_config import GLO # GLO es una variable publica del modulo clidtwins_config
from .clidtwins import DasoLidarSource # DasoLidarSource es la clase principal del modulo clidtwins
from .clidtwins import mostrarListaDrivers # mostrarListaDrivers es una funcion del modulo clidtwins
__all__ = [
    'GLO',
    'DasoLidarSource',
    'mostrarListaDrivers'
]


# from . import clidtwins # Inlcuye DasoLidarSource, mostrarListaDrivers, etc.
# from . import clidtwins_config # Incluye GLO, que es una variable publica del modulo clidtwins_config
# __all__ = [
#     'clidtwins',
#     'clidtwins_config',
# ]

