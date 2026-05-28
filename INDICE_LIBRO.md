# Índice del libro → RevitPythonLibrary

Referencia cruzada exhaustiva entre **"Más allá de Dynamo / Revit 2023"** (15 capítulos, p.37–679)
y las funciones de la biblioteca RevitPythonLibrary.

**Leyenda:**
- `lib_modulo.funcion()` → función implementada
- *(no implementado — candidato a lib_X.py)* → funcionalidad pendiente de agregar
- *(conceptual — fundamento Python/Revit)* → concepto teórico del libro, sin función directa

---

## i. INTRODUCCIÓN A LA PROGRAMACIÓN (p.37)

| Sección | Función / módulo |
|---|---|
| Evolución natural: Dynamo → Python | *(conceptual — ver README.md)* |
| Dynamo — nodos Python Script | Patrón base de todos los módulos: `DocumentManager`, `TransactionManager` |
| DesignScript — sintaxis básica | *(conceptual — DesignScript es nativo de Dynamo)* |
| Conceptos de programación imperativa | *(conceptual — fundamento Python)* |
| Variables, tipos y flujo de control | *(conceptual — fundamento Python)* |

---

## ii. PYTHON (p.43)

### 1. Introducción a Python

| Sección | Función / módulo |
|---|---|
| Historia y versiones (2.7 vs 3.x) | *(conceptual — fundamento Python)* |
| IronPython en Dynamo | *(conceptual — ver README.md → requisitos)* |

### 2. Entorno de trabajo

| Sección | Función / módulo |
|---|---|
| Editor de Python en Dynamo | *(conceptual — fundamento Python)* |
| VS Code + extensiones | *(conceptual — fundamento Python)* |

### 3. Importar librerías (clr)

| Sección | Función / módulo |
|---|---|
| import clr / AddReference | Cabecera estándar de todos los módulos de la biblioteca |
| Importar RevitAPI / RevitServices | Patrón de importación en `lib_general.py`, `lib_transacciones.py` |
| Importar System.Windows.Forms | `lib_ui.py` (formularios WPF/Windows Forms) |

### 4. Tipos básicos de datos

| Sección | Función / módulo |
|---|---|
| 4.1 Números (int, float, complex) | *(conceptual — fundamento Python)* |
| 4.2 Textos — str, format, f-strings | *(conceptual — fundamento Python)* |
| 4.2 Textos — Expresiones regulares (RegEx) | `lib_arquitectura.clasificar_habitaciones_por_nombre(habs, regex)` |
| 4.3 Booleanos — True / False | *(conceptual — fundamento Python)* |
| 4.3 Booleanos — isinstance() / type() | Usado internamente en `lib_general.unwrap()`, `lib_general.aplanar_lista()` |
| 4.4 Tipo de elemento (Element) | `lib_general.unwrap(elem)`, `lib_general.unwrap_lista(elems)` |
| 4.5 Casting (conversión de tipos) | `lib_general.id_a_int()`, `lib_general.pies_a_metros()` |

### 5. Variables

| Sección | Función / módulo |
|---|---|
| Declarar y reasignar variables | *(conceptual — fundamento Python)* |
| Variables globales en módulos | Patrón `doc`, `uidoc`, `app` en todos los módulos |

### 6. Comentarios y depuración

| Sección | Función / módulo |
|---|---|
| Comentarios # y docstrings | *(conceptual — fundamento Python)* |
| Depuración con OUT y print | *(conceptual — patrón Dynamo: OUT = resultado)* |

### 7. Operadores

| Sección | Función / módulo |
|---|---|
| Aritméticos, comparación, lógicos | *(conceptual — fundamento Python)* |
| Operador in / not in para listas | Usado en filtros de `lib_general`, `lib_arquitectura` |

### 8. Conjuntos de datos

| Sección | Función / módulo |
|---|---|
| 8.1 Listas — crear, indexar, slicing | *(conceptual — fundamento Python)* |
| 8.1 Listas — transponer / aplanar | `lib_general.aplanar_lista(lista)` |
| 8.1 Listas — ordenar, reverse | Usado en `lib_vistas.ordenar_planificacion_por_campo()` |
| 8.2 Tuplas — inmutabilidad, unpacking | *(conceptual — fundamento Python)* |
| 8.3 Conjuntos (set) — unión, intersección | *(conceptual — fundamento Python)* |
| 8.4 Diccionarios — crear, acceder, iterar | `lib_general.obtener_todos_parametros(elem)`, `lib_general.obtener_parametros_tipo(elem)`, `lib_general.agrupar_por_parametro(elems, nombre)` |

### 9. Herramientas de programación funcional

| Sección | Función / módulo |
|---|---|
| filter() | `lib_general.filtrar_por_valor_parametro(cat, nombre, val)` |
| map() | `lib_general.obtener_ids_int(elems)` |
| reduce() | *(conceptual — fundamento Python)* |
| zip() | Usado en `lib_excel.exportar_parametros_a_excel()` |

### 10. Condicionales

| Sección | Función / módulo |
|---|---|
| if / elif / else | *(conceptual — fundamento Python)* |
| Expresión ternaria (x if c else y) | Usado en múltiples módulos para valores por defecto |

### 11. Bucles

| Sección | Función / módulo |
|---|---|
| 11.1 while — bucle con condición | *(conceptual — fundamento Python)* |
| 11.2 for — iterar sobre listas | Base de todas las funciones de colección de la biblioteca |
| 11.3 Comprensión de listas [ ] | Usado en `lib_general.agrupar_por_parametro()`, `lib_coordinacion.exportar_parametros_a_csv()` |
| 11.4 Comprensión de diccionarios { } | Usado en `lib_general.obtener_todos_parametros()` |
| 11.5 Comprensión de conjuntos | *(conceptual — fundamento Python)* |

### 12. Funciones

| Sección | Función / módulo |
|---|---|
| 12.1 def — definir función | *(conceptual — fundamento Python)* |
| 12.2 Argumentos y parámetros | *(conceptual — fundamento Python)* |
| 12.3 Recursividad | `lib_general.aplanar_lista(lista)` |
| 12.3 Crear biblioteca de funciones | Toda la biblioteca `RevitPythonLibrary` |
| 12.4 Funciones built-in de Python | `lib_general.id_a_int()`, `lib_general.iniciar_transaccion()` |
| 12.5 Alcance Local & Global (scope) | Patrón de importación en `lib_completa.py` |
| 12.6 Funciones Anónimas (lambda) | `lib_general.filtrar_por_valor_parametro()` |
| 12.7 Decoradores (@decorator) | *(no implementado — candidato a decoradores de transacción)* |

### 13. Excepciones (Try / Except)

| Sección | Función / módulo |
|---|---|
| try / except / finally | `lib_transacciones.transaccion_nativa(funcion, nombre)` (rollback automático) |
| raise — lanzar excepción | `lib_transacciones.finalizar_transaccion_nativa(tx, confirmar=False)` |
| Excepciones de Revit API | Manejo de `InvalidOperationException` en `lib_transacciones` |

### 14. Errores comunes en IronPython

| Sección | Función / módulo |
|---|---|
| Tipos Revit vs Python nativo | `lib_general.unwrap()` resuelve elementos Dynamo → Revit |
| Unidades internas (pies) vs metros | `lib_general.pies_a_metros()`, `lib_general.metros_a_pies()` |
| None vs Null en IronPython | Patrón de guardia en todos los módulos |

### 15. Iteradores

| Sección | Función / módulo |
|---|---|
| iter() / next() | *(conceptual — fundamento Python)* |
| Iteradores en FilteredElementCollector | Base de `lib_general.filtrar_por_valor_parametro()` |

### 16. Generadores (yield)

| Sección | Función / módulo |
|---|---|
| yield — crear generadores | *(no implementado — candidato a optimización de colectores)* |
| Expresiones generadoras ( ) | *(conceptual — fundamento Python)* |

### 17. Clases y Herencia

| Sección | Función / módulo |
|---|---|
| class — definir clase | Patrón de clase usado en `lib_ui.formulario()` (WPF) |
| __init__ — constructor | Patrón de todas las clases de la biblioteca |
| Herencia (class Hijo(Padre)) | `lib_seleccion_ui.py` hereda `ISelectionFilter` de RevitAPI |
| Métodos especiales (__str__, __repr__) | *(conceptual — fundamento Python)* |

### 18. Otros módulos de Python

| Sección | Función / módulo |
|---|---|
| 18.1 datetime — fechas y horas | `lib_bases_datos.guardar_configuracion()` (timestamps en JSON) |
| 18.2 math — módulo matemáticas | `lib_geometria.calcular_centroide_numpy()`, `lib_geometria.distancias_entre_puntos_numpy()` (usa math internamente) |
| 18.3 random — números aleatorios | `lib_scientific.py` (numpy.random disponible) |
| 18.4 os / sys — sistema operativo | `lib_bases_datos.leer_json()`, `lib_bases_datos.escribir_json()`, `lib_bases_datos.leer_csv()`, `lib_bases_datos.escribir_csv()` |

### 19. Bases de datos

| Sección | Función / módulo |
|---|---|
| 19.1 Archivos de texto (.txt / .csv) | `lib_bases_datos.leer_csv()`, `lib_bases_datos.escribir_csv()` |
| 19.2 JSON — leer y escribir | `lib_bases_datos.leer_json()`, `lib_bases_datos.escribir_json()`, `lib_bases_datos.exportar_parametros_elementos()`, `lib_bases_datos.importar_parametros_desde_json()` |
| 19.3 SQLite | *(no implementado — candidato a lib_bases_datos.py)* |

### 20. Python 3 / CPython

| Sección | Función / módulo |
|---|---|
| 20.1 Instalar bibliotecas en CPython 3 | `lib_scientific.instalar_dependencias_scientific()` |
| 20.2 NumPy — arrays y álgebra | `lib_geometria.puntos_a_array_numpy()`, `lib_geometria.calcular_centroide_numpy()`, `lib_geometria.distancias_entre_puntos_numpy()`, `lib_geometria.ajuste_plano_numpy()`, `lib_scientific.xyz_a_numpy()`, `lib_scientific.numpy_a_xyz()` |
| 20.3 Pandas — DataFrames | `lib_scientific.elementos_a_dataframe()`, `lib_scientific.dataframe_a_parametros()`, `lib_scientific.schedule_a_dataframe()`, `lib_excel.leer_excel_pandas()`, `lib_excel.escribir_excel_pandas()` |
| 20.4 Matplotlib — gráficas | `lib_scientific.graficar_histograma()`, `lib_scientific.graficar_scatter()` |
| 20.5 Shapely — geometría 2D | `lib_scientific.poligono_shapely()`, `lib_scientific.interseccion_shapely()` |
| 20.6 NetworkX — grafos | `lib_scientific.grafo_conexiones()`, `lib_scientific.ruta_mas_corta()` |
| 20.7 SciPy — cálculo científico | `lib_scientific.calcular_estadisticas()` |

