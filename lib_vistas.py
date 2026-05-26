# -*- coding: utf-8 -*-
"""
lib_vistas.py
Biblioteca de funciones Revit/Dynamo — Vistas Avanzadas
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
    FilteredElementCollector, ElementId, View, View3D, ViewPlan, ViewSection,
    ViewFamilyType, ViewFamily, ViewDetailLevel, DisplayStyle, ViewDiscipline,
    PlanViewRange, PlanViewPlane, ElevationMarker, BoundingBoxXYZ, Transform,
    XYZ, ImageExportOptions, ImageResolution, ImageFileType, ExportRange,
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


def _metros_a_pies(v):
    return UnitUtils.ConvertToInternalUnits(v, UnitTypeId.Meters)

def _pies_a_metros(v):
    return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.Meters)

def _iniciar(nombre="Transaccion"):
    TransactionManager.Instance.EnsureInTransaction(doc)

def _finalizar():
    TransactionManager.Instance.TransactionTaskDone()


def crear_vista_3d_isometrica(nombre):
    """
    Crea una vista 3D isometrica con el nombre indicado.

    Args:
        nombre: nombre de la vista como string

    Returns:
        View3D creada, o None si no hay tipo de vista 3D disponible

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tipos = list(FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements())
    tipo = next((t for t in tipos if t.ViewFamily == ViewFamily.ThreeDimensional), None)
    if tipo is None:
        return None
    _iniciar("Crear Vista 3D Isometrica")
    vista = View3D.CreateIsometric(doc, tipo.Id)
    vista.Name = nombre
    _finalizar()
    return vista


def crear_seccion_desde_curva(curva, offset_m=2.0, altura_m=3.0):
    """
    Crea una ViewSection a partir de una curva o elemento con curva de ubicacion.

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
    v   = fin - ini
    w   = v.GetLength()
    mid = ini + 0.5 * v
    dir_l  = v.Normalize()
    normal = dir_l.CrossProduct(XYZ.BasisZ)
    off    = _metros_a_pies(offset_m)
    alt    = _metros_a_pies(altura_m)

    bb = BoundingBoxXYZ()
    t  = Transform.Identity
    t.Origin = mid
    t.BasisX = dir_l
    t.BasisY = XYZ.BasisZ
    t.BasisZ = normal
    bb.Transform = t
    bb.Min = XYZ(-w / 2, ini.Z, -off)
    bb.Max = XYZ( w / 2, alt,    off)

    tipos   = list(FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements())
    tipo_id = next(t.Id for t in tipos if t.ViewFamily == ViewFamily.Section)
    _iniciar("Crear Seccion desde Curva")
    seccion = ViewSection.CreateSection(doc, tipo_id, bb)
    _finalizar()
    return seccion


def crear_alzado_en_punto(punto_xyz, vista_plan_id, indice=0, escala=100):
    """
    Crea un ElevationMarker y un alzado en el indice indicado.

    Args:
        punto_xyz: XYZ de posicion del marcador de alzado
        vista_plan_id: ElementId de la vista de planta donde se crea el marcador
        indice: 0=Norte/Derecha, 1=Este/Abajo, 2=Sur/Izquierda, 3=Oeste/Arriba
        escala: escala de la vista de alzado

    Returns:
        tupla (ElevationMarker, View de alzado)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tipos   = list(FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements())
    tipo_id = next(t.Id for t in tipos if t.ViewFamily == ViewFamily.Elevation)
    _iniciar("Crear Alzado")
    marker = ElevationMarker.CreateElevationMarker(doc, tipo_id, punto_xyz, escala)
    alzado = marker.CreateElevation(doc, vista_plan_id, indice)
    _finalizar()
    return marker, alzado


def crear_cartela(vista_plan, punto1_xyz, punto2_xyz):
    """
    Crea una Callout (llamada) en una vista de planta.

    Args:
        vista_plan: ViewPlan de Revit donde se crea la llamada
        punto1_xyz: XYZ de la esquina inferior izquierda del recuadro
        punto2_xyz: XYZ de la esquina superior derecha del recuadro

    Returns:
        ViewSection (callout) creada

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tipos   = list(FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements())
    tipo_id = next(t.Id for t in tipos if t.ViewFamily == ViewFamily.FloorPlan)
    _iniciar("Crear Cartela")
    llamada = ViewSection.CreateCallout(doc, vista_plan.Id, tipo_id, punto1_xyz, punto2_xyz)
    _finalizar()
    return llamada


def crear_vista_detalle(elemento_referencia):
    """
    Crea una vista de detalle a partir del bounding box de un elemento.

    Args:
        elemento_referencia: elemento Revit cuyo bounding box define el area de detalle

    Returns:
        ViewSection (detalle) creada

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    caja    = elemento_referencia.get_BoundingBox(doc.ActiveView)
    tipos   = list(FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements())
    tipo_id = next(t.Id for t in tipos if t.ViewFamily == ViewFamily.Detail)
    _iniciar("Crear Detalle")
    detalle = ViewSection.CreateDetail(doc, tipo_id, caja)
    _finalizar()
    return detalle


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


def establecer_rango_de_vista(vista_plan, plano, nivel=None, offset_m=None):
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
    _iniciar("Establecer Rango Vista")
    if nivel is not None:
        rango.SetLevelId(plano, nivel.Id)
    if offset_m is not None:
        rango.SetOffset(plano, _metros_a_pies(offset_m))
    vista_plan.SetViewRange(rango)
    _finalizar()


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
    _iniciar("Escala Vista")
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
    _iniciar("Nivel Detalle Vista")
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
    _iniciar("Estilo Visual Vista")
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
    _iniciar("Disciplina Vista")
    vista.Discipline = disciplina
    _finalizar()


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
    _iniciar("Ocultar Elementos")
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
    _iniciar("Mostrar Elementos Ocultos")
    vista.UnhideElements(ids)
    _finalizar()


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
    _iniciar("CropBox Vista")
    vista.CropBoxActive = activar
    _finalizar()


def establecer_cropbox(vista, bbox_xyz):
    """
    Asigna un BoundingBoxXYZ como crop box de la vista y lo activa.

    Args:
        vista: View de Revit
        bbox_xyz: BoundingBoxXYZ de Revit

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar("Establecer CropBox")
    vista.CropBox        = bbox_xyz
    vista.CropBoxActive  = True
    vista.CropBoxVisible = True
    _finalizar()


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
    _iniciar("Aplicar Plantilla Vista")
    vista.ViewTemplateId = plantilla_id
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
    _iniciar("Ocultar/Mostrar Categoria")
    vista.SetCategoryHidden(cat_id, ocultar)
    _finalizar()


def exportar_vista_a_imagen(vista, ruta_salida, anchura_px=1920):
    """
    Exporta una vista a imagen PNG en la ruta indicada.

    Args:
        vista: View de Revit a exportar
        ruta_salida: ruta base de salida (sin extension)
        anchura_px: anchura en pixeles (por defecto 1920)

    Returns:
        ruta_salida

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    ids = List[ElementId]()
    ids.Add(vista.Id)
    opciones = ImageExportOptions()
    opciones.FilePath        = ruta_salida
    opciones.ExportRange     = ExportRange.SetOfViews
    opciones.SetViewsAndSheets(ids)
    opciones.ImageResolution = ImageResolution.DPI_150
    opciones.HLRandWFViewsFileType = ImageFileType.PNG
    doc.ExportImage(opciones)
    return ruta_salida
