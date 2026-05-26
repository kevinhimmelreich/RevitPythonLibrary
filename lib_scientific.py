# -*- coding: utf-8 -*-
"""
lib_scientific.py
Integracion Revit API <-> Python cientifico
pandas, numpy, scipy, matplotlib, shapely, networkx
Compatible: CPython 3.x (Dynamo 2.13+) | Revit 2024-2026
NOTA: IronPython 2.7 no soporta estas bibliotecas. En IronPython todas
las funciones devuelven None con un aviso. En CPython, si una biblioteca
no esta instalada, se instala automaticamente via pip al llamar la funcion.
Las funciones matplotlib retornan System.Drawing.Bitmap directamente
usable en Dynamo (Watch Image), o guardan a PNG si se pasa ruta_png.
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
    FilteredElementCollector, ElementId, ViewSchedule, SectionType,
    StorageType, UnitUtils, UnitTypeId, XYZ,
    SpatialElementBoundaryOptions
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


# ── Helpers internos ─────────────────────────────────────────────────────────

def _pies_a_m(v):
    return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.Meters)


def _m_a_pies(v):
    return UnitUtils.ConvertToInternalUnits(v, UnitTypeId.Meters)


def _id_int(element_id):
    try:
        return int(element_id.Value)
    except AttributeError:
        return element_id.IntegerValue


def _val_param(param):
    if param is None:
        return None
    t = param.StorageType
    if t == StorageType.String:
        return param.AsString()
    if t == StorageType.Integer:
        return param.AsInteger()
    if t == StorageType.Double:
        return param.AsDouble()
    if t == StorageType.ElementId:
        return _id_int(param.AsElementId())
    return None


def _iniciar(nombre="Transaccion"):
    TransactionManager.Instance.EnsureInTransaction(doc)


def _finalizar():
    TransactionManager.Instance.TransactionTaskDone()


def _asegurar(paquete, nombre_import=None):
    """
    Comprueba si un paquete Python esta disponible e intenta instalarlo
    automaticamente via pip si no lo esta.
    Solo funciona en CPython 3.x (Dynamo 2.13+); en IronPython 2.7
    devuelve False directamente.

    Args:
        paquete: nombre del paquete para pip (ej. "Pillow", "scipy")
        nombre_import: nombre del modulo para import cuando difiere
                       del nombre pip (ej. "PIL" para "Pillow").
                       Si None se usa paquete.

    Returns:
        True si el paquete esta disponible o se instalo correctamente,
        False en caso contrario.
    """
    nombre_import = nombre_import or paquete
    try:
        __import__(nombre_import)
        return True
    except ImportError:
        pass
    if not PY3:
        print(paquete + " no disponible en IronPython 2.7.")
        return False
    import subprocess
    print("Instalando " + paquete + " via pip...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", paquete],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=120
        )
        __import__(nombre_import)
        print(paquete + " instalado correctamente.")
        return True
    except Exception as exc:
        print("Error instalando " + paquete + ": " + str(exc))
        return False


def instalar_dependencias_scientific():
    """
    Instala todas las dependencias de lib_scientific usando pip.
    Llamar una vez al inicio en un entorno nuevo (CPython 3.x / Dynamo).
    En IronPython 2.7 no hace nada.

    Returns:
        dict {paquete: bool} indicando si cada paquete esta disponible

    Ejemplo en Dynamo:
        from lib_scientific import instalar_dependencias_scientific
        OUT = [instalar_dependencias_scientific()]
        # {"numpy": True, "pandas": True, "scipy": True, ...}
    """
    dependencias = [
        ("numpy",      "numpy"),
        ("pandas",     "pandas"),
        ("scipy",      "scipy"),
        ("matplotlib", "matplotlib"),
        ("shapely",    "shapely"),
        ("networkx",   "networkx"),
        ("Pillow",     "PIL"),
    ]
    return {pkg: _asegurar(pkg, imp) for pkg, imp in dependencias}


# ── matplotlib: conversion a Bitmap para Dynamo ──────────────────────────────

def figura_a_bitmap(fig):
    """
    Convierte una figura matplotlib a System.Drawing.Bitmap para
    visualizarla directamente en un nodo Watch Image de Dynamo.
    Basado en el patron plt2arr + convertToBitmap2 de Dynamo Python.
    Pillow y numpy se instalan automaticamente si no estan presentes.

    Args:
        fig: figura matplotlib (matplotlib.figure.Figure)

    Returns:
        System.Drawing.Bitmap, o None si faltan dependencias

    Requiere: CPython 3.x (Dynamo 2.13+), Pillow, numpy
    """
    if not _asegurar("numpy") or not _asegurar("Pillow", "PIL"):
        return None
    try:
        import System
        clr.AddReference("System.Drawing")
        from System.Drawing import Bitmap
        from System.IO import MemoryStream
    except Exception:
        print("System.Drawing no disponible (solo Dynamo / .NET).")
        return None
    import numpy as np
    import io as _io
    import PIL.Image
    fig.canvas.draw()
    rgba = fig.canvas.buffer_rgba()
    w, h = fig.canvas.get_width_height()
    arr = np.frombuffer(rgba, dtype=np.uint8).reshape((h, w, 4))
    img = PIL.Image.fromarray(arr[:, :, :3], "RGB")
    buf = _io.BytesIO()
    img.save(buf, format="BMP")
    net_bytes = System.Array[System.Byte](buf.getvalue())
    with MemoryStream(net_bytes) as ms:
        return Bitmap(ms)


def _cerrar_fig(fig, ruta_png):
    """
    Si ruta_png esta definida guarda la figura a disco y devuelve la ruta.
    Si no, convierte la figura a Bitmap para Dynamo y la devuelve.
    Cierra la figura en ambos casos.
    """
    import matplotlib.pyplot as plt
    if ruta_png:
        fig.savefig(ruta_png, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return ruta_png
    resultado = figura_a_bitmap(fig)
    plt.close(fig)
    return resultado


# ── pandas <-> Revit API ─────────────────────────────────────────────────────

def elementos_a_dataframe(elementos, parametros):
    """
    Exporta parametros de cualquier lista de elementos Revit a un
    pandas DataFrame. Base para cualquier analisis de datos del modelo.
    pandas se instala automaticamente si no esta disponible.

    Args:
        elementos: lista de elementos Revit
        parametros: lista de nombres de parametros a incluir

    Returns:
        DataFrame con columnas [ElementId, Categoria, Nivel, *params]
        o None si pandas no esta disponible

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("pandas"):
        return None
    import pandas as pd
    filas = []
    for elem in elementos:
        try:
            eid = _id_int(elem.Id)
        except Exception:
            continue
        p_nivel = elem.LookupParameter("Nivel de referencia")
        fila = {
            "ElementId": eid,
            "Categoria": (
                elem.Category.Name if elem.Category else ""
            ),
            "Nivel": (
                p_nivel.AsValueString() if p_nivel else ""
            ),
        }
        for nombre in parametros:
            fila[nombre] = _val_param(elem.LookupParameter(nombre))
        filas.append(fila)
    return pd.DataFrame(filas)


