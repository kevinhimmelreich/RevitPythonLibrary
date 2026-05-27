# -*- coding: utf-8 -*-
"""
lib_geometria.py
Biblioteca de funciones Revit/Dynamo — Geometria y Solidos
Compatible: IronPython 2.7 | CPython 3.x | Revit 2024-2026
Repositorio: https://github.com/kevinhimmelreich/RevitPythonLibrary
"""

import clr
import sys
import math

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

from System.Collections.Generic import List  # noqa: E402
from Autodesk.Revit.DB import (  # noqa: E402
    ElementId, Line, Arc, Plane, XYZ, Frame,
    NurbSpline, CurveLoop, BoundingBoxXYZ, Transform, GeometryObject,
    GeometryCreationUtilities, SolidOptions, BooleanOperationsUtils,
    BooleanOperationsType, DirectShape, BuiltInCategory, VertexPair,
    RuledSurface, UnitUtils, UnitTypeId
)
from RevitServices.Persistence import DocumentManager  # noqa: E402
from RevitServices.Transactions import TransactionManager  # noqa: E402

import Revit  # noqa: E402
clr.ImportExtensions(Revit.Elements)
clr.ImportExtensions(Revit.GeometryConversion)

doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
uidoc = uiapp.ActiveUIDocument

REVIT_VERSION = int(app.VersionNumber) if app else 0


def _metros_a_pies(v):
    return UnitUtils.ConvertToInternalUnits(v, UnitTypeId.Meters)


def _pies_a_metros(v):
    return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.Meters)


def _iniciar(nombre="Transaccion"):
    TransactionManager.Instance.EnsureInTransaction(doc)


def _finalizar():
    TransactionManager.Instance.TransactionTaskDone()


# ── Curvas basicas ───────────────────────────────────────────────────────────

def crear_linea(pt_inicio, pt_fin):
    """
    Crea una linea Revit entre dos puntos XYZ.

    Args:
        pt_inicio: XYZ del punto inicial
        pt_fin: XYZ del punto final

    Returns:
        Line de Revit

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return Line.CreateBound(pt_inicio, pt_fin)


def crear_arco(centro, radio_m, angulo_inicio_deg, angulo_fin_deg,
               plano_normal=None):
    """
    Crea un arco de Revit definido por centro, radio y angulos en grados.

    Args:
        centro: XYZ del centro del arco
        radio_m: radio en metros
        angulo_inicio_deg: angulo de inicio en grados
        angulo_fin_deg: angulo de fin en grados
        plano_normal: XYZ normal del plano (por defecto BasisZ)

    Returns:
        Arc de Revit

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if plano_normal is None:
        plano_normal = XYZ.BasisZ
    plano = Plane.CreateByNormalAndOrigin(plano_normal, centro)
    ini_rad = math.radians(angulo_inicio_deg)
    fin_rad = math.radians(angulo_fin_deg)
    return Arc.Create(plano, _metros_a_pies(radio_m), ini_rad, fin_rad)


def crear_arco_por_3_puntos(p1, p2, p3):
    """
    Crea un arco que pasa exactamente por tres puntos XYZ.

    Args:
        p1: XYZ del punto inicial
        p2: XYZ del punto intermedio
        p3: XYZ del punto final

    Returns:
        Arc de Revit

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return Arc.Create(p1, p3, p2)


def crear_nurbs_por_puntos(puntos_xyz, cerrada=False):
    """
    Crea una NurbSpline de Revit que pasa por una lista de puntos XYZ.

    Args:
        puntos_xyz: lista de XYZ por los que pasa la spline
        cerrada: si True anade el primer punto al final para cerrar la curva

    Returns:
        NurbSpline de Revit

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    lista = list(puntos_xyz)
    if cerrada and lista[0] != lista[-1]:
        lista.append(lista[0])
    pts = List[XYZ](lista)
    pesos = List[float]()
    for _ in lista:
        pesos.Add(1.0)
    return NurbSpline.CreateCurve(pts, pesos)


