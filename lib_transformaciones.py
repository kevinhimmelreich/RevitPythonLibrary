# -*- coding: utf-8 -*-
"""
lib_transformaciones.py
Biblioteca de funciones Revit/Dynamo — Transformaciones
Consolida TODAS las operaciones de transformacion: mover, copiar,
rotar, espejar, voltear, anclar, orientacion, ubicacion directa
y matematica de Transform.
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
    ElementId, ElementTransformUtils, Transform, Plane,
    Line, XYZ, LocationPoint, LocationCurve,
    UnitUtils, UnitTypeId
)
from Autodesk.Revit.DB.Structure import (  # noqa: E402
    StructuralFramingUtils
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


# ── Helpers internos ──────────────────────────────────────────────────────────

def _iniciar():
    TransactionManager.Instance.EnsureInTransaction(doc)


def _finalizar():
    TransactionManager.Instance.TransactionTaskDone()


def _rad(grados):
    return math.radians(grados)


def _metros_a_pies(v):
    return UnitUtils.ConvertToInternalUnits(v, UnitTypeId.Meters)


def _pies_a_metros(v):
    return UnitUtils.ConvertFromInternalUnits(v, UnitTypeId.Meters)


# ── Consultas de ubicacion ────────────────────────────────────────────────────

def obtener_ubicacion(elemento):
    """
    Lee la ubicacion de un elemento y retorna un dict con su tipo y
    valor. Centraliza la logica de distincion entre LocationPoint y
    LocationCurve.

    Args:
        elemento: elemento Revit

    Returns:
        dict con claves:
          "tipo":            "punto", "curva" o "desconocido"
          "punto":           XYZ (si es LocationPoint) o None
          "curva":           Curve (si es LocationCurve) o None
          "rotacion_grados": float o None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    loc = elemento.Location
    if isinstance(loc, LocationPoint):
        rot = (math.degrees(loc.Rotation)
               if hasattr(loc, "Rotation") else None)
        return {
            "tipo": "punto",
            "punto": loc.Point,
            "curva": None,
            "rotacion_grados": rot,
        }
    if isinstance(loc, LocationCurve):
        return {
            "tipo": "curva",
            "punto": None,
            "curva": loc.Curve,
            "rotacion_grados": None,
        }
    return {
        "tipo": "desconocido",
        "punto": None,
        "curva": None,
        "rotacion_grados": None,
    }


def obtener_punto_ubicacion(elemento):
    """
    Retorna el punto de ubicacion de un elemento con LocationPoint.

    Args:
        elemento: elemento Revit

    Returns:
        XYZ o None si el elemento no tiene LocationPoint

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    loc = elemento.Location
    return loc.Point if isinstance(loc, LocationPoint) else None


def obtener_curva_ubicacion(elemento):
    """
    Retorna la curva de ubicacion de un elemento con LocationCurve.

    Args:
        elemento: elemento Revit

    Returns:
        Curve o None si el elemento no tiene LocationCurve

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    loc = elemento.Location
    return loc.Curve if isinstance(loc, LocationCurve) else None


def obtener_rotacion_ubicacion(elemento):
    """
    Retorna la rotacion actual de un elemento con LocationPoint en
    grados.

    Args:
        elemento: elemento Revit

    Returns:
        float en grados, o None si el elemento no tiene LocationPoint

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    loc = elemento.Location
    if isinstance(loc, LocationPoint) and hasattr(loc, "Rotation"):
        return math.degrees(loc.Rotation)
    return None


def obtener_angulo_desde_hand_orientation(elemento):
    """
    Calcula el angulo de rotacion de un elemento en grados a partir
    de su HandOrientation (angulo respecto al eje X positivo en planta).

    Args:
        elemento: FamilyInstance o elemento con HandOrientation

    Returns:
        float angulo en grados [0, 360), o None si no aplica

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        h = elemento.HandOrientation
        return math.degrees(math.atan2(h.Y, h.X)) % 360.0
    except AttributeError:
        return None


# ── Modificacion directa de ubicacion ────────────────────────────────────────

