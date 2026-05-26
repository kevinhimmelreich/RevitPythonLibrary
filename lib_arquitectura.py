# -*- coding: utf-8 -*-
"""
lib_arquitectura.py
Biblioteca de funciones Revit/Dynamo — Arquitectura
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

# ── Revit API ─────────────────────────────────────────────────────────────────
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
clr.AddReference("RevitServices")
clr.AddReference("RevitNodes")

from System.Collections.Generic import List
from Autodesk.Revit.DB import (
    FilteredElementCollector, ElementId, Wall, WallType, Floor, FloorType,
    BuiltInCategory, BuiltInParameter, CurveArray, CurveLoop, UV, XYZ,
    BoundingBoxXYZ, SpatialElementBoundaryOptions, SpatialElementBoundaryLocation,
    SpatialElementGeometryCalculator, Phase, RoomFilter,
    CompoundStructure, CompoundStructureLayer, SketchPlane,
    UnitUtils, UnitTypeId
)
from Autodesk.Revit.DB.Architecture import Railing
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

import Revit
clr.ImportExtensions(Revit.Elements)

doc   = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app   = uiapp.Application
uidoc = uiapp.ActiveUIDocument

REVIT_VERSION = int(app.VersionNumber) if app else 0


def _pies_a_metros(v):
    return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.Meters)

def _metros_a_pies(v):
    return UnitUtils.ConvertToInternalUnits(v, UnitTypeId.Meters)

def _mm_a_pies(v):
    return UnitUtils.ConvertToInternalUnits(v, UnitTypeId.Millimeters)

def _pies_a_mm(v):
    return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.Millimeters)

def _pies2_a_m2(v):
    return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.SquareMeters)

def _iniciar(nombre="Transaccion"):
    TransactionManager.Instance.EnsureInTransaction(doc)

def _finalizar():
    TransactionManager.Instance.TransactionTaskDone()


def obtener_muros():
    """
    Retorna todos los muros de instancia del documento.

    Args:
        (ninguno)

    Returns:
        lista de Wall

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Walls)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_suelos():
    """
    Retorna todos los suelos de instancia del documento.

    Args:
        (ninguno)

    Returns:
        lista de Floor

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Floors)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_cubiertas():
    """
    Retorna todas las cubiertas de instancia del documento.

    Args:
        (ninguno)

    Returns:
        lista de elementos de cubierta

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Roofs)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_habitaciones(incluir_sin_colocar=True):
    """
    Retorna todas las habitaciones del documento.

    Args:
        incluir_sin_colocar: si True incluye habitaciones sin colocar

    Returns:
        lista de Room

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    rooms = list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Rooms)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    if not incluir_sin_colocar:
        rooms = [r for r in rooms if r.Location is not None]
    return rooms


def obtener_puertas():
    """
    Retorna todas las puertas de instancia del documento.

    Args:
        (ninguno)

    Returns:
        lista de FamilyInstance de puertas

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Doors)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_ventanas():
    """
    Retorna todas las ventanas de instancia del documento.

    Args:
        (ninguno)

    Returns:
        lista de FamilyInstance de ventanas

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Windows)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_escaleras():
    """
    Retorna todas las escaleras de instancia del documento.

    Args:
        (ninguno)

    Returns:
        lista de elementos de escalera

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Stairs)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_barandillas():
    """
    Retorna todas las barandillas de instancia del documento.

    Args:
        (ninguno)

    Returns:
        lista de Railing

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_StairsRailing)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_techos():
    """
    Retorna todos los techos de instancia del documento.

    Args:
        (ninguno)

    Returns:
        lista de elementos de techo

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Ceilings)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_mobiliario():
    """
    Retorna todos los elementos de mobiliario del documento.

    Args:
        (ninguno)

    Returns:
        lista de FamilyInstance de mobiliario

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Furniture)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def obtener_nombre_habitacion(habitacion):
    """
    Retorna el nombre de una habitacion.

    Args:
        habitacion: elemento Room de Revit

    Returns:
        nombre como string

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return habitacion.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()