def dataframe_a_parametros(df, col_id="ElementId", cols_ignorar=None):
    """
    Aplica los valores de un DataFrame a los parametros de los elementos
    Revit correspondientes. Inverso de elementos_a_dataframe.
    Permite flujos de trabajo editar-en-Excel -> aplicar-a-Revit.

    Args:
        df: pandas DataFrame con columna de ID y columnas de parametros
        col_id: columna con el ElementId (defecto "ElementId")
        cols_ignorar: conjunto adicional de columnas a no escribir

    Returns:
        dict {ok: [ids], error: [ids]}

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("pandas"):
        return None
    import pandas as pd
    ignorar = {"ElementId", "Categoria", "Nivel", col_id}
    if cols_ignorar:
        ignorar.update(cols_ignorar)
    cols = [c for c in df.columns if c not in ignorar]
    resultado = {"ok": [], "error": []}
    _iniciar("DataFrame a Revit")
    for _, fila in df.iterrows():
        try:
            elem = doc.GetElement(ElementId(int(fila[col_id])))
            if elem is None:
                resultado["error"].append(fila[col_id])
                continue
            for col in cols:
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
            resultado["ok"].append(int(fila[col_id]))
        except Exception as exc:
            resultado["error"].append(str(exc))
    _finalizar()
    return resultado


def schedule_a_dataframe(nombre_schedule):
    """
    Convierte una ViewSchedule de Revit en un pandas DataFrame.
    La primera fila se usa como cabecera de columnas.

    Args:
        nombre_schedule: nombre exacto de la ViewSchedule en Revit

    Returns:
        pandas DataFrame con los datos de la tabla, o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("pandas"):
        return None
    import pandas as pd
    colector = FilteredElementCollector(doc).OfClass(ViewSchedule)
    sch = next(
        (s for s in colector.ToElements()
         if s.Name == nombre_schedule),
        None
    )
    if sch is None:
        return None
    sec = sch.GetTableData().GetSectionData(SectionType.Body)
    filas = [
        [
            sch.GetCellText(SectionType.Body, row, col_i)
            for col_i in range(sec.NumberOfColumns)
        ]
        for row in range(sec.NumberOfRows)
    ]
    if len(filas) < 2:
        return pd.DataFrame()
    return pd.DataFrame(filas[1:], columns=filas[0])


