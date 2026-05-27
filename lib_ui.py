# -*- coding: utf-8 -*-
"""
lib_ui.py
Biblioteca de ventanas emergentes y dialogos WPF para Dynamo/Revit.
Basada en WPF (System.Windows) — compatible con Dynamo, que es WPF nativo.
Compatible: IronPython 2.7 | CPython 3.x | Revit 2024-2026
Repositorio: https://github.com/kevinhimmelreich/RevitPythonLibrary
"""

import clr
import sys

# ── Compatibilidad Python 2/3 ────────────────────────────────────────────────
PY3 = sys.version_info[0] >= 3
if PY3:
    string_types = (str,)
else:
    string_types = (str, unicode)  # noqa: F821

# ── WPF + .NET ───────────────────────────────────────────────────────────────
clr.AddReference("PresentationFramework")
clr.AddReference("PresentationCore")
clr.AddReference("WindowsBase")
clr.AddReference("System.Windows.Forms")   # para FolderBrowserDialog

from System.Windows import (                          # noqa: E402
    Window, MessageBox, MessageBoxButton,
    MessageBoxImage, MessageBoxResult,
    HorizontalAlignment, VerticalAlignment,
    Thickness, GridLength, SizeToContent,
    WindowStartupLocation
)
from System.Windows.Controls import (                 # noqa: E402
    StackPanel, DockPanel, Grid, ColumnDefinition,
    RowDefinition, Label, TextBox, Button, ComboBox,
    ComboBoxItem, ListBox, ListBoxItem, SelectionMode,
    CheckBox, ProgressBar, DataGrid, DataGridTextColumn,
    ScrollViewer, GroupBox, Separator, TextBlock
)
from System.Windows.Controls import Orientation       # noqa: E402
from System.Windows.Media import Brushes, SolidColorBrush, Color  # noqa: E402
from Microsoft.Win32 import OpenFileDialog, SaveFileDialog         # noqa: E402
from System.Windows.Forms import FolderBrowserDialog               # noqa: E402


# ── Estilo compartido ────────────────────────────────────────────────────────
_COLOR_ACENTO = "#2B579A"   # azul Revit/Office
_PADDING = Thickness(10)
_MARGEN = Thickness(5)


def _boton(texto, ancho=90):
    """Helper: crea un Button WPF con estilo basico."""
    btn = Button()
    btn.Content = texto
    btn.Width = ancho
    btn.Height = 30
    btn.Margin = Thickness(5)
    return btn


def _ventana(titulo, ancho=400, alto_auto=True):
    """Helper: crea una Window WPF centrada con estilo basico."""
    win = Window()
    win.Title = titulo
    win.Width = ancho
    win.WindowStartupLocation = WindowStartupLocation.CenterScreen
    win.ResizeMode = 2  # CanResizeWithGrip
    if alto_auto:
        win.SizeToContent = SizeToContent.Height
    win.Padding = _PADDING
    return win


# ── Dialogos simples ─────────────────────────────────────────────────────────

def mensaje(texto, titulo="Aviso", tipo="info"):
    """
    Muestra un cuadro de mensaje modal con icono segun el tipo.

    Args:
        texto: mensaje a mostrar
        titulo: titulo de la ventana (defecto "Aviso")
        tipo: "info", "advertencia", "error" o "pregunta"

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    iconos = {
        "info":        MessageBoxImage.Information,
        "advertencia": MessageBoxImage.Warning,
        "error":       MessageBoxImage.Error,
        "pregunta":    MessageBoxImage.Question,
    }
    icono = iconos.get(tipo, MessageBoxImage.Information)
    MessageBox.Show(texto, titulo, MessageBoxButton.OK, icono)


def confirmar(texto, titulo="Confirmar"):
    """
    Muestra un dialogo de confirmacion Si / No.

    Args:
        texto: pregunta a mostrar
        titulo: titulo de la ventana

    Returns:
        True si el usuario pulsa Si, False si pulsa No o cierra

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    res = MessageBox.Show(
        texto, titulo,
        MessageBoxButton.YesNo,
        MessageBoxImage.Question
    )
    return res == MessageBoxResult.Yes


