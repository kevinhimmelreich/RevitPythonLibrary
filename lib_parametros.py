# -*- coding: utf-8 -*-
"""
lib_parametros.py — Gestión completa de parámetros en Revit

Bloques:
  1. Archivo .txt (parámetros compartidos) — ruta, abrir, contenido
  2. Grupos en el .txt                     — listar, obtener, crear
  3. Definiciones en el .txt               — listar, obtener, crear por tipo
  4. Vincular compartidos al proyecto      — insert / update / remove / query
  5. Parámetros compartidos en familias    — agregar, quitar, convertir
  6. Parámetros locales en FamilyManager   — crear, eliminar
  7. Fórmulas en FamilyManager            — asignar, leer, borrar
  8. Anidar parámetros                    — AssociateElementParameterToFamilyParameter
  9. Cotas y FamilyLabel                  — asignar parámetro a cota
 10. Tipos de familia (FamilyManager)      — crear, duplicar, renombrar, eliminar
 11. Parámetros globales de proyecto       — crear, listar, valor, asociar, eliminar
 12. ExtensibleStorage                    — Schema, Entity, leer/escribir/eliminar
 13. Utilidades generales                  — GUID, buscar, listar

Requiere Revit 2022+ (usa SpecTypeId / GroupTypeId).
"""
import os
import clr
clr.AddReference("RevitAPI")

from Autodesk.Revit.DB import (
    ExternalDefinitionCreationOptions,
    InstanceBinding,
    TypeBinding,
    BuiltInCategory,
    SpecTypeId,
    GroupTypeId,
    FilteredElementCollector,
    SharedParameterElement,
    GlobalParameter,
    DoubleParameterValue,
    IntegerParameterValue,
    StringParameterValue,
    ElementIdParameterValue,
    ParameterUtils,
)
from Autodesk.Revit.DB.ExtensibleStorage import (
    SchemaBuilder,
    AccessLevel,
    Entity,
)
import System

# =============================================================================
#  1. ARCHIVO DE PARÁMETROS COMPARTIDOS (.txt)
# =============================================================================

def obtener_ruta_archivo_compartidos(app):
    """
    Devuelve la ruta del .txt de parámetros compartidos actualmente configurada,
    o cadena vacía si no hay ninguna.
    """
    return app.SharedParametersFilename or ""


def establecer_archivo_compartidos(app, ruta_txt):
    """
    Apunta la aplicación al .txt indicado y devuelve el DefinitionFile.

    Si el archivo no existe lo crea vacío (Revit escribe su cabecera al
    abrirlo por primera vez).  Devuelve None si la ruta es inválida.
    """
    directorio = os.path.dirname(ruta_txt)
    if directorio and not os.path.exists(directorio):
        return None
    if not os.path.exists(ruta_txt):
        # Crear archivo vacío; Revit añade la cabecera al abrirlo
        with open(ruta_txt, "w") as f:
            f.write("")
    app.SharedParametersFilename = ruta_txt
    return app.OpenSharedParameterFile()


def abrir_archivo_compartidos(app):
    """
    Abre y devuelve el DefinitionFile actualmente configurado.
    Devuelve None si no hay archivo configurado o la ruta no existe.
    """
    return app.OpenSharedParameterFile()


def info_archivo_compartidos(app):
    """
    Devuelve un dict con la ruta y el contenido resumido del .txt:
      {ruta, grupos: {nombre_grupo: [nombre_def, ...]}}
    """
    ruta = obtener_ruta_archivo_compartidos(app)
    df = abrir_archivo_compartidos(app)
    if df is None:
        return {"ruta": ruta, "grupos": {}}
    return {"ruta": ruta, "grupos": listar_grupos_y_definiciones(df)}


# =============================================================================
#  2. GRUPOS DENTRO DEL .txt
# =============================================================================

def obtener_grupos(definition_file):
    """Devuelve lista de todos los DefinitionGroup del archivo."""
    return list(definition_file.Groups)


def obtener_grupo(definition_file, nombre):
    """Devuelve el DefinitionGroup con ese nombre, o None si no existe."""
    return definition_file.Groups.get_Item(nombre)


def crear_grupo(definition_file, nombre):
    """
    Crea un DefinitionGroup en el .txt.
    Si ya existe lo devuelve sin duplicar.
    """
    grupo = obtener_grupo(definition_file, nombre)
    if grupo is None:
        grupo = definition_file.Groups.Create(nombre)
    return grupo