def establecer_punto_ubicacion(elemento, punto_xyz):
    """
    Asigna directamente el punto de ubicacion de un elemento.
    Alternativa a mover_elemento cuando se conoce la posicion absoluta
    destino y no el vector de desplazamiento.

    Args:
        elemento: elemento Revit con LocationPoint
        punto_xyz: XYZ de la nueva posicion absoluta

    Returns:
        True si se aplico, False si el elemento no tiene LocationPoint

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    loc = elemento.Location
    if not isinstance(loc, LocationPoint):
        return False
    _iniciar()
    loc.Point = punto_xyz
    _finalizar()
    return True


def establecer_curva_ubicacion(elemento, curva):
    """
    Asigna directamente la curva de ubicacion de un elemento.
    Permite redefinir la longitud o forma de muros, vigas, tuberias…

    Args:
        elemento: elemento Revit con LocationCurve
        curva: Curve de Revit (Line, Arc…)

    Returns:
        True si se aplico, False si el elemento no tiene LocationCurve

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    loc = elemento.Location
    if not isinstance(loc, LocationCurve):
        return False
    _iniciar()
    loc.Curve = curva
    _finalizar()
    return True


# ── Mover ─────────────────────────────────────────────────────────────────────

def mover_elemento(elemento, vector_xyz):
    """
    Mueve un elemento Revit por el vector indicado (en pies internos).

    Args:
        elemento: elemento Revit
        vector_xyz: XYZ con el desplazamiento en pies internos de Revit

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar()
    ElementTransformUtils.MoveElement(doc, elemento.Id, vector_xyz)
    _finalizar()


def mover_elemento_m(elemento, dx_m=0.0, dy_m=0.0, dz_m=0.0):
    """
    Mueve un elemento por las componentes del desplazamiento en metros.

    Args:
        elemento: elemento Revit
        dx_m: desplazamiento en X en metros
        dy_m: desplazamiento en Y en metros
        dz_m: desplazamiento en Z en metros

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    v = XYZ(
        _metros_a_pies(dx_m),
        _metros_a_pies(dy_m),
        _metros_a_pies(dz_m),
    )
    mover_elemento(elemento, v)


def mover_elementos(lista_elementos, vector_xyz):
    """
    Mueve varios elementos por el mismo vector en una sola operacion
    (MoveElements — mas eficiente que llamar MoveElement en bucle).

    Args:
        lista_elementos: lista de elementos Revit
        vector_xyz: XYZ con el desplazamiento en pies internos

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    ids = List[ElementId]([e.Id for e in lista_elementos])
    _iniciar()
    ElementTransformUtils.MoveElements(doc, ids, vector_xyz)
    _finalizar()


def alinear_a_punto(elemento, punto_destino_xyz):
    """
    Mueve un elemento para que su punto de ubicacion coincida con el
    punto destino. Calcula el vector de traslacion internamente.

    Args:
        elemento: elemento Revit con LocationPoint
        punto_destino_xyz: XYZ destino absoluto

    Returns:
        True si se movio, False si el elemento no tiene LocationPoint

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    loc = elemento.Location
    if not isinstance(loc, LocationPoint):
        return False
    vector = punto_destino_xyz - loc.Point
    mover_elemento(elemento, vector)
    return True


# ── Copiar ────────────────────────────────────────────────────────────────────

def copiar_elemento(elemento, vector_xyz):
    """
    Copia un elemento desplazado por el vector indicado.

    Args:
        elemento: elemento Revit a copiar
        vector_xyz: XYZ con el desplazamiento en pies internos

    Returns:
        elemento Revit copiado, o None si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar()
    nuevos_ids = ElementTransformUtils.CopyElement(
        doc, elemento.Id, vector_xyz)
    _finalizar()
    return doc.GetElement(list(nuevos_ids)[0]) if nuevos_ids else None


def copiar_elementos(lista_elementos, vector_xyz):
    """
    Copia varios elementos por el mismo vector en una sola operacion.

    Args:
        lista_elementos: lista de elementos Revit a copiar
        vector_xyz: XYZ con el desplazamiento en pies internos

    Returns:
        lista de elementos copiados

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    ids = List[ElementId]([e.Id for e in lista_elementos])
    _iniciar()
    nuevos_ids = ElementTransformUtils.CopyElements(doc, ids, vector_xyz)
    _finalizar()
    return [doc.GetElement(i) for i in nuevos_ids]


