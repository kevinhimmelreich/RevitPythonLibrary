# -*- coding: utf-8 -*-
"""
lib_completa.py
Importacion unica de toda la RevitPythonLibrary.
Compatible: IronPython 2.7 | CPython 3.x | Revit 2024-2026
Repositorio: https://github.com/kevinhimmelreich/RevitPythonLibrary

Uso en Dynamo:
    import sys
    sys.path.append(r"C:\ruta\a\RevitPythonLibrary")
    from lib_completa import *
"""

from lib_general import *
from lib_coordinacion import *
from lib_arquitectura import *
from lib_instalaciones import *
from lib_estructura import *
from lib_geometria import *
from lib_vistas import *
from lib_familias import *
from lib_cad import *
from lib_excel import *
from lib_bases_datos import *
from lib_colaborativo import *
from lib_transacciones import *
from lib_seleccion_ui import *