def crear_curva_senoidal(n_puntos, amplitud_m, n_ciclos, longitud_onda_m,
                         pos_y=0.0):
    """
    Genera una lista de puntos XYZ con forma senoidal para crear una spline.

    Args:
        n_puntos: numero de puntos a generar
        amplitud_m: amplitud de la onda en metros
        n_ciclos: numero de ciclos completos
        longitud_onda_m: longitud de onda en metros
        pos_y: valor fijo de Y (por defecto 0.0)

    Returns:
        lista de XYZ con forma senoidal

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    amp = _metros_a_pies(amplitud_m)
    lo = _metros_a_pies(longitud_onda_m)
    longitud_total = n_ciclos * lo
    x_vals = [i * longitud_total / (n_puntos - 1) for i in range(n_puntos)]
    z_vals = [amp * math.sin(2 * math.pi * xi / lo) for xi in x_vals]
    return [XYZ(xi, pos_y, zi) for xi, zi in zip(x_vals, z_vals)]


# ── CurveLoop ────────────────────────────────────────────────────────────────

def crear_curveloop_desde_curvas(lista_curvas):
    """
    Crea un CurveLoop a partir de una lista de curvas Revit.

    Args:
        lista_curvas: lista de curvas Revit en orden continuo

    Returns:
        CurveLoop de Revit

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    loop = CurveLoop()
    for c in lista_curvas:
        loop.Append(c)
    return loop


def desplazar_curveloop(curve_loop, vector_xyz):
    """
    Desplaza un CurveLoop un vector dado creando un nuevo CurveLoop.

    Args:
        curve_loop: CurveLoop de Revit
        vector_xyz: XYZ vector de traslacion

    Returns:
        nuevo CurveLoop desplazado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    t = Transform.CreateTranslation(vector_xyz)
    return CurveLoop.CreateViaTransform(curve_loop, t)


def crear_offset_curveloop(curve_loop, distancia_m):
    """
    Crea un CurveLoop desfasado a una distancia en metros.

    Args:
        curve_loop: CurveLoop de Revit
        distancia_m: distancia de desfase en metros

    Returns:
        nuevo CurveLoop desfasado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    normal = (curve_loop.GetPlane().Normal
              if curve_loop.HasPlane() else XYZ.BasisZ)
    return CurveLoop.CreateViaOffset(
        curve_loop, _metros_a_pies(distancia_m), normal)


def ordenar_curvas_en_cadena(curvas, tolerancia=1e-6):
    """
    Ordena curvas Revit nativas en un CurveLoop continuo.

    Args:
        curvas: lista de curvas Revit a ordenar
        tolerancia: tolerancia de distancia para considerar curvas conectadas

    Returns:
        CurveLoop ordenado y continuo

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    loop = CurveLoop()
    copia = list(curvas)
    loop.Append(copia.pop(0))
    while copia:
        for i, c in enumerate(copia):
            try:
                loop.Append(c)
                copia.pop(i)
                break
            except Exception:
                continue
    return loop


def ordenar_curvas_conectadas(curvas, tolerancia_m=0.01):
    """
    Ordena una lista desordenada de curvas en una cadena continua
    haciendo coincidir los extremos. Invierte curvas cuando es necesario.
    A diferencia de ordenar_curvas_en_cadena, maneja reversiones y
    retorna una lista (no CurveLoop) para mayor flexibilidad.

    Args:
        curvas: lista de curvas Revit desordenadas
        tolerancia_m: tolerancia de union en metros (por defecto 0.01)

    Returns:
        lista ordenada de curvas Revit con orientacion correcta

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not curvas:
        return []
    tol = UnitUtils.ConvertToInternalUnits(tolerancia_m, UnitTypeId.Meters)
    pendientes = list(curvas)
    ordenadas = [pendientes.pop(0)]
    while pendientes:
        fin = ordenadas[-1].GetEndPoint(1)
        encontrado = False
        for i, c in enumerate(pendientes):
            if fin.DistanceTo(c.GetEndPoint(0)) <= tol:
                ordenadas.append(pendientes.pop(i))
                encontrado = True
                break
            if fin.DistanceTo(c.GetEndPoint(1)) <= tol:
                ordenadas.append(c.CreateReversed())
                pendientes.pop(i)
                encontrado = True
                break
        if not encontrado:
            ordenadas.extend(pendientes)
            break
    return ordenadas