def copiar_elemento_a_nivel(elemento, nivel_destino):
    """
    Copia un elemento a la elevacion de un nivel diferente.
    Calcula el vector Z desde la ubicacion actual hasta el nivel destino.

    Args:
        elemento: elemento Revit
        nivel_destino: Level de Revit destino

    Returns:
        elemento copiado, o None si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    loc = elemento.Location
    if isinstance(loc, LocationPoint):
        z_actual = loc.Point.Z
    else:
        bb = elemento.BoundingBox[None]
        z_actual = bb.Min.Z if bb else 0.0
    dz = nivel_destino.ProjectElevation - z_actual
    return copiar_elemento(elemento, XYZ(0, 0, dz))


def copiar_elementos_entre_documentos(
        doc_origen, lista_ids, doc_destino,
        transform=None, opciones_pegar=None):
    """
    Copia elementos de un documento a otro aplicando un Transform.
    Cubre el patron tipico de copia desde links Revit o archivos
    abiertos en paralelo.

    Args:
        doc_origen: Document de Revit de origen
        lista_ids: lista de ElementId del documento de origen
        doc_destino: Document de Revit de destino
        transform: Transform de Revit (por defecto Transform.Identity)
        opciones_pegar: CopyPasteOptions (opcional)

    Returns:
        lista de elementos en el documento destino

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if transform is None:
        transform = Transform.Identity
    ids_net = List[ElementId](lista_ids)
    _iniciar()
    nuevos_ids = ElementTransformUtils.CopyElements(
        doc_origen, ids_net, doc_destino, transform, opciones_pegar)
    _finalizar()
    return [doc_destino.GetElement(i) for i in nuevos_ids]


# ── Rotar ─────────────────────────────────────────────────────────────────────

def rotar_elemento(elemento, punto_xyz, angulo_grados, eje_xyz=None):
    """
    Rota un elemento alrededor de un eje que pasa por el punto dado.

    Args:
        elemento: elemento Revit
        punto_xyz: XYZ punto por el que pasa el eje de rotacion
        angulo_grados: angulo de rotacion en grados (positivo =
            antihorario visto desde arriba si eje es Z)
        eje_xyz: XYZ vector de direccion del eje (por defecto Z
            vertical = rotacion en planta)

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if eje_xyz is None:
        eje_xyz = XYZ.BasisZ
    eje_linea = Line.CreateBound(punto_xyz, punto_xyz + eje_xyz)
    _iniciar()
    ElementTransformUtils.RotateElement(
        doc, elemento.Id, eje_linea, _rad(angulo_grados))
    _finalizar()


def rotar_elemento_en_propio_punto(elemento, angulo_grados,
                                    eje_xyz=None):
    """
    Rota un elemento alrededor de su propio punto de ubicacion.
    Si no tiene LocationPoint, usa el centroide del BoundingBox.

    Args:
        elemento: elemento Revit
        angulo_grados: angulo de rotacion en grados
        eje_xyz: XYZ vector de eje (por defecto Z = rotacion en planta)

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    loc = elemento.Location
    if isinstance(loc, LocationPoint):
        punto = loc.Point
    else:
        bb = elemento.BoundingBox[None]
        if bb is None:
            return
        punto = XYZ(
            (bb.Min.X + bb.Max.X) / 2.0,
            (bb.Min.Y + bb.Max.Y) / 2.0,
            (bb.Min.Z + bb.Max.Z) / 2.0,
        )
    rotar_elemento(elemento, punto, angulo_grados, eje_xyz)


def rotar_elementos(lista_elementos, punto_xyz, angulo_grados,
                    eje_xyz=None):
    """
    Rota varios elementos alrededor de un eje en una sola operacion.

    Args:
        lista_elementos: lista de elementos Revit
        punto_xyz: XYZ punto por el que pasa el eje de rotacion
        angulo_grados: angulo de rotacion en grados
        eje_xyz: XYZ vector de eje (por defecto Z = rotacion en planta)

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if eje_xyz is None:
        eje_xyz = XYZ.BasisZ
    eje_linea = Line.CreateBound(punto_xyz, punto_xyz + eje_xyz)
    ids = List[ElementId]([e.Id for e in lista_elementos])
    _iniciar()
    ElementTransformUtils.RotateElements(
        doc, ids, eje_linea, _rad(angulo_grados))
    _finalizar()


def rotar_vista(vista, punto_xyz, angulo_grados):
    """
    Rota una vista (seccion, alzado, etc.) alrededor de un punto en
    el eje Z. Util para ajustar la orientacion de secciones.

    Args:
        vista: View de Revit (ViewSection, View3D…)
        punto_xyz: XYZ punto por el que pasa el eje
        angulo_grados: angulo de rotacion en grados

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    eje_linea = Line.CreateBound(
        punto_xyz, XYZ(punto_xyz.X, punto_xyz.Y, punto_xyz.Z + 1))
    _iniciar()
    ElementTransformUtils.RotateElement(
        doc, vista.Id, eje_linea, _rad(angulo_grados))
    _finalizar()