def analisis_calidad_datos(elementos, parametros_requeridos):
    """
    Detecta elementos con parametros vacios o nulos. QA/QC del modelo.
    Devuelve solo los elementos incompletos con sus parametros faltantes.

    Args:
        elementos: lista de elementos Revit
        parametros_requeridos: lista de nombres de parametros obligatorios

    Returns:
        DataFrame con los elementos incompletos, o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    df = elementos_a_dataframe(elementos, parametros_requeridos)
    if df is None:
        return None
    mask = df[parametros_requeridos].isnull().any(axis=1)
    return df[mask].copy()


# ── numpy <-> Revit API ──────────────────────────────────────────────────────

def xyz_a_numpy(puntos_xyz):
    """
    Convierte una lista de XYZ de Revit a un array numpy (N, 3) en metros.
    numpy se instala automaticamente si no esta disponible.

    Args:
        puntos_xyz: lista de Autodesk.Revit.DB.XYZ

    Returns:
        numpy array shape (N, 3) en metros, o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("numpy"):
        return None
    import numpy as np
    return np.array(
        [[_pies_a_m(p.X), _pies_a_m(p.Y), _pies_a_m(p.Z)]
         for p in puntos_xyz]
    )


def numpy_a_xyz(arr_metros):
    """
    Convierte un array numpy (N, 3) en metros a una lista de XYZ Revit
    en unidades internas (pies).

    Args:
        arr_metros: numpy array de shape (N, 3) en metros

    Returns:
        lista de Autodesk.Revit.DB.XYZ, o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("numpy"):
        return None
    return [
        XYZ(_m_a_pies(float(row[0])),
            _m_a_pies(float(row[1])),
            _m_a_pies(float(row[2])))
        for row in arr_metros
    ]


def posiciones_elementos_numpy(elementos):
    """
    Extrae las posiciones (LocationPoint) de una lista de elementos Revit
    como array numpy (N, 3) en metros.

    Args:
        elementos: lista de elementos Revit con LocationPoint

    Returns:
        numpy array (N, 3) en metros, o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("numpy"):
        return None
    import numpy as np
    puntos = []
    for elem in elementos:
        loc = elem.Location
        if hasattr(loc, "Point"):
            p = loc.Point
            puntos.append(
                [_pies_a_m(p.X), _pies_a_m(p.Y), _pies_a_m(p.Z)]
            )
    return np.array(puntos) if puntos else np.empty((0, 3))


def centroide_nube(puntos_xyz):
    """
    Calcula el centroide de una nube de XYZ de Revit y lo devuelve
    como un nuevo XYZ en unidades internas (pies).

    Args:
        puntos_xyz: lista de Autodesk.Revit.DB.XYZ

    Returns:
        XYZ del centroide, o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    arr = xyz_a_numpy(puntos_xyz)
    if arr is None or len(arr) == 0:
        return None
    c = arr.mean(axis=0)
    return XYZ(
        _m_a_pies(float(c[0])),
        _m_a_pies(float(c[1])),
        _m_a_pies(float(c[2]))
    )


# ── scipy <-> Revit API ──────────────────────────────────────────────────────

def clustering_por_posicion(elementos, n_grupos):
    """
    Agrupa elementos por proximidad espacial usando K-Means (scipy).
    Util para zonar automaticamente elementos por area o planta.
    scipy se instala automaticamente si no esta disponible.

    Args:
        elementos: lista de elementos Revit con LocationPoint
        n_grupos: numero de grupos a generar

    Returns:
        dict {grupo_id: [elementos]} con los grupos resultantes,
        o None si scipy no esta disponible

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("scipy"):
        return None
    from scipy.cluster.vq import kmeans2
    arr = posiciones_elementos_numpy(elementos)
    if arr is None or len(arr) < n_grupos:
        return None
    std = arr.std(axis=0)
    std[std == 0] = 1
    arr_norm = arr / std
    _, etiquetas = kmeans2(arr_norm, n_grupos, minit="points")
    grupos = {}
    for elem, etiq in zip(elementos, etiquetas):
        grupos.setdefault(int(etiq), []).append(elem)
    return grupos


