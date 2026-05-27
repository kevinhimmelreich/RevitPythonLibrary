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
| `lib_general.py` | Utilidades compartidas: unwrap, transacciones, parametros, conversiones de unidades, colectores |
| `lib_coordinacion.py` | Vistas, planos, niveles, worksets, links, fases, categorias, overrides graficos |
| `lib_arquitectura.py` | Muros, suelos, cubiertas, habitaciones, puertas, ventanas, escaleras, barandillas, areas |
| `lib_instalaciones.py` | Conductos, tuberias, bandejas, conduits, equipos MEP, luminarias, sanitarios, espacios |
| `lib_estructura.py` | Pilares, vigas, forjados, cimentaciones, armaduras, cargas estructurales |
| `lib_geometria.py` | Curvas, solidos (extrusion, blend, barrido, revolution), booleanas, DirectShape, A* pathfinding |
| `lib_vistas.py` | Vistas 3D, secciones, alzados, cartelas, rango de vista, escala, nivel de detalle, export imagen |
| `lib_familias.py` | Carga, exportacion, instanciacion y gestion de familias |
| `lib_cad.py` | Importacion y analisis de archivos CAD (DWG/DXF): capas, curvas, bloques |
| `lib_excel.py` | Lectura/escritura Excel via DSOffice y COM Interop; pandas con formato y pivot |
| `lib_bases_datos.py` | JSON, CSV, exportacion IFC, schedules a CSV, GUIDs; pandas |
| `lib_colaborativo.py` | Worksharing: activar colaborativo, guardar central, sincronizar, worksets |
| `lib_transacciones.py` | TransactionGroup, Transaction nativa, SubTransaction, ForceClose |
| `lib_seleccion_ui.py` | Seleccion interactiva: elemento, cara, arista, punto, rectangulo, link |
| `lib_scientific.py` | Integracion Revit API con Python cientifico (pandas, numpy, scipy, matplotlib, shapely, networkx) |
| `lib_ui.py` | Ventanas emergentes y dialogos WPF: texto, numero, opciones, archivos, progreso |
| `lib_completa.py` | Importa todos los modulos con `from lib_completa import *` |

## Uso basico en Dynamo

```python
import sys
sys.path.append("C:/ruta/a/RevitPythonLibrary")

# Importar un modulo concreto
from lib_general import pies_a_metros, obtener_valor_parametro

# O importar todo
from lib_completa import *

# Ejemplo: obtener todos los niveles
niveles = obtener_niveles()
OUT = [n.Name for n in niveles]
```

---

## Referencia de funciones

### lib_general — Utilidades base

| Funcion | Descripcion |
|---|---|
| `unwrap(elem)` | Desenvuelve un elemento Dynamo al elemento Revit nativo |
| `unwrap_lista(elems)` | Desenvuelve una lista de elementos Dynamo |
| `id_a_int(element_id)` | Convierte ElementId a int, compatible Revit 2024+ |
| `iniciar_transaccion(nombre)` | Inicia o reanuda la transaccion Dynamo activa |
| `finalizar_transaccion()` | Marca la tarea de transaccion como completada |
| `obtener_valor_parametro(elem, nombre)` | Lee el valor de un parametro de instancia por nombre |
| `establecer_valor_parametro(elem, nombre, valor)` | Escribe el valor de un parametro de instancia |
| `obtener_todos_parametros(elem)` | Retorna todos los parametros como dict {nombre: valor} |
| `pies_a_metros(v)` | Convierte pies internos de Revit a metros |
| `metros_a_pies(v)` | Convierte metros a pies internos de Revit |
| `mm_a_pies(v)` | Convierte milimetros a pies internos |
| `pies_a_mm(v)` | Convierte pies internos a milimetros |
| `m2_a_pies2(v)` | Convierte m2 a pies2 internos |
| `pies2_a_m2(v)` | Convierte pies2 internos a m2 |
| `filtrar_por_categoria(cat_builtin)` | Colecta elementos de una categoria BuiltIn |
| `filtrar_por_clase(clase)` | Colecta elementos de una clase .NET |
| `obtener_elemento_por_id(id_int)` | Obtiene un elemento por su ID entero |

---

### lib_coordinacion — Coordinacion BIM

