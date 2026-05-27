# RevitPythonLibrary

Biblioteca modular de funciones Python para Revit/Dynamo, organizada por disciplina.
Derivada y refactorizada a partir de `LibreriaFunciones.py` (Kevin Himmelreich).

## Requisitos

| Componente | Version |
|---|---|
| Autodesk Revit | 2024 – 2026 |
| Dynamo | 2.x o superior |
| Python (dentro de Dynamo) | IronPython 2.7 **o** CPython 3.x (Dynamo 2.13+) |

## Estructura de modulos

| Archivo | Contenido |
|---|---|
| `lib_general.py` | Unwrap, transacciones, parametros, conversiones de unidades, utilidades Python |
| `lib_transformaciones.py` | Mover, copiar, rotar, espejar, voltear, anclar, orientacion, transform math |
| `lib_coordinacion.py` | Niveles, advertencias, worksets, links Revit, colisiones, exportacion CSV |
| `lib_arquitectura.py` | Habitaciones, muros, suelos, carpinteria, areas, barandillas |
| `lib_instalaciones.py` | Conductos, tuberias, bandejas, conduits, equipos MEP, luminarias |
| `lib_estructura.py` | Pilares, vigas, forjados, armaduras, cargas estructurales |
| `lib_geometria.py` | Curvas, CurveLoop, solidos, booleanas, DirectShape, A* pathfinding |
| `lib_vistas.py` | Vistas 3D/planta/seccion, cartelas, overrides, export imagen |
| `lib_familias.py` | Carga, exportacion, instanciacion y gestion de familias |
| `lib_cad.py` | Importacion y analisis de archivos CAD (DWG/DXF): capas, curvas, bloques |
| `lib_excel.py` | Lectura/escritura Excel via DSOffice y COM Interop; pandas |
| `lib_bases_datos.py` | JSON, CSV, exportacion IFC, schedules, GUIDs; pandas |
| `lib_colaborativo.py` | Worksharing: activar colaborativo, guardar central, worksets |
| `lib_transacciones.py` | TransactionGroup, Transaction nativa, SubTransaction |
| `lib_seleccion_ui.py` | Seleccion interactiva: elemento, cara, arista, punto, rectangulo, link |
| `lib_scientific.py` | pandas, numpy, scipy, matplotlib, shapely, networkx + Revit API |
| `lib_ui.py` | Ventanas WPF: texto, numero, opciones, archivos, progreso, tabla |
| `lib_completa.py` | Importa todos los modulos con `from lib_completa import *` |

## Uso basico en Dynamo

```python
import sys
sys.path.append("C:/ruta/a/RevitPythonLibrary")

from lib_general import pies_a_metros, obtener_valor_parametro
from lib_arquitectura import obtener_habitaciones, crear_suelo_desde_habitacion
```

---

## Referencia de funciones

### lib_general — Utilidades base

#### Parametros y elementos

| Funcion | Descripcion |
|---|---|
| `unwrap(elem)` | Desenvuelve un elemento Dynamo al elemento Revit nativo |
| `unwrap_lista(elems)` | Desenvuelve una lista de elementos Dynamo |
| `id_a_int(element_id)` | Convierte ElementId a int, compatible Revit 2024+ |
| `iniciar_transaccion(nombre)` | Inicia o reanuda la transaccion Dynamo activa |
| `finalizar_transaccion()` | Marca la tarea de transaccion como completada |
| `obtener_valor_parametro(elem, nombre)` | Lee el valor de un parametro de instancia por nombre |
| `establecer_valor_parametro(elem, nombre, val)` | Escribe el valor de un parametro de instancia |
| `obtener_todos_parametros(elem)` | Todos los parametros de instancia como dict {nombre: valor} |
| `obtener_parametros_tipo(elem)` | Todos los parametros de TIPO como dict {nombre: valor} |
| `agrupar_por_parametro(elems, nombre)` | Agrupa elementos por valor de un parametro |
| `filtrar_por_valor_parametro(cat, nombre, val)` | Filtra elementos del modelo por valor de parametro (texto) |
| `obtener_ids_int(elems)` | Lista de IDs enteros de los elementos dados |
| `aplanar_lista(lista)` | Aplana recursivamente una lista anidada |

#### Conversiones de unidades

| Funcion | Descripcion |
|---|---|
| `pies_a_metros(v)` | Convierte pies internos de Revit a metros |
| `metros_a_pies(v)` | Convierte metros a pies internos de Revit |
| `mm_a_pies(v)` | Convierte milimetros a pies internos |
| `pies_a_mm(v)` | Convierte pies internos a milimetros |
| `m2_a_pies2(v)` | Convierte m2 a pies2 internos |
| `pies2_a_m2(v)` | Convierte pies2 internos a m2 |

#### Eliminar elementos

| Funcion | Descripcion |
|---|---|
| `eliminar_elemento(elem)` | Elimina un elemento del documento |

#### Filtros avanzados (BoundingBox y logicos)

| Funcion | Descripcion |
|---|---|
| `filtrar_por_boundingbox(bbox, cat_bic, tol)` | Elementos cuyo bbox intersecta con el bbox dado (BoundingBoxIntersectsFilter) |
| `filtrar_dentro_de_bbox(bbox, cat_bic, tol)` | Elementos completamente contenidos en el bbox (BoundingBoxIsInsideFilter) |
| `filtrar_contiene_punto(punto, cat_bic, tol)` | Elementos cuyo bbox contiene el punto XYZ dado |
| `combinar_filtros_o(filtros)` | Combina ElementFilters con logica OR (LogicalOrFilter) |
| `combinar_filtros_y(filtros)` | Combina ElementFilters con logica AND (LogicalAndFilter) |
| `excluir_elementos(ids, cat_bic)` | Todos los elementos excepto los ids dados (ExclusionFilter) |
| `obtener_anotaciones_en_vista(vista, cat_bic)` | Anotaciones/etiquetas propias de una vista (ElementOwnerViewFilter) |
| `obtener_elementos_visibles_en_vista(vista, cat_bic)` | Elementos de modelo visibles en la vista |

#### Grupos y ensamblajes

| Funcion | Descripcion |
|---|---|
| `crear_grupo(elementos)` | Crea un Group a partir de una lista de elementos |
| `desagrupar(grupo)` | Desagrupa un Group y retorna los ElementId liberados |
| `obtener_miembros_grupo(grupo)` | Elementos miembro de un Group sin desagruparlo |
| `obtener_grupos()` | Todos los Group del documento |
| `crear_ensamblaje(elementos, nombre)` | Crea un AssemblyInstance a partir de una lista de elementos |
| `obtener_miembros_ensamblaje(ensamblaje)` | Elementos miembro de un AssemblyInstance |

