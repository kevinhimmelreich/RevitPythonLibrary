# Índice del libro → RevitPythonLibrary
## "Geometrías con la Revit API — o cómo cuadrar el círculo"
### Kevin Himmelreich (2025, no publicado)

Referencia cruzada entre cada sección del libro y las funciones de la biblioteca RevitPythonLibrary.

**Leyenda:**
- `lib_modulo.funcion()` → función implementada en la biblioteca
- *(no implementado — candidato a lib_X.py)* → funcionalidad pendiente
- *(conceptual — ver libro)* → concepto teórico sin función directa

---

## I. INTRODUCCIÓN

| Sección | Función / módulo |
|---|---|
| 1. Motivación y estructura del manual | *(conceptual — ver README.md)* |
| 2. Bibliotecas y desarrollos Python — Pandas | `lib_scientific.elementos_a_dataframe()`, `lib_excel.leer_excel_pandas()` |
| 2. Bibliotecas — Sympy (cálculo simbólico) | *(no implementado — candidato a lib_scientific.py)* |
| 2. Bibliotecas — Shapely (geometría 2D) | `lib_scientific.poligono_shapely()`, `lib_scientific.interseccion_shapely()` |
| 2. Bibliotecas — Scipy (optimización, álgebra) | `lib_scientific.calcular_estadisticas()` |
| 2. Bibliotecas — scikit-spatial | *(no implementado — candidato a lib_scientific.py)* |
| 2. Bibliotecas — Pygeos | *(no implementado — candidato a lib_scientific.py)* |
| 2. Bibliotecas — Matplotlib | `lib_scientific.graficar_histograma()`, `lib_scientific.graficar_scatter()` |
| 2. Bibliotecas — Vpython (objetos 3D) | *(no implementado — candidato a lib_scientific.py)* |
| 2. Bibliotecas — Trimesh (mallas) | *(no implementado — candidato a lib_scientific.py)* |
| 2. Bibliotecas — Spherical-Coordinates | *(no implementado — candidato a lib_scientific.py)* |
| 3. Plantilla Python — import clr, AddReference, DocumentManager | Cabecera estándar de todos los módulos de la biblioteca |

---

## II. GEOMETRIA REVIT API

### 1. Búsqueda de elementos geométricos

#### 1.1 Coleccionando elementos (FilteredElementCollector)

| Sección | Función / módulo |
|---|---|
| FEC — buscar en todo el documento | Base de `lib_general.filtrar_por_valor_parametro()` |
| FEC — buscar en vista específica | `lib_vistas.obtener_elementos_visibles_en_vista()` |

#### 1.2 Filtros rápidos

| Sección | Función / módulo |
|---|---|
| Elementos que no se pueden filtrar por clase (Curve, Edge, Mesh, Solid…) | *(conceptual — se obtienen como subelementos)* |
| Elementos por clase y categoría (ReferencePoint, CurveByPoints, Form…) | `lib_familias.obtener_familias_por_categoria()`, `lib_general.filtrar_por_valor_parametro()` |
| Elementos controlados por líneas (ElementIsCurveDrivenFilter) | *(no implementado — candidato a lib_general.py)* |
| Tipos de familias (FamilySymbolFilter) | `lib_familias.obtener_tipos_de_familia()` |
| Excluir de la búsqueda (ExclusionFilter) | `lib_general.excluir_elementos(ids, cat_bic)` |

#### 1.3 Filtros lentos

| Sección | Función / módulo |
|---|---|
| Elementos que interceptan con otros (ElementIntersectsElementFilter) | `lib_coordinacion.detectar_colisiones_bbox()` |
| Elementos que interceptan sólidos (ElementIntersectsSolidFilter) | `lib_coordinacion.detectar_colisiones_solidos()` |
| Tipos de líneas (CurveElementFilter, CurveElementType) | *(no implementado — candidato a lib_geometria.py)* |
| Instancias de familias (FamilyInstanceFilter por tipo) | `lib_familias.obtener_familias_por_categoria()` |

#### 1.4 Filtros lógicos

| Sección | Función / módulo |
|---|---|
| LogicalAndFilter | `lib_general.combinar_filtros_y(filtros)` |
| LogicalOrFilter | `lib_general.combinar_filtros_o(filtros)` |

#### 1.5 Buscar elementos dependientes (GetDependentElements)

| Sección | Función / módulo |
|---|---|
| GetDependentElements con filtro de clase (Sketch) | *(no implementado — candidato a lib_general.py)* |
| GetDependentElements sin filtro (None) | *(no implementado — candidato a lib_general.py)* |

---

### 2. Seleccionar elementos geométricos

#### 2.1 Usando nodos de Dynamo

| Sección | Función / módulo |
|---|---|
| Select Model Element / Elements + UnwrapElement() | `lib_general.unwrap(elem)`, `lib_general.unwrap_lista(elems)` |

#### 2.2 Usando la Revit API (Autodesk.Revit.UI.Selection)

| Sección | Función / módulo |
|---|---|
| PickBox(PickBoxStyle) | `lib_seleccion_ui.seleccionar_rectangulo()` |
| PickElementsByRectangle | `lib_seleccion_ui.seleccionar_rectangulo()` |
| PickObject(ObjectType.Element) | `lib_seleccion_ui.seleccionar_elemento()` |
| PickObject(ObjectType.Face) | `lib_seleccion_ui.seleccionar_cara()` |
| PickObject(ObjectType.Edge) | `lib_seleccion_ui.seleccionar_arista()` |
| PickObject(ObjectType.PointOnElement) | `lib_seleccion_ui.seleccionar_punto()` |
| PickObject(ObjectType.LinkedElement) | `lib_seleccion_ui.seleccionar_elemento_en_link()` |
| PickObject(ObjectType.Subelement) | *(no implementado — candidato a lib_seleccion_ui.py)* |
| PickObjects (múltiples) | `lib_seleccion_ui.seleccionar_multiples()` |
| PickPoint | `lib_seleccion_ui.seleccionar_punto()` |

#### 2.3 Aplicando los métodos de selección

| Sección | Función / módulo |
|---|---|
| Tabla ObjectType (Edge=3, Element=1, Face=4, LinkedElement=5, PointOnElement=2, Subelement=6) | *(conceptual — ver libro)* |
| Tipos de cara (PlanarFace, CylindricalFace, ConicalFace, RevolvedFace, RuledFace, HermiteFace) | *(conceptual — ver sección II.8 del libro)* |
| Seleccionar cara / arista / punto en cara | `lib_seleccion_ui.seleccionar_cara()`, `lib_seleccion_ui.seleccionar_arista()` |
| Seleccionar forma combinada / subelemento | *(no implementado — candidato a lib_seleccion_ui.py)* |
| Seleccionar planos de referencia | `lib_seleccion_ui.seleccionar_elemento()` |
| Seleccionar mediante rectángulo | `lib_seleccion_ui.seleccionar_rectangulo()` |

---

### 3. Sobre Puntos y Vectores

| Sección | Función / módulo |
|---|---|
| Tipos de puntos en Revit | *(conceptual — ver libro p.38ss)* |
| Qué es un vector (XYZ como vector) | `lib_transformaciones.vector_entre_puntos(origen, destino)` |
| Distancia entre dos puntos (DistanceTo) | `lib_transformaciones.distancia_entre_puntos_m(pto_a, pto_b)` |
| Distancia entre un punto y múltiples puntos | `lib_geometria.distancias_entre_puntos_numpy()` |
| Igualdad de puntos o vectores (IsAlmostEqualTo) | *(conceptual — método nativo de XYZ)* |
| Operaciones con vectores — suma (Add) | *(conceptual — método nativo de XYZ)* |
| Operaciones con vectores — resta (Subtract) | *(conceptual — método nativo de XYZ)* |
| Operaciones con vectores — multiplicación (Multiply) | *(conceptual — método nativo de XYZ)* |
| Longitud de vectores (GetLength) | *(conceptual — método nativo de XYZ)* |
| Vectores negativos (Negate) | *(conceptual — método nativo de XYZ)* |
| Ángulo entre vectores (DotProduct, AngleTo) | *(conceptual — método nativo de XYZ)* |
| Normalizar vectores (Normalize) | *(conceptual — método nativo de XYZ)* |
| Obtener vector perpendicular a otro | *(no implementado — candidato a lib_geometria.py)* |
| Mover puntos a través de un vector (Normalize + Multiply + Add) | `lib_transformaciones.mover_elemento(elem, vector_xyz)` |
| Mover puntos a través de dos vectores | `lib_transformaciones.alinear_a_punto(elem, punto_destino_xyz)` |

---

### 4. Sistemas de Coordenadas

#### 4.1 Tipos de sistemas

| Sección | Función / módulo |
|---|---|
| ByCoordinates (x, y) — punto 2D UV | *(conceptual — UV)* |
| ByCoordinates (x, y, z) — punto 3D XYZ | *(conceptual — XYZ nativo)* |
| ByCylindricalCoordinates (radio, ángulo, altura) | *(no implementado — candidato a lib_geometria.py)* |
| BySphericalCoordinates (r, θ, φ) | *(no implementado — candidato a lib_geometria.py)* |
| cartesianToPolar / cartesianToSpherical | *(no implementado — candidato a lib_geometria.py)* |