| Funcion | Descripcion |
|---|---|
| `obtener_documento_activo()` | Retorna el documento Revit activo |
| `obtener_todos_los_elementos(categoria)` | Colecta elementos, filtrados por categoria opcionalmente |
| `obtener_niveles()` | Todos los niveles ordenados por elevacion ascendente |
| `obtener_vistas_por_tipo(tipo_vista)` | Filtra vistas por ViewType excluyendo plantillas |
| `obtener_plantillas_de_vista()` | Todas las plantillas de vista del documento |
| `obtener_planos()` | Todos los planos (ViewSheet) del documento |
| `obtener_plano_por_numero(numero)` | Busca un plano por su numero |
| `obtener_links_revit()` | Todas las instancias de link Revit |
| `obtener_links_cad()` | Todas las instancias de link/importacion CAD |
| `obtener_advertencias()` | Todas las advertencias activas del documento |
| `obtener_worksets()` | Worksets de usuario del documento colaborativo |
| `asignar_workset(elem, workset_id)` | Asigna workset a un elemento |
| `obtener_categorias_modelo()` | Lista todas las categorias de modelo |
| `obtener_fases()` | Todas las fases del proyecto |
| `crear_vista_plano(nivel)` | Crea una vista de planta para un nivel |
| `crear_plano(numero, nombre)` | Crea un ViewSheet nuevo |
| `anadir_vista_a_plano(vista, plano, punto)` | Anade una vista a un plano en la posicion indicada |
| `duplicar_vista(vista, nombre)` | Duplica una vista con un nombre nuevo |
| `aplicar_plantilla_vista(vistas, nombre)` | Aplica plantilla de vista a una lista de vistas |
| `crear_seccion(curva)` | Crea una ViewSection desde una curva |
| `crear_vista_3d_isometrica(nombre)` | Crea una vista 3D isometrica |
| `exportar_vistas_a_imagen(vistas, carpeta)` | Exporta vistas a imagenes PNG |
| `sobreescribir_grafico_elemento(elem, vista, color)` | Aplica overrides de color a un elemento en una vista |

---

### lib_arquitectura — Arquitectura

| Funcion | Descripcion |
|---|---|
| `obtener_muros()` | Todos los muros del documento |
| `obtener_suelos()` | Todos los suelos del documento |
| `obtener_cubiertas()` | Todas las cubiertas del documento |
| `obtener_habitaciones()` | Todas las habitaciones del documento |
| `obtener_puertas()` | Todas las puertas del documento |
| `obtener_ventanas()` | Todas las ventanas del documento |
| `obtener_escaleras()` | Todas las escaleras del documento |
| `obtener_barandillas()` | Todas las barandillas del documento |
| `obtener_techos()` | Todos los techos del documento |
| `obtener_mobiliario()` | Todos los elementos de mobiliario |
| `obtener_area_habitacion(hab)` | Area de una habitacion en m2 |
| `obtener_habitaciones_por_nivel(nivel)` | Habitaciones de un nivel concreto |
| `obtener_muros_por_tipo(nombre_tipo)` | Muros filtrados por nombre de tipo |
| `obtener_grosor_muro(muro)` | Grosor total de un muro en mm |
| `obtener_elementos_en_habitacion(hab)` | Elementos cuya ubicacion cae dentro de una habitacion |
| `crear_muro(curva, tipo, nivel, altura)` | Crea un muro lineal |
| `crear_suelo(curvas, tipo, nivel)` | Crea un suelo desde un contorno |
| `calcular_volumen_habitacion(hab)` | Volumen de una habitacion en m3 |
| `clasificar_habitaciones_por_nombre(habs, patron)` | Clasifica habitaciones por regex en el nombre |
| `agrupar_habitaciones_por_nivel()` | Agrupa todas las habitaciones por nivel |
| `clasificar_habitaciones_por_estado()` | Clasifica por estado: colocadas, no_colocadas, etc. |
| `dataframe_habitaciones(habs)` | Exporta datos de habitaciones a DataFrame *(CPython)* |
| `estadisticas_habitaciones_pandas(habs)` | Estadisticas descriptivas de area y volumen *(CPython)* |

---

### lib_instalaciones — MEP / Instalaciones