#### Planos de referencia y ejes

| Funcion | Descripcion |
|---|---|
| `crear_plano_referencia(p1, p2, nombre)` | Crea un ReferencePlane entre dos puntos |
| `crear_eje(p1, p2, nombre)` | Crea un Grid (eje de proyecto) entre dos puntos |
| `obtener_ejes()` | Todos los Grid del documento |
| `obtener_planos_referencia()` | Todos los ReferencePlane del documento |

---

### lib_transformaciones — Transformaciones y movimiento

#### Ubicacion de elementos

| Funcion | Descripcion |
|---|---|
| `obtener_ubicacion(elem)` | Location raw del elemento (LocationPoint o LocationCurve) |
| `obtener_punto_ubicacion(elem)` | XYZ del punto de insercion (LocationPoint) |
| `obtener_curva_ubicacion(elem)` | Curva de ubicacion (LocationCurve) |
| `obtener_rotacion_ubicacion(elem)` | Angulo de rotacion en grados (LocationPoint.Rotation) |
| `obtener_angulo_desde_hand_orientation(instancia)` | Angulo en grados del vector HandOrientation en planta |
| `establecer_punto_ubicacion(elem, punto_xyz)` | Asigna directamente el punto de insercion |
| `establecer_curva_ubicacion(elem, curva)` | Asigna directamente la curva de ubicacion |

#### Mover

| Funcion | Descripcion |
|---|---|
| `mover_elemento(elem, vector_xyz)` | Mueve un elemento por un vector XYZ en pies |
| `mover_elemento_m(elem, dx_m, dy_m, dz_m)` | Mueve un elemento por desplazamientos en metros |
| `mover_elementos(lista_elems, vector_xyz)` | Mueve varios elementos con un solo comando |
| `alinear_a_punto(elem, punto_xyz)` | Mueve el elemento para que su LocationPoint coincida con el punto |

#### Copiar

| Funcion | Descripcion |
|---|---|
| `copiar_elemento(elem, vector_xyz)` | Copia un elemento desplazado por un vector |
| `copiar_elementos(lista_elems, vector_xyz)` | Copia varios elementos con un desplazamiento |
| `copiar_elemento_a_nivel(elem, nivel_destino)` | Copia el elemento al nivel destino ajustando Z |
| `copiar_elementos_entre_documentos(elems, doc_destino, tf)` | Copia elementos a otro documento con transformacion opcional |

#### Rotar

| Funcion | Descripcion |
|---|---|
| `rotar_elemento(elem, eje_linea, angulo_grados)` | Rota un elemento alrededor de un eje Line |
| `rotar_elemento_en_propio_punto(elem, angulo_grados)` | Rota el elemento alrededor de su LocationPoint (eje Z) |
| `rotar_elementos(lista_elems, eje_linea, angulo_grados)` | Rota varios elementos alrededor del mismo eje |
| `rotar_vista(vista, angulo_grados)` | Rota una vista de planta alrededor de su centro |

#### Espejar

| Funcion | Descripcion |
|---|---|
| `crear_plano_espejo(normal_xyz, origen_xyz)` | Crea un Plane por normal y origen para usar como espejo |
| `espejar_elementos(lista_elems, normal_xyz, origen_xyz, crear_copia)` | Espeja elementos; crear_copia=False hace mirror in-place |
| `espejar_elemento(elem, normal_xyz, origen_xyz, crear_copia)` | Espeja un unico elemento |

#### Voltear (Flip)

| Funcion | Descripcion |
|---|---|
| `voltear_elemento(instancia)` | Voltea la instancia con el flip principal disponible |
| `voltear_cara(instancia)` | Flip de la cara (FacingOrientation) — flipFacing / FlipFacing |
| `voltear_mano(instancia)` | Flip de la mano (HandOrientation) — flipHand / FlipHand |
| `voltear_extremos_viga(viga)` | Invierte los extremos de una viga estructural (FlipEnds) |

#### Anclar

| Funcion | Descripcion |
|---|---|
| `anclar_elemento(elem)` | Fija (pina) un elemento para que no se mueva |
| `desanclar_elemento(elem)` | Libera el elemento anclado |
| `esta_anclado(elem)` | True si el elemento esta anclado |
| `anclar_lista(elems, anclar)` | Ancla o desancla una lista de elementos |

#### Orientacion y estado de flip

| Funcion | Descripcion |
|---|---|
| `obtener_orientacion_mano(instancia)` | Vector HandOrientation de la instancia |
| `obtener_orientacion_cara(instancia)` | Vector FacingOrientation de la instancia |
| `obtener_esta_espejado(instancia)` | True si la instancia esta espejada (Mirrored) |
| `obtener_esta_volteado_cara(instancia)` | True si FacingFlipped es True |
| `obtener_esta_volteado_mano(instancia)` | True si HandFlipped es True |
| `obtener_orientacion_completa(instancia)` | Dict con mano, cara, espejado, flip_cara, flip_mano |

#### Matematica de Transform

| Funcion | Descripcion |
|---|---|
| `crear_transform_traslacion(vector_xyz)` | Transform de traslacion pura |
| `crear_transform_rotacion(origen_xyz, eje_xyz, angulo_grados)` | Transform de rotacion alrededor de eje en origen |
| `crear_transform_por_ejes(origen_xyz, eje_x, eje_y, eje_z)` | Transform a partir de origen y vectores de eje |
| `transformar_punto(punto_xyz, transform)` | Aplica un Transform a un punto XYZ |
| `transformar_vector(vector_xyz, transform)` | Aplica un Transform a un vector (sin traslacion) |
| `invertir_transform(transform)` | Inverse de un Transform |
| `combinar_transforms(t1, t2)` | Composicion de dos Transform (t1 primero, t2 segundo) |
| `obtener_transform_elemento(instancia)` | Transform de un elemento vinculado o instancia de familia |

#### Utilidades geometricas

| Funcion | Descripcion |
|---|---|
| `vector_entre_puntos(p1_xyz, p2_xyz)` | Vector XYZ normalizado de p1 a p2 |
| `distancia_entre_puntos_m(p1_xyz, p2_xyz)` | Distancia entre dos XYZ en metros |
| `centroide_bbox(elem)` | Centroide del BoundingBox de un elemento |

---

### lib_coordinacion — Coordinacion BIM

