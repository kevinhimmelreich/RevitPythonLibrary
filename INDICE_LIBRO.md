# Índice del libro → RevitPythonLibrary

Referencia cruzada entre los capítulos de **"Más allá de Dynamo / Revit 2023"**
y las funciones de la biblioteca.  
Formato: `modulo.funcion()` enlazado al archivo correspondiente.

---

## i. INTRODUCCIÓN A LA PROGRAMACIÓN (p.37)

| Sección del libro | Función / módulo relacionado |
|---|---|
| Evolución natural (Dynamo → Python) | Contexto general — ver `README.md` |
| Dynamo | Patrón base de todos los módulos: `DocumentManager`, `TransactionManager` |
| DesignScript | No aplica (DesignScript es nativo de Dynamo) |

---

## ii. PYTHON (p.43)

### 4. Tipos básicos de datos

| Sección | Función / módulo |
|---|---|
| 4.2 Textos — RegEx | `lib_arquitectura.clasificar_habitaciones_por_nombre(habs, regex)` |
| 4.3 Booleanos — isinstance() | Usado internamente en `lib_general.unwrap()`, `lib_general.aplanar_lista()` |

### 8. Conjuntos de datos

| Sección | Función / módulo |
|---|---|
| 8.1 Lista — transponer | `lib_general.aplanar_lista(lista)` |
| 8.4 Diccionarios | `lib_general.obtener_todos_parametros(elem)`, `lib_general.obtener_parametros_tipo(elem)`, `lib_general.agrupar_por_parametro(elems, nombre)` |

### 9. Herramientas de programación funcional

| Sección | Función / módulo |
|---|---|
| filter() | `lib_general.filtrar_por_valor_parametro(cat, nombre, val)` |
| map() | `lib_general.obtener_ids_int(elems)` |

### 11. Bucles

| Sección | Función / módulo |
|---|---|
| 11.3 Comprensión de listas | Usado en `lib_general.agrupar_por_parametro()`, `lib_coordinacion.exportar_parametros_a_csv()` |

### 12. Funciones

| Sección | Función / módulo |
|---|---|
| 12.3 Recursividad — actuar contra lista | `lib_general.aplanar_lista(lista)` |
| 12.3 Crear biblioteca de funciones | Toda la biblioteca `RevitPythonLibrary` |
| 12.4 Funciones built-in | `lib_general.id_a_int()`, `lib_general.iniciar_transaccion()` |
| 12.5 Alcance Local & Global | Patrón de importación en `lib_completa.py` |
| 12.6 Funciones Anónimas — filtrar | `lib_general.filtrar_por_valor_parametro()` |

### 13. Excepciones (Try/Except)

| Sección | Función / módulo |
|---|---|
| Capturar errores de Revit | `lib_transacciones.transaccion_nativa(funcion, nombre)` (rollback automático) |
| Raise an exception | `lib_transacciones.finalizar_transaccion_nativa(tx, confirmar=False)` |

### 18. Otros módulos de Python

| Sección | Función / módulo |
|---|---|
| 18.1 Fechas — datetime | `lib_bases_datos.guardar_configuracion()` (timestamps en JSON) |
| 18.4 Módulo Sistema operativo | `lib_bases_datos.leer_json()`, `lib_bases_datos.escribir_json()`, `lib_bases_datos.leer_csv()`, `lib_bases_datos.escribir_csv()` |

### 19. Bases de datos

| Sección | Función / módulo |
|---|---|
| 19.1 Archivos de texto | `lib_bases_datos.leer_csv()`, `lib_bases_datos.escribir_csv()` |
| 19.2 Bases de datos JSON | `lib_bases_datos.leer_json()`, `lib_bases_datos.escribir_json()`, `lib_bases_datos.exportar_parametros_elementos()`, `lib_bases_datos.importar_parametros_desde_json()` |

### 20. Python 3 / CPython

| Sección | Función / módulo |
|---|---|
| 20.1 Instalar Bibliotecas en CPython 3 | `lib_scientific.instalar_dependencias_scientific()` |
| 20.2 Numpy | `lib_geometria.puntos_a_array_numpy()`, `lib_geometria.calcular_centroide_numpy()`, `lib_geometria.distancias_entre_puntos_numpy()`, `lib_geometria.ajuste_plano_numpy()`, `lib_scientific.xyz_a_numpy()`, `lib_scientific.numpy_a_xyz()` |
| 20.3 Pandas | `lib_scientific.elementos_a_dataframe()`, `lib_scientific.dataframe_a_parametros()`, `lib_scientific.schedule_a_dataframe()`, `lib_excel.leer_excel_pandas()`, `lib_excel.escribir_excel_pandas()`, `lib_arquitectura.dataframe_habitaciones()`, `lib_instalaciones.dataframe_tuberias()`, `lib_instalaciones.dataframe_conductos()` |

---

## iii. REVIT API - INTRODUCCIÓN (p.145)