#### 4.2 Transformaciones

| Sección | Función / módulo |
|---|---|
| Obtener transformaciones de vínculos de Revit (GetTotalTransform) | `link_inst.GetTotalTransform()` — ver workflow en cap. v.10 de INDICE_LIBRO.md |
| Obtener transformaciones de familias cargables (GetTransform) | `lib_transformaciones.obtener_transform_elemento(instancia)` |
| Obtener transformaciones familias de sistema (BoundingBox.Transform) | *(no implementado directamente — usar get_BoundingBox().Transform)* |
| Crear transformaciones — Identidad (Transform.Identity) | `lib_transformaciones.crear_transform_traslacion(XYZ(0,0,0))` |
| Crear transformaciones — Traslación (CreateTranslation) | `lib_transformaciones.crear_transform_traslacion(vector_xyz)` |
| Crear transformaciones — Rotación por origen (CreateRotation) | `lib_transformaciones.crear_transform_rotacion(eje_xyz, angulo_grados)` |
| Crear transformaciones — Rotación en punto arbitrario (CreateRotationAtPoint) | *(no implementado — candidato a lib_transformaciones.py)* |
| Crear transformaciones — Reflexión (CreateReflection) | `lib_transformaciones.crear_plano_espejo(normal_xyz, origen_xyz)` |
| Crear transformaciones 1D (Transform1D) | *(no implementado — candidato a lib_transformaciones.py)* |
| Crear transformaciones 2D (Transform2D) | *(no implementado — candidato a lib_transformaciones.py)* |
| Aplicar transformaciones — SetCoordinateSystem (puntos de referencia) | *(no implementado — específico de familias adaptativas)* |
| Aplicar transformaciones — MoveElement / MoveElements | `lib_transformaciones.mover_elemento()`, `lib_transformaciones.mover_elementos()` |
| Aplicar transformaciones — CopyElement / CopyElements | `lib_transformaciones.copiar_elemento()`, `lib_transformaciones.copiar_elementos()` |
| Aplicar transformaciones — SolidUtils.CreateTransformed | `lib_geometria.booleano_interseccion()` (internamente) |
| Aplicar transformaciones — Curve.CreateTransformed | *(no implementado — candidato a lib_geometria.py)* |
| Métodos Transform — AlmostEqual, Multiply, OfPoint, OfVector, ScaleBasis | `lib_transformaciones.transformar_punto()`, `lib_transformaciones.transformar_vector()` |
| Propiedades Transform — BasisX/Y/Z, Origin, Scale, Determinant, Inverse… | `lib_transformaciones.invertir_transform()`, `lib_transformaciones.combinar_transforms()` |
| Método transformaciones 1D — TransformParameterDomain | *(no implementado — candidato a lib_transformaciones.py)* |
| Métodos transformaciones 2D — Assign, GetInverse, PostScale, PreScale… | *(no implementado — candidato a lib_transformaciones.py)* |
| Propiedades Transform 1D y 2D — Translation, BasisU, BasisV, Determinant… | *(no implementado — candidato a lib_transformaciones.py)* |

---

### 5. Modificadores de geometría

#### 5.1 Obtener la geometría de un Elemento (get_Geometry + Options)

| Sección | Función / módulo |
|---|---|
| Options (ComputeReferences, IncludeNonVisibleObjects, View) | Patrón interno de `lib_geometria.obtener_caras_solido()`, `lib_geometria.obtener_aristas_solido()` |
| get_Geometry(opt) — obtener sólidos, curvas, vértices, aristas | `lib_geometria.obtener_caras_solido()`, `lib_geometria.obtener_aristas_solido()` |

#### 5.2 Desplazar, Rotar y Escalar geometrías

| Sección | Función / módulo |
|---|---|
| Escalar sólido (ScaleBasisAndOrigin + SolidUtils.CreateTransformed) | *(no implementado — candidato a lib_geometria.py)* |
| Rotar sólido (Transform.CreateRotationAtPoint + SolidUtils.CreateTransformed) | *(no implementado — candidato a lib_geometria.py)* |

#### 5.3 Análisis geométrico

| Sección | Función / módulo |
|---|---|
| Distancia entre sólidos (BooleanOperationsUtils + triangulación de caras) | `lib_coordinacion.detectar_colisiones_solidos()` |

---

### 6. Ayudantes de geometría

#### 6.1 Tipos de planos (Plane) y proyección

| Sección | Función / módulo |
|---|---|
| Plane — concepto (Origin, Normal, XVec, YVec) | *(conceptual — ver libro)* |
| Proyectar puntos a un plano (Plane.Project) | *(no implementado — candidato a lib_geometria.py)* |
| Proyectar puntos en plano numpy (project_points_to_plane) | `lib_geometria.ajuste_plano_numpy()` |

#### 6.3 Plano de referencia (ReferencePlane)

| Sección | Función / módulo |
|---|---|
| Crear plano de referencia (doc.FamilyCreate.NewReferencePlane) | `lib_general.crear_plano_referencia()` |
| Métodos — Flip(), GetPlane(), GetReference() | *(conceptual — métodos nativos de ReferencePlane)* |
| Propiedades — BubbleEnd, Direction, FreeEnd, Name, Normal | *(conceptual — propiedades nativas)* |
| Parámetros BuiltIn de planos de referencia | *(conceptual — ver libro)* |

#### 6.4 Planos de boceto (SketchPlane)

| Sección | Función / módulo |
|---|---|
| Crear SketchPlane desde Plane | *(no implementado — se usa internamente en lib_geometria.py)* |
| Crear SketchPlane desde ReferencePlane | *(no implementado — se usa internamente en lib_familias.py)* |
| Métodos — GetPlane(), GetPlaneReference() | *(conceptual — métodos nativos)* |
| Propiedades — IsSuitableForModelElements | *(conceptual — propiedad nativa)* |
| Parámetros — SKETCH_PLANE_PARAM | *(conceptual — parámetro BuiltIn)* |

#### 6.5 Referencias (Reference)

| Sección | Función / módulo |
|---|---|
| Crear Referencia (Reference(elemento), GeometryCurve.Reference) | *(conceptual — uso directo del API)* |
| Propiedades de Referencia — ElementReferenceType, GlobalPoint, UVPoint, LinkedElementId | *(conceptual — propiedades nativas)* |
| Tabla tipos de referencia (NONE, LINEAR, SURFACE, FOREIGN, INSTANCE, CUT_EDGE, MESH, SUBELEMENT) | *(conceptual — enumerado ElementReferenceType)* |
| Obtener Referencias estables (ConvertToStableRepresentation, ParseFromStableRepresentation) | *(no implementado — candidato a lib_general.py)* |
| Referencias de anfitriones (HostObjectUtils.GetSideFaces) | *(no implementado — candidato a lib_arquitectura.py)* |

#### 6.6 XYZ

| Sección | Función / módulo |
|---|---|
| Puntos de coordenadas (XYZ como punto 3D) | `lib_transformaciones.vector_entre_puntos()` |
| Agrupar puntos en paneles (4 pts, generate_sequential_points) | `lib_geometria.agrupar_puntos_por_proximidad()` |
| Ecuación del plano (punto_en_plano con DotProduct) | *(no implementado — candidato a lib_geometria.py)* |

#### 6.7 UV

| Sección | Función / módulo |
|---|---|
| Puntos en cara (proyectar familias sobre caras de muro → UV) | *(no implementado — candidato a lib_geometria.py)* |
| Face.ComputeNormal(UV), Face.IsInside(UV) | *(no implementado — candidato a lib_geometria.py)* |
| Mover elementos en vistas bidimensionales (Transform2D) | *(no implementado — candidato a lib_transformaciones.py)* |

#### 6.8 Bounding Box XYZ

| Sección | Función / módulo |
|---|---|
| Obtener BoundingBoxXYZ de un elemento (get_BoundingBox + ToProtoType) | `lib_general.filtrar_por_boundingbox()` (usa bbox internamente) |
| Definir ámbito o recorte de una vista 2D o 3D | `lib_vistas.crear_vista_3d_por_bbox()` |
| Utilizarlo como filtro (dentro/fuera del espacio 3D) | `lib_general.filtrar_por_boundingbox()`, `lib_general.filtrar_dentro_de_bbox()`, `lib_general.filtrar_contiene_punto()` |
| Crear BoundingBox a partir de dos puntos (BoundingBoxXYZ + Min/Max) | *(no implementado — candidato a lib_geometria.py)* |
| Obtener BoundingBoxes de elementos girados | *(no implementado — candidato a lib_geometria.py)* |
| Obtener BoundingBox común a varios elementos (obtener_bounding_box_comun) | `lib_transformaciones.centroide_bbox(elem)` |
| Modificar BoundingBox existente (expandir_bounding_box) | *(no implementado — candidato a lib_geometria.py)* |

#### 6.9 BoundingBoxUV

| Sección | Función / módulo |
|---|---|
| Face.GetBoundingBox() → BoundingBoxUV con Min/Max UV | *(no implementado — candidato a lib_geometria.py)* |
| Subdividir cara en rejilla UV para generar puntos uniformes | *(no implementado — candidato a lib_geometria.py)* |

