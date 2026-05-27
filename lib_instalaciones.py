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

from Autodesk.Revit.DB import (  # noqa: E402
    FilteredElementCollector, BuiltInCategory, BuiltInParameter,
    UnitUtils, UnitTypeId, Line, XYZ, ElementTransformUtils,
    InsulationLiningBase, ConnectorSet
)
from Autodesk.Revit.DB import Mechanical, Plumbing  # noqa: E402
from Autodesk.Revit.DB.Mechanical import MechanicalSystem  # noqa: E402
from Autodesk.Revit.DB.Plumbing import (  # noqa: E402
    Pipe, PipingSystem, PlumbingUtils, PipeSettings
)
from Autodesk.Revit.DB.Electrical import CableTray  # noqa: E402
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

def _pies_a_metros(v):
    return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.Meters)


def _pies_a_mm(v):
    return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.Millimeters)


def _mm_a_pies(v):
    return UnitUtils.ConvertToInternalUnits(v, UnitTypeId.Millimeters)


def _iniciar():
    TransactionManager.Instance.EnsureInTransaction(doc)


def _finalizar():
    TransactionManager.Instance.TransactionTaskDone()


def _conn_manager(elemento):
    """Retorna el ConnectorManager del elemento MEP."""
    try:
        return elemento.ConnectorManager
    except AttributeError:
        return elemento.MEPModel.ConnectorManager


def _connectors(elemento):
    """Retorna la colección Connectors del elemento MEP."""
    return _conn_manager(elemento).Connectors


# ── Conectores ───────────────────────────────────────────────────────────────

def conectores_libres(elemento):
    """
    Retorna los conectores sin usar (extremos abiertos) de un elemento MEP.

    Args:
        elemento: elemento MEP de Revit

    Returns:
        lista de Connector sin conexión

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        return list(_conn_manager(elemento).UnusedConnectors)
    except Exception:
        return []


def elementos_conectados_a(elemento):
    """
    Retorna los elementos directamente conectados a un elemento MEP
    (vecinos de un salto en la red).

    Args:
        elemento: elemento MEP de Revit

    Returns:
        lista de Element conectados

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    vecinos = []
    try:
        for conn in _connectors(elemento):
            if not conn.IsConnected:
                continue
            for ref in conn.AllRefs:
                if ref.Owner.Id != elemento.Id:
                    vecinos.append(ref.Owner)
    except Exception:
        pass
    return vecinos


def conectores_mas_cercanos(elem1, elem2):
    """
    Encuentra el par de conectores más próximos entre dos elementos MEP.

    Args:
        elem1: primer elemento MEP
        elem2: segundo elemento MEP

    Returns:
        lista [conector_de_elem1, conector_de_elem2], o None si no hay

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    mejor = None
    dist_min = float("inf")
    try:
        for c1 in _connectors(elem1):
            for c2 in _connectors(elem2):
                d = c1.Origin.DistanceTo(c2.Origin)
                if d < dist_min:
                    dist_min = d
                    mejor = [c1, c2]
    except Exception:
        pass
    return mejor


def recorrer_sistema_mep(elemento_inicio):
    """
    Recorre recursivamente todos los elementos conectados en la red MEP
    partiendo de un elemento, usando los conectores AllRefs.

    Args:
        elemento_inicio: elemento MEP de Revit que actúa como raíz

    Returns:
        lista de Element que forman la red (sin incluir el de inicio)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    visitados = {elemento_inicio.Id: True}
    resultado = []

    def _visitar(elem):
        try:
            conns = elem.ConnectorManager.Connectors
        except AttributeError:
            try:
                conns = elem.MEPModel.ConnectorManager.Connectors
            except Exception:
                return
        for conn in conns:
            for ref in conn.AllRefs:
                oid = ref.Owner.Id
                if oid in visitados:
                    continue
                try:
                    if isinstance(ref.Owner, MechanicalSystem):
                        continue
                except Exception:
                    pass
                vecino = doc.GetElement(oid)
                if vecino is None:
                    continue
                visitados[oid] = True
                resultado.append(vecino)
                _visitar(vecino)

    _visitar(elemento_inicio)
    return resultado