def clustering_por_parametros(elementos, nombres_params, n_grupos):
    """
    Agrupa elementos segun los valores numericos de sus parametros usando
    K-Means. Complementa clustering_por_posicion cuando lo relevante no
    es la posicion sino las propiedades del elemento (area, espesor,
    diametro, longitud, etc.).

    Ejemplos de uso:
        - Agrupar muros por espesor y altura
        - Agrupar tuberias por diametro y longitud
        - Agrupar habitaciones por area y perimetro

    Args:
        elementos: lista de elementos Revit
        nombres_params: lista de nombres de parametros numericos
        n_grupos: numero de grupos a generar

    Returns:
        dict {grupo_id: [elementos]} con los grupos resultantes,
        o None si faltan dependencias o datos

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("scipy") or not _asegurar("numpy"):
        return None
    from scipy.cluster.vq import kmeans2
    import numpy as np
    filas = []
    validos = []
    for elem in elementos:
        valores = []
        ok = True
        for nombre in nombres_params:
            v = _val_param(elem.LookupParameter(nombre))
            if v is None or not isinstance(v, (int, float)):
                ok = False
                break
            valores.append(float(v))
        if ok:
            filas.append(valores)
            validos.append(elem)
    if len(filas) < n_grupos:
        return None
    arr = np.array(filas)
    std = arr.std(axis=0)
    std[std == 0] = 1
    _, etiquetas = kmeans2(arr / std, n_grupos, minit="points")
    grupos = {}
    for elem, etiq in zip(validos, etiquetas):
        grupos.setdefault(int(etiq), []).append(elem)
    return grupos


def vecinos_por_radio(elementos, radio_m):
    """
    Para cada elemento devuelve los elementos vecinos dentro de un radio.
    Usa un KD-Tree (scipy) para busqueda eficiente en 2D (planta).
    Util para detectar conflictos de espacio o proximidad entre MEP.
    scipy se instala automaticamente si no esta disponible.

    Args:
        elementos: lista de elementos Revit con LocationPoint
        radio_m: radio de busqueda en metros

    Returns:
        dict {ElementId: [ElementId vecinos]}, o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("scipy"):
        return None
    from scipy.spatial import KDTree
    arr = posiciones_elementos_numpy(elementos)
    if arr is None or len(arr) == 0:
        return None
    arbol = KDTree(arr[:, :2])
    ids = [_id_int(e.Id) for e in elementos]
    resultado = {}
    for i, eid in enumerate(ids):
        indices = arbol.query_ball_point(arr[i, :2], radio_m)
        resultado[eid] = [ids[j] for j in indices if j != i]
    return resultado