def confirmar_cancelar(texto, titulo="Confirmar"):
    """
    Muestra un dialogo Si / No / Cancelar.

    Args:
        texto: pregunta a mostrar
        titulo: titulo de la ventana

    Returns:
        True (Si), False (No) o None (Cancelar / cerrar)

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    res = MessageBox.Show(
        texto, titulo,
        MessageBoxButton.YesNoCancel,
        MessageBoxImage.Question
    )
    if res == MessageBoxResult.Yes:
        return True
    if res == MessageBoxResult.No:
        return False
    return None


# ── Entrada de texto y numeros ───────────────────────────────────────────────

def pedir_texto(etiqueta, titulo="Entrada", valor_defecto=""):
    """
    Muestra un dialogo con un campo de texto libre.

    Args:
        etiqueta: texto descriptivo sobre el campo
        titulo: titulo de la ventana
        valor_defecto: texto inicial del campo

    Returns:
        str con el texto introducido, o None si el usuario cancela

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    resultado = [None]
    win = _ventana(titulo)

    panel = StackPanel()
    panel.Margin = _PADDING

    lbl = Label()
    lbl.Content = etiqueta
    panel.Children.Add(lbl)

    txt = TextBox()
    txt.Text = str(valor_defecto)
    txt.Margin = _MARGEN
    txt.Height = 26
    panel.Children.Add(txt)

    fila_botones = StackPanel()
    fila_botones.Orientation = Orientation.Horizontal
    fila_botones.HorizontalAlignment = HorizontalAlignment.Right
    fila_botones.Margin = Thickness(0, 8, 0, 0)

    btn_ok = _boton("Aceptar")
    btn_cancel = _boton("Cancelar")

    def ok(s, e):
        resultado[0] = txt.Text
        win.Close()

    def cancelar(s, e):
        win.Close()

    btn_ok.Click += ok
    btn_cancel.Click += cancelar
    fila_botones.Children.Add(btn_ok)
    fila_botones.Children.Add(btn_cancel)
    panel.Children.Add(fila_botones)

    win.Content = panel
    txt.Focus()
    win.ShowDialog()
    return resultado[0]


def pedir_numero(
        etiqueta, titulo="Entrada",
        valor_defecto=0.0, minimo=None, maximo=None, decimales=2):
    """
    Muestra un dialogo para introducir un valor numerico con validacion.

    Args:
        etiqueta: texto descriptivo sobre el campo
        titulo: titulo de la ventana
        valor_defecto: valor inicial
        minimo: valor minimo permitido (None = sin limite)
        maximo: valor maximo permitido (None = sin limite)
        decimales: numero de decimales permitidos (0 para enteros)

    Returns:
        float (o int si decimales=0) con el valor, o None si cancela

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    resultado = [None]
    win = _ventana(titulo)

    panel = StackPanel()
    panel.Margin = _PADDING

    lbl = Label()
    rango = ""
    if minimo is not None and maximo is not None:
        rango = " [{} – {}]".format(minimo, maximo)
    elif minimo is not None:
        rango = " (min {})".format(minimo)
    elif maximo is not None:
        rango = " (max {})".format(maximo)
    lbl.Content = etiqueta + rango
    panel.Children.Add(lbl)

    txt = TextBox()
    txt.Text = str(valor_defecto)
    txt.Margin = _MARGEN
    txt.Height = 26
    panel.Children.Add(txt)

    aviso = Label()
    aviso.Foreground = Brushes.Red
    aviso.Content = ""
    panel.Children.Add(aviso)

    fila_botones = StackPanel()
    fila_botones.Orientation = Orientation.Horizontal
    fila_botones.HorizontalAlignment = HorizontalAlignment.Right

    btn_ok = _boton("Aceptar")
    btn_cancel = _boton("Cancelar")

    def ok(s, e):
        try:
            v = float(txt.Text.replace(",", "."))
            if minimo is not None and v < minimo:
                aviso.Content = "El valor debe ser >= {}".format(minimo)
                return
            if maximo is not None and v > maximo:
                aviso.Content = "El valor debe ser <= {}".format(maximo)
                return
            resultado[0] = int(v) if decimales == 0 else round(v, decimales)
            win.Close()
        except ValueError:
            aviso.Content = "Introduce un numero valido."

    def cancelar(s, e):
        win.Close()

    btn_ok.Click += ok
    btn_cancel.Click += cancelar
    fila_botones.Children.Add(btn_ok)
    fila_botones.Children.Add(btn_cancel)
    panel.Children.Add(fila_botones)

    win.Content = panel
    txt.Focus()
    win.ShowDialog()
    return resultado[0]


# ── Seleccion de opciones ─────────────────────────────────────────────────────

def seleccionar_opcion(opciones, etiqueta="Selecciona una opcion",
                       titulo="Seleccion", valor_defecto=None):
    """
    Muestra un desplegable con las opciones dadas.

    Args:
        opciones: lista de strings con las opciones
        etiqueta: texto descriptivo sobre el desplegable
        titulo: titulo de la ventana
        valor_defecto: opcion seleccionada por defecto

    Returns:
        str con la opcion seleccionada, o None si cancela

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not opciones:
        return None
    resultado = [None]
    win = _ventana(titulo)

    panel = StackPanel()
    panel.Margin = _PADDING

    lbl = Label()
    lbl.Content = etiqueta
    panel.Children.Add(lbl)

    combo = ComboBox()
    combo.Margin = _MARGEN
    combo.Height = 26
    for op in opciones:
        combo.Items.Add(str(op))
    if valor_defecto and str(valor_defecto) in [str(o) for o in opciones]:
        combo.SelectedItem = str(valor_defecto)
    else:
        combo.SelectedIndex = 0
    panel.Children.Add(combo)

    fila_botones = StackPanel()
    fila_botones.Orientation = Orientation.Horizontal
    fila_botones.HorizontalAlignment = HorizontalAlignment.Right
    fila_botones.Margin = Thickness(0, 8, 0, 0)

    btn_ok = _boton("Aceptar")
    btn_cancel = _boton("Cancelar")

    def ok(s, e):
        resultado[0] = combo.SelectedItem
        win.Close()

    def cancelar(s, e):
        win.Close()

    btn_ok.Click += ok
    btn_cancel.Click += cancelar
    fila_botones.Children.Add(btn_ok)
    fila_botones.Children.Add(btn_cancel)
    panel.Children.Add(fila_botones)

    win.Content = panel
    win.ShowDialog()
    return resultado[0]


