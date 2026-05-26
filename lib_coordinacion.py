# -*- coding: utf-8 -*-
"""
lib_coordinacion.py
Biblioteca de funciones Revit/Dynamo — Coordinacion BIM
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

from System.Collections.Generic import List
from Autodesk.Revit.DB import (
    FilteredElementCollector, ElementId, Level, View, ViewSheet, ViewPlan,
    ViewSection, View3D, ViewFamilyType, ViewFamily, ViewDuplicateOption,
    Viewport, UV, XYZ, BoundingBoxXYZ, Transform, Phase, Group,
    RevitLinkInstance, ImportInstance, BuiltInCategory, BuiltInParameter,
    WorksetKindFilter, WorksetKind, FilteredWorksetCollector, CategoryType,
    ImageExportOptions, ExportRange, ImageResolution, ImageFileType,
    OverrideGraphicSettings, Color, ElementTransformUtils, FamilySymbol,
    ElevationMarker
)
from Autodesk.Revit.DB import UnitUtils, UnitTypeId
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

def _iniciar_transaccion(nombre="Transaccion"):
    TransactionManager.Instance.EnsureInTransaction(doc)

def _finalizar_transaccion():
    TransactionManager.Instance.TransactionTaskDone()


def obtener_documento_activo():
    """
    Retorna el documento Revit activo del DocumentManager.

    Args:
        (ninguno)

    Returns:
        Document de Revit activo

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return DocumentManager.Instance.CurrentDBDocument


def obtener_todos_los_elementos(categoria=None):
    """
    Colecta todos los elementos de instancia del documento, filtrados opcionalmente por categoria.

    Args:
        categoria: BuiltInCategory opcional (ej. BuiltInCategory.OST_Walls)

    Returns:
        lista de elementos Revit

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    col = FilteredElementCollector(doc).WhereElementIsNotElementType()
    if categoria:
        col = col.OfCategory(categoria)
    return list(col.ToElements())


def obtener_elementos_por_clase(clase):
    """
    Colecta todos los elementos de una clase .NET del documento.

    Args:
        clase: tipo .NET de Revit (ej. Wall, Level, Floor)

    Returns:
        lista de elementos Revit

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(FilteredElementCollector(doc).OfClass(clase).ToElements())


def obtener_elemento_por_id(element_id):
    """
    Obtiene un elemento por su ElementId (acepta int o ElementId).

    Args:
        element_id: entero o ElementId del elemento

    Returns:
        elemento Revit o None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if isinstance(element_id, int):
        element_id = ElementId(element_id)
    return doc.GetElement(element_id)


def obtener_niveles():
    """
    Retorna todos los niveles del documento ordenados por elevacion ascendente.

    Args:
        (ninguno)

    Returns:
        lista de objetos Level ordenados por elevacion

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    niveles = list(FilteredElementCollector(doc).OfClass(Level).ToElements())
    return sorted(niveles, key=lambda l: l.Elevation)


def obtener_vistas_por_tipo(tipo_vista):
    """
    Filtra vistas del documento por ViewType excluyendo plantillas.

    Args:
        tipo_vista: ViewType (ej. ViewType.FloorPlan, ViewType.Section)

    Returns:
        lista de vistas del tipo indicado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    vistas = list(FilteredElementCollector(doc).OfClass(View).ToElements())
    return [v for v in vistas if v.ViewType == tipo_vista and not v.IsTemplate]


def obtener_plantillas_de_vista():
    """
    Retorna todas las plantillas de vista del documento.

    Args:
        (ninguno)

    Returns:
        lista de objetos View que son plantillas

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    vistas = list(FilteredElementCollector(doc).OfClass(View).ToElements())
    return [v for v in vistas if v.IsTemplate]


def obtener_planos():
    """
    Retorna todos los planos (ViewSheet) del documento.

    Args:
        (ninguno)

    Returns:
        lista de objetos ViewSheet

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(FilteredElementCollector(doc).OfClass(ViewSheet).ToElements())


def obtener_plano_por_numero(numero):
    """
    Busca y retorna un plano (ViewSheet) por su numero de plano.

    Args:
        numero: string con el numero de plano (ej. "A-101")

    Returns:
        ViewSheet o None si no existe

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    for p in obtener_planos():
        if p.SheetNumber == numero:
            return p
    return None