---

### 7. Agrupación de elementos

#### 7.1 ¿Qué es un Interfaz? (ABC, IElementCollector)

| Sección | Función / módulo |
|---|---|
| Interfaces en Python con ABC + @abstractmethod | *(conceptual — patrón de diseño)* |

#### 7.2 IEnumerable e IEnumerator: La Iteración en C# y Python

| Sección | Función / módulo |
|---|---|
| IEnumerable / IEnumerator — from System.Collections.Generic import * | Cabecera de todos los módulos de la biblioteca |
| IEnumerator — iter() / next() en Python para FEC | Base de todos los colectores de la biblioteca |
| IEnumerable — for loop implícito sobre FEC | Base de todos los colectores de la biblioteca |

#### 7.3 Iteradores

| Sección | Función / módulo |
|---|---|
| Ventajas de usar iterador frente a bucles (ForwardIterator) | *(conceptual — ver libro)* |

#### 7.4 Conjunto de elementos (colecciones del API)

| Sección | Función / módulo |
|---|---|
| ReferencePointArray | *(usado internamente en lib_familias.py)* |
| CurveArray, CurveArrArray | `lib_geometria.crear_curveloop_desde_curvas()` |
| EdgeArray, EdgeArrayArray | *(usado internamente en lib_geometria.py)* |
| ModelCurveArray, DetailCurveArray, SymbolicCurveArray | *(no implementado — candidato a lib_geometria.py)* |
| FaceArray, FormArray | *(no implementado — candidato a lib_familias.py)* |
| ReferenceArray, ReferenceArrayArray | *(usado internamente en lib_familias.py)* |
| ElementArray | *(usado internamente en lib_general.py)* |
| Listas fuertemente tipadas (List[ElementId]()) | Usado en `lib_general.obtener_ids_int()`, `lib_transformaciones.mover_elementos()` |

#### 7.5 Bucles de curvas (CurveLoop)

| Sección | Función / módulo |
|---|---|
| Crear CurveLoop (ordenarLineasLoop) | `lib_geometria.crear_curveloop_desde_curvas()` |
| Obtener CurveLoop de cara (face.EdgeLoops) | `lib_geometria.obtener_caras_solido()` |
| Copiar bucle (CurveLoop.CreateViaCopy) | *(no implementado — candidato a lib_geometria.py)* |
| Desfase de CurveLoop (CurveLoop.CreateViaOffset) | *(no implementado — candidato a lib_geometria.py)* |
| Desfase múltiple (CreateViaOffset con List[Double]) | *(no implementado — candidato a lib_geometria.py)* |
| Crear por engrosamiento (CurveLoop.CreateViaThicken) | *(no implementado — candidato a lib_geometria.py)* |
| Crear a través de transformaciones (Transform().Multiply) | `lib_transformaciones.combinar_transforms()` |
| Obtener datos — GetCurveLoopIterator, GetPlane, IsRectangular, IsOpen, NumberOfCurves, IsCounterclockwise | *(no implementado — candidato a lib_geometria.py)* |

---

### 8. Clases de elementos geométricos

| Sección | Función / módulo |
|---|---|
| Jerarquía: GeometryObject → Curve → Arc/Line/NurbSpline/Ellipse/HermiteSpline/CylindricalHelix | *(conceptual — ver libro)* |
| Jerarquía: APIObject → BoundingBoxXYZ (no es GeometryObject) | *(conceptual — ver libro)* |
| Tabla de clases: FORM, FREEFORM, FRAME, GENERIC FORM, GEOMETRY ELEMENT, GEOMETRY INSTANCE, GEOMETRY Object | *(conceptual — ver libro)* |
| FamilyItemFactory / ItemFactoryBase (métodos de creación en familias) | `lib_familias.cargar_familia()`, `lib_familias.colocar_instancia_familia()` |

---

## III. GEOMETRÍA EN REVIT

### 9. Componentes Geométricos en Revit

#### 9.1 Elementos geométricos en Revit

| Sección | Función / módulo |
|---|---|
| Diagrama GeometryElement → Solids / Meshes / GeometryInstances / Curves / Polylines | *(conceptual — ver libro)* |

#### 9.2 Puntos

| Sección | Función / módulo |
|---|---|
| Crear por coordenadas cartesianas (XYZ) | *(conceptual — XYZ nativo)* |
| Proyectar puntos a un plano (project_points_to_plane con numpy) | `lib_geometria.ajuste_plano_numpy()` |

#### 9.3 Puntos UV

| Sección | Función / módulo |
|---|---|
| Usar UV para crear Room, Space, Area y sus etiquetas | *(no implementado — candidato a lib_arquitectura.py)* |
| Edge.GetCurveUV — bucles internos de geometría | *(no implementado — candidato a lib_geometria.py)* |
| FieldDomainPointsByUV, Face.ComputeNormal(UV), Face.IsInside(UV) | *(no implementado — candidato a lib_geometria.py)* |
| NewPointOnFace() | *(no implementado — candidato a lib_familias.py)* |
| Mover elementos en vistas 2D (Transform2D) | *(no implementado — candidato a lib_transformaciones.py)* |
| CompoundStructure.SplitRegion(UV) | *(no implementado — candidato a lib_arquitectura.py)* |

#### 9.4 Curvas

| Tipo de curva | Función / módulo |
|---|---|
| Círculo (Arc con ángulo 0 a 2π) | `lib_geometria.crear_arco()` |
| Círculo que mejor se ajusta a puntos (fit_circle con scipy.minimize) | `lib_scientific.calcular_estadisticas()` (scipy disponible) |
| Círculo mejor ajuste 3D (fit_circle_3d + SVD + optimize) | *(no implementado — candidato a lib_geometria.py)* |
| Círculo por plano + centro + ángulo (Arc.Create con Plane) | `lib_geometria.crear_arco()` |
| Círculo mediante tres puntos (define_circle) | *(no implementado — candidato a lib_geometria.py)* |
| Círculo centro + inicio + ángulo (crear_arco_por_centro_inicio_angulo) | *(no implementado — candidato a lib_geometria.py)* |
| Punto más cercano a la curva (ComputeClosestPoints → ClosestPointsPairBetweenTwoCurves) | *(no implementado — candidato a lib_geometria.py)* |
| Crear Line Bound / UnBound | `lib_geometria.crear_linea()` |
| Arco de elipse (Ellipse.CreateCurve + ángulos inicio/fin) | *(no implementado — candidato a lib_geometria.py)* |
| Helicoide (Helix.ByAxis) | *(no implementado — candidato a lib_geometria.py)* |
| Espiral media esfera (numpy + ReferencePointArray + NewCurveByPoints) | `lib_scientific.xyz_a_numpy()` + `lib_geometria.crear_nurbs_por_puntos()` |
| Línea que mejor se ajuste a puntos (fit_line_3d con SVD) | *(no implementado — candidato a lib_geometria.py)* |
| Curvas Nurbs (geomdl, NurbSpline.CreateCurve) | `lib_geometria.crear_nurbs_por_puntos()` |
| Polycurve | *(no implementado — candidato a lib_geometria.py)* |
| Polígono (ByPoints, RegularPolygon) | *(no implementado — candidato a lib_geometria.py)* |
| Comprobación de línea en plano (curva_en_plano con DotProduct) | *(no implementado — candidato a lib_geometria.py)* |

#### 9.5 Parametrización de curvas

| Sección | Función / módulo |
|---|---|
| Evaluar (Evaluate con normalizado 0-1 o real) | *(conceptual — método nativo de Curve)* |
| Obtener parámetro final (GetEndParameter) | *(conceptual — método nativo de Curve)* |
| Obtener punto extremo (GetEndPoint) | *(conceptual — método nativo de Curve)* |
| Está dentro (IsInside) | *(conceptual — método nativo de Curve)* |
| Clonar (Clone) | *(conceptual — método nativo de Curve)* |
| Calcular puntos más cercanos (ComputeClosestPoints) | *(no implementado — candidato a lib_geometria.py)* |
| Calcular derivadas (ComputeDerivatives) | *(no implementado — candidato a lib_geometria.py)* |
| Calcular distancia normalizada (ComputeNormalizedParameter) | *(no implementado — candidato a lib_geometria.py)* |
| Calcular distancia real (ComputeRawParameter) | *(no implementado — candidato a lib_geometria.py)* |
| Crear desplazada (CreateOffset) | *(no implementado — candidato a lib_geometria.py)* |
| Invertir curva (CreateReversed) | *(no implementado — candidato a lib_geometria.py)* |
| Crear transformada (CreateTransformed con Transform) | *(no implementado — candidato a lib_geometria.py)* |
| Distancia más corta (Distance) | `lib_transformaciones.distancia_entre_puntos_m()` |
| Obtener referencia de extremo (GetEndPointReference) | *(no implementado — candidato a lib_geometria.py)* |
| Intersecar (Intersect → SetComparisonResult) | *(no implementado — candidato a lib_geometria.py)* |
| Proyectar (Project → IntersectionResult con Distance, Parameter) | *(no implementado — candidato a lib_geometria.py)* |
| Establecer estilo gráfico (SetGraphicsStyleId) | *(no implementado — candidato a lib_geometria.py)* |
| Descomponer en segmentos (Tessellate) | *(no implementado — candidato a lib_geometria.py)* |
| Dividir línea en dos (split_line_AtParameter) | *(no implementado — candidato a lib_geometria.py)* |
| Distancia punto a círculo (point_to_circle_distance con numpy) | `lib_scientific.xyz_a_numpy()` (numpy disponible) |