def seleccionar_multiples(opciones, etiqueta="Selecciona opciones",
                          titulo="Seleccion multiple",
                          seleccionados_defecto=None):
    """
    Muestra una lista con seleccion multiple mediante checkboxes.

    Args:
        opciones: lista de strings con las opciones
        etiqueta: texto descriptivo
        titulo: titulo de la ventana
        seleccionados_defecto: lista de opciones pre-seleccionadas

    Returns:
        lista de strings seleccionados, o None si cancela

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not opciones:
        return None
    seleccionados_defecto = seleccionados_defecto or []
    resultado = [None]
    win = _ventana(titulo)

    panel = StackPanel()
    panel.Margin = _PADDING

    lbl = Label()
    lbl.Content = etiqueta
    panel.Children.Add(lbl)

    scroll = ScrollViewer()
    scroll.MaxHeight = 300
    scroll.Margin = _MARGEN

    lista_panel = StackPanel()
    checks = []
    for op in opciones:
        cb = CheckBox()
        cb.Content = str(op)
        cb.Margin = Thickness(2)
        cb.IsChecked = str(op) in [str(s) for s in seleccionados_defecto]
        lista_panel.Children.Add(cb)
        checks.append(cb)

    scroll.Content = lista_panel
    panel.Children.Add(scroll)

    fila_botones = StackPanel()
    fila_botones.Orientation = Orientation.Horizontal
    fila_botones.HorizontalAlignment = HorizontalAlignment.Right
    fila_botones.Margin = Thickness(0, 8, 0, 0)

    btn_ok = _boton("Aceptar")
    btn_cancel = _boton("Cancelar")

    def ok(s, e):
        resultado[0] = [
            str(cb.Content) for cb in checks if cb.IsChecked
        ]
        win.Close()

    def cancelar(s, e):
        win.Close()

    btn_ok.Click += ok
    btn_cancel.Click += cancelar
    fila_botones.Children.Add(btn_ok)
    fila_botones.Children.Add(btn_cancel)
    panel.Children.Add(fila_botones)

    win.Content = panel
    win.ShowDialog()
    return resultado[0]


# ── Formularios ───────────────────────────────────────────────────────────────

def formulario(campos, titulo="Formulario"):
    """
    Genera un formulario dinamico con un campo de texto por entrada.
    Ideal para recoger varios parametros en un solo dialogo.

    Args:
        campos: dict {nombre_campo: valor_defecto} o lista de tuplas
                [(nombre, valor_defecto), ...]
                Los valores pueden ser str, int o float.

    Returns:
        dict {nombre_campo: valor_str} con los valores introducidos,
        o None si el usuario cancela

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if isinstance(campos, dict):
        items = list(campos.items())
    else:
        items = list(campos)

    resultado = [None]
    win = _ventana(titulo, ancho=420)

    grid = Grid()
    grid.Margin = _PADDING
    grid.ColumnDefinitions.Add(ColumnDefinition())
    grid.ColumnDefinitions.Add(ColumnDefinition())

    textboxes = {}
    for i, (nombre, defecto) in enumerate(items):
        grid.RowDefinitions.Add(RowDefinition())

        lbl = Label()
        lbl.Content = str(nombre) + ":"
        lbl.VerticalAlignment = VerticalAlignment.Center
        Grid.SetRow(lbl, i)
        Grid.SetColumn(lbl, 0)
        grid.Children.Add(lbl)

        txt = TextBox()
        txt.Text = str(defecto) if defecto is not None else ""
        txt.Margin = _MARGEN
        txt.Height = 26
        Grid.SetRow(txt, i)
        Grid.SetColumn(txt, 1)
        grid.Children.Add(txt)
        textboxes[nombre] = txt

    # Fila de botones
    grid.RowDefinitions.Add(RowDefinition())
    fila_botones = StackPanel()
    fila_botones.Orientation = Orientation.Horizontal
    fila_botones.HorizontalAlignment = HorizontalAlignment.Right
    fila_botones.Margin = Thickness(0, 10, 0, 0)

    btn_ok = _boton("Aceptar")
    btn_cancel = _boton("Cancelar")

    def ok(s, e):
        resultado[0] = {k: v.Text for k, v in textboxes.items()}
        win.Close()

    def cancelar(s, e):
        win.Close()

    btn_ok.Click += ok
    btn_cancel.Click += cancelar
    fila_botones.Children.Add(btn_ok)
    fila_botones.Children.Add(btn_cancel)
    Grid.SetRow(fila_botones, len(items))
    Grid.SetColumnSpan(fila_botones, 2)
    grid.Children.Add(fila_botones)

    win.Content = grid
    win.ShowDialog()
    return resultado[0]