| Funcion | Descripcion |
|---|---|
| `crear_nivel(elevacion_m, nombre)` | Crea un Level en la elevacion dada |
| `crear_niveles_en_bloque(elevaciones_m, nombres)` | Crea multiples niveles en una sola transaccion |
| `analizar_advertencias_por_tipo()` | Agrupa advertencias activas por tipo; retorna lista de dicts |
| `exportar_advertencias_a_csv(ruta_csv)` | Exporta advertencias agrupadas a CSV |
| `asignar_workset_a_lista(elems, workset_id)` | Asignacion masiva de workset; retorna numero asignados |
| `asignar_workset_por_categoria(cat_bic, workset_id)` | Asigna workset a todos los elementos de una categoria |
| `establecer_visibilidad_workset(workset_id, visible)` | Controla visibilidad por defecto de un workset |
| `detectar_elementos_sin_workset(elems, workset_id)` | QA: elementos que no pertenecen al workset esperado |
| `obtener_elementos_en_link(link, categorias_bic)` | FEC en documento vinculado; retorna (elementos, transform) |
| `obtener_elemento_en_link_por_unique_id(link, uid)` | Elemento de un link buscado por UniqueId |
| `filtrar_en_link_por_parametro(link, cat, param, val)` | Filtra en link por valor de parametro de instancia |
| `filtrar_en_link_por_boundingbox(link, bbox, cat, tol)` | Elementos del link cuyo bbox intersecta bbox del host |
| `filtrar_en_link_dentro_de_bbox(link, bbox, cat, tol)` | Elementos del link completamente dentro del bbox del host |
| `filtrar_en_link_contiene_punto(link, punto, cat, tol)` | Elementos del link cuyo bbox contiene el punto del host |
| `adquirir_coordenadas_de_link(link)` | Adquiere coordenadas del proyecto desde un link Revit |
| `copiar_elementos_desde_link(link, ids, opciones)` | Copia elementos de un link al documento activo |
| `comparar_parametro_en_link(elems_host, link, param)` | Compara parametro entre host y link por UniqueId |
| `detectar_colisiones_bbox(elems_a, elems_b, tol)` | Deteccion de colisiones por bounding box |
| `detectar_colisiones_solidos(elems_a, elems_b)` | Deteccion exacta de colisiones por solidos booleanos |
| `exportar_parametros_a_csv(elems, params, ruta)` | Exporta parametros de elementos a CSV |
| `contar_elementos_por_nivel(cat_bic)` | Dict {nombre_nivel: cantidad} de elementos de una categoria |
| `detectar_elementos_duplicados(cat_bic, tol)` | Agrupa elementos por proximidad de centroide |

---

### lib_arquitectura — Arquitectura

#### Habitaciones

| Funcion | Descripcion |
|---|---|
| `obtener_habitaciones(incluir_sin_colocar)` | Todas las habitaciones del documento |
| `obtener_nombre_habitacion(hab)` | Nombre de una habitacion |
| `obtener_numero_habitacion(hab)` | Numero de una habitacion |
| `obtener_area_habitacion(hab)` | Area en m2 |
| `obtener_habitaciones_por_nivel(nivel)` | Habitaciones de un nivel concreto |
| `obtener_centroide_habitacion(hab)` | Centroide XYZ de una habitacion |
| `obtener_contorno_habitacion(hab)` | Tupla (elementos_limite, curvas_limite) |
| `obtener_curveloops_habitacion(hab)` | Lista de CurveLoop del contorno (exterior e islas) |
| `obtener_elementos_en_habitacion(hab)` | Elementos dentro de la habitacion via RoomFilter |
| `obtener_puertas_de_habitacion(hab)` | Puertas asociadas a la habitacion (FromRoom/ToRoom) |
| `obtener_ventanas_de_habitacion(hab)` | Ventanas en los muros que delimitan la habitacion |
| `obtener_area_total_habitaciones()` | Area total de todas las habitaciones colocadas |
| `calcular_volumen_habitacion(hab)` | Volumen en m3 via SpatialElementGeometryCalculator |
| `calcular_ratio_acristalamiento(hab)` | Dict {area_hab, area_ventanas, ratio, ventanas} |
| `agrupar_habitaciones_por_nivel()` | Dict {nombre_nivel: [habitaciones]} |
| `clasificar_habitaciones_por_nombre(habs, regex)` | Agrupa por patron regex en el nombre |
| `clasificar_habitaciones_por_estado()` | Tupla (colocadas, no_colocadas, no_cerradas, redundantes) |
| `detectar_habitaciones_sin_numero()` | QA: habitaciones colocadas sin numero asignado |
| `detectar_habitaciones_duplicadas(tol)` | Grupos de habitaciones en la misma posicion |
| `renumerar_habitaciones_por_nivel(prefijo, inicio)` | Renumeracion sistematica por nivel |

#### Muros y carpinteria

| Funcion | Descripcion |
|---|---|
| `obtener_carpinteria()` | Puertas y ventanas combinadas del documento |
| `obtener_muros_por_tipo(nombre_tipo)` | Muros filtrados por nombre de tipo |
| `obtener_grosor_muro(muro)` | Grosor total en mm |
| `obtener_composicion_muro(muro)` | Capas del muro: funcion, material, grosor, es_estructural |
| `modificar_grosor_capa_estructural(tipo_muro, mm)` | Modifica el grosor de la capa estructural del tipo |
| `crear_muro(curva, nivel, tipo_id, altura_mm)` | Crea un muro lineal |

#### Suelos

| Funcion | Descripcion |
|---|---|
| `obtener_area_suelo(suelo)` | Area de un suelo en m2 |
| `crear_suelo(curvas, tipo_id, nivel)` | Crea un suelo desde un contorno de curvas |
| `crear_suelo_desde_habitacion(hab, tipo_id, curvas_extra, tol)` | Suelo desde contorno de habitacion con umbrales de puertas opcionales |
| `crear_abertura_suelo(suelo, curvas)` | Crea una abertura en un suelo |

#### Areas y barandillas

| Funcion | Descripcion |
|---|---|
| `crear_separacion_de_area(vista, curvas, plano)` | Crea lineas de separacion de area |

#### pandas *(CPython)*

| Funcion | Descripcion |
|---|---|
| `dataframe_habitaciones(habs)` | Habitaciones a DataFrame |
| `estadisticas_habitaciones_pandas(habs)` | Estadisticas descriptivas de area y volumen |

---

### lib_instalaciones — MEP / Instalaciones