def listar_grupos_y_definiciones(definition_file):
    """
    Devuelve dict {nombre_grupo: [nombre_def, ...]} con todo el contenido del .txt.
    """
    return {
        grupo.Name: [d.Name for d in grupo.Definitions]
        for grupo in definition_file.Groups
    }


# Nota sobre borrado de grupos/definiciones:
# La Revit API no expone métodos para eliminar un DefinitionGroup ni una
# ExternalDefinition del .txt. El archivo es texto plano con formato
# propietario; la única forma de eliminarlo es editar el .txt manualmente
# o reemplazarlo con uno nuevo. No existe borrar_grupo() ni borrar_definicion().


# =============================================================================
#  3. DEFINICIONES (parámetros individuales) DENTRO DE UN GRUPO
# =============================================================================

def obtener_definiciones(grupo):
    """Devuelve lista de todas las ExternalDefinition de un grupo."""
    return list(grupo.Definitions)


def obtener_definicion(grupo, nombre):
    """Devuelve la ExternalDefinition por nombre, o None."""
    return grupo.Definitions.get_Item(nombre)


def crear_definicion(grupo, nombre, spec_type_id=None, visible=True, descripcion=""):
    """
    Crea una ExternalDefinition en el grupo con el tipo de dato indicado.

    spec_type_id: ForgeTypeId de SpecTypeId (ej. SpecTypeId.String.Text).
                  Por defecto texto (SpecTypeId.String.Text).
    visible:      Si aparece en la interfaz de usuario de Revit.
    descripcion:  Texto descriptivo opcional.

    Si ya existe una definición con ese nombre la devuelve sin duplicar.
    """
    if spec_type_id is None:
        spec_type_id = SpecTypeId.String.Text
    existente = obtener_definicion(grupo, nombre)
    if existente is not None:
        return existente
    opts = ExternalDefinitionCreationOptions(nombre, spec_type_id)
    opts.Visible = visible
    if descripcion:
        opts.Description = descripcion
    return grupo.Definitions.Create(opts)


def crear_definicion_texto(grupo, nombre, visible=True, descripcion=""):
    """Atajo: parámetro de tipo Texto."""
    return crear_definicion(grupo, nombre, SpecTypeId.String.Text, visible, descripcion)


def crear_definicion_entero(grupo, nombre, visible=True, descripcion=""):
    """Atajo: parámetro de tipo Entero."""
    return crear_definicion(grupo, nombre, SpecTypeId.Int64, visible, descripcion)


def crear_definicion_numero(grupo, nombre, visible=True, descripcion=""):
    """Atajo: parámetro de tipo Número (real)."""
    return crear_definicion(grupo, nombre, SpecTypeId.Number, visible, descripcion)


def crear_definicion_longitud(grupo, nombre, visible=True, descripcion=""):
    """Atajo: parámetro de tipo Longitud."""
    return crear_definicion(grupo, nombre, SpecTypeId.Length, visible, descripcion)


def crear_definicion_area(grupo, nombre, visible=True, descripcion=""):
    """Atajo: parámetro de tipo Área."""
    return crear_definicion(grupo, nombre, SpecTypeId.Area, visible, descripcion)


def crear_definicion_volumen(grupo, nombre, visible=True, descripcion=""):
    """Atajo: parámetro de tipo Volumen."""
    return crear_definicion(grupo, nombre, SpecTypeId.Volume, visible, descripcion)


def crear_definicion_angulo(grupo, nombre, visible=True, descripcion=""):
    """Atajo: parámetro de tipo Ángulo."""
    return crear_definicion(grupo, nombre, SpecTypeId.Angle, visible, descripcion)


def crear_definicion_si_no(grupo, nombre, visible=True, descripcion=""):
    """Atajo: parámetro de tipo Sí/No (booleano)."""
    return crear_definicion(grupo, nombre, SpecTypeId.Boolean.YesNo, visible, descripcion)


def crear_definicion_url(grupo, nombre, visible=True, descripcion=""):
    """Atajo: parámetro de tipo URL."""
    return crear_definicion(grupo, nombre, SpecTypeId.String.Url, visible, descripcion)


# =============================================================================
#  4. VINCULAR PARÁMETROS AL PROYECTO
# =============================================================================