| Funcion | Descripcion |
|---|---|
| `obtener_conductos()` | Todos los conductos del documento |
| `obtener_tuberias()` | Todas las tuberias del documento |
| `obtener_bandejas_cable()` | Todas las bandejas de cable |
| `obtener_conduits()` | Todos los conduits electricos |
| `obtener_equipos_mecanicos()` | Todos los equipos mecanicos |
| `obtener_equipos_electricos()` | Todos los equipos electricos |
| `obtener_luminarias()` | Todas las luminarias |
| `obtener_sanitarios()` | Todos los sanitarios |
| `obtener_espacios()` | Todos los espacios MEP |
| `obtener_longitud_conducto(conducto)` | Longitud de un conducto en metros |
| `obtener_longitud_tuberia(tuberia)` | Longitud de una tuberia en metros |
| `obtener_diametro_exterior_tuberia(tub)` | Diametro exterior en mm |
| `obtener_sistema_tuberia(tub)` | Nombre del sistema de una tuberia |
| `agrupar_tuberias_por_sistema()` | Agrupa tuberias por nombre de sistema |
| `agrupar_conductos_por_sistema()` | Agrupa conductos por nombre de sistema |
| `obtener_longitud_total_conductos()` | Longitud total de conductos en metros |
| `obtener_longitud_total_tuberias()` | Longitud total de tuberias en metros |
| `crear_bandeja_cable(p1, p2, ancho, alto)` | Crea una bandeja de cables entre dos puntos |
| `dataframe_tuberias(tubs)` | Tuberias a DataFrame *(CPython)* |
| `dataframe_conductos(conds)` | Conductos a DataFrame *(CPython)* |
| `estadisticas_sistemas_pandas(tubs, conds)` | Estadisticas de longitud por sistema *(CPython)* |

---

### lib_estructura — Estructura

| Funcion | Descripcion |
|---|---|
| `obtener_pilares()` | Todos los pilares estructurales |
| `obtener_vigas()` | Todas las vigas estructurales |
| `obtener_forjados()` | Todos los forjados |
| `obtener_muros_estructurales()` | Muros con funcion estructural |
| `obtener_cimentaciones()` | Todos los elementos de cimentacion |
| `obtener_armaduras()` | Todas las armaduras (Rebar) |
| `obtener_longitud_viga(viga)` | Longitud de una viga en metros |
| `obtener_altura_pilar(pilar)` | Altura de un pilar en metros |
| `obtener_pilares_por_nivel(nivel)` | Pilares de un nivel concreto |
| `obtener_area_total_forjados()` | Area total de forjados en m2 |
| `obtener_materiales_usados()` | Materiales estructurales unicos en vigas y pilares |
| `crear_viga(curva, tipo, nivel)` | Crea una viga estructural |
| `crear_pilar_inclinado(p1, p2, tipo)` | Crea un pilar inclinado entre dos puntos XYZ |
| `crear_armadura(elem, curvas, tipo)` | Crea una armadura (Rebar) en un elemento |
| `distribuir_armadura_numero_fijo(...)` | Distribuye armadura con numero fijo de barras |
| `crear_armado_por_area(suelo, tipo)` | Crea un AreaReinforcement en un suelo estructural |
| `crear_carga_puntual(punto, fuerza)` | Crea una carga puntual libre |
| `crear_carga_lineal(p1, p2, valor)` | Crea una carga lineal libre |
| `crear_carga_superficial(curvas, valor)` | Crea una carga superficial |

---

### lib_geometria — Geometria