| Sección | Función / módulo |
|---|---|
| 4.2 Plantilla de Python Script | Patrón de todos los módulos: `import clr` → `AddReference` → `DocumentManager` |
| 6. Diferencias Document / UIDocument / Application | `lib_colaborativo.abrir_documento()`, `lib_colaborativo.cerrar_documento()` |
| 7. Desenvolviendo elementos de Revit | `lib_general.unwrap(elem)`, `lib_general.unwrap_lista(elems)` |
| 8. Métodos de conversión de geometría | `lib_transformaciones.*`, `lib_geometria.*` |
| 8.2 Puntos | `lib_geometria.crear_linea()`, `lib_transformaciones.transformar_punto()` |
| 8.2 Vectores | `lib_transformaciones.vector_entre_puntos()`, `lib_transformaciones.transformar_vector()` |
| 8.2 Líneas / Curvas | `lib_geometria.crear_linea()`, `lib_geometria.crear_arco()`, `lib_geometria.crear_nurbs_por_puntos()` |
| 8.3 De Revit a Dynamo | `lib_general.unwrap()` (inverso: elementos nativos) |
| 8.3 De Dynamo a Revit | `lib_general.unwrap()` |

---

## iv. REVIT API - COLECCIONAR ELEMENTOS (p.167)

### 1. Coleccionando elementos de Revit

| Sección | Función / módulo |
|---|---|
| 1.1 Buscar en todo el documento | Base de `lib_general.filtrar_por_valor_parametro()`, `lib_arquitectura.obtener_habitaciones()`, `lib_estructura.obtener_pilares_por_nivel()` |
| 1.2 Buscar en vista específica | `lib_vistas.obtener_elementos_visibles_en_vista()`, `lib_general.obtener_anotaciones_en_vista()` |
| 1.4 Filtros rápidos — Categoría | `lib_general.filtrar_por_valor_parametro(cat_bic, ...)` |
| 1.4 Filtros rápidos — múltiples categorías | `lib_general.obtener_anotaciones_en_vista(vista, cat_bic)` |
| 1.4 Filtros rápidos — BoundingBox intersecta | `lib_general.filtrar_por_boundingbox(bbox, cat_bic, tol)` |
| 1.4 Filtros rápidos — dentro de BoundingBox | `lib_general.filtrar_dentro_de_bbox(bbox, cat_bic, tol)` |
| 1.4 Filtros rápidos — punto dentro de BoundingBox | `lib_general.filtrar_contiene_punto(punto, cat_bic, tol)` |
| 1.4 Filtro Excluyente | `lib_general.excluir_elementos(ids, cat_bic)` |
| 1.4 Concatenación de filtros rápidos | `lib_general.combinar_filtros_y(filtros)`, `lib_general.combinar_filtros_o(filtros)` |
| 1.5 Filtros lentos — valores de parámetros | `lib_general.filtrar_por_valor_parametro(cat, nombre, val)` |
| 1.5 Filtrar habitaciones | `lib_arquitectura.obtener_habitaciones()` |
| 1.5 Filtrar espacios | `lib_instalaciones` (espacios MEP) |
| 1.5 Filtrar áreas | `lib_arquitectura.crear_separacion_de_area()` |
| 1.5 Filtrar elementos que intercepten | `lib_coordinacion.detectar_colisiones_bbox()`, `lib_coordinacion.detectar_colisiones_solidos()` |
| 1.6 Filtros lógicos — LogicalAndFilter | `lib_general.combinar_filtros_y(filtros)` |
| 1.6 Filtros lógicos — LogicalOrFilter | `lib_general.combinar_filtros_o(filtros)` |
| 1.7 Intersección / Unión de elementos | `lib_geometria.booleano_interseccion()`, `lib_geometria.booleano_union()` |
| 1.8 Pandas-Collector | `lib_scientific.elementos_a_dataframe()` |
| 2. Métodos de conversión de elementos | `lib_general.unwrap()`, `lib_general.id_a_int()` |
| 3. Coleccionando Subproyectos | `lib_colaborativo.obtener_worksets()` |

---

## v. REVIT API – MODIFICAR DOCUMENTO (p.201)

| Sección | Función / módulo |
|---|---|
| 1.1 TransactionManager de Dynamo | `lib_general.iniciar_transaccion()`, `lib_general.finalizar_transaccion()` |
| 1.2 Transacciones nativas de Revit | `lib_transacciones.iniciar_transaccion_nativa()`, `lib_transacciones.finalizar_transaccion_nativa()`, `lib_transacciones.transaccion_nativa()` |
| 1.2 Grupos de transacciones | `lib_transacciones.ejecutar_en_grupo()` |
| 1.2 Subtransacciones | `lib_transacciones.ejecutar_subtransaccion()`, `lib_transacciones.eliminar_elemento_en_subtransaccion()` |
| 1.2 Deshacer transacciones | `lib_transacciones.finalizar_transaccion_nativa(tx, confirmar=False)` |
| 1.2 Modificaciones de documento Revit 2023 | `lib_transacciones.comparar_documentos()` |