def vincular_a_proyecto(doc, app, definicion, lista_bic,
                        es_instancia=True, grupo_param=None):
    """
    Vincula una ExternalDefinition al proyecto para las categorías indicadas.

    doc        : Document activo del proyecto (no Family Editor)
    app        : UIApplication.Application (o Application)
    definicion : ExternalDefinition obtenida del .txt
    lista_bic  : lista de BuiltInCategory (ej. [BuiltInCategory.OST_Walls])
    es_instancia: True → InstanceBinding / False → TypeBinding
    grupo_param : GroupTypeId donde aparece el parámetro (por defecto GroupTypeId.Data)

    Devuelve True si se insertó, False si ya existía.
    """
    if grupo_param is None:
        grupo_param = GroupTypeId.Data
    cats = app.Create.NewCategorySet()
    for bic in lista_bic:
        cat = doc.Settings.Categories.get_Item(bic)
        if cat is not None:
            cats.Insert(cat)
    binding = (app.Create.NewInstanceBinding(cats) if es_instancia
               else app.Create.NewTypeBinding(cats))
    mapa = doc.ParameterBindings
    if mapa.Contains(definicion):
        return False
    return mapa.Insert(definicion, binding, grupo_param)


def actualizar_vinculo_proyecto(doc, app, definicion, lista_bic,
                                es_instancia=True, grupo_param=None):
    """
    Actualiza el binding de un parámetro ya vinculado (cambia categorías o tipo).
    Inserta si no existe. Devuelve True si tuvo éxito.
    """
    if grupo_param is None:
        grupo_param = GroupTypeId.Data
    cats = app.Create.NewCategorySet()
    for bic in lista_bic:
        cat = doc.Settings.Categories.get_Item(bic)
        if cat is not None:
            cats.Insert(cat)
    binding = (app.Create.NewInstanceBinding(cats) if es_instancia
               else app.Create.NewTypeBinding(cats))
    mapa = doc.ParameterBindings
    if mapa.Contains(definicion):
        return mapa.ReInsert(definicion, binding, grupo_param)
    return mapa.Insert(definicion, binding, grupo_param)


def desvincular_de_proyecto(doc, definicion):
    """
    Elimina el binding del parámetro compartido del proyecto.
    Devuelve True si se eliminó, False si no estaba vinculado.
    """
    mapa = doc.ParameterBindings
    if mapa.Contains(definicion):
        return mapa.Remove(definicion)
    return False


def esta_vinculado_proyecto(doc, definicion):
    """True si la ExternalDefinition ya tiene binding en el proyecto."""
    return doc.ParameterBindings.Contains(definicion)


def obtener_parametros_compartidos_proyecto(doc):
    """
    Lista todos los parámetros compartidos vinculados al proyecto.

    Devuelve lista de dicts:
      {nombre, es_instancia, categorias: [str], guid}
    """
    resultado = []
    mapa = doc.ParameterBindings
    it = mapa.ForwardIterator()
    it.Reset()
    while it.MoveNext():
        defn = it.Key
        binding = it.Current
        # Solo los que son ExternalDefinition (= compartidos)
        if not hasattr(defn, "GUID"):
            continue
        cats = [c.Name for c in binding.Categories]
        resultado.append({
            "nombre": defn.Name,
            "guid": str(defn.GUID),
            "es_instancia": isinstance(binding, InstanceBinding),
            "categorias": cats,
        })
    return resultado


def esta_parametro_en_categoria(doc, nombre_param, bic):
    """
    True si el parámetro compartido está vinculado a la categoría indicada.
    """
    mapa = doc.ParameterBindings
    it = mapa.ForwardIterator()
    it.Reset()
    cat_target = doc.Settings.Categories.get_Item(bic)
    while it.MoveNext():
        defn = it.Key
        if defn.Name != nombre_param:
            continue
        for cat in it.Current.Categories:
            if cat.Id == cat_target.Id:
                return True
    return False


# =============================================================================
#  5. PARÁMETROS COMPARTIDOS EN FAMILIAS (Family Editor)
# =============================================================================