def combinar_perimetros(curvas_a, curvas_b, tolerancia_m=0.01):
    """
    Combina dos contornos de curvas eliminando los segmentos compartidos
    y retornando el perimetro exterior unido y ordenado.

    Caso de uso tipico: contorno de una habitacion (curvas_a) mas el
    area de umbral de una puerta (curvas_b) para crear un suelo que
    cubra ambas superficies.

    Args:
        curvas_a: lista de curvas Revit (primer contorno)
        curvas_b: lista de curvas Revit (segundo contorno)
        tolerancia_m: tolerancia de coincidencia en metros

    Returns:
        lista de curvas Revit ordenadas del perimetro combinado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tol = UnitUtils.ConvertToInternalUnits(tolerancia_m, UnitTypeId.Meters)

    def _coinciden(c1, c2):
        a0, a1 = c1.GetEndPoint(0), c1.GetEndPoint(1)
        b0, b1 = c2.GetEndPoint(0), c2.GetEndPoint(1)
        return (
            (a0.DistanceTo(b0) <= tol and a1.DistanceTo(b1) <= tol) or
            (a0.DistanceTo(b1) <= tol and a1.DistanceTo(b0) <= tol)
        )

    restantes_b = list(curvas_b)
    resultado = []
    for ca in curvas_a:
        compartida = False
        for i, cb in enumerate(restantes_b):
            if _coinciden(ca, cb):
                compartida = True
                restantes_b.pop(i)
                break
        if not compartida:
            resultado.append(ca)
    resultado.extend(restantes_b)
    return ordenar_curvas_conectadas(resultado, tolerancia_m)


# ── Solidos ──────────────────────────────────────────────────────────────────

def _loop_desde_puntos(puntos_xyz):
    loop = CurveLoop()
    n = len(puntos_xyz)
    for i in range(n):
        loop.Append(Line.CreateBound(puntos_xyz[i], puntos_xyz[(i + 1) % n]))
    return loop


def _opciones_solido(material=None, estilo_grafico=None):
    mat_id = material.Id if material else ElementId.InvalidElementId
    style_id = (estilo_grafico.Id
                if estilo_grafico else ElementId.InvalidElementId)
    return SolidOptions(mat_id, style_id)


def crear_extrusion(curve_loops, direccion_xyz, distancia_m, material=None):
    """
    Crea un solido por extrusion de uno o varios CurveLoop.

    Args:
        curve_loops: CurveLoop o lista de puntos XYZ que define el perfil
        direccion_xyz: XYZ de la direccion de extrusion
        distancia_m: longitud de extrusion en metros
        material: elemento Material de Revit (opcional)

    Returns:
        Solid de Revit

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not isinstance(curve_loops, CurveLoop):
        curve_loops = _loop_desde_puntos(curve_loops)
    loops = List[CurveLoop]()
    loops.Add(curve_loops)
    opc = _opciones_solido(material)
    return GeometryCreationUtilities.CreateExtrusionGeometry(
        loops, direccion_xyz, _metros_a_pies(distancia_m), opc)


