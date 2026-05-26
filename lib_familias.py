# -*- coding: utf-8 -*-
"""
lib_familias.py
Biblioteca de funciones Revit/Dynamo — Familias
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

# ── Revit API ────────────────────────────────────────────────────────────────
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
clr.AddReference("RevitServices")
clr.AddReference("RevitNodes")

from Autodesk.Revit.DB import (
    FilteredElementCollector, ElementId, Family, FamilySymbol, FamilyInstance,
    FamilySymbolFilter, IFamilyLoadOptions, StructuralType, Line,
    ElementTransformUtils, XYZ, UnitUtils, UnitTypeId
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


# ── IFamilyLoadOptions (unica clase permitida por la interfaz .NET) ──────────
class _OpcionCarga(IFamilyLoadOptions):
    """Opciones de carga: sobreescribe parametros y acepta familias
    compartidas."""
    def OnFamilyFound(self, _familyInUse, _overwriteParameterValues):
        return True

    def OnSharedFamilyFound(
            self, _sharedFamily, _familyInUse, _source,
            _overwriteParameterValues):
        return True


def _iniciar(nombre="Transaccion"):
    TransactionManager.Instance.EnsureInTransaction(doc)


def _finalizar():
    TransactionManager.Instance.TransactionTaskDone()


def cargar_familia(ruta_rfa):
    """
    Carga una familia .rfa en el documento y activa todos sus tipos.

    Args:
        ruta_rfa: ruta completa al archivo .rfa

    Returns:
        lista de FamilySymbol activados, o None si no se cargo (ya existia
        o no se encontro)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not os.path.exists(ruta_rfa):
        return None
    ref_familia = clr.Reference[Family]()
    _iniciar("Cargar Familia")
    cargada = doc.LoadFamily(ruta_rfa, _OpcionCarga(), ref_familia)
    if cargada:
        familia = ref_familia.Value
        simbolos = []
        for sid in familia.GetFamilySymbolIds():
            s = doc.GetElement(sid)
            try:
                s.Activate()
            except Exception:
                pass
            simbolos.append(s)
        _finalizar()
        return simbolos
    _finalizar()
    return None


def obtener_tipos_de_familia(nombre_familia):
    """
    Retorna todos los FamilySymbol de una familia por su nombre y los activa.

    Args:
        nombre_familia: nombre de la familia como string

    Returns:
        lista de FamilySymbol activados

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tipos = list(
        FilteredElementCollector(doc).OfClass(FamilySymbol).ToElements()
    )
    resultado = [t for t in tipos if t.Family.Name == nombre_familia]
    _iniciar("Activar Tipos Familia")
    for t in resultado:
        if not t.IsActive:
            t.Activate()
    _finalizar()
    return resultado


def activar_tipo_familia(family_symbol):
    """
    Activa un FamilySymbol para que pueda ser colocado en el modelo.

    Args:
        family_symbol: FamilySymbol de Revit

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not family_symbol.IsActive:
        _iniciar("Activar Tipo Familia")
        family_symbol.Activate()
        _finalizar()


def colocar_instancia_familia(tipo_id, punto_xyz, nivel, angulo_rad=0.0):
    """
    Coloca una instancia de familia no estructural en un punto XYZ de un
    nivel.

    Args:
        tipo_id: ElementId del FamilySymbol
        punto_xyz: XYZ del punto de insercion
        nivel: objeto Level de Revit
        angulo_rad: rotacion en radianes respecto al eje Z (por defecto 0.0)

    Returns:
        FamilyInstance colocada

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tipo = doc.GetElement(tipo_id)
    if not tipo.IsActive:
        _iniciar("Activar Tipo")
        tipo.Activate()
        _finalizar()
    _iniciar("Colocar Instancia")
    instancia = doc.Create.NewFamilyInstance(
        punto_xyz, tipo, nivel, StructuralType.NonStructural)
    if angulo_rad != 0.0:
        eje = Line.CreateBound(punto_xyz, punto_xyz + XYZ.BasisZ)
        ElementTransformUtils.RotateElement(doc, instancia.Id, eje, angulo_rad)
    _finalizar()
    return instancia


def colocar_instancia_en_cara(tipo_id, cara, punto_en_cara):
    """
    Coloca una instancia de familia anclada a una cara de un elemento.

    Args:
        tipo_id: ElementId del FamilySymbol
        cara: Face de Revit como objeto Reference o Face
        punto_en_cara: XYZ del punto de insercion sobre la cara

    Returns:
        FamilyInstance colocada en la cara

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tipo = doc.GetElement(tipo_id)
    if not tipo.IsActive:
        _iniciar("Activar Tipo")
        tipo.Activate()
        _finalizar()
    _iniciar("Colocar Instancia en Cara")
    instancia = doc.Create.NewFamilyInstance(
        cara, punto_en_cara, XYZ.BasisX, tipo)
    _finalizar()
    return instancia


