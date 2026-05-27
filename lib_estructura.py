# -*- coding: utf-8 -*-
"""
lib_estructura.py
Biblioteca de funciones Revit/Dynamo — Estructura
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
    FilteredElementCollector, Level, Line, XYZ, CurveLoop,
    BuiltInCategory, BuiltInParameter,
    StructuralType, SketchPlane, UnitUtils, UnitTypeId
)
from Autodesk.Revit.DB.Structure import (  # noqa: E402
    Rebar, RebarStyle, RebarHookOrientation, RebarHostData,
    RebarHookType, AreaReinforcement, AreaReinforcementType,
    PointLoad, PointLoadType, LineLoad, LineLoadType, AreaLoad, AreaLoadType
)
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


def _pies3_a_m3(v):
    return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.CubicMeters)


def _iniciar(nombre="Transaccion"):
    TransactionManager.Instance.EnsureInTransaction(doc)


def _finalizar():
    TransactionManager.Instance.TransactionTaskDone()


# ── Propiedades de elementos ─────────────────────────────────────────────────

def obtener_longitud_viga(viga):
    """
    Retorna la longitud de una viga en metros.

    Args:
        viga: FamilyInstance de viga estructural

    Returns:
        longitud en metros (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = viga.get_Parameter(BuiltInParameter.INSTANCE_LENGTH_PARAM)
    return _pies_a_metros(param.AsDouble()) if param else 0.0


def obtener_altura_pilar(pilar):
    """
    Retorna la altura de un pilar en metros.

    Args:
        pilar: FamilyInstance de pilar estructural

    Returns:
        altura en metros (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = pilar.get_Parameter(BuiltInParameter.INSTANCE_LENGTH_PARAM)
    return _pies_a_metros(param.AsDouble()) if param else 0.0


def obtener_nivel_base_pilar(pilar):
    """
    Retorna el nivel base de un pilar estructural.

    Args:
        pilar: FamilyInstance de pilar estructural

    Returns:
        objeto Level o None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = pilar.get_Parameter(BuiltInParameter.FAMILY_BASE_LEVEL_PARAM)
    return doc.GetElement(param.AsElementId()) if param else None


def obtener_nivel_alto_pilar(pilar):
    """
    Retorna el nivel superior de un pilar estructural.

    Args:
        pilar: FamilyInstance de pilar estructural

    Returns:
        objeto Level o None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = pilar.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_PARAM)
    return doc.GetElement(param.AsElementId()) if param else None


def obtener_material_estructura(elemento):
    """
    Retorna el nombre del material estructural de una viga o pilar.

    Args:
        elemento: FamilyInstance de viga o pilar

    Returns:
        nombre del material como string, o None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = elemento.get_Parameter(
        BuiltInParameter.STRUCTURAL_MATERIAL_PARAM)
    if param:
        mat = doc.GetElement(param.AsElementId())
        return mat.Name if mat else None
    return None


# ── Filtros por nivel ────────────────────────────────────────────────────────

def obtener_pilares_por_nivel(nivel):
    """
    Retorna los pilares cuyo nivel base coincide con el nivel indicado.

    Args:
        nivel: objeto Level de Revit

    Returns:
        lista de FamilyInstance de pilares en ese nivel

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    pilares = list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_StructuralColumns)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    return [p for p in pilares
            if obtener_nivel_base_pilar(p) is not None
            and obtener_nivel_base_pilar(p).Id == nivel.Id]


def obtener_vigas_por_nivel(nivel):
    """
    Retorna las vigas cuyo nivel de referencia coincide con el nivel
    indicado.

    Args:
        nivel: objeto Level de Revit

    Returns:
        lista de FamilyInstance de vigas en ese nivel

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    bip = BuiltInParameter.INSTANCE_REFERENCE_LEVEL_PARAM
    vigas = list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_StructuralFraming)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    return [v for v in vigas
            if v.get_Parameter(bip) is not None
            and v.get_Parameter(bip).AsElementId() == nivel.Id]