| Funcion | Descripcion |
|---|---|
| `obtener_longitud_conducto(conducto)` | Longitud de un conducto en metros |
| `obtener_longitud_tuberia(tuberia)` | Longitud de una tuberia en metros |
| `obtener_diametro_exterior_tuberia(tub)` | Diametro exterior en mm |
| `obtener_sistema_tuberia(tub)` | Nombre del sistema de una tuberia |
| `agrupar_tuberias_por_sistema()` | Dict {nombre_sistema: [tuberias]} |
| `agrupar_conductos_por_sistema()` | Dict {nombre_sistema: [conductos]} |
| `obtener_longitud_total_conductos()` | Longitud total de conductos en metros |
| `obtener_longitud_total_tuberias()` | Longitud total de tuberias en metros |
| `crear_bandeja_cable(p1, p2, ancho, alto)` | Crea una bandeja de cables entre dos puntos |
| `dataframe_tuberias(tubs)` | Tuberias a DataFrame *(CPython)* |
| `dataframe_conductos(conds)` | Conductos a DataFrame *(CPython)* |
| `estadisticas_sistemas_pandas(tubs, conds)` | Estadisticas de longitud por sistema *(CPython)* |

---

### lib_estructura — Estructura

#### Propiedades y filtros

| Funcion | Descripcion |
|---|---|
| `obtener_longitud_viga(viga)` | Longitud de una viga en metros |
| `obtener_altura_pilar(pilar)` | Altura de un pilar en metros |
| `obtener_nivel_base_pilar(pilar)` | Level base de un pilar |
| `obtener_nivel_alto_pilar(pilar)` | Level superior de un pilar |
| `obtener_material_estructura(elem)` | Nombre del material estructural de viga o pilar |
| `obtener_propiedades_viga(viga)` | Dict con extensiones, justificaciones y offsets de una viga |
| `obtener_pilares_por_nivel(nivel)` | Pilares cuyo nivel base coincide |
| `obtener_vigas_por_nivel(nivel)` | Vigas cuyo nivel de referencia coincide |
| `agrupar_vigas_por_nivel()` | Dict {nombre_nivel: [vigas]} con todas las vigas |
| `obtener_area_forjado(forjado)` | Area de un forjado en m2 |
| `obtener_area_total_forjados()` | Area total de todos los forjados en m2 |
| `obtener_materiales_usados()` | Nombres de materiales unicos en vigas y pilares |
| `calcular_volumen_hormigon(categorias_bic)` | Volumen total de hormigon en m3 |

#### Creacion de elementos

| Funcion | Descripcion |
|---|---|
| `crear_viga(curva, nivel, tipo_id)` | Crea una viga estructural |
| `crear_pilar_vertical(punto, nivel, tipo_id)` | Crea un pilar vertical en la posicion indicada |
| `crear_pilar_inclinado(p_base, p_top, nivel, tipo_id)` | Crea un pilar inclinado entre dos puntos XYZ |

#### Armaduras

| Funcion | Descripcion |
|---|---|
| `crear_armadura(elem, tipo_barra_id, curvas, ...)` | Crea una Rebar en un elemento estructural |
| `distribuir_armadura_numero_fijo(rebar, n, longitud)` | Distribucion con numero fijo de barras |
| `distribuir_armadura_separacion_maxima(rebar, sep_mm, long)` | Distribucion con separacion maxima |
| `distribuir_armadura_separacion_minima(rebar, sep_mm, long)` | Distribucion con separacion minima |
| `establecer_armadura_solida_en_vista(rebar, vista)` | Representacion solida de armadura en vista |
| `obtener_armaduras_de_elemento(elem)` | Todas las Rebar anfitrionadas en un elemento |
| `crear_armado_por_area(suelo, tipo_id)` | Crea un AreaReinforcement en un suelo |
| `obtener_recubrimientos(elem)` | Dict de recubrimientos en mm (general, inferior, superior, ...) |

#### Cargas

| Funcion | Descripcion |
|---|---|
| `crear_carga_puntual(punto, fuerza, momento, nivel)` | Crea una PointLoad libre |
| `crear_carga_lineal(p1, p2, fuerza, momento, nivel)` | Crea una LineLoad libre |
| `crear_carga_superficial(curvas, fuerza)` | Crea una AreaLoad a partir de un contorno |

---

### lib_geometria — Geometria

#### Curvas

| Funcion | Descripcion |
|---|---|
| `crear_linea(p1, p2)` | Linea entre dos puntos XYZ |
| `crear_arco(centro, radio, ang_ini, ang_fin)` | Arco por centro y angulos en grados |
| `crear_arco_por_3_puntos(p1, p2, p3)` | Arco que pasa por tres puntos |
| `crear_nurbs_por_puntos(puntos)` | NurbSpline que pasa por los puntos |
| `crear_curva_senoidal(n, amplitud, ciclos, lambda)` | Lista de XYZ con forma senoidal |

#### CurveLoop

| Funcion | Descripcion |
|---|---|
| `crear_curveloop_desde_curvas(curvas)` | CurveLoop desde lista de curvas |
| `desplazar_curveloop(loop, vector)` | CurveLoop desplazado por un vector |
| `crear_offset_curveloop(loop, distancia_m)` | CurveLoop desfasado a la distancia dada |
| `ordenar_curvas_en_cadena(curvas)` | Ordena curvas en un CurveLoop (sin inversion de curvas) |
| `ordenar_curvas_conectadas(curvas, tol)` | Ordena curvas conectando extremos e invirtiendo si es necesario |
| `combinar_perimetros(curvas_a, curvas_b, tol)` | Fusiona dos contornos eliminando segmentos compartidos |

#### Solidos

| Funcion | Descripcion |
|---|---|
| `crear_extrusion(perfil, direccion, distancia)` | Solido por extrusion |
| `crear_blend(loop_inf, loop_sup)` | Solido blend entre dos perfiles |
| `crear_barrido(perfil, camino)` | Solido por barrido (sweep) |
| `crear_barrido_doble(perfiles, camino)` | SweptBlend con varios perfiles |
| `crear_esfera(centro, radio)` | Esfera solida |
| `crear_cilindro(centro, radio, altura)` | Cilindro solido |
| `crear_cono(centro, radio, altura)` | Cono solido |
| `crear_cono_truncado(centro, r_inf, r_sup, altura)` | Tronco de cono solido |
| `crear_revolution(perfil, ang_ini, ang_fin, centro)` | Solido de revolucion |
| `crear_directshape(geoms, categoria)` | DirectShape visible en el modelo |

#### Operaciones booleanas

| Funcion | Descripcion |
|---|---|
| `booleano_union(sol_a, sol_b)` | Union de dos solidos |
| `booleano_diferencia(sol_a, sol_b)` | Diferencia booleana |
| `booleano_interseccion(sol_a, sol_b)` | Interseccion booleana |
| `descomponer_solido(solido)` | Dict con caras, aristas, vertices, volumen_m3, area_m2 |

#### Algoritmos