def agregar_a_familia(doc, definicion, grupo_param=None, es_instancia=True):
    """
    Añade un parámetro compartido a la familia activa (solo en Family Editor).

    grupo_param: GroupTypeId donde aparece (por defecto GroupTypeId.Data)
    Devuelve el FamilyParameter creado.
    """
    if grupo_param is None:
        grupo_param = GroupTypeId.Data
    return doc.FamilyManager.AddParameter(definicion, grupo_param, es_instancia)


def quitar_de_familia(doc, nombre_param):
    """
    Elimina un parámetro de la familia activa por nombre.
    Devuelve True si se eliminó, False si no se encontró.
    """
    fm = doc.FamilyManager
    for fp in fm.GetParameters():
        if fp.Definition.Name == nombre_param:
            fm.RemoveParameter(fp)
            return True
    return False


def obtener_parametros_familia_manager(doc):
    """
    Lista todos los parámetros del FamilyManager activo.

    Devuelve lista de dicts:
      {nombre, es_instancia, es_compartido, tipo_dato}
    """
    fm = doc.FamilyManager
    return [
        {
            "nombre": fp.Definition.Name,
            "es_instancia": fp.IsInstance,
            "es_compartido": fp.IsShared,
            "tipo_dato": str(fp.Definition.GetDataType()),
        }
        for fp in fm.GetParameters()
    ]


def convertir_local_a_compartido(doc, nombre_param_local, definicion,
                                 grupo_param=None, es_instancia=True):
    """
    Reemplaza un parámetro de familia local por uno compartido equivalente.

    Elimina el parámetro local con ese nombre y añade el compartido.
    Nota: los valores asignados se pierden al eliminar el parámetro local.
    Devuelve el nuevo FamilyParameter compartido, o None si no encontró el local.
    """
    if grupo_param is None:
        grupo_param = GroupTypeId.Data
    fm = doc.FamilyManager
    encontrado = False
    for fp in fm.GetParameters():
        if fp.Definition.Name == nombre_param_local:
            fm.RemoveParameter(fp)
            encontrado = True
            break
    if not encontrado:
        return None
    return fm.AddParameter(definicion, grupo_param, es_instancia)


def renombrar_parametro_familia(doc, nombre_actual, nombre_nuevo):
    """
    Renombra un parámetro local de familia. No aplica a compartidos (GUID fijo).
    Devuelve True si tuvo éxito.
    """
    fm = doc.FamilyManager
    for fp in fm.GetParameters():
        if fp.Definition.Name == nombre_actual and not fp.IsShared:
            fm.RenameParameter(fp, nombre_nuevo)
            return True
    return False


# =============================================================================
#  6. UTILIDADES
# =============================================================================

def guid_de_parametro(doc, nombre_param):
    """
    Devuelve el GUID (str) del SharedParameterElement por nombre.
    Devuelve None si no se encuentra.
    """
    col = FilteredElementCollector(doc).OfClass(SharedParameterElement)
    for spe in col:
        if spe.Name == nombre_param:
            return str(spe.GuidValue)
    return None


def buscar_por_guid(doc, guid_str):
    """
    Devuelve el SharedParameterElement con ese GUID, o None.
    guid_str: string con formato '00000000-0000-0000-0000-000000000000'
    """
    guid = System.Guid(guid_str)
    return SharedParameterElement.Lookup(doc, guid)


def listar_parametros_compartidos_en_documento(doc):
    """
    Lista todos los SharedParameterElement presentes en el documento.

    Devuelve lista de dicts: {nombre, guid, id_elemento}
    """
    col = FilteredElementCollector(doc).OfClass(SharedParameterElement)
    return [
        {
            "nombre": spe.Name,
            "guid": str(spe.GuidValue),
            "id_elemento": spe.Id.IntegerValue,
        }
        for spe in col
    ]


def flujo_completo_compartido(app, doc, ruta_txt, nombre_grupo,
                              nombre_param, spec_type_id,
                              lista_bic, es_instancia=True,
                              grupo_param=None, descripcion=""):
    """
    Flujo comprimido para uso en Dynamo:
      1. Apunta al .txt
      2. Crea o recupera el grupo
      3. Crea o recupera la definición
      4. Vincula al proyecto para las categorías dadas
      5. Devuelve la ExternalDefinition

    Uso típico en Dynamo:
        import lib_parametros
        defn = lib_parametros.flujo_completo_compartido(
            app, doc,
            r"C:\BIM\compartidos.txt",
            "ASCH - Datos",
            "ASCH_CodigoObra",
            SpecTypeId.String.Text,
            [BuiltInCategory.OST_Walls, BuiltInCategory.OST_Floors],
        )
    """
    if grupo_param is None:
        grupo_param = GroupTypeId.Data
    df = establecer_archivo_compartidos(app, ruta_txt)
    if df is None:
        raise IOError("No se pudo abrir el archivo: " + ruta_txt)
    grupo = crear_grupo(df, nombre_grupo)
    defn = crear_definicion(grupo, nombre_param, spec_type_id,
                            descripcion=descripcion)
    vincular_a_proyecto(doc, app, defn, lista_bic, es_instancia, grupo_param)
    return defn