---

## vi. REVIT API - PARÁMETROS (p.207)

### 2. Parámetros de Familias

| Sección | Función / módulo |
|---|---|
| 2.1 Estructura interna de Familias (Family, FamilyInstance, FamilySymbol, FamilyType) | `lib_familias.obtener_tipos_de_familia()`, `lib_familias.activar_tipo_familia()` |
| 2.2 Acceder a parámetros de familias | `lib_general.obtener_todos_parametros(elem)`, `lib_general.obtener_parametros_tipo(elem)` |
| 2.2 Acceso a parámetro específico | `lib_general.obtener_valor_parametro(elem, nombre)` |
| 2.2 Lectura del valor de un parámetro | `lib_general.obtener_valor_parametro(elem, nombre)` |
| 2.2 Definir valor de parámetro | `lib_general.establecer_valor_parametro(elem, nombre, val)` |
| 2.2 Opciones de formato / FormatOptions | `lib_general.pies_a_metros()`, `lib_general.metros_a_pies()` (conversiones de unidad) |

### 3. Parámetros globales

| Sección | Función / módulo |
|---|---|
| Accediendo a parámetros globales | `lib_general.obtener_valor_parametro()` con parámetros BuiltIn |

### 5. BuiltInParameters

| Sección | Función / módulo |
|---|---|
| Tipo de almacenamiento | `lib_general.obtener_valor_parametro()` (maneja AsString/AsDouble/AsInteger/AsElementId) |

### 6. Parámetros compartidos

| Sección | Función / módulo |
|---|---|
| Detectar parámetros compartidos | `lib_general.obtener_todos_parametros(elem)` |
| Iterar a través de los parámetros del proyecto | `lib_general.obtener_todos_parametros(elem)`, `lib_general.obtener_parametros_tipo(elem)` |

### 7. Parámetros de información del proyecto

| Sección | Función / módulo |
|---|---|
| Configuraciones de ruta | `lib_bases_datos.cargar_configuracion()`, `lib_bases_datos.guardar_configuracion()` |
| Obtener y establecer categorías | `lib_general.filtrar_por_valor_parametro()` |

### 8. Administrador de familias

| Sección | Función / módulo |
|---|---|
| Insertar parámetros en familias | `lib_familias.obtener_parametros_familia()` |
| Obtener todos los parámetros | `lib_familias.obtener_parametros_familia(symbol)` |
| Crear un tipo de familia | `lib_familias.activar_tipo_familia()` |

### 9. Unidades

| Sección | Función / módulo |
|---|---|
| 9.1 Convertir unidades | `lib_general.pies_a_metros()`, `lib_general.metros_a_pies()`, `lib_general.mm_a_pies()`, `lib_general.pies_a_mm()` |
| 9.2 Convertir a unidades internas | `lib_general.metros_a_pies()`, `lib_general.mm_a_pies()` |
| 9.3 Convertir a unidades de modelo | `lib_general.pies_a_metros()`, `lib_general.pies_a_mm()` |
| 9.4 Cambios Revit 2021 (UnitUtils) | `lib_general.pies_a_metros()` (usa `UnitTypeId` internamente) |
| 9.5 Utilidades de unidades Revit 2022/2023 | Todos los métodos de conversión de `lib_general` |

### 11. Almacenamiento extendido (ExtensibleStorage)

| Sección | Función / módulo |
|---|---|
| Crear un conjunto de datos | `lib_bases_datos.guardar_configuracion()` (alternativa JSON) |

---

## vii. REVIT API - VISTAS (p.257)

### 1. Conceptos generales