# ── Espejar ───────────────────────────────────────────────────────────────────

def crear_plano_espejo(normal_xyz, origen_xyz):
    """
    Crea un Plane de Revit definido por su normal y un punto de origen.
    Argumento tipico para las funciones de espejado.

    Args:
        normal_xyz: XYZ vector normal al plano (debe ser unitario)
        origen_xyz: XYZ punto perteneciente al plano

    Returns:
        Plane de Revit

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return Plane.CreateByNormalAndOrigin(normal_xyz, origen_xyz)


def espejar_elementos(lista_elementos, normal_xyz, origen_xyz,
                      crear_copia=True):
    """
    Espeja una lista de elementos respecto a un plano definido por
    normal y origen.

    Args:
        lista_elementos: lista de elementos Revit
        normal_xyz: XYZ vector normal al plano de espejado
        origen_xyz: XYZ punto en el plano de espejado
        crear_copia: True → crea copias espejadas, originales intactos;
            False → espeja los elementos en su sitio (modifica)

    Returns:
        lista de ElementId resultantes

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    plano = Plane.CreateByNormalAndOrigin(normal_xyz, origen_xyz)
    ids = List[ElementId]([e.Id for e in lista_elementos])
    _iniciar()
    resultados = ElementTransformUtils.MirrorElements(
        doc, ids, plano, not crear_copia)
    _finalizar()
    return list(resultados)


def espejar_elemento(elemento, normal_xyz, origen_xyz,
                     crear_copia=True):
    """
    Espeja un unico elemento respecto a un plano.

    Args:
        elemento: elemento Revit
        normal_xyz: XYZ vector normal al plano de espejado
        origen_xyz: XYZ punto en el plano de espejado
        crear_copia: True para crear copia espejada; False para
            espejar in-situ

    Returns:
        lista de ElementId resultantes

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return espejar_elementos(
        [elemento], normal_xyz, origen_xyz, crear_copia)


# ── Voltear (Flip) ────────────────────────────────────────────────────────────

def voltear_elemento(elemento):
    """
    Voltea un elemento usando su metodo Flip().
    Para muros invierte la cara exterior; para puertas/ventanas voltea
    el sentido de apertura; para otros elementos su semantica varia.

    Args:
        elemento: elemento Revit que soporte Flip()

    Returns:
        True si se volteo correctamente, False si no aplica

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar()
    try:
        elemento.Flip()
        _finalizar()
        return True
    except Exception:
        _finalizar()
        return False


def voltear_cara(instancia_familia):
    """
    Voltea la orientacion de cara (FacingFlipped) de una FamilyInstance.
    Invierte la direccion en la que esta mirando el elemento.

    Args:
        instancia_familia: FamilyInstance de Revit

    Returns:
        True si se volteo, False si no aplica

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar()
    try:
        try:
            instancia_familia.flipFacing()
        except AttributeError:
            instancia_familia.FlipFacing()
        _finalizar()
        return True
    except Exception:
        _finalizar()
        return False


def voltear_mano(instancia_familia):
    """
    Voltea la orientacion de mano (HandFlipped) de una FamilyInstance.
    Invierte el lado izquierda/derecha del elemento.

    Args:
        instancia_familia: FamilyInstance de Revit

    Returns:
        True si se volteo, False si no aplica

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar()
    try:
        try:
            instancia_familia.flipHand()
        except AttributeError:
            instancia_familia.FlipHand()
        _finalizar()
        return True
    except Exception:
        _finalizar()
        return False


def voltear_extremos_viga(viga):
    """
    Voltea los extremos inicio/fin de una viga estructural.
    Afecta a la asignacion de condiciones de contorno y al offset de
    cada extremo.

    Args:
        viga: elemento Revit de tipo viga estructural

    Returns:
        True si se volteo, False si falla

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar()
    try:
        StructuralFramingUtils.FlipEnds(viga)
        _finalizar()
        return True
    except Exception:
        _finalizar()
        return False


# ── Anclar / Desanclar ────────────────────────────────────────────────────────

def anclar_elemento(elemento, anclar=True):
    """
    Ancla o desancla un elemento (propiedad Pinned).
    Los elementos anclados no pueden moverse hasta ser desanclados.

    Args:
        elemento: elemento Revit
        anclar: True para anclar, False para desanclar

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar()
    elemento.Pinned = anclar
    _finalizar()