def crear_blend(loop_inferior, loop_superior, pares_vertices=None):
    """
    Crea un solido tipo blend (fusion) entre dos CurveLoop.

    Args:
        loop_inferior: CurveLoop de la base
        loop_superior: CurveLoop del tope
        pares_vertices: lista de VertexPair (por defecto 1-a-1)

    Returns:
        Solid de Revit

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if pares_vertices is None:
        n = loop_inferior.NumberOfCurves()
        pares = List[VertexPair]([VertexPair(i, i) for i in range(n)])
    else:
        pares = List[VertexPair](pares_vertices)
    opc = _opciones_solido()
    return GeometryCreationUtilities.CreateBlendGeometry(
        loop_inferior, loop_superior, pares, opc)


def crear_barrido(perfil_loop, camino_loop, material=None):
    """
    Crea un solido por barrido (sweep) del perfil a lo largo del camino.

    Args:
        perfil_loop: CurveLoop del perfil de barrido
        camino_loop: CurveLoop del camino de barrido
        material: elemento Material de Revit (opcional)

    Returns:
        Solid de Revit

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    perfil = List[CurveLoop]()
    perfil.Add(perfil_loop)
    opc = _opciones_solido(material)
    return GeometryCreationUtilities.CreateSweptGeometry(
        camino_loop, 0, 0.0, perfil, opc)


def crear_barrido_doble(perfiles_loops, curva_camino, params_path=None):
    """
    Crea un solido de barrido y fusion (SweptBlend) con dos o mas perfiles.

    Args:
        perfiles_loops: lista de CurveLoop (minimo 2) a lo largo del camino
        curva_camino: curva Revit que define el camino
        params_path: lista de parametros sobre la curva (min/max si es None)

    Returns:
        Solid de Revit

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if params_path is None:
        params_path = [
            curva_camino.GetEndParameter(0),
            curva_camino.GetEndParameter(1),
        ]
    perfiles = List[CurveLoop](perfiles_loops)
    params = List[float](params_path)
    return GeometryCreationUtilities.CreateSweptBlendGeometry(
        curva_camino, params, perfiles, None)


def crear_esfera(centro_xyz, radio_m):
    """
    Crea una esfera solida por revolucion de un semicirculo.

    Args:
        centro_xyz: XYZ del centro de la esfera
        radio_m: radio en metros

    Returns:
        Solid de Revit (esfera)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    r = _metros_a_pies(radio_m)
    sp = centro_xyz.Subtract(XYZ.BasisZ.Multiply(r))
    ep = centro_xyz.Add(XYZ.BasisZ.Multiply(r))
    pt = centro_xyz.Add(XYZ.BasisX.Multiply(r))
    arc = Arc.Create(sp, ep, pt)
    loop = CurveLoop()
    loop.Append(arc)
    loop.Append(Line.CreateBound(ep, sp))
    frame = Frame(centro_xyz, XYZ.BasisX, XYZ.BasisY, XYZ.BasisZ)
    opc = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
    return GeometryCreationUtilities.CreateRevolvedGeometry(
        frame, [loop], 0.0, 2.0 * math.pi, opc)


def crear_cilindro(centro_base_xyz, radio_m, altura_m):
    """
    Crea un cilindro solido por extrusion de un circulo.

    Args:
        centro_base_xyz: XYZ del centro de la base del cilindro
        radio_m: radio en metros
        altura_m: altura en metros

    Returns:
        Solid de Revit (cilindro)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    r = _metros_a_pies(radio_m)
    h = _metros_a_pies(altura_m)
    plano = Plane.CreateByNormalAndOrigin(XYZ.BasisZ, centro_base_xyz)
    arc1 = Arc.Create(plano, r, 0.0, math.pi)
    arc2 = Arc.Create(plano, r, math.pi, 2.0 * math.pi)
    loop = CurveLoop()
    loop.Append(arc1)
    loop.Append(arc2)
    loops = List[CurveLoop]()
    loops.Add(loop)
    return GeometryCreationUtilities.CreateExtrusionGeometry(
        loops, XYZ.BasisZ, h)


def crear_cono(centro_base_xyz, radio_m, altura_m):
    """
    Crea un cono solido por revolucion de un triangulo.

    Args:
        centro_base_xyz: XYZ del centro de la base del cono
        radio_m: radio de la base en metros
        altura_m: altura del cono en metros

    Returns:
        Solid de Revit (cono)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    r = _metros_a_pies(radio_m)
    h = _metros_a_pies(altura_m)
    apex = centro_base_xyz.Add(XYZ.BasisZ.Multiply(h))
    base_p = centro_base_xyz.Add(XYZ.BasisX.Multiply(r))
    loop = CurveLoop()
    loop.Append(Line.CreateBound(apex, base_p))
    loop.Append(Line.CreateBound(base_p, centro_base_xyz))
    loop.Append(Line.CreateBound(centro_base_xyz, apex))
    frame = Frame(centro_base_xyz, XYZ.BasisX, XYZ.BasisY, XYZ.BasisZ)
    opc = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
    return GeometryCreationUtilities.CreateRevolvedGeometry(
        frame, [loop], 0.0, 2.0 * math.pi, opc)