# ── Seleccion de archivos y carpetas ─────────────────────────────────────────

def pedir_archivo(
        filtro="Todos los archivos (*.*)|*.*",
        titulo="Seleccionar archivo",
        carpeta_inicial=None):
    """
    Muestra el dialogo estandar de apertura de archivo de Windows.

    Args:
        filtro: filtro de tipos, formato "Descripcion (*.ext)|*.ext"
                Ejemplos: "Excel (*.xlsx)|*.xlsx|CSV (*.csv)|*.csv"
        titulo: titulo del dialogo
        carpeta_inicial: ruta de carpeta de inicio (opcional)

    Returns:
        str con la ruta del archivo seleccionado, o None si cancela

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    dlg = OpenFileDialog()
    dlg.Title = titulo
    dlg.Filter = filtro
    if carpeta_inicial:
        dlg.InitialDirectory = carpeta_inicial
    if dlg.ShowDialog():
        return dlg.FileName
    return None


def pedir_archivos_multiples(
        filtro="Todos los archivos (*.*)|*.*",
        titulo="Seleccionar archivos"):
    """
    Muestra el dialogo de apertura con seleccion multiple de archivos.

    Args:
        filtro: filtro de tipos
        titulo: titulo del dialogo

    Returns:
        lista de rutas seleccionadas, o None si cancela

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    dlg = OpenFileDialog()
    dlg.Title = titulo
    dlg.Filter = filtro
    dlg.Multiselect = True
    if dlg.ShowDialog():
        return list(dlg.FileNames)
    return None