def interpolacion_parametro(
        elementos, param_eje_x, param_eje_y, valores_x):
    """
    Interpola valores de un parametro en funcion de otro usando scipy.
    Ejemplo: temperatura en funcion de la altura de nivel, o caudal
    en funcion del diametro de tuberia.

    Args:
        elementos: lista de elementos Revit
        param_eje_x: nombre del parametro que actua como eje X
        param_eje_y: nombre del parametro a interpolar (eje Y)
        valores_x: lista de valores X donde interpolar

    Returns:
        numpy array con los valores Y interpolados, o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("scipy") or not _asegurar("numpy"):
        return None
    from scipy.interpolate import interp1d
    import numpy as np
    xs, ys = [], []
    for elem in elementos:
        px = elem.LookupParameter(param_eje_x)
        py = elem.LookupParameter(param_eje_y)
        if px and py:
            xs.append(_val_param(px))
            ys.append(_val_param(py))
    if len(xs) < 2:
        return None
    xs_arr = np.array(xs, dtype=float)
    ys_arr = np.array(ys, dtype=float)
    orden = xs_arr.argsort()
    fn = interp1d(
        xs_arr[orden], ys_arr[orden],
        kind="linear", fill_value="extrapolate"
    )
    return fn(np.array(valores_x, dtype=float))


# ── matplotlib <-> Revit API ─────────────────────────────────────────────────
# Todas las funciones retornan System.Drawing.Bitmap si ruta_png es None,
# o guardan a disco y devuelven la ruta si ruta_png esta definida.
# Usar OUT = [bitmap] en Dynamo para visualizar con Watch Image.

def limpiar_ejes(ax):
    """
    Elimina bordes superior y derecho del eje para un estilo limpio.
    Util antes de exportar graficos de calidad para informes BIM.

    Args:
        ax: objeto matplotlib Axes

    Returns:
        ax modificado (in-place)
    """
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.yaxis.set_ticks_position("left")
    ax.xaxis.set_ticks_position("bottom")
    return ax


def grafico_parametro_por_nivel(
        elementos, nombre_param, ruta_png=None,
        titulo=None, color="steelblue"):
    """
    Grafico de barras con el valor medio de un parametro numerico
    agrupado por nivel de Revit.
    matplotlib y pandas se instalan automaticamente si no estan presentes.

    Args:
        elementos: lista de elementos Revit
        nombre_param: nombre del parametro numerico a graficar
        ruta_png: ruta .png de salida (si None devuelve Bitmap)
        titulo: titulo del grafico (opcional)
        color: color de las barras (defecto "steelblue")

    Returns:
        Bitmap para Dynamo, ruta_png o None si falta dependencia

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("matplotlib") or not _asegurar("pandas"):
        return None
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd
    df = elementos_a_dataframe(elementos, [nombre_param])
    if df is None or nombre_param not in df.columns:
        return None
    df[nombre_param] = pd.to_numeric(
        df[nombre_param], errors="coerce"
    )
    agrupado = df.groupby("Nivel")[nombre_param].mean().dropna()
    fig, ax = plt.subplots(figsize=(10, 5))
    agrupado.plot(kind="bar", ax=ax, color=color)
    ax.set_title(
        titulo or ("Media de " + nombre_param + " por nivel")
    )
    ax.set_xlabel("Nivel")
    ax.set_ylabel(nombre_param)
    ax.tick_params(axis="x", rotation=45)
    limpiar_ejes(ax)
    fig.tight_layout()
    return _cerrar_fig(fig, ruta_png)


def histograma_parametro(
        elementos, nombre_param, ruta_png=None,
        bins=20, titulo=None, color="steelblue"):
    """
    Histograma de la distribucion de valores de un parametro numerico.
    Util para detectar outliers o verificar uniformidad del modelo.
    matplotlib y pandas se instalan automaticamente si no estan presentes.

    Args:
        elementos: lista de elementos Revit
        nombre_param: nombre del parametro numerico
        ruta_png: ruta .png de salida (si None devuelve Bitmap)
        bins: numero de intervalos (defecto 20)
        titulo: titulo del grafico (opcional)
        color: color de las barras

    Returns:
        Bitmap para Dynamo, ruta_png o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("matplotlib") or not _asegurar("pandas"):
        return None
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd
    df = elementos_a_dataframe(elementos, [nombre_param])
    if df is None:
        return None
    valores = pd.to_numeric(
        df[nombre_param], errors="coerce"
    ).dropna()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(valores, bins=bins, color=color, edgecolor="white")
    ax.set_title(titulo or ("Distribucion de " + nombre_param))
    ax.set_xlabel(nombre_param)
    ax.set_ylabel("Frecuencia")
    limpiar_ejes(ax)
    fig.tight_layout()
    return _cerrar_fig(fig, ruta_png)


def grafico_dispersion(
        elementos, param_x, param_y,
        ruta_png=None, titulo=None):
    """
    Grafico de dispersion (scatter) entre dos parametros numericos.
    Permite detectar correlaciones entre propiedades de elementos Revit.
    matplotlib y pandas se instalan automaticamente si no estan presentes.

    Args:
        elementos: lista de elementos Revit
        param_x: nombre del parametro para el eje X
        param_y: nombre del parametro para el eje Y
        ruta_png: ruta .png de salida (si None devuelve Bitmap)
        titulo: titulo del grafico (opcional)

    Returns:
        Bitmap para Dynamo, ruta_png o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("matplotlib") or not _asegurar("pandas"):
        return None
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd
    df = elementos_a_dataframe(elementos, [param_x, param_y])
    if df is None:
        return None
    df[param_x] = pd.to_numeric(df[param_x], errors="coerce")
    df[param_y] = pd.to_numeric(df[param_y], errors="coerce")
    df = df.dropna(subset=[param_x, param_y])
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df[param_x], df[param_y], alpha=0.6)
    ax.set_xlabel(param_x)
    ax.set_ylabel(param_y)
    ax.set_title(titulo or (param_x + " vs " + param_y))
    limpiar_ejes(ax)
    fig.tight_layout()
    return _cerrar_fig(fig, ruta_png)


