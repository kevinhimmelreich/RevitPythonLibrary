# -*- coding: utf-8 -*-
"""
lib_transacciones.py
Biblioteca de funciones Revit/Dynamo — Transacciones Avanzadas
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

from Autodesk.Revit.DB import (
    Transaction, TransactionGroup, SubTransaction
)
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

import Revit
clr.ImportExtensions(Revit.Elements)

doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
uidoc = uiapp.ActiveUIDocument

REVIT_VERSION = int(app.VersionNumber) if app else 0


def ejecutar_en_grupo(nombre_grupo, lista_funciones):
    """
    Ejecuta varias funciones dentro de un TransactionGroup.
    Confirma con Assimilate.

    Args:
        nombre_grupo: nombre del grupo de transacciones como string
        lista_funciones: lista de tuplas (callable, *args) a ejecutar
            en el grupo

    Returns:
        lista de resultados de cada funcion

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    grupo = TransactionGroup(doc, nombre_grupo)
    grupo.Start()
    resultados = []
    try:
        for item in lista_funciones:
            fn = item[0]
            args = item[1:] if len(item) > 1 else ()
            resultados.append(fn(*args))
        grupo.Assimilate()
    except Exception as e:
        grupo.RollBack()
        raise e
    return resultados


def iniciar_transaccion_nativa(nombre):
    """
    Inicia una Transaction nativa de Revit (no Dynamo) y la retorna.

    Args:
        nombre: nombre de la transaccion como string

    Returns:
        objeto Transaction iniciado (necesario para pasarlo a
        finalizar_transaccion_nativa)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    t = Transaction(doc, nombre)
    t.Start()
    return t


def finalizar_transaccion_nativa(transaction, commit=True):
    """
    Confirma o revierte una Transaction nativa de Revit.

    Args:
        transaction: objeto Transaction de Revit a cerrar
        commit: si True hace Commit, si False hace RollBack

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if commit:
        transaction.Commit()
    else:
        transaction.RollBack()


def ejecutar_subtransaccion(nombre, fn, *args):
    """
    Ejecuta una funcion dentro de una SubTransaction.
    Requiere una Transaction nativa activa en el contexto externo.

    Args:
        nombre: nombre descriptivo de la subtransaccion (informativo)
        fn: callable a ejecutar dentro de la subtransaccion
        *args: argumentos a pasar a fn

    Returns:
        resultado de fn

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    sub = SubTransaction(doc)
    sub.Start()
    try:
        resultado = fn(*args)
        sub.Commit()
        return resultado
    except Exception as e:
        sub.RollBack()
        raise e


def transaccion_nativa(nombre, fn, *args):
    """
    Ejecuta una funcion dentro de una Transaction nativa con RollBack
    automatico en caso de error.

    Args:
        nombre: nombre de la transaccion como string
        fn: callable a ejecutar
        *args: argumentos a pasar a fn

    Returns:
        resultado de fn

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    t = Transaction(doc, nombre)
    t.Start()
    try:
        resultado = fn(*args)
        t.Commit()
        return resultado
    except Exception as e:
        t.RollBack()
        raise e


def forzar_cierre_transacciones(doc_objetivo=None):
    """
    Fuerza el cierre de todas las transacciones Dynamo activas.
    Usar solo cuando sea estrictamente necesario (ej. al abrir documentos
    secundarios).

    Args:
        doc_objetivo: documento Revit (ignorado, actua sobre el
            TransactionManager global)

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    TransactionManager.Instance.ForceCloseTransaction()


def eliminar_elemento_en_subtransaccion(elemento):
    """
    Elimina un elemento del modelo dentro de una subtransaccion.

    Args:
        elemento: elemento Revit a eliminar

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    sub = SubTransaction(doc)
    sub.Start()
    doc.Delete(elemento.Id)
    sub.Commit()


def comparar_documentos(ruta_otro_doc):
    """
    Revit 2023+: compara el documento activo con otro por ruta y retorna
    diferencias.

    Args:
        ruta_otro_doc: ruta completa al otro archivo .rvt

    Returns:
        tupla (ids_creados, ids_modificados, ids_borrados)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    otro_doc = app.OpenDocumentFile(ruta_otro_doc)
    guid = otro_doc.GetDocumentVersion().VersionGUID
    dif = doc.GetChangedElements(guid)
    return (
        list(dif.GetCreatedElementIds()),
        list(dif.GetModifiedElementIds()),
        list(dif.GetDeletedElementIds()),
    )