def pedir_ruta_guardar(
        filtro="Todos los archivos (*.*)|*.*",
        titulo="Guardar como",
        nombre_defecto="",
        carpeta_inicial=None):
    """
    Muestra el dialogo estandar de guardar archivo de Windows.

    Args:
        filtro: filtro de tipos
        titulo: titulo del dialogo
        nombre_defecto: nombre de archivo sugerido
        carpeta_inicial: ruta de carpeta de inicio (opcional)

    Returns:
        str con la ruta elegida, o None si cancela

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    dlg = SaveFileDialog()
    dlg.Title = titulo
    dlg.Filter = filtro
    dlg.FileName = nombre_defecto
    if carpeta_inicial:
        dlg.InitialDirectory = carpeta_inicial
    if dlg.ShowDialog():
        return dlg.FileName
    return None


def pedir_carpeta(titulo="Seleccionar carpeta", carpeta_inicial=None):
    """
    Muestra el dialogo de seleccion de carpeta de Windows.

    Args:
        titulo: descripcion mostrada en el dialogo
        carpeta_inicial: ruta de inicio (opcional)

    Returns:
        str con la ruta de la carpeta seleccionada, o None si cancela

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    dlg = FolderBrowserDialog()
    dlg.Description = titulo
    if carpeta_inicial:
        dlg.SelectedPath = carpeta_inicial
    result = dlg.ShowDialog()
    # System.Windows.Forms.DialogResult.OK == 1
    if int(result) == 1:
        return dlg.SelectedPath
    return None


# ── Visualizacion de datos ────────────────────────────────────────────────────

def mostrar_tabla(datos, columnas=None, titulo="Resultados"):
    """
    Muestra una tabla de datos en una ventana WPF con DataGrid.
    Util para mostrar resultados de analisis o listados de elementos.

    Args:
        datos: lista de dicts o lista de listas con los datos
        columnas: lista de nombres de columna (si datos son listas)
                  Si datos son dicts, se infieren de las claves
        titulo: titulo de la ventana

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    win = _ventana(titulo, ancho=700, alto_auto=False)
    win.Height = 500
    win.SizeToContent = SizeToContent.Manual

    # Normalizar datos a lista de dicts
    if datos and isinstance(datos[0], dict):
        filas = datos
        cols = columnas or list(datos[0].keys())
    elif datos and isinstance(datos[0], (list, tuple)):
        cols = columnas or [
            "Col{}".format(i) for i in range(len(datos[0]))
        ]
        filas = [dict(zip(cols, fila)) for fila in datos]
    else:
        filas = []
        cols = columnas or []

    grid = DataGrid()
    grid.AutoGenerateColumns = False
    grid.IsReadOnly = True
    grid.Margin = _MARGEN

    for col_nombre in cols:
        col = DataGridTextColumn()
        col.Header = col_nombre
        col.Binding = clr.Reference[object]  # placeholder
        # Binding via code-behind no es directo en IronPython;
        # usamos ItemsSource con diccionarios y AutoGenerateColumns
        grid.Columns.Add(col)

    # Con dicts, AutoGenerateColumns es mas sencillo
    grid.AutoGenerateColumns = True
    grid.ItemsSource = filas

    panel = DockPanel()
    DockPanel.SetDock(grid, 4)  # Fill
    panel.Children.Add(grid)

    win.Content = panel
    win.ShowDialog()


def mostrar_lista(elementos, titulo="Lista", etiqueta=None):
    """
    Muestra una lista de elementos en una ventana scrollable de solo lectura.

    Args:
        elementos: lista de strings a mostrar
        titulo: titulo de la ventana
        etiqueta: texto descriptivo encima de la lista (opcional)

    Returns:
        None

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    win = _ventana(titulo, ancho=500, alto_auto=False)
    win.Height = 450

    panel = StackPanel()
    panel.Margin = _PADDING

    if etiqueta:
        lbl = Label()
        lbl.Content = etiqueta
        panel.Children.Add(lbl)

    scroll = ScrollViewer()
    scroll.Height = 350
    scroll.Margin = _MARGEN

    lista = ListBox()
    for elem in elementos:
        lista.Items.Add(str(elem))

    scroll.Content = lista
    panel.Children.Add(scroll)

    btn_cerrar = _boton("Cerrar", ancho=90)
    btn_cerrar.HorizontalAlignment = HorizontalAlignment.Right

    def cerrar(s, e):
        win.Close()

    btn_cerrar.Click += cerrar
    panel.Children.Add(btn_cerrar)

    win.Content = panel
    win.ShowDialog()


# ── Barra de progreso ─────────────────────────────────────────────────────────