def grafico_suma_por_categoria(
        elementos, nombre_param, ruta_png=None, titulo=None):
    """
    Grafico de sectores (pie) con la suma de un parametro numerico
    agrupada por categoria de elemento Revit. Util para reportes de
    cantidades (m2 por categoria, longitud MEP por sistema, etc.).
    matplotlib y pandas se instalan automaticamente si no estan presentes.

    Args:
        elementos: lista de elementos Revit
        nombre_param: parametro numerico a sumar por categoria
        ruta_png: ruta .png de salida (si None devuelve Bitmap)
        titulo: titulo del grafico (opcional)

    Returns:
        Bitmap para Dynamo, ruta_png o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("matplotlib") or not _asegurar("pandas"):
        return None
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd
    df = elementos_a_dataframe(elementos, [nombre_param])
    if df is None:
        return None
    df[nombre_param] = pd.to_numeric(
        df[nombre_param], errors="coerce"
    )
    resumen = df.groupby("Categoria")[nombre_param].sum().dropna()
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(resumen, labels=resumen.index, autopct="%1.1f%%")
    ax.set_title(titulo or (nombre_param + " por categoria"))
    fig.tight_layout()
    return _cerrar_fig(fig, ruta_png)


def scatter_elementos_coloreados(
        elementos, param_x, param_y,
        param_color=None, titulo=None,
        cmap="viridis", ruta_png=None):
    """
    Scatter donde el COLOR de cada punto esta mapeado al valor de un
    tercer parametro de Revit. Permite visualizar tres variables del
    modelo en un solo grafico con barra de color continua.

    Ejemplo: tuberias con eje X=longitud, eje Y=diametro,
    color=presion -> detecta relaciones ocultas entre propiedades MEP.

    Args:
        elementos: lista de elementos Revit
        param_x: nombre del parametro para el eje X
        param_y: nombre del parametro para el eje Y
        param_color: nombre del parametro para el color (opcional)
        titulo: titulo del grafico (opcional)
        cmap: colormap matplotlib (defecto "viridis")
        ruta_png: ruta .png de salida (si None devuelve Bitmap)

    Returns:
        Bitmap para Dynamo, ruta_png o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("matplotlib") or not _asegurar("pandas"):
        return None
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import pandas as pd
    cols = [param_x, param_y]
    if param_color:
        cols.append(param_color)
    df = elementos_a_dataframe(elementos, cols)
    if df is None:
        return None
    df[param_x] = pd.to_numeric(df[param_x], errors="coerce")
    df[param_y] = pd.to_numeric(df[param_y], errors="coerce")
    if param_color:
        df[param_color] = pd.to_numeric(
            df[param_color], errors="coerce"
        )
    df = df.dropna(subset=[param_x, param_y])
    fig, ax = plt.subplots(figsize=(9, 6))
    if param_color and param_color in df.columns:
        sc = ax.scatter(
            df[param_x], df[param_y],
            c=df[param_color], cmap=cmap, alpha=0.7
        )
        plt.colorbar(sc, ax=ax, label=param_color)
    else:
        ax.scatter(df[param_x], df[param_y], alpha=0.7)
    ax.set_xlabel(param_x)
    ax.set_ylabel(param_y)
    ax.set_title(titulo or (param_x + " vs " + param_y))
    limpiar_ejes(ax)
    fig.tight_layout()
    return _cerrar_fig(fig, ruta_png)