def obtener_parametros_familia(family_symbol):
    """
    Retorna un diccionario con los parametros de tipo de un FamilySymbol.

    Args:
        family_symbol: FamilySymbol de Revit

    Returns:
        diccionario {nombre_parametro: valor}

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    resultado = {}
    for param in family_symbol.Parameters:
        nombre = param.Definition.Name
        try:
            from Autodesk.Revit.DB import StorageType
            t = param.StorageType
            if t == StorageType.String:
                resultado[nombre] = param.AsString()
            elif t == StorageType.Integer:
                resultado[nombre] = param.AsInteger()
            elif t == StorageType.Double:
                resultado[nombre] = param.AsDouble()
            elif t == StorageType.ElementId:
                resultado[nombre] = param.AsElementId()
        except Exception:
            resultado[nombre] = None
    return resultado


def exportar_familia(familia, ruta_destino):
    """
    Exporta una familia a un archivo .rfa en la ruta indicada.

    Args:
        familia: elemento Family de Revit
        ruta_destino: ruta completa de salida incluyendo nombre y extension
            .rfa

    Returns:
        True si se exporto correctamente, False en caso contrario

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        fam_doc = doc.EditFamily(familia)
        fam_doc.SaveAs(ruta_destino)
        fam_doc.Close(False)
        return True
    except Exception:
        return False


def obtener_familias_por_categoria(nombre_categoria):
    """
    Retorna todas las familias del documento para una categoria dada.

    Args:
        nombre_categoria: nombre de la categoria como string

    Returns:
        lista de Family

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    familias = list(FilteredElementCollector(doc).OfClass(Family).ToElements())
    return [f for f in familias
            if f.FamilyCategory and f.FamilyCategory.Name == nombre_categoria]


def eliminar_familias_no_usadas():
    """
    Elimina del documento todas las familias sin instancias colocadas.

    Args:
        (ninguno)

    Returns:
        lista de nombres de familias eliminadas

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    eliminadas = []
    familias = list(FilteredElementCollector(doc).OfClass(Family).ToElements())
    _iniciar("Eliminar Familias No Usadas")
    for f in familias:
        usada = False
        for sid in f.GetFamilySymbolIds():
            col = FilteredElementCollector(doc)\
                  .OfClass(FamilyInstance)\
                  .WherePasses(FamilySymbolFilter(sid))
            if col.GetElementCount() > 0:
                usada = True
                break
        if not usada:
            try:
                doc.Delete(f.Id)
                eliminadas.append(f.Name)
            except Exception:
                pass
    _finalizar()
    return eliminadas


def exportar_todas_las_familias(directorio_destino):
    """
    Exporta todas las familias de usuario del documento como archivos .rfa
    organizados por categoria.

    Args:
        directorio_destino: ruta de la carpeta donde se exportan las familias

    Returns:
        tupla (exitosas, fallidas) con listas de nombres

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    exitosas, fallidas = [], []
    familias = list(FilteredElementCollector(doc).OfClass(Family).ToElements())
    _iniciar("Exportar Familias")
    for f in familias:
        if f.IsInPlace or not f.IsUserCreated:
            continue
        nombre = f.Name
        categoria = (f.FamilyCategory.Name
                     if f.FamilyCategory else "SinCategoria")
        carpeta = os.path.join(directorio_destino, categoria)
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
        ruta = os.path.join(carpeta, nombre + ".rfa")
        try:
            fam_doc = doc.EditFamily(f)
            fam_doc.SaveAs(ruta)
            fam_doc.Close(False)
            exitosas.append(nombre)
        except Exception:
            fallidas.append(nombre)
    _finalizar()
    return exitosas, fallidas
