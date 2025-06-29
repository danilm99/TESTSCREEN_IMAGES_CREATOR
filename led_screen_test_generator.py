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
        
        # Variables
        self.canvas_width = tk.StringVar(value="2560")
        self.canvas_height = tk.StringVar(value="1152")
        self.columns = tk.StringVar(value="20")
        self.rows = tk.StringVar(value="5")
        self.cell_width = tk.StringVar(value="128")
        self.show_numbers = tk.BooleanVar(value=True)
        self.show_grid = tk.BooleanVar(value=True)
        self.color_scheme = tk.StringVar(value="test_card")
        
        # Lista para almacenar StringVars de altura de cada fila
        self.row_height_vars = []
        self.row_height_entries = []
        
        self.setup_ui()
        self.update_row_heights()
        
    def setup_ui(self):
        # Frame principal con scroll
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Generador de Imágenes de Test para Pantallas LED", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Frame de configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
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
        grid_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(grid_frame, text="Configuración de cuadrícula:").pack(anchor=tk.W)
        
        grid_config_frame = ttk.Frame(grid_frame)
        grid_config_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(grid_config_frame, text="Columnas:").pack(side=tk.LEFT)
        ttk.Entry(grid_config_frame, textvariable=self.columns, width=8).pack(side=tk.LEFT, padx=(5, 15))
        ttk.Label(grid_config_frame, text="Filas:").pack(side=tk.LEFT)
        rows_entry = ttk.Entry(grid_config_frame, textvariable=self.rows, width=8)
        rows_entry.pack(side=tk.LEFT, padx=(5, 15))
        rows_entry.bind('<KeyRelease>', self.on_rows_change)
        
        ttk.Label(grid_config_frame, text="Ancho celda:").pack(side=tk.LEFT)
        ttk.Entry(grid_config_frame, textvariable=self.cell_width, width=8).pack(side=tk.LEFT, padx=(5, 0))
        
        # Frame para altura de filas individuales
        self.rows_frame = ttk.LabelFrame(config_frame, text="Altura de cada fila (píxeles)", padding="10")
        self.rows_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Esquema de colores
        color_frame = ttk.Frame(config_frame)
        color_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(color_frame, text="Esquema de colores:").pack(side=tk.LEFT)
        color_combo = ttk.Combobox(color_frame, textvariable=self.color_scheme, width=15)
        color_combo['values'] = ('test_card', 'rainbow', 'primary_colors', 'gradient')
        color_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Opciones
        options_frame = ttk.Frame(config_frame)
        options_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Checkbutton(options_frame, text="Mostrar números", variable=self.show_numbers).pack(side=tk.LEFT)
        ttk.Checkbutton(options_frame, text="Mostrar líneas de cuadrícula", variable=self.show_grid).pack(side=tk.LEFT, padx=(20, 0))
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
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
        scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mensaje inicial
        self.info_text.insert(tk.END, "Generador de Imágenes de Test para Pantallas LED\n\n")
        self.info_text.insert(tk.END, "Ejemplo: 2560x1152, 20 columnas, 5 filas\n")
        self.info_text.insert(tk.END, "Configure parámetros y genere vista previa\n")
        
    def on_rows_change(self, event=None):
        """Actualiza las entradas de altura cuando cambia el número de filas"""
        self.update_row_heights()
        
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
                font_size = max(16, int(min(cell_w, min(row_heights)) * 0.15))
            else:
                font_size = max(32, int(min(cell_w, min(row_heights)) * 0.15))
                
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.load_default()
                except:
                    font = None
            
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
                    
                    # Dibujar número si está habilitado
                    if self.show_numbers.get() and font:
                        text = f"{col+1},{row+1}"
                        
                        # Calcular posición del texto
                        bbox = draw.textbbox((0, 0), text, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                        
                        text_x = x + (cell_w - text_width) // 2
                        text_y = y + (current_row_h - text_height) // 2
                        
                        # Determinar color de texto contrastante
                        brightness = sum(color) / 3
                        text_color = 'black' if brightness > 128 else 'white'
                        shadow_color = 'white' if brightness > 128 else 'black'
                        
                        # Dibujar texto con sombra
                        draw.text((text_x + 2, text_y + 2), text, fill=shadow_color, font=font)
                        draw.text((text_x, text_y), text, fill=text_color, font=font)
                
                y_offset += current_row_h
            
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

def main():
    root = tk.Tk()
    app = LEDScreenTestGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
