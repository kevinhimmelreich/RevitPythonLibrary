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

# ── Revit API ────────────────────────────────────────────────────────────────
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
clr.AddReference("RevitServices")
clr.AddReference("RevitNodes")

from System.Collections.Generic import List  # noqa: E402

from Autodesk.Revit.DB import (  # noqa: E402
    FilteredElementCollector, ElementId, Level, XYZ,
    BuiltInParameter, StorageType,
    WorksetKindFilter, WorksetKind, FilteredWorksetCollector,
    WorksetDefaultVisibilitySettings, CategoryType,
    RevitLinkInstance, RevitLinkType, ElementMulticategoryFilter,
    ElementTransformUtils, UnitUtils, UnitTypeId, Autodesk,
    BoundingBoxIntersectsFilter, BoundingBoxIsInsideFilter,
    BoundingBoxContainsPointFilter, Outline
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


def _metros_a_pies(v):
    return UnitUtils.ConvertToInternalUnits(v, UnitTypeId.Meters)


def _pies_a_metros(v):
    return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.Meters)


def _iniciar():
    TransactionManager.Instance.EnsureInTransaction(doc)


def _finalizar():
    TransactionManager.Instance.TransactionTaskDone()


# ── Niveles ──────────────────────────────────────────────────────────────────

def obtener_niveles():
    """
    Retorna todos los niveles del documento ordenados por elevacion.

    Returns:
        lista de Level ordenados de menor a mayor elevacion
    """
    niveles = list(FilteredElementCollector(doc).OfClass(Level).ToElements())
    return sorted(niveles, key=lambda n: n.Elevation)


def crear_nivel(elevacion_m, nombre):
    """
    Crea un nivel a la elevacion indicada.

    Args:
        elevacion_m: elevacion en metros
        nombre: nombre del nivel

    Returns:
        Level creado
    """
    _iniciar()
    nivel = Level.Create(doc, _metros_a_pies(elevacion_m))
    try:
        nivel.Name = nombre
    except Exception:
        pass
    _finalizar()
    return nivel


def crear_niveles_en_bloque(elevaciones_m, nombres):
    """
    Crea varios niveles de una vez a partir de listas de elevaciones y
    nombres.

    Args:
        elevaciones_m: lista de elevaciones en metros
        nombres: lista de nombres para los niveles

    Returns:
        lista de Level creados
    """
    _iniciar()
    resultado = []
    for elev, nombre in zip(elevaciones_m, nombres):
        n = Level.Create(doc, _metros_a_pies(elev))
        try:
            n.Name = nombre
        except Exception:
            pass
        resultado.append(n)
    _finalizar()
    return resultado


# ── Advertencias ─────────────────────────────────────────────────────────────

def obtener_advertencias():
    """
    Retorna todas las advertencias activas del documento.

    Returns:
        lista de FailureMessage
    """
    return list(doc.GetWarnings())


def analizar_advertencias_por_tipo():
    """
    Agrupa las advertencias del documento por tipo de fallo.
    Limpia el texto largo del SDK de Autodesk.

    Returns:
        lista de dicts con claves:
          "tipo": texto de la advertencia (limpio)
          "elementos": lista de ElementId de los elementos afectados
          "cantidad": numero de advertencias de ese tipo
    """
    texto_a_limpiar = (
        "debido a uno de los motivos siguientes o a ambos:")
    advertencias = list(doc.GetWarnings())
    agrupadas = {}
    for adv in advertencias:
        desc = (Autodesk.Revit.DB.FailureMessage
                .GetDescriptionText(adv) or "")
        desc = desc.replace(texto_a_limpiar, "").strip()
        if ": " in desc:
            desc = desc.split(": ", 1)[1]
        if " no están conectados a una única red física" in desc:
            desc = "Elementos no conectados a una única red física"
        elem_ids = list(
            Autodesk.Revit.DB.FailureMessage.GetFailingElements(adv)
            or
            Autodesk.Revit.DB.FailureMessage.GetAdditionalElements(adv)
        )
        if desc not in agrupadas:
            agrupadas[desc] = []
        agrupadas[desc].extend(elem_ids)
    return [
        {"tipo": k, "elementos": v, "cantidad": len(v)}
        for k, v in sorted(
            agrupadas.items(), key=lambda x: -len(x[1]))
    ]


