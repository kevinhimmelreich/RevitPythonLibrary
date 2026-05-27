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

# ── Revit API ────────────────────────────────────────────────────────────────
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
clr.AddReference("RevitServices")
clr.AddReference("RevitNodes")

from System.Collections.Generic import List  # noqa: E402
from Autodesk.Revit.DB import (  # noqa: E402
    FilteredElementCollector, ElementId, Wall, WallType, Floor,
    BuiltInCategory, BuiltInParameter, CurveArray, CurveLoop, UV, XYZ,
    BoundingBoxXYZ, SpatialElementBoundaryOptions,
    SpatialElementBoundaryLocation,
    SpatialElementGeometryCalculator, Phase, RoomFilter,
    CompoundStructure, SketchPlane, MaterialFunctionAssignment,
    UnitUtils, UnitTypeId
)
from Autodesk.Revit.DB.Architecture import Railing  # noqa: E402
from RevitServices.Persistence import DocumentManager  # noqa: E402
from RevitServices.Transactions import TransactionManager  # noqa: E402

import Revit  # noqa: E402
clr.ImportExtensions(Revit.Elements)

doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
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


# ── Habitaciones ──────────────────────────────────────────────────────────────

def obtener_habitaciones(incluir_sin_colocar=True):
    """
    Retorna todas las habitaciones del documento.

    Args:
        incluir_sin_colocar: si False excluye habitaciones sin colocar

    Returns:
        lista de Room
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


def obtener_nombre_habitacion(habitacion):
    """
    Retorna el nombre de una habitacion.

    Returns:
        string con el nombre
    """
    return habitacion.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()


def obtener_numero_habitacion(habitacion):
    """
    Retorna el numero de una habitacion.

    Returns:
        string con el numero
    """
    return habitacion.get_Parameter(
        BuiltInParameter.ROOM_NUMBER).AsString()


def obtener_area_habitacion(habitacion):
    """
    Retorna el area de una habitacion en metros cuadrados.

    Returns:
        area en m2 (float)
    """
    param = habitacion.get_Parameter(BuiltInParameter.ROOM_AREA)
    return _pies2_a_m2(param.AsDouble()) if param else 0.0


def obtener_habitaciones_por_nivel(nivel):
    """
    Retorna las habitaciones de un nivel concreto.

    Args:
        nivel: objeto Level de Revit

    Returns:
        lista de Room en ese nivel
    """
    return [
        r for r in obtener_habitaciones()
        if r.Level and r.Level.Id == nivel.Id
    ]


def obtener_centroide_habitacion(habitacion):
    """
    Retorna el punto central XYZ de una habitacion a partir de su
    bounding box.

    Args:
        habitacion: Room de Revit

    Returns:
        XYZ del centroide o None si no hay bounding box
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
        habitacion: Room de Revit

    Returns:
        tupla (lista_elementos_limite, lista_curvas_limite)
    """
    opciones = SpatialElementBoundaryOptions()
    opciones.SpatialElementBoundaryLocation = (
        SpatialElementBoundaryLocation.Finish)
    elementos, curvas = [], []
    for segmentos in habitacion.GetBoundarySegments(opciones):
        for seg in segmentos:
            elementos.append(doc.GetElement(seg.ElementId))
            try:
                curvas.append(seg.GetCurve())
            except AttributeError:
                curvas.append(seg.Curve)
    return elementos, curvas


def obtener_curveloops_habitacion(habitacion):
    """
    Retorna el contorno de una habitacion como lista de CurveLoop,
    uno por cada loop de limite (exterior e islas interiores).

    Args:
        habitacion: Room de Revit

    Returns:
        lista de CurveLoop con los limites de la habitacion

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    opciones = SpatialElementBoundaryOptions()
    opciones.SpatialElementBoundaryLocation = (
        SpatialElementBoundaryLocation.Finish)
    loops = []
    for segmentos in habitacion.GetBoundarySegments(opciones):
        loop = CurveLoop()
        for seg in segmentos:
            try:
                loop.Append(seg.GetCurve())
            except AttributeError:
                loop.Append(seg.Curve)
        loops.append(loop)
    return loops


def calcular_volumen_habitacion(habitacion):
    """
    Calcula el volumen de una habitacion en metros cubicos.

    Returns:
        volumen en m3 (float)
    """
    calculator = SpatialElementGeometryCalculator(doc)
    resultado = calculator.CalculateSpatialElementGeometry(habitacion)
    solido = resultado.GetGeometry()
    return UnitUtils.ConvertFromInternalUnits(
        solido.Volume, UnitTypeId.CubicMeters)