# =============================================================================
#  6. PARÁMETROS LOCALES EN FAMILYMANAGER (no compartidos)
# =============================================================================

def crear_parametro_local_familia(doc, nombre, spec_type_id=None,
                                   grupo_param=None, es_instancia=True):
    """
    Crea un parámetro local (no compartido) en la familia activa.

    spec_type_id: ForgeTypeId de SpecTypeId (por defecto SpecTypeId.String.Text)
    grupo_param : GroupTypeId (por defecto GroupTypeId.Data)
    Devuelve el FamilyParameter creado, o None si ya existe.
    """
    if spec_type_id is None:
        spec_type_id = SpecTypeId.String.Text
    if grupo_param is None:
        grupo_param = GroupTypeId.Data
    fm = doc.FamilyManager
    for fp in fm.GetParameters():
        if fp.Definition.Name == nombre:
            return fp
    return fm.AddParameter(nombre, grupo_param, spec_type_id, es_instancia)


def eliminar_parametro_local_familia(doc, nombre):
    """
    Elimina un parámetro local de la familia activa.
    No funciona con parámetros compartidos (usa quitar_de_familia para esos).
    Devuelve True si se eliminó.
    """
    fm = doc.FamilyManager
    for fp in fm.GetParameters():
        if fp.Definition.Name == nombre and not fp.IsShared:
            fm.RemoveParameter(fp)
            return True
    return False


def obtener_tipos_familia_manager(doc):
    """
    Lista todos los FamilyType del FamilyManager con sus parámetros y valores.

    Devuelve lista de dicts: {nombre_tipo, parametros: {nombre: valor}}
    """
    fm = doc.FamilyManager
    params = list(fm.GetParameters())
    resultado = []
    for ft in fm.Types:
        vals = {}
        for fp in params:
            try:
                p = ft.AsValueString(fp)
                if p is None:
                    p = ft.AsString(fp)
                vals[fp.Definition.Name] = p
            except Exception:
                vals[fp.Definition.Name] = None
        resultado.append({"nombre_tipo": ft.Name, "parametros": vals})
    return resultado


# =============================================================================
#  7. FÓRMULAS EN FAMILYMANAGER
# =============================================================================

def establecer_formula_parametro(doc, nombre_param, formula):
    """
    Asigna una fórmula a un parámetro del FamilyManager.

    formula: string con la fórmula, ej. "Ancho * 2" o "if(Alto > 1000 mm, 1, 0)"
             Pasar None o "" para borrar la fórmula.
    Devuelve True si se aplicó.
    """
    fm = doc.FamilyManager
    for fp in fm.GetParameters():
        if fp.Definition.Name == nombre_param:
            fm.SetFormula(fp, formula if formula else None)
            return True
    return False


def leer_formula_parametro(doc, nombre_param):
    """
    Devuelve la fórmula del parámetro como string, o None si no tiene fórmula.
    """
    fm = doc.FamilyManager
    for fp in fm.GetParameters():
        if fp.Definition.Name == nombre_param:
            return fp.Formula
    return None


def borrar_formula_parametro(doc, nombre_param):
    """
    Elimina la fórmula de un parámetro (queda como valor libre).
    Devuelve True si se eliminó.
    """
    return establecer_formula_parametro(doc, nombre_param, None)


def listar_parametros_con_formula(doc):
    """
    Devuelve lista de dicts {nombre, formula} para todos los parámetros
    del FamilyManager que tienen fórmula asignada.
    """
    fm = doc.FamilyManager
    return [
        {"nombre": fp.Definition.Name, "formula": fp.Formula}
        for fp in fm.GetParameters()
        if fp.Formula
    ]