| Funcion | Descripcion |
|---|---|
| `obtener_bbox(elems)` | BoundingBox global de una lista de elementos |
| `punto_mas_cercano_en_curva(punto, curva)` | Proyeccion de punto sobre curva |
| `dividir_linea_en_n(linea, n)` | N puntos equidistantes sobre una linea |
| `agrupar_puntos_por_proximidad(puntos, tol)` | Agrupa puntos XYZ por proximidad (BFS) |
| `agrupar_curvas_conectadas(curvas, tol)` | Agrupa curvas que comparten extremos |
| `pathfinding_a_star(nodos, inicio, fin)` | Ruta A* sobre una grilla de nodos |
| `superficie_reglada_por_curvas(curva_inf, curva_sup)` | RuledSurface entre dos curvas |

#### numpy *(CPython)*

| Funcion | Descripcion |
|---|---|
| `puntos_a_array_numpy(puntos)` | Lista de XYZ a array numpy (N,3) en metros |
| `calcular_centroide_numpy(puntos)` | Centroide de una nube de puntos |
| `distancias_entre_puntos_numpy(puntos)` | Matriz (N,N) de distancias en metros |
| `bbox_desde_numpy(puntos)` | (min_xyz, max_xyz) como arrays numpy |
| `ajuste_plano_numpy(puntos)` | Ajuste de plano por SVD (centroide, normal) |

---

### lib_vistas — Vistas

#### Creacion de vistas

| Funcion | Descripcion |
|---|---|
| `crear_vista_planta(nivel, nombre, familia_nombre)` | Vista de planta para un nivel |
| `crear_vista_3d_isometrica(nombre)` | Vista 3D isometrica |
| `crear_vista_3d_por_bbox(bbox, nombre)` | Vista 3D con SectionBox aplicado |
| `crear_vista_3d_por_habitacion(hab, nombre, offset, escala)` | Vista 3D recortada al bounding box de una habitacion |
| `crear_vista_3d_desde_seccion(seccion)` | Vista 3D equivalente a una seccion |
| `crear_seccion_desde_curva(curva, desfase_m)` | ViewSection desde una curva |
| `crear_alzado_en_punto(punto, vista_planta)` | Alzado en un punto de la vista de planta |
| `crear_cartela(vista, esquina_inf_izq, esquina_sup_der)` | Callout en una vista de planta |
| `crear_vista_detalle(elem)` | Vista de detalle del bounding box de un elemento |
| `crear_vista_planta_desde_habitacion(hab, nombre, escala)` | Vista de planta recortada a una habitacion |

#### Duplicar y transformar vistas

| Funcion | Descripcion |
|---|---|
| `duplicar_vista(vista, nombre)` | Duplica una vista como copia independiente |
| `duplicar_vista_dependiente(vista, nombre)` | Duplica como vista dependiente |
| `duplicar_vistas(vistas, nombres)` | Duplica varias vistas en bloque |
| `convertir_vista_a_independiente(vista)` | Convierte vista dependiente en independiente |
| `copiar_elementos_entre_vistas(origen, destino, elems, tf)` | Copia anotaciones entre vistas |
| `girar_elemento_en_vista(elem, vista, angulo_grados)` | Gira un elemento alrededor de su eje Z local |

#### Recorte de vistas (CropBox)

| Funcion | Descripcion |
|---|---|
| `activar_cropbox(vista, activar)` | Activa o desactiva el crop box |
| `establecer_cropbox(vista, bbox)` | Asigna un BoundingBoxXYZ como crop box |
| `establecer_cropbox_desde_elemento(vista, elem)` | Crop box desde el bounding box de un elemento |
| `establecer_recorte_por_curvas(vista, curvas)` | Recorte poligonal arbitrario |
| `establecer_recorte_con_offset(vista, curvas, offset_m)` | Recorte con desfase en metros |
| `copiar_recorte_entre_vistas(vista_origen, vista_dest)` | Copia la forma de recorte a otra vista |
| `obtener_forma_recorte(vista)` | Curvas de la forma de recorte actual |

#### Propiedades de vista

| Funcion | Descripcion |
|---|---|
| `establecer_escala(vista, escala)` | Escala de la vista |
| `establecer_nivel_detalle(vista, nivel_detalle)` | Nivel de detalle (Bajo/Medio/Alto) |
| `establecer_estilo_visual(vista, estilo)` | Estilo visual (Alambre/Ocultas/Realista/etc.) |
| `establecer_disciplina(vista, disciplina)` | Disciplina de la vista |
| `obtener_rango_de_vista(vista_plan)` | PlanViewRange de una vista de planta |
| `obtener_rango_vista_completo(vista_plan)` | Dict completo de planos y offsets del rango de vista |
| `establecer_rango_de_vista(vista, plano, nivel, offset)` | Asigna nivel/offset a un plano del rango de vista |
| `aplicar_plantilla_de_vista(vista, plantilla_id)` | Aplica una plantilla de vista por Id |
| `aplicar_plantilla_por_nombre(vistas, nombre)` | Aplica plantilla buscando por nombre |

#### Visibilidad y graficos

| Funcion | Descripcion |
|---|---|
| `ocultar_elementos_en_vista(vista, ids)` | Oculta elementos en la vista |
| `mostrar_elementos_en_vista(vista, ids)` | Muestra elementos previamente ocultos |
| `ocultar_categoria_en_vista(vista, cat_bic, ocultar)` | Oculta o muestra una categoria completa |
| `aislar_elementos_temporalmente(vista, elems)` | Aislamiento temporal de elementos |
| `convertir_temporal_a_permanente(vista)` | Convierte aislamiento temporal a permanente |
| `sobreescribir_grafico_elemento(vista, elem, color, ...)` | Override de color, patron y transparencia |
| `limpiar_grafico_elemento(vista, elem)` | Elimina todos los overrides de un elemento |

#### Orientacion 3D

| Funcion | Descripcion |
|---|---|
| `establecer_orientacion_3d(vista, ojo, arriba, frente)` | Orienta una vista 3D por vectores de camara |
| `copiar_orientacion_3d(vista_ref, vistas_dest)` | Copia orientacion de una vista 3D a otras |
| `bloquear_vista_3d(vista, bloquear)` | Bloquea o desbloquea la orientacion |
| `restaurar_orientacion_3d(vista)` | Restaura la orientacion guardada |
| `obtener_section_box_3d(vista_3d)` | BoundingBoxXYZ del SectionBox en coordenadas absolutas |

#### Planos (Sheets)

| Funcion | Descripcion |
|---|---|
| `crear_plano(numero, nombre, tipo_id)` | Crea un plano (ViewSheet) |
| `anadir_vista_a_plano(plano, vista, posicion)` | Inserta una vista en un plano como Viewport |
| `centrar_vista_en_plano(plano, viewport)` | Centra un Viewport en el plano |