def exportar_advertencias_a_csv(ruta_csv):
    """
    Exporta las advertencias del documento a un archivo CSV.

    Args:
        ruta_csv: ruta completa del archivo de salida

    Returns:
        ruta_csv
    """
    grupos = analizar_advertencias_por_tipo()
    with io.open(ruta_csv, "w", encoding="utf-8") as f:
        f.write("Tipo;Cantidad;ElementIds\n")
        for g in grupos:
            ids_str = " | ".join(
                str(getattr(eid, "Value", eid.IntegerValue))
                for eid in g["elementos"]
            )
            f.write(u"{};{};{}\n".format(
                g["tipo"], g["cantidad"], ids_str))
    return ruta_csv


# ── Worksets ─────────────────────────────────────────────────────────────────

def obtener_worksets():
    """
    Retorna los worksets de usuario del documento colaborativo.

    Returns:
        lista de Workset, o lista vacia si no es colaborativo
    """
    if not doc.IsWorkshared:
        return []
    filtro = WorksetKindFilter(WorksetKind.UserWorkset)
    return list(
        FilteredWorksetCollector(doc).WherePasses(filtro).ToWorksets()
    )


def asignar_workset(elemento, workset_id):
    """
    Asigna un workset a un elemento. Requiere transaccion activa.

    Args:
        elemento: elemento Revit
        workset_id: WorksetId a asignar

    Returns:
        None
    """
    param = elemento.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
    if param and not param.IsReadOnly:
        param.Set(workset_id.IntegerValue)


def asignar_workset_a_lista(elementos, workset_id):
    """
    Asigna masivamente un workset a una lista de elementos.

    Args:
        elementos: lista de elementos Revit
        workset_id: WorksetId a asignar

    Returns:
        numero de elementos modificados (int)
    """
    _iniciar()
    count = 0
    for elem in elementos:
        param = elem.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
        if param and not param.IsReadOnly:
            param.Set(workset_id.IntegerValue)
            count += 1
    _finalizar()
    return count


