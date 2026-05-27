# -*- coding: utf-8 -*-
"""
lib_vistas.py
Biblioteca de funciones Revit/Dynamo — Vistas Avanzadas
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

from System.Collections.Generic import List  # noqa: E402

from Autodesk.Revit.DB import (  # noqa: E402
    FilteredElementCollector, ElementId, BuiltInParameter, BuiltInCategory,
    View, View3D, ViewPlan, ViewSection, ViewSheet, Viewport,
    ViewFamilyType, ViewFamily, ViewDuplicateOption,
    ViewDetailLevel, DisplayStyle, ViewDiscipline,
    PlanViewPlane, ElevationMarker,
    BoundingBoxXYZ, Transform, XYZ, Line, CurveLoop,
    ElementTransformUtils, OverrideGraphicSettings, Color,
    ViewOrientation3D, ImageExportOptions, ImageResolution,
    ImageFileType, ExportRange, UnitUtils, UnitTypeId,
    ParameterFilterElement, ParameterFilterRuleFactory,
    ElementParameterFilter,
    LogicalOrFilter, LogicalAndFilter, ElementFilter
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


# ── Helpers internos ─────────────────────────────────────────────────────────

def _metros_a_pies(v):
    return UnitUtils.ConvertToInternalUnits(v, UnitTypeId.Meters)


def _pies_a_metros(v):
    return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.Meters)


def _iniciar():
    TransactionManager.Instance.EnsureInTransaction(doc)


def _finalizar():
    TransactionManager.Instance.TransactionTaskDone()


def _tipo_vista(familia):
    """Retorna el primer ViewFamilyType que coincide con la familia dada."""
    tipos = FilteredElementCollector(doc).OfClass(
        ViewFamilyType).ToElements()
    return next((t for t in tipos if t.ViewFamily == familia), None)


# ── Creación de vistas ───────────────────────────────────────────────────────

def crear_vista_planta(nivel, nombre, familia_nombre=None):
    """
    Crea una vista de planta de suelo para el nivel indicado.

    Args:
        nivel: objeto Level de Revit
        nombre: nombre de la nueva vista
        familia_nombre: nombre de la familia ViewFamilyType a usar
            (por defecto busca "Plano de planta" o "Floor Plan")

    Returns:
        ViewPlan creada, o None si no hay tipo disponible

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tipos = list(
        FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements()
    )
    if familia_nombre:
        tipo = next(
            (t for t in tipos if familia_nombre in t.FamilyName), None)
    else:
        tipo = next(
            (t for t in tipos
             if t.ViewFamily == ViewFamily.FloorPlan), None)
    if tipo is None:
        return None
    _iniciar()
    vista = ViewPlan.Create(doc, tipo.Id, nivel.Id)
    vista.Name = nombre
    _finalizar()
    return vista


def crear_vista_3d_isometrica(nombre):
    """
    Crea una vista 3D isometrica con el nombre indicado.

    Args:
        nombre: nombre de la vista

    Returns:
        View3D creada, o None si no hay tipo disponible

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tipo = _tipo_vista(ViewFamily.ThreeDimensional)
    if tipo is None:
        return None
    _iniciar()
    vista = View3D.CreateIsometric(doc, tipo.Id)
    vista.Name = nombre
    _finalizar()
    return vista


def crear_vista_3d_por_bbox(bbox_xyz, nombre):
    """
    Crea una vista 3D isometrica recortada al BoundingBoxXYZ indicado.

    Args:
        bbox_xyz: BoundingBoxXYZ de Revit
        nombre: nombre de la vista

    Returns:
        View3D con SectionBox aplicado, o None si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tipo = _tipo_vista(ViewFamily.ThreeDimensional)
    if tipo is None:
        return None
    _iniciar()
    vista = View3D.CreateIsometric(doc, tipo.Id)
    vista.Name = nombre
    vista.SetSectionBox(bbox_xyz)
    _finalizar()
    return vista