def clasificar_habitaciones_por_nombre(habitaciones, patron_regex):
    """
    Clasifica habitaciones en grupos segun un patron regex en el nombre.

    Args:
        habitaciones: lista de Room de Revit
        patron_regex: patron de expresion regular

    Returns:
        dict {grupo_regex: [habitaciones]}
    """
    import re
    resultado = {}
    for r in habitaciones:
        nombre = (r.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()
                  or "")
        match = re.search(patron_regex, nombre, re.IGNORECASE)
        clave = match.group(0) if match else "Otro"
        resultado.setdefault(clave, []).append(r)
    return resultado


def obtener_elementos_en_habitacion(habitacion):
    """
    Retorna todos los elementos cuya ubicacion cae dentro de una
    habitacion usando RoomFilter.

    Returns:
        lista de elementos Revit dentro de la habitacion
    """
    filtro = RoomFilter(habitacion.Id)
    return list(
        FilteredElementCollector(doc).WherePasses(filtro).ToElements())


def obtener_puertas_de_habitacion(habitacion):
    """
    Retorna las puertas cuya habitacion de origen o destino coincide.

    Returns:
        lista de FamilyInstance de puertas asociadas
    """
    fases = list(FilteredElementCollector(doc).OfClass(Phase).ToElements())
    fase = fases[-1] if fases else None
    puertas = list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Doors)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    resultado = []
    for puerta in puertas:
        try:
            origen = puerta.FromRoom[fase]
            destino = puerta.ToRoom[fase]
            if (origen and origen.Id == habitacion.Id) or \
               (destino and destino.Id == habitacion.Id):
                resultado.append(puerta)
        except Exception:
            pass
    return resultado


def obtener_ventanas_de_habitacion(habitacion):
    """
    Retorna las ventanas cuyo muro anfitrion delimita la habitacion.

    Returns:
        lista de FamilyInstance de ventanas en esa habitacion
    """
    elementos_limite, _ = obtener_contorno_habitacion(habitacion)
    ids_muros = set(
        e.Id.IntegerValue for e in elementos_limite if e is not None)
    ventanas = list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Windows)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    return [v for v in ventanas
            if v.Host and v.Host.Id.IntegerValue in ids_muros]


def obtener_area_total_habitaciones():
    """
    Retorna el area total de todas las habitaciones colocadas en m2.

    Returns:
        area total en m2 (float)
    """
    return sum(
        obtener_area_habitacion(r) for r in obtener_habitaciones())


def agrupar_habitaciones_por_nivel():
    """
    Agrupa todas las habitaciones del documento por nombre de nivel.

    Returns:
        dict {nombre_nivel: [habitaciones]}
    """
    resultado = {}
    for r in obtener_habitaciones():
        nombre = r.Level.Name if r.Level else "Sin Nivel"
        resultado.setdefault(nombre, []).append(r)
    return resultado