def asignar_workset_por_categoria(categoria_bic, workset_id):
    """
    Asigna un workset a todos los elementos de una categoria BuiltIn.

    Args:
        categoria_bic: BuiltInCategory a procesar
        workset_id: WorksetId a asignar

    Returns:
        numero de elementos modificados (int)
    """
    elementos = list(
        FilteredElementCollector(doc)
        .OfCategory(categoria_bic)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    return asignar_workset_a_lista(elementos, workset_id)


def establecer_visibilidad_workset(workset_id, visible=False):
    """
    Cambia la visibilidad por defecto de un workset en todas las vistas.

    Args:
        workset_id: WorksetId del workset
        visible: True para mostrar, False para ocultar

    Returns:
        None
    """
    _iniciar()
    cfg = WorksetDefaultVisibilitySettings.GetWorksetDefaultVisibilitySettings(
        doc)
    cfg.SetWorksetVisibility(workset_id, visible)
    _finalizar()


def detectar_elementos_sin_workset(lista_elementos, workset_id_esperado):
    """
    Devuelve los elementos cuyo workset NO coincide con el esperado.
    Util para control de calidad BIM.

    Args:
        lista_elementos: lista de elementos Revit a verificar
        workset_id_esperado: WorksetId correcto

    Returns:
        lista de elementos con workset incorrecto
    """
    bip = BuiltInParameter.ELEM_PARTITION_PARAM
    esperado = workset_id_esperado.IntegerValue
    resultado = []
    for e in lista_elementos:
        p = e.get_Parameter(bip)
        if p and p.AsInteger() != esperado:
            resultado.append(e)
    return resultado


# ── Links Revit ──────────────────────────────────────────────────────────────

def obtener_links_revit():
    """
    Retorna todas las instancias de link Revit del documento.

    Returns:
        lista de RevitLinkInstance
    """
    return list(
        FilteredElementCollector(doc)
        .OfClass(RevitLinkInstance).ToElements()
    )


def obtener_elementos_en_link(link_instancia, categorias_bic):
    """
    Colecta elementos de un documento enlazado por una o varias categorias.
    Comprueba que el link este cargado antes de acceder al documento.

    Args:
        link_instancia: RevitLinkInstance del link
        categorias_bic: BuiltInCategory o lista de BuiltInCategory

    Returns:
        tupla (lista_elementos, transform_total) donde transform_total es
        el Transform del link en coordenadas del proyecto anfitrion,
        o ([], None) si el link no esta cargado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not RevitLinkType.IsLoaded(doc, link_instancia.GetTypeId()):
        return [], None
    link_doc = link_instancia.GetLinkDocument()
    if not isinstance(categorias_bic, (list, tuple)):
        categorias_bic = [categorias_bic]
    ids_cat = List[ElementId](ElementId(c) for c in categorias_bic)
    filtro = ElementMulticategoryFilter(ids_cat)
    elementos = list(
        FilteredElementCollector(link_doc)
        .WhereElementIsNotElementType()
        .WherePasses(filtro)
        .ToElements()
    )
    transform = link_instancia.GetTotalTransform()
    return elementos, transform


def adquirir_coordenadas_de_link(link_instancia):
    """
    Adquiere las coordenadas del proyecto desde un link Revit.

    Args:
        link_instancia: RevitLinkInstance de referencia

    Returns:
        True si se adquirieron correctamente
    """
    _iniciar()
    doc.AcquireCoordinates(link_instancia.Id)
    _finalizar()
    return True


def copiar_elementos_desde_link(
        link_instancia, ids_elementos, opciones_pegar=None):
    """
    Copia elementos de un documento enlazado al documento activo
    usando ElementTransformUtils.

    Args:
        link_instancia: RevitLinkInstance de origen
        ids_elementos: lista de ElementId del link
        opciones_pegar: CopyPasteOptions (opcional)

    Returns:
        lista de elementos copiados en el documento activo
    """
    if not RevitLinkType.IsLoaded(doc, link_instancia.GetTypeId()):
        return []
    link_doc = link_instancia.GetLinkDocument()
    tf = link_instancia.GetTotalTransform()
    ids_net = List[ElementId](ids_elementos)
    _iniciar()
    nuevos_ids = ElementTransformUtils.CopyElements(
        link_doc, ids_net, doc, tf, opciones_pegar)
    _finalizar()
    return [doc.GetElement(i) for i in nuevos_ids]


def comparar_parametro_en_link(
        elementos_host, link_instancia, nombre_param):
    """
    Compara el valor de un parametro entre elementos del host y sus
    equivalentes en un link por UniqueId.

    Args:
        elementos_host: lista de elementos Revit del documento activo
        link_instancia: RevitLinkInstance
        nombre_param: nombre del parametro a comparar

    Returns:
        lista de dicts con claves:
          "elemento_host", "valor_host", "valor_link", "igual"
    """
    if not RevitLinkType.IsLoaded(doc, link_instancia.GetTypeId()):
        return []
    link_doc = link_instancia.GetLinkDocument()
    resultado = []
    for elem in elementos_host:
        uid = elem.UniqueId
        elem_link = link_doc.GetElement(uid)
        p_host = elem.LookupParameter(nombre_param)
        val_host = p_host.AsString() if p_host else None
        val_link = None
        if elem_link:
            p_link = elem_link.LookupParameter(nombre_param)
            val_link = p_link.AsString() if p_link else None
        resultado.append({
            "elemento_host": elem,
            "valor_host": val_host,
            "valor_link": val_link,
            "igual": val_host == val_link,
        })
    return resultado


def obtener_elemento_en_link_por_unique_id(link_instancia, unique_id):
    """
    Busca un elemento en un link Revit por su UniqueId.

    Args:
        link_instancia: RevitLinkInstance del link
        unique_id: string con el UniqueId del elemento

    Returns:
        elemento Revit del link, o None si no se encuentra o no cargado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not RevitLinkType.IsLoaded(doc, link_instancia.GetTypeId()):
        return None
    link_doc = link_instancia.GetLinkDocument()
    return link_doc.GetElement(unique_id)


def filtrar_en_link_por_parametro(
        link_instancia, categoria_bic, nombre_param, valor):
    """
    Filtra elementos de un link por el valor de un parametro de instancia.
    La comparacion se hace como cadena de texto.

    Args:
        link_instancia: RevitLinkInstance del link
        categoria_bic: BuiltInCategory a colectar
        nombre_param: nombre del parametro como string
        valor: valor a buscar

    Returns:
        tupla (elementos_filtrados, transform_total)
        o ([], None) si el link no esta cargado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not RevitLinkType.IsLoaded(doc, link_instancia.GetTypeId()):
        return [], None
    link_doc = link_instancia.GetLinkDocument()
    elementos = list(
        FilteredElementCollector(link_doc)
        .OfCategory(categoria_bic)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    valor_str = str(valor)
    resultado = []
    for e in elementos:
        p = e.LookupParameter(nombre_param)
        if p is None:
            continue
        t = p.StorageType
        if t == StorageType.String:
            v = p.AsString()
        elif t == StorageType.Integer:
            v = p.AsInteger()
        elif t == StorageType.Double:
            v = p.AsDouble()
        elif t == StorageType.ElementId:
            try:
                v = p.AsElementId().Value
            except AttributeError:
                v = p.AsElementId().IntegerValue
        else:
            continue
        if str(v) == valor_str:
            resultado.append(e)
    return resultado, link_instancia.GetTotalTransform()


def filtrar_en_link_por_boundingbox(
        link_instancia, bbox_xyz, categoria_bic=None,
        tolerancia_m=0.0):
    """
    Filtra elementos de un link cuyo bounding box intersecta con el bbox
    dado (en coordenadas del host). Transforma el bbox al espacio del link
    antes de aplicar BoundingBoxIntersectsFilter.

    Args:
        link_instancia: RevitLinkInstance del link
        bbox_xyz: BoundingBoxXYZ en coordenadas del proyecto host
        categoria_bic: BuiltInCategory opcional
        tolerancia_m: margen de tolerancia en metros

    Returns:
        tupla (elementos_filtrados, transform_total)
        o ([], None) si el link no esta cargado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not RevitLinkType.IsLoaded(doc, link_instancia.GetTypeId()):
        return [], None
    link_doc = link_instancia.GetLinkDocument()
    tf = link_instancia.GetTotalTransform()
    inv = tf.Inverse
    min_link = inv.OfPoint(bbox_xyz.Min)
    max_link = inv.OfPoint(bbox_xyz.Max)
    mn = XYZ(
        min(min_link.X, max_link.X),
        min(min_link.Y, max_link.Y),
        min(min_link.Z, max_link.Z),
    )
    mx = XYZ(
        max(min_link.X, max_link.X),
        max(min_link.Y, max_link.Y),
        max(min_link.Z, max_link.Z),
    )
    tol = UnitUtils.ConvertToInternalUnits(tolerancia_m, UnitTypeId.Meters)
    outline = Outline(mn, mx)
    filtro = BoundingBoxIntersectsFilter(outline, tol)
    col = FilteredElementCollector(link_doc).WherePasses(filtro)
    if categoria_bic is not None:
        col = col.OfCategory(categoria_bic)
    elementos = list(col.WhereElementIsNotElementType().ToElements())
    return elementos, tf


def filtrar_en_link_dentro_de_bbox(
        link_instancia, bbox_xyz, categoria_bic=None,
        tolerancia_m=0.0):
    """
    Filtra elementos de un link completamente contenidos dentro del bbox
    del host. Usa BoundingBoxIsInsideFilter en espacio del link.

    Args:
        link_instancia: RevitLinkInstance del link
        bbox_xyz: BoundingBoxXYZ en coordenadas del proyecto host
        categoria_bic: BuiltInCategory opcional
        tolerancia_m: margen de tolerancia en metros

    Returns:
        tupla (elementos_filtrados, transform_total)
        o ([], None) si el link no esta cargado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not RevitLinkType.IsLoaded(doc, link_instancia.GetTypeId()):
        return [], None
    link_doc = link_instancia.GetLinkDocument()
    tf = link_instancia.GetTotalTransform()
    inv = tf.Inverse
    min_link = inv.OfPoint(bbox_xyz.Min)
    max_link = inv.OfPoint(bbox_xyz.Max)
    mn = XYZ(
        min(min_link.X, max_link.X),
        min(min_link.Y, max_link.Y),
        min(min_link.Z, max_link.Z),
    )
    mx = XYZ(
        max(min_link.X, max_link.X),
        max(min_link.Y, max_link.Y),
        max(min_link.Z, max_link.Z),
    )
    tol = UnitUtils.ConvertToInternalUnits(tolerancia_m, UnitTypeId.Meters)
    outline = Outline(mn, mx)
    filtro = BoundingBoxIsInsideFilter(outline, tol)
    col = FilteredElementCollector(link_doc).WherePasses(filtro)
    if categoria_bic is not None:
        col = col.OfCategory(categoria_bic)
    elementos = list(col.WhereElementIsNotElementType().ToElements())
    return elementos, tf


def filtrar_en_link_contiene_punto(
        link_instancia, punto_xyz, categoria_bic=None,
        tolerancia_m=0.0):
    """
    Filtra elementos de un link cuyo bounding box contiene el punto
    dado (en coordenadas del host).

    Args:
        link_instancia: RevitLinkInstance del link
        punto_xyz: XYZ en coordenadas del proyecto host
        categoria_bic: BuiltInCategory opcional
        tolerancia_m: margen de tolerancia en metros

    Returns:
        tupla (elementos_filtrados, transform_total)
        o ([], None) si el link no esta cargado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not RevitLinkType.IsLoaded(doc, link_instancia.GetTypeId()):
        return [], None
    link_doc = link_instancia.GetLinkDocument()
    tf = link_instancia.GetTotalTransform()
    punto_link = tf.Inverse.OfPoint(punto_xyz)
    tol = UnitUtils.ConvertToInternalUnits(tolerancia_m, UnitTypeId.Meters)
    filtro = BoundingBoxContainsPointFilter(punto_link, tol)
    col = FilteredElementCollector(link_doc).WherePasses(filtro)
    if categoria_bic is not None:
        col = col.OfCategory(categoria_bic)
    elementos = list(col.WhereElementIsNotElementType().ToElements())
    return elementos, tf


# ── Deteccion de colisiones ──────────────────────────────────────────────────

def detectar_colisiones_bbox(elementos_a, elementos_b, tolerancia_m=0.0):
    """
    Detecta colisiones duras entre dos conjuntos de elementos usando sus
    BoundingBox. Rapido para comprobaciones masivas (no usa solidos).

    Args:
        elementos_a: lista de elementos Revit (primer conjunto)
        elementos_b: lista de elementos Revit (segundo conjunto)
        tolerancia_m: margen adicional en metros para considerar colision

    Returns:
        lista de tuplas (elem_a, elem_b) de elementos en colision
    """
    tol = _metros_a_pies(tolerancia_m)
    colisiones = []
    for a in elementos_a:
        bb_a = a.BoundingBox[None]
        if bb_a is None:
            continue
        mn = XYZ(bb_a.Min.X - tol, bb_a.Min.Y - tol, bb_a.Min.Z - tol)
        mx = XYZ(bb_a.Max.X + tol, bb_a.Max.Y + tol, bb_a.Max.Z + tol)
        for b in elementos_b:
            if a.Id == b.Id:
                continue
            bb_b = b.BoundingBox[None]
            if bb_b is None:
                continue
            if (bb_b.Max.X >= mn.X and bb_b.Min.X <= mx.X and
                    bb_b.Max.Y >= mn.Y and bb_b.Min.Y <= mx.Y and
                    bb_b.Max.Z >= mn.Z and bb_b.Min.Z <= mx.Z):
                colisiones.append((a, b))
    return colisiones


def detectar_colisiones_solidos(elementos_a, elementos_b):
    """
    Detecta colisiones exactas usando interseccion de solidos Revit.
    Mas preciso que bbox pero mas lento.

    Args:
        elementos_a: lista de elementos Revit (primer conjunto)
        elementos_b: lista de elementos Revit (segundo conjunto)

    Returns:
        lista de dicts con:
          "elem_a", "elem_b", "solido_colision", "centroide"
    """
    from Autodesk.Revit.DB import Options, BooleanOperationsUtils
    from Autodesk.Revit.DB import BooleanOperationsType
    opts = Options()
    opts.DetailLevel = Autodesk.Revit.DB.ViewDetailLevel.Fine
    colisiones = []
    for a in elementos_a:
        geom_a = a.get_Geometry(opts)
        solidos_a = [
            s for g in (geom_a or [])
            for s in (
                [g] if hasattr(g, "Faces") else
                [ss for ss in g.GetInstanceGeometry()
                 if hasattr(ss, "Faces")]
            )
        ]
        for b in elementos_b:
            if a.Id == b.Id:
                continue
            geom_b = b.get_Geometry(opts)
            solidos_b = [
                s for g in (geom_b or [])
                for s in (
                    [g] if hasattr(g, "Faces") else
                    [ss for ss in g.GetInstanceGeometry()
                     if hasattr(ss, "Faces")]
                )
            ]
            for sa in solidos_a:
                for sb in solidos_b:
                    try:
                        inter = BooleanOperationsUtils.ExecuteBooleanOperation(
                            sa, sb, BooleanOperationsType.Intersect)
                        if inter and inter.Volume > 1e-10:
                            colisiones.append({
                                "elem_a": a,
                                "elem_b": b,
                                "solido_colision": inter,
                                "centroide": inter.ComputeCentroid(),
                            })
                            break
                    except Exception:
                        pass
    return colisiones


# ── Parametros de proyecto ───────────────────────────────────────────────────

def obtener_parametros_proyecto():
    """
    Lista todos los parametros de proyecto del documento.

    Returns:
        lista de dicts {nombre, grupo}
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


def exportar_parametros_a_csv(elementos, nombres_params, ruta_csv):
    """
    Exporta los valores de una lista de parametros de una lista de
    elementos a un archivo CSV.

    Args:
        elementos: lista de elementos Revit
        nombres_params: lista de nombres de parametros a exportar
        ruta_csv: ruta completa del archivo de salida

    Returns:
        ruta_csv
    """
    with io.open(ruta_csv, "w", encoding="utf-8") as f:
        encabezado = u"ElementId;" + u";".join(nombres_params) + u"\n"
        f.write(encabezado)
        for elem in elementos:
            try:
                eid = int(elem.Id.Value)
            except AttributeError:
                eid = elem.Id.IntegerValue
            valores = []
            for np in nombres_params:
                p = elem.LookupParameter(np)
                if p is None:
                    valores.append("")
                else:
                    t = p.StorageType
                    if t == Autodesk.Revit.DB.StorageType.String:
                        valores.append(p.AsString() or "")
                    elif t == Autodesk.Revit.DB.StorageType.Integer:
                        valores.append(str(p.AsInteger()))
                    elif t == Autodesk.Revit.DB.StorageType.Double:
                        valores.append(str(round(p.AsDouble(), 6)))
                    elif t == Autodesk.Revit.DB.StorageType.ElementId:
                        try:
                            valores.append(
                                str(p.AsElementId().Value))
                        except AttributeError:
                            valores.append(
                                str(p.AsElementId().IntegerValue))
                    else:
                        valores.append("")
            f.write(u"{};{}\n".format(eid, u";".join(valores)))
    return ruta_csv


# ── Categorias y modelo ──────────────────────────────────────────────────────

def obtener_categorias_modelo():
    """
    Lista todas las categorias de modelo del documento.

    Returns:
        lista de Category de tipo Model
    """
    cats = doc.Settings.Categories
    return [c for c in cats if c.CategoryType == CategoryType.Model]


def contar_elementos_por_nivel(categoria_bic):
    """
    Cuenta los elementos de una categoria agrupados por nivel.

    Args:
        categoria_bic: BuiltInCategory a contar

    Returns:
        dict {nombre_nivel: cantidad}
    """
    bip_nivel = BuiltInParameter.LEVEL_PARAM
    bip_nivel_alt = BuiltInParameter.FAMILY_LEVEL_PARAM
    elementos = list(
        FilteredElementCollector(doc)
        .OfCategory(categoria_bic)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    resultado = {}
    for e in elementos:
        p = (e.get_Parameter(bip_nivel)
             or e.get_Parameter(bip_nivel_alt))
        nivel_id = p.AsElementId() if p else None
        if nivel_id and nivel_id.IntegerValue > 0:
            nivel = doc.GetElement(nivel_id)
            nombre = nivel.Name if nivel else "Sin nivel"
        else:
            nombre = "Sin nivel"
        resultado[nombre] = resultado.get(nombre, 0) + 1
    return resultado


def detectar_elementos_duplicados(categoria_bic, tolerancia_m=0.001):
    """
    Detecta elementos de la misma categoria en la misma posicion
    (BBox centroide con tolerancia). Util para limpiar modelos.

    Args:
        categoria_bic: BuiltInCategory a verificar
        tolerancia_m: distancia maxima para considerar duplicado

    Returns:
        lista de grupos (cada grupo es lista de elementos duplicados)
    """
    tol = _metros_a_pies(tolerancia_m)
    elementos = list(
        FilteredElementCollector(doc)
        .OfCategory(categoria_bic)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    usados = set()
    grupos = []
    for i, a in enumerate(elementos):
        if i in usados:
            continue
        bb_a = a.BoundingBox[None]
        if bb_a is None:
            continue
        cx = (bb_a.Min.X + bb_a.Max.X) / 2.0
        cy = (bb_a.Min.Y + bb_a.Max.Y) / 2.0
        cz = (bb_a.Min.Z + bb_a.Max.Z) / 2.0
        grupo = [a]
        for j, b in enumerate(elementos):
            if j <= i or j in usados:
                continue
            bb_b = b.BoundingBox[None]
            if bb_b is None:
                continue
            bx = (bb_b.Min.X + bb_b.Max.X) / 2.0
            by = (bb_b.Min.Y + bb_b.Max.Y) / 2.0
            bz = (bb_b.Min.Z + bb_b.Max.Z) / 2.0
            dist = ((cx - bx) ** 2 + (cy - by) ** 2 +
                    (cz - bz) ** 2) ** 0.5
            if dist <= tol:
                grupo.append(b)
                usados.add(j)
        if len(grupo) > 1:
            usados.add(i)
            grupos.append(grupo)
    return grupos