# =============================================================================
#  8. ANIDAR PARÁMETROS (AssociateElementParameterToFamilyParameter)
# =============================================================================

def anidar_parametro(doc, instancia_anidada, nombre_param_inst,
                     nombre_param_familia):
    """
    Asocia el parámetro de una instancia de familia anidada al parámetro
    del FamilyManager de la familia padre (Family Editor).

    instancia_anidada  : FamilyInstance de la familia anidada
    nombre_param_inst  : nombre del parámetro en la instancia anidada
    nombre_param_familia: nombre del FamilyParameter en el FamilyManager padre

    Devuelve True si se asoció correctamente.
    """
    fm = doc.FamilyManager
    fp_padre = None
    for fp in fm.GetParameters():
        if fp.Definition.Name == nombre_param_familia:
            fp_padre = fp
            break
    if fp_padre is None:
        return False
    param = instancia_anidada.LookupParameter(nombre_param_inst)
    if param is None:
        return False
    fm.AssociateElementParameterToFamilyParameter(param, fp_padre)
    return True


def desanidar_parametro(doc, instancia_anidada, nombre_param_inst):
    """
    Elimina la asociación de un parámetro de instancia anidada con el
    FamilyParameter padre. Lo deja como parámetro independiente.
    Devuelve True si se desasocio.
    """
    param = instancia_anidada.LookupParameter(nombre_param_inst)
    if param is None:
        return False
    doc.FamilyManager.DissociateElementParameterFromFamilyParameter(param)
    return True


def obtener_parametros_anidados(doc, instancia_anidada):
    """
    Lista los parámetros de la instancia anidada que están asociados
    a algún FamilyParameter del padre.

    Devuelve lista de dicts: {nombre_param_inst, nombre_param_familia}
    """
    fm = doc.FamilyManager
    fp_por_id = {fp.Id: fp.Definition.Name for fp in fm.GetParameters()}
    resultado = []
    for param in instancia_anidada.Parameters:
        if param.AssociatedFamilyParameter is not None:
            afp = param.AssociatedFamilyParameter
            resultado.append({
                "nombre_param_inst": param.Definition.Name,
                "nombre_param_familia": afp.Definition.Name,
            })
    return resultado


# =============================================================================
#  9. COTAS Y FAMILYLABEL
# =============================================================================

def asignar_parametro_a_cota(doc, cota, nombre_param):
    """
    Asigna un FamilyParameter del FamilyManager como label de una cota.

    Esto crea la relación que permite controlar la geometría mediante el
    parámetro: cuando el usuario cambia el parámetro, la cota (y la
    geometría asociada) se actualiza.

    cota       : objeto Dimension en el Family Editor
    nombre_param: nombre del FamilyParameter
    Devuelve True si se asignó.
    """
    fm = doc.FamilyManager
    for fp in fm.GetParameters():
        if fp.Definition.Name == nombre_param:
            cota.FamilyLabel = fp
            return True
    return False


def quitar_label_de_cota(cota):
    """Elimina el FamilyLabel de una cota (queda como cota de referencia)."""
    cota.FamilyLabel = None


def obtener_label_de_cota(cota):
    """Devuelve el nombre del FamilyParameter asignado a la cota, o None."""
    if cota.FamilyLabel is not None:
        return cota.FamilyLabel.Definition.Name
    return None


# =============================================================================
# 10. TIPOS DE FAMILIA (FamilyManager)
# =============================================================================

def crear_tipo_familia(doc, nombre_tipo):
    """
    Crea un nuevo FamilyType en el FamilyManager activo.
    Si ya existe lo devuelve sin duplicar.
    Devuelve el FamilyType creado.
    """
    fm = doc.FamilyManager
    for ft in fm.Types:
        if ft.Name == nombre_tipo:
            return ft
    return fm.NewType(nombre_tipo)


def eliminar_tipo_familia(doc, nombre_tipo):
    """
    Elimina un FamilyType del FamilyManager.
    Devuelve True si se eliminó.
    """
    fm = doc.FamilyManager
    for ft in fm.Types:
        if ft.Name == nombre_tipo:
            fm.DeleteCurrentType()
            return True
    return False


def renombrar_tipo_familia(doc, nombre_actual, nombre_nuevo):
    """
    Renombra un FamilyType. Devuelve True si se renombró.
    """
    fm = doc.FamilyManager
    for ft in fm.Types:
        if ft.Name == nombre_actual:
            fm.CurrentType = ft
            fm.RenameCurrentType(nombre_nuevo)
            return True
    return False


