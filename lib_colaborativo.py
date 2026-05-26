# -*- coding: utf-8 -*-
"""
lib_colaborativo.py
Biblioteca de funciones Revit/Dynamo — Trabajo Colaborativo (Worksharing)
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

from Autodesk.Revit.DB import (
    FilteredWorksetCollector, WorksetKindFilter, WorksetKind, WorksetId,
    WorksetConfiguration, WorksetConfigurationOption, ModelPathUtils,
    BuiltInParameter, OpenOptions,
    WorksharingSaveAsOptions, SaveAsOptions, SimpleWorksetConfiguration,
    RelinquishOptions, SynchronizeWithCentralOptions,
    TransactWithCentralOptions, Workset
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


def activar_worksharing(nombre_workset_arq="Rejillas", nombre_workset_struct="Subproyecto"):
    """
    Activa el modo colaborativo del documento (operacion irreversible).

    Args:
        nombre_workset_arq: nombre del primer workset a crear (por defecto "Rejillas")
        nombre_workset_struct: nombre del segundo workset (por defecto "Subproyecto")

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not doc.IsWorkshared:
        doc.EnableWorksharing(nombre_workset_arq, nombre_workset_struct)


def guardar_como_central(ruta_archivo, max_backups=3, compactar=True):
    """
    Guarda el documento como archivo central en la ruta indicada.

    Args:
        ruta_archivo: ruta completa al archivo .rvt de salida
        max_backups: numero maximo de copias de seguridad (por defecto 3)
        compactar: si True compacta el archivo al guardar

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    ws_opts = WorksharingSaveAsOptions()
    ws_opts.SaveAsCentral = True
    ws_opts.OpenWorksetsDefault = SimpleWorksetConfiguration.AskUserToSpecify

    save_opts = SaveAsOptions()
    save_opts.MaximumBackups       = max_backups
    save_opts.Compact              = compactar
    save_opts.OverwriteExistingFile = True
    save_opts.PreviewViewId        = doc.ActiveView.Id
    save_opts.SetWorksharingOptions(ws_opts)

    doc.SaveAs(ruta_archivo, save_opts)


def sincronizar_con_central(ceder_todo=True, compactar=True, comentario=""):
    """
    Sincroniza el archivo local con el central cediendo worksets.

    Args:
        ceder_todo: si True cede todos los worksets y elementos
        compactar: si True compacta el archivo al sincronizar
        comentario: comentario de sincronizacion como string

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    r_opts = RelinquishOptions(ceder_todo)
    if not ceder_todo:
        r_opts.StandardWorksets   = True
        r_opts.ViewWorksets       = True
        r_opts.FamilyWorksets     = True
        r_opts.UserWorksets       = True
        r_opts.CheckedOutElements = True

    s_opts = SynchronizeWithCentralOptions()
    s_opts.SetRelinquishOptions(r_opts)
    s_opts.Compact         = compactar
    s_opts.Comments        = comentario
    s_opts.SaveLocalBefore = True
    s_opts.SaveLocalAfter  = True

    doc.SynchronizeWithCentral(TransactWithCentralOptions(), s_opts)


def crear_workset(nombre):
    """
    Crea un nuevo workset de usuario en el documento colaborativo.

    Args:
        nombre: nombre del workset como string

    Returns:
        objeto Workset creado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar("Crear Workset")
    ws = Workset.Create(doc, nombre)
    _finalizar()
    return ws


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


def asignar_workset_a_elemento(elemento, workset_id):
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


def asignar_workset_a_lista(elementos, workset_id):
    """
    Asigna masivamente un workset a una lista de elementos.

    Args:
        elementos: lista de elementos Revit
        workset_id: WorksetId a asignar

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar("Asignar Workset Masivo")
    for elem in elementos:
        param = elem.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
        if param and not param.IsReadOnly:
            param.Set(workset_id.IntegerValue)
    _finalizar()


def obtener_workset_de_elemento(elemento):
    """
    Retorna el WorksetId del elemento.

    Args:
        elemento: elemento Revit

    Returns:
        WorksetId o None si el documento no es colaborativo

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    param = elemento.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
    return WorksetId(param.AsInteger()) if param else None


def abrir_documento(ruta_archivo, cerrar_worksets=True, detached=False):
    """
    Abre un documento Revit con opciones de apertura.

    Args:
        ruta_archivo: ruta completa al archivo .rvt
        cerrar_worksets: si True cierra todos los worksets al abrir
        detached: si True abre el modelo desvinculado del central

    Returns:
        objeto Document de Revit abierto

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    opts = OpenOptions()
    cfg_opt = (WorksetConfigurationOption.CloseAllWorksets if cerrar_worksets
               else WorksetConfigurationOption.OpenAllWorksets)
    cfg = WorksetConfiguration(cfg_opt)
    opts.SetOpenWorksetsConfiguration(cfg)
    if detached:
        opts.DetachFromCentralOption = DetachFromCentralOption.DetachAndPreserveWorksets  # noqa: F821
    model_path = ModelPathUtils.ConvertUserVisiblePathToModelPath(ruta_archivo)
    return app.OpenDocumentFile(model_path, opts)


def cerrar_documento(doc_a_cerrar, guardar=False):
    """
    Cierra un documento Revit.

    Args:
        doc_a_cerrar: documento Document de Revit a cerrar
        guardar: si True guarda antes de cerrar

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    doc_a_cerrar.Close(guardar)