def verificar_extremos_abiertos(elementos_mep):
    """
    Identifica los elementos MEP que tienen conectores sin conectar.

    Args:
        elementos_mep: lista de elementos MEP de Revit

    Returns:
        lista de elementos con al menos un conector libre

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return [e for e in elementos_mep if conectores_libres(e)]


# ── Verificaciones de separación ─────────────────────────────────────────────

def verificar_separacion_conductos(ducto0, ducto1):
    """
    Verifica si la separación entre dos conductos es suficiente.
    El mínimo exigido es 2 × el ancho mayor de los dos conductos.

    Args:
        ducto0: primer elemento Duct de Revit
        ducto1: segundo elemento Duct de Revit

    Returns:
        dict con claves:
          "ok" (bool), "separacion_mm" (float), "minima_mm" (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        pw0 = ducto0.get_Parameter(BuiltInParameter.RBS_CURVE_WIDTH_PARAM)
        pw1 = ducto1.get_Parameter(BuiltInParameter.RBS_CURVE_WIDTH_PARAM)
        w0 = _pies_a_mm(pw0.AsDouble()) if pw0 else 0.0
        w1 = _pies_a_mm(pw1.AsDouble()) if pw1 else 0.0
        c0 = ducto0.Location.Curve.Evaluate(0.5, True)
        c1 = ducto1.Location.Curve.Evaluate(0.5, True)
        dist_mm = _pies_a_mm(c0.DistanceTo(c1))
        sep_mm = dist_mm - w0 / 2.0 - w1 / 2.0
        min_mm = max(2.0 * w0, 2.0 * w1)
        return {
            "ok": sep_mm >= min_mm,
            "separacion_mm": round(sep_mm, 1),
            "minima_mm": round(min_mm, 1),
        }
    except Exception:
        return {"ok": None, "separacion_mm": None, "minima_mm": None}


# ── Propiedades calculadas ────────────────────────────────────────────────────

def obtener_longitud_conducto(conducto):
    """
    Retorna la longitud de un conducto en metros.

    Args:
        conducto: elemento Duct de Revit

    Returns:
        longitud en metros (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    p = conducto.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH)
    return _pies_a_metros(p.AsDouble()) if p else 0.0


def obtener_longitud_tuberia(tuberia):
    """
    Retorna la longitud de una tubería en metros.

    Args:
        tuberia: elemento Pipe de Revit

    Returns:
        longitud en metros (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    p = tuberia.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH)
    return _pies_a_metros(p.AsDouble()) if p else 0.0


def obtener_longitud_bandeja(bandeja):
    """
    Retorna la longitud de una bandeja de cable en metros.

    Args:
        bandeja: elemento CableTray de Revit

    Returns:
        longitud en metros (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    p = bandeja.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH)
    return _pies_a_metros(p.AsDouble()) if p else 0.0


def obtener_diametro_exterior_tuberia(tuberia):
    """
    Retorna el diámetro exterior de una tubería en milímetros.

    Args:
        tuberia: elemento Pipe de Revit

    Returns:
        diámetro exterior en mm (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    p = tuberia.get_Parameter(BuiltInParameter.RBS_PIPE_OUTER_DIAMETER)
    return _pies_a_mm(p.AsDouble()) if p else 0.0


def obtener_diametro_interior_tuberia(tuberia):
    """
    Retorna el diámetro interior de una tubería en milímetros.

    Args:
        tuberia: elemento Pipe de Revit

    Returns:
        diámetro interior en mm (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    p = tuberia.get_Parameter(BuiltInParameter.RBS_PIPE_INNER_DIAM_PARAM)
    return _pies_a_mm(p.AsDouble()) if p else 0.0


def obtener_sistema_tuberia(tuberia):
    """
    Retorna el nombre del sistema de una tubería.

    Args:
        tuberia: elemento Pipe de Revit

    Returns:
        nombre del sistema como string, o None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    p = tuberia.get_Parameter(
        BuiltInParameter.RBS_PIPING_SYSTEM_TYPE_PARAM)
    if p:
        s = doc.GetElement(p.AsElementId())
        return s.Name if s else None
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
    p = conducto.get_Parameter(
        BuiltInParameter.RBS_DUCT_SYSTEM_TYPE_PARAM)
    if p:
        s = doc.GetElement(p.AsElementId())
        return s.Name if s else None
    return None


def area_seccion_conducto(conducto):
    """
    Calcula el área de sección transversal de un conducto en m².
    Funciona tanto para conductos circulares como rectangulares.

    Args:
        conducto: elemento Duct de Revit

    Returns:
        área en m² (float), o 0.0 si no disponible

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        pd = conducto.get_Parameter(
            BuiltInParameter.RBS_CURVE_DIAMETER_PARAM)
        if pd:
            r = _pies_a_metros(pd.AsDouble()) / 2.0
            return math.pi * r * r
        pw = conducto.get_Parameter(BuiltInParameter.RBS_CURVE_WIDTH_PARAM)
        ph = conducto.get_Parameter(
            BuiltInParameter.RBS_CURVE_HEIGHT_PARAM)
        if pw and ph:
            return (_pies_a_metros(pw.AsDouble())
                    * _pies_a_metros(ph.AsDouble()))
    except Exception:
        pass
    return 0.0


def velocidad_conducto(conducto):
    """
    Calcula la velocidad del flujo en un conducto en m/s.
    Requiere que el conducto tenga caudal asignado en el sistema.

    Args:
        conducto: elemento Duct de Revit

    Returns:
        velocidad en m/s (float), o None si no hay datos

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        pf = conducto.get_Parameter(BuiltInParameter.RBS_DUCT_FLOW_PARAM)
        if not pf:
            return None
        caudal = UnitUtils.ConvertFromInternalUnits(
            pf.AsDouble(), UnitTypeId.CubicMetersPerSecond)
        area = area_seccion_conducto(conducto)
        if area <= 0:
            return None
        return round(caudal / area, 3)
    except Exception:
        return None


def velocidad_tuberia(tuberia):
    """
    Calcula la velocidad del flujo en una tubería en m/s.

    Args:
        tuberia: elemento Pipe de Revit

    Returns:
        velocidad en m/s (float), o None si no hay datos

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        pf = tuberia.get_Parameter(BuiltInParameter.RBS_PIPE_FLOW_PARAM)
        pi = tuberia.get_Parameter(
            BuiltInParameter.RBS_PIPE_INNER_DIAM_PARAM)
        if not pf or not pi:
            return None
        caudal = UnitUtils.ConvertFromInternalUnits(
            pf.AsDouble(), UnitTypeId.CubicMetersPerSecond)
        r = _pies_a_metros(pi.AsDouble()) / 2.0
        area = math.pi * r * r
        if area <= 0:
            return None
        return round(caudal / area, 3)
    except Exception:
        return None


# ── Agrupación y estadísticas ────────────────────────────────────────────────

def agrupar_tuberias_por_sistema():
    """
    Agrupa todas las tuberías del documento por nombre de sistema.

    Args:
        (ninguno)

    Returns:
        diccionario {nombre_sistema: [tuberias]}

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    resultado = {}
    for t in (FilteredElementCollector(doc)
              .OfCategory(BuiltInCategory.OST_PipeCurves)
              .WhereElementIsNotElementType()
              .ToElements()):
        s = obtener_sistema_tuberia(t) or "Sin Sistema"
        resultado.setdefault(s, []).append(t)
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
    for c in (FilteredElementCollector(doc)
              .OfCategory(BuiltInCategory.OST_DuctCurves)
              .WhereElementIsNotElementType()
              .ToElements()):
        s = obtener_tipo_sistema_conducto(c) or "Sin Sistema"
        resultado.setdefault(s, []).append(c)
    return resultado


def obtener_longitud_total_conductos():
    """
    Retorna la longitud total de todos los conductos del documento en metros.

    Returns:
        longitud total en metros (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return sum(
        obtener_longitud_conducto(c)
        for c in (FilteredElementCollector(doc)
                  .OfCategory(BuiltInCategory.OST_DuctCurves)
                  .WhereElementIsNotElementType()
                  .ToElements())
    )


def obtener_longitud_total_tuberias():
    """
    Retorna la longitud total de todas las tuberías del documento en metros.

    Returns:
        longitud total en metros (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return sum(
        obtener_longitud_tuberia(t)
        for t in (FilteredElementCollector(doc)
                  .OfCategory(BuiltInCategory.OST_PipeCurves)
                  .WhereElementIsNotElementType()
                  .ToElements())
    )


def obtener_longitud_total_bandejas():
    """
    Retorna la longitud total de todas las bandejas de cable en metros.

    Returns:
        longitud total en metros (float)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return sum(
        obtener_longitud_bandeja(b)
        for b in (FilteredElementCollector(doc)
                  .OfCategory(BuiltInCategory.OST_CableTray)
                  .WhereElementIsNotElementType()
                  .ToElements())
    )


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
        e for e in (FilteredElementCollector(doc)
                    .OfCategory(BuiltInCategory.OST_MEPSpaces)
                    .WhereElementIsNotElementType()
                    .ToElements())
        if e.Level and e.Level.Id == nivel.Id
    ]


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


def categorizar_elementos_tuberia(elementos):
    """
    Clasifica una lista de elementos MEP mixtos en grupos por categoría.

    Args:
        elementos: lista de elementos Revit mezclados (tuberías,
                   accesorios, dispositivos, rociadores)

    Returns:
        dict con claves "tuberias", "accesorios", "dispositivos", "otros"

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    resultado = {
        "tuberias": [], "accesorios": [],
        "dispositivos": [], "otros": [],
    }
    _mapa = {
        "Pipes": "tuberias", "Tubos": "tuberias",
        "Pipe Fittings": "accesorios",
        "Accesorios de tuberías": "accesorios",
        "Pipe Accessories": "dispositivos",
        "Sprinklers": "dispositivos",
    }
    for e in elementos:
        try:
            clave = _mapa.get(e.Category.Name, "otros")
            resultado[clave].append(e)
        except Exception:
            resultado["otros"].append(e)
    return resultado


# ── Sistemas MEP ─────────────────────────────────────────────────────────────

def numero_redes_fisicas(sistema):
    """
    Retorna el número de redes físicas (sub-redes desconectadas)
    dentro de un sistema MEP.

    Args:
        sistema: MechanicalSystem o PipingSystem de Revit

    Returns:
        número de redes (int)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        return sistema.GetPhysicalNetworksNumber()
    except Exception:
        return 0


def dividir_sistema_mep(sistema):
    """
    Divide un sistema MEP con varias redes físicas en sistemas separados.

    Args:
        sistema: MechanicalSystem o PipingSystem con varias sub-redes

    Returns:
        lista de sistemas resultantes, o lista vacía si no se puede dividir

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        if numero_redes_fisicas(sistema) <= 1:
            return []
        _iniciar()
        ids = sistema.DivideSystem(doc)
        resultado = [doc.GetElement(i) for i in ids]
        _finalizar()
        return resultado
    except Exception:
        return []


def crear_sistema_mep(tipo_sistema, nombre=None):
    """
    Crea un nuevo sistema de fontanería o mecánico.

    Args:
        tipo_sistema: PipeSystemType o MechanicalSystemType de Revit
        nombre: nombre del sistema (opcional)

    Returns:
        sistema creado (PipingSystem o MechanicalSystem), o None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        _iniciar()
        if isinstance(tipo_sistema, Plumbing.PipeSystemType):
            s = (PipingSystem.Create(doc, tipo_sistema.Id, nombre)
                 if nombre else PipingSystem.Create(doc, tipo_sistema.Id))
        else:
            s = (MechanicalSystem.Create(doc, tipo_sistema.Id, nombre)
                 if nombre
                 else MechanicalSystem.Create(doc, tipo_sistema.Id))
        _finalizar()
        return s
    except Exception:
        return None


def agregar_elementos_a_sistema(sistema, terminales):
    """
    Agrega terminales o accesorios a un sistema MEP existente.
    Conecta el primer conector compatible de cada terminal al sistema.

    Args:
        sistema: MechanicalSystem o PipingSystem de Revit
        terminales: lista de FamilyInstance a agregar

    Returns:
        lista de elementos agregados con éxito

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not isinstance(terminales, list):
        terminales = [terminales]
    systype = sistema.SystemType
    resultado = []
    _iniciar()
    for terminal in terminales:
        try:
            for conn in terminal.MEPModel.ConnectorManager.Connectors:
                try:
                    compatible = False
                    try:
                        compatible = (conn.DuctSystemType == systype)
                    except Exception:
                        pass
                    if not compatible:
                        try:
                            compatible = (conn.PipeSystemType == systype)
                        except Exception:
                            pass
                    if compatible:
                        cset = ConnectorSet()
                        cset.Insert(conn)
                        sistema.Add(cset)
                        resultado.append(terminal)
                        break
                except Exception:
                    pass
        except Exception:
            pass
    _finalizar()
    return resultado


# ── Creación de elementos ────────────────────────────────────────────────────

def crear_tuberias_desde_lineas(lineas, tipo_id, sistema_id,
                                nivel, diametro_mm):
    """
    Crea tuberías desde una lista de líneas Revit.

    Args:
        lineas: lista de Line (con GetEndPoint(0/1))
        tipo_id: ElementId del tipo de tubería
        sistema_id: ElementId del tipo de sistema de fontanería
        nivel: objeto Level de Revit
        diametro_mm: diámetro nominal en mm (número o lista)

    Returns:
        lista de Pipe creadas (None donde falla)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not isinstance(diametro_mm, list):
        diametro_mm = [diametro_mm]
    dl = len(diametro_mm)
    resultado = []
    _iniciar()
    for i, linea in enumerate(lineas):
        try:
            p1 = linea.GetEndPoint(0)
            p2 = linea.GetEndPoint(1)
            pipe = Pipe.Create(doc, sistema_id, tipo_id, nivel.Id, p1, p2)
            param = pipe.get_Parameter(
                BuiltInParameter.RBS_PIPE_DIAMETER_PARAM)
            param.SetValueString(str(diametro_mm[i % dl]))
            resultado.append(pipe)
        except Exception:
            resultado.append(None)
    _finalizar()
    return resultado


def crear_bandejas_desde_lineas(lineas, tipo_id, niveles,
                                ancho_mm=300, alto_mm=100):
    """
    Crea bandejas de cable desde una lista de líneas.

    Args:
        lineas: lista de Line (con GetEndPoint(0/1))
        tipo_id: ElementId del tipo de bandeja
        niveles: Level o lista de Level de Revit
        ancho_mm: ancho en mm (número o lista, por defecto 300)
        alto_mm: alto en mm (número o lista, por defecto 100)

    Returns:
        lista de CableTray creadas (None donde falla)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not isinstance(niveles, list):
        niveles = [niveles]
    if not isinstance(ancho_mm, list):
        ancho_mm = [ancho_mm]
    if not isinstance(alto_mm, list):
        alto_mm = [alto_mm]
    nl, al, hl = len(niveles), len(ancho_mm), len(alto_mm)
    resultado = []
    _iniciar()
    for i, linea in enumerate(lineas):
        try:
            p1 = linea.GetEndPoint(0)
            p2 = linea.GetEndPoint(1)
            tray = CableTray.Create(
                doc, tipo_id, p1, p2, niveles[i % nl].Id)
            pw = tray.get_Parameter(
                BuiltInParameter.RBS_CABLETRAY_WIDTH_PARAM)
            ph = tray.get_Parameter(
                BuiltInParameter.RBS_CABLETRAY_HEIGHT_PARAM)
            if pw:
                pw.SetValueString(str(ancho_mm[i % al]))
            if ph:
                ph.SetValueString(str(alto_mm[i % hl]))
            resultado.append(tray)
        except Exception:
            resultado.append(None)
    _finalizar()
    return resultado


def crear_bandeja_cable(tipo_bandeja_id, punto_inicio_xyz,
                        punto_fin_xyz, nivel,
                        ancho_mm=300.0, alto_mm=100.0):
    """
    Crea una bandeja de cables entre dos puntos XYZ.

    Args:
        tipo_bandeja_id: ElementId del tipo de bandeja
        punto_inicio_xyz: XYZ del punto de inicio
        punto_fin_xyz: XYZ del punto de fin
        nivel: objeto Level de Revit
        ancho_mm: ancho en mm (por defecto 300)
        alto_mm: alto en mm (por defecto 100)

    Returns:
        CableTray creada

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar()
    tray = CableTray.Create(
        doc, tipo_bandeja_id, punto_inicio_xyz, punto_fin_xyz, nivel.Id)
    pw = tray.get_Parameter(BuiltInParameter.RBS_CABLETRAY_WIDTH_PARAM)
    ph = tray.get_Parameter(BuiltInParameter.RBS_CABLETRAY_HEIGHT_PARAM)
    if pw:
        pw.SetValueString(str(ancho_mm))
    if ph:
        ph.SetValueString(str(alto_mm))
    _finalizar()
    return tray


def tuberia_entre_conectores(conector1, conector2, tipo_id, nivel):
    """
    Crea una tubería conectando dos conectores MEP existentes.

    Args:
        conector1: Connector de inicio
        conector2: Connector de fin
        tipo_id: ElementId del tipo de tubería
        nivel: objeto Level de Revit

    Returns:
        Pipe creada, o None si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        _iniciar()
        pipe = Pipe.Create(doc, tipo_id, nivel.Id, conector1, conector2)
        _finalizar()
        return pipe
    except Exception:
        return None


def tuberia_desde_conector(conector, punto_xyz, tipo_id, nivel):
    """
    Crea una tubería desde un conector existente hasta un punto XYZ.

    Args:
        conector: Connector de inicio
        punto_xyz: XYZ del punto de fin
        tipo_id: ElementId del tipo de tubería
        nivel: objeto Level de Revit

    Returns:
        Pipe creada, o None si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        _iniciar()
        pipe = Pipe.Create(doc, tipo_id, nivel.Id, conector, punto_xyz)
        _finalizar()
        return pipe
    except Exception:
        return None


# ── Accesorios de empalme ────────────────────────────────────────────────────

def crear_te_mep(curva_principal, curva_ramal):
    """
    Inserta una te (NewTeeFitting) entre una curva MEP principal y un
    ramal. Divide la curva principal en el punto de derivación, copia
    el tramo restante y crea el fitting.

    Args:
        curva_principal: Duct o Pipe principal de Revit
        curva_ramal: Duct o Pipe de ramal de Revit

    Returns:
        FamilyInstance de la te, o None si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        _iniciar()
        try:
            ancho = curva_ramal.Diameter
        except AttributeError:
            ancho = curva_ramal.Width

        linea1 = curva_principal.Location.Curve
        ini = linea1.GetEndPoint(0)
        fin = linea1.GetEndPoint(1)
        ramal_ini = curva_ramal.Location.Curve.GetEndPoint(0)
        mid = linea1.Project(ramal_ini).XYZPoint
        lon = linea1.Length
        len1 = ini.DistanceTo(mid)
        mid_a = linea1.Evaluate((len1 - ancho / 2.0) / lon, True)
        mid_b = linea1.Evaluate((len1 + ancho / 2.0) / lon, True)

        if ini.DistanceTo(mid) < fin.DistanceTo(mid):
            ini, fin = fin, ini
            mid_a, mid_b = mid_b, mid_a

        end_conn = None
        for c in curva_principal.ConnectorManager.Connectors:
            if c.Origin.IsAlmostEqualTo(fin):
                end_conn = c
                break

        otro_fitting = None
        if end_conn:
            for ref in end_conn.AllRefs:
                if ref.IsConnectedTo(end_conn):
                    if ref.Owner.GetType().__name__ == "FamilyInstance":
                        otro_fitting = ref.Owner
                    end_conn.DisconnectFrom(ref)

        curva_principal.Location.Curve = Line.CreateBound(ini, mid_a)
        doc.Regenerate()

        offset = XYZ(mid_a.X - fin.X, mid_a.Y - fin.Y, mid_a.Z - fin.Z)
        nuevos = ElementTransformUtils.CopyElement(
            doc, curva_principal.Id, offset)
        curva3 = doc.GetElement(nuevos[0])
        doc.Regenerate()
        curva3.Location.Curve = Line.CreateBound(fin, mid_b)
        doc.Regenerate()

        c1_best = c2_best = c3_best = None
        d1 = d2 = float("inf")
        for a in curva_principal.ConnectorManager.Connectors:
            for b in curva_ramal.ConnectorManager.Connectors:
                d = a.Origin.DistanceTo(b.Origin)
                if d < d1:
                    d1 = d
                    c1_best, c2_best = a, b
            for e in curva3.ConnectorManager.Connectors:
                d = a.Origin.DistanceTo(e.Origin)
                if d < d2:
                    d2 = d
                    c3_best = e

        te = doc.Create.NewTeeFitting(c1_best, c2_best, c3_best)

        if otro_fitting:
            for c3 in curva3.ConnectorManager.Connectors:
                for cf in (otro_fitting.MEPModel
                           .ConnectorManager.Connectors):
                    if c3.Origin.IsAlmostEqualTo(cf.Origin):
                        c3.ConnectTo(cf)
                        break

        _finalizar()
        return te
    except Exception:
        return None


def crear_tap_mep(curva_principal, curva_ramal):
    """
    Inserta un takeoff fitting (tap) desde la curva principal hacia
    el ramal. Usa el conector del ramal más próximo a la línea principal.

    Args:
        curva_principal: Duct o Pipe principal de Revit
        curva_ramal: Duct o Pipe de ramal de Revit

    Returns:
        FamilyInstance del tap, o None si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        _iniciar()
        linea = curva_principal.Location.Curve
        mejor = None
        dist_min = float("inf")
        for c in _connectors(curva_ramal):
            d = linea.Project(c.Origin).Distance
            if d < dist_min:
                dist_min = d
                mejor = c
        if mejor is None:
            return None
        tap = doc.Create.NewTakeoffFitting(mejor, curva_principal)
        _finalizar()
        return tap
    except Exception:
        return None


# ── Aislamiento ──────────────────────────────────────────────────────────────

def agregar_aislamiento(elemento, tipo_aislamiento_id, espesor_mm):
    """
    Agrega aislamiento a una tubería o conducto.

    Args:
        elemento: Pipe o Duct de Revit
        tipo_aislamiento_id: ElementId del tipo de aislamiento
        espesor_mm: espesor del aislamiento en mm

    Returns:
        elemento de aislamiento creado, o None si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        espesor_ft = _mm_a_pies(espesor_mm)
        _iniciar()
        try:
            ins = Plumbing.PipeInsulation.Create(
                doc, elemento.Id, tipo_aislamiento_id, espesor_ft)
        except Exception:
            ins = Mechanical.DuctInsulation.Create(
                doc, elemento.Id, tipo_aislamiento_id, espesor_ft)
        _finalizar()
        return ins
    except Exception:
        return None


def agregar_aislamiento_multiples(
        elementos, tipo_aislamiento_id, espesores_mm):
    """
    Agrega aislamiento a múltiples tuberías o conductos en un lote.

    Args:
        elementos: lista de Pipe o Duct de Revit
        tipo_aislamiento_id: ElementId del tipo de aislamiento
        espesores_mm: espesor en mm (número o lista)

    Returns:
        dict {"ok": [con éxito], "error": [fallidos]}

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not isinstance(espesores_mm, list):
        espesores_mm = [espesores_mm]
    el = len(espesores_mm)
    ok, error = [], []
    _iniciar()
    for i, elem in enumerate(elementos):
        try:
            ft = _mm_a_pies(espesores_mm[i % el])
            try:
                Plumbing.PipeInsulation.Create(
                    doc, elem.Id, tipo_aislamiento_id, ft)
            except Exception:
                Mechanical.DuctInsulation.Create(
                    doc, elem.Id, tipo_aislamiento_id, ft)
            ok.append(elem)
        except Exception:
            error.append(elem)
    _finalizar()
    return {"ok": ok, "error": error}


def obtener_aislamiento(elemento):
    """
    Retorna el elemento de aislamiento de una tubería o conducto.

    Args:
        elemento: Pipe o Duct de Revit

    Returns:
        InsulationLiningBase, o None si no tiene aislamiento

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        ids = InsulationLiningBase.GetInsulationIds(doc, elemento.Id)
        if ids and ids.Count > 0:
            return doc.GetElement(ids[0])
    except Exception:
        pass
    return None


def tapon_en_extremos_abiertos(tuberia, tipo_tapon_id):
    """
    Coloca tapones en todos los extremos abiertos de una tubería.

    Args:
        tuberia: elemento Pipe de Revit
        tipo_tapon_id: ElementId del tipo de tapón

    Returns:
        la misma tubería, o None si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        _iniciar()
        PlumbingUtils.PlaceCapOnOpenEnds(doc, tuberia.Id, tipo_tapon_id)
        _finalizar()
        return tuberia
    except Exception:
        return None


# ── Configuración ────────────────────────────────────────────────────────────

def configurar_pendientes_tuberia(lista_pendientes):
    """
    Establece los valores de pendiente disponibles para tuberías en
    la configuración del documento.

    Args:
        lista_pendientes: lista de valores de pendiente (float, en %)

    Returns:
        lista de pendientes aplicada, o None si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        from System.Collections.Generic import List as NetList
        ajustes = PipeSettings.GetPipeSettings(doc)
        pendientes = NetList[float]()
        for v in lista_pendientes:
            pendientes.Add(float(v))
        _iniciar()
        ajustes.SetPipeSlopes(pendientes)
        _finalizar()
        return list(lista_pendientes)
    except Exception:
        return None


def configurar_preferencias_bandeja(tipo_bandeja, accesorios):
    """
    Configura las preferencias de enrutamiento de un tipo de bandeja
    de cable (codos, tes, cruces, transiciones, uniones).

    Args:
        tipo_bandeja: CableTrayType de Revit
        accesorios: dict con claves opcionales:
          "codo_hz"   → ElementId codo horizontal
          "codo_vt_int" → ElementId codo vertical interior
          "codo_vt_ext" → ElementId codo vertical exterior
          "te"        → ElementId accesorio en T
          "cruz"      → ElementId accesorio en cruz
          "transicion"→ ElementId transición
          "union"     → ElementId unión

    Returns:
        True si se aplica, False si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        _iniciar()
        if "codo_hz" in accesorios:
            tipo_bandeja.Elbow = accesorios["codo_hz"]
        if "codo_vt_int" in accesorios:
            tipo_bandeja.get_Parameter(
                BuiltInParameter.RBS_CURVETYPE_DEFAULT_ELBOWUP_PARAM
            ).Set(accesorios["codo_vt_int"])
        if "codo_vt_ext" in accesorios:
            tipo_bandeja.get_Parameter(
                BuiltInParameter.RBS_CURVETYPE_DEFAULT_ELBOWDOWN_PARAM
            ).Set(accesorios["codo_vt_ext"])
        if "te" in accesorios:
            tipo_bandeja.Tee = accesorios["te"]
        if "cruz" in accesorios:
            tipo_bandeja.Cross = accesorios["cruz"]
        if "transicion" in accesorios:
            tipo_bandeja.Transition = accesorios["transicion"]
        if "union" in accesorios:
            tipo_bandeja.Union = accesorios["union"]
        _finalizar()
        return True
    except Exception:
        return False


# ── pandas (CPython 3.x / Dynamo 2.13+) ─────────────────────────────────────

def dataframe_tuberias(tuberias):
    """
    Exporta datos de tuberías Revit a un pandas DataFrame.
    Requiere CPython 3.x (Dynamo 2.13+).

    Args:
        tuberias: lista de elementos Pipe de Revit

    Returns:
        pandas DataFrame con columnas [ElementId, Sistema, DiamExt_mm,
        DiamInt_mm, Longitud_m, Nivel, Velocidad_ms],
        o None si pandas no disponible

    Revit: 2024-2026 | CPython 3.x (Dynamo 2.13+)
    """
    try:
        import pandas as pd
    except ImportError:
        return None
    filas = []
    for tub in tuberias:
        try:
            eid = int(tub.Id.Value)
        except AttributeError:
            eid = tub.Id.IntegerValue
        p_niv = tub.get_Parameter(BuiltInParameter.RBS_START_LEVEL_PARAM)
        filas.append({
            "ElementId": eid,
            "Sistema": obtener_sistema_tuberia(tub) or "",
            "DiamExt_mm": round(obtener_diametro_exterior_tuberia(tub), 1),
            "DiamInt_mm": round(obtener_diametro_interior_tuberia(tub), 1),
            "Longitud_m": round(obtener_longitud_tuberia(tub), 3),
            "Nivel": p_niv.AsValueString() if p_niv else "",
            "Velocidad_ms": velocidad_tuberia(tub),
        })
    return pd.DataFrame(filas)


def dataframe_conductos(conductos):
    """
    Exporta datos de conductos de ventilación a un pandas DataFrame.
    Requiere CPython 3.x (Dynamo 2.13+).

    Args:
        conductos: lista de elementos Duct de Revit

    Returns:
        pandas DataFrame con columnas [ElementId, Sistema, Ancho_mm,
        Alto_mm, Longitud_m, Nivel, AreaSeccion_m2, Velocidad_ms],
        o None si pandas no disponible

    Revit: 2024-2026 | CPython 3.x (Dynamo 2.13+)
    """
    try:
        import pandas as pd
    except ImportError:
        return None
    filas = []
    for duc in conductos:
        try:
            eid = int(duc.Id.Value)
        except AttributeError:
            eid = duc.Id.IntegerValue
        pw = duc.get_Parameter(BuiltInParameter.RBS_CURVE_WIDTH_PARAM)
        ph = duc.get_Parameter(BuiltInParameter.RBS_CURVE_HEIGHT_PARAM)
        p_niv = duc.get_Parameter(BuiltInParameter.RBS_START_LEVEL_PARAM)
        filas.append({
            "ElementId": eid,
            "Sistema": obtener_tipo_sistema_conducto(duc) or "",
            "Ancho_mm": round(_pies_a_mm(pw.AsDouble()), 1) if pw else 0,
            "Alto_mm": round(_pies_a_mm(ph.AsDouble()), 1) if ph else 0,
            "Longitud_m": round(obtener_longitud_conducto(duc), 3),
            "Nivel": p_niv.AsValueString() if p_niv else "",
            "AreaSeccion_m2": round(area_seccion_conducto(duc), 4),
            "Velocidad_ms": velocidad_conducto(duc),
        })
    return pd.DataFrame(filas)


def estadisticas_sistemas_pandas(tuberias=None, conductos=None):
    """
    Calcula estadísticas de longitud agrupadas por sistema.
    Requiere CPython 3.x (Dynamo 2.13+).

    Args:
        tuberias: lista de Pipe (opcional)
        conductos: lista de Duct (opcional)

    Returns:
        dict {tipo: DataFrame con describe() por Sistema},
        o None si pandas no disponible

    Revit: 2024-2026 | CPython 3.x (Dynamo 2.13+)
    """
    try:
        import pandas  # noqa: F401
    except ImportError:
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