def desanclar_elemento(elemento):
    """
    Desancla un elemento anclado. Equivale a anclar_elemento(e, False).

    Args:
        elemento: elemento Revit

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    anclar_elemento(elemento, False)


def esta_anclado(elemento):
    """
    Retorna si un elemento esta anclado (Pinned).

    Args:
        elemento: elemento Revit

    Returns:
        True si esta anclado, False en caso contrario

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return bool(elemento.Pinned)


def anclar_lista(lista_elementos, anclar=True):
    """
    Ancla o desancla una lista de elementos en bloque.

    Args:
        lista_elementos: lista de elementos Revit
        anclar: True para anclar, False para desanclar

    Returns:
        numero de elementos modificados

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    _iniciar()
    count = 0
    for e in lista_elementos:
        try:
            e.Pinned = anclar
            count += 1
        except Exception:
            pass
    _finalizar()
    return count


# ── Consultas de orientacion ──────────────────────────────────────────────────

def obtener_orientacion_mano(elemento):
    """
    Retorna el vector HandOrientation de una FamilyInstance o elemento
    estructural. Indica la direccion de la "mano" del elemento.

    Args:
        elemento: elemento Revit con HandOrientation

    Returns:
        XYZ vector, o None si no aplica

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        return elemento.HandOrientation
    except AttributeError:
        return None


def obtener_orientacion_cara(elemento):
    """
    Retorna el vector FacingOrientation de una FamilyInstance.
    Indica hacia donde "mira" el elemento.

    Args:
        elemento: FamilyInstance de Revit

    Returns:
        XYZ vector, o None si no aplica

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        return elemento.FacingOrientation
    except AttributeError:
        return None


def obtener_esta_espejado(instancia):
    """
    Indica si una FamilyInstance esta espejada (Mirrored).

    Args:
        instancia: FamilyInstance de Revit

    Returns:
        True si esta espejada, False si no o si no aplica

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        return bool(instancia.Mirrored)
    except AttributeError:
        return False


def obtener_esta_volteado_cara(instancia):
    """
    Indica si la cara (FacingFlipped) de una FamilyInstance esta
    volteada respecto al estado original de la familia.

    Args:
        instancia: FamilyInstance de Revit

    Returns:
        True si FacingFlipped, False en caso contrario o si no aplica

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        return bool(instancia.FacingFlipped)
    except AttributeError:
        return False


def obtener_esta_volteado_mano(instancia):
    """
    Indica si la mano (HandFlipped) de una FamilyInstance esta
    volteada respecto al estado original de la familia.

    Args:
        instancia: FamilyInstance de Revit

    Returns:
        True si HandFlipped, False en caso contrario o si no aplica

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        return bool(instancia.HandFlipped)
    except AttributeError:
        return False


def obtener_orientacion_completa(instancia):
    """
    Retorna un dict con toda la informacion de orientacion de una
    FamilyInstance.

    Args:
        instancia: FamilyInstance de Revit

    Returns:
        dict con claves:
          "hand":          XYZ HandOrientation o None
          "facing":        XYZ FacingOrientation o None
          "espejado":      bool Mirrored
          "cara_volteada": bool FacingFlipped
          "mano_volteada": bool HandFlipped
          "angulo_grados": float angulo en planta o None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    hand = obtener_orientacion_mano(instancia)
    angulo = None
    if hand is not None:
        angulo = math.degrees(math.atan2(hand.Y, hand.X)) % 360.0
    return {
        "hand": hand,
        "facing": obtener_orientacion_cara(instancia),
        "espejado": obtener_esta_espejado(instancia),
        "cara_volteada": obtener_esta_volteado_cara(instancia),
        "mano_volteada": obtener_esta_volteado_mano(instancia),
        "angulo_grados": angulo,
    }


# ── Matematica de Transform ───────────────────────────────────────────────────

def crear_transform_traslacion(vector_xyz):
    """
    Crea un Transform de traslacion pura a partir de un vector.

    Args:
        vector_xyz: XYZ vector de traslacion en pies internos

    Returns:
        Transform

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return Transform.CreateTranslation(vector_xyz)


