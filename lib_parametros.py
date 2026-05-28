# -*- coding: utf-8 -*-
"""
lib_parametros.py — Gestión de parámetros compartidos en Revit

Cubre el ciclo completo:
  1. Archivo .txt  →  establecer ruta, abrir, volcar contenido
  2. Grupos        →  listar, obtener, crear
  3. Definiciones  →  listar, obtener, crear (por tipo de dato)
  4. Proyecto      →  vincular / actualizar / desvincular / consultar
  5. Familias      →  agregar, quitar, listar, convertir de local a compartido
  6. Utilidades    →  buscar por GUID, listar todo

Requiere Revit 2022+ (usa SpecTypeId / GroupTypeId en lugar de los enums
deprecados ParameterType / BuiltInParameterGroup).
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