def crear_cono_truncado(centro_base_xyz, radio_inf_m, radio_sup_m, altura_m):
    """
    Crea un tronco de cono solido por revolucion de un trapecio.

    Args:
        centro_base_xyz: XYZ del centro de la base inferior
        radio_inf_m: radio de la base inferior en metros
        radio_sup_m: radio de la base superior en metros
        altura_m: altura del tronco en metros

    Returns:
        Solid de Revit (tronco de cono)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    rb = _metros_a_pies(radio_inf_m)
    rt = _metros_a_pies(radio_sup_m)
    h = _metros_a_pies(altura_m)
    p0 = centro_base_xyz
    p1 = centro_base_xyz.Add(XYZ.BasisX.Multiply(rb))
    p2 = (centro_base_xyz.Add(XYZ.BasisZ.Multiply(h))
          .Add(XYZ.BasisX.Multiply(rt)))
    p3 = centro_base_xyz.Add(XYZ.BasisZ.Multiply(h))
    loop = CurveLoop()
    loop.Append(Line.CreateBound(p0, p1))
    loop.Append(Line.CreateBound(p1, p2))
    loop.Append(Line.CreateBound(p2, p3))
    loop.Append(Line.CreateBound(p3, p0))
    frame = Frame(centro_base_xyz, XYZ.BasisX, XYZ.BasisY, XYZ.BasisZ)
    opc = SolidOptions(ElementId.InvalidElementId, ElementId.InvalidElementId)
    return GeometryCreationUtilities.CreateRevolvedGeometry(
        frame, [loop], 0.0, 2.0 * math.pi, opc)


def crear_revolution(loop_perfil, angulo_inicio=0.0, angulo_fin=None,
                     centro=None, material=None):
    """
    Crea un solido de revolucion del perfil alrededor del eje Z local.

    Args:
        loop_perfil: CurveLoop del perfil a revolucionar
        angulo_inicio: angulo de inicio en radianes (por defecto 0.0)
        angulo_fin: angulo de fin en radianes (por defecto 2*pi)
        centro: XYZ del centro de revolucion (por defecto origen)
        material: elemento Material de Revit (opcional)

    Returns:
        Solid de Revit

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if angulo_fin is None:
        angulo_fin = 2.0 * math.pi
    if centro is None:
        centro = XYZ.Zero
    frame = Frame(centro, XYZ.BasisX, XYZ.BasisY, XYZ.BasisZ)
    opc = _opciones_solido(material)
    return GeometryCreationUtilities.CreateRevolvedGeometry(
        frame, [loop_perfil], angulo_inicio, angulo_fin, opc)


def crear_directshape(geometrias, categoria_bic=None, nombre="DS"):
    """
    Crea un DirectShape visible en el modelo a partir de una lista de
    GeometryObject.

    Args:
        geometrias: lista de GeometryObject (Solid, Mesh, etc.)
        categoria_bic: BuiltInCategory (por defecto OST_GenericModel)
        nombre: nombre descriptivo del DirectShape

    Returns:
        DirectShape creado en el documento

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if categoria_bic is None:
        categoria_bic = BuiltInCategory.OST_GenericModel
    _iniciar("Crear DirectShape")
    ds = DirectShape.CreateElement(doc, ElementId(categoria_bic))
    ds.ApplicationId = "RevitPythonLibrary"
    ds.ApplicationDataId = nombre
    ds.SetShape(List[GeometryObject](geometrias))
    _finalizar()
    return ds


# ── Operaciones booleanas ────────────────────────────────────────────────────

def booleano_union(solido_a, solido_b):
    """
    Ejecuta la union booleana de dos solidos de Revit.

    Args:
        solido_a: Solid de Revit (base)
        solido_b: Solid de Revit (a unir)

    Returns:
        Solid resultado de la union

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return BooleanOperationsUtils.ExecuteBooleanOperation(
        solido_a, solido_b, BooleanOperationsType.Union)


