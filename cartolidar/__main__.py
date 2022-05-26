#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Tools for Lidar processing focused on Spanish PNOA datasets

@author:     Jose Bengoa
@copyright:  2022 @clid
@license:    GNU General Public License v3 (GPLv3)
@contact:    cartolidar@gmail.com
'''

import sys
import os
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__version__ = '0.0a2'
__date__ = '2016-2022'
__updated__ = '2022-05-18'
__all__ = []

# ==============================================================================
# Verbose provisional para la version alpha
if '-vvv' in sys.argv:
    __verbose__ = 3
elif '-vv' in sys.argv:
    __verbose__ = 2
elif '-v' in sys.argv or '--verbose' in sys.argv:
    __verbose__ = 1
else:
    __verbose__ = 0
if __verbose__ > 2:
    print(f'cartolidar.__main__-> __name__:     <{__name__}>')
    print(f'cartolidar.__main__-> __package__:  <{__package__}>')
    print(f'cartolidar.__main__-> sys.argv:     <{sys.argv}>')
    print()
# ==============================================================================


# ==============================================================================
def leerArgumentosEnLineaDeComandos(
        argv=None,
        opcionesPrincipales=[],
    ):
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

        optionsHelp = ';\n'.join(opcionesPrincipales)
        parser.add_argument('-o',  # '--option',
                            dest='menuOption',
                            type=int,
                            # help=f'{opcionesPrincipales[0]}; \n{opcionesPrincipales[1]}; \n{opcionesPrincipales[2]}. Default: %(default)s',
                            help=f'{optionsHelp}. Default: %(default)s',
                            default = '0',)
        parser.add_argument('-H',
                            dest='toolHelp',
                            type=str,
                            help='Nombre de la herramienta para la que se quiere obtener ayuda (qlidtwins, clidmerge, etc.). Default: %(default)s',
                            default = 'None',)

        # parser.add_argument('-I', '--idProceso',
        #                     dest='idProceso',
        #                     type=int,
        #                     help='Numero aleatorio para identificar el proceso que se esta ejecutando (se asigna automaticamente; no usar este argumento)',)

        # args = parser.parse_args()
        # Se ignoran argumentos desconocidos sin problemas porque no los hay posicionales
        args, unknown = parser.parse_known_args()
        if __verbose__ > 2 and not unknown is None and unknown != []:
            print(f'\ncartolidar.__main__-> Argumentos ignorados: {unknown}')
        return args, unknown
    except KeyboardInterrupt:
        return None, None
    except TypeError:
        return None, None
    except Exception as e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "   for help use -h\n")
        return None, None


# ==============================================================================
def foo():
    pass


# ==============================================================================
if __name__ == '__main__':

    opcionesPrincipales = [
        '0. Mostrar el menu principal',
        '1. qlidtwins: buscar o verificar zonas analogas a una de referencia (con un determinado patron dasoLidar)',
        '2. qlidmerge: integrar ficheros asc de 2x2 km en una capa tif unica (componer mosaico: merge)',
    ]

    args, unknown = leerArgumentosEnLineaDeComandos(
        opcionesPrincipales=opcionesPrincipales,
        )
    if args is None:
        print('\ncartolidar-> ATENCION: revisar error en argumentos en linea')
        print('\t-> La funcion leerArgumentosEnLineaDeComandos<> ha dado error')
        sys.exit(0)


    if not args.toolHelp == 'None':
        # for num_arg in range(len(sys.argv) - 1):
        #     del sys.argv[num_arg + 1]
        print(f'sys.argv pre:  {sys.argv}')
        for sys_arg in sys.argv[1:]:
            sys.argv.remove(sys_arg)
        print(f'sys.argv post: {sys.argv}')
        sys.argv.append('-h')
        if '-e' in unknown:
            # print(f'\ncartolidar.__main__-> Recuperando el argumento ignorado: -e')
            sys.argv.append('-e')
        print(f'sys.argv fin:  {sys.argv}')
        if args.toolHelp == 'qlidtwins':
            from cartolidar import qlidtwins
            sys.exit(0)
        elif args.toolHelp == 'qlidmerge':
            from cartolidar import qlidmerge
            sys.exit(0)
        else:
            print(f'Revisar los argumentos. El argumento -H debe ir con nombre del modulo sobre el que se pide ayuda.')
            print(f'\t-> sys.argv: {sys.argv}')
            sys.exit(0)



    opcionPorDefecto = 1
    if args.menuOption <= 0:
        print('\ncartolidar-> Menu de herramientas de cartolidar')
        for opcionPrincipal in opcionesPrincipales[1:]:
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
        print(f'\nSe ha elegido:\n\t{opcionesPrincipales[nOpcionElegida]}')
    elif args.menuOption < len(opcionesPrincipales):
        print(f'\nOpcion elegida en linea de comandos:\n\t{opcionesPrincipales[args.menuOption]}')
        nOpcionElegida = args.menuOption
    else:
        print(f'\nATENCION: Opcion elegida en linea de comandos no disponible:\n\t{args.menuOption}')
        print('Fin de cartolidar\n')
        sys.exit(0)

    if nOpcionElegida == 1:
        if __verbose__ > 1:
            print('\ncartolidar.__main__-> Se ha elegido ejecutar qlidtwuins:')
            print('\t-> Se importa el modulo qlidtwins.py.')
        from cartolidar import qlidtwins
    elif nOpcionElegida == 2:
        if __verbose__ > 1:
            print('\ncartolidar.__main__-> Se ha elegido ejecutar qlidmerge.')
        print('\nAVISO: herramienta pendiente de incluir en cartolidar.')
        # from cartolidar import qlidmerge
    print('\nFin de cartolidar\n')

#TODO: Completar cuando haya incluido mas herramientas en cartolidar