def mapa_calor_planta(
        habitaciones, nombre_param,
        ruta_png=None, titulo=None, cmap="YlOrRd"):
    """
    Genera un mapa de calor de la planta del edificio coloreando cada
    habitacion segun el valor de un parametro numerico. Combina shapely
    (para los contornos del modelo) con matplotlib (visualizacion).

    Ideal para representar areas, ocupacion, temperatura, iluminacion
    u otros KPI directamente sobre la planta del edificio.
    matplotlib, numpy y shapely se instalan automaticamente si faltan.

    Args:
        habitaciones: lista de Room de Revit
        nombre_param: parametro numerico a mapear como color
        ruta_png: ruta .png de salida (si None devuelve Bitmap)
        titulo: titulo del grafico (opcional)
        cmap: colormap matplotlib (defecto "YlOrRd")

    Returns:
        Bitmap para Dynamo, ruta_png o None

    Requiere: CPython 3.x (Dynamo 2.13+), shapely, matplotlib
    """
    if (not _asegurar("matplotlib")
            or not _asegurar("numpy")
            or not _asegurar("shapely")):
        return None
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    from matplotlib.patches import Polygon as MplPoly
    from matplotlib.collections import PatchCollection
    import numpy as np

    patches = []
    valores = []
    for hab in habitaciones:
        pol = habitacion_a_shapely(hab)
        if pol is None or not pol.is_valid:
            continue
        v = _val_param(hab.LookupParameter(nombre_param))
        if v is None:
            continue
        coords = list(pol.exterior.coords)
        patches.append(MplPoly(coords, closed=True))
        valores.append(float(v))

    if not patches:
        return None

    vals = np.array(valores)
    norm = mcolors.Normalize(vmin=vals.min(), vmax=vals.max())
    cmap_obj = plt.get_cmap(cmap)

    fig, ax = plt.subplots(figsize=(12, 10))
    col = PatchCollection(patches, norm=norm, cmap=cmap_obj, alpha=0.8)
    col.set_array(vals)
    ax.add_collection(col)
    plt.colorbar(col, ax=ax, label=nombre_param)
    ax.autoscale_view()
    ax.set_aspect("equal")
    ax.set_title(titulo or ("Mapa de calor: " + nombre_param))
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    limpiar_ejes(ax)
    fig.tight_layout()
    return _cerrar_fig(fig, ruta_png)


# ── shapely <-> Revit API ────────────────────────────────────────────────────

def curvas_a_shapely(curvas_revit):
    """
    Convierte una lista de curvas de Revit a un Polygon de Shapely.
    Las curvas deben formar un contorno cerrado en planta (2D).
    shapely se instala automaticamente si no esta disponible.

    Args:
        curvas_revit: lista de Curve de Revit (contorno cerrado)

    Returns:
        shapely.geometry.Polygon, o None si shapely no disponible

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("shapely"):
        return None
    from shapely.geometry import Polygon
    puntos = []
    for curva in curvas_revit:
        p = curva.GetEndPoint(0)
        puntos.append((_pies_a_m(p.X), _pies_a_m(p.Y)))
    return Polygon(puntos)


def habitacion_a_shapely(habitacion):
    """
    Convierte una habitacion (Room) de Revit en un Polygon de Shapely.
    Usa el primer bucle de contorno de la habitacion.
    shapely se instala automaticamente si no esta disponible.

    Args:
        habitacion: elemento Room de Revit

    Returns:
        shapely.geometry.Polygon, o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("shapely"):
        return None
    from shapely.geometry import Polygon
    opts = SpatialElementBoundaryOptions()
    segmentos = habitacion.GetBoundarySegments(opts)
    if not segmentos:
        return None
    loop = segmentos[0]
    puntos = [
        (_pies_a_m(seg.GetCurve().GetEndPoint(0).X),
         _pies_a_m(seg.GetCurve().GetEndPoint(0).Y))
        for seg in loop
    ]
    return Polygon(puntos)