| Sección | Función / módulo |
|---|---|
| 1.1 Vistas en el modelo | `lib_vistas.crear_vista_planta()`, `lib_vistas.crear_vista_3d_isometrica()`, `lib_vistas.crear_seccion_desde_curva()`, `lib_vistas.crear_alzado_en_punto()` |
| 1.1 Vista activa | `lib_general.obtener_anotaciones_en_vista()` (usa vista activa) |
| 1.2 Plantillas de vistas | `lib_vistas.aplicar_plantilla_de_vista()`, `lib_vistas.aplicar_plantilla_por_nombre()` |
| 1.3 Crear filtros de vistas | `lib_vistas.crear_filtro_vista_por_texto()`, `lib_vistas.crear_filtro_vista_por_entero()`, `lib_vistas.crear_filtro_vista_combinado()` |
| 1.3 Añadir filtros de vista | `lib_vistas.aplicar_filtro_a_vista()` |
| 1.3 Modificar visibilidad de filtros | `lib_vistas.aplicar_filtro_a_vista(vista, filtro_id, visible, ogs)` |
| 1.3 Obtener filtros de vista | `lib_vistas.listar_filtros_de_vista()`, `lib_vistas.obtener_filtros_del_documento()` |
| 1.3 Eliminar filtros de vista | `lib_vistas.eliminar_filtro_de_vista()` |
| 1.3 Aislar elementos en vista | `lib_vistas.aislar_elementos_temporalmente()`, `lib_vistas.ocultar_elementos_en_vista()` |
| 1.3 Modos temporales de vista | `lib_vistas.aislar_elementos_temporalmente()`, `lib_vistas.convertir_temporal_a_permanente()` |
| 1.3 Duplicar vistas | `lib_vistas.duplicar_vista()`, `lib_vistas.duplicar_vistas()` |
| 1.3 Obtener vistas dependientes | `lib_vistas.duplicar_vista_dependiente()` |
| 1.3 Convertir en vistas independientes | `lib_vistas.convertir_vista_a_independiente()` |
| 1.3 Recortar vista | `lib_vistas.activar_cropbox()`, `lib_vistas.establecer_cropbox()`, `lib_vistas.establecer_recorte_por_curvas()`, `lib_vistas.establecer_recorte_con_offset()` |
| 1.3 Aplicar Caja de referencia | `lib_vistas.crear_vista_3d_por_bbox()` |
| 1.3 Mostrar elementos ocultos | `lib_vistas.mostrar_elementos_en_vista()` |
| 1.3 Ocultar categorías | `lib_vistas.ocultar_categoria_en_vista()` |
| 1.3 Nivel de detalle | `lib_vistas.establecer_nivel_detalle()` |
| 1.3 Disciplina de vista | `lib_vistas.establecer_disciplina()` |
| 1.3 Estilo visual | `lib_vistas.establecer_estilo_visual()` |
| 1.3 Escala de vista | `lib_vistas.establecer_escala()` |
| 1.3 Modificaciones de visualización (overrides) | `lib_vistas.sobreescribir_grafico_elemento()`, `lib_vistas.limpiar_grafico_elemento()` |

### 2. Plantas

| Sección | Función / módulo |
|---|---|
| Crear un plano de planta | `lib_vistas.crear_vista_planta()` |
| Crear plano de áreas | `lib_arquitectura.crear_separacion_de_area()` |
| 2.1 Rango de vista | `lib_vistas.obtener_rango_de_vista()`, `lib_vistas.obtener_rango_vista_completo()` |
| 2.1 Definir Niveles / desfases | `lib_vistas.establecer_rango_de_vista()` |

### 3. Alzados / Secciones

| Sección | Función / módulo |
|---|---|
| 3.1 Crear Alzados | `lib_vistas.crear_alzado_en_punto()` |
| 3.2 Crear secciones | `lib_vistas.crear_seccion_desde_curva()` |
| 3.2 Crear Llamadas (Callouts) | `lib_vistas.crear_cartela()` |
| 3.2 Crear secciones de detalle | `lib_vistas.crear_vista_detalle()` |

### 4. Vistas tridimensionales

| Sección | Función / módulo |
|---|---|
| Vista isométrica | `lib_vistas.crear_vista_3d_isometrica()` |
| Crear vista 3D por SectionBox | `lib_vistas.crear_vista_3d_por_bbox()` |
| Vista 3D desde habitación | `lib_vistas.crear_vista_3d_por_habitacion()` |
| Vista 3D desde sección | `lib_vistas.crear_vista_3d_desde_seccion()` |
| Orientar vista 3D | `lib_vistas.establecer_orientacion_3d()`, `lib_vistas.copiar_orientacion_3d()` |
| Bloquear / desbloquear 3D | `lib_vistas.bloquear_vista_3d()` |
| SectionBox 3D | `lib_vistas.obtener_section_box_3d()` |

### 5. Tablas de planificación

| Sección | Función / módulo |
|---|---|
| Buscar tabla | `lib_vistas.obtener_planificaciones()` |
| Modificar visualización | `lib_vistas.ordenar_planificacion_por_campo()` |
| Crear tabla + campos | `lib_vistas.crear_planificacion()`, `lib_vistas.anadir_campo_a_planificacion()` |
| Exportar tablas | `lib_bases_datos.exportar_schedule_a_csv()`, `lib_excel.exportar_schedule_a_excel()` |
| Obtener datos de tabla | `lib_vistas.obtener_datos_de_planificacion()` |

### 6. Planos

| Sección | Función / módulo |
|---|---|
| Crear planos | `lib_vistas.crear_plano()` |
| Ventanas gráficas | `lib_vistas.anadir_vista_a_plano()`, `lib_vistas.centrar_vista_en_plano()` |
| 6.2 Revisiones | `lib_vistas.crear_revision()`, `lib_vistas.obtener_revisiones()`, `lib_vistas.asignar_revision_a_plano()` |
| Imprimir Planos | `lib_vistas.exportar_vista_a_imagen()` |

### 8. Elementos de referencia

