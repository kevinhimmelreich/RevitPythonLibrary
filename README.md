# RevitPythonLibrary

Biblioteca modular de funciones Python para Revit/Dynamo, organizada por disciplina.
Derivada y refactorizada a partir de `LibreriaFunciones.py` (Kevin Himmelreich).

## Requisitos

| Componente | Version |
|---|---|
| Autodesk Revit | 2024 – 2026 |
| Dynamo | 2.x o superior |
| Python (dentro de Dynamo) | IronPython 2.7 **o** CPython 3.x (Dynamo 2.13+) |

## Estructura

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
| `lib_excel.py` | Lectura/escritura Excel via DSOffice y COM Interop; pandas (CPython 3.x) |
| `lib_bases_datos.py` | JSON, CSV, exportacion IFC, schedules a CSV, GUIDs; pandas (CPython 3.x) |
| `lib_colaborativo.py` | Worksharing: activar colaborativo, guardar central, sincronizar, worksets |
| `lib_transacciones.py` | TransactionGroup, Transaction nativa, SubTransaction, ForceClose |
| `lib_seleccion_ui.py` | Seleccion interactiva: elemento, cara, arista, punto, rectangulo, link |
| `lib_scientific.py` | **Integracion Revit API con Python cientifico** (ver seccion) |
| `lib_completa.py` | Importa todos los modulos con `from lib_completa import *` |

## lib_scientific — Revit API + Python cientifico

Requiere **CPython 3.x (Dynamo 2.13+)**. En IronPython 2.7 todas las funciones
retornan `None` con un aviso. Cada libreria se importa de forma diferida
(`try/except ImportError`) para no bloquear la carga del modulo.

| Libreria | Funciones |
|---|---|
| **pandas** | `elementos_a_dataframe`, `dataframe_a_parametros`, `schedule_a_dataframe`, `analisis_calidad_datos` |
| **numpy** | `xyz_a_numpy`, `numpy_a_xyz`, `posiciones_elementos_numpy`, `centroide_nube` |
| **scipy** | `clustering_por_posicion`, `vecinos_por_radio`, `interpolacion_parametro` |
| **matplotlib** | `grafico_parametro_por_nivel`, `histograma_parametro`, `grafico_dispersion`, `grafico_suma_por_categoria` |
| **shapely** | `curvas_a_shapely`, `habitacion_a_shapely`, `detectar_solapamientos`, `buffer_habitacion` |
| **networkx** | `sistema_mep_a_grafo`, `analisis_red_mep`, `ruta_mas_corta_mep` |

### Ejemplo: QA/QC — elementos sin parametros obligatorios

```python
import sys
sys.path.append("C:/ruta/a/RevitPythonLibrary")
from lib_scientific import analisis_calidad_datos
from lib_arquitectura import obtener_muros

muros = obtener_muros()
incompletos = analisis_calidad_datos(
    muros, ["Marca", "Comentarios", "Descripcion del tipo"]
)
OUT = [incompletos]
```

### Ejemplo: clustering de equipos MEP por zona

```python
from lib_scientific import clustering_por_posicion
from lib_instalaciones import obtener_equipos_mecanicos

equipos = obtener_equipos_mecanicos()
zonas = clustering_por_posicion(equipos, n_grupos=4)
OUT = [[e.Id.IntegerValue for e in zona] for zona in zonas.values()]
```

### Ejemplo: grafico de areas por nivel

```python
from lib_scientific import grafico_parametro_por_nivel
from lib_arquitectura import obtener_habitaciones

habitaciones = obtener_habitaciones()
grafico_parametro_por_nivel(
    habitaciones, "Area",
    ruta_png="C:/Proyecto/areas_por_nivel.png",
    titulo="Area media por nivel"
)
```

### Ejemplo: analisis de red MEP

```python
from lib_scientific import sistema_mep_a_grafo, analisis_red_mep
from lib_instalaciones import obtener_tuberias

tuberias = obtener_tuberias()
grafo = sistema_mep_a_grafo(tuberias)
metricas = analisis_red_mep(grafo)
OUT = [metricas]
# {"nodos": 142, "aristas": 138, "grado_medio": 1.94, ...}
```

## Uso basico en Dynamo

```python
import sys
sys.path.append("C:/ruta/a/RevitPythonLibrary")

# Importar un modulo concreto
from lib_general import pies_a_metros, obtener_valor_parametro

# O importar todo (incluido lib_scientific)
from lib_completa import *

# Ejemplo: obtener todos los niveles
niveles = obtener_niveles()
OUT = [n.Name for n in niveles]
```

## Compatibilidad de unidades (Revit 2024+)

Todas las funciones de conversion usan `UnitTypeId` (nunca `DisplayUnitType`).
Los `ElementId` se convierten con `id_a_int()` que soporta `.Value` (Revit 2024+)
e `.IntegerValue` (Revit 2023 y anteriores).

## Licencia

MIT — uso libre - Kevin Himmelreich