#### Exportar

| Funcion | Descripcion |
|---|---|
| `exportar_vista_a_imagen(vista, ruta, ancho_px)` | Exporta la vista a PNG |
| `exportar_vistas_a_imagen(vistas, ruta_base)` | Exporta varias vistas a imagen |

#### Filtros de vista (ParameterFilterElement)

| Funcion | Descripcion |
|---|---|
| `crear_filtro_vista_por_texto(nombre, cats, param_bip, texto, cond)` | ParameterFilterElement de texto (igual/contiene/empieza/termina/no_igual) |
| `crear_filtro_vista_por_entero(nombre, cats, param_bip, val, cond)` | ParameterFilterElement de entero (igual/mayor/menor/mayor_igual/menor_igual) |
| `crear_filtro_vista_combinado(nombre, cats, filtros, logica)` | Combina filtros existentes con logica OR/AND |
| `aplicar_filtro_a_vista(vista, filtro_id, visible, ogs)` | Aplica un filtro a una vista con visibilidad y override |
| `eliminar_filtro_de_vista(vista, filtro_id)` | Elimina un filtro de una vista |
| `listar_filtros_de_vista(vista)` | Filtros aplicados a la vista como lista de dicts |
| `obtener_filtros_del_documento()` | Todos los ParameterFilterElement del documento |

#### Planificaciones (Schedules)

| Funcion | Descripcion |
|---|---|
| `crear_planificacion(cat_bic, nombre, parametros_bip)` | Crea una ViewSchedule con los campos indicados |
| `anadir_campo_a_planificacion(planif, param_bip, tipo)` | Añade un campo a una planificacion existente |
| `ordenar_planificacion_por_campo(planif, campo, asc)` | Ordena la planificacion por un ScheduleField |
| `obtener_datos_de_planificacion(planif)` | Contenido de la planificacion como lista de dicts |
| `obtener_planificaciones()` | Todas las ViewSchedule del documento |

#### Anotaciones de vista

| Funcion | Descripcion |
|---|---|
| `crear_nota_de_texto(vista, pos, texto, tipo_id)` | Crea una TextNote en la vista |
| `etiquetar_elemento(vista, ref, pos, modo, orient, lider)` | Crea un IndependentTag para el elemento referenciado |
| `etiquetar_lista_de_elementos(vista, pares_ref_pos, modo)` | Etiqueta varios elementos en bloque |

#### Elementos de redaccion

| Funcion | Descripcion |
|---|---|
| `crear_region_rellena(vista, bucles_curvas, tipo_id)` | Crea una FilledRegion en la vista |
| `crear_curva_detalle(vista, curva)` | Crea una DetailCurve (linea de detalle) en la vista |
| `crear_curvas_detalle(vista, curvas)` | Crea varias DetailCurve en bloque |
| `crear_cota_lineal(vista, linea, referencias, tipo_id)` | Dimension lineal a partir de linea y References |

#### Revisiones

| Funcion | Descripcion |
|---|---|
| `crear_revision(descripcion, fecha, emitida_por)` | Crea una nueva Revision en el documento |
| `obtener_revisiones()` | Todas las Revision del documento en orden de secuencia |
| `crear_nube_revision(vista, bucles_curvas, revision_id)` | RevisionCloud en la vista para la revision indicada |
| `obtener_nubes_en_vista(vista)` | Todas las RevisionCloud de una vista |
| `asignar_revision_a_plano(plano, revision_id, asignar)` | Asigna o quita una revision de un plano |
| `establecer_numeracion_revision(tipo)` | Tipo de numeracion de revisiones (PerSheet/Shared) |

---

### lib_familias — Familias

| Funcion | Descripcion |
|---|---|
| `cargar_familia(ruta)` | Carga una familia .rfa en el documento |
| `obtener_tipos_de_familia(nombre)` | Todos los FamilySymbol de una familia |
| `activar_tipo_familia(symbol)` | Activa un FamilySymbol para colocarlo |
| `colocar_instancia_familia(symbol, punto, nivel)` | Coloca una instancia en un punto XYZ |
| `colocar_instancia_en_cara(symbol, cara, punto)` | Coloca una instancia en una cara |
| `obtener_parametros_familia(symbol)` | Dict con parametros de tipo del FamilySymbol |
| `exportar_familia(familia, carpeta)` | Exporta una familia a .rfa |
| `obtener_familias_por_categoria(cat)` | Familias del documento de una categoria |
| `eliminar_familias_no_usadas()` | Elimina familias sin instancias colocadas |
| `exportar_todas_las_familias(carpeta)` | Exporta todas las familias de usuario a .rfa |

---

### lib_cad — Archivos CAD

| Funcion | Descripcion |
|---|---|
| `clasificar_links_cad()` | Dict {"enlazadas": [...], "importadas": [...]} |
| `obtener_nombres_capas_cad(link)` | Nombres de todos los layers de una instancia CAD |
| `obtener_curvas_por_capa(link, capa)` | Curvas de un layer especifico de un CAD |
| `obtener_datos_bloques_cad(link)` | Datos de bloques: simbolo, origen, geometrias |
| `obtener_categoria_de_capa(link, capa)` | Category de Revit para un layer CAD |
| `obtener_origen_link_cad(link)` | XYZ del origen del link en coordenadas del proyecto |
| `eliminar_link_cad(link)` | Elimina una instancia de link CAD |
| `eliminar_todos_links_cad()` | Elimina todos los links CAD del documento |
| `desanclar_link_cad(link)` | Desancla un link CAD para moverlo |

---

### lib_excel — Excel

| Funcion | Descripcion |
|---|---|
| `leer_excel_dsoffice(ruta, hoja)` | Lee Excel via DSOffice (nativo Dynamo) |
| `escribir_excel_dsoffice(ruta, hoja, datos)` | Escribe Excel via DSOffice |
| `obtener_hojas_excel(ruta)` | Nombres de todas las hojas del archivo |
| `leer_excel_com(ruta, hoja)` | Lee Excel via COM Interop (requiere Office) |
| `escribir_excel_com(ruta, datos, hoja)` | Escribe Excel via COM Interop |
| `exportar_parametros_a_excel(elems, params, ruta)` | Parametros Revit a Excel via DSOffice |
| `importar_parametros_desde_excel(ruta, hoja)` | Excel a parametros de elementos Revit |
| `exportar_schedule_a_excel(nombre, ruta)` | Schedule Revit a Excel |
| `leer_excel_pandas(ruta, hoja)` | Excel a DataFrame *(CPython)* |
| `leer_todas_las_hojas_pandas(ruta)` | Todas las hojas a dict de DataFrames *(CPython)* |
| `escribir_excel_pandas(df, ruta, hoja)` | DataFrame a Excel *(CPython)* |
| `escribir_multiples_hojas_pandas(dict_dfs, ruta)` | Varios DataFrames a varias hojas *(CPython)* |
| `exportar_parametros_a_dataframe(elems, params)` | Parametros Revit a DataFrame *(CPython)* |
| `aplicar_dataframe_a_parametros(df)` | DataFrame a parametros de elementos Revit *(CPython)* |
| `excel_a_parametros_revit(ruta, hoja)` | Flujo completo Excel a Revit *(CPython)* |
| `dataframe_a_excel_formato(df, ruta)` | DataFrame a Excel con cabecera negrita *(CPython)* |
| `schedule_a_dataframe_pandas(nombre)` | Schedule Revit a DataFrame *(CPython)* |
| `pivot_dataframe_elementos(elems, params, ...)` | Tabla pivot de parametros Revit *(CPython)* |

