# -*- coding: utf-8 -*-
"""
lib_general.py
Biblioteca de funciones Revit/Dynamo — Utilidades Generales
Compatible: IronPython 2.7 | CPython 3.x | Revit 2024-2026
Repositorio: https://github.com/kevinhimmelreich/RevitPythonLibrary
"""

import clr
import sys
import io

# ── Compatibilidad Python 2/3 ────────────────────────────────────────────────
PY3 = sys.version_info[0] >= 3
if PY3:
    string_types = (str,)
    text_type = str
else:
    string_types = (str, unicode)  # noqa: F821
    text_type = unicode            # noqa: F821

# ── Revit API ─────────────────────────────────────────────────────────────────
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
clr.AddReference("RevitServices")
clr.AddReference("RevitNodes")

from Autodesk.Revit.DB import (
    FilteredElementCollector, ElementId, StorageType,
    UnitUtils, UnitTypeId
)
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

import Revit
clr.ImportExtensions(Revit.Elements)

doc   = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app   = uiapp.Application
uidoc = uiapp.ActiveUIDocument

REVIT_VERSION = int(app.VersionNumber) if app else 0


def unwrap(element):
    """
    Desenvuelve un elemento Dynamo al elemento Revit nativo subyacente.

    Args:
        element: elemento Dynamo o Revit

    Returns:
        elemento Revit nativo

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        return element.InternalElement
    except AttributeError:
        try:
            return UnwrapElement(element)  # noqa: F821
        except Exception:
            return element


def unwrap_lista(elementos):
    """
    Desenvuelve una lista de elementos Dynamo a elementos Revit nativos.

    Args:
        elementos: lista de elementos Dynamo o Revit

    Returns:
        lista de elementos Revit nativos

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return [unwrap(e) for e in elementos]


def id_a_int(element_id):
    """
    Convierte un ElementId a entero de forma compatible con Revit 2024+.

    Args:
        element_id: objeto ElementId de Revit

    Returns:
        entero con el valor del ElementId

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        return int(element_id.Value)       # Revit 2024+ (Int64)
    except AttributeError:
        return element_id.IntegerValue     # Revit <= 2023


def iniciar_transaccion(nombre="Transaccion"):
    """
    Inicia o reanuda la transaccion Dynamo activa.

    Args:
        nombre: nombre descriptivo de la transaccion

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    TransactionManager.Instance.EnsureInTransaction(doc)


def finalizar_transaccion():
    """
    Marca la tarea de transaccion Dynamo como completada.

    Args:
        (ninguno)

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    TransactionManager.Instance.TransactionTaskDone()


def obtener_valor_parametro(elemento, nombre_param):
    """
    Lee el valor de un parametro de instancia por nombre de forma segura.

    Args:
        elemento: elemento Revit
        nombre_param: nombre del parametro como string

    Returns:
        valor del parametro (str, int, float o ElementId) o None si no existe

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = elemento.LookupParameter(nombre_param)
    if param is None:
        return None
    t = param.StorageType
    if t == StorageType.String:
        return param.AsString()
    elif t == StorageType.Integer:
        return param.AsInteger()
    elif t == StorageType.Double:
        return param.AsDouble()
    elif t == StorageType.ElementId:
        return param.AsElementId()
    return None


def establecer_valor_parametro(elemento, nombre_param, valor):
    """
    Escribe el valor de un parametro de instancia por nombre. Requiere transaccion activa.

    Args:
        elemento: elemento Revit
        nombre_param: nombre del parametro como string
        valor: valor a asignar (debe ser compatible con el StorageType)

    Returns:
        True si se escribio correctamente, False en caso contrario

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = elemento.LookupParameter(nombre_param)
    if param is None or param.IsReadOnly:
        return False
    t = param.StorageType
    try:
        if t == StorageType.String:
            param.Set(str(valor))
        elif t == StorageType.Integer:
            param.Set(int(valor))
        elif t == StorageType.Double:
            param.Set(float(valor))
        elif t == StorageType.ElementId:
            param.Set(valor)
        return True
    except Exception:
        return False


def obtener_todos_parametros(elemento):
    """
    Retorna todos los parametros de un elemento como diccionario {nombre: valor}.

    Args:
        elemento: elemento Revit

    Returns:
        diccionario {nombre_parametro: valor}

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    resultado = {}
    for param in elemento.Parameters:
        nombre = param.Definition.Name
        try:
            t = param.StorageType
            if t == StorageType.String:
                resultado[nombre] = param.AsString()
            elif t == StorageType.Integer:
                resultado[nombre] = param.AsInteger()
            elif t == StorageType.Double:
                resultado[nombre] = param.AsDouble()
            elif t == StorageType.ElementId:
                resultado[nombre] = id_a_int(param.AsElementId())
        except Exception:
            resultado[nombre] = None
    return resultado


def pies_a_metros(valor_pies):
    """
    Convierte pies internos de Revit a metros.

    Args:
        valor_pies: valor numerico en pies internos de Revit

    Returns:
        valor en metros (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return UnitUtils.ConvertFromInternalUnits(valor_pies, UnitTypeId.Meters)


def metros_a_pies(valor_metros):
    """
    Convierte metros a pies internos de Revit.

    Args:
        valor_metros: valor numerico en metros

    Returns:
        valor en pies internos de Revit (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return UnitUtils.ConvertToInternalUnits(valor_metros, UnitTypeId.Meters)


def mm_a_pies(valor_mm):
    """
    Convierte milimetros a pies internos de Revit.

    Args:
        valor_mm: valor numerico en milimetros

    Returns:
        valor en pies internos de Revit (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return UnitUtils.ConvertToInternalUnits(valor_mm, UnitTypeId.Millimeters)


def pies_a_mm(valor_pies):
    """
    Convierte pies internos de Revit a milimetros.

    Args:
        valor_pies: valor numerico en pies internos de Revit

    Returns:
        valor en milimetros (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return UnitUtils.ConvertFromInternalUnits(valor_pies, UnitTypeId.Millimeters)


def m2_a_pies2(valor_m2):
    """
    Convierte metros cuadrados a pies cuadrados internos de Revit.

    Args:
        valor_m2: valor numerico en metros cuadrados

    Returns:
        valor en pies cuadrados internos de Revit (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return UnitUtils.ConvertToInternalUnits(valor_m2, UnitTypeId.SquareMeters)


def pies2_a_m2(valor_pies2):
    """
    Convierte pies cuadrados internos de Revit a metros cuadrados.

    Args:
        valor_pies2: valor numerico en pies cuadrados internos de Revit

    Returns:
        valor en metros cuadrados (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return UnitUtils.ConvertFromInternalUnits(valor_pies2, UnitTypeId.SquareMeters)


def filtrar_por_categoria(categoria_builtIn):
    """
    Retorna todos los elementos de instancia de una categoria BuiltIn del documento activo.

    Args:
        categoria_builtIn: valor BuiltInCategory (ej. BuiltInCategory.OST_Walls)

    Returns:
        lista de elementos Revit

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(categoria_builtIn)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def filtrar_por_clase(clase):
    """
    Retorna todos los elementos de una clase .NET del documento activo.

    Args:
        clase: tipo .NET de Revit (ej. Wall, Floor, Level)

    Returns:
        lista de elementos Revit

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfClass(clase)
        .ToElements()
    )


def obtener_elemento_por_id(int_id):
    """
    Obtiene un elemento del documento por su ID entero.

    Args:
        int_id: entero con el ID del elemento

    Returns:
        elemento Revit o None si no existe

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return doc.GetElement(ElementId(int_id))