def crear_vista_3d_por_habitacion(
        habitacion, nombre, offset_mm=500, escala=50):
    """
    Crea una vista 3D isometrica recortada al bounding box de una
    habitación con un margen de offset.

    Args:
        habitacion: Room de Revit
        nombre: nombre de la vista
        offset_mm: margen de offset en mm (por defecto 500)
        escala: escala numérica de la vista (por defecto 50)

    Returns:
        View3D creada, o None si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tipo = _tipo_vista(ViewFamily.ThreeDimensional)
    if tipo is None:
        return None
    off = _metros_a_pies(offset_mm / 1000.0)
    bb = habitacion.BoundingBox[doc.ActiveView]
    nuevo = BoundingBoxXYZ()
    nuevo.Min = XYZ(bb.Min.X - off, bb.Min.Y - off, bb.Min.Z - off)
    nuevo.Max = XYZ(bb.Max.X + off, bb.Max.Y + off, bb.Max.Z + off)
    _iniciar()
    vista = View3D.CreateIsometric(doc, tipo.Id)
    vista.Name = nombre
    vista.SetSectionBox(nuevo)
    vista.CropBoxActive = True
    vista.CropBoxVisible = True
    vista.Scale = escala
    vista.DetailLevel = ViewDetailLevel.Fine
    vista.DisplayStyle = DisplayStyle.Shading
    _finalizar()
    return vista


def crear_vista_3d_desde_seccion(seccion):
    """
    Genera una vista 3D isometrica con SectionBox equivalente a la
    región de corte de una vista de sección.
    Extruye la forma de recorte a lo largo de la dirección de vista
    usando el parámetro 'Far Clip Offset'.

    Args:
        seccion: ViewSection de Revit

    Returns:
        View3D creada, o None si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tipo = _tipo_vista(ViewFamily.ThreeDimensional)
    if tipo is None:
        return None
    try:
        mgr = seccion.GetCropRegionShapeManager()
        formas = mgr.GetCropShape()
        if not formas:
            return None
        p_far = seccion.LookupParameter("Far Clip Offset")
        profundidad = (p_far.AsDouble() if p_far else
                       _metros_a_pies(2.0))
        dir_vista = seccion.ViewDirection
        puntos = []
        for curva in formas[0]:
            puntos.append(curva.GetEndPoint(0))
        xs = [p.X for p in puntos]
        ys = [p.Y for p in puntos]
        zs = [p.Z for p in puntos]
        offset_dir = dir_vista.Multiply(profundidad)
        mn = XYZ(min(xs), min(ys), min(zs))
        mx = XYZ(max(xs), max(ys), max(zs))
        mn2 = mn.Subtract(offset_dir)
        mx2 = mx.Add(offset_dir)
        bbox = BoundingBoxXYZ()
        bbox.Min = XYZ(min(mn.X, mn2.X), min(mn.Y, mn2.Y),
                       min(mn.Z, mn2.Z))
        bbox.Max = XYZ(max(mx.X, mx2.X), max(mx.Y, mx2.Y),
                       max(mx.Z, mx2.Z))
        _iniciar()
        vista = View3D.CreateIsometric(doc, tipo.Id)
        try:
            vista.Name = seccion.Name + " (3D)"
        except Exception:
            pass
        vista.SetSectionBox(bbox)
        vista.Scale = 50
        _finalizar()
        return vista
    except Exception:
        return None


def crear_seccion_desde_curva(curva, offset_m=2.0, altura_m=3.0):
    """
    Crea una ViewSection a partir de una curva o elemento con curva
    de ubicacion.

    Args:
        curva: curva Revit o elemento con .Location.Curve
        offset_m: profundidad lateral en metros (por defecto 2.0)
        altura_m: altura de corte en metros (por defecto 3.0)

    Returns:
        ViewSection creada

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if hasattr(curva, "Location"):
        curva = curva.Location.Curve
    ini = curva.GetEndPoint(0)
    fin = curva.GetEndPoint(1)
    v = fin - ini
    w = v.GetLength()
    mid = ini + 0.5 * v
    dir_l = v.Normalize()
    normal = dir_l.CrossProduct(XYZ.BasisZ)
    off = _metros_a_pies(offset_m)
    alt = _metros_a_pies(altura_m)
    bb = BoundingBoxXYZ()
    t = Transform.Identity
    t.Origin = mid
    t.BasisX = dir_l
    t.BasisY = XYZ.BasisZ
    t.BasisZ = normal
    bb.Transform = t
    bb.Min = XYZ(-w / 2, ini.Z, -off)
    bb.Max = XYZ(w / 2, alt, off)
    tipo = _tipo_vista(ViewFamily.Section)
    _iniciar()
    seccion = ViewSection.CreateSection(doc, tipo.Id, bb)
    _finalizar()
    return seccion


def crear_alzado_en_punto(punto_xyz, vista_plan_id, indice=0, escala=100):
    """
    Crea un ElevationMarker y un alzado en el indice indicado.

    Args:
        punto_xyz: XYZ de posicion del marcador
        vista_plan_id: ElementId de la vista de planta
        indice: 0=Norte/Der, 1=Este/Abajo, 2=Sur/Izq, 3=Oeste/Arriba
        escala: escala de la vista de alzado

    Returns:
        tupla (ElevationMarker, View de alzado)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tipo = _tipo_vista(ViewFamily.Elevation)
    _iniciar()
    marker = ElevationMarker.CreateElevationMarker(
        doc, tipo.Id, punto_xyz, escala)
    alzado = marker.CreateElevation(doc, vista_plan_id, indice)
    _finalizar()
    return marker, alzado


def crear_cartela(vista_plan, punto1_xyz, punto2_xyz):
    """
    Crea una Callout (llamada) en una vista de planta.

    Args:
        vista_plan: ViewPlan de Revit
        punto1_xyz: XYZ esquina inferior izquierda
        punto2_xyz: XYZ esquina superior derecha

    Returns:
        ViewSection (callout) creada

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tipo = _tipo_vista(ViewFamily.FloorPlan)
    _iniciar()
    llamada = ViewSection.CreateCallout(
        doc, vista_plan.Id, tipo.Id, punto1_xyz, punto2_xyz)
    _finalizar()
    return llamada


def crear_vista_detalle(elemento_referencia):
    """
    Crea una vista de detalle a partir del bounding box de un elemento.

    Args:
        elemento_referencia: elemento Revit cuyo BoundingBox define
            el area de detalle

    Returns:
        ViewSection (detalle) creada

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    caja = elemento_referencia.get_BoundingBox(doc.ActiveView)
    tipo = _tipo_vista(ViewFamily.Detail)
    _iniciar()
    detalle = ViewSection.CreateDetail(doc, tipo.Id, caja)
    _finalizar()
    return detalle