---

## iii. REVIT API - INTRODUCCIÓN (p.145)

### 1-3. Fundamentos de la API

| Sección | Función / módulo |
|---|---|
| 1. Qué es la Revit API | *(conceptual — ver README.md)* |
| 2. Revit API Browser / RevitLookup | *(conceptual — herramienta externa)* |
| 3. Diagrama de objetos Revit | *(conceptual — ver README.md)* |

### 4. Plantilla de Python Script

| Sección | Función / módulo |
|---|---|
| 4.1 Estructura del nodo Python en Dynamo | *(conceptual — patrón OUT = resultado)* |
| 4.2 Plantilla de Python Script | Cabecera de todos los módulos: `import clr` → `AddReference` → `DocumentManager` |

### 5. El objeto Document

| Sección | Función / módulo |
|---|---|
| Acceder a Document activo | `doc` disponible en todos los módulos |
| Diferencia Application / Document / UIDocument | `lib_colaborativo.abrir_documento()`, `lib_colaborativo.cerrar_documento()` |

### 6. Diferencias Document / UIDocument / Application

| Sección | Función / módulo |
|---|---|
| Document (DB) | Usado en `lib_general`, `lib_transacciones` |
| UIDocument (UI) | Usado en `lib_seleccion_ui`, `lib_ui` |
| Application / UIApplication | `lib_colaborativo.abrir_documento()` |

### 7. Desenvolviendo elementos de Revit

| Sección | Función / módulo |
|---|---|
| UnwrapElement — Dynamo → Revit | `lib_general.unwrap(elem)`, `lib_general.unwrap_lista(elems)` |
| Acceder a propiedades nativas | `lib_general.obtener_valor_parametro(elem, nombre)` |

### 8. Geometría en Revit API

| Sección | Función / módulo |
|---|---|
| 8.1 Sistema de coordenadas | `lib_transformaciones.crear_transform_por_ejes()` |
| 8.2 Puntos (XYZ) | `lib_geometria.crear_linea()`, `lib_transformaciones.transformar_punto()` |
| 8.2 Vectores (XYZ como vector) | `lib_transformaciones.vector_entre_puntos()`, `lib_transformaciones.transformar_vector()` |
| 8.2 Líneas / Curvas | `lib_geometria.crear_linea()`, `lib_geometria.crear_arco()`, `lib_geometria.crear_nurbs_por_puntos()` |
| 8.2 BoundingBox | `lib_general.filtrar_por_boundingbox()`, `lib_general.filtrar_dentro_de_bbox()` |
| 8.2 Sólidos | `lib_geometria.booleano_interseccion()`, `lib_geometria.booleano_union()`, `lib_geometria.booleano_diferencia()` |
| 8.2 Caras y Aristas | `lib_geometria.obtener_caras_solido()`, `lib_geometria.obtener_aristas_solido()` |
| 8.3 De Revit a Dynamo (wrappers) | `lib_general.unwrap()` (inverso: elementos nativos) |
| 8.3 De Dynamo a Revit (unwrap) | `lib_general.unwrap()` |

---

## iv. REVIT API - COLECCIONAR ELEMENTOS (p.167)

### 1. FilteredElementCollector (FEC)

| Sección | Función / módulo |
|---|---|
| 1.1 Buscar en todo el documento | Base de `lib_general.filtrar_por_valor_parametro()`, `lib_arquitectura.obtener_habitaciones()` |
| 1.2 Buscar en vista específica | `lib_vistas.obtener_elementos_visibles_en_vista()`, `lib_general.obtener_anotaciones_en_vista()` |
| 1.3 Buscar en selección actual | `lib_seleccion_ui.obtener_seleccion_actual()` |

### 1.4 Filtros rápidos (Quick Filters)

| Sección | Función / módulo |
|---|---|
| Por Categoría (OfCategory) | `lib_general.filtrar_por_valor_parametro(cat_bic, ...)` |
| Por Clase (OfClass) | `lib_general.filtrar_por_valor_parametro()` (WhereElementIsNotElementType) |
| Múltiples categorías (MultiCategoryFilter) | `lib_general.obtener_anotaciones_en_vista(vista, cat_bic)` |
| Tipos de familia (FamilySymbol) | `lib_familias.obtener_tipos_de_familia()` |
| Dependientes de vista | *(no implementado — candidato a lib_vistas.py)* |
| Opciones de diseño (DesignOptionFilter) | *(no implementado — candidato a lib_general.py)* |
| Controlados por línea (line-based) | *(no implementado — candidato a lib_geometria.py)* |
| Estructurales (StructuralFilter) | `lib_estructura.obtener_pilares_por_nivel()`, `lib_estructura.obtener_vigas_por_nivel()` |
| Muros cortina (CurtainWallFilter) | *(no implementado — candidato a lib_arquitectura.py)* |
| Por subproyecto (WorksetFilter) | `lib_colaborativo.obtener_worksets()` |
| BoundingBox intersecta | `lib_general.filtrar_por_boundingbox(bbox, cat_bic, tol)` |
| Dentro de BoundingBox | `lib_general.filtrar_dentro_de_bbox(bbox, cat_bic, tol)` |
| Punto dentro de BoundingBox | `lib_general.filtrar_contiene_punto(punto, cat_bic, tol)` |
| Filtro Excluyente (ExclusionFilter) | `lib_general.excluir_elementos(ids, cat_bic)` |
| Concatenación de filtros rápidos | `lib_general.combinar_filtros_y(filtros)`, `lib_general.combinar_filtros_o(filtros)` |

### 1.5 Filtros lentos (Slow Filters)

| Sección | Función / módulo |
|---|---|
| Por valor de parámetro | `lib_general.filtrar_por_valor_parametro(cat, nombre, val)` |
| Por ejemplar de familia (FamilyInstanceFilter) | *(no implementado — candidato a lib_familias.py)* |
| Por nivel (LevelFilter) | `lib_estructura.obtener_pilares_por_nivel()`, `lib_arquitectura.obtener_habitaciones_por_nivel()` |
| Por uso estructural | `lib_estructura.obtener_vigas_por_nivel()` |
| Por función de muro | `lib_arquitectura.obtener_muros_por_tipo()` |
| Por material | `lib_estructura.obtener_material_estructura()` |
| Con etiquetas | *(no implementado — candidato a lib_vistas.py)* |
| Seleccionables en vista | `lib_vistas.obtener_elementos_visibles_en_vista()` |
| Filtros booleanos (AND / OR) | `lib_general.combinar_filtros_y(filtros)`, `lib_general.combinar_filtros_o(filtros)` |
| Filtrar habitaciones | `lib_arquitectura.obtener_habitaciones()` |
| Filtrar espacios MEP | *(no implementado — candidato a lib_instalaciones.py)* |
| Filtrar áreas | `lib_arquitectura.crear_separacion_de_area()` |
| Filtrar elementos que se intercepten | `lib_coordinacion.detectar_colisiones_bbox()`, `lib_coordinacion.detectar_colisiones_solidos()` |

### 1.6 Filtros lógicos

| Sección | Función / módulo |
|---|---|
| LogicalAndFilter | `lib_general.combinar_filtros_y(filtros)` |
| LogicalOrFilter | `lib_general.combinar_filtros_o(filtros)` |

### 1.7 Otras operaciones FEC

| Sección | Función / módulo |
|---|---|
| .ToElements() — lista completa | Base de todos los colectores de la biblioteca |
| .FirstElement() — primer resultado | Usado en `lib_familias.cargar_familia()` |
| .GetElementCount() — cantidad | *(conceptual — uso directo de FEC)* |
| Iterador (.GetEnumerator) | *(conceptual — fundamento Python/FEC)* |
| Intersección / Unión de resultados | `lib_geometria.booleano_interseccion()`, `lib_geometria.booleano_union()` |

### 1.8 Pandas-Collector

| Sección | Función / módulo |
|---|---|
| Convertir FEC a DataFrame | `lib_scientific.elementos_a_dataframe()` |
| Filtrar y agrupar con Pandas | `lib_scientific.dataframe_a_parametros()` |

### 2. Conversión de elementos

| Sección | Función / módulo |
|---|---|
| Element.Id → int | `lib_general.id_a_int()`, `lib_general.obtener_ids_int(elems)` |
| doc.GetElement(id) | Usado internamente en múltiples módulos |
| UniqueId | `lib_bases_datos.obtener_guid_elemento()` |

### 3. Coleccionando Subproyectos (Worksets)

| Sección | Función / módulo |
|---|---|
| Obtener worksets del modelo | `lib_colaborativo.obtener_worksets()` |
| Filtrar por workset | `lib_coordinacion.detectar_elementos_sin_workset()` |

---

## v. REVIT API – MODIFICAR DOCUMENTO (p.201)

### 1. Transacciones

| Sección | Función / módulo |
|---|---|
| 1.1 TransactionManager de Dynamo | `lib_general.iniciar_transaccion()`, `lib_general.finalizar_transaccion()` |
| 1.2 Transacciones nativas de Revit (Transaction) | `lib_transacciones.iniciar_transaccion_nativa()`, `lib_transacciones.finalizar_transaccion_nativa()`, `lib_transacciones.transaccion_nativa()` |
| 1.2 Grupos de transacciones (TransactionGroup) | `lib_transacciones.ejecutar_en_grupo()` |
| 1.2 Subtransacciones (SubTransaction) | `lib_transacciones.ejecutar_subtransaccion()`, `lib_transacciones.eliminar_elemento_en_subtransaccion()` |
| 1.2 Deshacer transacciones (RollBack) | `lib_transacciones.finalizar_transaccion_nativa(tx, confirmar=False)` |
| 1.2 Modificaciones de documento Revit 2023 | `lib_transacciones.comparar_documentos()` |

### 2. Eliminar elementos

| Sección | Función / módulo |
|---|---|
| doc.Delete(id) | `lib_transacciones.eliminar_elemento_en_subtransaccion()` |
| Eliminar lista de elementos | Patrón usado en `lib_familias.eliminar_familias_no_usadas()` |

### 3. Mover elementos (`lib_transformaciones`)

| Sección / operación | Función |
|---|---|
| Mover por vector XYZ (pies internos) | `lib_transformaciones.mover_elemento(elem, vector_xyz)` |
| Mover por desplazamiento en metros | `lib_transformaciones.mover_elemento_m(elem, dx_m, dy_m, dz_m)` |
| Mover varios elementos en bloque | `lib_transformaciones.mover_elementos(lista_elems, vector_xyz)` |
| Mover a posición absoluta (LocationPoint) | `lib_transformaciones.establecer_punto_ubicacion(elem, punto_xyz)` |
| Redefinir curva de ubicación (muro, viga…) | `lib_transformaciones.establecer_curva_ubicacion(elem, curva)` |
| Alinear elemento a punto destino | `lib_transformaciones.alinear_a_punto(elem, punto_destino_xyz)` |
| Obtener ubicación (punto o curva) | `lib_transformaciones.obtener_ubicacion(elem)` |
| Obtener punto de ubicación | `lib_transformaciones.obtener_punto_ubicacion(elem)` |
| Obtener curva de ubicación | `lib_transformaciones.obtener_curva_ubicacion(elem)` |
| Calcular vector entre dos puntos | `lib_transformaciones.vector_entre_puntos(origen, destino)` |
| Distancia entre dos puntos (metros) | `lib_transformaciones.distancia_entre_puntos_m(pto_a, pto_b)` |
| Centroide del BoundingBox de un elemento | `lib_transformaciones.centroide_bbox(elem)` |