| Sección | Función / módulo |
|---|---|
| 8.1 Niveles — Crear | `lib_coordinacion.crear_nivel()`, `lib_coordinacion.crear_niveles_en_bloque()` |
| 8.2 Rejillas / Ejes | `lib_general.crear_eje()`, `lib_general.obtener_ejes()` |
| 8.2 Planos de referencia | `lib_general.crear_plano_referencia()`, `lib_general.obtener_planos_referencia()` |

### 9. Elementos de anotación

| Sección | Función / módulo |
|---|---|
| 9.1 Líneas de detalle | `lib_vistas.crear_curva_detalle()`, `lib_vistas.crear_curvas_detalle()` |
| 9.2 Cotas | `lib_vistas.crear_cota_lineal()` |
| 9.3 Etiquetas — Etiquetar elementos | `lib_vistas.etiquetar_elemento()`, `lib_vistas.etiquetar_lista_de_elementos()` |
| 9.3 Notas de texto | `lib_vistas.crear_nota_de_texto()` |

---

## viii. REVIT API - FAMILIAS (p.343)

### 1. Familias cargables

| Sección | Función / módulo |
|---|---|
| 1.1 Cargar familias | `lib_familias.cargar_familia()` |
| 1.2 Cargar tipos específicos | `lib_familias.obtener_tipos_de_familia()`, `lib_familias.activar_tipo_familia()` |
| 1.3 Insertar familias sin anfitrión (punto) | `lib_familias.colocar_instancia_familia()` |
| 1.3 Insertar familias con anfitrión (cara) | `lib_familias.colocar_instancia_en_cara()` |
| 1.4 Familias anidadas | `lib_familias.obtener_familias_por_categoria()` |
| Obtener parámetros familia | `lib_familias.obtener_parametros_familia()` |

### 2. Familias de sistema

| Sección | Función / módulo |
|---|---|
| 2.1 Muros — Crear | `lib_arquitectura.crear_muro()` |
| 2.1 Propiedades de muros | `lib_arquitectura.obtener_grosor_muro()`, `lib_arquitectura.obtener_composicion_muro()` |
| 2.1 Filtrar muros por tipo | `lib_arquitectura.obtener_muros_por_tipo()` |
| 2.2 Suelos — Crear | `lib_arquitectura.crear_suelo()`, `lib_arquitectura.crear_suelo_desde_habitacion()` |
| 2.2 Área suelo | `lib_arquitectura.obtener_area_suelo()` |
| 2.2 Abertura en suelo | `lib_arquitectura.crear_abertura_suelo()` |
| 2.3 Elementos Multicapa (CompoundStructure) | `lib_arquitectura.obtener_composicion_muro()`, `lib_arquitectura.modificar_grosor_capa_estructural()` |

### 3. Tipos de familia

| Sección | Función / módulo |
|---|---|
| Duplicar / crear tipos | `lib_familias.activar_tipo_familia()` |
| Datos de identidad | `lib_familias.obtener_parametros_familia()` |

### 4. Agrupación de elementos

| Sección | Función / módulo |
|---|---|
| 4.1 Grupos — Obtener | `lib_general.obtener_grupos()` |
| 4.1 Grupos — Crear | `lib_general.crear_grupo()` |
| 4.1 Grupos — Desagrupar | `lib_general.desagrupar()` |
| 4.1 Grupos — Miembros | `lib_general.obtener_miembros_grupo()` |
| 4.2 Montajes — Crear | `lib_general.crear_ensamblaje()` |
| 4.2 Montajes — Miembros | `lib_general.obtener_miembros_ensamblaje()` |

### 5. Exportar y gestionar familias

| Sección | Función / módulo |
|---|---|
| Exportar familia | `lib_familias.exportar_familia()`, `lib_familias.exportar_todas_las_familias()` |
| Eliminar familias no usadas | `lib_familias.eliminar_familias_no_usadas()` |

---

## ix. REVIT API - MATERIALES (p.405)

| Sección | Función / módulo |
|---|---|
| 1.3 Parámetros de Identidad | `lib_general.obtener_valor_parametro(elem, "Material")` |
| Materiales usados en estructura | `lib_estructura.obtener_material_estructura()`, `lib_estructura.obtener_materiales_usados()` |
| Volumen de hormigón | `lib_estructura.calcular_volumen_hormigon()` |

> **Nota:** La gestión avanzada de materiales (crear, modificar pestaña Gráficos/Aspecto/Físico/Térmica)
> no tiene funciones dedicadas actualmente. Candidato a `lib_materiales.py` futuro.

---

## x. REVIT API - ELEMENTOS ESPACIALES (p.429)

### 2. Habitaciones

