#!/usr/bin/python
# encoding: utf-8
'''
cartolidar: Tools for Lidar processing focused on Spanish PNOA datasets

@author:     Jose Bengoa
@copyright:  2022 @clid
@license:    GNU General Public License v3 (GPLv3)
@contact:    cartolidar@gmail.com
@deffield    updated: 2022-05-17
'''
# Script interactivo para ejecucion con:
#   $ python -m cartolidar [options]
# Con esa instruccion se ejecuta pimero el __init__.py de cartolidar
# Completar cuando haya incluido varias herramientas

import sys
import os
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

# try:
#     import psutil
#     psutilOk = True
# except:
#     psutilOk = False

print(f'cartolidar.__main__-> __name__:     <{__name__}>')
print(f'cartolidar.__main__-> __package__:  <{__package__}>')
print(f'cartolidar.__main__-> sys.argv:     <{sys.argv}>')
print()

# from cartolidar.clidtools.clidtwins_config import GLO

__all__ = []
__version__ = '0.0.dev1'
__date__ = '2016-2022'
__updated__ = '2022-05-03'
__verbose__ = True


# ==============================================================================
def leerArgumentosEnLineaDeComandos(argv=None):
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    if os.path.basename(sys.argv[0]) == '__main__.py':
        if __package__ is None:
            program_name = 'cartoLidar'
        else:
            program_name = __package__
    else:
        program_name = os.path.basename(sys.argv[0])
    
    program_version = 'v{}'.format(__version__)
    program_build_date = str(__updated__)
    program_version_message = '{} {} ({})'.format(program_name, program_version, program_build_date)
    # program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    # program_shortdesc = __import__('__main__').__doc__
    program_shortdesc = '''  CartoLidar is a collection of tools to process lidar files "las" and "laz" and
  generate other products aimed to forestry and natural environment management.

  This project is in alpha version and includes only the "clidtwins" tool.

  "clidtwins" searchs for similar areas to a reference one in terms of dasoLidar Variables (DLVs)
  DLV: Lidar variables that describe or characterize forest structure (or vegetation in general).
'''

    program_license = '''{}

  Created by @clid {}.
  Licensed GNU General Public License v3 (GPLv3) https://fsf.org/
  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.
'''.format(program_shortdesc, str(__date__))

    # print('qlidtwins-> sys.argv:', sys.argv)

    # ==========================================================================
    # https://docs.python.org/es/3/howto/argparse.html
    # https://docs.python.org/3/library/argparse.html
    # https://ellibrodepython.com/python-argparse
    try:
        # Setup argument parser
        parser = ArgumentParser(
            description=program_license,
            formatter_class=RawDescriptionHelpFormatter,
            fromfile_prefix_chars='@',
            )
        # Opciones:
        parser.add_argument('-v', '--verbose',
                            dest='verbose',
                            action='count', # Cuenta el numero de veces que aparece la v (-v, -vv, -vvv, etc.)
                            # action="store_true",
                            help='set verbosity level [default: %(default)s]',
                            default = False,)
        parser.add_argument('-V', '--version',
                            action='version',
                            version=program_version_message,)

        parser.add_argument('-a',  # '--action',
                            dest='accionPrincipal',
                            type=int,
                            help=f'Accion a ejecutar: \n{accionesPrincipales[0]}; \n{accionesPrincipales[1]}. Default: %(default)s',
                            default = '0',)

        # parser.add_argument('-I', '--idProceso',
        #                     dest='idProceso',
        #                     type=int,
        #                     help='Numero aleatorio para identificar el proceso que se esta ejecutando (se asigna automaticamente; no usar este argumento)',)

        args = parser.parse_args()
        return args
    except KeyboardInterrupt:
        return None
    except TypeError:
        return None
    except Exception as e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "   for help use -h\n")
        return None


# ==============================================================================
# def infoUsuario():
#     if psutilOk:
#         try:
#             USERusuario = psutil.users()[0].name
#         except:
#             USERusuario = psutil.users()
#         if not isinstance(USERusuario, str) or USERusuario == '':
#             USERusuario = 'PC1'
#         return USERusuario
#     else:
#         return 'SinUsuario'


# ==============================================================================
def foo():
    pass


# ==============================================================================
if __name__ == '__main__':
    # GRAL_verbose = False
    # GRAL_nombreUsuario = infoUsuario()

    accionesPrincipales = [
        '1. qlidtwins: buscar o verificar zonas analogas a una de referencia (con un determinado patron dasoLidar)',
        '2. qlidmerge: integrar ficheros asc de 2x2 km en una capa tif unica (componer mosaico: merge)',
    ]

    args = leerArgumentosEnLineaDeComandos()
    if args is None:
        print('\ncartolidar-> ATENCION: revisar error en argumentos en linea')
        print('\t-> La funcion leerArgumentosEnLineaDeComandos<> ha dado error')
        sys.exit(0)

    opcionPorDefecto = 1
    if args.accionPrincipal <= 0:
        print('\ncartolidar-> Menu de herramientas de cartolidar')
        for opcionPrincipal in accionesPrincipales:
            print(f'\t{opcionPrincipal}.')
        selec = input(f'Elije opcion ({opcionPorDefecto}): ')
        if selec == '':
            nOpcionElegida = opcionPorDefecto
        else:
            try:
                nOpcionElegida = int(selec)
            except:
                print(f'\nATENCION: Opcion elegida no disponible: <{selec}>')
                sys.exit(0)
        print(f'\nSe ha elegido {accionesPrincipales[nOpcionElegida - 1]}')
    elif args.accionPrincipal <= len(accionesPrincipales):
        print(f'\nOpcion elegida en linea de comandos: {accionesPrincipales[args.accionPrincipal - 1]}')
        nOpcionElegida = args.accionPrincipal
    else:
        print(f'\nATENCION: Opcion elegida en linea de comandos no disponible: {args.accionPrincipal}')
        sys.exit(0)

    if nOpcionElegida == 1:
        print('\ncartolidar.__main__-> Se ha elegido ejecutar qlidtwuins: se importa el modulo.')
        from cartolidar import qlidtwins
    elif nOpcionElegida == 2:
        print('\ncartolidar.__main__-> Se ha elegido ejecutar qlidmerge.')
        print('\t AVISO: herramienta pendiente de incluir en el paquete.')
        # from cartolidar import qlidmerge
    else:
        print('\nOpcion no disponible.')
    print('Fin de cartolidar')