def obtener_tipos_de_familia(nombre_familia):
    """
    Retorna todos los FamilySymbol de una familia por su nombre.

    Args:
        nombre_familia: nombre de la familia como string

    Returns:
        lista de FamilySymbol

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tipos = list(FilteredElementCollector(doc).OfClass(FamilySymbol).ToElements())
    return [t for t in tipos if t.Family.Name == nombre_familia]


def obtener_parametros_proyecto():
    """
    Lista todos los parametros de proyecto (compartidos y de proyecto).

    Args:
        (ninguno)

    Returns:
        lista de dicts {nombre, grupo}

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    resultado = []
    it = doc.ParameterBindings.ForwardIterator()
    it.Reset()
    while it.MoveNext():
        d = it.Key
        try:
            grupo = str(d.GetGroupTypeId())
        except AttributeError:
            grupo = str(d.ParameterGroup)
        resultado.append({"nombre": d.Name, "grupo": grupo})
    return resultado


def obtener_links_revit():
    """
    Retorna todas las instancias de link Revit del documento.

    Args:
        (ninguno)

    Returns:
        lista de RevitLinkInstance

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements())


def obtener_links_cad():
    """
    Retorna todas las instancias de importacion/link CAD del documento.

    Args:
        (ninguno)

    Returns:
        lista de ImportInstance

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(FilteredElementCollector(doc).OfClass(ImportInstance).ToElements())


def obtener_advertencias():
    """
    Retorna todas las advertencias activas del documento.

    Args:
        (ninguno)

    Returns:
        lista de FailureMessage

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(doc.GetWarnings())


def obtener_worksets():
    """
    Retorna los worksets de usuario del documento colaborativo.

    Args:
        (ninguno)

    Returns:
        lista de Workset, o lista vacia si el documento no es colaborativo

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not doc.IsWorkshared:
        return []
    filtro = WorksetKindFilter(WorksetKind.UserWorkset)
    return list(FilteredWorksetCollector(doc).WherePasses(filtro).ToWorksets())


def asignar_workset(elemento, workset_id):
    """
    Asigna un workset a un elemento. Requiere transaccion activa.

    Args:
        elemento: elemento Revit
        workset_id: WorksetId a asignar

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = elemento.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
    if param and not param.IsReadOnly:
        param.Set(workset_id.IntegerValue)


def obtener_categorias_modelo():
    """
    Lista todas las categorias de modelo del documento.

    Args:
        (ninguno)

    Returns:
        lista de Category de tipo Model

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    cats = doc.Settings.Categories
    return [c for c in cats if c.CategoryType == CategoryType.Model]


def obtener_fases():
    """
    Retorna todas las fases del proyecto.

    Args:
        (ninguno)

    Returns:
        lista de Phase

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(FilteredElementCollector(doc).OfClass(Phase).ToElements())


def obtener_grupos():
    """
    Retorna todos los grupos del documento.

    Args:
        (ninguno)

    Returns:
        lista de Group

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(FilteredElementCollector(doc).OfClass(Group).ToElements())


def exportar_ids_a_txt(elementos, ruta_archivo):
    """
    Exporta los ElementId de una lista de elementos a un archivo de texto.

    Args:
        elementos: lista de elementos Revit
        ruta_archivo: ruta completa del archivo .txt de salida

    Returns:
        ruta_archivo

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    def _id_a_int(eid):
        try:
            return int(eid.Value)
        except AttributeError:
            return eid.IntegerValue

    with io.open(ruta_archivo, "w", encoding="utf-8") as f:
        for e in elementos:
            f.write(str(_id_a_int(e.Id)) + "\n")
    return ruta_archivo


def crear_vista_plano(nivel, tipo_vista_id, nombre):
    """
    Crea una vista de planta para un nivel dado.

    Args:
        nivel: objeto Level de Revit
        tipo_vista_id: ElementId del ViewFamilyType de planta
        nombre: nombre de la nueva vista como string

    Returns:
        ViewPlan creada

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar_transaccion("Crear Vista Planta")
    vista = ViewPlan.Create(doc, tipo_vista_id, nivel.Id)
    vista.Name = nombre
    _finalizar_transaccion()
    return vista