def duplicar_tipo_familia(doc, nombre_origen, nombre_nuevo):
    """
    Duplica un FamilyType con un nombre nuevo.
    Devuelve el nuevo FamilyType.
    """
    fm = doc.FamilyManager
    for ft in fm.Types:
        if ft.Name == nombre_origen:
            fm.CurrentType = ft
            return fm.NewType(nombre_nuevo)
    return None


def activar_tipo_familia_manager(doc, nombre_tipo):
    """
    Establece el FamilyType activo en el FamilyManager.
    Devuelve True si se activó.
    """
    fm = doc.FamilyManager
    for ft in fm.Types:
        if ft.Name == nombre_tipo:
            fm.CurrentType = ft
            return True
    return False


def obtener_tipo_activo_familia_manager(doc):
    """Devuelve el nombre del FamilyType activo en el FamilyManager."""
    ft = doc.FamilyManager.CurrentType
    return ft.Name if ft is not None else None


def establecer_valor_en_tipo(doc, nombre_tipo, nombre_param, valor):
    """
    Establece el valor de un parámetro en un FamilyType específico.
    Activa el tipo, asigna el valor y restaura el tipo anterior.
    """
    fm = doc.FamilyManager
    tipo_anterior = fm.CurrentType
    activar_tipo_familia_manager(doc, nombre_tipo)
    for fp in fm.GetParameters():
        if fp.Definition.Name == nombre_param:
            try:
                if isinstance(valor, float):
                    fm.Set(fp, valor)
                elif isinstance(valor, int):
                    fm.Set(fp, valor)
                elif isinstance(valor, str):
                    fm.Set(fp, valor)
            except Exception:
                pass
            break
    if tipo_anterior is not None:
        fm.CurrentType = tipo_anterior


# =============================================================================
# 11. PARÁMETROS GLOBALES DE PROYECTO (GlobalParameter)
# =============================================================================

def crear_parametro_global(doc, nombre, spec_type_id=None):
    """
    Crea un GlobalParameter en el proyecto.

    spec_type_id: ForgeTypeId de SpecTypeId (por defecto SpecTypeId.String.Text)
    Devuelve el GlobalParameter creado, o el existente si ya hay uno con ese nombre.
    """
    if spec_type_id is None:
        spec_type_id = SpecTypeId.String.Text
    existente = obtener_parametro_global(doc, nombre)
    if existente is not None:
        return existente
    return GlobalParameter.Create(doc, nombre, spec_type_id)


def obtener_parametros_globales(doc):
    """
    Devuelve lista de todos los GlobalParameter del proyecto.
    """
    ids = GlobalParameter.GetAllGlobalParameters(doc)
    return [doc.GetElement(eid) for eid in ids]


def obtener_parametro_global(doc, nombre):
    """Devuelve el GlobalParameter con ese nombre, o None."""
    for eid in GlobalParameter.GetAllGlobalParameters(doc):
        gp = doc.GetElement(eid)
        if gp.Name == nombre:
            return gp
    return None


def establecer_valor_global(gp, valor):
    """
    Asigna el valor a un GlobalParameter.
    Detecta automáticamente el tipo: str, float, int o ElementId.
    """
    if isinstance(valor, str):
        gp.SetValue(StringParameterValue(valor))
    elif isinstance(valor, float):
        gp.SetValue(DoubleParameterValue(valor))
    elif isinstance(valor, int):
        gp.SetValue(IntegerParameterValue(valor))
    else:
        gp.SetValue(ElementIdParameterValue(valor))


def obtener_valor_global(gp):
    """
    Lee el valor de un GlobalParameter como tipo Python nativo.
    """
    val = gp.GetValue()
    if val is None:
        return None
    if hasattr(val, "Value"):
        return val.Value
    return val


def eliminar_parametro_global(doc, nombre):
    """
    Elimina un GlobalParameter del proyecto por nombre.
    Devuelve True si se eliminó.
    """
    gp = obtener_parametro_global(doc, nombre)
    if gp is None:
        return False
    doc.Delete(gp.Id)
    return True