### 4. Copiar elementos (`lib_transformaciones`)

| Sección / operación | Función |
|---|---|
| Copiar un elemento por vector | `lib_transformaciones.copiar_elemento(elem, vector_xyz)` |
| Copiar varios elementos por vector | `lib_transformaciones.copiar_elementos(lista_elems, vector_xyz)` |
| Copiar elemento a otro nivel (ajusta Z) | `lib_transformaciones.copiar_elemento_a_nivel(elem, nivel_destino)` |
| Copiar elementos entre documentos / links | `lib_transformaciones.copiar_elementos_entre_documentos(doc_origen, ids, doc_destino, transform)` |

### 5. Rotar elementos (`lib_transformaciones`)

| Sección / operación | Función |
|---|---|
| Rotar un elemento alrededor de eje + punto | `lib_transformaciones.rotar_elemento(elem, punto_xyz, angulo_grados, eje_xyz)` |
| Rotar sobre su propio punto de ubicación | `lib_transformaciones.rotar_elemento_en_propio_punto(elem, angulo_grados, eje_xyz)` |
| Rotar varios elementos a la vez | `lib_transformaciones.rotar_elementos(lista_elems, punto_xyz, angulo_grados, eje_xyz)` |
| Rotar una vista (sección, alzado…) | `lib_transformaciones.rotar_vista(vista, punto_xyz, angulo_grados)` |
| Leer ángulo de rotación actual (LocationPoint) | `lib_transformaciones.obtener_rotacion_ubicacion(elem)` |
| Leer ángulo desde HandOrientation | `lib_transformaciones.obtener_angulo_desde_hand_orientation(elem)` |

### 6. Espejar elementos (`lib_transformaciones`)

| Sección / operación | Función |
|---|---|
| Espejar lista de elementos (con/sin copia) | `lib_transformaciones.espejar_elementos(lista_elems, normal_xyz, origen_xyz, crear_copia)` |
| Espejar un elemento único | `lib_transformaciones.espejar_elemento(elem, normal_xyz, origen_xyz, crear_copia)` |
| Crear plano de espejado (Plane) | `lib_transformaciones.crear_plano_espejo(normal_xyz, origen_xyz)` |

### 7. Voltear / Flip (`lib_transformaciones`)

| Sección / operación | Función |
|---|---|
| Flip principal del elemento (Flip()) | `lib_transformaciones.voltear_elemento(elem)` |
| Flip de cara (FacingOrientation) | `lib_transformaciones.voltear_cara(instancia)` |
| Flip de mano (HandOrientation) | `lib_transformaciones.voltear_mano(instancia)` |
| Invertir extremos de viga estructural | `lib_transformaciones.voltear_extremos_viga(viga)` |
| Consultar si cara está volteada | `lib_transformaciones.obtener_esta_volteado_cara(instancia)` |
| Consultar si mano está volteada | `lib_transformaciones.obtener_esta_volteado_mano(instancia)` |
| Consultar si está espejado (Mirrored) | `lib_transformaciones.obtener_esta_espejado(instancia)` |

### 8. Anclar / Desanclar (`lib_transformaciones`)

| Sección / operación | Función |
|---|---|
| Anclar un elemento (Pinned = True) | `lib_transformaciones.anclar_elemento(elem, anclar=True)` |
| Desanclar un elemento | `lib_transformaciones.desanclar_elemento(elem)` |
| Anclar / desanclar lista en bloque | `lib_transformaciones.anclar_lista(lista_elems, anclar)` |
| Consultar si está anclado | `lib_transformaciones.esta_anclado(elem)` |

### 9. Orientación de elementos (`lib_transformaciones`)

| Sección / operación | Función |
|---|---|
| HandOrientation (dirección de mano) | `lib_transformaciones.obtener_orientacion_mano(elem)` |
| FacingOrientation (dirección de cara) | `lib_transformaciones.obtener_orientacion_cara(elem)` |
| Resumen completo de orientación | `lib_transformaciones.obtener_orientacion_completa(instancia)` |

### 10. Matemática de Transform (`lib_transformaciones`)

> Transform es el objeto de Revit que describe cómo pasar de un sistema de
> coordenadas a otro. Se usa especialmente para convertir puntos/vectores entre
> un modelo vinculado y el modelo activo.

| Sección / operación | Función |
|---|---|
| Transform de traslación pura | `lib_transformaciones.crear_transform_traslacion(vector_xyz)` |
| Transform de rotación (eje + ángulo) | `lib_transformaciones.crear_transform_rotacion(eje_xyz, angulo_grados)` |
| Transform por origen y ejes locales | `lib_transformaciones.crear_transform_por_ejes(origen, eje_x, eje_y, eje_z)` |
| Aplicar Transform a un punto XYZ | `lib_transformaciones.transformar_punto(transform, punto_xyz)` |
| Aplicar Transform a un vector XYZ | `lib_transformaciones.transformar_vector(transform, vector_xyz)` |
| Invertir un Transform | `lib_transformaciones.invertir_transform(transform)` |
| Combinar dos Transform en secuencia | `lib_transformaciones.combinar_transforms(t_a, t_b)` |
| Obtener Transform de una FamilyInstance | `lib_transformaciones.obtener_transform_elemento(instancia)` |
| Transform.Identity (sin transformación) | `Transform.Identity` — disponible tras `from Autodesk.Revit.DB import Transform` |

#### Workflow: Transformaciones entre link y modelo activo en Dynamo

```
# 1. Obtener la instancia del link
link_inst = lib_coordinacion.obtener_links_revit()[0]

# 2. Obtener el Transform que lleva coordenadas del link → coordenadas del host
tf = link_inst.GetTotalTransform()

# 3. Convertir un punto del link al espacio del modelo activo
punto_link = lib_transformaciones.obtener_punto_ubicacion(elem_en_link)
punto_host = lib_transformaciones.transformar_punto(tf, punto_link)

# 4. Copiar elementos del link al modelo activo con posición correcta
doc_link   = link_inst.GetLinkDocument()
ids_link   = [e.Id for e in lista_elems_del_link]
copiados   = lib_transformaciones.copiar_elementos_entre_documentos(
                 doc_link, ids_link, doc, tf)

# 5. Mover un elemento del host para alinearlo con una posición del link
vector = lib_transformaciones.vector_entre_puntos(
             lib_transformaciones.obtener_punto_ubicacion(elem_host),
             punto_host)
lib_transformaciones.mover_elemento(elem_host, vector)
```

---

## vi. REVIT API - PARÁMETROS (p.207)

### 1. Tipos de parámetros

| Sección | Función / módulo |
|---|---|
| Parámetros de familia vs de tipo | `lib_general.obtener_todos_parametros(elem)`, `lib_general.obtener_parametros_tipo(elem)` |
| Parámetros BuiltIn vs definidos por usuario | `lib_general.obtener_valor_parametro(elem, nombre)` |

### 2. Parámetros de Familias

| Sección | Función / módulo |
|---|---|
| 2.1 Estructura: Family / FamilySymbol / FamilyInstance | `lib_familias.obtener_tipos_de_familia()`, `lib_familias.activar_tipo_familia()` |
| 2.2 Acceder a parámetros de familia | `lib_general.obtener_todos_parametros(elem)`, `lib_general.obtener_parametros_tipo(elem)` |
| 2.2 Acceso a parámetro específico (LookupParameter) | `lib_general.obtener_valor_parametro(elem, nombre)` |
| 2.2 Lectura del valor (AsString / AsDouble / AsInteger / AsElementId) | `lib_general.obtener_valor_parametro(elem, nombre)` |
| 2.2 Definir valor (Set) | `lib_general.establecer_valor_parametro(elem, nombre, val)` |
| 2.2 Opciones de formato (FormatOptions) | `lib_general.pies_a_metros()`, `lib_general.metros_a_pies()` |

### 3. Parámetros globales

| Sección | Función / módulo |
|---|---|
| Obtener parámetros globales del proyecto | `lib_general.obtener_valor_parametro()` con parámetros BuiltIn |
| Crear parámetro global | *(no implementado — candidato a lib_general.py)* |
| Enlazar parámetro a elemento | *(no implementado — candidato a lib_general.py)* |

### 4. Parámetros de grupo (Group Parameters)

| Sección | Función / módulo |
|---|---|
| Obtener parámetros de grupo | *(no implementado — candidato a lib_general.py)* |
| Grupos de parámetros (BuiltInParameterGroup) | *(conceptual — ver Revit API docs)* |

### 5. BuiltInParameters (BIP)

| Sección | Función / módulo |
|---|---|
| Enumerar BuiltInParameters | `lib_general.obtener_todos_parametros(elem)` |
| Tipo de almacenamiento (StorageType) | `lib_general.obtener_valor_parametro()` (gestiona AsString/AsDouble/AsInteger/AsElementId) |
| ROOM_NAME, ROOM_NUMBER, LEVEL_NAME | `lib_arquitectura.obtener_nombre_habitacion()`, `lib_arquitectura.obtener_numero_habitacion()`, `lib_coordinacion.obtener_nivel_elemento()` |

### 6. Parámetros compartidos (Shared Parameters)