def clasificar_habitaciones_por_estado():
    """
    Clasifica todas las habitaciones por estado: colocadas, no_colocadas,
    no_cerradas, redundantes.

    Returns:
        tupla (colocadas, no_colocadas, no_cerradas, redundantes)
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


def detectar_habitaciones_sin_numero():
    """
    Retorna habitaciones colocadas que no tienen numero asignado.
    Util para control de calidad BIM.

    Returns:
        lista de Room sin numero
    """
    resultado = []
    for r in obtener_habitaciones(incluir_sin_colocar=False):
        p = r.get_Parameter(BuiltInParameter.ROOM_NUMBER)
        if p is None or not (p.AsString() or "").strip():
            resultado.append(r)
    return resultado


def detectar_habitaciones_duplicadas(tolerancia_m=0.5):
    """
    Detecta habitaciones colocadas en la misma posicion (por centroide
    XY con tolerancia).

    Args:
        tolerancia_m: distancia maxima en m para considerar duplicado

    Returns:
        lista de grupos (cada grupo es lista de Room duplicados)
    """
    tol = _metros_a_pies(tolerancia_m)
    rooms = [r for r in obtener_habitaciones()
             if r.Location is not None and r.Area > 0]
    usados = set()
    grupos = []
    for i, a in enumerate(rooms):
        if i in usados:
            continue
        ca = obtener_centroide_habitacion(a)
        if ca is None:
            continue
        grupo = [a]
        for j, b in enumerate(rooms):
            if j <= i or j in usados:
                continue
            cb = obtener_centroide_habitacion(b)
            if cb is None:
                continue
            dist = ((ca.X - cb.X) ** 2 + (ca.Y - cb.Y) ** 2) ** 0.5
            if dist <= tol:
                grupo.append(b)
                usados.add(j)
        if len(grupo) > 1:
            usados.add(i)
            grupos.append(grupo)
    return grupos


def renumerar_habitaciones_por_nivel(prefijo=None, inicio=1):
    """
    Renumera todas las habitaciones colocadas agrupandolas por nivel.
    El numero resultante es <prefijo><indice_nivel><numero_secuencial>.

    Args:
        prefijo: prefijo de texto (opcional, ej. "H")
        inicio: numero de inicio para la secuencia (por defecto 1)

    Returns:
        lista de Room renumeradas
    """
    from collections import OrderedDict
    agrupadas = OrderedDict()
    for r in sorted(
            obtener_habitaciones(incluir_sin_colocar=False),
            key=lambda r: (
                r.Level.Elevation if r.Level else 0)):
        nivel = r.Level.Name if r.Level else "Sin nivel"
        agrupadas.setdefault(nivel, []).append(r)
    _iniciar("Renumerar habitaciones")
    modificadas = []
    for idx_nivel, (_, rooms) in enumerate(agrupadas.items()):
        for idx_room, r in enumerate(rooms):
            p = r.get_Parameter(BuiltInParameter.ROOM_NUMBER)
            if p and not p.IsReadOnly:
                num = (
                    ("{}{}".format(
                        prefijo or "", idx_nivel + 1)
                     if prefijo else str(idx_nivel + 1))
                    + "{:02d}".format(inicio + idx_room)
                )
                p.Set(num)
                modificadas.append(r)
    _finalizar()
    return modificadas


def calcular_ratio_acristalamiento(habitacion):
    """
    Calcula el ratio de acristalamiento de una habitacion:
    area_ventanas / area_habitacion.

    Args:
        habitacion: Room de Revit

    Returns:
        dict con claves:
          "area_habitacion_m2", "area_ventanas_m2", "ratio",
          "ventanas": lista de FamilyInstance
    """
    area_room = obtener_area_habitacion(habitacion)
    ventanas = obtener_ventanas_de_habitacion(habitacion)
    area_v = 0.0
    for v in ventanas:
        p = v.get_Parameter(BuiltInParameter.HOST_AREA_COMPUTED)
        if p:
            area_v += _pies2_a_m2(p.AsDouble())
    ratio = (area_v / area_room) if area_room > 0 else 0.0
    return {
        "area_habitacion_m2": round(area_room, 3),
        "area_ventanas_m2": round(area_v, 3),
        "ratio": round(ratio, 4),
        "ventanas": ventanas,
    }


# ── Muros ─────────────────────────────────────────────────────────────────────

def obtener_carpinteria():
    """
    Retorna puertas y ventanas combinadas del documento.

    Returns:
        lista de FamilyInstance de puertas y ventanas
    """
    puertas = list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Doors)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    ventanas = list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Windows)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    return puertas + ventanas


def obtener_muros_por_tipo(nombre_tipo):
    """
    Retorna muros filtrados por nombre de tipo.

    Args:
        nombre_tipo: nombre del tipo de muro como string

    Returns:
        lista de Wall con ese tipo
    """
    muros = list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Walls)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    return [m for m in muros
            if doc.GetElement(m.GetTypeId()).Name == nombre_tipo]


def obtener_grosor_muro(muro):
    """
    Retorna el grosor total de un muro en milimetros.

    Returns:
        grosor en mm (float)
    """
    return _pies_a_mm(muro.Width)


def obtener_area_suelo(suelo):
    """
    Retorna el area de un suelo en metros cuadrados.

    Returns:
        area en m2 (float)
    """
    param = suelo.get_Parameter(BuiltInParameter.HOST_AREA_COMPUTED)
    return _pies2_a_m2(param.AsDouble()) if param else 0.0


def obtener_composicion_muro(muro):
    """
    Retorna el desglose de capas del tipo de muro con material, grosor
    y funcion de cada capa.

    Args:
        muro: elemento Wall de Revit

    Returns:
        lista de dicts con claves:
          "indice", "funcion", "material", "grosor_mm", "es_estructural"

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tipo = doc.GetElement(muro.GetTypeId())
    cs = tipo.GetCompoundStructure() if hasattr(tipo, "GetCompoundStructure") \
        else None
    if cs is None:
        return []
    funciones_nombres = {
        MaterialFunctionAssignment.Structure: "Estructura",
        MaterialFunctionAssignment.Substrate: "Substrato",
        MaterialFunctionAssignment.Insulation: "Aislamiento",
        MaterialFunctionAssignment.Finish1: "Acabado1",
        MaterialFunctionAssignment.Finish2: "Acabado2",
        MaterialFunctionAssignment.Membrane: "Membrana",
    }
    capas = list(cs.GetLayers())
    resultado = []
    for i, capa in enumerate(capas):
        mat = doc.GetElement(capa.MaterialId)
        resultado.append({
            "indice": i,
            "funcion": funciones_nombres.get(capa.Function, "Otro"),
            "material": mat.Name if mat else "Sin material",
            "grosor_mm": round(_pies_a_mm(capa.Width), 2),
            "es_estructural": (
                capa.Function == MaterialFunctionAssignment.Structure),
        })
    return resultado