def agrupar_vigas_por_nivel():
    """
    Agrupa todas las vigas del documento por nombre de nivel de referencia.

    Args:
        (ninguno)

    Returns:
        dict {nombre_nivel: [vigas]}

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    bip = BuiltInParameter.INSTANCE_REFERENCE_LEVEL_PARAM
    vigas = list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_StructuralFraming)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    resultado = {}
    for v in vigas:
        p = v.get_Parameter(bip)
        if p is None:
            continue
        nivel = doc.GetElement(p.AsElementId())
        nombre = nivel.Name if nivel else "Sin nivel"
        resultado.setdefault(nombre, []).append(v)
    return resultado


# ── Cantidades y volumenes ───────────────────────────────────────────────────

def obtener_area_forjado(forjado):
    """
    Retorna el area de un forjado en metros cuadrados.

    Args:
        forjado: elemento Floor de Revit

    Returns:
        area en m2 (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = forjado.get_Parameter(BuiltInParameter.HOST_AREA_COMPUTED)
    return _pies2_a_m2(param.AsDouble()) if param else 0.0


def obtener_area_total_forjados():
    """
    Retorna el area total de todos los forjados del documento en m2.

    Args:
        (ninguno)

    Returns:
        area total en m2 (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    forjados = list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_Floors)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    return sum(obtener_area_forjado(f) for f in forjados)


def obtener_materiales_usados():
    """
    Lista los nombres de materiales estructurales unicos usados en vigas
    y pilares.

    Args:
        (ninguno)

    Returns:
        lista de nombres de material (strings)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    materiales = set()
    vigas = list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_StructuralFraming)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    pilares = list(
        FilteredElementCollector(doc)
        .OfCategory(BuiltInCategory.OST_StructuralColumns)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    for e in vigas + pilares:
        mat = obtener_material_estructura(e)
        if mat:
            materiales.add(mat)
    return list(materiales)


def calcular_volumen_hormigon(categorias_bic=None):
    """
    Suma HOST_VOLUME_COMPUTED de los elementos estructurales indicados.
    Sin argumento suma pilares, vigas, forjados y cimentaciones.

    Args:
        categorias_bic: lista de BuiltInCategory (opcional)

    Returns:
        volumen total en m3 (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if categorias_bic is None:
        categorias_bic = [
            BuiltInCategory.OST_StructuralColumns,
            BuiltInCategory.OST_StructuralFraming,
            BuiltInCategory.OST_Floors,
            BuiltInCategory.OST_StructuralFoundation,
        ]
    total = 0.0
    for bic in categorias_bic:
        elementos = list(
            FilteredElementCollector(doc)
            .OfCategory(bic)
            .WhereElementIsNotElementType()
            .ToElements()
        )
        for e in elementos:
            p = e.get_Parameter(BuiltInParameter.HOST_VOLUME_COMPUTED)
            if p:
                total += p.AsDouble()
    return _pies3_a_m3(total)


# ── Creacion de elementos ────────────────────────────────────────────────────

def crear_viga(curva_revit, nivel, tipo_viga_id):
    """
    Crea una viga estructural a partir de una curva Revit.

    Args:
        curva_revit: curva Revit (Line) que define el eje de la viga
        nivel: objeto Level de Revit
        tipo_viga_id: ElementId del FamilySymbol de la viga

    Returns:
        FamilyInstance de viga creada

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tipo = doc.GetElement(tipo_viga_id)
    tipo.Activate()
    _iniciar("Crear Viga")
    viga = doc.Create.NewFamilyInstance(
        curva_revit, tipo, nivel, StructuralType.Beam)
    _finalizar()
    return viga


def crear_pilar_vertical(punto_base_xyz, nivel, tipo_pilar_id):
    """
    Crea un pilar estructural vertical en la posicion y nivel indicados.

    Args:
        punto_base_xyz: XYZ del punto de insercion del pilar
        nivel: objeto Level de Revit (nivel base)
        tipo_pilar_id: ElementId del FamilySymbol del pilar

    Returns:
        FamilyInstance de pilar creado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tipo = doc.GetElement(tipo_pilar_id)
    tipo.Activate()
    _iniciar("Crear Pilar Vertical")
    pilar = doc.Create.NewFamilyInstance(
        punto_base_xyz, tipo, nivel, StructuralType.Column)
    _finalizar()
    return pilar


def crear_pilar_inclinado(
        punto_base_xyz, punto_top_xyz, nivel, tipo_pilar_id):
    """
    Crea un pilar estructural inclinado entre dos puntos XYZ.

    Args:
        punto_base_xyz: XYZ del punto inferior del pilar
        punto_top_xyz: XYZ del punto superior del pilar
        nivel: objeto Level de Revit (nivel base)
        tipo_pilar_id: ElementId del FamilySymbol del pilar

    Returns:
        FamilyInstance de pilar creado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    linea = Line.CreateBound(punto_base_xyz, punto_top_xyz)
    tipo = doc.GetElement(tipo_pilar_id)
    tipo.Activate()
    _iniciar("Crear Pilar Inclinado")
    pilar = doc.Create.NewFamilyInstance(
        linea, tipo, nivel, StructuralType.Column)
    _finalizar()
    return pilar


def obtener_propiedades_viga(viga):
    """
    Retorna un diccionario con las propiedades estructurales clave de una
    viga.

    Args:
        viga: FamilyInstance de viga estructural

    Returns:
        diccionario con extension_inicio, extension_fin, offset_y_m,
        offset_z_m, etc.

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    def _vstr(bip):
        p = viga.get_Parameter(bip)
        return p.AsValueString() if p else None

    def _vdbl(bip):
        p = viga.get_Parameter(bip)
        return _pies_a_metros(p.AsDouble()) if p else None

    return {
        "extension_inicio": _vdbl(BuiltInParameter.START_EXTENSION),
        "extension_fin": _vdbl(BuiltInParameter.END_EXTENSION),
        "corte_union_inicio": _vdbl(BuiltInParameter.START_JOIN_CUTBACK),
        "corte_union_fin": _vdbl(BuiltInParameter.END_JOIN_CUTBACK),
        "justificacion_yz": _vstr(BuiltInParameter.YZ_JUSTIFICATION),
        "justificacion_y": _vstr(BuiltInParameter.Y_JUSTIFICATION),
        "offset_y_m": _vdbl(BuiltInParameter.Y_OFFSET_VALUE),
        "justificacion_z": _vstr(BuiltInParameter.Z_JUSTIFICATION),
        "offset_z_m": _vdbl(BuiltInParameter.Z_OFFSET_VALUE),
    }


# ── Armaduras ────────────────────────────────────────────────────────────────

def crear_armadura(
        elemento_anfitrion, tipo_barra_id, curvas,
        estilo=None, gancho_inicio_id=None, gancho_fin_id=None):
    """
    Crea una armadura (Rebar) en un elemento estructural a partir de curvas.

    Args:
        elemento_anfitrion: elemento estructural Revit anfitrion
        tipo_barra_id: ElementId del RebarBarType
        curvas: lista de curvas Revit que definen la forma de la barra
        estilo: RebarStyle (por defecto RebarStyle.Standard)
        gancho_inicio_id: ElementId del RebarHookType inicial (opcional)
        gancho_fin_id: ElementId del RebarHookType final (opcional)

    Returns:
        Rebar creada

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if estilo is None:
        estilo = RebarStyle.Standard
    tipo_barra = doc.GetElement(tipo_barra_id)
    gancho_ini = (
        doc.GetElement(gancho_inicio_id) if gancho_inicio_id else None)
    gancho_fin = (
        doc.GetElement(gancho_fin_id) if gancho_fin_id else None)
    origen = XYZ.BasisZ
    _iniciar("Crear Armadura")
    rebar = Rebar.CreateFromCurves(
        doc, estilo, tipo_barra, gancho_ini, gancho_fin,
        elemento_anfitrion, origen, List[Curve](curvas),  # noqa: F821
        RebarHookOrientation.Left, RebarHookOrientation.Left, True, True)
    _finalizar()
    return rebar


def distribuir_armadura_numero_fijo(
        rebar, num_barras, longitud_array_m,
        lado_normal=True, incluir_primera=True, incluir_ultima=True):
    """
    Distribuye una armadura con numero fijo de barras a lo largo de una
    longitud.

    Args:
        rebar: elemento Rebar de Revit
        num_barras: numero entero de barras
        longitud_array_m: longitud total del array en metros
        lado_normal: si True las barras se distribuyen en el lado normal
        incluir_primera: si True incluye la primera barra
        incluir_ultima: si True incluye la ultima barra

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar("Distribuir Armadura Numero Fijo")
    rebar.GetShapeDrivenAccessor().SetLayoutAsFixedNumber(
        num_barras, _metros_a_pies(longitud_array_m),
        lado_normal, incluir_primera, incluir_ultima)
    _finalizar()


def distribuir_armadura_separacion_maxima(
        rebar, separacion_mm, longitud_array_m,
        lado_normal=True, incluir_primera=True, incluir_ultima=True):
    """
    Distribuye una armadura respetando una separacion maxima entre barras.

    Args:
        rebar: elemento Rebar de Revit
        separacion_mm: separacion maxima entre barras en milimetros
        longitud_array_m: longitud total del array en metros
        lado_normal: si True las barras se distribuyen en el lado normal
        incluir_primera: si True incluye la primera barra
        incluir_ultima: si True incluye la ultima barra

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar("Distribuir Armadura Separacion Maxima")
    rebar.GetShapeDrivenAccessor().SetLayoutAsMaximumSpacing(
        _mm_a_pies(separacion_mm), _metros_a_pies(longitud_array_m),
        lado_normal, incluir_primera, incluir_ultima)
    _finalizar()


def distribuir_armadura_separacion_minima(
        rebar, separacion_mm, longitud_array_m,
        lado_normal=True, incluir_primera=True, incluir_ultima=True):
    """
    Distribuye una armadura respetando una separacion minima entre barras.

    Args:
        rebar: elemento Rebar de Revit
        separacion_mm: separacion minima entre barras en milimetros
        longitud_array_m: longitud total del array en metros
        lado_normal: si True las barras se distribuyen en el lado normal
        incluir_primera: si True incluye la primera barra
        incluir_ultima: si True incluye la ultima barra

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar("Distribuir Armadura Separacion Minima")
    rebar.GetShapeDrivenAccessor().SetLayoutAsMinimumSpacing(
        _mm_a_pies(separacion_mm), _metros_a_pies(longitud_array_m),
        lado_normal, incluir_primera, incluir_ultima)
    _finalizar()


def establecer_armadura_solida_en_vista(rebar, vista):
    """
    Fuerza la representacion solida de una armadura en una vista.

    Args:
        rebar: elemento Rebar de Revit
        vista: vista de Revit en la que aplicar la representacion solida

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar("Armadura Solida en Vista")
    rebar.SetSolidInView(vista, True)
    _finalizar()


def obtener_armaduras_de_elemento(elemento):
    """
    Retorna todas las armaduras anfitrionadas en un elemento estructural.

    Args:
        elemento: elemento estructural Revit

    Returns:
        lista de Rebar

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return [
        doc.GetElement(rid)
        for rid in RebarHostData.GetRebarHostData(elemento).GetRebarIds()
    ]


def crear_armado_por_area(
        suelo, tipo_barra_id, tipo_gancho_id=None, direccion_xyz=None):
    """
    Crea un AreaReinforcement en un suelo estructural.

    Args:
        suelo: elemento Floor estructural anfitrion
        tipo_barra_id: ElementId del RebarBarType
        tipo_gancho_id: ElementId del RebarHookType (opcional)
        direccion_xyz: XYZ de la direccion principal (por defecto (1,0,0))

    Returns:
        AreaReinforcement creado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if direccion_xyz is None:
        direccion_xyz = XYZ(1, 0, 0)
    if tipo_gancho_id is None:
        tipo_gancho_id = (
            FilteredElementCollector(doc)
            .OfClass(RebarHookType)
            .FirstElementId()
        )
    _iniciar("Armado por Area")
    tipo_area_id = doc.GetElement(
        AreaReinforcementType.CreateDefaultAreaReinforcementType(doc)).Id
    armado = AreaReinforcement.Create(
        doc, suelo, direccion_xyz, tipo_area_id,
        tipo_barra_id, tipo_gancho_id)
    _finalizar()
    return armado


def obtener_recubrimientos(elemento_estructural):
    """
    Retorna los recubrimientos en milimetros de un elemento estructural.

    Args:
        elemento_estructural: elemento Revit estructural

    Returns:
        diccionario {general, inferior, superior, interior, exterior} en mm

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    def _v(bip):
        p = elemento_estructural.get_Parameter(bip)
        return _pies_a_mm(p.AsDouble()) if p else None

    return {
        "general": _v(BuiltInParameter.CLEAR_COVER),
        "inferior": _v(BuiltInParameter.CLEAR_COVER_BOTTOM),
        "superior": _v(BuiltInParameter.CLEAR_COVER_TOP),
        "interior": _v(BuiltInParameter.CLEAR_COVER_INTERIOR),
        "exterior": _v(BuiltInParameter.CLEAR_COVER_EXTERIOR),
    }


# ── Cargas estructurales ─────────────────────────────────────────────────────

def crear_carga_puntual(
        punto_xyz, fuerza_xyz, momento_xyz=None, nivel=None):
    """
    Crea una carga puntual libre en el modelo.

    Args:
        punto_xyz: XYZ de aplicacion de la carga
        fuerza_xyz: XYZ con los componentes de fuerza
        momento_xyz: XYZ con los componentes de momento (por defecto cero)
        nivel: Level de Revit (usa el mas bajo si es None)

    Returns:
        PointLoad creada

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if momento_xyz is None:
        momento_xyz = XYZ.Zero
    tipo = FilteredElementCollector(doc).OfClass(PointLoadType).FirstElement()
    if nivel is None:
        niveles = list(
            FilteredElementCollector(doc).OfClass(Level).ToElements())
        nivel = sorted(niveles, key=lambda niv: niv.Elevation)[0]
    plano = SketchPlane.Create(doc, nivel.Id)
    _iniciar("Crear Carga Puntual")
    carga = PointLoad.Create(
        doc, punto_xyz, fuerza_xyz, momento_xyz, tipo, plano)
    _finalizar()
    return carga


def crear_carga_lineal(
        p1_xyz, p2_xyz, fuerza_xyz, momento_xyz=None, nivel=None):
    """
    Crea una carga lineal libre entre dos puntos.

    Args:
        p1_xyz: XYZ del punto inicial
        p2_xyz: XYZ del punto final
        fuerza_xyz: XYZ con los componentes de fuerza por unidad de longitud
        momento_xyz: XYZ con los componentes de momento (por defecto cero)
        nivel: Level de Revit (usa el mas bajo si es None)

    Returns:
        LineLoad creada

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if momento_xyz is None:
        momento_xyz = XYZ.Zero
    tipo = FilteredElementCollector(doc).OfClass(LineLoadType).FirstElement()
    if nivel is None:
        niveles = list(
            FilteredElementCollector(doc).OfClass(Level).ToElements())
        nivel = sorted(niveles, key=lambda niv: niv.Elevation)[0]
    plano = SketchPlane.Create(doc, nivel.Id)
    _iniciar("Crear Carga Lineal")
    carga = LineLoad.Create(
        doc, p1_xyz, p2_xyz, fuerza_xyz, momento_xyz, tipo, plano)
    _finalizar()
    return carga


def crear_carga_superficial(contorno_curvas, fuerza_xyz):
    """
    Crea una carga superficial a partir de un contorno de curvas.

    Args:
        contorno_curvas: lista de curvas Revit que forman el contorno cerrado
        fuerza_xyz: XYZ con los componentes de fuerza por unidad de area

    Returns:
        AreaLoad creada

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tipo = FilteredElementCollector(doc).OfClass(AreaLoadType).FirstElement()
    lineas = List[Curve](contorno_curvas)  # noqa: F821
    loop = CurveLoop.Create(lineas)
    _iniciar("Crear Carga Superficial")
    carga = AreaLoad.Create(doc, [loop], fuerza_xyz, tipo)
    _finalizar()
    return carga