| Sección | Función / módulo |
|---|---|
| Detectar parámetros compartidos (IsShared) | `lib_general.obtener_todos_parametros(elem)` |
| Iterar parámetros del proyecto | `lib_general.obtener_todos_parametros(elem)`, `lib_general.obtener_parametros_tipo(elem)` |
| Ruta del archivo .txt activo | `lib_parametros.obtener_ruta_archivo_compartidos(app)` |
| Apuntar / crear archivo .txt | `lib_parametros.establecer_archivo_compartidos(app, ruta)` |
| Abrir DefinitionFile | `lib_parametros.abrir_archivo_compartidos(app)` |
| Volcar contenido del .txt | `lib_parametros.listar_grupos_y_definiciones(def_file)` |
| Crear grupo en el .txt | `lib_parametros.crear_grupo(def_file, nombre)` |
| Obtener grupo del .txt | `lib_parametros.obtener_grupo(def_file, nombre)` |
| Crear definición (genérico) | `lib_parametros.crear_definicion(grupo, nombre, SpecTypeId.*)` |
| Crear definición Texto | `lib_parametros.crear_definicion_texto(grupo, nombre)` |
| Crear definición Entero | `lib_parametros.crear_definicion_entero(grupo, nombre)` |
| Crear definición Número | `lib_parametros.crear_definicion_numero(grupo, nombre)` |
| Crear definición Longitud | `lib_parametros.crear_definicion_longitud(grupo, nombre)` |
| Crear definición Área | `lib_parametros.crear_definicion_area(grupo, nombre)` |
| Crear definición Sí/No | `lib_parametros.crear_definicion_si_no(grupo, nombre)` |
| Vincular al proyecto (Insert en BindingMap) | `lib_parametros.vincular_a_proyecto(doc, app, defn, lista_bic)` |
| Actualizar binding (cambiar categorías) | `lib_parametros.actualizar_vinculo_proyecto(doc, app, defn, lista_bic)` |
| Desvincular del proyecto | `lib_parametros.desvincular_de_proyecto(doc, defn)` |
| Consultar si está vinculado | `lib_parametros.esta_vinculado_proyecto(doc, defn)` |
| Listar todos los compartidos del proyecto | `lib_parametros.obtener_parametros_compartidos_proyecto(doc)` |
| Agregar compartido a familia | `lib_parametros.agregar_a_familia(doc, defn)` |
| Quitar parámetro de familia | `lib_parametros.quitar_de_familia(doc, nombre)` |
| Convertir local → compartido en familia | `lib_parametros.convertir_local_a_compartido(doc, nombre_local, defn)` |
| Buscar por GUID | `lib_parametros.buscar_por_guid(doc, guid_str)` |
| Flujo completo en una llamada | `lib_parametros.flujo_completo_compartido(app, doc, ruta, grupo, nombre, tipo, bics)` |

### 7. Parámetros de información del proyecto

| Sección | Función / módulo |
|---|---|
| Obtener ProjectInfo | `lib_bases_datos.cargar_configuracion()`, `lib_bases_datos.guardar_configuracion()` |
| Nombre de proyecto, número, cliente | `lib_general.obtener_valor_parametro(doc.ProjectInformation, "Project Name")` |
| Configuraciones de ruta | `lib_bases_datos.cargar_configuracion()`, `lib_bases_datos.guardar_configuracion()` |

### 8. Administrador de familias (FamilyManager)

| Sección | Función / módulo |
|---|---|
| FamilyManager — acceso | `lib_familias.obtener_parametros_familia(symbol)` |
| Insertar parámetros en familias | `lib_familias.obtener_parametros_familia()` |
| Obtener todos los parámetros de familia | `lib_familias.obtener_parametros_familia(symbol)` |
| Crear un tipo de familia | `lib_familias.activar_tipo_familia()` |
| Eliminar parámetros | *(no implementado — candidato a lib_familias.py)* |

### 8.1 Fórmulas de parámetros

| Sección | Función / módulo |
|---|---|
| Asignar fórmula a parámetro | *(no implementado — candidato a lib_familias.py)* |
| Leer fórmula de parámetro | *(no implementado — candidato a lib_familias.py)* |

### 9. Unidades

| Sección | Función / módulo |
|---|---|
| 9.1 Convertir unidades (UnitUtils) | `lib_general.pies_a_metros()`, `lib_general.metros_a_pies()`, `lib_general.mm_a_pies()`, `lib_general.pies_a_mm()` |
| 9.2 Convertir a unidades internas (pies) | `lib_general.metros_a_pies()`, `lib_general.mm_a_pies()` |
| 9.3 Convertir a unidades de modelo | `lib_general.pies_a_metros()`, `lib_general.pies_a_mm()` |
| 9.4 Cambios Revit 2021 (DisplayUnitType → UnitTypeId) | `lib_general.pies_a_metros()` (usa `UnitTypeId` internamente) |
| 9.5 Utilidades de unidades Revit 2022/2023 | Todos los métodos de conversión de `lib_general` |

### 10. Nuevas utilidades Revit 2022/2023

| Sección | Función / módulo |
|---|---|
| ParameterUtils — nuevas utilidades | *(no implementado — candidato a lib_general.py)* |
| ForgeTypeId para parámetros | *(conceptual — ver Revit 2022+ API docs)* |

### 11. Almacenamiento extendido (ExtensibleStorage)

| Sección | Función / módulo |
|---|---|
| 11.1 Crear esquema de datos (Schema) | *(no implementado — candidato a lib_bases_datos.py)* |
| 11.1 Escribir datos en elemento | `lib_bases_datos.guardar_configuracion()` (alternativa JSON) |
| 11.2 Leer datos de elemento | `lib_bases_datos.cargar_configuracion()` |
| 11.2 Filtrar por ExtensibleStorage | *(no implementado — candidato a lib_bases_datos.py)* |

---

## vii. REVIT API - VISTAS (p.257)

### 1. Conceptos generales

| Sección | Función / módulo |
|---|---|
| 1.1 Jerarquía de vistas en Revit | *(conceptual — ver libro p.257)* |
| 1.1 ViewType — tipos de vista | `lib_vistas.crear_vista_planta()`, `lib_vistas.crear_vista_3d_isometrica()`, `lib_vistas.crear_seccion_desde_curva()`, `lib_vistas.crear_alzado_en_punto()` |
| 1.1 Vista activa (ActiveView) | `lib_general.obtener_anotaciones_en_vista()` (usa vista activa) |
| 1.2 Plantillas de vistas — aplicar | `lib_vistas.aplicar_plantilla_de_vista()`, `lib_vistas.aplicar_plantilla_por_nombre()` |
| 1.2 Plantillas de vistas — obtener | `lib_vistas.aplicar_plantilla_por_nombre()` (busca por nombre) |
| 1.3 Crear filtros de vista (ParameterFilterElement) | `lib_vistas.crear_filtro_vista_por_texto()`, `lib_vistas.crear_filtro_vista_por_entero()`, `lib_vistas.crear_filtro_vista_combinado()` |
| 1.3 Añadir filtros a vista | `lib_vistas.aplicar_filtro_a_vista()` |
| 1.3 Modificar visibilidad de filtros | `lib_vistas.aplicar_filtro_a_vista(vista, filtro_id, visible, ogs)` |
| 1.3 Obtener filtros de vista | `lib_vistas.listar_filtros_de_vista()`, `lib_vistas.obtener_filtros_del_documento()` |
| 1.3 Eliminar filtros de vista | `lib_vistas.eliminar_filtro_de_vista()` |
| 1.3 Aislar elementos en vista | `lib_vistas.aislar_elementos_temporalmente()`, `lib_vistas.ocultar_elementos_en_vista()` |
| 1.3 Modos temporales de vista | `lib_vistas.aislar_elementos_temporalmente()`, `lib_vistas.convertir_temporal_a_permanente()` |
| 1.3 Duplicar vistas | `lib_vistas.duplicar_vista()`, `lib_vistas.duplicar_vistas()` |
| 1.3 Vistas dependientes | `lib_vistas.duplicar_vista_dependiente()` |
| 1.3 Convertir vistas dependientes a independientes | `lib_vistas.convertir_vista_a_independiente()` |
| 1.3 Recortar vista (CropBox) | `lib_vistas.activar_cropbox()`, `lib_vistas.establecer_cropbox()`, `lib_vistas.establecer_recorte_por_curvas()`, `lib_vistas.establecer_recorte_con_offset()` |
| 1.3 Caja de referencia (SectionBox) | `lib_vistas.crear_vista_3d_por_bbox()` |
| 1.3 Mostrar elementos ocultos | `lib_vistas.mostrar_elementos_en_vista()` |
| 1.3 Ocultar categorías | `lib_vistas.ocultar_categoria_en_vista()` |
| 1.3 Nivel de detalle (LOD) | `lib_vistas.establecer_nivel_detalle()` |
| 1.3 Disciplina de vista | `lib_vistas.establecer_disciplina()` |
| 1.3 Estilo visual | `lib_vistas.establecer_estilo_visual()` |
| 1.3 Escala de vista | `lib_vistas.establecer_escala()` |
| 1.3 Overrides gráficos de elementos | `lib_vistas.sobreescribir_grafico_elemento()`, `lib_vistas.limpiar_grafico_elemento()` |

### 2. Plantas

| Sección | Función / módulo |
|---|---|
| Crear plano de planta (FloorPlan) | `lib_vistas.crear_vista_planta()` |
| Crear plano de techo (CeilingPlan) | *(no implementado — candidato a lib_vistas.py)* |
| Crear plano de áreas | `lib_arquitectura.crear_separacion_de_area()` |
| 2.1 Rango de vista — obtener | `lib_vistas.obtener_rango_de_vista()`, `lib_vistas.obtener_rango_vista_completo()` |
| 2.1 Rango de vista — definir niveles y desfases | `lib_vistas.establecer_rango_de_vista()` |
| 2.2 Esquemas de color — obtener | *(no implementado — candidato a lib_vistas.py)* |
| 2.2 Esquemas de color — aplicar | *(no implementado — candidato a lib_vistas.py)* |
| 2.2 Leyendas de color — crear | *(no implementado — candidato a lib_vistas.py)* |
| 2.2 Vista colocada en plano (Revit 2023) | *(no implementado — candidato a lib_vistas.py)* |
| 2.1 Subyacente (Underlay) | *(no implementado — candidato a lib_vistas.py)* |
| Visibilidad de piezas (Parts) | *(no implementado — candidato a lib_vistas.py)* |
| Configuración de sol (Sun Settings) | *(no implementado — candidato a lib_vistas.py)* |
| Filtrar planos de área | *(no implementado — candidato a lib_vistas.py)* |

### 3. Alzados / Secciones

| Sección | Función / módulo |
|---|---|
| 3.1 Crear Alzados (Elevation) | `lib_vistas.crear_alzado_en_punto()` |
| 3.2 Crear secciones (Section) | `lib_vistas.crear_seccion_desde_curva()` |
| 3.2 Crear Llamadas (Callout) | `lib_vistas.crear_cartela()` |
| 3.2 Crear secciones de detalle | `lib_vistas.crear_vista_detalle()` |
| 3.2 Sección de sala (Room Section) | *(no implementado — candidato a lib_vistas.py)* |

### 4. Vistas tridimensionales

| Sección | Función / módulo |
|---|---|
| Vista isométrica (3D) | `lib_vistas.crear_vista_3d_isometrica()` |
| Vista 3D por SectionBox | `lib_vistas.crear_vista_3d_por_bbox()` |
| Vista 3D desde habitación | `lib_vistas.crear_vista_3d_por_habitacion()` |
| Vista 3D desde sección | `lib_vistas.crear_vista_3d_desde_seccion()` |
| Orientar vista 3D | `lib_vistas.establecer_orientacion_3d()`, `lib_vistas.copiar_orientacion_3d()` |
| Bloquear / desbloquear vista 3D | `lib_vistas.bloquear_vista_3d()` |
| Obtener SectionBox de vista 3D | `lib_vistas.obtener_section_box_3d()` |

### 5. Tablas de planificación (Schedules)