def booleano_diferencia(solido_a, solido_b):
    """
    Ejecuta la diferencia booleana: solido_a menos solido_b.

    Args:
        solido_a: Solid de Revit (base)
        solido_b: Solid de Revit (a restar)

    Returns:
        Solid resultado de la diferencia

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return BooleanOperationsUtils.ExecuteBooleanOperation(
        solido_a, solido_b, BooleanOperationsType.Difference)


def booleano_interseccion(solido_a, solido_b):
    """
    Ejecuta la interseccion booleana de dos solidos de Revit.

    Args:
        solido_a: Solid de Revit
        solido_b: Solid de Revit

    Returns:
        Solid resultado de la interseccion

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return BooleanOperationsUtils.ExecuteBooleanOperation(
        solido_a, solido_b, BooleanOperationsType.Intersect)


def descomponer_solido(solido):
    """
    Descompone un solido en sus subelementos geometricos.

    Args:
        solido: Solid de Revit

    Returns:
        diccionario {caras, aristas, vertices, volumen_m3, area_m2}

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    caras, aristas, vertices = [], [], []
    for face in solido.Faces:
        caras.append(face)
    for edge in solido.Edges:
        crv = edge.AsCurve()
        aristas.append(crv)
        vertices.append(crv.Evaluate(0, True))
    return {
        "caras":     caras,
        "aristas":   aristas,
        "vertices":  vertices,
        "volumen_m3": UnitUtils.ConvertFromInternalUnits(
            solido.Volume, UnitTypeId.CubicMeters),
        "area_m2":    UnitUtils.ConvertFromInternalUnits(
            solido.SurfaceArea, UnitTypeId.SquareMeters),
    }


# ── Algoritmos geometricos ───────────────────────────────────────────────────

def obtener_bbox(elementos):
    """
    Calcula el BoundingBoxXYZ global que engloba una lista de elementos.

    Args:
        elementos: lista de elementos Revit

    Returns:
        BoundingBoxXYZ total, o None si no hay elementos con bbox

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    min_x = min_y = min_z = float("inf")
    max_x = max_y = max_z = float("-inf")
    encontrado = False
    for e in elementos:
        bb = e.BoundingBox[None]
        if bb is None:
            continue
        encontrado = True
        min_x = min(min_x, bb.Min.X)
        min_y = min(min_y, bb.Min.Y)
        min_z = min(min_z, bb.Min.Z)
        max_x = max(max_x, bb.Max.X)
        max_y = max(max_y, bb.Max.Y)
        max_z = max(max_z, bb.Max.Z)
    if not encontrado:
        return None
    bb_total = BoundingBoxXYZ()
    bb_total.Min = XYZ(min_x, min_y, min_z)
    bb_total.Max = XYZ(max_x, max_y, max_z)
    return bb_total


def punto_mas_cercano_en_curva(punto_xyz, curva):
    """
    Proyecta un punto XYZ sobre una curva Revit y retorna el resultado.

    Args:
        punto_xyz: XYZ a proyectar
        curva: curva Revit (Line, Arc, etc.)

    Returns:
        diccionario {punto_proyectado, distancia_m, parametro}

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    res = curva.Project(punto_xyz)
    return {
        "punto_proyectado": res.XYZPoint,
        "distancia_m": UnitUtils.ConvertFromInternalUnits(
            res.Distance, UnitTypeId.Meters),
        "parametro":        res.Parameter,
    }


def dividir_linea_en_n(linea, n):
    """
    Divide una linea en n puntos equidistantes.

    Args:
        linea: curva Revit (Line)
        n: numero de puntos a generar (incluye extremos)

    Returns:
        lista de n XYZ equidistantes sobre la linea

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return [linea.Evaluate(i / float(n - 1), True) for i in range(n)]