def crear_plano(numero, nombre, tipo_plano_id=None):
    """
    Crea un plano (ViewSheet) nuevo con numero y nombre.

    Args:
        numero: numero del plano como string (ej. "A-101")
        nombre: nombre del plano como string
        tipo_plano_id: ElementId del tipo de cajetín (opcional, usa el primero si es None)

    Returns:
        ViewSheet creado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar_transaccion("Crear Plano")
    if tipo_plano_id is None:
        tipos = list(
            FilteredElementCollector(doc)
            .OfClass(FamilySymbol)
            .OfCategory(BuiltInCategory.OST_TitleBlocks)
            .ToElements()
        )
        tipo_plano_id = tipos[0].Id if tipos else ElementId.InvalidElementId
    plano = ViewSheet.Create(doc, tipo_plano_id)
    plano.SheetNumber = numero
    plano.Name = nombre
    _finalizar_transaccion()
    return plano


def anadir_vista_a_plano(plano, vista, punto_uv=None):
    """
    Anade una vista a un plano en la posicion indicada.

    Args:
        plano: ViewSheet de destino
        vista: View a insertar
        punto_uv: UV con la posicion en el plano (por defecto (0.5, 0.5))

    Returns:
        Viewport creado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if punto_uv is None:
        punto_uv = UV(0.5, 0.5)
    _iniciar_transaccion("Anadir Vista a Plano")
    viewport = Viewport.Create(doc, plano.Id, vista.Id, XYZ(punto_uv.U, punto_uv.V, 0))
    _finalizar_transaccion()
    return viewport


def duplicar_vista(vista, nombre):
    """
    Duplica una vista con el nombre indicado (sin detalle).

    Args:
        vista: View de origen
        nombre: nombre de la nueva vista como string

    Returns:
        View duplicada

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar_transaccion("Duplicar Vista")
    nuevo_id = vista.Duplicate(ViewDuplicateOption.Duplicate)
    nueva = doc.GetElement(nuevo_id)
    try:
        nueva.Name = nombre
    except Exception:
        pass
    _finalizar_transaccion()
    return nueva


def aplicar_plantilla_vista(vistas, nombre_plantilla):
    """
    Aplica una plantilla de vista por nombre a una lista de vistas.

    Args:
        vistas: lista de View de Revit
        nombre_plantilla: nombre de la plantilla como string

    Returns:
        lista de vistas actualizadas, o None si la plantilla no existe

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    todas = list(FilteredElementCollector(doc).OfClass(View).ToElements())
    plantilla = next((v for v in todas if v.IsTemplate and v.Name == nombre_plantilla), None)
    if plantilla is None:
        return None
    _iniciar_transaccion("Aplicar Plantilla Vista")
    for v in vistas:
        v.ViewTemplateId = plantilla.Id
    _finalizar_transaccion()
    return vistas


def crear_seccion(curva, tipo_vista_id, offset=1.0, altura=3.0):
    """
    Crea una vista de seccion a partir de una curva Revit.

    Args:
        curva: curva Revit (Line) que define el eje de corte
        tipo_vista_id: ElementId del ViewFamilyType de seccion
        offset: profundidad lateral en metros (por defecto 1.0)
        altura: altura de corte en metros (por defecto 3.0)

    Returns:
        ViewSection creada

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    sp  = curva.GetEndPoint(0)
    ep  = curva.GetEndPoint(1)
    v   = ep - sp
    w   = v.GetLength()
    mid = sp + 0.5 * v
    dir_linea = v.Normalize()
    up  = XYZ.BasisZ
    normal = dir_linea.CrossProduct(up)

    off = _metros_a_pies(offset)
    alt = _metros_a_pies(altura)

    bb = BoundingBoxXYZ()
    t  = Transform.Identity
    t.Origin = mid
    t.BasisX = dir_linea
    t.BasisY = up
    t.BasisZ = normal
    bb.Transform = t
    bb.Min = XYZ(-w / 2, 0, -off)
    bb.Max = XYZ( w / 2, alt,  off)

    _iniciar_transaccion("Crear Seccion")
    seccion = ViewSection.CreateSection(doc, tipo_vista_id, bb)
    _finalizar_transaccion()
    return seccion


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
    _iniciar_transaccion("Crear Vista 3D")
    vista = View3D.CreateIsometric(doc, tipo.Id)
    vista.Name = nombre
    _finalizar_transaccion()
    return vista


def crear_vista_plano_desde_habitacion(habitacion, tipo_vista_id, offset_m=1.0, escala=50):
    """
    Crea una vista de planta recortada al bounding box de una habitacion.

    Args:
        habitacion: elemento Room de Revit
        tipo_vista_id: ElementId del ViewFamilyType de planta
        offset_m: margen adicional alrededor de la habitacion en metros
        escala: escala de la vista (ej. 50 para 1:50)

    Returns:
        ViewPlan recortada a la habitacion

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    bbox = habitacion.BoundingBox[doc.ActiveView]
    off  = _metros_a_pies(offset_m)
    nuevo_bb = BoundingBoxXYZ()
    nuevo_bb.Min = XYZ(bbox.Min.X - off, bbox.Min.Y - off, bbox.Min.Z - off)
    nuevo_bb.Max = XYZ(bbox.Max.X + off, bbox.Max.Y + off, bbox.Max.Z + off)

    _iniciar_transaccion("Crear Vista Plano Habitacion")
    nivel = habitacion.Level
    vista = ViewPlan.Create(doc, tipo_vista_id, nivel.Id)
    vista.CropBox        = nuevo_bb
    vista.CropBoxActive  = True
    vista.CropBoxVisible = False
    vista.Scale          = escala
    _finalizar_transaccion()
    return vista