---

### lib_bases_datos — Bases de datos y formatos

| Funcion | Descripcion |
|---|---|
| `leer_json(ruta)` | Lee un archivo JSON |
| `escribir_json(datos, ruta)` | Exporta un objeto Python a JSON |
| `leer_csv(ruta)` | Lee CSV como lista de dicts |
| `escribir_csv(datos, ruta)` | Exporta datos a CSV |
| `exportar_parametros_elementos(elems, params, ruta)` | Parametros Revit a JSON |
| `importar_parametros_desde_json(ruta)` | JSON a parametros de elementos Revit |
| `exportar_ifc(ruta)` | Exporta el documento a IFC |
| `exportar_schedule_a_csv(nombre, ruta)` | Schedule Revit a CSV |
| `listar_schedules()` | Nombres de todas las schedules del documento |
| `obtener_guid_elemento(elem)` | UniqueId (GUID) de un elemento |
| `obtener_elemento_por_guid(guid)` | Elemento por UniqueId |
| `guardar_configuracion(config, ruta)` | Guarda dict de configuracion como JSON |
| `cargar_configuracion(ruta)` | Carga configuracion desde JSON |
| `exportar_a_dataframe(elems, params)` | Parametros Revit a DataFrame *(CPython)* |
| `importar_desde_dataframe(df)` | DataFrame a parametros Revit *(CPython)* |
| `estadisticas_dataframe(df)` | Estadisticas descriptivas de columnas numericas *(CPython)* |
| `agrupar_dataframe(df, col, aggfunc)` | Agrupa DataFrame por columna *(CPython)* |
| `exportar_dataframe_a_csv(df, ruta)` | DataFrame a CSV con encoding UTF-8 *(CPython)* |
| `leer_csv_pandas(ruta)` | CSV a DataFrame con encoding UTF-8 *(CPython)* |

---

### lib_colaborativo — Worksharing

| Funcion | Descripcion |
|---|---|
| `activar_worksharing()` | Activa el modo colaborativo (operacion irreversible) |
| `guardar_como_central(ruta)` | Guarda el documento como archivo central |
| `sincronizar_con_central()` | Sincroniza con el central cediendo worksets |
| `crear_workset(nombre)` | Crea un nuevo workset de usuario |
| `obtener_worksets()` | Worksets de usuario del documento |
| `asignar_workset_a_elemento(elem, workset_id)` | Asigna workset a un elemento |
| `asignar_workset_a_lista(elems, workset_id)` | Asignacion masiva de workset |
| `obtener_workset_de_elemento(elem)` | WorksetId del elemento |
| `abrir_documento(ruta)` | Abre un documento Revit |
| `cerrar_documento(doc)` | Cierra un documento Revit |

---

### lib_transacciones — Transacciones

| Funcion | Descripcion |
|---|---|
| `ejecutar_en_grupo(funciones, nombre)` | Ejecuta varias funciones en un TransactionGroup |
| `iniciar_transaccion_nativa(nombre)` | Inicia una Transaction nativa de Revit |
| `finalizar_transaccion_nativa(tx, confirmar)` | Confirma o revierte una Transaction nativa |
| `ejecutar_subtransaccion(funcion)` | Ejecuta una funcion en una SubTransaction |
| `transaccion_nativa(funcion, nombre)` | Funcion en Transaction nativa con rollback automatico |
| `forzar_cierre_transacciones()` | Fuerza el cierre de transacciones Dynamo activas |
| `eliminar_elemento_en_subtransaccion(elem)` | Elimina un elemento en subtransaccion |
| `comparar_documentos(ruta_otro)` | Compara el documento activo con otro (Revit 2023+) |

---

### lib_seleccion_ui — Seleccion interactiva

| Funcion | Descripcion |
|---|---|
| `seleccionar_elemento()` | El usuario selecciona un elemento del modelo |
| `seleccionar_cara()` | El usuario selecciona una cara de un elemento |
| `seleccionar_arista()` | El usuario selecciona una arista |
| `seleccionar_punto()` | El usuario marca un punto libre |
| `seleccionar_multiples()` | El usuario selecciona varios elementos |
| `seleccionar_rectangulo()` | El usuario selecciona elementos con rectangulo |
| `seleccionar_elemento_en_link()` | Selecciona un elemento dentro de un Revit Link |
| `obtener_seleccion_actual()` | ElementIds de los elementos seleccionados en Revit |
| `establecer_seleccion(ids)` | Establece la seleccion activa en Revit |

---

### lib_scientific — Python cientifico + Revit API

Requiere **CPython 3.x (Dynamo 2.13+)**.