def crear_transform_rotacion(eje_xyz, angulo_grados):
    """
    Crea un Transform de rotacion alrededor de un eje unitario.

    Args:
        eje_xyz: XYZ vector unitario del eje de rotacion
        angulo_grados: angulo de rotacion en grados

    Returns:
        Transform

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return Transform.CreateRotation(eje_xyz, _rad(angulo_grados))


def crear_transform_por_ejes(origen_xyz, eje_x, eje_y, eje_z=None):
    """
    Construye un Transform a partir de un origen y vectores de ejes.
    Util para definir sistemas de coordenadas locales: secciones,
    BoundingBoxXYZ de corte, etc.

    Args:
        origen_xyz: XYZ origen del sistema de coordenadas
        eje_x:      XYZ vector unitario del eje X local
        eje_y:      XYZ vector unitario del eje Y local
        eje_z:      XYZ vector del eje Z (si es None se calcula
                    como eje_x cross eje_y)

    Returns:
        Transform

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if eje_z is None:
        eje_z = eje_x.CrossProduct(eje_y)
    t = Transform.Identity
    t.Origin = origen_xyz
    t.BasisX = eje_x
    t.BasisY = eje_y
    t.BasisZ = eje_z
    return t


def transformar_punto(transform, punto_xyz):
    """
    Aplica un Transform a un punto XYZ (incluye traslacion).

    Args:
        transform: Transform de Revit
        punto_xyz: XYZ punto a transformar

    Returns:
        XYZ punto transformado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return transform.OfPoint(punto_xyz)


def transformar_vector(transform, vector_xyz):
    """
    Aplica un Transform a un vector XYZ (solo rotacion, sin traslacion).

    Args:
        transform: Transform de Revit
        vector_xyz: XYZ vector a transformar

    Returns:
        XYZ vector transformado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return transform.OfVector(vector_xyz)


def invertir_transform(transform):
    """
    Retorna el Transform inverso.
    Util para pasar de coordenadas globales a locales y viceversa
    (por ejemplo para convertir puntos del host al espacio del link).

    Args:
        transform: Transform de Revit

    Returns:
        Transform inverso

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return transform.Inverse


def combinar_transforms(transform_a, transform_b):
    """
    Combina dos Transform en secuencia (A seguido de B).
    Equivale a aplicar primero transform_a y despues transform_b.

    Args:
        transform_a: Transform de Revit (se aplica primero)
        transform_b: Transform de Revit (se aplica segundo)

    Returns:
        Transform combinado

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return transform_b.Multiply(transform_a)


def obtener_transform_elemento(elemento):
    """
    Retorna el Transform de una FamilyInstance u otro elemento con
    geometria instanciada. Describe la posicion y orientacion del
    elemento en coordenadas del proyecto.

    Args:
        elemento: FamilyInstance u elemento con GetTransform()

    Returns:
        Transform del elemento, o None si no aplica

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    try:
        return elemento.GetTransform()
    except AttributeError:
        return None


# ── Utilidades geometricas ────────────────────────────────────────────────────

def vector_entre_puntos(punto_origen, punto_destino):
    """
    Calcula el vector de desplazamiento entre dos puntos XYZ.
    Util como argumento para mover_elemento o copiar_elemento.

    Args:
        punto_origen:  XYZ punto de partida
        punto_destino: XYZ punto de llegada

    Returns:
        XYZ vector (punto_destino - punto_origen)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return punto_destino - punto_origen


def distancia_entre_puntos_m(punto_a, punto_b):
    """
    Calcula la distancia entre dos puntos XYZ en metros.

    Args:
        punto_a: XYZ primer punto
        punto_b: XYZ segundo punto

    Returns:
        float distancia en metros

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return _pies_a_metros(punto_a.DistanceTo(punto_b))


def centroide_bbox(elemento):
    """
    Retorna el centroide del BoundingBox de un elemento en coordenadas
    del proyecto.

    Args:
        elemento: elemento Revit

    Returns:
        XYZ centroide, o None si el elemento no tiene BoundingBox

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    bb = elemento.BoundingBox[None]
    if bb is None:
        return None
    return XYZ(
        (bb.Min.X + bb.Max.X) / 2.0,
        (bb.Min.Y + bb.Max.Y) / 2.0,
        (bb.Min.Z + bb.Max.Z) / 2.0,
    )
