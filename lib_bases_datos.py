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

# ── Revit API ────────────────────────────────────────────────────────────────
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
clr.AddReference("RevitServices")
clr.AddReference("RevitNodes")

from System.IO import Path  # noqa: E402
from Autodesk.Revit.DB import (  # noqa: E402
    FilteredElementCollector, ElementId, ViewSchedule, SectionType,
    IFCExportOptions, StorageType
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


# ── JSON ─────────────────────────────────────────────────────────────────────

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


# ── CSV ──────────────────────────────────────────────────────────────────────

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
    return [
        dict(zip(cabeceras, linea.strip().split(separador)))
        for linea in lineas[1:]
        if linea.strip()
    ]


def escribir_csv(ruta, filas, encabezados=None, separador=";"):
    """
    Exporta datos a un archivo CSV.

    Args:
        ruta: ruta completa al archivo .csv de salida
        filas: lista de dicts o lista de listas con los datos
        encabezados: lista de nombres de columnas (si None los infiere
                     del primer dict)
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


# ── Parametros Revit / JSON ──────────────────────────────────────────────────

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
            "UniqueId": elem.UniqueId,
            "Categoria": elem.Category.Name if elem.Category else "",
        }
        for p in parametros:
            param = elem.LookupParameter(p)
            fila[p] = _obtener_valor_param(param)
        datos.append(fila)
    return escribir_json(ruta_archivo, datos)


def importar_parametros_desde_json(ruta_archivo):
    """
    Lee un JSON de exportar_parametros_elementos y aplica valores
    a los elementos del modelo.

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


# ── IFC ──────────────────────────────────────────────────────────────────────

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
    nombre = Path.GetFileName(ruta_ifc)
    doc.Export(directorio, nombre, opciones)
    return ruta_ifc


# ── Schedules / CSV ──────────────────────────────────────────────────────────

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
    colector = FilteredElementCollector(doc).OfClass(ViewSchedule)
    schedules = list(colector.ToElements())
    sch = next((s for s in schedules if s.Name == nombre_schedule), None)
    if sch is None:
        return None
    seccion = sch.GetTableData().GetSectionData(SectionType.Body)
    filas = []
    for row in range(seccion.NumberOfRows):
        fila = [
            sch.GetCellText(SectionType.Body, row, col)
            for col in range(seccion.NumberOfColumns)
        ]
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
    colector = FilteredElementCollector(doc).OfClass(ViewSchedule)
    return [s.Name for s in colector.ToElements()]


# ── GUIDs ────────────────────────────────────────────────────────────────────

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


# ── Configuracion ────────────────────────────────────────────────────────────

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


# ── pandas (CPython 3.x / Dynamo 2.13+) ──────────────────────────────────────

def exportar_a_dataframe(elementos, parametros):
    """
    Exporta parametros de elementos Revit a un pandas DataFrame.
    Requiere CPython 3.x (Dynamo 2.13+). En IronPython retorna None con aviso.

    Args:
        elementos: lista de elementos Revit
        parametros: lista de nombres de parametros a incluir como columnas

    Returns:
        pandas DataFrame con columnas [ElementId, UniqueId, Categoria,
        *parametros], o None si pandas no esta disponible

    Revit: 2024-2026 | CPython 3.x (Dynamo 2.13+)
    """
    try:
        import pandas as pd
    except ImportError:
        print("pandas no disponible. Requiere CPython 3.x (Dynamo 2.13+).")
        return None

    filas = []
    for elem in elementos:
        try:
            eid = int(elem.Id.Value)
        except AttributeError:
            eid = elem.Id.IntegerValue
        fila = {
            "ElementId": eid,
            "UniqueId": elem.UniqueId,
            "Categoria": elem.Category.Name if elem.Category else "",
        }
        for nombre in parametros:
            fila[nombre] = _obtener_valor_param(elem.LookupParameter(nombre))
        filas.append(fila)
    return pd.DataFrame(filas)


def importar_desde_dataframe(df, col_id="ElementId"):
    """
    Aplica valores de un pandas DataFrame a los elementos Revit por ElementId.
    Las columnas ElementId, UniqueId y Categoria se omiten automaticamente.
    Requiere CPython 3.x (Dynamo 2.13+).

    Args:
        df: pandas DataFrame con columna de ID y columnas de parametros
        col_id: nombre de la columna que contiene el ElementId
                (por defecto "ElementId")

    Returns:
        diccionario {ok: [ids], error: [ids]}

    Revit: 2024-2026 | CPython 3.x (Dynamo 2.13+)
    """
    try:
        import pandas as pd
    except ImportError:
        print("pandas no disponible. Requiere CPython 3.x (Dynamo 2.13+).")
        return None

    columnas_ignorar = {col_id, "UniqueId", "Categoria"}
    cols_param = [c for c in df.columns if c not in columnas_ignorar]
    resultados = {"ok": [], "error": []}

    _iniciar("Importar desde DataFrame")
    for _, fila in df.iterrows():
        try:
            elem = doc.GetElement(ElementId(int(fila[col_id])))
            if elem is None:
                resultados["error"].append(fila[col_id])
                continue
            for col in cols_param:
                valor = fila[col]
                if pd.isna(valor):
                    continue
                param = elem.LookupParameter(col)
                if param and not param.IsReadOnly:
                    t = param.StorageType
                    if t == StorageType.String:
                        param.Set(str(valor))
                    elif t == StorageType.Integer:
                        param.Set(int(valor))
                    elif t == StorageType.Double:
                        param.Set(float(valor))
            resultados["ok"].append(int(fila[col_id]))
        except Exception as e:
            resultados["error"].append(str(e))
    _finalizar()
    return resultados


def estadisticas_dataframe(df, columnas_numericas=None):
    """
    Calcula estadisticas descriptivas de columnas numericas de un DataFrame.
    Requiere CPython 3.x (Dynamo 2.13+).

    Args:
        df: pandas DataFrame
        columnas_numericas: lista de nombres de columnas a analizar
                            (si None analiza todas las numericas)

    Returns:
        pandas DataFrame con estadisticas (count, mean, std, min,
        max, percentiles), o None si pandas no esta disponible

    Revit: 2024-2026 | CPython 3.x (Dynamo 2.13+)
    """
    try:
        import pandas  # noqa: F401 — solo comprueba disponibilidad
    except ImportError:
        print("pandas no disponible. Requiere CPython 3.x (Dynamo 2.13+).")
        return None

    if columnas_numericas:
        return df[columnas_numericas].describe()
    return df.select_dtypes(include="number").describe()


def agrupar_dataframe(df, col_grupo, col_valor, operacion="sum"):
    """
    Agrupa un DataFrame por una columna y aplica una operacion de agregacion.
    Requiere CPython 3.x (Dynamo 2.13+).

    Args:
        df: pandas DataFrame
        col_grupo: nombre de la columna de agrupacion (ej. "Categoria")
        col_valor: nombre de la columna numerica a agregar
        operacion: "sum", "mean", "count", "min", "max" (por defecto "sum")

    Returns:
        pandas Series con el resultado de la agregacion,
        o None si pandas no esta disponible

    Revit: 2024-2026 | CPython 3.x (Dynamo 2.13+)
    """
    try:
        import pandas  # noqa: F401 — solo comprueba disponibilidad
    except ImportError:
        print("pandas no disponible. Requiere CPython 3.x (Dynamo 2.13+).")
        return None

    return getattr(df.groupby(col_grupo)[col_valor], operacion)()


def exportar_dataframe_a_csv(df, ruta, separador=";", indice=False):
    """
    Exporta un pandas DataFrame a CSV con encoding UTF-8.
    Requiere CPython 3.x (Dynamo 2.13+).

    Args:
        df: pandas DataFrame a exportar
        ruta: ruta completa al archivo .csv de salida
        separador: caracter separador (por defecto ";")
        indice: si True incluye el indice del DataFrame como columna

    Returns:
        ruta del archivo creado, o None si pandas no esta disponible

    Revit: 2024-2026 | CPython 3.x (Dynamo 2.13+)
    """
    try:
        import pandas  # noqa: F401 — solo comprueba disponibilidad
    except ImportError:
        print("pandas no disponible. Requiere CPython 3.x (Dynamo 2.13+).")
        return None

    df.to_csv(ruta, sep=separador, encoding="utf-8", index=indice)
    return ruta


def leer_csv_pandas(ruta, separador=";"):
    """
    Lee un archivo CSV a un pandas DataFrame con encoding UTF-8.
    Requiere CPython 3.x (Dynamo 2.13+).

    Args:
        ruta: ruta completa al archivo .csv
        separador: caracter separador (por defecto ";")

    Returns:
        pandas DataFrame, o None si pandas no esta disponible

    Revit: 2024-2026 | CPython 3.x (Dynamo 2.13+)
    """
    try:
        import pandas as pd
    except ImportError:
        print("pandas no disponible. Requiere CPython 3.x (Dynamo 2.13+).")
        return None

    return pd.read_csv(ruta, sep=separador, encoding="utf-8")