def crear_vista_planta_desde_habitacion(
        habitacion, nombre, offset_m=1.0, escala=50):
    """
    Crea una vista de planta recortada al bounding box de una habitacion.

    Args:
        habitacion: Room de Revit
        nombre: nombre de la vista
        offset_m: margen de offset en metros (por defecto 1.0)
        escala: escala numérica (por defecto 50)

    Returns:
        ViewPlan creada con CropBox aplicado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    bbox = habitacion.BoundingBox[doc.ActiveView]
    off = _metros_a_pies(offset_m)
    nuevo = BoundingBoxXYZ()
    nuevo.Min = XYZ(bbox.Min.X - off, bbox.Min.Y - off, bbox.Min.Z)
    nuevo.Max = XYZ(bbox.Max.X + off, bbox.Max.Y + off, bbox.Max.Z)
    nivel = habitacion.Level
    tipo = _tipo_vista(ViewFamily.FloorPlan)
    _iniciar()
    vista = ViewPlan.Create(doc, tipo.Id, nivel.Id)
    try:
        vista.Name = nombre
    except Exception:
        pass
    vista.CropBox = nuevo
    vista.CropBoxActive = True
    vista.CropBoxVisible = False
    vista.Scale = escala
    _finalizar()
    return vista


# ── Duplicar y transformar vistas ────────────────────────────────────────────

def duplicar_vista(vista, nombre):
    """
    Duplica una vista con una copia independiente.

    Args:
        vista: View de Revit a duplicar
        nombre: nombre de la nueva vista

    Returns:
        View duplicada, o None si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        _iniciar()
        nuevo_id = vista.Duplicate(ViewDuplicateOption.Duplicate)
        nueva = doc.GetElement(nuevo_id)
        try:
            nueva.Name = nombre
        except Exception:
            pass
        _finalizar()
        return nueva
    except Exception:
        return None


def duplicar_vista_dependiente(vista, nombre):
    """
    Duplica una vista como vista dependiente (vinculada a la original).

    Args:
        vista: View de Revit a duplicar
        nombre: nombre de la nueva vista dependiente

    Returns:
        View dependiente creada, o None si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        _iniciar()
        nuevo_id = vista.Duplicate(ViewDuplicateOption.AsDependent)
        nueva = doc.GetElement(nuevo_id)
        try:
            nueva.Name = nombre
        except Exception:
            pass
        _finalizar()
        return nueva
    except Exception:
        return None


def duplicar_vistas(vistas, nombres):
    """
    Duplica una lista de vistas con los nombres indicados.

    Args:
        vistas: lista de View de Revit
        nombres: lista de nombres para las nuevas vistas (o lista de
            listas para crear varias copias por vista)

    Returns:
        lista de View duplicadas

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    resultado = []
    _iniciar()
    for vista, nombre in zip(vistas, nombres):
        if isinstance(nombre, list):
            resultado.append([duplicar_vista(vista, n) for n in nombre])
        else:
            resultado.append(duplicar_vista(vista, nombre))
    _finalizar()
    return resultado


def convertir_vista_a_independiente(vista):
    """
    Convierte una vista dependiente en vista independiente.

    Args:
        vista: View dependiente de Revit

    Returns:
        True si la conversion es exitosa, False si ya es independiente
        o si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        vista.ConvertToIndependent()
        return True
    except Exception:
        return False


def girar_elemento_en_vista(elemento, vista, angulo_grados):
    """
    Gira un elemento usando el centro de su bounding box en la vista
    como eje de rotacion (eje vertical Z).

    Args:
        elemento: elemento Revit a girar
        vista: View donde está el elemento
        angulo_grados: angulo de rotacion en grados

    Returns:
        elemento girado, o None si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        angulo = math.radians(angulo_grados)
        bbox = elemento.BoundingBox[vista]
        diagonal = Line.CreateBound(bbox.Min, bbox.Max)
        centro = diagonal.Evaluate(0.5, True)
        eje = Line.CreateBound(centro, XYZ(centro.X, centro.Y, centro.Z + 1))
        _iniciar()
        ElementTransformUtils.RotateElement(doc, elemento.Id, eje, angulo)
        _finalizar()
        return elemento
    except Exception:
        return None


def copiar_elementos_entre_vistas(
        origen, destino, elementos, transformacion=None):
    """
    Copia elementos de una vista a otra. Usado para copiar anotaciones,
    etiquetas y objetos específicos de vista.

    Args:
        origen: View de Revit de origen
        destino: View de Revit de destino
        elementos: lista de elementos a copiar (con atributo .Id)
        transformacion: Transform de Revit (opcional, None = sin offset)

    Returns:
        lista de Element copiados

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    ids = List[ElementId](e.Id for e in elementos if hasattr(e, "Id"))
    _iniciar()
    copiados = ElementTransformUtils.CopyElements(
        origen, ids, destino, transformacion, None)
    _finalizar()
    return [doc.GetElement(i) for i in copiados]


# ── Crop region (recorte de vistas) ──────────────────────────────────────────

def activar_cropbox(vista, activar=True):
    """
    Activa o desactiva el crop box de una vista.

    Args:
        vista: View de Revit
        activar: True para activar, False para desactivar

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar()
    vista.CropBoxActive = activar
    _finalizar()


def establecer_cropbox(vista, bbox_xyz):
    """
    Asigna un BoundingBoxXYZ como crop box rectangular y lo activa.

    Args:
        vista: View de Revit
        bbox_xyz: BoundingBoxXYZ de Revit

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar()
    vista.CropBox = bbox_xyz
    vista.CropBoxActive = True
    vista.CropBoxVisible = True
    _finalizar()


def establecer_cropbox_desde_elemento(vista, elemento):
    """
    Asigna el bounding box de un elemento como crop box de la vista.

    Args:
        vista: View de Revit
        elemento: elemento Revit cuyo BoundingBox define el recorte

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    caja = elemento.get_BoundingBox(vista)
    _iniciar()
    vista.CropBox = caja
    vista.CropBoxActive = True
    vista.CropBoxVisible = True
    _finalizar()


