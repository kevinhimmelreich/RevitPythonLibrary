# -*- coding: utf-8 -*-
"""
lib_instalaciones.py
Biblioteca de funciones Revit/Dynamo — Instalaciones MEP
Compatible: IronPython 2.7 | CPython 3.x | Revit 2024-2026
Repositorio: https://github.com/kevinhimmelreich/RevitPythonLibrary
"""

import clr
import sys
import math

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
    FilteredElementCollector, ElementId, BuiltInCategory, BuiltInParameter,
    UnitUtils, UnitTypeId
)
from Autodesk.Revit.DB.Mechanical import MechanicalSystem, Duct
from Autodesk.Revit.DB.Plumbing import Pipe, PipingSystem
from Autodesk.Revit.DB.Electrical import CableTray
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

import Revit
clr.ImportExtensions(Revit.Elements)

doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
uidoc = uiapp.ActiveUIDocument

REVIT_VERSION = int(app.VersionNumber) if app else 0


def _pies_a_metros(v):
    return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.Meters)


def _pies_a_mm(v):
    return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.Millimeters)


def _mm_a_pies(v):
    return UnitUtils.ConvertToInternalUnits(v, UnitTypeId.Millimeters)


def _iniciar(nombre="Transaccion"):
    TransactionManager.Instance.EnsureInTransaction(doc)


def _finalizar():
    TransactionManager.Instance.TransactionTaskDone()


def obtener_conductos():
    """
    Retorna todos los conductos de instancia del documento.

    Args:
        (ninguno)

    Returns:
        lista de Duct

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_DuctCurves)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_accesorios_conductos():
    """
    Retorna todos los accesorios de conductos del documento.

    Args:
        (ninguno)

    Returns:
        lista de FamilyInstance de accesorios de conducto

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_DuctFitting)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_terminales_conductos():
    """
    Retorna todos los terminales de conductos del documento.

    Args:
        (ninguno)

    Returns:
        lista de FamilyInstance de terminales de conducto

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_DuctTerminal)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_tuberias():
    """
    Retorna todas las tuberias de instancia del documento.

    Args:
        (ninguno)

    Returns:
        lista de Pipe

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_PipeCurves)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_accesorios_tuberias():
    """
    Retorna todos los accesorios de tuberias del documento.

    Args:
        (ninguno)

    Returns:
        lista de FamilyInstance de accesorios de tuberia

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_PipeFitting)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_bandejas_cable():
    """
    Retorna todas las bandejas de cable del documento.

    Args:
        (ninguno)

    Returns:
        lista de CableTray

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_CableTray)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_conduits():
    """
    Retorna todos los conduits electricos del documento.

    Args:
        (ninguno)

    Returns:
        lista de Conduit

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Conduit)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_equipos_mecanicos():
    """
    Retorna todos los equipos mecanicos del documento.

    Args:
        (ninguno)

    Returns:
        lista de FamilyInstance de equipos mecanicos

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_MechanicalEquipment)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_equipos_electricos():
    """
    Retorna todos los equipos electricos del documento.

    Args:
        (ninguno)

    Returns:
        lista de FamilyInstance de equipos electricos

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_ElectricalEquipment)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_luminarias():
    """
    Retorna todas las luminarias del documento.

    Args:
        (ninguno)

    Returns:
        lista de FamilyInstance de luminarias

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_LightingFixtures)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_sanitarios():
    """
    Retorna todos los sanitarios del documento.

    Args:
        (ninguno)

    Returns:
        lista de FamilyInstance de sanitarios

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_PlumbingFixtures)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_espacios():
    """
    Retorna todos los espacios MEP del documento.

    Args:
        (ninguno)

    Returns:
        lista de Space

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_MEPSpaces)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_sistemas_mecanicos():
    """
    Retorna todos los sistemas mecanicos del documento.

    Args:
        (ninguno)

    Returns:
        lista de MechanicalSystem

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc).OfClass(MechanicalSystem).ToElements()
    )


def obtener_sistemas_fontaneria():
    """
    Retorna todos los sistemas de fontaneria del documento.

    Args:
        (ninguno)

    Returns:
        lista de PipingSystem

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc).OfClass(PipingSystem).ToElements()
    )


def obtener_longitud_conducto(conducto):
    """
    Retorna la longitud de un conducto en metros.

    Args:
        conducto: elemento Duct de Revit

    Returns:
        longitud en metros (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = conducto.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH)
    return _pies_a_metros(param.AsDouble()) if param else 0.0


def obtener_longitud_tuberia(tuberia):
    """
    Retorna la longitud de una tuberia en metros.

    Args:
        tuberia: elemento Pipe de Revit

    Returns:
        longitud en metros (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = tuberia.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH)
    return _pies_a_metros(param.AsDouble()) if param else 0.0