def detectar_solapamientos(habitaciones):
    """
    Detecta pares de habitaciones cuyos contornos se solapan en planta.
    Util para validar separacion de espacios en el modelo.
    shapely se instala automaticamente si no esta disponible.

    Args:
        habitaciones: lista de Room de Revit

    Returns:
        lista de tuplas (id1, id2, area_solape_m2), o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("shapely"):
        return None
    poligonos = []
    for hab in habitaciones:
        pol = habitacion_a_shapely(hab)
        if pol and pol.is_valid:
            poligonos.append((_id_int(hab.Id), pol))
    solapamientos = []
    for i in range(len(poligonos)):
        for j in range(i + 1, len(poligonos)):
            id1, pol1 = poligonos[i]
            id2, pol2 = poligonos[j]
            if pol1.intersects(pol2):
                area = pol1.intersection(pol2).area
                if area > 0.01:
                    solapamientos.append(
                        (id1, id2, round(area, 3))
                    )
    return solapamientos


def buffer_habitacion(habitacion, distancia_m):
    """
    Genera el perimetro expandido de una habitacion a una distancia dada.
    Util para calcular zonas de influencia o distancias de seguridad.

    Args:
        habitacion: Room de Revit
        distancia_m: distancia de expansion en metros

    Returns:
        shapely.geometry.Polygon del area expandida, o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    pol = habitacion_a_shapely(habitacion)
    if pol is None:
        return None
    return pol.buffer(distancia_m)


# ── networkx <-> Revit API ───────────────────────────────────────────────────

def sistema_mep_a_grafo(elementos_mep):
    """
    Construye un grafo NetworkX a partir de elementos MEP conectados
    (conductos, tuberias, bandejas de cable). Los nodos son ElementId
    enteros y las aristas representan conexiones fisicas entre ellos.
    networkx se instala automaticamente si no esta disponible.

    Args:
        elementos_mep: lista de elementos MEP de Revit

    Returns:
        networkx.Graph con atributos pos y categoria por nodo, o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("networkx"):
        return None
    import networkx as nx
    grafo = nx.Graph()
    for elem in elementos_mep:
        eid = _id_int(elem.Id)
        loc = elem.Location
        pos = None
        if hasattr(loc, "Curve"):
            mp = loc.Curve.Evaluate(0.5, True)
            pos = (_pies_a_m(mp.X), _pies_a_m(mp.Y))
        grafo.add_node(
            eid,
            pos=pos,
            categoria=(
                elem.Category.Name if elem.Category else ""
            )
        )
        try:
            mep = getattr(elem, "MEPModel", None)
            if mep is None:
                continue
            cm = mep.ConnectorManager
            if cm is None:
                continue
            for conector in cm.Connectors:
                for ref in conector.AllRefs:
                    try:
                        vecino = _id_int(ref.Owner.Id)
                        if vecino != eid:
                            grafo.add_edge(eid, vecino)
                    except Exception:
                        pass
        except Exception:
            pass
    return grafo


def analisis_red_mep(grafo):
    """
    Calcula metricas basicas de una red MEP representada como grafo
    NetworkX: nodos, aristas, grado medio, componentes y aislados.
    Util para verificar la conectividad del sistema MEP del modelo.

    Args:
        grafo: networkx.Graph generado con sistema_mep_a_grafo

    Returns:
        dict con metricas {nodos, aristas, grado_medio,
        componentes_conectadas, nodos_aislados}

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("networkx"):
        return None
    import networkx as nx
    grados = [d for _, d in grafo.degree()]
    return {
        "nodos": grafo.number_of_nodes(),
        "aristas": grafo.number_of_edges(),
        "grado_medio": (
            round(sum(grados) / len(grados), 2) if grados else 0
        ),
        "componentes_conectadas": (
            nx.number_connected_components(grafo)
        ),
        "nodos_aislados": len(list(nx.isolates(grafo))),
    }


def ruta_mas_corta_mep(grafo, id_inicio, id_fin):
    """
    Calcula la ruta mas corta entre dos elementos MEP en el grafo.
    Util para trazar caminos de distribucion o verificar conectividad.

    Args:
        grafo: networkx.Graph de sistema_mep_a_grafo
        id_inicio: ElementId (int) del nodo de inicio
        id_fin: ElementId (int) del nodo de destino

    Returns:
        lista de ElementId (int) en la ruta, o None si no hay camino

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    if not _asegurar("networkx"):
        return None
    import networkx as nx
    try:
        return nx.shortest_path(grafo, id_inicio, id_fin)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None