def establecer_recorte_por_curvas(vista, curvas):
    """
    Aplica una forma de recorte poligonal arbitraria a la vista usando
    una lista de curvas que forman un bucle cerrado (CurveLoop).

    Args:
        vista: View de Revit
        curvas: lista de curvas Revit (Line, Arc…) que forman el bucle

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    bucle = CurveLoop()
    for c in curvas:
        bucle.Append(c)
    _iniciar()
    vista.CropBoxActive = True
    vista.GetCropRegionShapeManager().SetCropShape(bucle)
    _finalizar()


def establecer_recorte_con_offset(vista, curvas, offset_m):
    """
    Aplica un recorte poligonal con un desfase (offset) en metros.
    El CurveLoop se expande o contrae segun el offset indicado.

    Args:
        vista: View de Revit
        curvas: lista de curvas Revit que forman el perimetro
        offset_m: desfase en metros (positivo = expandir)

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    off = _metros_a_pies(offset_m)
    bucle = CurveLoop()
    for c in curvas:
        bucle.Append(c)
    desfasado = CurveLoop.CreateViaOffset(bucle, off, XYZ(0, 0, 1))
    _iniciar()
    vista.CropBoxActive = True
    vista.GetCropRegionShapeManager().SetCropShape(desfasado)
    _finalizar()


def copiar_recorte_entre_vistas(vista_origen, vista_destino):
    """
    Copia la forma de recorte (CropRegionShape) de una vista a otra.

    Args:
        vista_origen: View de Revit con el recorte de referencia
        vista_destino: View de Revit que recibe el recorte

    Returns:
        vista_destino modificada

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    mgr_origen = vista_origen.GetCropRegionShapeManager()
    bucle = mgr_origen.GetCropShape()[0]
    _iniciar()
    vista_destino.GetCropRegionShapeManager().SetCropShape(bucle)
    vista_destino.CropBoxActive = True
    vista_destino.CropBoxVisible = True
    _finalizar()
    return vista_destino


def obtener_forma_recorte(vista):
    """
    Retorna las curvas que definen la forma de recorte actual de una vista.

    Args:
        vista: View de Revit

    Returns:
        lista de curvas del primer CurveLoop, o lista vacía si no hay
        recorte activo

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        mgr = vista.GetCropRegionShapeManager()
        formas = mgr.GetCropShape()
        if formas:
            return list(formas[0])
    except Exception:
        pass
    return []


# ── Propiedades y rango de vista ─────────────────────────────────────────────

def establecer_escala(vista, escala):
    """
    Establece la escala de una vista.

    Args:
        vista: View de Revit
        escala: entero (ej. 100 para 1:100)

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar()
    vista.Scale = escala
    _finalizar()


def establecer_nivel_detalle(vista, nivel=None):
    """
    Establece el nivel de detalle de una vista.

    Args:
        vista: View de Revit
        nivel: ViewDetailLevel (por defecto ViewDetailLevel.Fine)

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if nivel is None:
        nivel = ViewDetailLevel.Fine
    _iniciar()
    vista.DetailLevel = nivel
    _finalizar()


def establecer_estilo_visual(vista, estilo=None):
    """
    Establece el estilo visual de una vista.

    Args:
        vista: View de Revit
        estilo: DisplayStyle (por defecto DisplayStyle.ShadingWithEdges)

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if estilo is None:
        estilo = DisplayStyle.ShadingWithEdges
    _iniciar()
    vista.DisplayStyle = estilo
    _finalizar()


def establecer_disciplina(vista, disciplina=None):
    """
    Establece la disciplina de una vista.

    Args:
        vista: View de Revit
        disciplina: ViewDiscipline (por defecto ViewDiscipline.Coordination)

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if disciplina is None:
        disciplina = ViewDiscipline.Coordination
    _iniciar()
    vista.Discipline = disciplina
    _finalizar()


def obtener_rango_de_vista(vista_plan):
    """
    Retorna el PlanViewRange de una vista de planta.

    Args:
        vista_plan: ViewPlan de Revit

    Returns:
        objeto PlanViewRange

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return vista_plan.GetViewRange()


def obtener_rango_vista_completo(vista_plan):
    """
    Retorna un diccionario con los niveles y offsets (en metros) de
    los cinco planos del rango de vista de una planta.

    Args:
        vista_plan: ViewPlan de Revit

    Returns:
        dict con claves:
          "nivel_proyecto_m", "TopClipPlane_nivel",
          "TopClipPlane_offset_m", "CutPlane_nivel",
          "CutPlane_offset_m", "BottomClipPlane_nivel",
          "BottomClipPlane_offset_m", "ViewDepthPlane_nivel",
          "ViewDepthPlane_offset_m", "UnderlayBottom_nivel",
          "UnderlayBottom_offset_m"

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    rango = vista_plan.GetViewRange()
    nivel_proy = _pies_a_metros(vista_plan.GenLevel.ProjectElevation)

    def _nivel(plano):
        lid = rango.GetLevelId(plano)
        return doc.GetElement(lid) if lid else None

    def _offset(plano):
        return _pies_a_metros(rango.GetOffset(plano))

    return {
        "nivel_proyecto_m": nivel_proy,
        "TopClipPlane_nivel": _nivel(PlanViewPlane.TopClipPlane),
        "TopClipPlane_offset_m": _offset(PlanViewPlane.TopClipPlane),
        "CutPlane_nivel": _nivel(PlanViewPlane.CutPlane),
        "CutPlane_offset_m": _offset(PlanViewPlane.CutPlane),
        "BottomClipPlane_nivel": _nivel(PlanViewPlane.BottomClipPlane),
        "BottomClipPlane_offset_m": _offset(
            PlanViewPlane.BottomClipPlane),
        "ViewDepthPlane_nivel": _nivel(PlanViewPlane.ViewDepthPlane),
        "ViewDepthPlane_offset_m": _offset(
            PlanViewPlane.ViewDepthPlane),
        "UnderlayBottom_nivel": _nivel(PlanViewPlane.UnderlayBottom),
        "UnderlayBottom_offset_m": _offset(PlanViewPlane.UnderlayBottom),
    }