| Sección | Función / módulo |
|---|---|
| Crear Habitaciones | *(no implementado — se crea manualmente en Revit)* |
| Propiedades de Habitaciones | `lib_arquitectura.obtener_nombre_habitacion()`, `lib_arquitectura.obtener_numero_habitacion()`, `lib_arquitectura.obtener_area_habitacion()`, `lib_arquitectura.obtener_centroide_habitacion()` |
| Contorno habitaciones | `lib_arquitectura.obtener_contorno_habitacion()`, `lib_arquitectura.obtener_curveloops_habitacion()` |
| Elementos dentro de una habitación | `lib_arquitectura.obtener_elementos_en_habitacion()` |
| Delimitadores de habitación | `lib_arquitectura.obtener_contorno_habitacion()` |
| Filtrar habitaciones | `lib_arquitectura.obtener_habitaciones()`, `lib_arquitectura.obtener_habitaciones_por_nivel()` |
| Propiedades FromRoom / ToRoom | `lib_arquitectura.obtener_puertas_de_habitacion()` |
| Calcular volumen habitación | `lib_arquitectura.calcular_volumen_habitacion()` |
| QA habitaciones | `lib_arquitectura.detectar_habitaciones_sin_numero()`, `lib_arquitectura.detectar_habitaciones_duplicadas()`, `lib_arquitectura.clasificar_habitaciones_por_estado()` |
| Renumerar habitaciones | `lib_arquitectura.renumerar_habitaciones_por_nivel()` |
| Agrupar por nivel | `lib_arquitectura.agrupar_habitaciones_por_nivel()` |
| Ratio acristalamiento | `lib_arquitectura.calcular_ratio_acristalamiento()` |

### 2.1 Áreas

| Sección | Función / módulo |
|---|---|
| Crear delimitadores de áreas | `lib_arquitectura.crear_separacion_de_area()` |

### 4. Circuitos de muros (PlanTopology)

| Sección | Función / módulo |
|---|---|
| Elementos que delimitan una habitación | `lib_arquitectura.obtener_contorno_habitacion()` |
| Acceso a geometría de elementos espaciales | `lib_arquitectura.obtener_curveloops_habitacion()`, `lib_arquitectura.calcular_volumen_habitacion()` |

---

## xi. REVIT API - INSTALACIONES (p.465)

### 2. Entorno documento Revit

| Sección | Función / módulo |
|---|---|
| Sistemas — Agrupar por sistema | `lib_instalaciones.agrupar_tuberias_por_sistema()`, `lib_instalaciones.agrupar_conductos_por_sistema()` |
| Configuración de Sistemas | `lib_instalaciones.obtener_sistema_tuberia()` |

### 3. Enrutamiento de instalaciones

| Sección | Función / módulo |
|---|---|
| Enrutamiento Bandejas | `lib_instalaciones.crear_bandeja_cable()` |

### 6. Mecánica (conductos)

| Sección | Función / módulo |
|---|---|
| Longitud de conductos | `lib_instalaciones.obtener_longitud_conducto()` |
| Longitud total de conductos | `lib_instalaciones.obtener_longitud_total_conductos()` |
| Agrupar conductos por sistema | `lib_instalaciones.agrupar_conductos_por_sistema()` |

### 8. Fontanería (tuberías)

| Sección | Función / módulo |
|---|---|
| Longitud de tuberías | `lib_instalaciones.obtener_longitud_tuberia()` |
| Diámetro exterior | `lib_instalaciones.obtener_diametro_exterior_tuberia()` |
| Longitud total | `lib_instalaciones.obtener_longitud_total_tuberias()` |
| Agrupar por sistema | `lib_instalaciones.agrupar_tuberias_por_sistema()` |

### 10. Advertencias

| Sección | Función / módulo |
|---|---|
| Obtener advertencias del modelo | `lib_coordinacion.analizar_advertencias_por_tipo()` |
| Exportar advertencias | `lib_coordinacion.exportar_advertencias_a_csv()` |

> **Nota:** MEP avanzado (circuitos eléctricos, paneles, sistemas lógicos, creación de conductos/tuberías)
> está parcialmente cubierto en `lib_instalaciones.py`. Se puede ampliar con funciones específicas.

---

## xii. REVIT API - ESTRUCTURAS (p.539)

### 3. Familias cargables

| Sección | Función / módulo |
|---|---|
| 3.1 Vigas — Crear | `lib_estructura.crear_viga()` |
| 3.1 Propiedades de vigas geométricas | `lib_estructura.obtener_longitud_viga()`, `lib_estructura.obtener_propiedades_viga()` |
| 3.1 Material vigas | `lib_estructura.obtener_material_estructura()` |
| 3.1 Vigas por nivel | `lib_estructura.obtener_vigas_por_nivel()`, `lib_estructura.agrupar_vigas_por_nivel()` |
| 3.4 Pilares — Crear vertical | `lib_estructura.crear_pilar_vertical()` |
| 3.4 Pilares — Crear inclinado | `lib_estructura.crear_pilar_inclinado()` |
| 3.4 Propiedades pilares geométricas | `lib_estructura.obtener_altura_pilar()`, `lib_estructura.obtener_nivel_base_pilar()`, `lib_estructura.obtener_nivel_alto_pilar()` |
| 3.4 Pilares por nivel | `lib_estructura.obtener_pilares_por_nivel()` |