| Funcion | Descripcion |
|---|---|
| `crear_linea(p1, p2)` | Crea una linea entre dos puntos XYZ |
| `crear_arco(centro, radio, ang_ini, ang_fin)` | Crea un arco por centro y angulos |
| `crear_arco_por_3_puntos(p1, p2, p3)` | Crea un arco por tres puntos |
| `crear_nurbs_por_puntos(puntos)` | Crea una NurbSpline que pasa por los puntos |
| `crear_curveloop_desde_curvas(curvas)` | Crea un CurveLoop desde una lista de curvas |
| `crear_extrusion(perfil, altura)` | Crea un solido por extrusion |
| `crear_blend(perfil1, perfil2)` | Crea un solido blend entre dos perfiles |
| `crear_barrido(perfil, camino)` | Crea un solido por barrido |
| `crear_esfera(centro, radio)` | Crea una esfera solida |
| `crear_cilindro(centro, radio, altura)` | Crea un cilindro solido |
| `crear_directshape(geoms, categoria)` | Crea un DirectShape visible en el modelo |
| `booleano_union(sol_a, sol_b)` | Union booleana de dos solidos |
| `booleano_diferencia(sol_a, sol_b)` | Diferencia booleana |
| `booleano_interseccion(sol_a, sol_b)` | Interseccion booleana |
| `obtener_bbox(elementos)` | BoundingBox global de una lista de elementos |
| `dividir_linea_en_n(linea, n)` | Divide una linea en N puntos equidistantes |
| `agrupar_puntos_por_proximidad(puntos, tol)` | Agrupa puntos XYZ por proximidad (BFS) |
| `pathfinding_a_star(grilla, inicio, fin)` | Ruta A* sobre una grilla de nodos |
| `puntos_a_array_numpy(puntos)` | XYZ de Revit a numpy array (N,3) en metros *(CPython)* |
| `calcular_centroide_numpy(puntos)` | Centroide de una nube de puntos *(CPython)* |
| `ajuste_plano_numpy(puntos)` | Ajuste de plano por SVD *(CPython)* |

---

### lib_vistas — Vistas

| Funcion | Descripcion |
|---|---|
| `crear_vista_3d_isometrica(nombre)` | Crea una vista 3D isometrica |
| `crear_seccion_desde_curva(curva)` | Crea una ViewSection desde una curva |
| `crear_alzado_en_punto(punto, vista)` | Crea un alzado en un punto dado |
| `crear_cartela(vista, region)` | Crea una Callout en una vista de planta |
| `crear_vista_detalle(elem)` | Vista de detalle del bounding box de un elemento |
| `establecer_rango_de_vista(vista, nivel, offset)` | Asigna nivel y offset al rango de vista |
| `establecer_escala(vista, escala)` | Establece la escala de una vista |
| `establecer_nivel_detalle(vista, nivel)` | Establece el nivel de detalle |
| `establecer_estilo_visual(vista, estilo)` | Establece el estilo visual |
| `ocultar_elementos_en_vista(elems, vista)` | Oculta elementos en una vista |
| `mostrar_elementos_en_vista(elems, vista)` | Muestra elementos previamente ocultos |
| `activar_cropbox(vista, activar)` | Activa o desactiva el crop box |
| `aplicar_plantilla_de_vista(vista, plantilla)` | Aplica una plantilla de vista |
| `ocultar_categoria_en_vista(cat, vista)` | Oculta una categoria completa en una vista |
| `exportar_vista_a_imagen(vista, ruta)` | Exporta una vista a PNG |

---

### lib_familias — Familias

| Funcion | Descripcion |
|---|---|
| `cargar_familia(ruta)` | Carga una familia .rfa en el documento |
| `obtener_tipos_de_familia(nombre)` | Todos los FamilySymbol de una familia |
| `activar_tipo_familia(symbol)` | Activa un FamilySymbol para poder colocarlo |
| `colocar_instancia_familia(symbol, punto, nivel)` | Coloca una instancia en un punto XYZ |
| `colocar_instancia_en_cara(symbol, cara, punto)` | Coloca una instancia en una cara |
| `obtener_parametros_familia(symbol)` | Dict con los parametros de tipo del FamilySymbol |
| `exportar_familia(familia, carpeta)` | Exporta una familia a .rfa |
| `obtener_familias_por_categoria(cat)` | Familias del documento para una categoria |
| `eliminar_familias_no_usadas()` | Elimina familias sin instancias colocadas |
| `exportar_todas_las_familias(carpeta)` | Exporta todas las familias de usuario a .rfa |

---

### lib_cad — Archivos CAD

| Funcion | Descripcion |
|---|---|
| `obtener_todos_links_cad()` | Todas las instancias de importacion/link CAD |
| `obtener_nombres_capas_cad(link)` | Nombres de todos los layers de una instancia CAD |
| `obtener_curvas_por_capa(link, capa)` | Curvas de un layer especifico de un CAD |
| `obtener_datos_bloques_cad(link)` | Datos de bloques de una importacion CAD |
| `obtener_origen_link_cad(link)` | Vector de desplazamiento del link CAD al origen |
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
| `dataframe_a_excel_formato(df, ruta)` | DataFrame a Excel con cabecera negrita y anchos auto *(CPython)* |
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