#### 9.6 Superficies

| Sección | Función / módulo |
|---|---|
| Superficies a partir de NurbSplines (NewLoftForm desde ReferenceArrayArray) | *(no implementado — específico de familias conceptuales)* |

#### 9.7 Mosaicos

| Sección | Función / módulo |
|---|---|
| ConvexHull (scipy.spatial) | `lib_scientific.calcular_estadisticas()` (scipy disponible) |
| Delaunay (scipy.spatial) | `lib_scientific.calcular_estadisticas()` (scipy disponible) |
| Voronoi (shapely.ops.voronoi_diagram) | `lib_scientific.interseccion_shapely()` (shapely disponible) |
| Voronoi esférico (Splipy T-Spline) | *(no implementado — candidato a lib_scientific.py)* |

#### 9.8 Mallas

| Sección | Función / módulo |
|---|---|
| Mesh (ByPointsFaceIndices, FaceIndices, VertexNormals, VertexPositions) | *(no implementado — candidato a lib_geometria.py)* |

---

## III.II → IV. SÓLIDOS (cap. 10-11 del libro)

### 10. Sólidos

#### 10.1 Crear Geometrías (GeometryCreationUtilities)

| Tipo de sólido | Función / módulo |
|---|---|
| Sólido por extrusión (CreateExtrusionGeometry) | `lib_geometria.booleano_interseccion()` (internamente usa sólidos) |
| Sólido tipo blend / fusión (CreateBlendGeometry + VertexPair) | *(no implementado — candidato a lib_geometria.py)* |
| Sólido por barrido / sweep (CreateSweptGeometry) | *(no implementado — candidato a lib_geometria.py)* |
| Sólido por barrido con dirección (CreateFixedReferenceSweptGeometry) | *(no implementado — candidato a lib_geometria.py)* |
| Sólido barrido y fusión / swept blend (CreateSweptBlendGeometry) | *(no implementado — candidato a lib_geometria.py)* |
| Sólido entre varios perfiles (CreateLoftGeometry) | *(no implementado — candidato a lib_geometria.py)* |
| Sólido de revolución (CreateRevolvedGeometry + Frame) | *(no implementado — candidato a lib_geometria.py)* |
| Función esfera (revolución de semicírculo + CreateRevolvedGeometry) | *(no implementado — candidato a lib_geometria.py)* |
| Apollonian (empaquetado de esferas tangentes con Soddy) | *(no implementado — candidato a lib_geometria.py)* |
| Crear cono (revolución de triángulo) | *(no implementado — candidato a lib_geometria.py)* |
| Crear cono truncado (revolución de trapecio) | *(no implementado — candidato a lib_geometria.py)* |
| Propiedades de un cono (clase RevolvedSolid personalizada) | *(no implementado — candidato a lib_geometria.py)* |
| Cuboid (ByCorners, ByLengths, ByLengths con CoordinateSystem) | *(no implementado — candidato a lib_geometria.py)* |
| Cilindro (dos arcos + CreateExtrusionGeometry) | *(no implementado — candidato a lib_geometria.py)* |

#### 10.2 Subelementos de Sólidos

| Sección | Función / módulo |
|---|---|
| Descomponer un sólido (Faces, Edges) | `lib_geometria.obtener_caras_solido()`, `lib_geometria.obtener_aristas_solido()` |
| Función DescomponerGeom (get_Geometry + Options) | *(no implementado como función pública — candidato a lib_geometria.py)* |
| Descomponer caras (EdgeLoops de cada Face) | `lib_geometria.obtener_caras_solido()` |
| Edges — métodos: AsCurve, AsCurveFollowingFace, ComputeDerivatives, Evaluate, GetEndPointReference, GetFace, IsFlippedOnFace, Tessellate, TessellateOnFace | *(no implementado — candidato a lib_geometria.py)* |

#### 10.3 Tipos de caras

| Tipo | Función / módulo |
|---|---|
| PlanarFace — FaceNormal, Origin, XVector, YVector | `lib_geometria.obtener_caras_solido()` |
| CylindricalFace — Axis, Origin, Radius | `lib_geometria.obtener_caras_solido()` |
| ConicalFace — Axis, HalfAngle, Origin, Radius | `lib_geometria.obtener_caras_solido()` |
| RevolvedFace — Axis, Curve, Origin, Radius | `lib_geometria.obtener_caras_solido()` |
| RuledFace — Curve, IsExtruded, Point, RulingsAreParallel | `lib_geometria.obtener_caras_solido()` |
| HermiteFace — MixedDerivs | `lib_geometria.obtener_caras_solido()` |

---

### 11. DirectShapes

#### 11.1 Elementos válidos solo para DirectShapes

| Tipo | Función / módulo |
|---|---|
| Solid (sólidos complejos creados desde cero o importados) | `lib_geometria.crear_directshape_desde_solido()` |
| Superficie reglada (RuledSurface.Create) | *(no implementado — candidato a lib_geometria.py)* |
| Mesh (importaciones desde Rhino, SketchUp…) | *(no implementado — candidato a lib_geometria.py)* |
| Face, Surface, HermiteSpline, HermiteSurface | *(no implementado — candidato a lib_geometria.py)* |

#### 11.2-11.5 DirectShape — Geometrías, Familias anidadas, Transformaciones

| Sección | Función / módulo |
|---|---|
| 11.2 Geometrías en DirectShape | `lib_geometria.crear_directshape_desde_solido()` |
| 11.3 Familias anidadas en DirectShape | *(no implementado — candidato a lib_geometria.py)* |
| 11.4 Transformaciones — Origen Interfaz de Revit vs Dynamo | *(conceptual — ver INDICE_LIBRO.md cap. v.10)* |

---

## IV → III.II. FAMILIAS

### 1. Jerarquía de Familia

| Sección | Función / módulo |
|---|---|
| Estructura: Family / FamilyInstance / FamilySymbol / FamilyType | `lib_familias.obtener_tipos_de_familia()`, `lib_familias.activar_tipo_familia()` |
| Diferencias tipos vs símbolos | *(conceptual — ver libro)* |
| Moverse entre objetos (FamilyInstance → FamilyType → Family) | `lib_familias.obtener_familias_por_categoria()` |
| Moverse hacia abajo (Family → FamilyTypes → FamilyInstances) | `lib_familias.obtener_tipos_de_familia()` |
| 1.2. Planos de Referencia en familias (GetReferences, FamilyInstanceReferenceType) | *(no implementado — candidato a lib_familias.py)* |

### 2. Geometrías de familias

| Sección | Función / módulo |
|---|---|
| 2.1 Boceto entorno de familia (editar Sketch + NewModelCurve en plano) | *(no implementado — candidato a lib_familias.py)* |
| 2.2 Boceto en entorno de Proyecto (SketchEditScope + PythonNet3 + IFailuresPreprocessor) | *(no implementado — requiere PythonNet3/CPython3)* |
| 2.3 Líneas simbólicas (NewSymbolicCurve) | *(no implementado — candidato a lib_familias.py)* |
| 2.4 Perfiles — crear (NewCurveLoopsProfile, NewFamilySymbolProfile) | *(no implementado — candidato a lib_familias.py)* |
| 2.5 Extrusión (NewExtrusion) | *(no implementado — candidato a lib_familias.py)* |
| 2.5 Revolución (NewRevolution) | *(no implementado — candidato a lib_familias.py)* |
| 2.5 Fundidos/Blend (NewBlend + VertexPairs) | *(no implementado — candidato a lib_familias.py)* |
| 2.5 Barridos (NewSweep — dos sobrecargas: CurveArray o ReferenceArray) | *(no implementado — candidato a lib_familias.py)* |
| 2.5 Barrido con fundido (NewSweptBlend) | *(no implementado — candidato a lib_familias.py)* |
| 2.5 Formas vacías (isSolid=False) | *(no implementado — candidato a lib_familias.py)* |
| 2.5 Controles (ControlShape: HorizontalArrow, VerticalArrow, DoubleHorizontalArrow) | *(no implementado — candidato a lib_familias.py)* |
| 2.6 Aplicar perfiles (AssociateElementParameterToFamilyParameter en barridos) | *(no implementado — candidato a lib_familias.py)* |

### 3. Operaciones con Geometrías (en familias)

