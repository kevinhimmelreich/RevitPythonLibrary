# -*- coding: utf-8 -*-
"""
lib_scientific.py
Integracion Revit API <-> Python cientifico
pandas, numpy, scipy, matplotlib, shapely, networkx
Compatible: CPython 3.x (Dynamo 2.13+) | Revit 2024-2026
NOTA: IronPython 2.7 no soporta estas bibliotecas. Todas las
funciones retornan None con aviso si la biblioteca no esta disponible.
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


def _no_disponible(lib):
    print(lib + " no disponible. Requiere CPython 3.x (Dynamo 2.13+).")


# ── pandas <-> Revit API ─────────────────────────────────────────────────────

def elementos_a_dataframe(elementos, parametros):
    """
    Exporta parametros de cualquier lista de elementos Revit a un
    pandas DataFrame. Base para cualquier analisis de datos del modelo.

    Args:
        elementos: lista de elementos Revit
        parametros: lista de nombres de parametros a incluir

    Returns:
        DataFrame con columnas [ElementId, Categoria, Nivel, *params]
        o None si pandas no esta disponible

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    try:
        import pandas as pd
    except ImportError:
        _no_disponible("pandas")
        return None
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
    try:
        import pandas as pd
    except ImportError:
        _no_disponible("pandas")
        return None
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
    try:
        import pandas as pd
    except ImportError:
        _no_disponible("pandas")
        return None
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

    Args:
        puntos_xyz: lista de Autodesk.Revit.DB.XYZ

    Returns:
        numpy array shape (N, 3) en metros, o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    try:
        import numpy as np
    except ImportError:
        _no_disponible("numpy")
        return None
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
    try:
        import numpy  # noqa: F401
    except ImportError:
        _no_disponible("numpy")
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
    try:
        import numpy as np
    except ImportError:
        _no_disponible("numpy")
        return None
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
    Util para zonar elementos automaticamente por area o planta.

    Args:
        elementos: lista de elementos Revit con LocationPoint
        n_grupos: numero de grupos a generar

    Returns:
        dict {grupo_id: [elementos]} con los grupos resultantes,
        o None si scipy no esta disponible

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    try:
        from scipy.cluster.vq import kmeans2
        import numpy as np
    except ImportError:
        _no_disponible("scipy / numpy")
        return None
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


def vecinos_por_radio(elementos, radio_m):
    """
    Para cada elemento devuelve los elementos vecinos dentro de un radio.
    Usa un KD-Tree (scipy) para busqueda eficiente en 2D (planta).
    Util para detectar conflictos de espacio o proximidad entre MEP.

    Args:
        elementos: lista de elementos Revit con LocationPoint
        radio_m: radio de busqueda en metros

    Returns:
        dict {ElementId: [ElementId vecinos]}, o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    try:
        from scipy.spatial import KDTree
    except ImportError:
        _no_disponible("scipy")
        return None
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
    try:
        from scipy.interpolate import interp1d
        import numpy as np
    except ImportError:
        _no_disponible("scipy / numpy")
        return None
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

def _guardar_figura(fig, ruta_png):
    """Guarda figura matplotlib a PNG y libera memoria."""
    fig.savefig(ruta_png, dpi=150, bbox_inches="tight")
    import matplotlib.pyplot as plt
    plt.close(fig)
    return ruta_png


def grafico_parametro_por_nivel(
        elementos, nombre_param, ruta_png,
        titulo=None, color="steelblue"):
    """
    Grafico de barras con el valor medio de un parametro numerico
    agrupado por nivel de Revit. Exporta a PNG.

    Args:
        elementos: lista de elementos Revit
        nombre_param: nombre del parametro numerico a graficar
        ruta_png: ruta de salida del archivo .png
        titulo: titulo del grafico (opcional)
        color: color de las barras (defecto "steelblue")

    Returns:
        ruta_png si se genero correctamente, None si falta dependencia

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import pandas as pd
    except ImportError:
        _no_disponible("matplotlib / pandas")
        return None
    df = elementos_a_dataframe(elementos, [nombre_param])
    if df is None or nombre_param not in df.columns:
        return None
    df[nombre_param] = pd.to_numeric(
        df[nombre_param], errors="coerce"
    )
    agrupado = df.groupby("Nivel")[nombre_param].mean().dropna()
    fig, ax = plt.subplots(figsize=(10, 5))
    agrupado.plot(kind="bar", ax=ax, color=color)
    ax.set_title(titulo or ("Media de " + nombre_param + " por nivel"))
    ax.set_xlabel("Nivel")
    ax.set_ylabel(nombre_param)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return _guardar_figura(fig, ruta_png)