Requiere **CPython 3.x (Dynamo 2.13+)**. Las dependencias se instalan automaticamente
via pip la primera vez que se llama a cada funcion.

| Libreria | Funcion | Descripcion |
|---|---|---|
| — | `instalar_dependencias_scientific()` | Instala todas las dependencias de una vez |
| — | `estado_dependencias()` | Comprueba que librerias estan disponibles |
| — | `figura_a_bitmap(fig)` | Figura matplotlib a Bitmap para Watch Image de Dynamo |
| **pandas** | `elementos_a_dataframe(elems, params)` | Elementos Revit a DataFrame |
| **pandas** | `dataframe_a_parametros(df)` | DataFrame a parametros de elementos Revit |
| **pandas** | `schedule_a_dataframe(nombre)` | Schedule Revit a DataFrame |
| **pandas** | `analisis_calidad_datos(elems, params)` | QA/QC: elementos con parametros vacios |
| **numpy** | `xyz_a_numpy(puntos)` | Lista de XYZ a array numpy (N,3) en metros |
| **numpy** | `numpy_a_xyz(arr)` | Array numpy a lista de XYZ Revit |
| **numpy** | `posiciones_elementos_numpy(elems)` | LocationPoint de elementos a array numpy |
| **numpy** | `centroide_nube(puntos)` | Centroide de una nube de XYZ |
| **scipy** | `clustering_por_posicion(elems, n)` | Agrupa elementos por proximidad espacial (K-Means) |
| **scipy** | `clustering_por_parametros(elems, params, n)` | Agrupa elementos por valores de parametros (K-Means) |
| **scipy** | `vecinos_por_radio(elems, radio_m)` | Vecinos de cada elemento en un radio |
| **scipy** | `interpolacion_parametro(elems, px, py, xs)` | Interpola un parametro en funcion de otro |
| **matplotlib** | `grafico_parametro_por_nivel(elems, param)` | Barras: media de parametro por nivel |
| **matplotlib** | `histograma_parametro(elems, param)` | Histograma de distribucion de valores |
| **matplotlib** | `grafico_dispersion(elems, px, py)` | Scatter entre dos parametros numericos |
| **matplotlib** | `grafico_suma_por_categoria(elems, param)` | Pie: suma de parametro por categoria |
| **matplotlib** | `scatter_elementos_coloreados(elems, px, py, pc)` | Scatter con tercer parametro como color |
| **matplotlib** | `mapa_calor_planta(habs, param)` | Planta coloreada por parametro (shapely + mpl) |
| **shapely** | `curvas_a_shapely(curvas)` | Curvas Revit a Polygon de Shapely |
| **shapely** | `habitacion_a_shapely(hab)` | Room Revit a Polygon de Shapely |
| **shapely** | `detectar_solapamientos(habs)` | Pares de habitaciones que se solapan en planta |
| **shapely** | `buffer_habitacion(hab, dist_m)` | Perimetro expandido de una habitacion |
| **networkx** | `sistema_mep_a_grafo(elems_mep)` | Elementos MEP conectados a grafo NetworkX |
| **networkx** | `analisis_red_mep(grafo)` | Metricas de conectividad de la red MEP |
| **networkx** | `ruta_mas_corta_mep(grafo, id1, id2)` | Ruta mas corta entre dos elementos MEP |

---

### lib_ui — Ventanas emergentes WPF

Dialogos modernos basados en WPF, compatibles con Dynamo (que es WPF nativo).
Todos los resultados vienen por `return` — ninguna funcion usa la consola.