def modificar_grosor_capa_estructural(tipo_muro, nuevo_grosor_mm):
    """
    Modifica el grosor de la capa estructural de un tipo de muro.

    Args:
        tipo_muro: WallType de Revit
        nuevo_grosor_mm: nuevo grosor en milimetros

    Returns:
        True si se modifico, False si no habia capa estructural
    """
    cs = tipo_muro.GetCompoundStructure()
    if cs is None:
        return False
    capas = list(cs.GetLayers())
    for i, capa in enumerate(capas):
        if capa.Function == MaterialFunctionAssignment.Structure:
            _iniciar("Modificar grosor capa")
            cs.SetLayerWidth(i, _mm_a_pies(nuevo_grosor_mm))
            tipo_muro.SetCompoundStructure(cs)
            _finalizar()
            return True
    return False


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
    """
    _iniciar("Crear Muro")
    muro = Wall.Create(doc, curva, tipo_muro_id, nivel.Id,
                       _mm_a_pies(altura_mm), 0, False, False)
    _finalizar()
    return muro


# ── Suelos y forjados ─────────────────────────────────────────────────────────

def crear_suelo(lineas_contorno, tipo_suelo_id, nivel):
    """
    Crea un suelo a partir de un contorno de curvas.
    Compatible Revit 2024+ (CurveLoop) y anterior (CurveArray).

    Args:
        lineas_contorno: lista de curvas Revit que forman el contorno
        tipo_suelo_id: ElementId del FloorType
        nivel: objeto Level de Revit

    Returns:
        Floor creado
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
        suelo = doc.Create.NewFloor(
            curva_array, tipo_suelo_id, nivel, False)
    _finalizar()
    return suelo