| Sección | Función / módulo |
|---|---|
| Buscar tabla por nombre | `lib_vistas.obtener_planificaciones()` |
| Modificar visualización (orden, totales) | `lib_vistas.ordenar_planificacion_por_campo()` |
| Crear tabla + añadir campos | `lib_vistas.crear_planificacion()`, `lib_vistas.anadir_campo_a_planificacion()` |
| Exportar tablas a CSV | `lib_bases_datos.exportar_schedule_a_csv()` |
| Exportar tablas a Excel | `lib_excel.exportar_schedule_a_excel()` |
| Obtener datos de tabla | `lib_vistas.obtener_datos_de_planificacion()` |

### 6. Planos (Sheets)

| Sección | Función / módulo |
|---|---|
| Crear planos | `lib_vistas.crear_plano()` |
| Añadir vistas a plano (Viewport) | `lib_vistas.anadir_vista_a_plano()`, `lib_vistas.centrar_vista_en_plano()` |
| 6.1 Duplicar planos (Revit 2023) | *(no implementado — candidato a lib_vistas.py)* |
| 6.2 Revisiones — crear | `lib_vistas.crear_revision()` |
| 6.2 Revisiones — obtener | `lib_vistas.obtener_revisiones()` |
| 6.2 Revisiones — asignar a plano | `lib_vistas.asignar_revision_a_plano()` |
| Imprimir / Exportar planos | `lib_vistas.exportar_vista_a_imagen()` |

### 7. Diseño y documentación

| Sección | Función / módulo |
|---|---|
| Leyendas (Legend views) | *(no implementado — candidato a lib_vistas.py)* |
| Navegador de proyectos (API) | *(no implementado — candidato a lib_vistas.py)* |
| Organizar browser por parámetros | *(no implementado — candidato a lib_vistas.py)* |

### 8. Elementos de referencia

| Sección | Función / módulo |
|---|---|
| 8.1 Niveles — Crear | `lib_coordinacion.crear_nivel()`, `lib_coordinacion.crear_niveles_en_bloque()` |
| 8.1 Niveles — Obtener | `lib_coordinacion.obtener_niveles()`, `lib_coordinacion.obtener_nivel_mas_cercano()` |
| 8.2 Rejillas / Ejes — Crear | `lib_general.crear_eje()` |
| 8.2 Rejillas / Ejes — Obtener | `lib_general.obtener_ejes()` |
| 8.2 Planos de referencia — Crear | `lib_general.crear_plano_referencia()` |
| 8.2 Planos de referencia — Obtener | `lib_general.obtener_planos_referencia()` |

### 9. Elementos de anotación

| Sección | Función / módulo |
|---|---|
| 9.1 Líneas de detalle | `lib_vistas.crear_curva_detalle()`, `lib_vistas.crear_curvas_detalle()` |
| 9.2 Cotas — crear cota lineal | `lib_vistas.crear_cota_lineal()` |
| 9.2 Cotas — propiedades detalladas (DimensionType) | *(no implementado — candidato a lib_vistas.py)* |
| 9.2 Cotas — modificar segmentos | *(no implementado — candidato a lib_vistas.py)* |
| 9.3 Etiquetas — etiquetar elementos (TagMode) | `lib_vistas.etiquetar_elemento()`, `lib_vistas.etiquetar_lista_de_elementos()` |
| 9.3 Etiquetas — posición y orientación | *(no implementado — candidato a lib_vistas.py)* |
| 9.3 Etiquetas — líderes (leader) | *(no implementado — candidato a lib_vistas.py)* |
| 9.3 Notas de texto | `lib_vistas.crear_nota_de_texto()` |

### 10. Elementos temporales

| Sección | Función / módulo |
|---|---|
| TemporaryViewMode — aislar / ocultar | `lib_vistas.aislar_elementos_temporalmente()` |
| Convertir temporal a permanente | `lib_vistas.convertir_temporal_a_permanente()` |
| Limpiar modo temporal | *(no implementado — candidato a lib_vistas.py)* |

---

## viii. REVIT API - FAMILIAS (p.343)

### 1. Familias cargables

| Sección | Función / módulo |
|---|---|
| 1.1 Cargar familia (.rfa) | `lib_familias.cargar_familia()` |
| 1.2 Cargar tipos específicos de familia | `lib_familias.obtener_tipos_de_familia()`, `lib_familias.activar_tipo_familia()` |
| 1.3 Insertar familia sin anfitrión (punto) | `lib_familias.colocar_instancia_familia()` |
| 1.3 Insertar familia con anfitrión (cara) | `lib_familias.colocar_instancia_en_cara()` |
| 1.4 Familias anidadas | `lib_familias.obtener_familias_por_categoria()` |
| 1.5 Crear geometrías en familias (FamilyCreationData) | *(no implementado — candidato a lib_familias.py)* |
| 1.6 Agrupar por proximidad | `lib_geometria.agrupar_puntos_por_proximidad()` |
| 1.7 Cortar geometrías (SolidOptions / CutGeometry) | `lib_geometria.booleano_diferencia()` |
| 1.8 Unir geometrías (JoinGeometryUtils) | `lib_geometria.booleano_union()` |
| Obtener parámetros de familia | `lib_familias.obtener_parametros_familia()` |

### 2. Familias de sistema

| Sección | Función / módulo |
|---|---|
| 2.1 Muros — Crear (Wall.Create) | `lib_arquitectura.crear_muro()` |
| 2.1 Muros — Propiedades (grosor, composición) | `lib_arquitectura.obtener_grosor_muro()`, `lib_arquitectura.obtener_composicion_muro()` |
| 2.1 Muros — Filtrar por tipo | `lib_arquitectura.obtener_muros_por_tipo()` |
| 2.1 Muros cortina — rejillas (CurtainGrid) | *(no implementado — candidato a lib_arquitectura.py)* |
| 2.1 Muros cortina — montantes (Mullion) | *(no implementado — candidato a lib_arquitectura.py)* |
| 2.1 Muros cortina — paneles (CurtainPanel) | *(no implementado — candidato a lib_arquitectura.py)* |
| 2.2 Suelos — Crear (Floor.Create) | `lib_arquitectura.crear_suelo()`, `lib_arquitectura.crear_suelo_desde_habitacion()` |
| 2.2 Suelos — Área | `lib_arquitectura.obtener_area_suelo()` |
| 2.2 Suelos — Abertura | `lib_arquitectura.crear_abertura_suelo()` |
| 2.3 Elementos Multicapa (CompoundStructure) | `lib_arquitectura.obtener_composicion_muro()`, `lib_arquitectura.modificar_grosor_capa_estructural()` |
| 2.4 Piezas (Parts) — crear y acceder | *(no implementado — candidato a lib_arquitectura.py)* |
| 2.5 Barandillas (Railing) — crear | *(no implementado — candidato a lib_arquitectura.py)* |
| 2.5 Barandillas — propiedades (path, type) | *(no implementado — candidato a lib_arquitectura.py)* |
| 2.6 Techos (Roof) — crear por huella | *(no implementado — candidato a lib_arquitectura.py)* |
| 2.6 Techos — propiedades | *(no implementado — candidato a lib_arquitectura.py)* |
| 2.7 Escaleras (Stair) — crear | *(no implementado — candidato a lib_arquitectura.py)* |
| 2.7 Escaleras — rellanos, tramos, barandillas | *(no implementado — candidato a lib_arquitectura.py)* |

### 3. Tipos de familia

| Sección | Función / módulo |
|---|---|
| Duplicar / crear tipos (NewFamilyType) | `lib_familias.activar_tipo_familia()` |
| Datos de identidad del tipo | `lib_familias.obtener_parametros_familia()` |
| Cambiar tipo de familia a elemento | `lib_familias.activar_tipo_familia()` |

### 4. Agrupación de elementos

| Sección | Función / módulo |
|---|---|
| 4.1 Grupos — Obtener | `lib_general.obtener_grupos()` |
| 4.1 Grupos — Crear (Group.Create) | `lib_general.crear_grupo()` |
| 4.1 Grupos — Desagrupar | `lib_general.desagrupar()` |
| 4.1 Grupos — Obtener miembros | `lib_general.obtener_miembros_grupo()` |
| 4.2 Montajes — Crear (Assembly.Create) | `lib_general.crear_ensamblaje()` |
| 4.2 Montajes — Obtener miembros | `lib_general.obtener_miembros_ensamblaje()` |

### 5. Masas y emplazamiento

| Sección | Función / módulo |
|---|---|
| Masas conceptuales | *(no implementado — candidato a lib_geometria.py DirectShape)* |
| Topografía (TopographySurface) | *(no implementado — candidato a lib_general.py)* |
| Subregiones de topografía | *(no implementado — candidato a lib_general.py)* |

### 6. Exportar y gestionar familias

| Sección | Función / módulo |
|---|---|
| Exportar familia individual | `lib_familias.exportar_familia()` |
| Exportar todas las familias | `lib_familias.exportar_todas_las_familias()` |
| Eliminar familias no usadas | `lib_familias.eliminar_familias_no_usadas()` |

---

## ix. REVIT API - MATERIALES (p.405)

### 1. Gestión de materiales

| Sección | Función / módulo |
|---|---|
| 1.1 Crear material (Material.Create) | *(no implementado — candidato a lib_materiales.py)* |
| 1.2 Parámetros de usuario (Material.LookupParameter) | `lib_general.obtener_valor_parametro(elem, "Material")` |
| 1.3 Parámetros de Identidad (nombre, clase, descripción) | `lib_general.obtener_valor_parametro(elem, nombre)` |
| 1.4 Pestaña Gráficos (color superficial, cortado, patrón) | *(no implementado — candidato a lib_materiales.py)* |
| 1.5 Pestaña Aspecto (AppearanceAsset, AssetProperty) | *(no implementado — candidato a lib_materiales.py)* |
| 1.6 Pestaña Física — Hormigón | *(no implementado — candidato a lib_materiales.py)* |
| 1.6 Pestaña Física — Acero | *(no implementado — candidato a lib_materiales.py)* |
| 1.6 Pestaña Física — Madera | *(no implementado — candidato a lib_materiales.py)* |
| 1.7 Pestaña Térmica | *(no implementado — candidato a lib_materiales.py)* |
| 1.8 Aplicar propiedades a elementos | `lib_estructura.obtener_material_estructura()`, `lib_estructura.obtener_materiales_usados()` |

### 2. Consultas de materiales

| Sección | Función / módulo |
|---|---|
| Materiales usados en estructura | `lib_estructura.obtener_materiales_usados()` |
| Volumen de material (hormigón) | `lib_estructura.calcular_volumen_hormigon()` |
| Área por material en elementos compuestos | *(no implementado — candidato a lib_materiales.py)* |

> **Nota:** La gestión avanzada de materiales no tiene módulo dedicado actualmente.
> Se recomienda crear `lib_materiales.py` con las funciones indicadas como candidatas.

---

