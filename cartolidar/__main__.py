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
import logging
import traceback

__version__ = '0.0a3'
__date__ = '2016-2022'
__updated__ = '2022-06-01'
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
    # En eclipse se adopta el valor indicado en Run Configurations -> Arguments
    __verbose__ = 0
# ==============================================================================
if '-q' in sys.argv:
    __quiet__ = 1
    __verbose__ = 0
else:
    __quiet__ = 0
# ==============================================================================
# TB = '\t'
TB = ' ' * 12
TV = ' ' * 3
# ==============================================================================

# ==============================================================================
# set a format which is simpler for console use
formatter0 = logging.Formatter('{message}', style='{')
# define a Handler which writes INFO messages or higher to the sys.stderr
consoleLog = logging.StreamHandler()
if __verbose__ == 3:
    consoleLog.setLevel(logging.DEBUG)
elif __verbose__ == 2:
    consoleLog.setLevel(logging.INFO)
elif __verbose__ == 1:
    consoleLog.setLevel(logging.WARNING)
elif not __quiet__:
    consoleLog.setLevel(logging.ERROR)
else:
    consoleLog.setLevel(logging.CRITICAL)
consoleLog.setFormatter(formatter0)
myLog = logging.getLogger(__name__.split('.')[-1])
myLog.addHandler(consoleLog)
# ==============================================================================
myLog.debug('{:_^80}'.format(''))
myLog.debug('cartolidar.__main__-> Debug & alpha version info:')
myLog.debug(f'{TB}-> __verbose__:  <{__verbose__}>')
myLog.debug(f'{TB}-> __package__ : <{__package__ }>')
myLog.debug(f'{TB}-> __name__:     <{__name__}>')
myLog.debug(f'{TB}-> sys.argv:     <{sys.argv}>')
myLog.debug('{:=^80}'.format(''))
# ==============================================================================


# ==============================================================================
def mensajeError(program_name):
    # https://stackoverflow.com/questions/1278705/when-i-catch-an-exception-how-do-i-get-the-type-file-and-line-number
    exc_type, exc_obj, exc_tb = sys.exc_info()
    # ==================================================================
    # tb = traceback.extract_tb(exc_tb)[-1]
    # lineError = tb[1]
    # funcError = tb[2]
    try:
        lineasTraceback = list((traceback.format_exc()).split('\n'))
        codigoConError = lineasTraceback[2]
    except:
        codigoConError = ''
    # ==================================================================
    fileNameError = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    lineError = exc_tb.tb_lineno
    funcError = os.path.split(exc_tb.tb_frame.f_code.co_name)[1]
    typeError = exc_type.__name__
    try:
        descError = exc_obj.strerror
    except:
        descError = exc_obj
    sys.stderr.write(f'\nOps! Ha surgido un error inesperado.\n')
    sys.stderr.write(f'Si quieres contribuir a depurar este programa envía el\n')
    sys.stderr.write(f'texto que aparece a continacion a: cartolidar@gmail.com\n')
    sys.stderr.write(f'\tError en:    {fileNameError}\n')
    sys.stderr.write(f'\tFuncion:     {funcError}\n')
    sys.stderr.write(f'\tLinea:       {lineError}\n')
    sys.stderr.write(f'\tDescripcion: {descError}\n') # = {exc_obj}
    sys.stderr.write(f'\tTipo:        {typeError}\n')
    sys.stderr.write(f'\tError en:    {codigoConError}\n')
    sys.stderr.write(f'Gracias!\n')
    # ==================================================================
    sys.stderr.write(f'\nFor help use:\n')
    sys.stderr.write(f'\thelp for main arguments:         python {program_name}.py -h\n')
    sys.stderr.write(f'\thelp for main & extra arguments: python {program_name}.py -e 1 -h\n')
    # ==================================================================
    # sys.stderr.write('\nFormato estandar del traceback:\n')
    # sys.stderr.write(traceback.format_exc())
    return (lineError, descError, typeError)


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

        # args = parser.parse_args()
        # Se ignoran argumentos desconocidos sin problemas porque no los hay posicionales
        args, unknown = parser.parse_known_args()
        if not unknown is None and unknown != []:
            myLog.warning(f'\ncartolidar.__main__-> Argumentos ignorados: {unknown}')
        return args, unknown
    except KeyboardInterrupt:
        program_name = 'cartolidar_main'
        mensajeError(program_name)
        return None, None
    except TypeError:
        program_name = 'cartolidar_main'
        mensajeError(program_name)
        return None, None
    except Exception as excpt:
        program_name = 'cartolidar_main'
        mensajeError(program_name)
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
        myLog.error('\ncartolidar-> ATENCION: error en los argumentos en linea de comandos')
        # myLog.error('\t-> La funcion leerArgumentosEnLineaDeComandos<> ha dado error')
        sys.stderr.write(f'\nFor help use:\n')
        sys.stderr.write(f'\tpython -m cartolidar -h\n')
        sys.exit(0)


    if not args.toolHelp == 'None':
        # for num_arg in range(len(sys.argv) - 1):
        #     del sys.argv[num_arg + 1]
        myLog.debug(f'sys.argv pre:  {sys.argv}')
        for sys_arg in sys.argv[1:]:
            sys.argv.remove(sys_arg)
        myLog.debug(f'sys.argv post: {sys.argv}')
        sys.argv.append('-h')
        if '-e' in unknown:
            # myLog.debug(f'\ncartolidar.__main__-> Recuperando el argumento ignorado: -e')
            sys.argv.append('-e')
        myLog.debug(f'sys.argv fin:  {sys.argv}')
        if args.toolHelp == 'qlidtwins':
            from cartolidar import qlidtwins
            sys.exit(0)
        elif args.toolHelp == 'qlidmerge':
            from cartolidar import qlidmerge
            sys.exit(0)
        else:
            myLog.error(f'Revisar los argumentos. El argumento -H debe ir con nombre del modulo sobre el que se pide ayuda.')
            myLog.error(f'\t-> sys.argv: {sys.argv}')
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
                myLog.error(f'\nATENCION: Opcion elegida no disponible: <{selec}>')
                sys.exit(0)
        myLog.info(f'\nSe ha elegido:\n\t{opcionesPrincipales[nOpcionElegida]}')
    elif args.menuOption < len(opcionesPrincipales):
        myLog.info(f'\nOpcion elegida en linea de comandos:\n\t{opcionesPrincipales[args.menuOption]}')
        nOpcionElegida = args.menuOption
    else:
        myLog.error(f'\nATENCION: Opcion elegida en linea de comandos no disponible:\n\t{args.menuOption}')
        myLog.error('Fin de cartolidar\n')
        sys.exit(0)

    if nOpcionElegida == 1:
        myLog.info('\ncartolidar.__main__-> Se ha elegido ejecutar qlidtwuins:')
        myLog.debug('\t-> Se importa el modulo qlidtwins.py.')
        from cartolidar import qlidtwins
    elif nOpcionElegida == 2:
        myLog.info('\ncartolidar.__main__-> Se ha elegido ejecutar qlidmerge.')
        myLog.warning('\nAVISO: herramienta pendiente de incluir en cartolidar.')
        # from cartolidar import qlidmerge
    myLog.info('\nFin de cartolidar\n')

#TODO: Completar cuando haya incluido mas herramientas en cartolidar

