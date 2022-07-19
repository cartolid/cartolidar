'''
Created on 9 may 2022

@author: benmarjo
'''
# Se ejecuta cuando se llama al paquete en linea de comandos con \>python -m clidtools

import os
import importlib
import importlib.util

if __name__ == '__main__':
    print('clidtools-> Menu de herramientas de cartolidar')
    print('\t1. clidtwins')
    print('\t2. clidmerge')
    selec = input('Elije opcion (0): ')
    try:
        nOpcionElegida = int(selec)
    except:
        nOpcionElegida = 0
    if nOpcionElegida == 1:
        print('\nSe ha elegido ejecutar clidtwuins de forma interactiva')
        # import clidtwins
        spec = importlib.util.find_spec('cartolidar')
        if not spec is None:
            from cartolidar.clidtools.clidtwins import DasoLidarSource
        else:
            try:
                from cartolidar.clidtools.clidtwins import DasoLidarSource
            except:
                if '-v' in sys.argv or '--verbose' in sys.argv:
                    print(f'clidttools__main__-> Aviso: cartolidar no esta instalado en site-packages (se esta ejecutando una version local sin instalar).\n')
                    print(f'\t-> Se importa clidconfig desde clidtwcfg del directorio local {os.getcwd()}/clidtools.\n')
                from clidtools.clidtwins import DasoLidarSource
        # print('Metodos de DasoLidarSource: {}'.format(dir(DasoLidarSource)))
    elif nOpcionElegida == 1:
        print('\nOpcion clidmerge no disponible por el momento.')
    else:
        print('\nElegir una de las opciones disponibles.')
    print('Fin de clidtools')