### 4. Familias de sistema

| Sección | Función / módulo |
|---|---|
| Forjados — Área | `lib_estructura.obtener_area_forjado()`, `lib_estructura.obtener_area_total_forjados()` |
| Materiales usados | `lib_estructura.obtener_materiales_usados()` |
| Volumen de hormigón | `lib_estructura.calcular_volumen_hormigon()` |

### 5. Huecos

| Sección | Función / módulo |
|---|---|
| Huecos en suelos | `lib_arquitectura.crear_abertura_suelo()` |

### 6. Cargas estructurales

| Sección | Función / módulo |
|---|---|
| 6.1 Cargas puntuales libres | `lib_estructura.crear_carga_puntual()` |
| 6.2 Cargas lineales libres | `lib_estructura.crear_carga_lineal()` |
| 6.3 Cargas superficiales | `lib_estructura.crear_carga_superficial()` |

### 7. Armaduras

| Sección | Función / módulo |
|---|---|
| Recubrimientos | `lib_estructura.obtener_recubrimientos()` |
| Crear armadura | `lib_estructura.crear_armadura()` |
| Tipos de barras | `lib_estructura.crear_armadura()` (tipo_barra_id) |
| Distribución con nº fijo | `lib_estructura.distribuir_armadura_numero_fijo()` |
| Distribución separación máxima | `lib_estructura.distribuir_armadura_separacion_maxima()` |
| Distribución separación mínima | `lib_estructura.distribuir_armadura_separacion_minima()` |
| Representación sólida | `lib_estructura.establecer_armadura_solida_en_vista()` |
| Armaduras de un elemento | `lib_estructura.obtener_armaduras_de_elemento()` |
| 7.2 Armados por área | `lib_estructura.crear_armado_por_area()` |

---

## xiii. REVIT API – TRABAJO COLABORATIVO (p.607)

### 1. Archivos centrales

| Sección | Función / módulo |
|---|---|
| Activar el modelo compartido | `lib_colaborativo.activar_worksharing()` |
| Guardar archivo como central | `lib_colaborativo.guardar_como_central()` |
| Sincronizar con central | `lib_colaborativo.sincronizar_con_central()` |
| Abrir archivo colaborativo | `lib_colaborativo.abrir_documento()` |
| 1.8 Subproyectos (Worksets) — Crear | `lib_colaborativo.crear_workset()` |
| 1.8 Worksets — Obtener | `lib_colaborativo.obtener_worksets()` |
| 1.8 Asignar workset a elemento | `lib_colaborativo.asignar_workset_a_elemento()` |
| 1.8 Asignar workset masivo | `lib_colaborativo.asignar_workset_a_lista()` |
| 1.8 Obtener workset de elemento | `lib_colaborativo.obtener_workset_de_elemento()` |
| QA — Elementos sin workset correcto | `lib_coordinacion.detectar_elementos_sin_workset()` |
| Asignar workset por categoría | `lib_coordinacion.asignar_workset_por_categoria()` |
| Visibilidad de workset | `lib_coordinacion.establecer_visibilidad_workset()` |

### 4. Vínculos de Revit

| Sección | Función / módulo |
|---|---|
| 4.1 Búsqueda de elementos en vínculos | `lib_coordinacion.obtener_elementos_en_link()`, `lib_coordinacion.obtener_elemento_en_link_por_unique_id()` |
| 4.1 Filtrar en link por parámetro | `lib_coordinacion.filtrar_en_link_por_parametro()` |
| 4.1 Filtrar en link por BoundingBox | `lib_coordinacion.filtrar_en_link_por_boundingbox()`, `lib_coordinacion.filtrar_en_link_dentro_de_bbox()`, `lib_coordinacion.filtrar_en_link_contiene_punto()` |
| 4.3 Adquirir coordenadas de link | `lib_coordinacion.adquirir_coordenadas_de_link()` |
| 4.5 Copiar elementos desde link | `lib_coordinacion.copiar_elementos_desde_link()` |
| 4.4 Transformaciones de vínculos | `lib_transformaciones.obtener_transform_elemento()` |
| 4.4 Clases Transform | `lib_transformaciones.crear_transform_traslacion()`, `lib_transformaciones.crear_transform_rotacion()`, `lib_transformaciones.crear_transform_por_ejes()`, `lib_transformaciones.transformar_punto()`, `lib_transformaciones.transformar_vector()`, `lib_transformaciones.invertir_transform()`, `lib_transformaciones.combinar_transforms()` |
| 4.5 Copiar entre documentos | `lib_transformaciones.copiar_elementos_entre_documentos()` |
| 4.5 Mover elementos | `lib_transformaciones.mover_elemento()`, `lib_transformaciones.mover_elementos()` |
| 4.5 Copiar elementos | `lib_transformaciones.copiar_elemento()`, `lib_transformaciones.copiar_elementos()` |
| 4.5 Simetría de elementos | `lib_transformaciones.espejar_elementos()`, `lib_transformaciones.espejar_elemento()` |
| 4.5 Rotar elementos | `lib_transformaciones.rotar_elemento()`, `lib_transformaciones.rotar_elementos()` |
| 4.7 Archivos AutoCAD — Clasificar links | `lib_cad.clasificar_links_cad()` |
| 4.7 Archivos AutoCAD — Capas | `lib_cad.obtener_nombres_capas_cad()` |
| 4.7 Archivos AutoCAD — Curvas por capa | `lib_cad.obtener_curvas_por_capa()` |
| 4.7 Archivos AutoCAD — Eliminar links | `lib_cad.eliminar_link_cad()`, `lib_cad.eliminar_todos_links_cad()` |
| 4.7 Archivos AutoCAD — Recargar | `lib_cad.desanclar_link_cad()` |
| 4.9 Exportar IFC | `lib_bases_datos.exportar_ifc()` |