| Funcion | Descripcion |
|---|---|
| `mensaje(texto, titulo, tipo)` | Cuadro de mensaje: info, advertencia, error, pregunta |
| `confirmar(texto, titulo)` | Dialogo Si / No — devuelve True / False |
| `confirmar_cancelar(texto, titulo)` | Dialogo Si / No / Cancelar — devuelve True / False / None |
| `pedir_texto(etiqueta, titulo, defecto)` | Campo de texto libre — devuelve str |
| `pedir_numero(etiqueta, titulo, defecto, min, max)` | Campo numerico con validacion — devuelve float |
| `seleccionar_opcion(opciones, etiqueta)` | Desplegable de opciones — devuelve str seleccionado |
| `seleccionar_multiples(opciones, etiqueta)` | Lista con checkboxes — devuelve lista de seleccionados |
| `formulario(campos, titulo)` | Formulario dinamico multi-campo — devuelve dict {campo: valor} |
| `pedir_archivo(filtro, titulo)` | Dialogo estandar de apertura de archivo — devuelve ruta |
| `pedir_archivos_multiples(filtro, titulo)` | Apertura con seleccion multiple — devuelve lista de rutas |
| `pedir_ruta_guardar(filtro, titulo, nombre)` | Dialogo de guardar archivo — devuelve ruta |
| `pedir_carpeta(titulo)` | Dialogo de seleccion de carpeta — devuelve ruta |
| `mostrar_lista(elems, titulo, etiqueta)` | Lista de elementos en ventana scrollable |
| `mostrar_tabla(datos, columnas, titulo)` | Tabla de datos en ventana con DataGrid |
| `con_progreso(elems, funcion, titulo)` | Barra de progreso mientras procesa una lista |
| `seleccionar_parametros(params, titulo)` | Seleccion multiple de parametros Revit |
| `seleccionar_niveles(doc, titulo, multiples)` | Dialogo para elegir niveles del documento |
| `seleccionar_categorias(doc, titulo, multiples)` | Dialogo para elegir categorias del modelo |

---

## Ejemplos

### Pedir parametros al usuario y aplicar a elementos

```python
from lib_ui import formulario, confirmar
from lib_arquitectura import obtener_muros

datos = formulario({
    "Marca": "",
    "Comentarios": "",
    "Codigo": ""
}, titulo="Datos para muros")

if datos and confirmar("Aplicar a todos los muros?"):
    from lib_general import iniciar_transaccion, finalizar_transaccion
    iniciar_transaccion()
    for muro in obtener_muros():
        for param, valor in datos.items():
            p = muro.LookupParameter(param)
            if p and not p.IsReadOnly:
                p.Set(valor)
    finalizar_transaccion()
OUT = [datos]
```

### Seleccionar archivo Excel y leer con pandas

```python
from lib_ui import pedir_archivo
from lib_excel import leer_excel_pandas

ruta = pedir_archivo(filtro="Excel (*.xlsx)|*.xlsx")
df = leer_excel_pandas(ruta) if ruta else None
OUT = [df.to_dict("records") if df is not None else None]
```

### Procesar elementos con barra de progreso

```python
from lib_ui import con_progreso
from lib_arquitectura import obtener_habitaciones

habitaciones = obtener_habitaciones()

def etiquetar(hab, i):
    p = hab.LookupParameter("Indice")
    if p and not p.IsReadOnly:
        p.Set(i + 1)
    return hab.Id.IntegerValue

OUT = [con_progreso(habitaciones, etiquetar, titulo="Etiquetando...")]
```

### QA/QC — elementos sin parametros obligatorios

```python
from lib_scientific import analisis_calidad_datos
from lib_arquitectura import obtener_muros

incompletos = analisis_calidad_datos(
    obtener_muros(), ["Marca", "Comentarios", "Descripcion del tipo"]
)
OUT = [incompletos]
```

### Clustering de equipos MEP por zona

```python
from lib_scientific import clustering_por_posicion
from lib_instalaciones import obtener_equipos_mecanicos

zonas = clustering_por_posicion(obtener_equipos_mecanicos(), n_grupos=4)
OUT = [[e.Id.IntegerValue for e in zona] for zona in zonas.values()]
```

---

## Compatibilidad de unidades (Revit 2024+)

Todas las funciones de conversion usan `UnitTypeId` (nunca `DisplayUnitType`).
Los `ElementId` se convierten con `id_a_int()` que soporta `.Value` (Revit 2024+)
e `.IntegerValue` (Revit 2023 y anteriores).

## Licencia

MIT — uso libre con atribucion a Kevin Himmelreich