def con_progreso(elementos, funcion, titulo="Procesando...",
                 etiqueta="Procesando elemento {i} de {total}..."):
    """
    Ejecuta una funcion sobre cada elemento mostrando una barra de progreso.
    La ventana se cierra automaticamente al finalizar.

    Args:
        elementos: lista de elementos a procesar
        funcion: callable(elemento, indice) que procesa cada elemento
        titulo: titulo de la ventana de progreso
        etiqueta: plantilla del mensaje. Usa {i} para el indice (1-based)
                  y {total} para el total.

    Returns:
        lista con los resultados de funcion(elemento, indice),
        o None si la lista esta vacia

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    if not elementos:
        return None
    total = len(elementos)
    resultados = []

    win = Window()
    win.Title = titulo
    win.Width = 450
    win.Height = 130
    win.ResizeMode = 0  # NoResize
    win.WindowStartupLocation = WindowStartupLocation.CenterScreen

    panel = StackPanel()
    panel.Margin = _PADDING

    lbl = Label()
    lbl.Content = etiqueta.format(i=1, total=total)
    panel.Children.Add(lbl)

    barra = ProgressBar()
    barra.Minimum = 0
    barra.Maximum = total
    barra.Value = 0
    barra.Height = 22
    barra.Margin = _MARGEN
    panel.Children.Add(barra)

    win.Content = panel

    # Procesamos elemento a elemento actualizando la UI
    # (ShowDialog bloquearia; usamos Show + Dispatcher)
    from System.Windows.Threading import (
        Dispatcher, DispatcherPriority
    )

    win.Show()
    dispatcher = win.Dispatcher

    for i, elem in enumerate(elementos):
        idx = i + 1
        res = funcion(elem, i)
        resultados.append(res)

        def actualizar(idx=idx, total=total):
            barra.Value = idx
            lbl.Content = etiqueta.format(i=idx, total=total)

        dispatcher.Invoke(
            actualizar, DispatcherPriority.Background
        )

    win.Close()
    return resultados


# ── Dialogo de parametros Revit ───────────────────────────────────────────────

def seleccionar_parametros(nombres_params, titulo="Seleccionar parametros",
                           seleccionados_defecto=None):
    """
    Dialogo especializado para seleccionar parametros de Revit de una lista.
    Alias semantico de seleccionar_multiples para mayor legibilidad.

    Args:
        nombres_params: lista de nombres de parametros disponibles
        titulo: titulo de la ventana
        seleccionados_defecto: lista de parametros pre-seleccionados

    Returns:
        lista de nombres de parametros seleccionados, o None si cancela

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    return seleccionar_multiples(
        nombres_params,
        etiqueta="Selecciona los parametros:",
        titulo=titulo,
        seleccionados_defecto=seleccionados_defecto
    )


def seleccionar_niveles(doc, titulo="Seleccionar niveles",
                        multiples=True):
    """
    Muestra los niveles del documento Revit para que el usuario seleccione.

    Args:
        doc: documento Revit activo
        titulo: titulo de la ventana
        multiples: True para seleccion multiple, False para una sola opcion

    Returns:
        lista de elementos Level seleccionados, o None si cancela

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    clr.AddReference("RevitAPI")
    from Autodesk.Revit.DB import FilteredElementCollector, Level
    niveles = list(
        FilteredElementCollector(doc)
        .OfClass(Level)
        .ToElements()
    )
    if not niveles:
        mensaje("No hay niveles en el documento.", tipo="advertencia")
        return None
    nombres = [n.Name for n in niveles]
    mapa = {n.Name: n for n in niveles}

    if multiples:
        seleccion = seleccionar_multiples(nombres, titulo=titulo)
        if seleccion is None:
            return None
        return [mapa[n] for n in seleccion if n in mapa]
    else:
        seleccion = seleccionar_opcion(nombres, titulo=titulo)
        if seleccion is None:
            return None
        return mapa.get(seleccion)


def seleccionar_categorias(doc, titulo="Seleccionar categorias",
                           multiples=True):
    """
    Muestra las categorias de modelo del documento para que el usuario elija.

    Args:
        doc: documento Revit activo
        titulo: titulo de la ventana
        multiples: True para seleccion multiple, False para una sola opcion

    Returns:
        lista de nombres de categorias seleccionadas, o None si cancela

    Revit: 2024-2026 | IronPython 2.7 + CPython 3.x
    """
    clr.AddReference("RevitAPI")
    from Autodesk.Revit.DB import Category, CategoryType
    cats = [
        c for c in doc.Settings.Categories
        if c.CategoryType == CategoryType.Model
    ]
    nombres = sorted([c.Name for c in cats])

    if multiples:
        return seleccionar_multiples(nombres, titulo=titulo)
    else:
        return seleccionar_opcion(nombres, titulo=titulo)