def listar_parametros_globales(doc):
    """
    Lista todos los GlobalParameter del proyecto con nombre y valor.
    Devuelve lista de dicts: {nombre, valor, spec_type}
    """
    resultado = []
    for gp in obtener_parametros_globales(doc):
        resultado.append({
            "nombre": gp.Name,
            "valor": obtener_valor_global(gp),
            "spec_type": str(gp.GetDefinition().GetDataType()),
        })
    return resultado


def asociar_elemento_a_global(doc, elemento, nombre_param, gp):
    """
    Asocia el parámetro de instancia de un elemento a un GlobalParameter
    del proyecto (Revit 2022+, usa ParameterUtils).

    elemento    : Element del proyecto
    nombre_param: nombre del parámetro de instancia
    gp          : GlobalParameter

    Devuelve True si se asoció.
    """
    param = elemento.LookupParameter(nombre_param)
    if param is None:
        return False
    return ParameterUtils.AssociateElementParameterToGlobalParameter(
        doc, elemento.Id, param.Id, gp.Id
    )


def desasociar_elemento_de_global(doc, elemento, nombre_param):
    """
    Elimina la asociación entre el parámetro de instancia y cualquier
    GlobalParameter. Devuelve True si se desasoció.
    """
    param = elemento.LookupParameter(nombre_param)
    if param is None:
        return False
    return ParameterUtils.DissociateElementParameterFromGlobalParameter(
        doc, elemento.Id, param.Id
    )


def esta_asociado_a_global(elemento, nombre_param):
    """True si el parámetro está asociado a un GlobalParameter."""
    param = elemento.LookupParameter(nombre_param)
    if param is None:
        return False
    return ParameterUtils.IsParameterAssociatedWithGlobalParameter(param.Id)


# =============================================================================
# 12. EXTENSIBLE STORAGE (Schema + Entity)
# =============================================================================

def crear_schema(guid_str, nombre_schema, descripcion="",
                 lectura_publica=True, escritura_propia=True):
    """
    Crea o recupera un Schema de ExtensibleStorage.

    guid_str : GUID único del schema en formato '00000000-...'
    Devuelve el Schema.
    """
    from Autodesk.Revit.DB.ExtensibleStorage import Schema
    guid = System.Guid(guid_str)
    schema = Schema.Lookup(guid)
    if schema is not None:
        return schema
    sb = SchemaBuilder(guid)
    sb.SetSchemaName(nombre_schema)
    if descripcion:
        sb.SetDocumentation(descripcion)
    sb.SetReadAccessLevel(AccessLevel.Public if lectura_publica else AccessLevel.Vendor)
    sb.SetWriteAccessLevel(AccessLevel.Application if escritura_propia else AccessLevel.Public)
    return sb.Finish()


def agregar_campo_schema(schema_builder, nombre_campo, tipo_clr):
    """
    Añade un campo simple al SchemaBuilder antes de llamar a Finish().

    tipo_clr: tipo CLR, ej. System.String, System.Double, System.Int32
    Devuelve el FieldBuilder.
    """
    return schema_builder.AddSimpleField(nombre_campo, tipo_clr)


def escribir_datos_extensibles(elemento, schema, datos_dict):
    """
    Escribe datos en un elemento mediante ExtensibleStorage.

    datos_dict: {nombre_campo: valor}  — los valores deben coincidir
                con el tipo definido en el Schema.
    """
    entity = Entity(schema)
    for nombre, valor in datos_dict.items():
        field = schema.GetField(nombre)
        if field is not None:
            entity.Set(field, valor)
    elemento.SetEntity(entity)


def leer_datos_extensibles(elemento, schema):
    """
    Lee datos de ExtensibleStorage de un elemento.
    Devuelve dict {nombre_campo: valor} o {} si no hay datos del schema.
    """
    entity = elemento.GetEntity(schema)
    if not entity.IsValid():
        return {}
    resultado = {}
    for field in schema.ListFields():
        try:
            resultado[field.FieldName] = entity.Get(field)
        except Exception:
            resultado[field.FieldName] = None
    return resultado


def eliminar_datos_extensibles(elemento, schema):
    """
    Elimina los datos de ExtensibleStorage de un elemento para el schema dado.
    """
    elemento.DeleteEntity(schema)


def tiene_datos_extensibles(elemento, schema):
    """True si el elemento tiene datos del schema indicado."""
    return elemento.GetEntity(schema).IsValid()