def establecer_rango_de_vista(
        vista_plan, plano, nivel=None, offset_m=None):
    """
    Asigna un nivel y/o offset a un plano del rango de vista.

    Args:
        vista_plan: ViewPlan de Revit
        plano: PlanViewPlane (ej. PlanViewPlane.CutPlane)
        nivel: objeto Level de Revit (opcional)
        offset_m: offset en metros (opcional)

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    rango = vista_plan.GetViewRange()
    _iniciar()
    if nivel is not None:
        rango.SetLevelId(plano, nivel.Id)
    if offset_m is not None:
        rango.SetOffset(plano, _metros_a_pies(offset_m))
    vista_plan.SetViewRange(rango)
    _finalizar()


def obtener_subyacente(vista_plan):
    """
    Retorna la información de subyacente (underlay) de una vista de
    planta: nivel inferior, nivel superior y orientación.

    Args:
        vista_plan: ViewPlan de Revit

    Returns:
        dict con claves "nivel_base" (Level o None),
        "nivel_superior" (Level o None), "orientacion" (str o None)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    nivel_base = nivel_sup = orientacion = None
    try:
        if hasattr(vista_plan, "GetUnderlayBaseLevel"):
            lid = vista_plan.GetUnderlayBaseLevel()
            if lid and lid.IntegerValue > 0:
                nivel_base = doc.GetElement(lid)
            lid2 = vista_plan.GetUnderlayTopLevel()
            if lid2 and lid2.IntegerValue > 0:
                nivel_sup = doc.GetElement(lid2)
            orientacion = str(vista_plan.GetUnderlayOrientation())
        else:
            p = vista_plan.get_Parameter(
                BuiltInParameter.VIEW_UNDERLAY_ID)
            if p:
                lid = p.AsElementId()
                if lid.IntegerValue > 0:
                    nivel_base = doc.GetElement(lid)
    except Exception:
        pass
    return {
        "nivel_base": nivel_base,
        "nivel_superior": nivel_sup,
        "orientacion": orientacion,
    }


def eliminar_subyacente(vista_plan):
    """
    Elimina el subyacente (underlay) de una vista de planta.

    Args:
        vista_plan: ViewPlan de Revit

    Returns:
        True si se elimina, False si no aplica

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        p = vista_plan.get_Parameter(BuiltInParameter.VIEW_UNDERLAY_ID)
        if p is None:
            return False
        _iniciar()
        p.Set(ElementId.InvalidElementId)
        _finalizar()
        return True
    except Exception:
        return False


def aplicar_plantilla_de_vista(vista, plantilla_id):
    """
    Aplica una plantilla de vista a la vista indicada.

    Args:
        vista: View de Revit
        plantilla_id: ElementId de la plantilla de vista

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar()
    vista.ViewTemplateId = plantilla_id
    _finalizar()


def aplicar_plantilla_por_nombre(vistas, nombre_plantilla):
    """
    Aplica una plantilla de vista a una o varias vistas buscando
    la plantilla por nombre.

    Args:
        vistas: View o lista de View de Revit
        nombre_plantilla: nombre exacto de la plantilla

    Returns:
        lista de vistas modificadas, o None si la plantilla no existe

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    todas = FilteredElementCollector(doc).OfClass(View).ToElements()
    plantilla = next(
        (v for v in todas if v.IsTemplate and v.Name == nombre_plantilla),
        None)
    if plantilla is None:
        return None
    if not isinstance(vistas, list):
        vistas = [vistas]
    _iniciar()
    for v in vistas:
        v.ViewTemplateId = plantilla.Id
    _finalizar()
    return vistas


def asignar_caja_referencia(vista, caja_referencia):
    """
    Asigna una caja de referencia a la vista (Volume of Interest).

    Args:
        vista: View de Revit
        caja_referencia: elemento Reference Box de Revit

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = vista.get_Parameter(
        BuiltInParameter.VIEWER_VOLUME_OF_INTEREST_CROP)
    _iniciar()
    param.Set(caja_referencia.Id)
    _finalizar()


# ── Visibilidad y gráficos ───────────────────────────────────────────────────

def ocultar_elementos_en_vista(vista, lista_ids):
    """
    Oculta una lista de elementos en la vista indicada.

    Args:
        vista: View de Revit
        lista_ids: lista de ElementId a ocultar

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    ids = List[ElementId](lista_ids)
    _iniciar()
    vista.HideElements(ids)
    _finalizar()


def mostrar_elementos_en_vista(vista, lista_ids):
    """
    Muestra elementos previamente ocultos en la vista indicada.

    Args:
        vista: View de Revit
        lista_ids: lista de ElementId a mostrar

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    ids = List[ElementId](lista_ids)
    _iniciar()
    vista.UnhideElements(ids)
    _finalizar()