def crear_suelo_desde_habitacion(
        habitacion, tipo_suelo_id, curvas_extra=None, tolerancia_m=0.01):
    """
    Crea un suelo a partir del contorno de una habitacion, combinando
    opcionalmente curvas adicionales como umbrales de puertas.

    Flujo tipico: habitacion con puerta → contorno de habitacion + linea
    del umbral de puerta → suelo que cubre habitacion y umbral.

    Args:
        habitacion: Room de Revit
        tipo_suelo_id: ElementId del FloorType
        curvas_extra: lista de curvas Revit adicionales (umbrales, etc.)
        tolerancia_m: tolerancia de coincidencia al combinar contornos

    Returns:
        Floor creado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    from lib_geometria import combinar_perimetros  # noqa: E402
    _, curvas_base = obtener_contorno_habitacion(habitacion)
    if curvas_extra:
        curvas_base = combinar_perimetros(
            curvas_base, list(curvas_extra), tolerancia_m)
    return crear_suelo(curvas_base, tipo_suelo_id, habitacion.Level)


def crear_abertura_suelo(suelo, lineas_contorno):
    """
    Crea una abertura en un suelo a partir de un contorno de curvas.

    Args:
        suelo: elemento Floor de Revit
        lineas_contorno: lista de curvas Revit del contorno de la abertura

    Returns:
        Opening creada
    """
    curva_array = CurveArray()
    for linea in lineas_contorno:
        curva_array.Append(linea)
    _iniciar("Abertura en Suelo")
    abertura = doc.Create.NewOpening(suelo, curva_array, True)
    _finalizar()
    return abertura


# ── Areas ─────────────────────────────────────────────────────────────────────

def crear_area_en_punto(vista_area, punto_uv):
    """
    Crea un area en un punto UV de una vista de area.

    Args:
        vista_area: AreaPlan View de Revit
        punto_uv: UV o tupla (u, v) con la posicion

    Returns:
        elemento Area creado
    """
    uv = UV(punto_uv[0], punto_uv[1]) if not isinstance(punto_uv, UV) \
        else punto_uv
    _iniciar("Crear Area")
    area = doc.Create.NewArea(vista_area, uv)
    _finalizar()
    return area


def crear_separacion_de_area(vista_area, curvas, sketch_plane):
    """
    Crea lineas de separacion de area a partir de una lista de curvas.
    La vista debe ser de tipo AreaPlan.

    Args:
        vista_area: vista AreaPlan de Revit
        curvas: lista de curvas Revit (Line, Arc)
        sketch_plane: SketchPlane activo en la vista

    Returns:
        lista de ModelCurve (lineas de separacion creadas), o lista vacia
        si la vista no es AreaPlan
    """
    if str(vista_area.ViewType) != "AreaPlan":
        return []
    _iniciar("Crear Separacion Area")
    resultado = []
    for curva in curvas:
        sep = doc.Create.NewAreaBoundaryLine(
            sketch_plane, curva, vista_area)
        resultado.append(sep)
    _finalizar()
    return resultado


# ── Barandillas ───────────────────────────────────────────────────────────────

def crear_barandilla(nivel, lineas_curva, tipo_barandilla_id):
    """
    Crea una barandilla a partir de una lista de curvas Revit.

    Args:
        nivel: objeto Level de Revit
        lineas_curva: lista de curvas Revit que forman el trayecto
        tipo_barandilla_id: ElementId del tipo de barandilla

    Returns:
        Railing creada
    """
    loop = CurveLoop()
    for c in lineas_curva:
        loop.Append(c)
    _iniciar("Crear Barandilla")
    barandilla = Railing.Create(doc, loop, tipo_barandilla_id, nivel.Id)
    _finalizar()
    return barandilla


# ── pandas (CPython 3.x / Dynamo 2.13+) ─────────────────────────────────────

def dataframe_habitaciones(habitaciones):
    """
    Exporta datos de habitaciones Revit a un pandas DataFrame.
    Requiere CPython 3.x (Dynamo 2.13+).

    Args:
        habitaciones: lista de elementos Room de Revit

    Returns:
        pandas DataFrame con columnas [ElementId, Nombre, Numero,
        Area_m2, Volumen_m3, Nivel], o None si pandas no disponible

    Revit: 2024-2026 | CPython 3.x (Dynamo 2.13+)
    """
    try:
        import pandas as pd
    except ImportError:
        return None
    filas = []
    for hab in habitaciones:
        try:
            eid = int(hab.Id.Value)
        except AttributeError:
            eid = hab.Id.IntegerValue
        p_nombre = (hab.LookupParameter("Nombre")
                    or hab.LookupParameter("Name"))
        nombre = p_nombre.AsString() if p_nombre else ""
        filas.append({
            "ElementId": eid,
            "Nombre": nombre,
            "Numero": hab.Number,
            "Area_m2": round(hab.Area * 0.0929, 3),
            "Volumen_m3": round(hab.Volume * 0.0283, 3),
            "Nivel": hab.Level.Name if hab.Level else "",
        })
    return pd.DataFrame(filas)


def estadisticas_habitaciones_pandas(habitaciones):
    """
    Calcula estadisticas descriptivas de areas y volumenes de habitaciones.
    Requiere CPython 3.x (Dynamo 2.13+).

    Args:
        habitaciones: lista de elementos Room de Revit

    Returns:
        pandas DataFrame con estadisticas de Area_m2 y Volumen_m3,
        o None si pandas no disponible

    Revit: 2024-2026 | CPython 3.x (Dynamo 2.13+)
    """
    df = dataframe_habitaciones(habitaciones)
    if df is None:
        return None
    return df[["Area_m2", "Volumen_m3"]].describe()