def agrupar_puntos_por_proximidad(puntos, tolerancia_m):
    """
    Agrupa puntos XYZ por proximidad usando BFS.

    Args:
        puntos: lista de XYZ a agrupar
        tolerancia_m: distancia maxima en metros para considerar puntos
            como vecinos

    Returns:
        lista de grupos (cada grupo es una lista de XYZ)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tol_pies = UnitUtils.ConvertToInternalUnits(
        tolerancia_m, UnitTypeId.Meters)
    cola = set()
    pendientes = list(puntos)
    grupos = []
    while pendientes:
        grupo = []
        cola.add(pendientes.pop())
        while cola:
            actual = cola.pop()
            grupo.append(actual)
            nuevos = [
                p for p in pendientes
                if actual.DistanceTo(p) <= tol_pies
            ]
            cola.update(nuevos)
            pendientes = [p for p in pendientes if p not in cola]
        grupos.append(grupo)
    return grupos


def agrupar_curvas_conectadas(lista_curvas, tolerancia_m=0.01):
    """
    Agrupa curvas que comparten puntos extremos dentro de la tolerancia dada.

    Args:
        lista_curvas: lista de curvas Revit
        tolerancia_m: tolerancia de distancia en metros para considerar
            curvas conectadas

    Returns:
        lista de grupos de curvas conectadas

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    tol_pies = UnitUtils.ConvertToInternalUnits(
        tolerancia_m, UnitTypeId.Meters)
    cola = set()
    pendientes = list(lista_curvas)
    grupos = []
    while pendientes:
        forma = []
        cola.add(pendientes.pop())
        while cola:
            actual = cola.pop()
            forma.append(actual)
            for candidato in list(pendientes):
                for pc in (candidato.GetEndPoint(0), candidato.GetEndPoint(1)):
                    for pa in (actual.GetEndPoint(0), actual.GetEndPoint(1)):
                        if pc.DistanceTo(pa) <= tol_pies:
                            cola.add(candidato)
            pendientes = [c for c in pendientes if c not in cola]
        grupos.append(forma)
    return grupos


def pathfinding_a_star(nodos, inicio, fin, distancia_max=1.125):
    """
    Busqueda de ruta A* entre dos nodos sobre una grilla. Cada nodo debe
    tener .point, .G, .H, .parent.

    Args:
        nodos: lista de nodos con atributos point (XYZ), G, H, parent
        inicio: nodo inicial
        fin: nodo destino
        distancia_max: distancia maxima entre nodos vecinos en pies internos

    Returns:
        lista de nodos del camino optimo

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    def _dist(n1, n2):
        return math.hypot(n2.point.X - n1.point.X, n2.point.Y - n1.point.Y)

    def _vecinos(nodo, grilla, dmax):
        return [
            c for c in grilla
            if 0 < nodo.point.DistanceTo(c.point) <= dmax
        ]

    abiertos = set([inicio])
    cerrados = set()
    while abiertos:
        actual = min(abiertos, key=lambda n: n.G + n.H)
        if actual == fin:
            camino = []
            while actual.parent:
                camino.append(actual)
                actual = actual.parent
            camino.append(actual)
            return list(reversed(camino))
        abiertos.discard(actual)
        cerrados.add(actual)
        for vecino in _vecinos(actual, nodos, distancia_max):
            if vecino in cerrados:
                continue
            nuevo_g = actual.G - _dist(actual, vecino)
            if vecino in abiertos:
                if vecino.G > nuevo_g:
                    vecino.parent = actual
            else:
                vecino.G = nuevo_g
                vecino.H = _dist(vecino, fin)
                vecino.parent = actual
                abiertos.add(vecino)
    raise ValueError("A* no encontro ruta entre los nodos indicados.")


def superficie_reglada_por_curvas(curva_inf, curva_sup):
    """
    Crea una superficie reglada entre dos curvas Revit.

    Args:
        curva_inf: curva Revit inferior
        curva_sup: curva Revit superior

    Returns:
        RuledSurface de Revit

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return RuledSurface.Create(curva_inf, curva_sup)


