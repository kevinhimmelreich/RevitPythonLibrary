# -*- coding: utf-8 -*-
"""
lib_seleccion_ui.py
Biblioteca de funciones Revit/Dynamo — Seleccion Interactiva UI
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

from System.Collections.Generic import List
from Autodesk.Revit.DB import ElementId
from Autodesk.Revit.UI.Selection import ObjectType as UIObjectType
from RevitServices.Persistence import DocumentManager

import Revit
clr.ImportExtensions(Revit.Elements)

doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
uidoc = uiapp.ActiveUIDocument

REVIT_VERSION = int(app.VersionNumber) if app else 0


def _selection():
    return uiapp.ActiveUIDocument.Selection


def seleccionar_elemento(mensaje="Selecciona un elemento"):
    """
    Pide al usuario que seleccione un elemento del modelo.

    Args:
        mensaje: texto que se muestra en la barra de estado de Revit

    Returns:
        elemento Revit seleccionado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    ref = _selection().PickObject(UIObjectType.Element, mensaje)
    return doc.GetElement(ref.ElementId)


def seleccionar_cara(mensaje="Selecciona una cara"):
    """
    Pide al usuario que seleccione una cara de un elemento.

    Args:
        mensaje: texto que se muestra en la barra de estado de Revit

    Returns:
        tupla (elemento, cara) donde cara es el GeometryObject Face

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    ref = _selection().PickObject(UIObjectType.Face, mensaje)
    elem = doc.GetElement(ref.ElementId)
    cara = elem.GetGeometryObjectFromReference(ref)
    return elem, cara


def seleccionar_arista(mensaje="Selecciona una arista"):
    """
    Pide al usuario que seleccione una arista de un elemento.

    Args:
        mensaje: texto que se muestra en la barra de estado de Revit

    Returns:
        tupla (elemento, arista) donde arista es el GeometryObject Edge

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    ref = _selection().PickObject(UIObjectType.Edge, mensaje)
    elem = doc.GetElement(ref.ElementId)
    arista = elem.GetGeometryObjectFromReference(ref)
    return elem, arista


def seleccionar_punto(mensaje="Selecciona un punto en el modelo"):
    """
    Pide al usuario un punto libre en el plano de trabajo activo.

    Args:
        mensaje: texto que se muestra en la barra de estado de Revit

    Returns:
        XYZ del punto seleccionado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return _selection().PickPoint(mensaje)


def seleccionar_punto_en_elemento(mensaje="Selecciona un punto"):
    """
    Pide al usuario un punto sobre una cara o curva de un elemento.

    Args:
        mensaje: texto que se muestra en la barra de estado de Revit

    Returns:
        tupla (referencia, XYZ) del punto seleccionado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    ref = _selection().PickObject(UIObjectType.PointOnElement, mensaje)
    return ref, ref.GlobalPoint


def seleccionar_multiples(mensaje="Selecciona elementos"):
    """
    Permite al usuario seleccionar varios elementos del modelo.

    Args:
        mensaje: texto que se muestra en la barra de estado de Revit

    Returns:
        lista de elementos Revit seleccionados

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    refs = _selection().PickObjects(UIObjectType.Element, mensaje)
    return [doc.GetElement(r.ElementId) for r in refs]


def seleccionar_rectangulo(mensaje="Dibuja un rectangulo de seleccion"):
    """
    Permite al usuario seleccionar elementos trazando un rectangulo.

    Args:
        mensaje: texto que se muestra en la barra de estado de Revit

    Returns:
        lista de elementos Revit dentro del rectangulo

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(_selection().PickElementsByRectangle(mensaje))


def seleccionar_elemento_en_link(
        mensaje="Selecciona un elemento en un link"):
    """
    Selecciona un elemento dentro de un Revit Link.

    Args:
        mensaje: texto que se muestra en la barra de estado de Revit

    Returns:
        tupla (instancia_link, referencia) del elemento seleccionado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    ref = _selection().PickObject(UIObjectType.LinkedElement, mensaje)
    link = doc.GetElement(ref.ElementId)
    return link, ref


def obtener_seleccion_actual():
    """
    Retorna los ElementId de los elementos actualmente seleccionados
    en Revit.

    Args:
        (ninguno)

    Returns:
        lista de ElementId seleccionados

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(_selection().GetElementIds())


def establecer_seleccion(lista_ids):
    """
    Establece la seleccion activa en Revit con una lista de ElementId.

    Args:
        lista_ids: lista de ElementId a seleccionar

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    ids = List[ElementId](lista_ids)
    _selection().SetElementIds(ids)