| Sección | Función / módulo |
|---|---|
| Intersección línea con sólidos (IntersectWithCurve + SolidCurveIntersectionOptions) | *(no implementado — candidato a lib_geometria.py)* |
| 3.1 Operaciones booleanas (BooleanOperationsUtils.ExecuteBooleanOperation) | `lib_geometria.booleano_interseccion()`, `lib_geometria.booleano_union()`, `lib_geometria.booleano_diferencia()` |
| 3.1 Modificar sólido original (ExecuteBooleanOperationModifyingOriginalSolid) | *(no implementado — candidato a lib_geometria.py)* |
| 3.2 Cortar con un plano (CutWithHalfSpace) | *(no implementado — candidato a lib_geometria.py)* |
| 3.2 Modificar sólido original con plano (CutWithHalfSpaceModifyingOriginalSolid) | *(no implementado — candidato a lib_geometria.py)* |
| 3.3 Combinación de geometrías (doc.CombineElements + CombinableElementArray) | *(no implementado — candidato a lib_familias.py)* |
| 4.1 Utilidades de corte (SolidSolidCutUtils — solo en proyecto) | *(no implementado — candidato a lib_geometria.py)* |
| 4.2 Utilidades de unión (JoinGeometryUtils.JoinGeometry + Unjoin + SwitchJoinOrder) | `lib_geometria.booleano_union()` |
| 4.3 Utilidades de sólidos (SolidUtils — Clone, CreateTransformed, TessellateSolidOrShell, SplitVolumes) | *(no implementado — candidato a lib_geometria.py)* |

---

## IV → V. DISEÑO CONCEPTUAL

### 1. Familia patrón de "Baldosa" (TilePattern)

| Sección | Función / módulo |
|---|---|
| Tipos de patrones (TilePatternsBuiltIn: Rectangle, Hexagon, Triangle, Octagon, Rhomboid, Arrows…) | *(no implementado — candidato a lib_familias.py)* |
| División horizontal y vertical (CurtainPanelHorizontalSpacing / VerticalSpacing) | *(no implementado — candidato a lib_familias.py)* |
| Obtener tipos de patrones (FEC por categoría OST_CurtainWallPanels) | *(no implementado — candidato a lib_familias.py)* |
| Patrón actual (FEC por OST_IOSTTilePatternGrid, GetTypeId) | *(no implementado — candidato a lib_familias.py)* |
| Cambiar Tile Pattern (LookupParameter("Tipo") + doc.Settings.TilePatterns.GetTilePattern) | *(no implementado — candidato a lib_familias.py)* |
| Propiedades de Patrón — espaciado U/V (BuiltInParameter) | *(no implementado — candidato a lib_familias.py)* |
| Obtener puntos adaptativos (FEC por OST_AdaptivePoints / OST_ReferencePoints) | *(no implementado — candidato a lib_familias.py)* |

### 2. Puntos adaptativos (ReferencePoint)

| Sección | Función / módulo |
|---|---|
| Crear puntos de referencia (doc.FamilyCreate.NewReferencePoint) | *(no implementado — candidato a lib_familias.py)* |
| Propiedades puntos referencia (CoordinatePlaneVisibility, Visible, POINT_ELEMENT_DRIVEN) | *(no implementado — candidato a lib_familias.py)* |
| Planos de referencia y sistema de coordenadas (GetCoordinatePlaneReferenceXY/YZ/XZ, GetCoordinateSystem) | *(no implementado — candidato a lib_familias.py)* |
| Mover puntos (ElementTransformUtils.MoveElement + SetCoordinateSystem + Transform) | `lib_transformaciones.mover_elemento()` |
| Transformaciones para puntos (CreateTranslation, CreateRotation, CreateRotationAtPoint, CreateReflection) | `lib_transformaciones.crear_transform_traslacion()`, `lib_transformaciones.crear_transform_rotacion()` |
| Buscar punto de referencia por coordenadas (IsAlmostEqualTo) | *(no implementado — candidato a lib_familias.py)* |

### 3. Líneas de Referencia (CurveByPoints)

| Sección | Función / módulo |
|---|---|
| Crear líneas entre dos puntos (doc.FamilyCreate.NewCurveByPoints + ReferencePointArray) | *(no implementado — candidato a lib_familias.py)* |
| Crear línea de referencia con varios puntos | *(no implementado — candidato a lib_familias.py)* |
| Propiedades de línea entre puntos (IsReferenceLine, ReferenceType, SketchPlane, Visible) | *(no implementado — candidato a lib_familias.py)* |
| Crear línea rotada (rotatarLineaEntrePuntos) | *(no implementado — candidato a lib_familias.py)* |

#### 3.1 Utilidades de CurveByPoints (CurveByPointsUtils)

| Sección | Función / módulo |
|---|---|
| Crear arco de referencia con tres puntos (CreateArcThroughPoints) | *(no implementado — candidato a lib_familias.py)* |
| Crear rectángulo mediante dos puntos (CreateRectangle + CurveProjectionType) | *(no implementado — candidato a lib_familias.py)* |
| Tipo de Proyección (FromTopDown, ParallelToLevel, FollowSurfaceUV) | *(conceptual — enumerado CurveProjectionType)* |
| Añadir curvas a región de cara (SetSketchOnSurface + AddCurvesToFaceRegion) | *(no implementado — candidato a lib_familias.py)* |
| Obtener regiones de caras (cara.HasRegions, cara.GetRegions) | *(no implementado — candidato a lib_familias.py)* |
| Obtener anfitrión de cara (CurveByPointsUtils.GetHostFace) | *(no implementado — candidato a lib_familias.py)* |
| Extruir región de cara (NewFormByThickenSingleFace / NewExtrusionForm) | *(no implementado — candidato a lib_familias.py)* |

#### 3.2 Puntos basados en línea (No anidados)

| Sección | Función / módulo |
|---|---|
| Dividir línea con puntos adaptativos (dividirLineaEntrePts, dividirLineaEntrePts2) | *(no implementado — candidato a lib_familias.py)* |
| Alinear puntos adaptativos con una línea (SetCoordinateSystem con Plane.XVec/YVec/Normal) | *(no implementado — candidato a lib_familias.py)* |

### 4. Anidar puntos adaptativos en elementos

| Tipo de anidamiento | Función / módulo |
|---|---|
| Punto anidado en punto (NewPointRelativeToPoint + SetPointElementReference) | *(no implementado — candidato a lib_familias.py)* |
| Punto anidado en curva (PointLocationOnCurve + NewPointOnEdge) | *(no implementado — candidato a lib_familias.py)* |
| Tipos de medición (PointOnCurveMeasurementType: Angle, ChordLength, NormalizedCurveParameter, SegmentLength…) | *(conceptual — enumerado del API)* |
| Crear puntos equidistantes sobre curva (dividirLineaPtsAnidados) | *(no implementado — candidato a lib_familias.py)* |
| Anidar puntos más cercanos entre dos curvas (puntosCercanosEntreLineas) | *(no implementado — candidato a lib_familias.py)* |
| Obtener puntos anidados en una curva (puntosEnLinea por FEC) | *(no implementado — candidato a lib_familias.py)* |
| Crear geometrías en puntos equidistantes (círculos en puntos de línea) | *(no implementado — candidato a lib_familias.py)* |
| Encaje de líneas entre puntos — Short, Long, Cross (lineasEntrePuntos + Lacing) | *(no implementado — candidato a lib_familias.py)* |
| Punto sobre arco o círculo (PointLocationOnCurve con tipo Angle) | *(no implementado — candidato a lib_familias.py)* |
| Punto sobre plano de referencia (NewPointOnPlane + GetCoordinatePlaneReferenceXY) | *(no implementado — candidato a lib_familias.py)* |
| Punto en intersección de cara y línea (NewPointOnEdgeFaceIntersection) | *(no implementado — candidato a lib_familias.py)* |

### 5. Geometrías adaptativas

#### 5.1 Líneas de modelo en diseño conceptual

| Tipo de geometría | Función / módulo |
|---|---|
| Crear círculo (Arc + SketchPlane + NewModelCurve) | `lib_geometria.crear_arco()` |
| Crear círculo anidado en punto de referencia (GetCoordinatePlaneReferenceYZ) | *(no implementado — candidato a lib_familias.py)* |
| Crear Rectángulo (CurveByPointsUtils.CreateRectangle) | *(no implementado — candidato a lib_familias.py)* |
| Crear Polígono Inscrito (CrearPoligonoInscrito) | *(no implementado — candidato a lib_geometria.py)* |
| Crear Polígono Circunscrito (CrearPoligonoCircunscrito) | *(no implementado — candidato a lib_geometria.py)* |
| Crear Arco por Inicio Fin Radio (crear_arco_por_inicio_fin_radio) | `lib_geometria.crear_arco()` |
| Crear Arco por Centro y extremos (crear_arco_por_centro_y_extremos) | `lib_geometria.crear_arco()` |
| Crear Arco por Tangente y punto final | *(no implementado — candidato a lib_geometria.py)* |
| Crear Arco de empalme | *(no implementado — candidato a lib_geometria.py)* |
| Crear Elipse (Ellipse.CreateCurve) | *(no implementado — candidato a lib_geometria.py)* |
| Crear Elipse Parcial (Ellipse.CreateCurve con start/end param) | *(no implementado — candidato a lib_geometria.py)* |
| Crear Spline a través de puntos (ReferencePointArray + NewCurveByPoints) | `lib_geometria.crear_nurbs_por_puntos()` |
| Sumar dos perímetros (shapely.ops.voronoi_diagram + polygonize + unary_union) | `lib_scientific.interseccion_shapely()` |

#### 5.2 Formas en diseño conceptual