def ocultar_categoria_en_vista(vista, categoria_bic, ocultar=True):
    """
    Oculta o muestra una categoria completa en una vista.

    Args:
        vista: View de Revit
        categoria_bic: BuiltInCategory a ocultar/mostrar
        ocultar: True para ocultar, False para mostrar

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    cat_id = ElementId(categoria_bic)
    _iniciar()
    vista.SetCategoryHidden(cat_id, ocultar)
    _finalizar()


def aislar_elementos_temporalmente(vista, elementos):
    """
    Aísla temporalmente una lista de elementos en la vista. Equivale
    a usar Aislar Elemento en la interfaz de Revit.

    Args:
        vista: View de Revit
        elementos: lista de elementos Revit a aislar

    Returns:
        True si se aplica correctamente, False si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        ids = List[ElementId]([e.Id for e in elementos])
        _iniciar()
        vista.IsolateElementsTemporary(ids)
        _finalizar()
        return True
    except Exception:
        return False


def convertir_temporal_a_permanente(vista):
    """
    Convierte el aislamiento u ocultamiento temporal de una vista a
    permanente, manteniendo solo los elementos visibles.

    Args:
        vista: View de Revit con aislamiento temporal activo

    Returns:
        True si la conversion es exitosa, False si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        _iniciar()
        vista.ConvertTemporaryHideIsolateToPermanent()
        _finalizar()
        return True
    except Exception:
        return False


def sobreescribir_grafico_elemento(
        vista, elemento,
        color_superficie=None,
        patron_sup_id=None,
        color_corte=None,
        patron_corte_id=None,
        transparencia=None):
    """
    Aplica overrides de color y patron de relleno a un elemento en
    una vista sin modificar el elemento en si.

    Args:
        vista: View de Revit
        elemento: elemento Revit al que aplicar el override
        color_superficie: tupla (R, G, B) para el color de superficie
        patron_sup_id: ElementId del patron de superficie (opcional)
        color_corte: tupla (R, G, B) para el color de corte (opcional)
        patron_corte_id: ElementId del patron de corte (opcional)
        transparencia: entero 0-100 para transparencia de superficie

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    ogs = OverrideGraphicSettings()
    if color_superficie:
        col = Color(
            color_superficie[0], color_superficie[1], color_superficie[2])
        ogs.SetSurfaceForegroundPatternColor(col)
        ogs.SetSurfaceForegroundPatternVisible(True)
    if patron_sup_id:
        ogs.SetSurfaceForegroundPatternId(patron_sup_id)
    if color_corte:
        col = Color(color_corte[0], color_corte[1], color_corte[2])
        ogs.SetCutForegroundPatternColor(col)
        ogs.SetCutForegroundPatternVisible(True)
    if patron_corte_id:
        ogs.SetCutForegroundPatternId(patron_corte_id)
    if transparencia is not None:
        ogs.SetSurfaceTransparency(int(transparencia))
    _iniciar()
    vista.SetElementOverrides(elemento.Id, ogs)
    _finalizar()


def limpiar_grafico_elemento(vista, elemento):
    """
    Elimina todos los overrides graficos de un elemento en la vista,
    restaurando la apariencia por defecto.

    Args:
        vista: View de Revit
        elemento: elemento Revit

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar()
    vista.SetElementOverrides(elemento.Id, OverrideGraphicSettings())
    _finalizar()


# ── Orientación de vistas 3D ─────────────────────────────────────────────────

def establecer_orientacion_3d(vista, ojo_xyz, arriba_xyz, frente_xyz):
    """
    Establece la orientacion de una vista 3D o de perspectiva.

    Args:
        vista: View3D de Revit
        ojo_xyz: XYZ posicion del ojo / camara
        arriba_xyz: XYZ vector hacia arriba de la camara
        frente_xyz: XYZ vector de vision (hacia donde apunta la camara)

    Returns:
        True si la orientacion se aplica, False si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        vo = ViewOrientation3D(ojo_xyz, arriba_xyz, frente_xyz)
        _iniciar()
        vista.SetOrientation(vo)
        vista.SaveOrientation()
        _finalizar()
        return True
    except Exception:
        return False


def copiar_orientacion_3d(vista_control, vistas_destino):
    """
    Copia la orientacion de una vista 3D de referencia a una o varias
    vistas destino, bloqueando todas ellas.

    Args:
        vista_control: View3D con la orientacion de referencia
        vistas_destino: View3D o lista de View3D de destino

    Returns:
        lista de vistas modificadas

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not isinstance(vistas_destino, list):
        vistas_destino = [vistas_destino]
    _iniciar()
    vista_control.Unlock()
    orientacion = vista_control.GetOrientation()
    vista_control.SaveOrientationAndLock()
    for v in vistas_destino:
        v.Unlock()
        v.SetOrientation(orientacion)
        v.SaveOrientationAndLock()
    _finalizar()
    return vistas_destino


def bloquear_vista_3d(vista, bloquear=True):
    """
    Bloquea o desbloquea la orientacion de una vista 3D.

    Args:
        vista: View3D de Revit
        bloquear: True para bloquear, False para desbloquear

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar()
    if bloquear:
        vista.SaveOrientationAndLock()
    else:
        vista.Unlock()
    _finalizar()