## x. REVIT API - ELEMENTOS ESPACIALES (p.429)

### 1. Conceptos de elementos espaciales

| Sección | Función / módulo |
|---|---|
| Room vs Space vs Area | *(conceptual — ver libro p.429)* |
| SpatialElement — clase base | `lib_arquitectura.obtener_habitaciones()` |

### 2. Habitaciones (Rooms)

| Sección | Función / módulo |
|---|---|
| Crear habitaciones | *(no implementado — se crea manualmente en Revit)* |
| Propiedades — nombre, número | `lib_arquitectura.obtener_nombre_habitacion()`, `lib_arquitectura.obtener_numero_habitacion()` |
| Propiedades — área | `lib_arquitectura.obtener_area_habitacion()` |
| Propiedades — centroide | `lib_arquitectura.obtener_centroide_habitacion()` |
| Contorno de habitación (CurveLoop) | `lib_arquitectura.obtener_contorno_habitacion()`, `lib_arquitectura.obtener_curveloops_habitacion()` |
| Elementos dentro de habitación | `lib_arquitectura.obtener_elementos_en_habitacion()` |
| Delimitadores de habitación | `lib_arquitectura.obtener_contorno_habitacion()` |
| Filtrar habitaciones | `lib_arquitectura.obtener_habitaciones()`, `lib_arquitectura.obtener_habitaciones_por_nivel()` |
| Propiedades FromRoom / ToRoom (puertas) | `lib_arquitectura.obtener_puertas_de_habitacion()` |
| Calcular volumen habitación | `lib_arquitectura.calcular_volumen_habitacion()` |
| QA — sin número / duplicadas | `lib_arquitectura.detectar_habitaciones_sin_numero()`, `lib_arquitectura.detectar_habitaciones_duplicadas()` |
| QA — estado de habitaciones | `lib_arquitectura.clasificar_habitaciones_por_estado()` |
| Renumerar habitaciones por nivel | `lib_arquitectura.renumerar_habitaciones_por_nivel()` |
| Agrupar por nivel | `lib_arquitectura.agrupar_habitaciones_por_nivel()` |
| Ratio acristalamiento | `lib_arquitectura.calcular_ratio_acristalamiento()` |

### 2.1 Áreas (Areas)

| Sección | Función / módulo |
|---|---|
| Crear delimitadores de áreas | `lib_arquitectura.crear_separacion_de_area()` |
| Filtrar planos de área | *(no implementado — candidato a lib_arquitectura.py)* |

### 3. Espacios MEP (Spaces)

| Sección | Función / módulo |
|---|---|
| Crear espacio MEP | *(no implementado — candidato a lib_instalaciones.py)* |
| Propiedades MEP de espacio (caudal, carga térmica) | *(no implementado — candidato a lib_instalaciones.py)* |
| Acceso a espacio desde elemento MEP | *(no implementado — candidato a lib_instalaciones.py)* |

### 3.1 Zonas climáticas (Zones)

| Sección | Función / módulo |
|---|---|
| Crear zonas climáticas (HVAC Zones) | *(no implementado — candidato a lib_instalaciones.py)* |
| Añadir espacios a zonas | *(no implementado — candidato a lib_instalaciones.py)* |
| Propiedades de zona (setpoints) | *(no implementado — candidato a lib_instalaciones.py)* |

### 4. Circuitos de muros (PlanTopology)

| Sección | Función / módulo |
|---|---|
| Elementos que delimitan habitación | `lib_arquitectura.obtener_contorno_habitacion()` |
| Acceso a geometría de elementos espaciales | `lib_arquitectura.obtener_curveloops_habitacion()`, `lib_arquitectura.calcular_volumen_habitacion()` |

### 5. Recorridos de escape (Path of Travel)

| Sección | Función / módulo |
|---|---|
| Crear PathOfTravel | *(no implementado — candidato a lib_geometria.py A*)* |
| A* — pathfinding en planta | `lib_geometria.encontrar_camino_astar()` |
| Analizar distancias de evacuación | *(no implementado — candidato a lib_geometria.py)* |

---

## xi. REVIT API - INSTALACIONES (p.465)

### 1. Conceptos MEP en Revit

| Sección | Función / módulo |
|---|---|
| Disciplinas MEP (Mechanical/Electrical/Plumbing) | *(conceptual — ver libro p.465)* |
| Categorías MEP principales | Base de filtros en `lib_instalaciones.py` |

### 2. Configuraciones del sistema

| Sección | Función / módulo |
|---|---|
| Configuraciones mecánicas (duct/pipe settings) | *(no implementado — candidato a lib_instalaciones.py)* |
| Configuraciones de tuberías | *(no implementado — candidato a lib_instalaciones.py)* |
| Configuraciones eléctricas | *(no implementado — candidato a lib_instalaciones.py)* |

### 3. Enrutamiento de sistemas

| Sección | Función / módulo |
|---|---|
| Enrutamiento de tuberías (RoutingPreferenceManager) | *(no implementado — candidato a lib_instalaciones.py)* |
| Enrutamiento de conductos | *(no implementado — candidato a lib_instalaciones.py)* |
| Enrutamiento de bandejas cable | `lib_instalaciones.crear_bandeja_cable()` |

### 4. Conectores en familias MEP

| Sección | Función / módulo |
|---|---|
| ConnectorElement — obtener conectores | *(no implementado — candidato a lib_instalaciones.py)* |
| Propiedades del conector (flujo, presión, diámetro) | *(no implementado — candidato a lib_instalaciones.py)* |
| Conectar elementos por conectores | *(no implementado — candidato a lib_instalaciones.py)* |

### 4.1 Gestor de conectores

| Sección | Función / módulo |
|---|---|
| ConnectorManager — acceso | *(no implementado — candidato a lib_instalaciones.py)* |
| Iterar conectores de un elemento | *(no implementado — candidato a lib_instalaciones.py)* |

### 5. Sistemas lógicos

| Sección | Función / módulo |
|---|---|
| Crear sistema mecánico (MechanicalSystem) | *(no implementado — candidato a lib_instalaciones.py)* |
| Crear sistema de tuberías (PipingSystem) | *(no implementado — candidato a lib_instalaciones.py)* |
| Crear sistema eléctrico (ElectricalSystem) | *(no implementado — candidato a lib_instalaciones.py)* |
| Obtener sistema de tubería de elemento | `lib_instalaciones.obtener_sistema_tuberia()` |
| Agrupar tuberías por sistema | `lib_instalaciones.agrupar_tuberias_por_sistema()` |
| Agrupar conductos por sistema | `lib_instalaciones.agrupar_conductos_por_sistema()` |

### 6. Mecánica (Conductos)

| Sección | Función / módulo |
|---|---|
| Crear conducto (Duct.Create) | *(no implementado — candidato a lib_instalaciones.py)* |
| Crear accesorios de conducto | *(no implementado — candidato a lib_instalaciones.py)* |
| Crear trazado de conductos | *(no implementado — candidato a lib_instalaciones.py)* |
| Longitud de conductos | `lib_instalaciones.obtener_longitud_conducto()` |
| Longitud total de conductos | `lib_instalaciones.obtener_longitud_total_conductos()` |
| Agrupar conductos por sistema | `lib_instalaciones.agrupar_conductos_por_sistema()` |
| DataFrame de conductos | `lib_instalaciones.dataframe_conductos()` |

### 7. Electricidad (Circuitos y Paneles)

| Sección | Función / módulo |
|---|---|
| Crear circuito eléctrico | *(no implementado — candidato a lib_instalaciones.py)* |
| Añadir elementos al circuito | *(no implementado — candidato a lib_instalaciones.py)* |
| Paneles de distribución | *(no implementado — candidato a lib_instalaciones.py)* |
| Bandejas de cable (CableTray) | `lib_instalaciones.crear_bandeja_cable()` |
| Conduits — propiedades | `lib_instalaciones.obtener_conduits()` |

### 8. Fontanería (Tuberías)

| Sección | Función / módulo |
|---|---|
| Crear tubería (Pipe.Create) | *(no implementado — candidato a lib_instalaciones.py)* |
| Crear trazados de tuberías | *(no implementado — candidato a lib_instalaciones.py)* |
| Marcadores de rotura de tubería | *(no implementado — candidato a lib_instalaciones.py)* |
| Longitud de tuberías | `lib_instalaciones.obtener_longitud_tuberia()` |
| Diámetro exterior | `lib_instalaciones.obtener_diametro_exterior_tuberia()` |
| Longitud total de tuberías | `lib_instalaciones.obtener_longitud_total_tuberias()` |
| Agrupar por sistema | `lib_instalaciones.agrupar_tuberias_por_sistema()` |
| DataFrame de tuberías | `lib_instalaciones.dataframe_tuberias()` |

### 9. Intersección de referencias con rayos

| Sección | Función / módulo |
|---|---|
| ReferenceIntersector — crear | *(no implementado — candidato a lib_geometria.py)* |
| Lanzar rayo desde punto | *(no implementado — candidato a lib_geometria.py)* |
| Detectar intersecciones de rayo | *(no implementado — candidato a lib_geometria.py)* |

### 10. Advertencias MEP

| Sección | Función / módulo |
|---|---|
| Obtener advertencias del modelo | `lib_coordinacion.analizar_advertencias_por_tipo()` |
| Exportar advertencias a CSV | `lib_coordinacion.exportar_advertencias_a_csv()` |

---

## xii. REVIT API - ESTRUCTURAS (p.539)

### 1. Conceptos estructura en Revit

| Sección | Función / módulo |
|---|---|
| Categorías estructurales principales | Base de filtros en `lib_estructura.py` |
| StructuralType, StructuralRole | `lib_estructura.crear_pilar_vertical()`, `lib_estructura.crear_viga()` |

### 2. Configuraciones estructurales

| Sección | Función / módulo |
|---|---|
| Modelo analítico (AnalyticalModel) | *(no implementado — candidato a lib_estructura.py)* |
| Condiciones de contorno (BoundaryConditions) | *(no implementado — candidato a lib_estructura.py)* |
| Representación simbólica | *(no implementado — candidato a lib_estructura.py)* |
| Casos de carga (LoadCase) | *(no implementado — candidato a lib_estructura.py)* |
| Combinaciones de carga (LoadCombination) | *(no implementado — candidato a lib_estructura.py)* |
| Conexiones estructurales | *(no implementado — candidato a lib_estructura.py)* |

### 3. Familias cargables estructurales