def histograma_parametro(
        elementos, nombre_param, ruta_png,
        bins=20, titulo=None, color="steelblue"):
    """
    Histograma de la distribucion de valores de un parametro numerico.
    Util para detectar outliers o verificar uniformidad del modelo.

    Args:
        elementos: lista de elementos Revit
        nombre_param: nombre del parametro numerico
        ruta_png: ruta de salida del archivo .png
        bins: numero de intervalos (defecto 20)
        titulo: titulo del grafico (opcional)
        color: color de las barras

    Returns:
        ruta_png o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import pandas as pd
    except ImportError:
        _no_disponible("matplotlib / pandas")
        return None
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
    fig.tight_layout()
    return _guardar_figura(fig, ruta_png)


def grafico_dispersion(
        elementos, param_x, param_y, ruta_png, titulo=None):
    """
    Grafico de dispersion (scatter) entre dos parametros numericos.
    Permite detectar correlaciones entre propiedades de elementos Revit.

    Args:
        elementos: lista de elementos Revit
        param_x: nombre del parametro para el eje X
        param_y: nombre del parametro para el eje Y
        ruta_png: ruta de salida del archivo .png
        titulo: titulo del grafico (opcional)

    Returns:
        ruta_png o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import pandas as pd
    except ImportError:
        _no_disponible("matplotlib / pandas")
        return None
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
    fig.tight_layout()
    return _guardar_figura(fig, ruta_png)


def grafico_suma_por_categoria(
        elementos, nombre_param, ruta_png, titulo=None):
    """
    Grafico de sectores (pie) con la suma de un parametro numerico
    agrupada por categoria de elemento Revit. Util para reportes de
    cantidades (m2 por categoria, longitud MEP por sistema, etc.).

    Args:
        elementos: lista de elementos Revit
        nombre_param: parametro numerico a sumar por categoria
        ruta_png: ruta de salida del archivo .png
        titulo: titulo del grafico (opcional)

    Returns:
        ruta_png o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import pandas as pd
    except ImportError:
        _no_disponible("matplotlib / pandas")
        return None
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
    return _guardar_figura(fig, ruta_png)


# ── shapely <-> Revit API ────────────────────────────────────────────────────

def curvas_a_shapely(curvas_revit):
    """
    Convierte una lista de curvas de Revit a un Polygon de Shapely.
    Las curvas deben formar un contorno cerrado en planta (2D).

    Args:
        curvas_revit: lista de Curve de Revit (contorno cerrado)

    Returns:
        shapely.geometry.Polygon, o None si shapely no disponible

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    try:
        from shapely.geometry import Polygon
    except ImportError:
        _no_disponible("shapely")
        return None
    puntos = []
    for curva in curvas_revit:
        p = curva.GetEndPoint(0)
        puntos.append((_pies_a_m(p.X), _pies_a_m(p.Y)))
    return Polygon(puntos)


def habitacion_a_shapely(habitacion):
    """
    Convierte una habitacion (Room) de Revit en un Polygon de Shapely.
    Usa el primer bucle de contorno de la habitacion.

    Args:
        habitacion: elemento Room de Revit

    Returns:
        shapely.geometry.Polygon, o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    try:
        from shapely.geometry import Polygon
    except ImportError:
        _no_disponible("shapely")
        return None
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

    Args:
        habitaciones: lista de Room de Revit

    Returns:
        lista de tuplas (id1, id2, area_solape_m2), o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    try:
        from shapely.geometry import Polygon  # noqa: F401
    except ImportError:
        _no_disponible("shapely")
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
        distancia_m: distancia de expansion en metros (positivo = hacia fuera)

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

    Args:
        elementos_mep: lista de elementos MEP de Revit

    Returns:
        networkx.Graph con atributos pos y categoria por nodo, o None

    Requiere: CPython 3.x (Dynamo 2.13+)
    """
    try:
        import networkx as nx
    except ImportError:
        _no_disponible("networkx")
        return None
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
    try:
        import networkx as nx
    except ImportError:
        _no_disponible("networkx")
        return None
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
    try:
        import networkx as nx
    except ImportError:
        _no_disponible("networkx")
        return None
    try:
        return nx.shortest_path(grafo, id_inicio, id_fin)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None