def exportar_vistas_a_imagen(vistas, ruta_base, formato=None):
    """
    Exporta una lista de vistas a imagenes en la ruta indicada.

    Args:
        vistas: lista de View de Revit
        ruta_base: ruta base de salida (sin extension)
        formato: ImageFileType (por defecto ImageFileType.PNG)

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
    opciones.FilePath        = ruta_base
    opciones.ExportRange     = ExportRange.SetOfViews
    opciones.SetViewsAndSheets(ids)
    opciones.ImageResolution = ImageResolution.DPI_150
    opciones.HLRandWFViewsFileType = formato
    doc.ExportImage(opciones)
    return ruta_base


def copiar_elementos_entre_vistas(vista_origen, vista_destino, elementos, transformacion=None):
    """
    Copia elementos anotados de una vista a otra.

    Args:
        vista_origen: View de origen
        vista_destino: View de destino
        elementos: lista de elementos Revit a copiar
        transformacion: objeto Transform de Revit (opcional)

    Returns:
        lista de elementos copiados

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    ids = List[ElementId]([e.Id for e in elementos if hasattr(e, "Id")])
    _iniciar_transaccion("Copiar Elementos Entre Vistas")
    copiados = ElementTransformUtils.CopyElements(
        vista_origen, ids, vista_destino, transformacion, None)
    _finalizar_transaccion()
    return [doc.GetElement(i) for i in copiados]


def sobreescribir_grafico_elemento(vista, elemento, color_superficie=None,
                                   patron_sup_id=None, color_corte=None, patron_corte_id=None):
    """
    Aplica overrides de color y patron de relleno a un elemento en una vista.

    Args:
        vista: View donde aplicar el override
        elemento: elemento Revit
        color_superficie: tupla (R, G, B) para el color de superficie (opcional)
        patron_sup_id: ElementId del patron de relleno de superficie (opcional)
        color_corte: tupla (R, G, B) para el color de corte (opcional)
        patron_corte_id: ElementId del patron de corte (opcional)

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    ogs = OverrideGraphicSettings()
    if color_superficie:
        col = Color(color_superficie[0], color_superficie[1], color_superficie[2])
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
    _iniciar_transaccion("Override Grafico")
    vista.SetElementOverrides(elemento.Id, ogs)
    _finalizar_transaccion()


def crear_alzado(posicion_xyz, vista_plan_id, indice=0, escala=100):
    """
    Crea un ElevationMarker y un alzado en el indice indicado.

    Args:
        posicion_xyz: XYZ de posicion del marcador de alzado
        vista_plan_id: ElementId de la vista de planta donde se crea el marcador
        indice: 0=Norte/Derecha, 1=Este/Abajo, 2=Sur/Izquierda, 3=Oeste/Arriba
        escala: escala de la vista de alzado

    Returns:
        tupla (ElevationMarker, View de alzado)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tipos = list(FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements())
    tipo_id = next(t.Id for t in tipos if t.ViewFamily == ViewFamily.Elevation)
    _iniciar_transaccion("Crear Alzado")
    marker = ElevationMarker.CreateElevationMarker(doc, tipo_id, posicion_xyz, escala)
    alzado = marker.CreateElevation(doc, vista_plan_id, indice)
    _finalizar_transaccion()
    return marker, alzado
