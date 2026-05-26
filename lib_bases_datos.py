# -*- coding: utf-8 -*-
"""
lib_bases_datos.py
Biblioteca de funciones Revit/Dynamo — Bases de Datos (JSON, CSV, IFC, GUID)
Compatible: IronPython 2.7 | CPython 3.x | Revit 2024-2026
Repositorio: https://github.com/kevinhimmelreich/RevitPythonLibrary
"""

import clr
import sys
import io
import json

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

from System.IO import Path
from Autodesk.Revit.DB import (
    FilteredElementCollector, ElementId, ViewSchedule, SectionType,
    IFCExportOptions, StorageType
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


def _iniciar(nombre="Transaccion"):
    TransactionManager.Instance.EnsureInTransaction(doc)

def _finalizar():
    TransactionManager.Instance.TransactionTaskDone()


def _id_a_int(element_id):
    try:
        return int(element_id.Value)
    except AttributeError:
        return element_id.IntegerValue


def _obtener_valor_param(param):
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
        return _id_a_int(param.AsElementId())
    return None


# ── JSON ──────────────────────────────────────────────────────────────────────

def leer_json(ruta):
    """
    Lee un archivo JSON y retorna el objeto Python resultante.

    Args:
        ruta: ruta completa al archivo .json

    Returns:
        dict o lista con el contenido del JSON

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    with io.open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def escribir_json(ruta, datos):
    """
    Exporta un objeto Python a un archivo JSON con indentacion de 2 espacios.

    Args:
        ruta: ruta completa al archivo .json de salida
        datos: dict o lista a serializar

    Returns:
        ruta del archivo creado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    with io.open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
    return ruta


# ── CSV ───────────────────────────────────────────────────────────────────────

def leer_csv(ruta, separador=";"):
    """
    Lee un archivo CSV y retorna una lista de diccionarios {columna: valor}.

    Args:
        ruta: ruta completa al archivo .csv
        separador: caracter separador de columnas (por defecto ";")

    Returns:
        lista de dicts con los datos del CSV

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    with io.open(ruta, "r", encoding="utf-8") as f:
        lineas = f.readlines()
    if not lineas:
        return []
    cabeceras = lineas[0].strip().split(separador)
    return [dict(zip(cabeceras, l.strip().split(separador))) for l in lineas[1:] if l.strip()]


def escribir_csv(ruta, filas, encabezados=None, separador=";"):
    """
    Exporta datos a un archivo CSV.

    Args:
        ruta: ruta completa al archivo .csv de salida
        filas: lista de dicts o lista de listas con los datos
        encabezados: lista de nombres de columnas (si None los infiere del primer dict)
        separador: caracter separador (por defecto ";")

    Returns:
        ruta del archivo creado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not filas:
        return ruta
    if encabezados is None and isinstance(filas[0], dict):
        encabezados = list(filas[0].keys())

    with io.open(ruta, "w", encoding="utf-8") as f:
        if encabezados:
            f.write(separador.join([str(h) for h in encabezados]) + "\n")
        for fila in filas:
            if isinstance(fila, dict):
                valores = [str(fila.get(h, "") or "") for h in encabezados]
            else:
                valores = [str(v) if v is not None else "" for v in fila]
            f.write(separador.join(valores) + "\n")
    return ruta


# ── Parametros Revit ↔ JSON ───────────────────────────────────────────────────

def exportar_parametros_elementos(elementos, parametros, ruta_archivo):
    """
    Exporta parametros especificos de una lista de elementos Revit a JSON.

    Args:
        elementos: lista de elementos Revit
        parametros: lista de nombres de parametros a exportar
        ruta_archivo: ruta completa al archivo .json de salida

    Returns:
        ruta del archivo creado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    datos = []
    for elem in elementos:
        fila = {
            "ElementId": _id_a_int(elem.Id),
            "UniqueId":  elem.UniqueId,
            "Categoria": elem.Category.Name if elem.Category else "",
        }
        for p in parametros:
            param = elem.LookupParameter(p)
            fila[p] = _obtener_valor_param(param)
        datos.append(fila)
    return escribir_json(ruta_archivo, datos)


def importar_parametros_desde_json(ruta_archivo):
    """
    Lee un JSON exportado con exportar_parametros_elementos y aplica los valores a los elementos.

    Args:
        ruta_archivo: ruta completa al archivo .json

    Returns:
        diccionario {ok: [ids], error: [ids]}

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    datos = leer_json(ruta_archivo)
    resultados = {"ok": [], "error": []}
    _iniciar("Importar Parametros JSON")
    for fila in datos:
        elem = doc.GetElement(ElementId(fila.get("ElementId", -1)))
        if elem is None:
            resultados["error"].append(fila.get("ElementId"))
            continue
        for clave, valor in fila.items():
            if clave in ("ElementId", "UniqueId", "Categoria"):
                continue
            param = elem.LookupParameter(clave)
            if param and not param.IsReadOnly and valor is not None:
                try:
                    t = param.StorageType
                    if t == StorageType.String:
                        param.Set(str(valor))
                    elif t == StorageType.Integer:
                        param.Set(int(valor))
                    elif t == StorageType.Double:
                        param.Set(float(valor))
                except Exception:
                    pass
        resultados["ok"].append(fila.get("ElementId"))
    _finalizar()
    return resultados


# ── IFC ───────────────────────────────────────────────────────────────────────

def exportar_ifc(ruta_ifc, opciones=None):
    """
    Exporta el documento activo a formato IFC.

    Args:
        ruta_ifc: ruta completa al archivo .ifc de salida
        opciones: IFCExportOptions (si None usa opciones por defecto)

    Returns:
        ruta_ifc

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if opciones is None:
        opciones = IFCExportOptions()
    directorio = Path.GetDirectoryName(ruta_ifc)
    nombre     = Path.GetFileName(ruta_ifc)
    doc.Export(directorio, nombre, opciones)
    return ruta_ifc


# ── Schedules → CSV ──────────────────────────────────────────────────────────

def exportar_schedule_a_csv(nombre_schedule, ruta_archivo, separador=";"):
    """
    Exporta una tabla de planificacion Revit a CSV.

    Args:
        nombre_schedule: nombre de la ViewSchedule de Revit
        ruta_archivo: ruta completa al archivo .csv de salida
        separador: caracter separador (por defecto ";")

    Returns:
        ruta del archivo creado, o None si no se encontro la schedule

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    schedules = list(FilteredElementCollector(doc).OfClass(ViewSchedule).ToElements())
    sch = next((s for s in schedules if s.Name == nombre_schedule), None)
    if sch is None:
        return None
    seccion = sch.GetTableData().GetSectionData(SectionType.Body)
    filas   = []
    for row in range(seccion.NumberOfRows):
        fila = [sch.GetCellText(SectionType.Body, row, col)
                for col in range(seccion.NumberOfColumns)]
        filas.append(fila)
    if len(filas) < 1:
        return None
    encabezados = filas[0]
    return escribir_csv(ruta_archivo, filas[1:], encabezados, separador)


def listar_schedules():
    """
    Lista los nombres de todas las tablas de planificacion del documento.

    Args:
        (ninguno)

    Returns:
        lista de nombres de ViewSchedule (strings)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return [s.Name for s in FilteredElementCollector(doc).OfClass(ViewSchedule).ToElements()]


# ── GUIDs ─────────────────────────────────────────────────────────────────────

def obtener_guid_elemento(elemento):
    """
    Retorna el UniqueId (GUID) de un elemento Revit.

    Args:
        elemento: elemento Revit

    Returns:
        UniqueId como string

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return elemento.UniqueId


def obtener_elemento_por_guid(guid_str):
    """
    Busca y retorna un elemento Revit por su UniqueId.

    Args:
        guid_str: UniqueId como string

    Returns:
        elemento Revit o None si no existe

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return doc.GetElement(guid_str)


# ── Configuracion ─────────────────────────────────────────────────────────────

def guardar_configuracion(configuracion, ruta_archivo):
    """
    Guarda un diccionario de configuracion como JSON.

    Args:
        configuracion: diccionario con la configuracion
        ruta_archivo: ruta completa al archivo .json de salida

    Returns:
        ruta del archivo creado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return escribir_json(ruta_archivo, configuracion)


def cargar_configuracion(ruta_archivo):
    """
    Carga un diccionario de configuracion desde un archivo JSON.

    Args:
        ruta_archivo: ruta completa al archivo .json

    Returns:
        diccionario con la configuracion

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return leer_json(ruta_archivo)