| Sección | Función / módulo |
|---|---|
| 3.1 Vigas — Crear (FamilyInstance beam) | `lib_estructura.crear_viga()` |
| 3.1 Vigas — propiedades geométricas | `lib_estructura.obtener_longitud_viga()`, `lib_estructura.obtener_propiedades_viga()` |
| 3.1 Vigas — material | `lib_estructura.obtener_material_estructura()` |
| 3.1 Vigas por nivel | `lib_estructura.obtener_vigas_por_nivel()`, `lib_estructura.agrupar_vigas_por_nivel()` |
| 3.2 Tornapuntas (Braces) — crear | *(no implementado — candidato a lib_estructura.py)* |
| 3.2 Tornapuntas — propiedades | *(no implementado — candidato a lib_estructura.py)* |
| 3.3 Vigas celosía (Truss) — crear | *(no implementado — candidato a lib_estructura.py)* |
| 3.3 Vigas celosía — miembros | *(no implementado — candidato a lib_estructura.py)* |
| 3.4 Pilares — Crear vertical | `lib_estructura.crear_pilar_vertical()` |
| 3.4 Pilares — Crear inclinado | `lib_estructura.crear_pilar_inclinado()` |
| 3.4 Pilares — propiedades geométricas | `lib_estructura.obtener_altura_pilar()`, `lib_estructura.obtener_nivel_base_pilar()`, `lib_estructura.obtener_nivel_alto_pilar()` |
| 3.4 Pilares — propiedades analíticas | *(no implementado — candidato a lib_estructura.py)* |
| 3.4 Pilares — enlaces analíticos | *(no implementado — candidato a lib_estructura.py)* |
| 3.4 Pilares por nivel | `lib_estructura.obtener_pilares_por_nivel()` |
| 3.5 Cimentaciones (Foundation) | *(no implementado — candidato a lib_estructura.py)* |
| 3.5 Cimentaciones corridas (Wall Foundation) | *(no implementado — candidato a lib_estructura.py)* |
| 3.5 Losas de cimentación | *(no implementado — candidato a lib_estructura.py)* |

### 4. Familias de sistema estructurales

| Sección | Función / módulo |
|---|---|
| Forjados — Área | `lib_estructura.obtener_area_forjado()`, `lib_estructura.obtener_area_total_forjados()` |
| Forjados — Crear (Floor structural) | `lib_arquitectura.crear_suelo()` (con StructuralFloorType) |
| Materiales usados | `lib_estructura.obtener_materiales_usados()` |
| Volumen de hormigón | `lib_estructura.calcular_volumen_hormigon()` |

### 5. Huecos estructurales

| Sección | Función / módulo |
|---|---|
| Huecos en suelos/forjados | `lib_arquitectura.crear_abertura_suelo()` |
| Huecos en muros (Opening) | *(no implementado — candidato a lib_arquitectura.py)* |

### 6. Cargas estructurales

| Sección | Función / módulo |
|---|---|
| 6.1 Cargas puntuales libres | `lib_estructura.crear_carga_puntual()` |
| 6.2 Cargas lineales libres | `lib_estructura.crear_carga_lineal()` |
| 6.3 Cargas superficiales | `lib_estructura.crear_carga_superficial()` |
| 6.4 Cargas sísmicas | *(no implementado — candidato a lib_estructura.py)* |

### 7. Armaduras (Rebar)

| Sección | Función / módulo |
|---|---|
| Recubrimientos (RebarCoverType) | `lib_estructura.obtener_recubrimientos()` |
| Crear armadura (Rebar.Create) | `lib_estructura.crear_armadura()` |
| Tipos de barras (RebarBarType) | `lib_estructura.crear_armadura()` (tipo_barra_id) |
| Distribución fija (número fijo) | `lib_estructura.distribuir_armadura_numero_fijo()` |
| Distribución separación máxima | `lib_estructura.distribuir_armadura_separacion_maxima()` |
| Distribución separación mínima | `lib_estructura.distribuir_armadura_separacion_minima()` |
| Representación sólida en vista | `lib_estructura.establecer_armadura_solida_en_vista()` |
| Obtener armaduras de elemento | `lib_estructura.obtener_armaduras_de_elemento()` |
| 7.2 Armados por área (RebarInSystem) | `lib_estructura.crear_armado_por_area()` |
| 7.3 Armados por camino (Path Rebar) | *(no implementado — candidato a lib_estructura.py)* |
| 7.5 Propagación de armados | *(no implementado — candidato a lib_estructura.py)* |

### 8. Acero y Prefabricado

| Sección | Función / módulo |
|---|---|
| Acero estructural (Steel Connections API) | *(no implementado — requiere Advance Steel)* |
| Prefabricado (Precast API) | *(no implementado — requiere extensión Precast)* |

---

## xiii. REVIT API – TRABAJO COLABORATIVO (p.607)

### 1. Archivos centrales (Worksharing)

| Sección | Función / módulo |
|---|---|
| Activar el modelo compartido | `lib_colaborativo.activar_worksharing()` |
| Guardar archivo como central | `lib_colaborativo.guardar_como_central()` |
| Sincronizar con central (SWC) | `lib_colaborativo.sincronizar_con_central()` |
| 1.2 Guardar en BIM360 / Autodesk Docs | *(no implementado — requiere Cloud Worksharing API)* |
| 1.4 Abrir archivo colaborativo local | `lib_colaborativo.abrir_documento()` |
| 1.4 Abrir desde BIM360 | *(no implementado — requiere Cloud Worksharing API)* |
| 1.5 Procesamiento por lotes de archivos | *(no implementado — candidato a lib_colaborativo.py)* |
| 1.6 Visibilidad en colaborativo | *(no implementado — candidato a lib_colaborativo.py)* |
| 1.7 Utilidades de trabajo colaborativo | `lib_colaborativo.activar_worksharing()`, `lib_colaborativo.sincronizar_con_central()` |
| 1.8 Subproyectos (Worksets) — Crear | `lib_colaborativo.crear_workset()` |
| 1.8 Worksets — Obtener | `lib_colaborativo.obtener_worksets()` |
| 1.8 Worksets — Asignar a elemento | `lib_colaborativo.asignar_workset_a_elemento()` |
| 1.8 Worksets — Asignar masivo | `lib_colaborativo.asignar_workset_a_lista()` |
| 1.8 Worksets — Obtener de elemento | `lib_colaborativo.obtener_workset_de_elemento()` |
| QA — Elementos sin workset correcto | `lib_coordinacion.detectar_elementos_sin_workset()` |
| Asignar workset por categoría | `lib_coordinacion.asignar_workset_por_categoria()` |
| Visibilidad de workset en vista | `lib_coordinacion.establecer_visibilidad_workset()` |

### 2. Archivos locales

| Sección | Función / módulo |
|---|---|
| Crear copia local | *(no implementado — candidato a lib_colaborativo.py)* |
| Guardar copia local | *(no implementado — candidato a lib_colaborativo.py)* |

### 3. Fases (Phases)

| Sección | Función / módulo |
|---|---|
| Obtener fases del proyecto | *(no implementado — candidato a lib_coordinacion.py)* |
| Crear fase | *(no implementado — candidato a lib_coordinacion.py)* |
| Filtrar elementos por fase | `lib_general.obtener_valor_parametro(elem, "Phase Created")` |
| Asignar fase a elemento | *(no implementado — candidato a lib_coordinacion.py)* |
| Comparar documentos Revit 2023 | `lib_transacciones.comparar_documentos()` |

### 4. Vínculos de Revit

| Sección | Función / módulo |
|---|---|
| 4.1 Búsqueda de elementos en vínculos | `lib_coordinacion.obtener_elementos_en_link()`, `lib_coordinacion.obtener_elemento_en_link_por_unique_id()` |
| 4.1 Filtrar en link por parámetro | `lib_coordinacion.filtrar_en_link_por_parametro()` |
| 4.1 Filtrar en link por BoundingBox | `lib_coordinacion.filtrar_en_link_por_boundingbox()`, `lib_coordinacion.filtrar_en_link_dentro_de_bbox()`, `lib_coordinacion.filtrar_en_link_contiene_punto()` |
| 4.2 Tipos de vínculos — añadir vínculo | *(no implementado — candidato a lib_coordinacion.py)* |
| 4.2 Tipos de vínculos — recargar | *(no implementado — candidato a lib_coordinacion.py)* |
| 4.2 Tipos de vínculos — descargar | *(no implementado — candidato a lib_coordinacion.py)* |
| 4.3 Adquirir coordenadas de link | `lib_coordinacion.adquirir_coordenadas_de_link()` |
| 4.3 Instancias de vínculos (RevitLinkInstance) | `lib_coordinacion.obtener_elementos_en_link()` |
| 4.4 Transform de vínculo (GetTotalTransform) | `link_inst.GetTotalTransform()` — ver **workflow completo en cap. v.10** |
| 4.4 Clase Transform — todas las operaciones | Ver **cap. v.10** — `lib_transformaciones.crear_transform_traslacion/rotacion/por_ejes`, `transformar_punto`, `invertir_transform`, `combinar_transforms` |
| 4.5 Copiar elementos desde link | `lib_coordinacion.copiar_elementos_desde_link()` |
| 4.5 Copiar entre documentos con Transform | `lib_transformaciones.copiar_elementos_entre_documentos(doc_link, ids, doc, tf)` |
| 4.5 Mover elementos (vector o punto absoluto) | Ver **cap. v.3** — `lib_transformaciones.mover_elemento/mover_elemento_m/mover_elementos/alinear_a_punto` |
| 4.5 Copiar elementos (vector o nivel) | Ver **cap. v.4** — `lib_transformaciones.copiar_elemento/copiar_elementos/copiar_elemento_a_nivel` |
| 4.5 Rotar elementos | Ver **cap. v.5** — `lib_transformaciones.rotar_elemento/rotar_elemento_en_propio_punto/rotar_elementos` |
| 4.5 Simetría (Mirror) | Ver **cap. v.6** — `lib_transformaciones.espejar_elemento/espejar_elementos` |
| 4.5 Voltear cara/mano/extremos | Ver **cap. v.7** — `lib_transformaciones.voltear_cara/voltear_mano/voltear_extremos_viga` |
| 4.7 Archivos AutoCAD — clasificar links | `lib_cad.clasificar_links_cad()` |
| 4.7 AutoCAD — obtener capas | `lib_cad.obtener_nombres_capas_cad()` |
| 4.7 AutoCAD — curvas por capa | `lib_cad.obtener_curvas_por_capa()` |
| 4.7 AutoCAD — eliminar links | `lib_cad.eliminar_link_cad()`, `lib_cad.eliminar_todos_links_cad()` |
| 4.7 AutoCAD — desanclar link CAD | `lib_cad.desanclar_link_cad()` |
| 4.8 Importar otros modelos (IFC, SKP…) | *(no implementado — candidato a lib_bases_datos.py)* |
| 4.9 Exportar a Navisworks | *(no implementado — candidato a lib_bases_datos.py)* |
| 4.9 Exportar a PDF | *(no implementado — candidato a lib_vistas.py)* |
| 4.9 Exportar IFC | `lib_bases_datos.exportar_ifc()` |

---

## xiv. INTERFAZ DE USUARIO (p.659)

### 1. Selección desde la interfaz de usuario