| Tipo de forma | Función / módulo |
|---|---|
| Forma por extrusión Cilindro (NewExtrusionForm + ReferenceArray) | *(no implementado — candidato a lib_familias.py)* |
| Forma por extrusión prisma (CreaFormaExtruidaDesdePuntos) | *(no implementado — candidato a lib_familias.py)* |
| Forma por barrido (NewSweptBlendForm) | *(no implementado — candidato a lib_familias.py)* |
| Forma por barrido con varios perfiles (ReferenceArrayArray) | *(no implementado — candidato a lib_familias.py)* |
| Forma por solevado (NewLoftForm) | *(no implementado — candidato a lib_familias.py)* |
| Forma por revolución (NewRevolveForms) | *(no implementado — candidato a lib_familias.py)* |
| Forma por engrosado de superficie (NewFormByThickenSingleFace) | *(no implementado — candidato a lib_familias.py)* |
| Referencias de forma (get_Geometry + opt) | *(no implementado — candidato a lib_familias.py)* |
| Seleccionar Referencia Específica (getCurveLoopReferencesOnProfile) | *(no implementado — candidato a lib_familias.py)* |
| Propiedades Formas (IsInXRayMode, ProfileCount, PathCurveCount, Pinned, TopOffset/BaseOffset, AreProfilesConstrained) | *(no implementado — candidato a lib_familias.py)* |
| Parámetros BuiltIn formas (ELEM_CATEGORY_PARAM, LOCKED_TOP_OFFSET, MATERIAL_ID_PARAM…) | *(conceptual — ver libro)* |
| Proyectar perpendicular a plano (cara.Project) | *(no implementado — candidato a lib_familias.py)* |
| Proyectar punto a cara (NewPointOnEdgeFaceIntersection con rayos) | *(no implementado — candidato a lib_familias.py)* |

#### 5.3 Visibilidad de geometrías (FamilyElementVisibility)

| Sección | Función / módulo |
|---|---|
| GetVisibility / SetVisibility (IsShownInCoarse, Fine, LeftRight, PlanRCPCut…) | *(no implementado — candidato a lib_familias.py)* |

#### 5.4 Modificar formas

| Sección | Función / módulo |
|---|---|
| Añadir arista (AddEdge — 3 sobrecargas) | *(no implementado — candidato a lib_familias.py)* |
| Añadir perfil (AddProfile) | *(no implementado — candidato a lib_familias.py)* |
| Añadir perfiles (bucle AddProfile recalculando aristas) | *(no implementado — candidato a lib_familias.py)* |
| Modificar perfiles (MoveProfile, RotateProfile, ScaleProfile, CanManipulateProfile) | *(no implementado — candidato a lib_familias.py)* |
| Borrar perfil (DeleteProfile) | *(no implementado — candidato a lib_familias.py)* |
| Propiedades de aristas (AsCurve, Evaluate, GetEndPointReference, GetFace, Tessellate) | `lib_geometria.obtener_aristas_solido()` |
| Propiedades de caras (Area, EdgeLoops, HasRegions, IsTwoSided, MaterialElementId, Reference) | `lib_geometria.obtener_caras_solido()` |
| Métodos de caras (ComputeDerivatives, ComputeNormal, GetBoundingBoxUV, GetEdgesAsCurveLoops, Triangulate) | *(no implementado — candidato a lib_geometria.py)* |
| Rotar/Escalar subelemento (RotateSubElement, ScaleSubElement, MoveSubElement) | *(no implementado — candidato a lib_familias.py)* |
| Obtener líneas de perfiles (perfilesForma con iterador) | *(no implementado — candidato a lib_familias.py)* |
| Referencias perfiles (GetCurvesAndEdgesReferences, IsProfileEdge, GetProfileLoopAndReference) | *(no implementado — candidato a lib_familias.py)* |
| Agrupar elementos de perfiles (por posición en espacio) | *(no implementado — candidato a lib_familias.py)* |
| Obtener planos de perfiles (planoDePerfil, CurveLoop.GetPlane) | *(no implementado — candidato a lib_familias.py)* |
| Crear formas de secciones con plano (PerfilDelCorte + extrusionLineasEnPlano) | *(no implementado — candidato a lib_familias.py)* |

#### 5.5 Cortar geometría con plano

| Sección | Función / módulo |
|---|---|
| Mediante geometrías auxiliares (CrearPlanoSolidoDeRefPlane + BooleanOperationsUtils.Intersect) | `lib_geometria.booleano_interseccion()` |
| Mediante plano (BooleanOperationsUtils.CutWithHalfSpace) | *(no implementado — candidato a lib_geometria.py)* |
| Interpretación resultados (PerfilDelCorte — filtrar líneas en plano) | *(no implementado — candidato a lib_geometria.py)* |
| Corte de sólidos (CutWithHalfSpace aplicado a sólidos geométricos) | *(no implementado — candidato a lib_geometria.py)* |
| Cortes múltiples (cortarSolido recursivo) | *(no implementado — candidato a lib_geometria.py)* |
| Visualizaciones líneas (AsCurve().ToProtoType() de Edges) | *(no implementado — conversión a Dynamo)* |
| Calcular polígonos internos (shapely + Intersect(Face, Curve)) | `lib_scientific.interseccion_shapely()` |

#### 5.6 Calcular geometría cerrada (Complejo)

| Sección | Función / módulo |
|---|---|
| *(pendiente de desarrollo en el libro)* | *(no implementado — candidato a lib_geometria.py)* |

#### 5.7 Interceptor de referencias (ReferenceIntersector)

| Sección | Función / módulo |
|---|---|
| Crear interceptor — todos los elementos (ReferenceIntersector + Vista3D) | *(no implementado — candidato a lib_geometria.py)* |
| Crear interceptor — con filtro (ElementCategoryFilter + FindReferenceTarget) | *(no implementado — candidato a lib_geometria.py)* |
| FindReferenceTarget: Element, Mesh, Edge, Curve, Face, All | *(conceptual — enumerado del API)* |
| Crear interceptor — elementos específicos (por Id) | *(no implementado — candidato a lib_geometria.py)* |
| Intersecar elementos en vínculos (FindReferencesInRevitLinks = True) | *(no implementado — candidato a lib_geometria.py)* |
| Buscar la intersección más cercana (FindNearest + GetReference) | *(no implementado — candidato a lib_geometria.py)* |
| Buscar todas las intersecciones (Find) | *(no implementado — candidato a lib_geometria.py)* |

---

### 6. Subdividir elementos

#### 6.1 Camino dividido (DividedPath)

| Sección | Función / módulo |
|---|---|
| Dividir camino (DividedPath.Create + List[Reference]) | *(no implementado — candidato a lib_familias.py)* |
| Elemento de intersección (SetIntersectingElements con niveles) | *(no implementado — candidato a lib_familias.py)* |
| Definir cantidad de nodos (DIVIDEDPATH_LAYOUT) | *(no implementado — candidato a lib_familias.py)* |
| Separar referencias (SeparateReferencesIntoConnectedReferences) | *(no implementado — candidato a lib_familias.py)* |
| Repetir familia en camino dividido (ComponentRepeater.RepeatElements) | *(no implementado — candidato a lib_familias.py)* |
| Propiedades — SpacingRuleLayout, FixedNumberOfPoints, Distance, DividedPathMeasurementType, NumberOfPoints | *(no implementado — candidato a lib_familias.py)* |
| Obtener puntos de camino dividido (get_Geometry con ViewDetailLevel.Fine) | *(no implementado — candidato a lib_familias.py)* |

#### 6.2 Repetir elementos en Camino dividido

| Sección | Función / módulo |
|---|---|
| Obtener puntos de colocación (DividedPath.Create doble) | *(no implementado — candidato a lib_familias.py)* |
| Crear adaptativa (AdaptiveComponentInstanceUtils.CreateAdaptiveComponentInstance) | *(no implementado — candidato a lib_familias.py)* |
| Crear referencias de colocación (NewPointRelativeToPoint) | *(no implementado — candidato a lib_familias.py)* |
| Reposicionar familia (SetPointElementReference) | *(no implementado — candidato a lib_familias.py)* |
| Repetir elemento (ComponentRepeater.RepeatElements) | *(no implementado — candidato a lib_familias.py)* |
| Buscar elementos repetidos (FEC de ComponentRepeaterSlot) | *(no implementado — candidato a lib_familias.py)* |
| Eliminar slot (MakeEmpty) | *(no implementado — candidato a lib_familias.py)* |
| Aplicar familia por defecto (MakeDefault) | *(no implementado — candidato a lib_familias.py)* |
| Cambiar tipo en slot (FamilyType = sym.Id) | *(no implementado — candidato a lib_familias.py)* |
| Cambiar todas las familias (DefaultFamilyType) | *(no implementado — candidato a lib_familias.py)* |
| Eliminar repetidor (ComponentRepeater.RemoveRepeaters) | *(no implementado — candidato a lib_familias.py)* |

#### 6.3 Subdividir caras (DividedSurface)