### 3. Fases

| Sección | Función / módulo |
|---|---|
| Propiedades de fase | `lib_general.obtener_valor_parametro(elem, "Phase Created")` |
| Comparar documentos Revit 2023 | `lib_transacciones.comparar_documentos()` |

---

## xiv. INTERFAZ DE USUARIO (p.659)

### 1. Solicitud de selección de la Interfaz de Usuario

| Sección | Función / módulo |
|---|---|
| 1.1 Seleccionar elementos | `lib_seleccion_ui.seleccionar_elemento()`, `lib_seleccion_ui.seleccionar_multiples()` |
| 1.1 Seleccionar mediante rectángulo | `lib_seleccion_ui.seleccionar_rectangulo()` |
| 1.1 Seleccionar cara | `lib_seleccion_ui.seleccionar_cara()` |
| 1.1 Seleccionar arista | `lib_seleccion_ui.seleccionar_arista()` |
| 1.1 Seleccionar puntos | `lib_seleccion_ui.seleccionar_punto()` |
| 1.1 Seleccionar elemento en link | `lib_seleccion_ui.seleccionar_elemento_en_link()` |
| 1.1 Obtener selección actual | `lib_seleccion_ui.obtener_seleccion_actual()` |
| 1.1 Establecer selección | `lib_seleccion_ui.establecer_seleccion()` |

### 2. Ventanas emergentes (TaskDialogs)

| Sección | Función / módulo |
|---|---|
| Crear ventana emergente | `lib_ui.mensaje()`, `lib_ui.confirmar()`, `lib_ui.confirmar_cancelar()` |
| Botones y acciones | `lib_ui.confirmar()`, `lib_ui.confirmar_cancelar()` |
| Barra de progreso | `lib_ui.con_progreso()` |
| Pedir texto | `lib_ui.pedir_texto()` |
| Pedir número | `lib_ui.pedir_numero()` |

### 3. Formularios de Windows

| Sección | Función / módulo |
|---|---|
| Crear formulario / ventana | `lib_ui.formulario()`, `lib_ui.mostrar_lista()`, `lib_ui.mostrar_tabla()` |
| Seleccionar opción | `lib_ui.seleccionar_opcion()` |
| Selección múltiple | `lib_ui.seleccionar_multiples()` |
| Diálogos de archivo / carpeta | `lib_ui.pedir_archivo()`, `lib_ui.pedir_archivos_multiples()`, `lib_ui.pedir_ruta_guardar()`, `lib_ui.pedir_carpeta()` |
| Seleccionar niveles | `lib_ui.seleccionar_niveles()` |
| Seleccionar categorías | `lib_ui.seleccionar_categorias()` |
| Seleccionar parámetros | `lib_ui.seleccionar_parametros()` |

---

## Secciones del libro sin cobertura actual (candidatas a nuevos módulos)

| Sección | Descripción | Módulo sugerido |
|---|---|---|
| vi.8 Administrador de familias | Insertar/borrar/reemplazar parámetros en familias | `lib_familias.py` ampliar |
| ix. Materiales completo | Crear, modificar Gráficos/Aspecto/Físico/Térmica | `lib_materiales.py` nuevo |
| xi. Circuitos eléctricos | Crear circuito, paneles, cableado, bandejas avanzadas | `lib_instalaciones.py` ampliar |
| xi. Sistemas lógicos MEP | Crear sistema de conductos/tuberías/eléctrico | `lib_instalaciones.py` ampliar |
| xi. Intersección de referencias con rayos | ReferenceIntersector | `lib_geometria.py` ampliar |
| xii. Acero y Prefabricado | API de acero estructural | `lib_estructura.py` ampliar |
| xiii.3 Fases | Crear, combinar, filtrar fases | `lib_coordinacion.py` ampliar |

---

*Generado automáticamente — actualizar al añadir nuevas funciones a la biblioteca.*
