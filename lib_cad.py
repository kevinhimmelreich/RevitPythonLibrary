# -*- coding: utf-8 -*-
"""
lib_cad.py
Biblioteca de funciones Revit/Dynamo — CAD (DWG/DXF)
Compatible: IronPython 2.7 | CPython 3.x | Revit 2024-2026
Repositorio: https://github.com/kevinhimmelreich/RevitPythonLibrary
"""

import clr
import sys

# ── Compatibilidad Python 2/3 ────────────────────────────────────────────────
PY3 = sys.version_info[0] >= 3
if PY3:
    string_types = (str,)
    text_type = str
else:
    string_types = (str, unicode)  # noqa: F821
    text_type = unicode            # noqa: F821

# ── Revit API ────────────────────────────────────────────────────────────────
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
clr.AddReference("RevitServices")
clr.AddReference("RevitNodes")

from Autodesk.Revit.DB import (
    FilteredElementCollector, ImportInstance, Options, XYZ
)
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

import Revit
clr.ImportExtensions(Revit.Elements)

doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
uidoc = uiapp.ActiveUIDocument

REVIT_VERSION = int(app.VersionNumber) if app else 0


def _iniciar(nombre="Transaccion"):
    TransactionManager.Instance.EnsureInTransaction(doc)


def _finalizar():
    TransactionManager.Instance.TransactionTaskDone()


def obtener_todos_links_cad():
    """
    Retorna todas las instancias de importacion/link CAD del documento.

    Args:
        (ninguno)

    Returns:
        lista de ImportInstance

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc).OfClass(ImportInstance).ToElements()
    )


def obtener_nombres_capas_cad(instancia_cad):
    """
    Retorna lista ordenada con los nombres de todos los layers de una
    instancia CAD.

    Args:
        instancia_cad: ImportInstance de Revit (link o importacion CAD)

    Returns:
        lista de strings con los nombres de capa ordenados alfabeticamente

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    subcats = instancia_cad.Category.SubCategories
    return sorted([sc.Name for sc in subcats])


def obtener_curvas_por_capa(instancia_cad, nombre_capa):
    """
    Extrae todas las curvas de un layer especifico de una importacion CAD.

    Args:
        instancia_cad: ImportInstance de Revit
        nombre_capa: nombre del layer CAD como string

    Returns:
        lista de curvas Revit del layer indicado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    opciones = instancia_cad.get_Geometry(Options())
    geometrias = []
    for g in opciones:
        try:
            for obj in g.GetInstanceGeometry():
                geometrias.append(obj)
        except Exception:
            pass

    curvas = []
    for geo in geometrias:
        tipo = str(geo.GetType())
        if "Solid" in tipo:
            continue
        style_id = geo.GraphicsStyleId
        style = doc.GetElement(style_id)
        if style and style.GraphicsStyleCategory.Name == nombre_capa:
            curvas.append(geo)
    return curvas


def obtener_datos_bloques_cad(instancia_cad):
    """
    Extrae datos de bloques de una importacion CAD.

    Args:
        instancia_cad: ImportInstance de Revit

    Returns:
        lista de dicts {simbolo, origen, geometrias}

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    opciones = instancia_cad.get_Geometry(Options())
    bloques = []
    for g in opciones:
        try:
            for obj in g.GetSymbolGeometry():
                tipo = str(obj.GetType())
                if "GeometryInstance" in tipo:
                    bloques.append({
                        "simbolo":    obj.Symbol,
                        "origen":     obj.Transform.Origin,
                        "geometrias": list(obj.GetInstanceGeometry()),
                    })
        except Exception:
            pass
    return bloques


def obtener_origen_link_cad(instancia_cad):
    """
    Retorna el vector de desplazamiento entre el origen del link CAD y el
    proyecto Revit.

    Args:
        instancia_cad: ImportInstance de Revit

    Returns:
        XYZ con la posicion del origen del link CAD en coordenadas del
        proyecto

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    origen_cad = instancia_cad.GetTransform().Origin
    return XYZ(origen_cad.X, origen_cad.Y, origen_cad.Z)


def eliminar_link_cad(instancia_cad):
    """
    Elimina una instancia de link/importacion CAD del documento.

    Args:
        instancia_cad: ImportInstance de Revit a eliminar

    Returns:
        ElementId eliminado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    eid = instancia_cad.Id
    _iniciar("Eliminar CAD Link")
    doc.Delete(eid)
    _finalizar()
    return eid


def eliminar_todos_links_cad():
    """
    Elimina todos los links/importaciones CAD del documento.

    Args:
        (ninguno)

    Returns:
        lista de ElementId eliminados

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    links = obtener_todos_links_cad()
    ids = [enlace.Id for enlace in links]
    _iniciar("Eliminar Todos CAD Links")
    for eid in ids:
        try:
            doc.Delete(eid)
        except Exception:
            pass
    _finalizar()
    return ids


def obtener_categoria_de_capa(instancia_cad, nombre_capa):
    """
    Retorna el objeto Category correspondiente a un layer de una importacion
    CAD.

    Args:
        instancia_cad: ImportInstance de Revit
        nombre_capa: nombre del layer CAD como string

    Returns:
        Category de Revit o None si no se encuentra

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    subcats = instancia_cad.Category.SubCategories
    for sc in subcats:
        if sc.Name == nombre_capa:
            return sc
    return None


def desanclar_link_cad(instancia_cad):
    """
    Desancla un link CAD para permitir su movimiento.

    Args:
        instancia_cad: ImportInstance de Revit

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar("Desanclar CAD Link")
    instancia_cad.Pinned = False
    _finalizar()