| Sección | Función / módulo |
|---|---|
| Crear superficie dividida (DividedSurface.Create + USpacingRule) | *(no implementado — candidato a lib_familias.py)* |
| Obtener superficie dividida (GetReferencesWithDividedSurface + GetDividedSurfaceForReference) | *(no implementado — candidato a lib_familias.py)* |
| Cambiar patrón de Baldosa (ChangeTypeId + TilePatternsBuiltIn) | *(no implementado — candidato a lib_familias.py)* |
| Propiedades consulta (NumberOfUGridlines, NumberOfVGridlines, USpacingRule, VSpacingRule) | *(no implementado — candidato a lib_familias.py)* |
| Propiedades modificables (AllGridRotation, BorderTile, ComponentRotation, IsComponentFlipped/Mirrored, UPatternIndent, VPatternIndent) | *(no implementado — candidato a lib_familias.py)* |
| Métodos (GetAllIntersectionElements, IsSeedNode, GetGridNodeLocation/Reference/UV, GetGridSegment, GetTileFamilyInstance, GetTileReference, RemoveAllIntersectionElements) | *(no implementado — candidato a lib_familias.py)* |
| Parámetros BuiltIn de DividedSurface (grid_option, display_nodes, tile_pattern, pattern_mirror, surface_area…) | *(conceptual — ver libro)* |

#### 6.4 Repetir elementos en superficies divididas

| Sección | Función / módulo |
|---|---|
| Familias adaptativas de patrón de baldosa en superficie dividida | *(no implementado — candidato a lib_familias.py)* |

---

### 7. Utilidades de Familias Adaptativas

#### 7.1 Utilidades de componentes adaptativos (AdaptiveComponentFamilyUtils)

| Sección | Función / módulo |
|---|---|
| GetNumberOfAdaptivePoints, GetNumberOfPlacementPoints, GetNumberOfHandlePoints | *(no implementado — candidato a lib_familias.py)* |
| IsAdaptiveComponentFamily, IsAdaptivePlacementPoint, IsAdaptiveShapeHandle | *(no implementado — candidato a lib_familias.py)* |
| SetPlacementNumber, SetPointConstraintType, SetPointOrientationType, MakeAdaptivePoint | *(no implementado — candidato a lib_familias.py)* |
| Orientaciones: ToHost, ToHostAndLoopSystem, ToGlobalZthenHost, ToGlobalXYZ, ToInstanceZthenHost, ToInstance | *(conceptual — enumerado AdaptivePointOrientationType)* |

#### 7.2 Utilidades de instancias Adaptativas (AdaptiveComponentInstanceUtils)

| Sección | Función / módulo |
|---|---|
| CreateAdaptiveComponentInstance + GetInstancePlacementPointElementRefIds | *(no implementado — candidato a lib_familias.py)* |
| SetPointElementReference (recolocar en puntos, líneas, caras) | *(no implementado — candidato a lib_familias.py)* |
| GetInstancePlacementPointElementRefIds, GetInstanceShapeHandleElementRefIds | *(no implementado — candidato a lib_familias.py)* |
| HasAdaptivePoints, IsAdaptiveComponentInstance, IsInstanceFlippedFromHostFace | *(no implementado — candidato a lib_familias.py)* |
| SetInstanceFlippedFromHostFace, MoveAdaptiveComponentInstance (con Transform + desenlazar) | `lib_transformaciones.mover_elemento()` |

---

## V (IV) → CONTROL DE GEOMETRÍAS

### 1. Controlar geometrías mediante parámetros

#### 1.1 Cotas (Dimension)

| Sección | Función / módulo |
|---|---|
| Tipos de cotas — DimensionStyleType: Linear, Angular, Radial, Diameter, ArcLength, Elevation, Coordinates, Parallel, Slope | *(no implementado — candidato a lib_familias.py)* |
| Función estiloTipoDeCota(tipo) — buscar por StyleType | *(no implementado — candidato a lib_familias.py)* |

#### 1.2 Acotar elementos

| Sección | Función / módulo |
|---|---|
| Elementos acotables (ReferencePlane, ModelCurve, caras, aristas) | *(no implementado — candidato a lib_familias.py)* |
| Crear líneas base para cotas (linea_per_planos_paral_offset) | *(no implementado — candidato a lib_familias.py)* |
| Línea perpendicular a planos de referencia paralelos | *(no implementado — candidato a lib_familias.py)* |
| Arco entre planos (crear_arco_entre_planos para cotas angulares) | *(no implementado — candidato a lib_familias.py)* |
| Línea paralela a arco (crear_arco_paralelo para longitud de arco) | *(no implementado — candidato a lib_familias.py)* |
| Cota alineada (NewLinearDimension) | *(no implementado — candidato a lib_familias.py)* |
| Cota alineada múltiple (múltiples refs en ReferenceArray, AreSegmentsEqual) | *(no implementado — candidato a lib_familias.py)* |
| Cota angular (NewAngularDimension) | *(no implementado — candidato a lib_familias.py)* |
| Cota radial (NewRadialDimension) | *(no implementado — candidato a lib_familias.py)* |
| Cota de diámetro (NewDiameterDimension) | *(no implementado — candidato a lib_familias.py)* |
| Cota longitud de arco (NewArcLengthDimension) | *(no implementado — candidato a lib_familias.py)* |
| Obtener elementos acotados (cota.References → ElementId) | *(no implementado — candidato a lib_familias.py)* |

#### 1.3 Parámetros de familia

| Sección | Función / módulo |
|---|---|
| Listar parámetros del FamilyManager | `lib_parametros.obtener_parametros_familia_manager(doc)` |
| Crear parámetro local (AddParameter con GroupTypeId + SpecTypeId) | *(no implementado — candidato a lib_familias.py)* |
| Buscar parámetros (paramByName — GetParameters + Definition.Name) | `lib_familias.obtener_parametros_familia(symbol)` |
| Agregar parámetro compartido a familia | `lib_parametros.agregar_a_familia(doc, defn)` |
| Quitar parámetro de familia | `lib_parametros.quitar_de_familia(doc, nombre)` |
| Convertir parámetro local en compartido | `lib_parametros.convertir_local_a_compartido(doc, nombre_local, defn)` |
| Renombrar parámetro local | `lib_parametros.renombrar_parametro_familia(doc, nombre_actual, nombre_nuevo)` |
| Asignar fórmulas a parámetros (doc.FamilyManager.SetFormula) | *(no implementado — candidato a lib_familias.py)* |
| Anidar parámetros a propiedades (AssociateElementParameterToFamilyParameter) | *(no implementado — candidato a lib_familias.py)* |
| Aplicar parámetros a cota (cota.FamilyLabel = param) | *(no implementado — candidato a lib_familias.py)* |

#### 1.4 Parámetros compartidos (Shared Parameters)

| Sección | Función / módulo |
|---|---|
| Obtener ruta del .txt activo | `lib_parametros.obtener_ruta_archivo_compartidos(app)` |
| Apuntar / crear el archivo .txt | `lib_parametros.establecer_archivo_compartidos(app, ruta)` |
| Abrir DefinitionFile | `lib_parametros.abrir_archivo_compartidos(app)` |
| Ver contenido completo del .txt | `lib_parametros.listar_grupos_y_definiciones(def_file)` |
| Crear grupo en el .txt | `lib_parametros.crear_grupo(def_file, nombre)` |
| Obtener grupo existente | `lib_parametros.obtener_grupo(def_file, nombre)` |
| Crear definición Texto | `lib_parametros.crear_definicion_texto(grupo, nombre)` |
| Crear definición Entero | `lib_parametros.crear_definicion_entero(grupo, nombre)` |
| Crear definición Número | `lib_parametros.crear_definicion_numero(grupo, nombre)` |
| Crear definición Longitud | `lib_parametros.crear_definicion_longitud(grupo, nombre)` |
| Crear definición Área | `lib_parametros.crear_definicion_area(grupo, nombre)` |
| Crear definición Sí/No | `lib_parametros.crear_definicion_si_no(grupo, nombre)` |
| Crear definición (tipo genérico con SpecTypeId) | `lib_parametros.crear_definicion(grupo, nombre, SpecTypeId.*)` |
| Vincular al proyecto (BindingMap.Insert) | `lib_parametros.vincular_a_proyecto(doc, app, defn, lista_bic)` |
| Actualizar categorías de binding | `lib_parametros.actualizar_vinculo_proyecto(doc, app, defn, lista_bic)` |
| Desvincular del proyecto | `lib_parametros.desvincular_de_proyecto(doc, defn)` |
| Consultar si está vinculado | `lib_parametros.esta_vinculado_proyecto(doc, defn)` |
| Listar todos los compartidos del proyecto | `lib_parametros.obtener_parametros_compartidos_proyecto(doc)` |
| Buscar SharedParameterElement por GUID | `lib_parametros.buscar_por_guid(doc, guid_str)` |
| Obtener GUID de un parámetro | `lib_parametros.guid_de_parametro(doc, nombre)` |
| Flujo completo en una llamada | `lib_parametros.flujo_completo_compartido(app, doc, ruta, grupo, nombre, tipo, bics)` |

> **Nota sobre borrado del .txt:** La Revit API no expone métodos para eliminar
> un `DefinitionGroup` ni una `ExternalDefinition` del archivo. Para borrarlos
> hay que editar el .txt manualmente o reemplazarlo por uno nuevo.

### 2. Matrices de Objetos