def obtener_diametro_exterior_tuberia(tuberia):
    """
    Retorna el diametro exterior de una tuberia en milimetros.

    Args:
        tuberia: elemento Pipe de Revit

    Returns:
        diametro exterior en mm (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = tuberia.get_Parameter(BuiltInParameter.RBS_PIPE_OUTER_DIAMETER)
    return _pies_a_mm(param.AsDouble()) if param else 0.0


def obtener_diametro_interior_tuberia(tuberia):
    """
    Retorna el diametro interior de una tuberia en milimetros.

    Args:
        tuberia: elemento Pipe de Revit

    Returns:
        diametro interior en mm (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = tuberia.get_Parameter(BuiltInParameter.RBS_PIPE_INNER_DIAM_PARAM)
    return _pies_a_mm(param.AsDouble()) if param else 0.0


def obtener_sistema_tuberia(tuberia):
    """
    Retorna el nombre del sistema de una tuberia.

    Args:
        tuberia: elemento Pipe de Revit

    Returns:
        nombre del sistema como string, o None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = tuberia.get_Parameter(
        BuiltInParameter.RBS_PIPING_SYSTEM_TYPE_PARAM)
    if param:
        sistema = doc.GetElement(param.AsElementId())
        return sistema.Name if sistema else None
    return None


def obtener_tipo_sistema_conducto(conducto):
    """
    Retorna el nombre del tipo de sistema de un conducto.

    Args:
        conducto: elemento Duct de Revit

    Returns:
        nombre del sistema como string, o None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = conducto.get_Parameter(BuiltInParameter.RBS_DUCT_SYSTEM_TYPE_PARAM)
    if param:
        sistema = doc.GetElement(param.AsElementId())
        return sistema.Name if sistema else None
    return None


def obtener_longitud_bandeja(bandeja):
    """
    Retorna la longitud de una bandeja de cable en metros.

    Args:
        bandeja: elemento CableTray de Revit

    Returns:
        longitud en metros (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = bandeja.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH)
    return _pies_a_metros(param.AsDouble()) if param else 0.0


def agrupar_tuberias_por_sistema():
    """
    Agrupa todas las tuberias del documento por nombre de sistema.

    Args:
        (ninguno)

    Returns:
        diccionario {nombre_sistema: [tuberias]}

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    resultado = {}
    for t in obtener_tuberias():
        sistema = obtener_sistema_tuberia(t) or "Sin Sistema"
        resultado.setdefault(sistema, []).append(t)
    return resultado


def agrupar_conductos_por_sistema():
    """
    Agrupa todos los conductos del documento por nombre de sistema.

    Args:
        (ninguno)

    Returns:
        diccionario {nombre_sistema: [conductos]}

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    resultado = {}
    for c in obtener_conductos():
        sistema = obtener_tipo_sistema_conducto(c) or "Sin Sistema"
        resultado.setdefault(sistema, []).append(c)
    return resultado


def obtener_longitud_total_conductos():
    """
    Retorna la longitud total de todos los conductos del documento en metros.

    Args:
        (ninguno)

    Returns:
        longitud total en metros (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return sum(obtener_longitud_conducto(c) for c in obtener_conductos())


def obtener_longitud_total_tuberias():
    """
    Retorna la longitud total de todas las tuberias del documento en metros.

    Args:
        (ninguno)

    Returns:
        longitud total en metros (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return sum(obtener_longitud_tuberia(t) for t in obtener_tuberias())


def obtener_longitud_total_bandejas():
    """
    Retorna la longitud total de todas las bandejas de cable del documento
    en metros.

    Args:
        (ninguno)

    Returns:
        longitud total en metros (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return sum(obtener_longitud_bandeja(b) for b in obtener_bandejas_cable())


def obtener_espacios_por_nivel(nivel):
    """
    Retorna los espacios MEP de un nivel concreto.

    Args:
        nivel: objeto Level de Revit

    Returns:
        lista de Space en ese nivel

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return [
        e for e in obtener_espacios()
        if e.Level and e.Level.Id == nivel.Id
    ]


def crear_bandeja_cable(tipo_bandeja_id, punto_inicio_xyz, punto_fin_xyz,
                        nivel, ancho_mm=300.0, alto_mm=100.0):
    """
    Crea una bandeja de cables entre dos puntos XYZ con ancho y alto en mm.

    Args:
        tipo_bandeja_id: ElementId del tipo de bandeja
        punto_inicio_xyz: XYZ del punto de inicio
        punto_fin_xyz: XYZ del punto de fin
        nivel: objeto Level de Revit
        ancho_mm: ancho de la bandeja en milimetros (por defecto 300)
        alto_mm: altura de la bandeja en milimetros (por defecto 100)

    Returns:
        CableTray creada

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar("Crear Bandeja Cable")
    bandeja = CableTray.Create(
        doc, tipo_bandeja_id, punto_inicio_xyz, punto_fin_xyz, nivel.Id)
    p_ancho = bandeja.get_Parameter(
        BuiltInParameter.RBS_CABLETRAY_WIDTH_PARAM)
    p_alto = bandeja.get_Parameter(
        BuiltInParameter.RBS_CABLETRAY_HEIGHT_PARAM)
    if p_ancho:
        p_ancho.SetValueString(str(ancho_mm))
    if p_alto:
        p_alto.SetValueString(str(alto_mm))
    _finalizar()
    return bandeja


def verificar_espacio_en_punto(punto_xyz):
    """
    Retorna el espacio MEP que contiene el punto XYZ indicado.

    Args:
        punto_xyz: XYZ del punto a consultar

    Returns:
        Space en ese punto, o None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        return doc.GetSpaceAtPoint(punto_xyz)
    except Exception:
        return None


# ── pandas (CPython 3.x / Dynamo 2.13+) ─────────────────────────────────────

def dataframe_tuberias(tuberias):
    """
    Exporta datos de tuberias Revit a un pandas DataFrame.
    Requiere CPython 3.x (Dynamo 2.13+).

    Args:
        tuberias: lista de elementos Pipe de Revit

    Returns:
        pandas DataFrame con columnas [ElementId, Sistema, Diametro_mm,
        Longitud_m, Nivel], o None si pandas no disponible

    Revit: 2024-2026 | CPython 3.x (Dynamo 2.13+)
    """
    try:
        import pandas as pd
    except ImportError:
        print("pandas no disponible. Requiere CPython 3.x (Dynamo 2.13+).")
        return None
    filas = []
    for tub in tuberias:
        try:
            eid = int(tub.Id.Value)
        except AttributeError:
            eid = tub.Id.IntegerValue
        p_long = tub.LookupParameter("Longitud")
        p_diam = tub.LookupParameter("Diametro exterior")
        p_sist = tub.LookupParameter("Nombre del sistema")
        p_niv = tub.LookupParameter("Nivel de referencia")
        filas.append({
            "ElementId": eid,
            "Sistema": p_sist.AsString() if p_sist else "",
            "Diametro_mm": round(
                (p_diam.AsDouble() * 304.8) if p_diam else 0, 1
            ),
            "Longitud_m": round(
                (p_long.AsDouble() * 0.3048) if p_long else 0, 3
            ),
            "Nivel": p_niv.AsValueString() if p_niv else "",
        })
    return pd.DataFrame(filas)


def dataframe_conductos(conductos):
    """
    Exporta datos de conductos de ventilacion a un pandas DataFrame.
    Requiere CPython 3.x (Dynamo 2.13+).

    Args:
        conductos: lista de elementos Duct de Revit

    Returns:
        pandas DataFrame con columnas [ElementId, Sistema, Longitud_m,
        Nivel], o None si pandas no disponible

    Revit: 2024-2026 | CPython 3.x (Dynamo 2.13+)
    """
    try:
        import pandas as pd
    except ImportError:
        print("pandas no disponible. Requiere CPython 3.x (Dynamo 2.13+).")
        return None
    filas = []
    for duc in conductos:
        try:
            eid = int(duc.Id.Value)
        except AttributeError:
            eid = duc.Id.IntegerValue
        p_long = duc.LookupParameter("Longitud")
        p_sist = duc.LookupParameter("Nombre del sistema")
        p_niv = duc.LookupParameter("Nivel de referencia")
        filas.append({
            "ElementId": eid,
            "Sistema": p_sist.AsString() if p_sist else "",
            "Longitud_m": round(
                (p_long.AsDouble() * 0.3048) if p_long else 0, 3
            ),
            "Nivel": p_niv.AsValueString() if p_niv else "",
        })
    return pd.DataFrame(filas)


def estadisticas_sistemas_pandas(tuberias=None, conductos=None):
    """
    Calcula estadisticas de longitud agrupadas por sistema para
    tuberias y/o conductos. Requiere CPython 3.x (Dynamo 2.13+).

    Args:
        tuberias: lista de Pipe (opcional)
        conductos: lista de Duct (opcional)

    Returns:
        dict con DataFrames de estadisticas por tipo MEP,
        o None si pandas no disponible

    Revit: 2024-2026 | CPython 3.x (Dynamo 2.13+)
    """
    try:
        import pandas  # noqa: F401 — solo comprueba disponibilidad
    except ImportError:
        print("pandas no disponible. Requiere CPython 3.x (Dynamo 2.13+).")
        return None
    resultado = {}
    if tuberias:
        df = dataframe_tuberias(tuberias)
        if df is not None:
            resultado["tuberias"] = (
                df.groupby("Sistema")["Longitud_m"].describe()
            )
    if conductos:
        df = dataframe_conductos(conductos)
        if df is not None:
            resultado["conductos"] = (
                df.groupby("Sistema")["Longitud_m"].describe()
            )
    return resultado
