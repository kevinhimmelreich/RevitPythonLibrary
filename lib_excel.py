# -*- coding: utf-8 -*-
"""
lib_excel.py
Biblioteca de funciones Revit/Dynamo — Excel
Compatible: IronPython 2.7 | CPython 3.x | Revit 2024-2026
Repositorio: https://github.com/kevinhimmelreich/RevitPythonLibrary
"""

import clr
import sys
import os

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

from Autodesk.Revit.DB import (
    FilteredElementCollector, ElementId, ViewSchedule, SectionType,
    StorageType
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
        try:
            return int(param.AsElementId().Value)
        except AttributeError:
            return param.AsElementId().IntegerValue
    return None


# ── DSOffice (nativo Dynamo) ──────────────────────────────────────────────────

def leer_excel_dsoffice(ruta, nombre_hoja, fila_inicio=0, col_inicio=0):
    """
    Lee datos de Excel usando DSOffice (nativo Dynamo). Devuelve lista de listas.

    Args:
        ruta: ruta completa al archivo .xlsx
        nombre_hoja: nombre de la hoja de Excel
        fila_inicio: fila de inicio (0-based)
        col_inicio: columna de inicio (0-based)

    Returns:
        lista de listas con los datos de la hoja

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    clr.AddReference("DSOffice")
    from DSOffice import Data
    return Data.OpenXLSX(ruta, nombre_hoja, fila_inicio, col_inicio, False)


def escribir_excel_dsoffice(ruta, nombre_hoja, datos_2d, fila_inicio=0, col_inicio=0, sobreescribir=True):
    """
    Escribe datos en Excel usando DSOffice (nativo Dynamo).

    Args:
        ruta: ruta completa al archivo .xlsx
        nombre_hoja: nombre de la hoja de Excel
        datos_2d: lista de listas con los datos a escribir
        fila_inicio: fila de inicio (0-based)
        col_inicio: columna de inicio (0-based)
        sobreescribir: si True sobreescribe el archivo existente

    Returns:
        True si la operacion fue exitosa

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    clr.AddReference("DSOffice")
    from DSOffice import Data
    Data.WriteToXLSX(datos_2d, ruta, nombre_hoja, fila_inicio, col_inicio, sobreescribir)
    return True


def obtener_hojas_excel(ruta):
    """
    Retorna los nombres de todas las hojas de un archivo Excel via DSOffice.

    Args:
        ruta: ruta completa al archivo .xlsx

    Returns:
        lista de nombres de hojas (strings)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    clr.AddReference("DSOffice")
    from DSOffice import Data
    return Data.GetWorksheetsFromXLSX(ruta)


# ── COM Interop (requiere Microsoft Office instalado) ─────────────────────────

def leer_excel_com(ruta, nombre_hoja=None, indice_hoja=1):
    """
    Lee datos de Excel usando COM Interop (requiere Office instalado). Fuera de Dynamo.

    Args:
        ruta: ruta completa al archivo .xlsx
        nombre_hoja: nombre de la hoja (tiene preferencia sobre indice_hoja)
        indice_hoja: indice de la hoja (1-based, usado si nombre_hoja es None)

    Returns:
        lista de listas con los valores de la hoja

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    clr.AddReference("Microsoft.Office.Interop.Excel")
    from Microsoft.Office.Interop import Excel as _Excel
    xl = _Excel.ApplicationClass()
    xl.Visible = False
    try:
        wb = xl.Workbooks.Open(ruta)
        ws = wb.Sheets[nombre_hoja] if nombre_hoja else wb.Sheets[indice_hoja]
        usado = ws.UsedRange
        datos = []
        for i in range(1, usado.Rows.Count + 1):
            fila = [ws.Cells[i, j].Value2 for j in range(1, usado.Columns.Count + 1)]
            datos.append(fila)
        wb.Close(False)
        return datos
    finally:
        xl.Quit()


def escribir_excel_com(ruta, datos_2d, nombre_hoja="Hoja1", fila_inicio=1, col_inicio=1):
    """
    Escribe datos en Excel usando COM Interop (requiere Office instalado). Fuera de Dynamo.

    Args:
        ruta: ruta completa al archivo .xlsx
        datos_2d: lista de listas con los datos a escribir
        nombre_hoja: nombre de la hoja de destino
        fila_inicio: fila inicial (1-based)
        col_inicio: columna inicial (1-based)

    Returns:
        True si la operacion fue exitosa

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    clr.AddReference("Microsoft.Office.Interop.Excel")
    from Microsoft.Office.Interop import Excel as _Excel
    xl = _Excel.ApplicationClass()
    xl.Visible = False
    try:
        wb = xl.Workbooks.Open(ruta) if os.path.exists(ruta) else xl.Workbooks.Add()
        try:
            ws = wb.Sheets[nombre_hoja]
        except Exception:
            ws = wb.Sheets.Add()
            ws.Name = nombre_hoja
        for i, fila in enumerate(datos_2d):
            for j, valor in enumerate(fila):
                ws.Cells[fila_inicio + i, col_inicio + j].Value2 = valor
        wb.SaveAs(ruta)
        wb.Close(True)
    finally:
        xl.Quit()
    return True


def crear_libro_excel_nuevo(ruta):
    """
    Crea un nuevo libro Excel vacio en la ruta indicada usando COM Interop.

    Args:
        ruta: ruta completa al archivo .xlsx a crear

    Returns:
        True si se creo correctamente

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    clr.AddReference("Microsoft.Office.Interop.Excel")
    from Microsoft.Office.Interop import Excel as _Excel
    xl = _Excel.ApplicationClass()
    xl.Visible = False
    try:
        wb = xl.Workbooks.Add()
        wb.SaveAs(ruta)
        wb.Close(True)
    finally:
        xl.Quit()
    return True


def cerrar_excel_com(excel_app, guardar=False):
    """
    Cierra una instancia de Excel COM de forma segura.

    Args:
        excel_app: instancia de Excel.ApplicationClass
        guardar: si True guarda antes de cerrar

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        for wb in list(excel_app.Workbooks):
            wb.Close(guardar)
        excel_app.Quit()
    except Exception:
        pass


# ── Integracion Revit <-> Excel ───────────────────────────────────────────────

def exportar_parametros_a_excel(elementos, nombres_params, ruta_salida, nombre_hoja="Datos"):
    """
    Exporta una lista de elementos Revit con sus parametros a Excel via DSOffice.

    Args:
        elementos: lista de elementos Revit
        nombres_params: lista de nombres de parametros a exportar
        ruta_salida: ruta completa al archivo .xlsx de salida
        nombre_hoja: nombre de la hoja de destino

    Returns:
        True si la exportacion fue exitosa

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    cabecera = ["ElementId", "UniqueId", "Categoria"] + list(nombres_params)
    filas    = [cabecera]
    for elem in elementos:
        try:
            eid_int = int(elem.Id.Value)
        except AttributeError:
            eid_int = elem.Id.IntegerValue
        fila = [
            eid_int,
            elem.UniqueId,
            elem.Category.Name if elem.Category else "",
        ]
        for nombre in nombres_params:
            param = elem.LookupParameter(nombre)
            fila.append(_obtener_valor_param(param))
        filas.append(fila)
    return escribir_excel_dsoffice(ruta_salida, nombre_hoja, filas)


def importar_parametros_desde_excel(ruta_excel, nombre_hoja, id_col=0, datos_col=None):
    """
    Lee un Excel exportado con exportar_parametros_a_excel y aplica valores a los elementos Revit.

    Args:
        ruta_excel: ruta completa al archivo .xlsx
        nombre_hoja: nombre de la hoja a leer
        id_col: indice de la columna con el ElementId (0-based)
        datos_col: dict {nombre_param: indice_col} (si None usa la cabecera)

    Returns:
        diccionario {ok: [ids], error: [ids]}

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    datos = leer_excel_dsoffice(ruta_excel, nombre_hoja)
    if not datos or isinstance(datos, string_types):
        return datos
    cabecera = datos[0]
    if datos_col is None:
        datos_col = {
            cabecera[i]: i for i in range(len(cabecera))
            if i != id_col and cabecera[i] not in ("UniqueId", "Categoria")
        }
    resultados = {"ok": [], "error": []}
    _iniciar("Importar Parametros Excel")
    for fila in datos[1:]:
        try:
            elem = doc.GetElement(ElementId(int(fila[id_col])))
            if elem is None:
                resultados["error"].append(fila[id_col])
                continue
            for param_nombre, col_idx in datos_col.items():
                p = elem.LookupParameter(param_nombre)
                if p and not p.IsReadOnly:
                    valor = fila[col_idx]
                    t = p.StorageType
                    if t == StorageType.String:
                        p.Set(str(valor) if valor is not None else "")
                    elif t == StorageType.Integer:
                        p.Set(int(valor))
                    elif t == StorageType.Double:
                        p.Set(float(valor))
            resultados["ok"].append(int(fila[id_col]))
        except Exception as e:
            resultados["error"].append(str(e))
    _finalizar()
    return resultados


def exportar_schedule_a_excel(nombre_schedule, ruta_salida, nombre_hoja="Schedule"):
    """
    Exporta una tabla de planificacion Revit directamente a Excel via DSOffice.

    Args:
        nombre_schedule: nombre de la ViewSchedule de Revit
        ruta_salida: ruta completa al archivo .xlsx de salida
        nombre_hoja: nombre de la hoja de destino

    Returns:
        True si la exportacion fue exitosa, None si no se encontro la schedule

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    schedules = list(FilteredElementCollector(doc).OfClass(ViewSchedule).ToElements())
    sch = next((s for s in schedules if s.Name == nombre_schedule), None)
    if sch is None:
        return None
    seccion = sch.GetTableData().GetSectionData(SectionType.Body)
    filas   = []
    for row in range(seccion.NumberOfRows):
        filas.append([
            sch.GetCellText(SectionType.Body, row, col)
            for col in range(seccion.NumberOfColumns)
        ])
    return escribir_excel_dsoffice(ruta_salida, nombre_hoja, filas)