| Sección | Función / módulo |
|---|---|
| 2.1 Matriz lineal no asociativa (LinearArray.ArrayElementsWithoutAssociation) | *(no implementado — candidato a lib_familias.py)* |
| 2.1 Matriz lineal asociativa (LinearArray.Create + IsElementArrayable) | *(no implementado — candidato a lib_familias.py)* |
| 2.1 Anidar parámetro a matriz (larr.Label = param, NumMembers) | *(no implementado — candidato a lib_familias.py)* |
| 2.1 Obtener elementos de matriz (GetCopiedElementIds, GetOriginalMembersIds) | *(no implementado — candidato a lib_familias.py)* |
| 2.2 Matriz radial no asociativa (RadialArray.ArrayElementsWithoutAssociation) | *(no implementado — candidato a lib_familias.py)* |
| 2.2 Matriz radial asociativa (RadialArray.Create + IsValidArraySize + IsRotationAngleValid) | *(no implementado — candidato a lib_familias.py)* |
| 2.2 Obtener elementos de matriz radial | *(no implementado — candidato a lib_familias.py)* |

### 3. Restricción de elementos

| Sección | Función / módulo |
|---|---|
| Anclar referencias (alinear_linea_a_plano + doc.FamilyCreate.NewAlignment) | *(no implementado — candidato a lib_familias.py)* |
| Bloquear objetos (elem.Pinned = True) | `lib_transformaciones.anclar_elemento(elem, anclar=True)` |
| Definir plano de trabajo (SKETCH_PLANE_PARAM) | *(no implementado — candidato a lib_familias.py)* |

---

## VI (V). ENTORNO DE REVIT

| Sección | Función / módulo |
|---|---|
| 1. Masa Conceptual — Crear Masas (no se puede desde la API) | *(no implementado — limitación del API)* |
| 1. Masa Conceptual — Crear formas (no disponible en entorno proyecto) | *(no implementado — solo en entorno familia)* |
| 1.3 Subdividir líneas en masa | *(no implementado — candidato a lib_familias.py)* |
| 1.4 Subdividir caras en masa | *(no implementado — candidato a lib_familias.py)* |
| 1.5 Sistemas de muro cortina | *(no implementado — candidato a lib_arquitectura.py)* |
| 2. Instancias de familias adaptativas en Proyecto (AdaptiveComponentInstanceUtils) | *(no implementado — candidato a lib_familias.py)* |
| 3. Muros por cara (FaceWall.Create + IsValidFaceReferenceForFaceWall) | *(no implementado — candidato a lib_arquitectura.py)* |
| 4. Análisis geométrico de elementos | *(no implementado — candidato a lib_geometria.py)* |
| 5. Armadura estructural | `lib_estructura.crear_armadura()` |

---

## VII (VI). Conectores de Dynamo — Data Exchange

| Sección | Función / módulo |
|---|---|
| AEC Data Model Nodes (GraphQL API para parámetros) | *(externo — Autodesk Data Connector for Dynamo)* |
| Data Exchange Nodes (ACC Docs, hub/project/exchange) | *(externo — Autodesk Data Connector for Dynamo)* |

---

## VIII (VII). Model Context Protocol (MCP) in Revit & Dynamo

| Sección | Función / módulo |
|---|---|
| Function Calling (LLM + tools JSON) | *(conceptual — integración IA)* |
| MCP Framework (Host, Client, Server) | *(conceptual — integración IA)* |
| Transporte — Stdio, Stream (HTTP), SSE | *(conceptual — integración IA)* |
| .NET MCP Framework — [McpServerToolType], [McpServerTool] | *(conceptual — C# AddIn, no Python/Dynamo)* |
| Bind Revit — JSON como interfaz de comandos (CreateWall, InsertWindowInWall…) | *(conceptual — integración IA via C#)* |

---

## IX (VIII). BIBLIOGRAFÍA / X (IX). ANEXOS

### Anexo 1. Funciones propias del manual

| Función | Función / módulo |
|---|---|
| convertidorUniComun(valor, unidad, toInternals) | `lib_general.pies_a_metros()`, `lib_general.metros_a_pies()`, `lib_general.mm_a_pies()` |
| parameterValue(parameter, valorComoTexto) | `lib_general.obtener_valor_parametro()` |
| elimPtsDuplicados(points, tolerance) | `lib_geometria.agrupar_puntos_por_proximidad()` |
| remove_duplicates_by_element_id(objects) | `lib_general.obtener_ids_int()` (IDs únicos) |
| SolidoDeSurface(geom) — extrae Solid de geometría | `lib_geometria.obtener_caras_solido()` |
| paramByName(name) — buscar parámetro por nombre | `lib_familias.obtener_parametros_familia()` |
| plt2arr(fig), convertToBitmap2(npImgArray) — matplotlib → Bitmap .NET | *(no implementado — candidato a lib_scientific.py)* |

### Anexo 2. Bibliotecas Python (resumen)

| Biblioteca | Función / módulo |
|---|---|
| NumPy | `lib_scientific.xyz_a_numpy()`, `lib_scientific.numpy_a_xyz()`, `lib_geometria.*_numpy()` |
| Pandas | `lib_scientific.elementos_a_dataframe()`, `lib_excel.leer_excel_pandas()` |
| Sympy | *(no implementado — candidato a lib_scientific.py)* |
| Shapely | `lib_scientific.poligono_shapely()`, `lib_scientific.interseccion_shapely()` |
| Scipy | `lib_scientific.calcular_estadisticas()` |
| scikit-spatial | *(no implementado — candidato a lib_scientific.py)* |
| Pygeos | *(no implementado — candidato a lib_scientific.py)* |
| Matplotlib | `lib_scientific.graficar_histograma()`, `lib_scientific.graficar_scatter()` |
| Vpython | *(no implementado — candidato a lib_scientific.py)* |
| Trimesh | *(no implementado — candidato a lib_scientific.py)* |
| Spherical-Coordinates | *(no implementado — candidato a lib_scientific.py)* |

### Anexo 3. Funciones incorporadas en Dynamo

| Función Python | Equivalente en biblioteca |
|---|---|
| all(lista) / any(lista) — todos/alguno verdadero | *(conceptual — Python nativo)* |
| in / not in — ContainsKey | *(conceptual — Python nativo)* |
| lista.count(x), len(lista) — CountFalse/CountTrue/Count | *(conceptual — Python nativo)* |
| lista.index(x) — IndexOf | *(conceptual — Python nativo)* |
| all(type(x) == type(a[0]) for x in a) — IsHomogeneous | *(conceptual — Python nativo)* |
| [sub for grupo in lista for sub in grupo] — Flatten | `lib_general.aplanar_lista(lista)` |

---

## Resumen de funcionalidades SIN implementar (candidatas a nuevos módulos)

| Categoría | Descripción | Módulo sugerido |
|---|---|---|
| Sólidos geométricos | CreateExtrusionGeometry, CreateBlendGeometry, CreateSweptGeometry, CreateLoftGeometry, CreateRevolvedGeometry sin DirectShape | `lib_geometria.py` ampliar |
| Operaciones sólidos | CutWithHalfSpace, SolidUtils.Clone/CreateTransformed/TessellateSolidOrShell | `lib_geometria.py` ampliar |
| Curvas avanzadas | Distancia punto a círculo, circle fit 3D, crear elipse, helicoide, desfase CurveLoop | `lib_geometria.py` ampliar |
| Transformaciones avanzadas | Transform1D, Transform2D, CreateRotationAtPoint, coordenadas cilíndricas/esféricas | `lib_transformaciones.py` ampliar |
| Proyecciones y análisis | Proyectar punto a plano (Plane.Project), ecuación del plano, BoundingBox girado | `lib_geometria.py` ampliar |
| Puntos adaptativos | Toda la sección IV.2–IV.4 (ReferencePoint, PointLocationOnCurve, CurveByPoints) | `lib_familias.py` ampliar |
| Formas en familias | NewExtrusion, NewRevolution, NewBlend, NewSweep, NewSweptBlend, NewExtrusionForm, NewLoftForm | `lib_familias.py` ampliar |
| Parámetros compartidos | ✅ **IMPLEMENTADO** — gestión completa del .txt, grupos, definiciones, bindings proyecto/familia | `lib_parametros.py` (nuevo) |
| Control de geometría | Cotas (NewLinearDimension, NewAngularDimension…), matrices (LinearArray, RadialArray), alineaciones | `lib_familias.py` ampliar |
| Subdivisión adaptativa | DividedPath, DividedSurface, ComponentRepeater, AdaptiveComponentInstanceUtils | `lib_familias.py` ampliar |
| Entorno de proyecto | FaceWall, Masa conceptual API, sistemas de muro cortina | `lib_arquitectura.py` ampliar |
| Colecciones | ModelCurveArray, DetailCurveArray, SymbolicCurveArray, FaceArray, FormArray | `lib_geometria.py` ampliar |
| Bibliotecas científicas | Sympy, scikit-spatial, Pygeos, Vpython, Trimesh, Spherical-Coordinates | `lib_scientific.py` ampliar |

---

*Generado 2026-05-28 — complementa INDICE_LIBRO.md (para "Más allá de Dynamo").*
*Este archivo indexa "Geometrías con la Revit API" (Kevin Himmelreich, no publicado).*
