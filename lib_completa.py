# -*- coding: utf-8 -*-
"""
lib_completa.py
Importacion unica de toda la RevitPythonLibrary.
Compatible: IronPython 2.7 | CPython 3.x | Revit 2024-2026
Repositorio: https://github.com/kevinhimmelreich/RevitPythonLibrary

Uso en Dynamo:
    import sys
    sys.path.append("C:/ruta/a/RevitPythonLibrary")
    from lib_completa import *
"""

from lib_general import *        # noqa: F401,F403
from lib_coordinacion import *   # noqa: F401,F403
from lib_arquitectura import *   # noqa: F401,F403
from lib_instalaciones import *  # noqa: F401,F403
from lib_estructura import *     # noqa: F401,F403
from lib_geometria import *      # noqa: F401,F403
from lib_vistas import *         # noqa: F401,F403
from lib_familias import *       # noqa: F401,F403
from lib_cad import *            # noqa: F401,F403
from lib_excel import *          # noqa: F401,F403
from lib_bases_datos import *    # noqa: F401,F403
from lib_colaborativo import *   # noqa: F401,F403
from lib_transacciones import *  # noqa: F401,F403
from lib_seleccion_ui import *   # noqa: F401,F403
from lib_scientific import *     # noqa: F401,F403