| Libreria | Funcion | Descripcion |
|---|---|---|
| — | `instalar_dependencias_scientific()` | Instala todas las dependencias de una vez |
| — | `estado_dependencias()` | Comprueba que librerias estan disponibles |
| — | `figura_a_bitmap(fig)` | Figura matplotlib a Bitmap para Watch Image |
| **pandas** | `elementos_a_dataframe(elems, params)` | Elementos Revit a DataFrame |
| **pandas** | `dataframe_a_parametros(df)` | DataFrame a parametros de elementos Revit |
| **pandas** | `schedule_a_dataframe(nombre)` | Schedule Revit a DataFrame |
| **pandas** | `analisis_calidad_datos(elems, params)` | QA/QC: elementos con parametros vacios |
| **numpy** | `xyz_a_numpy(puntos)` | Lista de XYZ a array numpy (N,3) en metros |
| **numpy** | `numpy_a_xyz(arr)` | Array numpy a lista de XYZ Revit |
| **numpy** | `posiciones_elementos_numpy(elems)` | LocationPoint de elementos a array numpy |
| **numpy** | `centroide_nube(puntos)` | Centroide de una nube de XYZ |
| **scipy** | `clustering_por_posicion(elems, n)` | Agrupa elementos por proximidad espacial (K-Means) |
| **scipy** | `clustering_por_parametros(elems, params, n)` | Agrupa elementos por valores de parametros |
| **scipy** | `vecinos_por_radio(elems, radio_m)` | Vecinos de cada elemento en un radio |
| **scipy** | `interpolacion_parametro(elems, px, py, xs)` | Interpola un parametro en funcion de otro |
| **matplotlib** | `grafico_parametro_por_nivel(elems, param)` | Barras: media de parametro por nivel |
| **matplotlib** | `histograma_parametro(elems, param)` | Histograma de distribucion de valores |
| **matplotlib** | `grafico_dispersion(elems, px, py)` | Scatter entre dos parametros |
| **matplotlib** | `grafico_suma_por_categoria(elems, param)` | Pie: suma de parametro por categoria |
| **shapely** | `curvas_a_shapely(curvas)` | Curvas Revit a Polygon de Shapely |
| **shapely** | `habitacion_a_shapely(hab)` | Room Revit a Polygon de Shapely |
| **shapely** | `detectar_solapamientos(habs)` | Pares de habitaciones que se solapan |
| **networkx** | `sistema_mep_a_grafo(elems_mep)` | Elementos MEP conectados a grafo NetworkX |
| **networkx** | `analisis_red_mep(grafo)` | Metricas de conectividad de la red MEP |
| **networkx** | `ruta_mas_corta_mep(grafo, id1, id2)` | Ruta mas corta entre dos elementos MEP |

---

### lib_ui — Ventanas emergentes WPF

| Funcion | Descripcion |
|---|---|
| `mensaje(texto, titulo, tipo)` | Cuadro de mensaje: info, advertencia, error, pregunta |
| `confirmar(texto, titulo)` | Dialogo Si / No — devuelve True / False |
| `confirmar_cancelar(texto, titulo)` | Dialogo Si / No / Cancelar — devuelve True / False / None |
| `pedir_texto(etiqueta, titulo, defecto)` | Campo de texto libre |
| `pedir_numero(etiqueta, titulo, defecto, min, max)` | Campo numerico con validacion |
| `seleccionar_opcion(opciones, etiqueta)` | Desplegable de opciones |
| `seleccionar_multiples(opciones, etiqueta)` | Lista con checkboxes |
| `formulario(campos, titulo)` | Formulario dinamico multi-campo |
| `pedir_archivo(filtro, titulo)` | Dialogo de apertura de archivo |
| `pedir_archivos_multiples(filtro, titulo)` | Apertura con seleccion multiple |
| `pedir_ruta_guardar(filtro, titulo, nombre)` | Dialogo de guardar archivo |
| `pedir_carpeta(titulo)` | Dialogo de seleccion de carpeta |
| `mostrar_lista(elems, titulo, etiqueta)` | Lista en ventana scrollable |
| `mostrar_tabla(datos, columnas, titulo)` | Tabla con DataGrid |
| `con_progreso(elems, funcion, titulo)` | Barra de progreso mientras procesa una lista |
| `seleccionar_parametros(params, titulo)` | Seleccion multiple de parametros Revit |
| `seleccionar_niveles(doc, titulo, multiples)` | Dialogo para elegir niveles del documento |
| `seleccionar_categorias(doc, titulo, multiples)` | Dialogo para elegir categorias del modelo |

---

## Ejemplos

### Suelo desde habitacion con umbral de puerta

```python
from lib_arquitectura import (
    obtener_habitaciones, obtener_puertas_de_habitacion,
    crear_suelo_desde_habitacion
)
from lib_geometria import combinar_perimetros

# Obtener habitacion y tipo de suelo
hab = obtener_habitaciones()[0]
tipo_id = ...  # ElementId del FloorType

# Umbrales de puertas: cada puerta aporta una linea de cierre
puertas = obtener_puertas_de_habitacion(hab)
curvas_umbral = []
for puerta in puertas:
    ancho = puerta.Symbol.get_Parameter(
        BuiltInParameter.DOOR_WIDTH).AsDouble()
    # construir linea del umbral en posicion de la puerta...
    # curvas_umbral.append(linea_umbral)

suelo = crear_suelo_desde_habitacion(hab, tipo_id, curvas_umbral)
OUT = [suelo]
```

### Ordenar curvas de un CAD desordenadas

```python
from lib_geometria import ordenar_curvas_conectadas
from lib_cad import obtener_curvas_por_capa, clasificar_links_cad

links = clasificar_links_cad()["enlazadas"]
curvas = obtener_curvas_por_capa(links[0], "MURO")
curvas_ordenadas = ordenar_curvas_conectadas(curvas, tolerancia_m=0.01)
OUT = [curvas_ordenadas]
```

### Filtrar elementos por valor de parametro

```python
from lib_general import filtrar_por_valor_parametro
from Autodesk.Revit.DB import BuiltInCategory

muros_ext = filtrar_por_valor_parametro(
    BuiltInCategory.OST_Walls, "Funcion", "Exterior")
OUT = [muros_ext]
```

### Agrupar vigas por nivel y calcular volumen hormigon

```python
from lib_estructura import agrupar_vigas_por_nivel, calcular_volumen_hormigon

por_nivel = agrupar_vigas_por_nivel()
vol_total = calcular_volumen_hormigon()  # pilares+vigas+forjados+cimentacion

OUT = [
    {nivel: len(vigas) for nivel, vigas in por_nivel.items()},
    vol_total
]
```

### Procesar lista con barra de progreso

```python
from lib_ui import con_progreso
from lib_general import filtrar_por_valor_parametro, aplanar_lista
from Autodesk.Revit.DB import BuiltInCategory

muros = filtrar_por_valor_parametro(
    BuiltInCategory.OST_Walls, "Fase de construccion", "Nueva construccion")

def marcar(muro, idx):
    p = muro.LookupParameter("Marca")
    if p and not p.IsReadOnly:
        p.Set("M-{:04d}".format(idx + 1))
    return muro.Id.IntegerValue

OUT = [con_progreso(muros, marcar, titulo="Marcando muros...")]
```

---

## Compatibilidad de unidades (Revit 2024+)

Todas las funciones de conversion usan `UnitTypeId` (nunca `DisplayUnitType`).
Los `ElementId` se convierten con `id_a_int()` que soporta `.Value` (Revit 2024+)
e `.IntegerValue` (Revit 2023 y anteriores).

Las funciones nunca usan `print()` — los resultados van siempre por `return`.

## Licencia

MIT — uso libre con atribucion a Kevin Himmelreich