def restaurar_orientacion_3d(vista):
    """
    Restaura la orientacion guardada de una vista 3D (si estaba bloqueada).

    Args:
        vista: View3D de Revit

    Returns:
        True si se restaura, False si la vista no estaba bloqueada

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        if vista.HasBeenLocked():
            _iniciar()
            vista.RestoreOrientationAndLock()
            _finalizar()
            return True
    except Exception:
        pass
    return False


def obtener_section_box_3d(vista_3d):
    """
    Retorna el BoundingBoxXYZ del SectionBox de una vista 3D,
    corregido con la transformacion del propio SectionBox.

    Args:
        vista_3d: View3D de Revit

    Returns:
        BoundingBoxXYZ en coordenadas absolutas del proyecto

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    sbox = vista_3d.GetSectionBox()
    tf = sbox.Transform
    ox, oy, oz = tf.Origin.X, tf.Origin.Y, tf.Origin.Z
    bbox = BoundingBoxXYZ()
    bbox.Min = XYZ(sbox.Min.X + ox, sbox.Min.Y + oy, sbox.Min.Z + oz)
    bbox.Max = XYZ(sbox.Max.X + ox, sbox.Max.Y + oy, sbox.Max.Z + oz)
    return bbox


# ── Planos (Sheets) ──────────────────────────────────────────────────────────

def crear_plano(numero, nombre, tipo_plano_id=None):
    """
    Crea un plano (Sheet) nuevo con numero y nombre indicados.

    Args:
        numero: numero de plano como string (ej. "A-001")
        nombre: nombre del plano
        tipo_plano_id: ElementId del cajetín (TitleBlock); si es None
            usa el primer cajetín disponible

    Returns:
        ViewSheet creada, o None si no hay cajetin disponible

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if tipo_plano_id is None:
        tipos = list(
            FilteredElementCollector(doc)
            .OfCategory(BuiltInCategory.OST_TitleBlocks)
            .WhereElementIsElementType()
            .ToElements()
        )
        if not tipos:
            return None
        tipo_plano_id = tipos[0].Id
    _iniciar()
    plano = ViewSheet.Create(doc, tipo_plano_id)
    plano.SheetNumber = numero
    plano.Name = nombre
    _finalizar()
    return plano


def anadir_vista_a_plano(plano, vista, posicion_xyz=None):
    """
    Inserta una vista en un plano como Viewport.

    Args:
        plano: ViewSheet de Revit
        vista: View de Revit a insertar
        posicion_xyz: XYZ de posicion en el plano (por defecto centro)

    Returns:
        Viewport creado, o None si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if posicion_xyz is None:
        posicion_xyz = XYZ(0.5, 0.5, 0)
    try:
        _iniciar()
        vp = Viewport.Create(doc, plano.Id, vista.Id, posicion_xyz)
        _finalizar()
        return vp
    except Exception:
        return None


def centrar_vista_en_plano(plano, viewport):
    """
    Mueve un Viewport al centro del area del plano.

    Args:
        plano: ViewSheet de Revit
        viewport: Viewport a centrar

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        outline = plano.Outline
        centro = XYZ(
            (outline.Min.U + outline.Max.U) / 2.0,
            (outline.Min.V + outline.Max.V) / 2.0,
            0)
        _iniciar()
        viewport.SetBoxCenter(centro)
        _finalizar()
    except Exception:
        pass


# ── Exportar ─────────────────────────────────────────────────────────────────

def exportar_vista_a_imagen(
        vista, ruta_salida, anchura_px=1920, formato=None):
    """
    Exporta una vista a imagen PNG en la ruta indicada.

    Args:
        vista: View de Revit a exportar
        ruta_salida: ruta base de salida (sin extension)
        anchura_px: anchura en pixeles (por defecto 1920)
        formato: ImageFileType (por defecto PNG)

    Returns:
        ruta_salida

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if formato is None:
        formato = ImageFileType.PNG
    ids = List[ElementId]()
    ids.Add(vista.Id)
    opciones = ImageExportOptions()
    opciones.FilePath = ruta_salida
    opciones.ExportRange = ExportRange.SetOfViews
    opciones.SetViewsAndSheets(ids)
    opciones.ImageResolution = ImageResolution.DPI_150
    opciones.HLRandWFViewsFileType = formato
    doc.ExportImage(opciones)
    return ruta_salida


def exportar_vistas_a_imagen(vistas, ruta_base, formato=None):
    """
    Exporta una lista de vistas a imagenes.

    Args:
        vistas: lista de View de Revit
        ruta_base: ruta base de salida (sin extension)
        formato: ImageFileType (por defecto PNG)

    Returns:
        ruta_base

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if formato is None:
        formato = ImageFileType.PNG
    ids = List[ElementId]()
    for v in vistas:
        ids.Add(v.Id)
    opciones = ImageExportOptions()
    opciones.FilePath = ruta_base
    opciones.ExportRange = ExportRange.SetOfViews
    opciones.SetViewsAndSheets(ids)
    opciones.ImageResolution = ImageResolution.DPI_150
    opciones.HLRandWFViewsFileType = formato
    doc.ExportImage(opciones)
    return ruta_base


# ── Filtros de vista (ParameterFilterElement) ─────────────────────────────────

def _cat_ids_net(categorias_bic):
    from System.Collections.Generic import List as NetList  # noqa: E402
    return NetList[ElementId](ElementId(c) for c in categorias_bic)


def crear_filtro_vista_por_texto(
        nombre_filtro, categorias_bic, param_bip, texto,
        condicion="igual"):
    """
    Crea un ParameterFilterElement de texto y lo registra en el documento.

    Args:
        nombre_filtro: nombre del filtro en Revit
        categorias_bic: lista de BuiltInCategory
        param_bip: BuiltInParameter del parametro a filtrar
        texto: valor de texto a comparar
        condicion: "igual", "contiene", "empieza_con", "termina_con",
            "no_igual"

    Returns:
        ParameterFilterElement creado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    cat_ids = _cat_ids_net(categorias_bic)
    param_id = ElementId(param_bip)
    fab = ParameterFilterRuleFactory
    if condicion == "contiene":
        regla = fab.CreateContainsRule(param_id, texto, False)
    elif condicion == "empieza_con":
        regla = fab.CreateBeginsWithRule(param_id, texto, False)
    elif condicion == "termina_con":
        regla = fab.CreateEndsWithRule(param_id, texto, False)
    elif condicion == "no_igual":
        regla = fab.CreateNotEqualsRule(param_id, texto)
    else:
        regla = fab.CreateEqualsRule(param_id, texto)
    ef = ElementParameterFilter(regla)
    _iniciar()
    filtro = ParameterFilterElement.Create(doc, nombre_filtro, cat_ids, ef)
    _finalizar()
    return filtro