| Sección | Función / módulo |
|---|---|
| 1.1 Seleccionar elemento único | `lib_seleccion_ui.seleccionar_elemento()` |
| 1.1 Seleccionar múltiples elementos | `lib_seleccion_ui.seleccionar_multiples()` |
| 1.1 Seleccionar mediante rectángulo | `lib_seleccion_ui.seleccionar_rectangulo()` |
| 1.1 Seleccionar cara | `lib_seleccion_ui.seleccionar_cara()` |
| 1.1 Seleccionar arista | `lib_seleccion_ui.seleccionar_arista()` |
| 1.1 Seleccionar punto | `lib_seleccion_ui.seleccionar_punto()` |
| 1.1 Seleccionar elemento en link | `lib_seleccion_ui.seleccionar_elemento_en_link()` |
| 1.1 Obtener selección actual | `lib_seleccion_ui.obtener_seleccion_actual()` |
| 1.1 Establecer selección | `lib_seleccion_ui.establecer_seleccion()` |

### 2. Ventanas emergentes (TaskDialogs)

| Sección | Función / módulo |
|---|---|
| Crear ventana emergente (TaskDialog) | `lib_ui.mensaje()` |
| Confirmación Sí/No | `lib_ui.confirmar()` |
| Confirmación con cancelar | `lib_ui.confirmar_cancelar()` |
| Barra de progreso | `lib_ui.con_progreso()` |
| Solicitar texto al usuario | `lib_ui.pedir_texto()` |
| Solicitar número al usuario | `lib_ui.pedir_numero()` |

### 3. Formularios de Windows (WPF / Windows Forms)

| Sección | Función / módulo |
|---|---|
| Crear formulario / ventana WPF | `lib_ui.formulario()` |
| Mostrar lista de elementos | `lib_ui.mostrar_lista()` |
| Mostrar tabla de datos | `lib_ui.mostrar_tabla()` |
| Seleccionar opción (ComboBox/RadioButton) | `lib_ui.seleccionar_opcion()` |
| Selección múltiple (CheckBox) | `lib_ui.seleccionar_multiples()` |
| Diálogo de archivo (OpenFileDialog) | `lib_ui.pedir_archivo()`, `lib_ui.pedir_archivos_multiples()` |
| Diálogo guardar (SaveFileDialog) | `lib_ui.pedir_ruta_guardar()` |
| Diálogo de carpeta | `lib_ui.pedir_carpeta()` |
| Seleccionar niveles | `lib_ui.seleccionar_niveles()` |
| Seleccionar categorías | `lib_ui.seleccionar_categorias()` |
| Seleccionar parámetros | `lib_ui.seleccionar_parametros()` |

---

## xv. GLOSARIO (p.679)

| Término | Referencia en la biblioteca |
|---|---|
| AddIn / Plugin | *(conceptual — ver README.md)* |
| API (Application Programming Interface) | *(conceptual — fundamento Revit API)* |
| BIM (Building Information Modeling) | *(conceptual — contexto del proyecto)* |
| BoundingBox | `lib_general.filtrar_por_boundingbox()`, `lib_general.filtrar_dentro_de_bbox()` |
| BuiltInCategory (BIC) | Usado en todos los colectores de la biblioteca |
| BuiltInParameter (BIP) | `lib_general.obtener_valor_parametro()` |
| clr (Common Language Runtime) | Cabecera de importación en todos los módulos |
| CurveLoop | `lib_geometria.crear_curveloop_desde_curvas()`, `lib_arquitectura.obtener_curveloops_habitacion()` |
| DirectShape | `lib_geometria.crear_directshape_desde_solido()` |
| Document / UIDocument | `lib_colaborativo.abrir_documento()`, `lib_colaborativo.cerrar_documento()` |
| DSOffice (Dynamo) | `lib_excel.leer_excel_dsoffice()`, `lib_excel.escribir_excel_dsoffice()` |
| ElementId | `lib_general.id_a_int()`, `lib_general.obtener_ids_int()` |
| ExtensibleStorage | `lib_bases_datos.guardar_configuracion()` |
| FamilyInstance / FamilySymbol | `lib_familias.colocar_instancia_familia()`, `lib_familias.obtener_tipos_de_familia()` |
| FilteredElementCollector (FEC) | Base de todos los colectores de la biblioteca |
| GUID / UniqueId | `lib_bases_datos.obtener_guid_elemento()` |
| IFC (Industry Foundation Classes) | `lib_bases_datos.exportar_ifc()` |
| IronPython 2.7 | Stack tecnológico de toda la biblioteca |
| LookupParameter | `lib_general.obtener_valor_parametro()` |
| MEP (Mechanical, Electrical, Plumbing) | `lib_instalaciones.py` |
| OverrideGraphicSettings (OGS) | `lib_vistas.sobreescribir_grafico_elemento()` |
| Revit API | Toda la biblioteca |
| SectionBox | `lib_vistas.crear_vista_3d_por_bbox()`, `lib_vistas.obtener_section_box_3d()` |
| Solid (sólido geométrico) | `lib_geometria.booleano_interseccion()`, `lib_geometria.booleano_union()`, `lib_geometria.booleano_diferencia()` |
| Transaction / TransactionGroup | `lib_transacciones.transaccion_nativa()`, `lib_transacciones.ejecutar_en_grupo()` |
| Transform (transformación espacial) | `lib_transformaciones.crear_transform_traslacion()`, `lib_transformaciones.crear_transform_rotacion()` |
| UniqueId | `lib_bases_datos.obtener_guid_elemento()` |
| Unwrap / UnwrapElement | `lib_general.unwrap()`, `lib_general.unwrap_lista()` |
| Workset / Worksharing | `lib_colaborativo.crear_workset()`, `lib_colaborativo.asignar_workset_a_elemento()` |
| XYZ (punto/vector) | `lib_geometria.crear_linea()`, `lib_transformaciones.transformar_punto()` |

---

## Resumen de cobertura por módulo

| Módulo | Capítulos cubiertos | Funciones principales |
|---|---|---|
| `lib_general.py` | ii, iii, iv, v, vi | unwrap, filtros, parámetros, unidades, ejes, planos referencia |
| `lib_transformaciones.py` | iii, xiii | move, copy, rotate, mirror, flip, Transform |
| `lib_coordinacion.py` | iv, vii, xiii | niveles, worksets, links, colisiones, advertencias, CSV |
| `lib_arquitectura.py` | ii, viii, x | habitaciones, muros, suelos, áreas, puertas, ventanas |
| `lib_instalaciones.py` | xi | conductos, tuberías, bandejas, conduits, MEP |
| `lib_estructura.py` | ix, xii | pilares, vigas, forjados, armaduras, materiales, cargas |
| `lib_geometria.py` | iii, viii, x | curvas, CurveLoop, sólidos, booleans, DirectShape, A* |
| `lib_vistas.py` | vii | vistas 3D/planta/sección/alzado, planos, filtros, tablas |
| `lib_familias.py` | vi, viii | cargar, exportar, colocar, gestionar familias |
| `lib_cad.py` | xiii | análisis de links CAD (capas, curvas, bloques) |
| `lib_excel.py` | ii, vi | DSOffice + COM Interop + pandas read/write Excel |
| `lib_bases_datos.py` | ii, vi, xiii | JSON, CSV, IFC export, schedules, GUIDs |
| `lib_colaborativo.py` | xiii | worksharing, worksets, BIM360 parcial |
| `lib_transacciones.py` | v | Transaction, TransactionGroup, SubTransaction |
| `lib_seleccion_ui.py` | xiv | selección interactiva (elemento, cara, arista, punto) |
| `lib_scientific.py` | ii | pandas, numpy, scipy, matplotlib, shapely, networkx |
| `lib_ui.py` | xiv | WPF: texto, número, opciones, archivos, progreso, tabla |

---

## Secciones sin cobertura actual (candidatos a nuevos módulos)

| Sección | Descripción | Módulo sugerido |
|---|---|---|
| vi.3 Parámetros globales | Crear y enlazar parámetros globales | `lib_general.py` ampliar |
| vi.4 Parámetros de grupo | Grupos de parámetros BuiltIn | `lib_general.py` ampliar |
| vi.6.1 Crear parámetro compartido | Definición + Binding + TXT | `lib_general.py` ampliar |
| vi.8.1 Fórmulas de parámetros | Asignar/leer fórmulas | `lib_familias.py` ampliar |
| vii.2.2 Esquemas y leyendas de color | ColorFillScheme, ColorFillLegend | `lib_vistas.py` ampliar |
| vii.7 Leyendas y navegador | Legend views, browser organizer | `lib_vistas.py` ampliar |
| viii.2.1 Muros cortina | CurtainGrid, Mullion, CurtainPanel | `lib_arquitectura.py` ampliar |
| viii.2.4-2.7 Piezas, barandillas, techos, escaleras | Parts, Railing, Roof, Stair API | `lib_arquitectura.py` ampliar |
| viii.5 Masas y topografía | Mass, TopographySurface | `lib_geometria.py` ampliar |
| ix. Materiales completo | Crear, Gráficos, Aspecto, Físico, Térmico | `lib_materiales.py` nuevo |
| x.3 Espacios MEP | Space, HVAC Zones, Path of Travel | `lib_instalaciones.py` ampliar |
| xi.3 Enrutamiento MEP | RoutingPreferenceManager para tuberías/conductos | `lib_instalaciones.py` ampliar |
| xi.4 Conectores | ConnectorElement, ConnectorManager | `lib_instalaciones.py` ampliar |
| xi.5 Sistemas lógicos | MechanicalSystem, PipingSystem, ElectricalSystem | `lib_instalaciones.py` ampliar |
| xi.7 Circuitos eléctricos | ElectricalSystem, paneles, cableado | `lib_instalaciones.py` ampliar |
| xi.9 Intersección de rayos | ReferenceIntersector | `lib_geometria.py` ampliar |
| xii.2 Config. estructurales | AnalyticalModel, BoundaryConditions, LoadCase | `lib_estructura.py` ampliar |
| xii.3.2 Tornapuntas | Braces estructurales | `lib_estructura.py` ampliar |
| xii.3.3 Vigas celosía | Truss API | `lib_estructura.py` ampliar |
| xii.3.5 Cimentaciones | Foundation, WallFoundation | `lib_estructura.py` ampliar |
| xii.7.3 Armados por camino | Path Rebar | `lib_estructura.py` ampliar |
| xii.7.5 Propagación armados | Rebar propagation | `lib_estructura.py` ampliar |
| xii.8 Acero y prefabricado | Steel Connections, Precast API | `lib_estructura.py` ampliar |
| xiii.2 Archivos locales | Crear/guardar copia local | `lib_colaborativo.py` ampliar |
| xiii.3 Fases | Crear, combinar, filtrar fases | `lib_coordinacion.py` ampliar |
| xiii.1.2/1.4 BIM360 | Cloud Worksharing API | `lib_colaborativo.py` ampliar |

---

*Generado 2026-05-28 — actualizar al añadir nuevas funciones a la biblioteca.*