def obtener_numero_habitacion(habitacion):
    """
    Retorna el numero de una habitacion.

    Args:
        habitacion: elemento Room de Revit

    Returns:
        numero como string

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return habitacion.get_Parameter(BuiltInParameter.ROOM_NUMBER).AsString()


def obtener_area_habitacion(habitacion):
    """
    Retorna el area de una habitacion en metros cuadrados.

    Args:
        habitacion: elemento Room de Revit

    Returns:
        area en m2 (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = habitacion.get_Parameter(BuiltInParameter.ROOM_AREA)
    return _pies2_a_m2(param.AsDouble()) if param else 0.0


def obtener_area_suelo(suelo):
    """
    Retorna el area de un suelo en metros cuadrados.

    Args:
        suelo: elemento Floor de Revit

    Returns:
        area en m2 (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = suelo.get_Parameter(BuiltInParameter.HOST_AREA_COMPUTED)
    return _pies2_a_m2(param.AsDouble()) if param else 0.0


def obtener_habitaciones_por_nivel(nivel):
    """
    Retorna las habitaciones de un nivel concreto.

    Args:
        nivel: objeto Level de Revit

    Returns:
        lista de Room en ese nivel

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return [r for r in obtener_habitaciones() if r.Level and r.Level.Id == nivel.Id]


def obtener_muros_por_tipo(nombre_tipo):
    """
    Retorna muros filtrados por nombre de tipo.

    Args:
        nombre_tipo: nombre del tipo de muro como string

    Returns:
        lista de Wall con ese tipo

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return [m for m in obtener_muros()
            if doc.GetElement(m.GetTypeId()).Name == nombre_tipo]


def obtener_grosor_muro(muro):
    """
    Retorna el grosor total de un muro en milimetros.

    Args:
        muro: elemento Wall de Revit

    Returns:
        grosor en mm (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return _pies_a_mm(muro.Width)


def obtener_carpinteria():
    """
    Retorna puertas y ventanas combinadas del documento.

    Args:
        (ninguno)

    Returns:
        lista de FamilyInstance de puertas y ventanas

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return obtener_puertas() + obtener_ventanas()


def obtener_elementos_en_habitacion(habitacion):
    """
    Retorna todos los elementos cuya ubicacion cae dentro de una habitacion.

    Args:
        habitacion: elemento Room de Revit

    Returns:
        lista de elementos Revit dentro de la habitacion

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    filtro = RoomFilter(habitacion.Id)
    return list(FilteredElementCollector(doc).WherePasses(filtro).ToElements())


def crear_muro(curva, nivel, tipo_muro_id, altura_mm=3000.0):
    """
    Crea un muro lineal a partir de una curva Revit.

    Args:
        curva: curva Revit (Line) que define el eje del muro
        nivel: objeto Level de Revit
        tipo_muro_id: ElementId del WallType
        altura_mm: altura del muro en milimetros (por defecto 3000)

    Returns:
        Wall creado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar("Crear Muro")
    muro = Wall.Create(doc, curva, tipo_muro_id, nivel.Id,
                       _mm_a_pies(altura_mm), 0, False, False)
    _finalizar()
    return muro


def crear_suelo(lineas_contorno, tipo_suelo_id, nivel):
    """
    Crea un suelo a partir de un contorno de curvas. Compatible Revit 2024+.

    Args:
        lineas_contorno: lista de curvas Revit que forman el contorno cerrado
        tipo_suelo_id: ElementId del FloorType
        nivel: objeto Level de Revit

    Returns:
        Floor creado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar("Crear Suelo")
    if REVIT_VERSION >= 2024:
        loop = CurveLoop()
        for c in lineas_contorno:
            loop.Append(c)
        loops = List[CurveLoop]()
        loops.Add(loop)
        suelo = Floor.Create(doc, loops, tipo_suelo_id, nivel.Id)
    else:
        curva_array = CurveArray()
        for c in lineas_contorno:
            curva_array.Append(c)
        suelo = doc.Create.NewFloor(curva_array, tipo_suelo_id, nivel, False)
    _finalizar()
    return suelo


def obtener_centroide_habitacion(habitacion):
    """
    Retorna el punto central XYZ de una habitacion a partir de su bounding box.

    Args:
        habitacion: elemento Room de Revit

    Returns:
        XYZ del centroide o None si no hay bounding box

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    bbox = habitacion.BoundingBox[None]
    if bbox is None:
        return None
    return XYZ(
        (bbox.Min.X + bbox.Max.X) / 2.0,
        (bbox.Min.Y + bbox.Max.Y) / 2.0,
        habitacion.Level.Elevation
    )


def obtener_contorno_habitacion(habitacion):
    """
    Retorna los elementos y curvas de contorno de una habitacion.

    Args:
        habitacion: elemento Room de Revit

    Returns:
        tupla (lista_elementos_limite, lista_curvas_limite)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    opciones = SpatialElementBoundaryOptions()
    opciones.SpatialElementBoundaryLocation = SpatialElementBoundaryLocation.Finish
    elementos, curvas = [], []
    for segmentos in habitacion.GetBoundarySegments(opciones):
        for seg in segmentos:
            elementos.append(doc.GetElement(seg.ElementId))
            try:
                curvas.append(seg.GetCurve())
            except AttributeError:
                curvas.append(seg.Curve)
    return elementos, curvas


def calcular_volumen_habitacion(habitacion):
    """
    Calcula el volumen de una habitacion en metros cubicos.

    Args:
        habitacion: elemento Room de Revit

    Returns:
        volumen en m3 (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    calculator = SpatialElementGeometryCalculator(doc)
    resultado  = calculator.CalculateSpatialElementGeometry(habitacion)
    solido     = resultado.GetGeometry()
    pies3 = solido.Volume
    return UnitUtils.ConvertFromInternalUnits(pies3, UnitTypeId.CubicMeters)


def clasificar_habitaciones_por_nombre(habitaciones, patron_regex):
    """
    Clasifica una lista de habitaciones en grupos segun un patron regex en el nombre.

    Args:
        habitaciones: lista de Room de Revit
        patron_regex: patron de expresion regular como string

    Returns:
        diccionario {grupo_regex: [habitaciones]}

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    import re
    resultado = {}
    for r in habitaciones:
        nombre = r.get_Parameter(BuiltInParameter.ROOM_NAME).AsString() or ""
        match = re.search(patron_regex, nombre, re.IGNORECASE)
        clave = match.group(0) if match else "Otro"
        resultado.setdefault(clave, []).append(r)
    return resultado


def obtener_puertas_de_habitacion(habitacion):
    """
    Retorna las puertas cuya habitacion de origen o destino es la indicada.

    Args:
        habitacion: elemento Room de Revit

    Returns:
        lista de FamilyInstance de puertas asociadas a esa habitacion

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    fases = list(FilteredElementCollector(doc).OfClass(Phase).ToElements())
    fase  = fases[-1] if fases else None
    resultado = []
    for puerta in obtener_puertas():
        try:
            origen  = puerta.FromRoom[fase]
            destino = puerta.ToRoom[fase]
            if (origen and origen.Id == habitacion.Id) or \
               (destino and destino.Id == habitacion.Id):
                resultado.append(puerta)
        except Exception:
            pass
    return resultado


def obtener_ventanas_de_habitacion(habitacion):
    """
    Retorna las ventanas cuyo muro anfitrion delimita la habitacion indicada.

    Args:
        habitacion: elemento Room de Revit

    Returns:
        lista de FamilyInstance de ventanas en esa habitacion

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    elementos_limite, _ = obtener_contorno_habitacion(habitacion)
    ids_muros = set(e.Id.IntegerValue for e in elementos_limite if e is not None)
    resultado = []
    for v in obtener_ventanas():
        host = v.Host
        if host and host.Id.IntegerValue in ids_muros:
            resultado.append(v)
    return resultado


def obtener_area_total_habitaciones():
    """
    Retorna el area total de todas las habitaciones colocadas en metros cuadrados.

    Args:
        (ninguno)

    Returns:
        area total en m2 (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return sum(obtener_area_habitacion(r) for r in obtener_habitaciones())


def agrupar_habitaciones_por_nivel():
    """
    Agrupa todas las habitaciones del documento por nombre de nivel.

    Args:
        (ninguno)

    Returns:
        diccionario {nombre_nivel: [habitaciones]}

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    resultado = {}
    for r in obtener_habitaciones():
        nivel_nombre = r.Level.Name if r.Level else "Sin Nivel"
        resultado.setdefault(nivel_nombre, []).append(r)
    return resultado


def obtener_tipos_de_muros():
    """
    Retorna todos los tipos de muro del documento.

    Args:
        (ninguno)

    Returns:
        lista de WallType

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(FilteredElementCollector(doc).OfClass(WallType).ToElements())


def obtener_tipos_de_suelos():
    """
    Retorna todos los tipos de suelo del documento.

    Args:
        (ninguno)

    Returns:
        lista de FloorType

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(FilteredElementCollector(doc).OfClass(FloorType).ToElements())


def crear_barandilla(nivel, lineas_curva, tipo_barandilla_id):
    """
    Crea una barandilla a partir de una lista de curvas Revit.

    Args:
        nivel: objeto Level de Revit
        lineas_curva: lista de curvas Revit que forman el trayecto
        tipo_barandilla_id: ElementId del tipo de barandilla

    Returns:
        Railing creada

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    loop = CurveLoop()
    for c in lineas_curva:
        loop.Append(c)
    _iniciar("Crear Barandilla")
    barandilla = Railing.Create(doc, loop, tipo_barandilla_id, nivel.Id)
    _finalizar()
    return barandilla


def obtener_areas():
    """
    Retorna todos los elementos de area del documento.

    Args:
        (ninguno)

    Returns:
        lista de elementos de Area

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Areas)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def crear_area_en_punto(vista_area, punto_uv):
    """
    Crea un area en un punto UV de una vista de area.

    Args:
        vista_area: AreaPlan View de Revit
        punto_uv: UV o tupla (u, v) con la posicion

    Returns:
        elemento Area creado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    uv = UV(punto_uv[0], punto_uv[1]) if not isinstance(punto_uv, UV) else punto_uv
    _iniciar("Crear Area")
    area = doc.Create.NewArea(vista_area, uv)
    _finalizar()
    return area


def crear_abertura_suelo(suelo, lineas_contorno):
    """
    Crea una abertura en un suelo a partir de un contorno de curvas.

    Args:
        suelo: elemento Floor de Revit
        lineas_contorno: lista de curvas Revit que forman el contorno de la abertura

    Returns:
        Opening creada

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    curva_array = CurveArray()
    for l in lineas_contorno:
        curva_array.Append(l)
    _iniciar("Abertura en Suelo")
    abertura = doc.Create.NewOpening(suelo, curva_array, True)
    _finalizar()
    return abertura


def clasificar_habitaciones_por_estado():
    """
    Clasifica todas las habitaciones por estado: colocadas, no_colocadas, no_cerradas, redundantes.

    Args:
        (ninguno)

    Returns:
        tupla (colocadas, no_colocadas, no_cerradas, redundantes)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    rooms = obtener_habitaciones()
    colocadas, no_colocadas, no_cerradas, redundantes = [], [], [], []
    opciones = SpatialElementBoundaryOptions()
    for r in rooms:
        loc = r.Location
        seg = r.GetBoundarySegments(opciones)
        if loc is None:
            no_colocadas.append(r)
        elif len(seg) < 1:
            no_cerradas.append(r)
        elif r.Area == 0:
            redundantes.append(r)
        else:
            colocadas.append(r)
    return colocadas, no_colocadas, no_cerradas, redundantes