def crear_filtro_vista_por_entero(
        nombre_filtro, categorias_bic, param_bip, valor,
        condicion="igual"):
    """
    Crea un ParameterFilterElement de entero y lo registra en el documento.

    Args:
        nombre_filtro: nombre del filtro en Revit
        categorias_bic: lista de BuiltInCategory
        param_bip: BuiltInParameter del parametro a filtrar
        valor: entero a comparar
        condicion: "igual", "mayor", "menor", "mayor_igual",
            "menor_igual", "no_igual"

    Returns:
        ParameterFilterElement creado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    cat_ids = _cat_ids_net(categorias_bic)
    param_id = ElementId(param_bip)
    fab = ParameterFilterRuleFactory
    if condicion == "mayor":
        regla = fab.CreateGreaterRule(param_id, int(valor))
    elif condicion == "menor":
        regla = fab.CreateLessRule(param_id, int(valor))
    elif condicion == "mayor_igual":
        regla = fab.CreateGreaterOrEqualRule(param_id, int(valor))
    elif condicion == "menor_igual":
        regla = fab.CreateLessOrEqualRule(param_id, int(valor))
    elif condicion == "no_igual":
        regla = fab.CreateNotEqualsRule(param_id, int(valor))
    else:
        regla = fab.CreateEqualsRule(param_id, int(valor))
    ef = ElementParameterFilter(regla)
    _iniciar()
    filtro = ParameterFilterElement.Create(doc, nombre_filtro, cat_ids, ef)
    _finalizar()
    return filtro


def crear_filtro_vista_combinado(
        nombre_filtro, categorias_bic, filtros_parciales,
        logica="o"):
    """
    Combina varios ParameterFilterElement existentes en un nuevo filtro
    con logica OR o AND.

    Args:
        nombre_filtro: nombre del filtro resultante
        categorias_bic: lista de BuiltInCategory
        filtros_parciales: lista de ParameterFilterElement ya creados
        logica: "o" para OR, "y" para AND

    Returns:
        ParameterFilterElement combinado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    from System.Collections.Generic import List as NetList  # noqa: E402
    cat_ids = _cat_ids_net(categorias_bic)
    efs = NetList[ElementFilter](
        [f.GetElementFilter() for f in filtros_parciales])
    if logica == "y":
        ef_combinado = LogicalAndFilter(efs)
    else:
        ef_combinado = LogicalOrFilter(efs)
    _iniciar()
    filtro = ParameterFilterElement.Create(
        doc, nombre_filtro, cat_ids, ef_combinado)
    _finalizar()
    return filtro


def aplicar_filtro_a_vista(
        vista, filtro_id, visible=True, ogs=None):
    """
    Aplica un ParameterFilterElement a una vista con visibilidad y
    override grafico opcionales.

    Args:
        vista: View de Revit
        filtro_id: ElementId del ParameterFilterElement
        visible: True para mostrar, False para ocultar elementos
        ogs: OverrideGraphicSettings opcional

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if ogs is None:
        ogs = OverrideGraphicSettings()
    _iniciar()
    vista.AddFilter(filtro_id)
    vista.SetFilterVisibility(filtro_id, visible)
    vista.SetFilterOverrides(filtro_id, ogs)
    _finalizar()


def eliminar_filtro_de_vista(vista, filtro_id):
    """
    Elimina un filtro de parametro de una vista.

    Args:
        vista: View de Revit
        filtro_id: ElementId del ParameterFilterElement a eliminar

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar()
    vista.RemoveFilter(filtro_id)
    _finalizar()


def listar_filtros_de_vista(vista):
    """
    Retorna los filtros aplicados a una vista como lista de dicts.

    Args:
        vista: View de Revit

    Returns:
        lista de dicts con claves "filtro", "visible", "override"

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    resultado = []
    for fid in vista.GetFilters():
        filtro = doc.GetElement(fid)
        resultado.append({
            "filtro": filtro,
            "visible": vista.GetFilterVisibility(fid),
            "override": vista.GetFilterOverrides(fid),
        })
    return resultado


def obtener_filtros_del_documento():
    """
    Retorna todos los ParameterFilterElement del documento.

    Args:
        (ninguno)

    Returns:
        lista de ParameterFilterElement

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfClass(ParameterFilterElement)
        .ToElements()
    )
