import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import colorsys
import os
import math

class LEDScreenTestGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Imágenes de Test para Pantallas LED")
        self.root.geometry("700x600")
        # Diccionario para los botones de la cuadrícula de asignación
        self.grid_buttons = {}
        
        # Variables
        self.canvas_width = tk.StringVar(value="2560")
        self.canvas_height = tk.StringVar(value="1152")
        self.columns = tk.StringVar(value="20")
        self.rows = tk.StringVar(value="5")
        self.cell_width = tk.StringVar(value="128")
        self.show_numbers = tk.BooleanVar(value=True)
        self.show_grid = tk.BooleanVar(value=True)
        self.color_scheme = tk.StringVar(value="test_card")
        
        # Variables para texto central
        self.center_text_line1 = tk.StringVar(value="2560*1152")
        self.center_text_line2 = tk.StringVar(value="MAIN")
        self.show_center_text = tk.BooleanVar(value=True)

        # Variables para lógica NovaLCT: lado de inicio y patrón
        self.start_side = tk.StringVar(value="izquierda")  # izquierda, derecha, arriba, abajo
        self.pattern = tk.StringVar(value="lineal")  # lineal, serpentina
        
        # Lista para almacenar StringVars de altura de cada fila
        self.row_height_vars = []
        self.row_height_entries = []
        
        # Sistema de asignación de puertos
        self.port_assignments = {}  # {(col, row): {'main': (card, port), 'backup': (card, port)}}
        self.assignment_mode = tk.StringVar(value="main")  # "main" o "backup"
        self.selected_card = tk.StringVar(value="1")
        self.selected_port = tk.StringVar(value="1")
        self.assignment_panel_visible = tk.BooleanVar(value=True)

        # Configuración de cableado
        self.modules_per_port = tk.StringVar(value="10")  # Módulos por puerto
        self.cable_direction = tk.StringVar(value="horizontal")  # "horizontal" o "vertical"
        
        self.setup_ui()
        self.update_row_heights()
        # Forzar creación y visualización de la cuadrícula de asignación al final de la inicialización
        self.create_assignment_grid()
        
    def setup_ui(self):
        # Crear canvas y scrollbar para scroll
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configurar el scroll
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel para scroll con rueda del ratón
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _on_key_press(event):
            """Manejar scroll con teclas de dirección"""
            if event.keysym == 'Up':
                canvas.yview_scroll(-1, "units")
            elif event.keysym == 'Down':
                canvas.yview_scroll(1, "units")
            elif event.keysym == 'Prior':  # Page Up
                canvas.yview_scroll(-5, "units")
            elif event.keysym == 'Next':   # Page Down
                canvas.yview_scroll(5, "units")
        
        def bind_mousewheel(widget):
            """Vincula el scroll del mouse a un widget"""
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel(child)
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        canvas.bind("<Key>", _on_key_press)
        canvas.focus_set()  # Permitir que el canvas reciba eventos de teclado
        
        # Aplicar scroll a todos los widgets después de crear la interfaz
        self.root.after(100, lambda: bind_mousewheel(scrollable_frame))
        
        # Guardar referencia al canvas para uso posterior
        self.main_canvas = canvas
        
        # Frame principal dentro del scrollable_frame
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Generador de Imágenes de Test para Pantallas LED", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 20))
        

        # Frame de configuración (ocupa todo el ancho)
        config_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="10")
        config_frame.pack(fill=tk.X, expand=True, pady=(0, 10))


        # Panel de asignación de puertos (ocupa todo el ancho)
        self.assignment_frame = ttk.LabelFrame(main_frame, text="Asignación de Puertos Main/Backup", padding="10")
        self.assignment_panel_visible.set(True)
        self.setup_assignment_panel()
        # Toggle para mostrar/ocultar el panel de asignación
        assignment_toggle_frame = ttk.Frame(main_frame)
        assignment_toggle_frame.pack(fill=tk.X, pady=(0, 0))
        self.assignment_toggle_btn = ttk.Button(
            assignment_toggle_frame,
            text="▲ Ocultar Asignación de Puertos",
            command=self.toggle_assignment_panel
        )
        self.assignment_toggle_btn.pack(anchor=tk.W)
        # Empaquetar el panel de asignación de inmediato
        self.assignment_frame.pack(fill=tk.X, expand=True, pady=(0, 10))
        
        # Configuración del canvas
        canvas_frame = ttk.Frame(config_frame)
        canvas_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(canvas_frame, text="Tamaño total (píxeles):").pack(anchor=tk.W)
        size_frame = ttk.Frame(canvas_frame)
        size_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(size_frame, text="Ancho:").pack(side=tk.LEFT)
        ttk.Entry(size_frame, textvariable=self.canvas_width, width=10).pack(side=tk.LEFT, padx=(5, 15))
        ttk.Label(size_frame, text="Alto:").pack(side=tk.LEFT)
        ttk.Entry(size_frame, textvariable=self.canvas_height, width=10).pack(side=tk.LEFT, padx=(5, 0))
        
        # Configuración de la cuadrícula
        grid_frame = ttk.Frame(config_frame)
        grid_frame.pack(fill=tk.X, pady=(0, 10), expand=True)

        ttk.Label(grid_frame, text="Configuración de cuadrícula:").pack(anchor=tk.W)

        grid_config_frame = ttk.Frame(grid_frame)
        grid_config_frame.pack(fill=tk.X, pady=(5, 0), expand=True)

        ttk.Label(grid_config_frame, text="Columnas:").pack(side=tk.LEFT)
        ttk.Entry(grid_config_frame, textvariable=self.columns, width=8).pack(side=tk.LEFT, padx=(5, 15))
        ttk.Label(grid_config_frame, text="Filas:").pack(side=tk.LEFT)
        rows_entry = ttk.Entry(grid_config_frame, textvariable=self.rows, width=8)
        rows_entry.pack(side=tk.LEFT, padx=(5, 15))
        rows_entry.bind('<KeyRelease>', self.on_rows_change)

        ttk.Label(grid_config_frame, text="Ancho celda:").pack(side=tk.LEFT)
        ttk.Entry(grid_config_frame, textvariable=self.cell_width, width=8).pack(side=tk.LEFT, padx=(5, 15))

        # Selector de lado de inicio y patrón
        ttk.Label(grid_config_frame, text="Lado inicio:").pack(side=tk.LEFT, padx=(10, 0))
        start_side_combo = ttk.Combobox(grid_config_frame, textvariable=self.start_side, width=10, state="readonly")
        start_side_combo['values'] = ("izquierda", "derecha", "arriba", "abajo")
        start_side_combo.pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(grid_config_frame, text="Patrón:").pack(side=tk.LEFT)
        pattern_combo = ttk.Combobox(grid_config_frame, textvariable=self.pattern, width=10, state="readonly")
        pattern_combo['values'] = ("lineal", "serpentina")
        pattern_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Frame para altura de filas individuales
        self.rows_frame = ttk.LabelFrame(config_frame, text="Altura de cada fila (píxeles)", padding="10")
        self.rows_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Frame para texto central
        text_frame = ttk.LabelFrame(config_frame, text="Texto Central", padding="10")
        text_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Checkbutton(text_frame, text="Mostrar texto central", variable=self.show_center_text).pack(anchor=tk.W)
        
        text_inputs_frame = ttk.Frame(text_frame)
        text_inputs_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(text_inputs_frame, text="Línea 1:").pack(anchor=tk.W)
        ttk.Entry(text_inputs_frame, textvariable=self.center_text_line1, width=30).pack(fill=tk.X, pady=(2, 5))
        ttk.Label(text_inputs_frame, text="Línea 2:").pack(anchor=tk.W)
        ttk.Entry(text_inputs_frame, textvariable=self.center_text_line2, width=30).pack(fill=tk.X, pady=(2, 0))
        
        # Esquema de colores
        color_frame = ttk.Frame(config_frame)
        color_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(color_frame, text="Esquema de colores:").pack(side=tk.LEFT)
        color_combo = ttk.Combobox(color_frame, textvariable=self.color_scheme, width=15)
        color_combo['values'] = ('test_card', 'rainbow', 'primary_colors', 'gradient')
        color_combo.pack(side=tk.LEFT, padx=(5, 0))
        

        # El botón de toggle ya está configurado arriba
        # El assignment_frame ya está empacado arriba
        # El texto del botón ya está configurado arriba

    # Eliminada función show_assignment_panel_on_start porque ya no es necesaria
        
        # Opciones
        options_frame = ttk.Frame(config_frame)
        options_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Checkbutton(options_frame, text="Mostrar números", variable=self.show_numbers).pack(side=tk.LEFT)
        ttk.Checkbutton(options_frame, text="Mostrar líneas de cuadrícula", variable=self.show_grid).pack(side=tk.LEFT, padx=(20, 0))
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, expand=True, pady=(10, 0))
        
        ttk.Button(button_frame, text="Calcular dimensiones automáticamente", 
                  command=self.auto_calculate).pack(pady=(0, 10))
        
        ttk.Button(button_frame, text="Generar Vista Previa", 
                  command=self.generate_preview).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Generar y Guardar", 
                  command=self.generate_and_save).pack(side=tk.LEFT)
        
        # Frame de información
        info_frame = ttk.LabelFrame(main_frame, text="Información", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.info_text = tk.Text(info_frame, height=6, wrap=tk.WORD)
        info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mensaje inicial
        self.info_text.insert(tk.END, "Generador de Imágenes de Test para Pantallas LED\n\n")
        self.info_text.insert(tk.END, "Ejemplo: 2560x1152, 20 columnas, 5 filas\n")
        self.info_text.insert(tk.END, "Configure parámetros y genere vista previa\n")
        
    def on_rows_change(self, event=None):
        """Actualiza las entradas de altura cuando cambia el número de filas"""
        self.update_row_heights()
        # Actualizar cuadrícula de asignación si está visible
        if self.assignment_panel_visible.get():
            self.create_assignment_grid()
            self.assignment_grid_inner.update_idletasks()
            self.assignment_grid_canvas.configure(scrollregion=self.assignment_grid_canvas.bbox("all"))
        
    def update_row_heights(self):
        """Actualiza los campos de entrada para altura de cada fila"""
        try:
            rows = int(self.rows.get())
        except ValueError:
            rows = 5
            
        # Limpiar frame
        for widget in self.rows_frame.winfo_children():
            widget.destroy()
            
        # Limpiar listas
        self.row_height_vars.clear()
        self.row_height_entries.clear()
        
        # Crear entradas para cada fila
        for i in range(rows):
            row_frame = ttk.Frame(self.rows_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(row_frame, text=f"Fila {i+1}:", width=8).pack(side=tk.LEFT)
            
            height_var = tk.StringVar(value="256" if i < rows-1 else "128")
            self.row_height_vars.append(height_var)
            
            entry = ttk.Entry(row_frame, textvariable=height_var, width=8)
            entry.pack(side=tk.LEFT, padx=(5, 0))
            self.row_height_entries.append(entry)
        
    def auto_calculate(self):
        """Calcula automáticamente las dimensiones"""
        try:
            total_width = int(self.canvas_width.get())
            total_height = int(self.canvas_height.get())
            cols = int(self.columns.get())
            rows = int(self.rows.get())
            
            # Calcular ancho de celda
            cell_w = total_width // cols
            self.cell_width.set(str(cell_w))
            
            # Calcular alto de celda distribuyendo uniformemente
            cell_h = total_height // rows
            remainder = total_height % rows
            
            # Actualizar alturas de filas
            for i in range(rows):
                if i < len(self.row_height_vars):
                    # Distribuir el resto en las primeras filas
                    height = cell_h + (1 if i < remainder else 0)
                    self.row_height_vars[i].set(str(height))
                
            self.info_text.insert(tk.END, f"\nDimensiones calculadas:\n")
            self.info_text.insert(tk.END, f"- Ancho de celda: {cell_w}px\n")
            self.info_text.insert(tk.END, f"- Alto base: {cell_h}px\n")
            self.info_text.see(tk.END)
            
        except ValueError:
            messagebox.showerror("Error", "Por favor, introduzca valores numéricos válidos")
    
    def get_test_card_color(self, col, row, total_cols, total_rows):
        """Genera colores tipo carta de ajuste"""
        scheme = self.color_scheme.get()
        
        if scheme == "test_card":
            # Colores típicos de carta de ajuste
            colors = [
                (255, 255, 255),  # Blanco
                (255, 255, 0),    # Amarillo
                (0, 255, 255),    # Cian
                (0, 255, 0),      # Verde
                (255, 0, 255),    # Magenta
                (255, 0, 0),      # Rojo
                (0, 0, 255),      # Azul
                (0, 0, 0),        # Negro
                (192, 192, 192),  # Gris claro
                (128, 128, 128),  # Gris medio
                (64, 64, 64),     # Gris oscuro
                (255, 128, 0),    # Naranja
                (128, 255, 0),    # Verde lima
                (0, 128, 255),    # Azul claro
                (255, 0, 128),    # Rosa
                (128, 0, 255),    # Violeta
            ]
            
            # Patrón por filas
            if row == 0:  # Primera fila - colores primarios
                color_index = col % 8
                return colors[color_index]
            elif row == 1:  # Segunda fila - colores secundarios  
                color_index = (col % 8) + 8 if col % 8 < 8 else col % 8
                return colors[color_index] if color_index < len(colors) else colors[col % len(colors)]
            else:  # Resto de filas - patrón alterno
                return colors[(col + row * 3) % len(colors)]
                
        elif scheme == "primary_colors":
            # Solo colores primarios y secundarios
            colors = [
                (255, 0, 0),      # Rojo
                (0, 255, 0),      # Verde
                (0, 0, 255),      # Azul
                (255, 255, 0),    # Amarillo
                (255, 0, 255),    # Magenta
                (0, 255, 255),    # Cian
                (255, 255, 255),  # Blanco
                (0, 0, 0),        # Negro
            ]
            return colors[(col + row) % len(colors)]
            
        elif scheme == "rainbow":
            # Arco iris por columnas
            hue = (col / total_cols) * 360
            saturation = 1.0
            value = 1.0
            rgb = colorsys.hsv_to_rgb(hue/360, saturation, value)
            return tuple(int(c * 255) for c in rgb)
            
        elif scheme == "gradient":
            # Gradiente horizontal
            r = int(255 * (col / total_cols))
            g = int(255 * (1 - col / total_cols))
            b = int(255 * (row / total_rows))
            return (r, g, b)
            
        return (128, 128, 128)  # Gris por defecto
    
    def generate_image(self, preview_scale=None):
        """Genera la imagen de test"""
        try:
            # Obtener parámetros
            total_width = int(self.canvas_width.get())
            total_height = int(self.canvas_height.get())
            cols = int(self.columns.get())
            rows = int(self.rows.get())
            cell_w = int(self.cell_width.get())
            
            # Obtener alturas de filas
            row_heights = []
            for i in range(rows):
                if i < len(self.row_height_vars):
                    row_heights.append(int(self.row_height_vars[i].get()))
                else:
                    row_heights.append(256)
            
            # Escalar para vista previa si es necesario
            if preview_scale:
                total_width = int(total_width * preview_scale)
                total_height = int(total_height * preview_scale)
                cell_w = int(cell_w * preview_scale)
                row_heights = [int(h * preview_scale) for h in row_heights]
            
            # Crear imagen
            image = Image.new('RGB', (total_width, total_height), 'black')
            draw = ImageDraw.Draw(image)
            
            # Calcular tamaño de fuente basado en el tamaño de celda
            if preview_scale:
                font_size_small = max(10, int(min(cell_w, min(row_heights)) * 0.08))
                font_size_main = max(12, int(min(cell_w, min(row_heights)) * 0.10))
                font_size_center = max(24, int(min(total_width, total_height) * 0.03))
            else:
                font_size_small = max(16, int(min(cell_w, min(row_heights)) * 0.08))
                font_size_main = max(20, int(min(cell_w, min(row_heights)) * 0.10))
                font_size_center = max(48, int(min(total_width, total_height) * 0.03))
                
            try:
                font_small = ImageFont.truetype("arial.ttf", font_size_small)
                font_main = ImageFont.truetype("arial.ttf", font_size_main)
                font_center = ImageFont.truetype("arial.ttf", font_size_center)
            except:
                try:
                    font_small = ImageFont.load_default()
                    font_main = ImageFont.load_default()
                    font_center = ImageFont.load_default()
                except:
                    font_small = font_main = font_center = None
            
            # Dibujar celdas
            y_offset = 0
            for row in range(rows):
                current_row_h = row_heights[row] if row < len(row_heights) else row_heights[-1]
                
                for col in range(cols):
                    # Calcular posición
                    x = col * cell_w
                    y = y_offset
                    
                    # Generar color
                    color = self.get_test_card_color(col, row, cols, rows)
                    
                    # Dibujar celda
                    draw.rectangle([x, y, x + cell_w, y + current_row_h], fill=color)
                    
                    # Dibujar líneas de cuadrícula si está habilitado
                    if self.show_grid.get():
                        draw.rectangle([x, y, x + cell_w, y + current_row_h], outline='white', width=2)

                    # Dibujar numeración y asignación de puertos
                    if self.show_numbers.get() and font_main and font_small:
                        # Obtener asignaciones de puertos
                        main_assignment = self.port_assignments.get((col, row), {}).get('main', None)
                        backup_assignment = self.port_assignments.get((col, row), {}).get('backup', None)

                        # Línea 1: Posición (col+1, row+1) - más grande y negrita
                        line1 = f"{col+1},{row+1}"

                        # Línea 2: MAIN: tarjeta-puerto
                        if main_assignment:
                            line2 = f"MAIN: {main_assignment[0]}-{main_assignment[1]}"
                        else:
                            line2 = "MAIN: --"

                        # Línea 3: BKP: tarjeta-puerto
                        if backup_assignment:
                            line3 = f"BKP: {backup_assignment[0]}-{backup_assignment[1]}"
                        else:
                            line3 = "BKP: --"

                        # Calcular posiciones de texto
                        bbox1 = draw.textbbox((0, 0), line1, font=font_main)
                        bbox2 = draw.textbbox((0, 0), line2, font=font_small)
                        bbox3 = draw.textbbox((0, 0), line3, font=font_small)

                        text1_width = bbox1[2] - bbox1[0]
                        text1_height = bbox1[3] - bbox1[1]
                        text2_height = bbox2[3] - bbox2[1]
                        text3_height = bbox3[3] - bbox3[1]

                        total_text_height = text1_height + text2_height + text3_height + 4  # 4px de separación

                        # Centrar verticalmente el conjunto de líneas
                        start_y = y + (current_row_h - total_text_height) // 2

                        # Determinar color de texto contrastante
                        color = self.get_test_card_color(col, row, cols, rows)
                        brightness = sum(color) / 3
                        text_color = 'black' if brightness > 128 else 'white'
                        shadow_color = 'white' if brightness > 128 else 'black'

                        # Dibujar línea 1 (principal - más grande)
                        text1_x = x + (cell_w - text1_width) // 2
                        text1_y = start_y
                        draw.text((text1_x + 1, text1_y + 1), line1, fill=shadow_color, font=font_main)
                        draw.text((text1_x, text1_y), line1, fill=text_color, font=font_main)

                        # Dibujar línea 2 (MAIN)
                        text2_width = bbox2[2] - bbox2[0]
                        text2_x = x + (cell_w - text2_width) // 2
                        text2_y = text1_y + text1_height + 2
                        draw.text((text2_x + 1, text2_y + 1), line2, fill=shadow_color, font=font_small)
                        draw.text((text2_x, text2_y), line2, fill=text_color, font=font_small)

                        # Dibujar línea 3 (BACKUP)
                        text3_width = bbox3[2] - bbox3[0]
                        text3_x = x + (cell_w - text3_width) // 2
                        text3_y = text2_y + text2_height + 2
                        draw.text((text3_x + 1, text3_y + 1), line3, fill=shadow_color, font=font_small)
                        draw.text((text3_x, text3_y), line3, fill=text_color, font=font_small)

                y_offset += current_row_h
            
            # Dibujar texto central si está habilitado
            if self.show_center_text.get() and font_center:
                line1 = self.center_text_line1.get().strip()
                line2 = self.center_text_line2.get().strip()
                
                if line1 or line2:
                    # Calcular posición central
                    center_x = total_width // 2
                    center_y = total_height // 2
                    
                    # Calcular dimensiones del texto
                    bbox1 = draw.textbbox((0, 0), line1, font=font_center) if line1 else (0, 0, 0, 0)
                    bbox2 = draw.textbbox((0, 0), line2, font=font_center) if line2 else (0, 0, 0, 0)
                    
                    text1_height = bbox1[3] - bbox1[1] if line1 else 0
                    text2_height = bbox2[3] - bbox2[1] if line2 else 0
                    total_text_height = text1_height + text2_height + (5 if line1 and line2 else 0)
                    
                    start_y = center_y - total_text_height // 2
                    
                    # Dibujar línea 1
                    if line1:
                        text1_width = bbox1[2] - bbox1[0]
                        text1_x = center_x - text1_width // 2
                        text1_y = start_y
                        
                        # Fondo semitransparente (simulado con rectángulo gris)
                        padding = 10
                        draw.rectangle([
                            text1_x - padding, text1_y - padding,
                            text1_x + text1_width + padding, text1_y + text1_height + padding
                        ], fill=(0, 0, 0, 128), outline='white', width=2)
                        
                        # Texto con sombra
                        draw.text((text1_x + 2, text1_y + 2), line1, fill='black', font=font_center)
                        draw.text((text1_x, text1_y), line1, fill='white', font=font_center)
                    
                    # Dibujar línea 2
                    if line2:
                        text2_width = bbox2[2] - bbox2[0]
                        text2_x = center_x - text2_width // 2
                        text2_y = start_y + text1_height + (5 if line1 else 0)
                        
                        if not line1:  # Si no hay línea 1, añadir fondo para línea 2
                            padding = 10
                            draw.rectangle([
                                text2_x - padding, text2_y - padding,
                                text2_x + text2_width + padding, text2_y + text2_height + padding
                            ], fill=(0, 0, 0, 128), outline='white', width=2)
                        
                        # Texto con sombra
                        draw.text((text2_x + 2, text2_y + 2), line2, fill='black', font=font_center)
                        draw.text((text2_x, text2_y), line2, fill='white', font=font_center)
            
            return image
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar la imagen: {str(e)}")
            return None
    
    def generate_preview(self):
        """Genera y muestra una vista previa"""
        # Calcular escala para vista previa (máximo 1000px de ancho)
        total_width = int(self.canvas_width.get())
        if total_width > 1000:
            scale = 1000 / total_width
        else:
            scale = 1
            
        image = self.generate_image(preview_scale=scale)
        if image:
            # Mostrar en ventana nueva
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Vista Previa")
            
            # Convertir para Tkinter
            from PIL import ImageTk
            photo = ImageTk.PhotoImage(image)
            
            label = tk.Label(preview_window, image=photo)
            label.pack()
            # Mantener referencia para evitar garbage collection
            setattr(preview_window, 'photo_ref', photo)
            
            self.info_text.insert(tk.END, f"\nVista previa generada (escala: {scale:.2f})\n")
            self.info_text.see(tk.END)
    
    def generate_and_save(self):
        """Genera la imagen a tamaño completo y la guarda"""
        image = self.generate_image()
        if image:
            # Seleccionar archivo de destino
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")],
                title="Guardar imagen de test"
            )
            
            if filename:
                try:
                    image.save(filename)
                    self.info_text.insert(tk.END, f"\nImagen guardada: {filename}\n")
                    self.info_text.insert(tk.END, f"Dimensiones: {image.width}x{image.height}\n")
                    self.info_text.see(tk.END)
                    messagebox.showinfo("Éxito", f"Imagen guardada en:\n{filename}")
                except Exception as e:
                    messagebox.showerror("Error", f"Error al guardar la imagen: {str(e)}")
    
    def setup_assignment_panel(self):
        """Configura el panel de asignación de puertos"""
        # Configuración de cableado
        cable_config_frame = ttk.LabelFrame(self.assignment_frame, text="Configuración de Cableado", padding="5")
        cable_config_frame.pack(fill=tk.X, pady=(0, 10))

        config_row1 = ttk.Frame(cable_config_frame)
        config_row1.pack(fill=tk.X, pady=2)

        ttk.Label(config_row1, text="Módulos por puerto:").pack(side=tk.LEFT)
        modules_combo = ttk.Combobox(config_row1, textvariable=self.modules_per_port, width=8)
        modules_combo['values'] = ['5', '10', '15', '20', '25', '30']
        modules_combo.pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(config_row1, text="Dirección:").pack(side=tk.LEFT)
        direction_combo = ttk.Combobox(config_row1, textvariable=self.cable_direction, width=10)
        direction_combo['values'] = ['horizontal', 'vertical']
        direction_combo.pack(side=tk.LEFT, padx=(5, 0))

        # --- Canvas con scrollbars para la cuadrícula de módulos ---
        grid_canvas_frame = ttk.Frame(self.assignment_frame)
        grid_canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Canvas para la cuadrícula
        self.assignment_grid_canvas = tk.Canvas(grid_canvas_frame, height=400)
        self.assignment_grid_canvas.grid(row=0, column=0, sticky="nsew")
        # Hacer que el canvas y el frame interno se expandan al ancho disponible
        grid_canvas_frame.columnconfigure(0, weight=1)
        grid_canvas_frame.rowconfigure(0, weight=1)
        # Frame interno donde se dibuja la cuadrícula
        self.assignment_grid_inner = ttk.Frame(self.assignment_grid_canvas)
        self.assignment_grid_window = self.assignment_grid_canvas.create_window((0, 0), window=self.assignment_grid_inner, anchor="nw")
        def expand_grid_inner_to_canvas(event=None):
            canvas_width = self.assignment_grid_canvas.winfo_width()
            self.assignment_grid_canvas.itemconfig(self.assignment_grid_window, width=canvas_width)
        self.assignment_grid_inner.bind('<Configure>', expand_grid_inner_to_canvas)

        # Scrollbars
        self.assignment_grid_vscroll = ttk.Scrollbar(grid_canvas_frame, orient="vertical", command=self.assignment_grid_canvas.yview)
        self.assignment_grid_vscroll.grid(row=0, column=1, sticky="ns")
        self.assignment_grid_hscroll = ttk.Scrollbar(self.assignment_frame, orient="horizontal", command=self.assignment_grid_canvas.xview)
        self.assignment_grid_hscroll.pack(fill=tk.X, side=tk.BOTTOM)

        self.assignment_grid_canvas.configure(yscrollcommand=self.assignment_grid_vscroll.set, xscrollcommand=self.assignment_grid_hscroll.set)

        # Frame interno donde se dibuja la cuadrícula
        self.assignment_grid_inner = ttk.Frame(self.assignment_grid_canvas)
        self.assignment_grid_window = self.assignment_grid_canvas.create_window((0, 0), window=self.assignment_grid_inner, anchor="nw")

        # Ajustar scrollregion dinámicamente
        self.assignment_grid_inner.bind(
            "<Configure>",
            lambda event: self.assignment_grid_canvas.configure(scrollregion=self.assignment_grid_canvas.bbox("all"))
        )

        # Permitir scroll con mousewheel
        def _on_mousewheel(event):
            if event.state & 0x1:  # Shift presionado: scroll horizontal
                self.assignment_grid_canvas.xview_scroll(int(-1*(event.delta/120)), "units")
            else:
                self.assignment_grid_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.assignment_grid_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Hacer que el frame y canvas se expandan con la ventana
        # Eliminado pack_propagate(False) para permitir expansión natural

        # Guardar referencias para uso posterior
        self.assignment_grid_frame = grid_canvas_frame

        # --- Controles manuales de asignación ---
        manual_frame = ttk.LabelFrame(self.assignment_frame, text="Asignación Manual", padding="5")
        manual_frame.pack(fill=tk.X, pady=(0, 10))

        # Modo (main/backup)
        ttk.Label(manual_frame, text="Modo:").pack(side=tk.LEFT)
        mode_combo = ttk.Combobox(manual_frame, textvariable=self.assignment_mode, width=7, state="readonly")
        mode_combo['values'] = ("main", "backup")
        mode_combo.pack(side=tk.LEFT, padx=(5, 10))

        # Tarjeta
        ttk.Label(manual_frame, text="Tarjeta:").pack(side=tk.LEFT)
        card_entry = ttk.Entry(manual_frame, textvariable=self.selected_card, width=5)
        card_entry.pack(side=tk.LEFT, padx=(5, 10))

        # Puerto
        ttk.Label(manual_frame, text="Puerto:").pack(side=tk.LEFT)
        port_entry = ttk.Entry(manual_frame, textvariable=self.selected_port, width=5)
        port_entry.pack(side=tk.LEFT, padx=(5, 10))

        # Botón asignar línea
        ttk.Button(manual_frame, text="Asignar línea", command=self.assign_line).pack(side=tk.LEFT, padx=(5, 10))

        # Botón limpiar
        ttk.Button(manual_frame, text="Limpiar todo", command=self.clear_all_assignments).pack(side=tk.LEFT, padx=(5, 10))

        # Botón auto-asignar
        ttk.Button(manual_frame, text="Auto-asignar", command=self.auto_assign_ports).pack(side=tk.LEFT, padx=(5, 0))

        # Widget para mostrar info de líneas de cableado
        self.line_info_text = tk.Text(self.assignment_frame, height=5, wrap=tk.WORD, state="disabled")
        self.line_info_text.pack(fill=tk.X, pady=(10, 0))

        # Llamar a la creación de la cuadrícula (debe existir la función)
        self.create_assignment_grid()

    def create_assignment_grid(self):
        # Limpia el frame antes de redibujar
        for widget in self.assignment_grid_inner.winfo_children():
            widget.destroy()
        self.grid_buttons.clear()
        # Obtener dimensiones
        try:
            cols = int(self.columns.get())
            rows = int(self.rows.get())
        except Exception:
            cols, rows = 10, 5
        cell_w = 60
        cell_h = 50
        # Crear botones/labels para cada módulo
        for row in range(rows):
            self.assignment_grid_inner.grid_rowconfigure(row, weight=1)
            for col in range(cols):
                self.assignment_grid_inner.grid_columnconfigure(col, weight=1)
                main_assignment = self.port_assignments.get((col, row), {}).get('main', None)
                backup_assignment = self.port_assignments.get((col, row), {}).get('backup', None)
                btn_text = f"{col+1},{row+1}\n"
                if main_assignment:
                    btn_text += f"M:{main_assignment[0]}-{main_assignment[1]}\n"
                else:
                    btn_text += "M:--\n"
                if backup_assignment:
                    btn_text += f"B:{backup_assignment[0]}-{backup_assignment[1]}"
                else:
                    btn_text += "B:--"
                btn = tk.Button(self.assignment_grid_inner, text=btn_text, width=8, height=3)
                btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
                # Click izquierdo: asignar manualmente
                btn.bind("<Button-1>", lambda event, c=col, r=row: self.assign_module_port(c, r))
                # Click derecho: mostrar info
                btn.bind("<Button-3>", lambda event, c=col, r=row: self.show_module_info(c, r))
                self.grid_buttons[(col, row)] = btn

    def assign_module_port(self, col, row):
        """Asigna manualmente el puerto/tarjeta seleccionados al módulo clicado"""
        try:
            card = int(self.selected_card.get())
            port = int(self.selected_port.get())
            mode = self.assignment_mode.get()
        except ValueError:
            messagebox.showerror("Error", "Seleccione tarjeta y puerto válidos")
            return
        if (col, row) not in self.port_assignments:
            self.port_assignments[(col, row)] = {}
        self.port_assignments[(col, row)][mode] = (card, port)
        self.update_grid_button(col, row)
        self.update_line_info()
        # Hacer que las columnas y filas se expandan
        # (Eliminado: la expansión ahora la gestiona el frame/canvas externo)
        # Forzar actualización de scrollregion
        self.assignment_grid_inner.update_idletasks()
        self.assignment_grid_canvas.configure(scrollregion=self.assignment_grid_canvas.bbox("all"))

    #
        
    def toggle_assignment_panel(self):
        """Muestra/oculta el panel de asignación"""
        if self.assignment_panel_visible.get():
            # Ocultar panel
            self.assignment_frame.pack_forget()
            self.assignment_toggle_btn.config(text="▼ Mostrar Asignación de Puertos")
            self.assignment_panel_visible.set(False)
        else:
            # Mostrar panel
            self.assignment_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
            self.assignment_toggle_btn.config(text="▲ Ocultar Asignación de Puertos")
            self.assignment_panel_visible.set(True)
            self.create_assignment_grid()  # Actualizar cuadrícula
            self.assignment_grid_inner.update_idletasks()
            self.assignment_grid_canvas.configure(scrollregion=self.assignment_grid_canvas.bbox("all"))
            # Scroll hacia el panel de asignación después de un breve delay
            self.root.after(100, self.scroll_to_assignment_panel)

    def scroll_to_assignment_panel(self):
        """Hace scroll hacia el panel de asignación"""
        if hasattr(self, 'main_canvas'):
            # Obtener la posición del panel de asignación
            self.main_canvas.update_idletasks()
            bbox = self.main_canvas.bbox("all")
            if bbox:
                # Scroll hacia la parte inferior donde está el panel
                canvas_height = self.main_canvas.winfo_height()
                total_height = bbox[3] - bbox[1]
                if total_height > canvas_height:
                    # Scroll hacia abajo para mostrar el panel
                    scroll_position = 0.7  # 70% hacia abajo
                    self.main_canvas.yview_moveto(scroll_position)
        
    def update_grid_button(self, col, row):
        """Actualiza el texto de un botón de la cuadrícula"""
        if (col, row) not in self.grid_buttons:
            return
            
        main_assignment = self.port_assignments.get((col, row), {}).get('main', None)
        backup_assignment = self.port_assignments.get((col, row), {}).get('backup', None)
        
        btn_text = f"{col+1},{row+1}\n"
        if main_assignment:
            btn_text += f"M:{main_assignment[0]}-{main_assignment[1]}\n"
        else:
            btn_text += "M:--\n"
            
        if backup_assignment:
            btn_text += f"B:{backup_assignment[0]}-{backup_assignment[1]}"
        else:
            btn_text += "B:--"
            
        self.grid_buttons[(col, row)].config(text=btn_text)
        
    def clear_all_assignments(self):
        """Limpia todas las asignaciones de puertos"""
        if messagebox.askyesno("Confirmar", "¿Eliminar todas las asignaciones de puertos?"):
            self.port_assignments.clear()
            self.create_assignment_grid()
            
    def auto_assign_ports(self):
        """Asignación automática de líneas de cableado"""
        try:
            cols = int(self.columns.get())
            rows = int(self.rows.get())
            modules_per_port = int(self.modules_per_port.get())
        except ValueError:
            return
            
        total_modules = cols * rows
        total_lines = math.ceil(total_modules / modules_per_port)
        
        # Diálogo de configuración auto-asignación
        dialog = tk.Toplevel(self.root)
        dialog.title("Auto-Asignación de Líneas de Cableado")
        dialog.geometry("450x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Configuración de Auto-Asignación por Líneas", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Información
        info_frame = ttk.LabelFrame(dialog, text="Información", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(info_frame, text=f"Total módulos: {total_modules}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Módulos por línea: {modules_per_port}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Líneas necesarias: {total_lines}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Dirección: {self.cable_direction.get()}").pack(anchor=tk.W)
        
        # Configuración MAIN
        main_frame = ttk.LabelFrame(dialog, text="MAIN", padding="10")
        main_frame.pack(fill=tk.X, padx=10, pady=5)
        
        main_start_card = tk.StringVar(value="1")
        main_start_port = tk.StringVar(value="1")
        
        ttk.Label(main_frame, text="Tarjeta inicial:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=main_start_card, width=5).grid(row=0, column=1, padx=5)
        ttk.Label(main_frame, text="Puerto inicial:").grid(row=0, column=2, sticky=tk.W, padx=(10,0))
        ttk.Entry(main_frame, textvariable=main_start_port, width=5).grid(row=0, column=3, padx=5)
        
        # Configuración BACKUP
        backup_frame = ttk.LabelFrame(dialog, text="BACKUP", padding="10")
        backup_frame.pack(fill=tk.X, padx=10, pady=5)
        
        backup_start_card = tk.StringVar(value="1")
        backup_start_port = tk.StringVar(value="11")
        
        ttk.Label(backup_frame, text="Tarjeta inicial:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(backup_frame, textvariable=backup_start_card, width=5).grid(row=0, column=1, padx=5)
        ttk.Label(backup_frame, text="Puerto inicial:").grid(row=0, column=2, sticky=tk.W, padx=(10,0))
        ttk.Entry(backup_frame, textvariable=backup_start_port, width=5).grid(row=0, column=3, padx=5)
        
        # Opción de dirección backup
        backup_option_frame = ttk.Frame(backup_frame)
        backup_option_frame.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(10,0))
        
        backup_reverse = tk.BooleanVar(value=True)
        ttk.Checkbutton(backup_option_frame, text="Backup entra por extremo opuesto (recomendado)", 
                       variable=backup_reverse).pack(anchor=tk.W)
        
        def apply_auto_assignment():
            try:
                main_card = int(main_start_card.get())
                main_port = int(main_start_port.get())
                backup_card = int(backup_start_card.get())
                backup_port = int(backup_start_port.get())

                # Limpiar asignaciones anteriores
                self.port_assignments.clear()

                # Generar lista de todos los módulos en orden NovaLCT (lado de inicio y patrón)
                direction = self.cable_direction.get()
                start_side = self.start_side.get()
                pattern = self.pattern.get()

                def get_novalct_order(cols, rows, direction, start_side, pattern):
                    order = []
                    if direction == "horizontal":
                        for row in range(rows):
                            if pattern == "serpentina" and row % 2 == 1:
                                col_range = range(cols-1, -1, -1)
                            else:
                                col_range = range(cols)
                            if start_side == "izquierda":
                                pass  # col_range ya es correcto
                            elif start_side == "derecha":
                                col_range = reversed(list(col_range))
                            elif start_side == "arriba" or start_side == "abajo":
                                # Para horizontal, arriba/abajo no cambian el orden
                                pass
                            for col in col_range:
                                order.append((col, row))
                        if start_side == "abajo":
                            order = order[::-1]
                    else:  # vertical
                        for col in range(cols):
                            if pattern == "serpentina" and col % 2 == 1:
                                row_range = range(rows-1, -1, -1)
                            else:
                                row_range = range(rows)
                            if start_side == "arriba":
                                pass
                            elif start_side == "abajo":
                                row_range = reversed(list(row_range))
                            elif start_side == "izquierda" or start_side == "derecha":
                                # Para vertical, izq/der no cambian el orden
                                pass
                            for row in row_range:
                                order.append((col, row))
                        if start_side == "derecha":
                            order = order[::-1]
                    return order

                all_modules = get_novalct_order(cols, rows, direction, start_side, pattern)

                # Asignar MAIN
                current_main_card = main_card
                current_main_port = main_port

                for i in range(0, len(all_modules), modules_per_port):
                    line_modules = all_modules[i:i+modules_per_port]
                    for col, row in line_modules:
                        if (col, row) not in self.port_assignments:
                            self.port_assignments[(col, row)] = {}
                        self.port_assignments[(col, row)]['main'] = (current_main_card, current_main_port)
                    current_main_port += 1
                    if current_main_port > 16:
                        current_main_port = 1
                        current_main_card += 1

                # Asignar BACKUP (orden inverso de líneas si backup_reverse)
                current_backup_card = backup_card
                current_backup_port = backup_port

                for i in range(0, len(all_modules), modules_per_port):
                    line_modules = all_modules[i:i+modules_per_port]
                    if backup_reverse.get():
                        line_modules = line_modules[::-1]
                    for col, row in line_modules:
                        if (col, row) not in self.port_assignments:
                            self.port_assignments[(col, row)] = {}
                        self.port_assignments[(col, row)]['backup'] = (current_backup_card, current_backup_port)
                    current_backup_port += 1
                    if current_backup_port > 16:
                        current_backup_port = 1
                        current_backup_card += 1

                self.create_assignment_grid()
                self.update_line_info()

                self.info_text.insert(tk.END, f"\nAuto-asignación completada (NovaLCT):\n")
                self.info_text.insert(tk.END, f"- {total_lines} líneas de {modules_per_port} módulos\n")
                self.info_text.insert(tk.END, f"- Dirección: {direction}\n")
                self.info_text.insert(tk.END, f"- Lado inicio: {start_side}\n")
                self.info_text.insert(tk.END, f"- Patrón: {pattern}\n")
                self.info_text.insert(tk.END, f"- Backup reverso: {'Sí' if backup_reverse.get() else 'No'}\n")
                self.info_text.see(tk.END)

                dialog.destroy()

            except ValueError:
                messagebox.showerror("Error", "Ingrese valores numéricos válidos")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Aplicar", command=apply_auto_assignment).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def get_line_modules(self, line_start_col, line_start_row):
        """Obtiene todos los módulos de una línea basándose en la configuración"""
        try:
            cols = int(self.columns.get())
            rows = int(self.rows.get())
            modules_per_port = int(self.modules_per_port.get())
            direction = self.cable_direction.get()
        except ValueError:
            return []
            
        modules = []
        current_col, current_row = line_start_col, line_start_row
        
        for i in range(modules_per_port):
            # Verificar que estamos dentro de la cuadrícula
            if 0 <= current_col < cols and 0 <= current_row < rows:
                modules.append((current_col, current_row))
                
                # Calcular siguiente posición según dirección
                if direction == "horizontal":
                    current_col += 1
                    if current_col >= cols:  # Saltar a siguiente fila
                        current_col = 0
                        current_row += 1
                elif direction == "vertical":
                    current_row += 1
                    if current_row >= rows:  # Saltar a siguiente columna
                        current_row = 0
                        current_col += 1
            else:
                break
                
        return modules
        
    def assign_line(self):
        """Asigna una línea completa (fila o columna) al puerto/tarjeta seleccionados, sobrescribiendo asignaciones si es necesario"""
        try:
            card = int(self.selected_card.get())
            port = int(self.selected_port.get())
            mode = self.assignment_mode.get()
            direction = self.cable_direction.get()
            cols = int(self.columns.get())
            rows = int(self.rows.get())
        except ValueError:
            messagebox.showerror("Error", "Seleccione tarjeta, puerto y dimensiones válidos")
            return

        # Determinar la línea a asignar según la dirección y el primer módulo seleccionado
        # Buscar el primer módulo sin asignar en la dirección correspondiente
        start_module = self.find_next_unassigned_module(mode)
        if not start_module:
            messagebox.showinfo("Info", f"Todos los módulos ya tienen {mode.upper()} asignado")
            return

        # Asignar a toda la línea (fila o columna completa)
        line_modules = []
        if direction == "horizontal":
            # Asignar toda la fila del módulo encontrado
            row = start_module[1]
            for col in range(cols):
                line_modules.append((col, row))
        else:
            # Asignar toda la columna del módulo encontrado
            col = start_module[0]
            for row in range(rows):
                line_modules.append((col, row))

        # Asignar puerto/tarjeta a todos los módulos de la línea (sobrescribe cualquier asignación anterior)
        for col, row in line_modules:
            if (col, row) not in self.port_assignments:
                self.port_assignments[(col, row)] = {}
            if mode == "main":
                self.port_assignments[(col, row)]['main'] = (card, port)
            else:
                self.port_assignments[(col, row)]['backup'] = (card, port)

        # Actualizar interfaz
        self.create_assignment_grid()
        self.update_line_info()

        # Auto-incrementar puerto
        next_port = port + 1
        if next_port <= 16:
            self.selected_port.set(str(next_port))
        else:
            next_card = card + 1
            self.selected_card.set(str(next_card))
            self.selected_port.set("1")

        self.info_text.insert(tk.END, f"\n{mode.upper()}: Línea asignada a tarjeta {card}, puerto {port} (sobrescribe toda la {'fila' if direction == 'horizontal' else 'columna'})\n")
        self.info_text.see(tk.END)
            
    def find_next_unassigned_module(self, mode):
        """Encuentra el siguiente módulo sin asignar para el modo especificado"""
        try:
            cols = int(self.columns.get())
            rows = int(self.rows.get())
            direction = self.cable_direction.get()
        except ValueError:
            return None
            
        # Recorrer según la dirección configurada
        if direction == "horizontal":
            for row in range(rows):
                for col in range(cols):
                    assignment = self.port_assignments.get((col, row), {}).get(mode, None)
                    if assignment is None:
                        return (col, row)
        else:  # vertical
            for col in range(cols):
                for row in range(rows):
                    assignment = self.port_assignments.get((col, row), {}).get(mode, None)
                    if assignment is None:
                        return (col, row)
                        
        return None
        
    def update_line_info(self):
        """Actualiza la información sobre las líneas configuradas"""
        self.line_info_text.config(state="normal")
        self.line_info_text.delete(1.0, tk.END)
        
        try:
            modules_per_port = int(self.modules_per_port.get())
            direction = self.cable_direction.get()
            cols = int(self.columns.get())
            rows = int(self.rows.get())
        except ValueError:
            return
            
        total_modules = cols * rows
        total_ports_needed = math.ceil(total_modules / modules_per_port)
        
        info_text = f"Configuración de cableado:\n"
        info_text += f"• {modules_per_port} módulos por puerto\n"
        info_text += f"• Dirección: {direction}\n"
        info_text += f"• Total módulos: {total_modules}\n"
        info_text += f"• Puertos necesarios: {total_ports_needed} (main) + {total_ports_needed} (backup)\n"
        
        self.line_info_text.insert(tk.END, info_text)
        self.line_info_text.config(state="disabled")
    
    def show_module_info(self, col, row):
        """Muestra información detallada del módulo seleccionado"""
        main_assignment = self.port_assignments.get((col, row), {}).get('main', None)
        backup_assignment = self.port_assignments.get((col, row), {}).get('backup', None)
        
        info = f"Módulo ({col+1},{row+1}):\n"
        if main_assignment:
            info += f"MAIN: Tarjeta {main_assignment[0]}, Puerto {main_assignment[1]}\n"
        else:
            info += "MAIN: Sin asignar\n"
            
        if backup_assignment:
            info += f"BACKUP: Tarjeta {backup_assignment[0]}, Puerto {backup_assignment[1]}\n"
        else:
            info += "BACKUP: Sin asignar\n"
            
        messagebox.showinfo("Información del Módulo", info)

def main():
    root = tk.Tk()
    # Hacer que la ventana principal sea redimensionable y los paneles se expandan
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    app = LEDScreenTestGenerator(root)
    root.minsize(800, 600)
    root.mainloop()

if __name__ == "__main__":
    main()
