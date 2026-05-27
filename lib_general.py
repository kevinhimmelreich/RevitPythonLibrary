# -*- coding: utf-8 -*-
"""
lib_general.py
Biblioteca de funciones Revit/Dynamo — Utilidades Generales
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

from Autodesk.Revit.DB import (  # noqa: E402
    FilteredElementCollector, StorageType, ElementId,
    ElementTransformUtils, UnitUtils, UnitTypeId,
    BoundingBoxIntersectsFilter, BoundingBoxIsInsideFilter,
    BoundingBoxContainsPointFilter, Outline,
    LogicalOrFilter, LogicalAndFilter, ExclusionFilter,
    ElementOwnerViewFilter, ElementFilter,
    Group, AssemblyInstance,
    ReferencePlane, Grid, Line, XYZ
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


def unwrap(element):
    """
    Desenvuelve un elemento Dynamo al elemento Revit nativo subyacente.

    Args:
        element: elemento Dynamo o Revit

    Returns:
        elemento Revit nativo

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        return element.InternalElement
    except AttributeError:
        try:
            return UnwrapElement(element)  # noqa: F821
        except Exception:
            return element


def unwrap_lista(elementos):
    """
    Desenvuelve una lista de elementos Dynamo a elementos Revit nativos.

    Args:
        elementos: lista de elementos Dynamo o Revit

    Returns:
        lista de elementos Revit nativos

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return [unwrap(e) for e in elementos]


def id_a_int(element_id):
    """
    Convierte un ElementId a entero de forma compatible con Revit 2024+.

    Args:
        element_id: objeto ElementId de Revit

    Returns:
        entero con el valor del ElementId

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        return int(element_id.Value)       # Revit 2024+ (Int64)
    except AttributeError:
        return element_id.IntegerValue     # Revit <= 2023


def iniciar_transaccion(nombre="Transaccion"):
    """
    Inicia o reanuda la transaccion Dynamo activa.

    Args:
        nombre: nombre descriptivo de la transaccion

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    TransactionManager.Instance.EnsureInTransaction(doc)


def finalizar_transaccion():
    """
    Marca la tarea de transaccion Dynamo como completada.

    Args:
        (ninguno)

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    TransactionManager.Instance.TransactionTaskDone()


def obtener_valor_parametro(elemento, nombre_param):
    """
    Lee el valor de un parametro de instancia por nombre de forma segura.

    Args:
        elemento: elemento Revit
        nombre_param: nombre del parametro como string

    Returns:
        valor del parametro (str, int, float o ElementId) o None si no existe

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = elemento.LookupParameter(nombre_param)
    if param is None:
        return None
    t = param.StorageType
    if t == StorageType.String:
        return param.AsString()
    elif t == StorageType.Integer:
        return param.AsInteger()
    elif t == StorageType.Double:
        return param.AsDouble()
    elif t == StorageType.ElementId:
        return param.AsElementId()
    return None


def establecer_valor_parametro(elemento, nombre_param, valor):
    """
    Escribe el valor de un parametro de instancia por nombre.
    Requiere transaccion activa.

    Args:
        elemento: elemento Revit
        nombre_param: nombre del parametro como string
        valor: valor a asignar (debe ser compatible con el StorageType)

    Returns:
        True si se escribio correctamente, False en caso contrario

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = elemento.LookupParameter(nombre_param)
    if param is None or param.IsReadOnly:
        return False
    t = param.StorageType
    try:
        if t == StorageType.String:
            param.Set(str(valor))
        elif t == StorageType.Integer:
            param.Set(int(valor))
        elif t == StorageType.Double:
            param.Set(float(valor))
        elif t == StorageType.ElementId:
            param.Set(valor)
        return True
    except Exception:
        return False


