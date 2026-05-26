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
| `lib_general.py` | Utilidades compartidas: unwrap, transacciones Dynamo, parametros, conversiones de unidades, colectores basicos |
| `lib_coordinacion.py` | Vistas, planos, niveles, worksets, links, fases, categorias, overrides graficos |
| `lib_arquitectura.py` | Muros, suelos, cubiertas, habitaciones, puertas, ventanas, escaleras, barandillas, areas |
| `lib_instalaciones.py` | Conductos, tuberias, bandejas, conduits, equipos MEP, luminarias, sanitarios, espacios |
| `lib_estructura.py` | Pilares, vigas, forjados, cimentaciones, armaduras, cargas estructurales |
| `lib_geometria.py` | Curvas, solidos (extrusion, blend, barrido, revolution), booleanas, DirectShape, A* pathfinding |
| `lib_vistas.py` | Vistas 3D, secciones, alzados, cartelas, rango de vista, escala, nivel de detalle, export imagen |
| `lib_familias.py` | Carga, exportacion, instanciacion y gestion de familias |
| `lib_cad.py` | Importacion y analisis de archivos CAD (DWG/DXF): capas, curvas, bloques |
| `lib_excel.py` | Lectura/escritura Excel via DSOffice (Dynamo) y COM Interop; export de schedules |
| `lib_bases_datos.py` | JSON, CSV, exportacion IFC, schedules a CSV, GUIDs |
| `lib_colaborativo.py` | Worksharing: activar colaborativo, guardar central, sincronizar, worksets |
| `lib_transacciones.py` | TransactionGroup, Transaction nativa, SubTransaction, ForceClose |
| `lib_seleccion_ui.py` | Seleccion interactiva: elemento, cara, arista, punto, rectangulo, link |
| `lib_completa.py` | Importa todo con `from lib_completa import *` |

## Uso basico en Dynamo

```python
import sys
sys.path.append(r"C:\ruta\a\RevitPythonLibrary")

# Importar un modulo concreto
from lib_general import pies_a_metros, obtener_valor_parametro

# O importar todo
from lib_completa import *

# Ejemplo: obtener todos los niveles
niveles = obtener_niveles()
OUT = [n.Name for n in niveles]
```

## Ejemplo: exportar parametros a Excel

```python
import sys
sys.path.append(r"C:\ruta\a\RevitPythonLibrary")
from lib_arquitectura import obtener_muros
from lib_excel import exportar_parametros_a_excel

muros = obtener_muros()
exportar_parametros_a_excel(
    elementos   = muros,
    nombres_params = ["Marca", "Comentarios", "Descripcion del tipo"],
    ruta_salida = r"C:\Proyecto\muros.xlsx",
    nombre_hoja = "Muros"
)
OUT = ["Exportacion completada"]
```

## Compatibilidad de unidades (Revit 2024+)

Todas las funciones de conversion usan `UnitTypeId` (nunca `DisplayUnitType`).
Los `ElementId` se convierten con la funcion `id_a_int()` que soporta `.Value` (Revit 2024+) y `.IntegerValue` (Revit <= 2023).

## Licencia

MIT — uso libre con atribucion a Kevin Himmelreich