# ── numpy (CPython 3.x / Dynamo 2.13+) ──────────────────────────────────────

def puntos_a_array_numpy(puntos_xyz):
    """
    Convierte una lista de XYZ de Revit a un array numpy (N, 3) en metros.
    Requiere CPython 3.x (Dynamo 2.13+).

    Args:
        puntos_xyz: lista de Autodesk.Revit.DB.XYZ

    Returns:
        numpy array de shape (N, 3), o None si numpy no disponible

    Revit: 2024-2026 | CPython 3.x (Dynamo 2.13+)
    """
    try:
        import numpy as np
    except ImportError:
        return None
    return np.array(
        [[p.X * 0.3048, p.Y * 0.3048, p.Z * 0.3048] for p in puntos_xyz]
    )


def calcular_centroide_numpy(puntos_xyz):
    """
    Calcula el centroide de una nube de puntos XYZ usando numpy.
    Requiere CPython 3.x (Dynamo 2.13+).

    Args:
        puntos_xyz: lista de Autodesk.Revit.DB.XYZ

    Returns:
        numpy array [cx, cy, cz] en metros, o None si numpy no disponible

    Revit: 2024-2026 | CPython 3.x (Dynamo 2.13+)
    """
    arr = puntos_a_array_numpy(puntos_xyz)
    if arr is None:
        return None
    return arr.mean(axis=0)


def distancias_entre_puntos_numpy(puntos_xyz):
    """
    Calcula la matriz de distancias entre todos los puntos de la lista.
    Requiere CPython 3.x (Dynamo 2.13+).

    Args:
        puntos_xyz: lista de Autodesk.Revit.DB.XYZ

    Returns:
        numpy array (N, N) con distancias en metros,
        o None si numpy no disponible

    Revit: 2024-2026 | CPython 3.x (Dynamo 2.13+)
    """
    try:
        import numpy as np
    except ImportError:
        return None
    arr = puntos_a_array_numpy(puntos_xyz)
    if arr is None:
        return None
    diff = arr[:, np.newaxis, :] - arr[np.newaxis, :, :]
    return np.sqrt((diff ** 2).sum(axis=-1))


def bbox_desde_numpy(puntos_xyz):
    """
    Calcula el bounding box (min/max XYZ) de una nube de puntos.
    Requiere CPython 3.x (Dynamo 2.13+).

    Args:
        puntos_xyz: lista de Autodesk.Revit.DB.XYZ

    Returns:
        tupla (min_xyz, max_xyz) como arrays numpy en metros,
        o None si numpy no disponible

    Revit: 2024-2026 | CPython 3.x (Dynamo 2.13+)
    """
    arr = puntos_a_array_numpy(puntos_xyz)
    if arr is None:
        return None
    return arr.min(axis=0), arr.max(axis=0)


def ajuste_plano_numpy(puntos_xyz):
    """
    Ajusta un plano a una nube de puntos mediante SVD (minimos cuadrados).
    Requiere CPython 3.x (Dynamo 2.13+).

    Args:
        puntos_xyz: lista de Autodesk.Revit.DB.XYZ (minimo 3 puntos)

    Returns:
        tupla (centroide, normal) como arrays numpy,
        o None si numpy no disponible

    Revit: 2024-2026 | CPython 3.x (Dynamo 2.13+)
    """
    try:
        import numpy as np
    except ImportError:
        return None
    arr = puntos_a_array_numpy(puntos_xyz)
    if arr is None:
        return None
    centroide = arr.mean(axis=0)
    _, _, Vt = np.linalg.svd(arr - centroide)
    normal = Vt[-1]
    return centroide, normal