def obtener_todos_parametros(elemento):
    """
    Retorna todos los parametros de un elemento como diccionario
    {nombre: valor}.

    Args:
        elemento: elemento Revit

    Returns:
        diccionario {nombre_parametro: valor}

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    resultado = {}
    for param in elemento.Parameters:
        nombre = param.Definition.Name
        try:
            t = param.StorageType
            if t == StorageType.String:
                resultado[nombre] = param.AsString()
            elif t == StorageType.Integer:
                resultado[nombre] = param.AsInteger()
            elif t == StorageType.Double:
                resultado[nombre] = param.AsDouble()
            elif t == StorageType.ElementId:
                resultado[nombre] = id_a_int(param.AsElementId())
        except Exception:
            resultado[nombre] = None
    return resultado


def pies_a_metros(valor_pies):
    """
    Convierte pies internos de Revit a metros.

    Args:
        valor_pies: valor numerico en pies internos de Revit

    Returns:
        valor en metros (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return UnitUtils.ConvertFromInternalUnits(valor_pies, UnitTypeId.Meters)


def metros_a_pies(valor_metros):
    """
    Convierte metros a pies internos de Revit.

    Args:
        valor_metros: valor numerico en metros

    Returns:
        valor en pies internos de Revit (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return UnitUtils.ConvertToInternalUnits(valor_metros, UnitTypeId.Meters)


def mm_a_pies(valor_mm):
    """
    Convierte milimetros a pies internos de Revit.

    Args:
        valor_mm: valor numerico en milimetros

    Returns:
        valor en pies internos de Revit (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return UnitUtils.ConvertToInternalUnits(
        valor_mm, UnitTypeId.Millimeters)


def pies_a_mm(valor_pies):
    """
    Convierte pies internos de Revit a milimetros.

    Args:
        valor_pies: valor numerico en pies internos de Revit

    Returns:
        valor en milimetros (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return UnitUtils.ConvertFromInternalUnits(
        valor_pies, UnitTypeId.Millimeters)


def m2_a_pies2(valor_m2):
    """
    Convierte metros cuadrados a pies cuadrados internos de Revit.

    Args:
        valor_m2: valor numerico en metros cuadrados

    Returns:
        valor en pies cuadrados internos de Revit (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return UnitUtils.ConvertToInternalUnits(valor_m2, UnitTypeId.SquareMeters)


def pies2_a_m2(valor_pies2):
    """
    Convierte pies cuadrados internos de Revit a metros cuadrados.

    Args:
        valor_pies2: valor numerico en pies cuadrados internos de Revit

    Returns:
        valor en metros cuadrados (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return UnitUtils.ConvertFromInternalUnits(
        valor_pies2, UnitTypeId.SquareMeters)


def copiar_elemento(elemento, vector_xyz):
    """
    Copia un elemento Revit desplazado por el vector indicado.

    Args:
        elemento: elemento Revit a copiar
        vector_xyz: XYZ con el vector de desplazamiento en pies internos

    Returns:
        elemento Revit copiado, o None si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    TransactionManager.Instance.EnsureInTransaction(doc)
    nuevos_ids = ElementTransformUtils.CopyElement(
        doc, elemento.Id, vector_xyz)
    TransactionManager.Instance.TransactionTaskDone()
    return doc.GetElement(list(nuevos_ids)[0]) if nuevos_ids else None


def mover_elemento(elemento, vector_xyz):
    """
    Mueve un elemento Revit por el vector indicado.

    Args:
        elemento: elemento Revit a mover
        vector_xyz: XYZ con el vector de desplazamiento en pies internos

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    TransactionManager.Instance.EnsureInTransaction(doc)
    ElementTransformUtils.MoveElement(doc, elemento.Id, vector_xyz)
    TransactionManager.Instance.TransactionTaskDone()


def eliminar_elemento(elemento):
    """
    Elimina un elemento del documento.

    Args:
        elemento: elemento Revit a eliminar

    Returns:
        ElementId del elemento eliminado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    eid = elemento.Id
    TransactionManager.Instance.EnsureInTransaction(doc)
    doc.Delete(eid)
    TransactionManager.Instance.TransactionTaskDone()
    return eid


def agrupar_por_parametro(elementos, nombre_param):
    """
    Agrupa una lista de elementos por el valor de un parametro de instancia.

    Args:
        elementos: lista de elementos Revit
        nombre_param: nombre del parametro como string

    Returns:
        dict {valor_parametro: [elementos]}

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    grupos = {}
    for e in elementos:
        valor = obtener_valor_parametro(e, nombre_param)
        clave = str(valor) if valor is not None else "Sin valor"
        grupos.setdefault(clave, []).append(e)
    return grupos


def obtener_ids_int(elementos):
    """
    Retorna una lista de enteros con los IDs de los elementos dados.

    Args:
        elementos: lista de elementos Revit

    Returns:
        lista de enteros con los IDs

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return [id_a_int(e.Id) for e in elementos]


def filtrar_por_valor_parametro(categoria_bic, nombre_param, valor):
    """
    Colecta todos los elementos de una categoria y los filtra por el
    valor de un parametro de instancia. La comparacion se hace como
    cadena de texto para compatibilidad con cualquier StorageType.

    Args:
        categoria_bic: BuiltInCategory de Revit
        nombre_param: nombre del parametro como string
        valor: valor a buscar

    Returns:
        lista de elementos cuyo parametro coincide con el valor dado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    elementos = list(
        FilteredElementCollector(doc)
        .OfCategory(categoria_bic)
        .WhereElementIsNotElementType()
        .ToElements()
    )
    valor_str = str(valor)
    return [
        e for e in elementos
        if str(obtener_valor_parametro(e, nombre_param)) == valor_str
    ]


def aplanar_lista(lista):
    """
    Aplana recursivamente una lista anidada de cualquier profundidad.

    Args:
        lista: lista potencialmente anidada (listas o tuplas internas)

    Returns:
        lista plana con todos los elementos en orden de aparicion

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    resultado = []
    for item in lista:
        if isinstance(item, (list, tuple)):
            resultado.extend(aplanar_lista(item))
        else:
            resultado.append(item)
    return resultado


def obtener_parametros_tipo(elemento):
    """
    Retorna los parametros de TIPO de un elemento como dict {nombre: valor}.
    Complementa a obtener_todos_parametros que devuelve los de instancia.

    Args:
        elemento: elemento Revit

    Returns:
        diccionario {nombre_parametro: valor} de los parametros del tipo,
        o dict vacio si el elemento no tiene tipo

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tipo = doc.GetElement(elemento.GetTypeId())
    if tipo is None:
        return {}
    resultado = {}
    for param in tipo.Parameters:
        nombre = param.Definition.Name
        try:
            t = param.StorageType
            if t == StorageType.String:
                resultado[nombre] = param.AsString()
            elif t == StorageType.Integer:
                resultado[nombre] = param.AsInteger()
            elif t == StorageType.Double:
                resultado[nombre] = param.AsDouble()
            elif t == StorageType.ElementId:
                resultado[nombre] = id_a_int(param.AsElementId())
        except Exception:
            resultado[nombre] = None
    return resultado


def filtrar_por_boundingbox(bbox_xyz, categoria_bic=None,
                            tolerancia_m=0.0):
    """
    Retorna elementos cuyo bounding box intersecta con el bbox dado.
    Usa BoundingBoxIntersectsFilter (filtro rapido nativo de Revit).

    Args:
        bbox_xyz: BoundingBoxXYZ de Revit que define la zona de busqueda
        categoria_bic: BuiltInCategory opcional para limitar la busqueda
        tolerancia_m: margen adicional en metros

    Returns:
        lista de elementos que intersectan el bbox

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tol = UnitUtils.ConvertToInternalUnits(tolerancia_m, UnitTypeId.Meters)
    outline = Outline(bbox_xyz.Min, bbox_xyz.Max)
    filtro = BoundingBoxIntersectsFilter(outline, tol)
    col = FilteredElementCollector(doc).WherePasses(filtro)
    if categoria_bic is not None:
        col = col.OfCategory(categoria_bic)
    return list(col.WhereElementIsNotElementType().ToElements())


def filtrar_dentro_de_bbox(bbox_xyz, categoria_bic=None,
                           tolerancia_m=0.0):
    """
    Retorna elementos cuyos bounding boxes estan completamente contenidos
    dentro del bbox dado. Usa BoundingBoxIsInsideFilter.

    Args:
        bbox_xyz: BoundingBoxXYZ de Revit que define la zona
        categoria_bic: BuiltInCategory opcional
        tolerancia_m: margen de tolerancia en metros

    Returns:
        lista de elementos cuyos bboxes estan dentro del bbox dado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tol = UnitUtils.ConvertToInternalUnits(tolerancia_m, UnitTypeId.Meters)
    outline = Outline(bbox_xyz.Min, bbox_xyz.Max)
    filtro = BoundingBoxIsInsideFilter(outline, tol)
    col = FilteredElementCollector(doc).WherePasses(filtro)
    if categoria_bic is not None:
        col = col.OfCategory(categoria_bic)
    return list(col.WhereElementIsNotElementType().ToElements())


def filtrar_contiene_punto(punto_xyz, categoria_bic=None,
                           tolerancia_m=0.0):
    """
    Retorna elementos cuyo bounding box contiene el punto dado.
    Usa BoundingBoxContainsPointFilter.

    Args:
        punto_xyz: XYZ del punto a buscar
        categoria_bic: BuiltInCategory opcional
        tolerancia_m: margen de tolerancia en metros

    Returns:
        lista de elementos cuyo bbox contiene el punto

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tol = UnitUtils.ConvertToInternalUnits(tolerancia_m, UnitTypeId.Meters)
    filtro = BoundingBoxContainsPointFilter(punto_xyz, tol)
    col = FilteredElementCollector(doc).WherePasses(filtro)
    if categoria_bic is not None:
        col = col.OfCategory(categoria_bic)
    return list(col.WhereElementIsNotElementType().ToElements())


def combinar_filtros_o(filtros):
    """
    Combina una lista de ElementFilter con logica OR.
    Util para buscar elementos de varias clases o condiciones a la vez.

    Args:
        filtros: lista de ElementFilter de Revit

    Returns:
        LogicalOrFilter combinado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    from System.Collections.Generic import List as NetList  # noqa: E402
    lista = NetList[ElementFilter](filtros)
    return LogicalOrFilter(lista)


def combinar_filtros_y(filtros):
    """
    Combina una lista de ElementFilter con logica AND.
    Permite encadenar condiciones que deben cumplirse simultaneamente.

    Args:
        filtros: lista de ElementFilter de Revit

    Returns:
        LogicalAndFilter combinado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    from System.Collections.Generic import List as NetList  # noqa: E402
    lista = NetList[ElementFilter](filtros)
    return LogicalAndFilter(lista)


def excluir_elementos(ids_excluir, categoria_bic=None):
    """
    Colecta elementos del documento excluyendo los ids dados.
    Usa ExclusionFilter.

    Args:
        ids_excluir: lista de ElementId a excluir
        categoria_bic: BuiltInCategory opcional para limitar la busqueda

    Returns:
        lista de elementos que NO estan en ids_excluir

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    from System.Collections.Generic import List as NetList  # noqa: E402
    lista = NetList[ElementId](ids_excluir)
    filtro = ExclusionFilter(lista)
    col = FilteredElementCollector(doc).WherePasses(filtro)
    if categoria_bic is not None:
        col = col.OfCategory(categoria_bic)
    return list(col.WhereElementIsNotElementType().ToElements())


def obtener_anotaciones_en_vista(vista, categoria_bic=None):
    """
    Retorna los elementos especificos de vista (anotaciones, etiquetas,
    lineas de detalle…) de la vista indicada.
    Usa ElementOwnerViewFilter que solo devuelve elementos propios de vista.

    Args:
        vista: View de Revit
        categoria_bic: BuiltInCategory opcional

    Returns:
        lista de elementos de anotacion de la vista

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    filtro = ElementOwnerViewFilter(vista.Id)
    col = FilteredElementCollector(doc).WherePasses(filtro)
    if categoria_bic is not None:
        col = col.OfCategory(categoria_bic)
    return list(col.ToElements())


def obtener_elementos_visibles_en_vista(vista, categoria_bic=None):
    """
    Retorna los elementos de modelo visibles en la vista usando el
    colector de vista (FilteredElementCollector con Id de vista).

    Args:
        vista: View de Revit
        categoria_bic: BuiltInCategory opcional

    Returns:
        lista de elementos visibles en la vista

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    col = FilteredElementCollector(doc, vista.Id)
    if categoria_bic is not None:
        col = col.OfCategory(categoria_bic)
    return list(col.WhereElementIsNotElementType().ToElements())


# ── Grupos y ensamblajes ──────────────────────────────────────────────────────

def crear_grupo(elementos):
    """
    Crea un GroupType a partir de una lista de elementos y coloca
    una instancia Group en el documento.

    Args:
        elementos: lista de elementos Revit a agrupar

    Returns:
        Group (instancia) creado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    from System.Collections.Generic import List as NetList  # noqa: E402
    ids = NetList[ElementId]([e.Id for e in elementos])
    TransactionManager.Instance.EnsureInTransaction(doc)
    grupo = doc.Create.NewGroup(ids)
    TransactionManager.Instance.TransactionTaskDone()
    return grupo


def desagrupar(grupo):
    """
    Desagrupa un Group y devuelve los ids de los elementos liberados.

    Args:
        grupo: Group de Revit

    Returns:
        lista de ElementId de los elementos desagrupados

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    TransactionManager.Instance.EnsureInTransaction(doc)
    ids = list(grupo.UngroupMembers())
    TransactionManager.Instance.TransactionTaskDone()
    return ids


def obtener_miembros_grupo(grupo):
    """
    Retorna los elementos miembro de un Group sin desagruparlo.

    Args:
        grupo: Group de Revit

    Returns:
        lista de elementos miembro

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return [doc.GetElement(i) for i in grupo.GetMemberIds()]


def obtener_grupos():
    """
    Retorna todos los Groups (instancias) del documento.

    Args:
        (ninguno)

    Returns:
        lista de Group

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc).OfClass(Group).ToElements()
    )


def crear_ensamblaje(elementos, nombre=None):
    """
    Crea un AssemblyInstance a partir de una lista de elementos.

    Args:
        elementos: lista de elementos Revit a ensamblar
        nombre: nombre del ensamblaje (opcional)

    Returns:
        AssemblyInstance creado, o None si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    from System.Collections.Generic import List as NetList  # noqa: E402
    ids = NetList[ElementId]([e.Id for e in elementos])
    TransactionManager.Instance.EnsureInTransaction(doc)
    try:
        cat_id = elementos[0].Category.Id
        ensamblaje = AssemblyInstance.Create(doc, ids, cat_id)
        if nombre:
            if AssemblyInstance.IsAssemblyNameUnique(doc, nombre):
                ensamblaje.AssemblyTypeName = nombre
        TransactionManager.Instance.TransactionTaskDone()
        return ensamblaje
    except Exception:
        TransactionManager.Instance.TransactionTaskDone()
        return None


def obtener_miembros_ensamblaje(ensamblaje):
    """
    Retorna los elementos miembro de un AssemblyInstance.

    Args:
        ensamblaje: AssemblyInstance de Revit

    Returns:
        lista de elementos miembro

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return [doc.GetElement(i) for i in ensamblaje.GetMemberIds()]


# ── Planos de referencia y ejes ───────────────────────────────────────────────

def crear_plano_referencia(punto1_xyz, punto2_xyz, nombre=None):
    """
    Crea un ReferencePlane entre dos puntos en la vista activa.

    Args:
        punto1_xyz: XYZ primer punto de definicion
        punto2_xyz: XYZ segundo punto de definicion
        nombre: nombre del plano de referencia (opcional)

    Returns:
        ReferencePlane creado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    TransactionManager.Instance.EnsureInTransaction(doc)
    plano = doc.Create.NewReferencePlane(
        punto1_xyz, punto2_xyz,
        XYZ(0, 0, 1), doc.ActiveView)
    if nombre:
        try:
            plano.Name = nombre
        except Exception:
            pass
    TransactionManager.Instance.TransactionTaskDone()
    return plano


def crear_eje(punto1_xyz, punto2_xyz, nombre=None):
    """
    Crea un Grid (eje de proyecto) entre dos puntos.

    Args:
        punto1_xyz: XYZ punto inicial del eje
        punto2_xyz: XYZ punto final del eje
        nombre: nombre del eje (opcional)

    Returns:
        Grid creado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    linea = Line.CreateBound(punto1_xyz, punto2_xyz)
    TransactionManager.Instance.EnsureInTransaction(doc)
    eje = Grid.Create(doc, linea)
    if nombre:
        try:
            eje.Name = nombre
        except Exception:
            pass
    TransactionManager.Instance.TransactionTaskDone()
    return eje


def obtener_ejes():
    """
    Retorna todos los Grid del documento.

    Args:
        (ninguno)

    Returns:
        lista de Grid

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc).OfClass(Grid).ToElements()
    )


def obtener_planos_referencia():
    """
    Retorna todos los ReferencePlane del documento.

    Args:
        (ninguno)

    Returns:
        lista de ReferencePlane

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return list(
        FilteredElementCollector(doc)
        .OfClass(ReferencePlane).ToElements()
    )
