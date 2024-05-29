import tkinter as tk
import customtkinter as ctk
from Planilla import Planilla
from Ventanas import Ventanas
from tkinter import messagebox
import os

class Interfaz_trabajo():
    def __init__(self, spreadsheet_name_entry, filtro_entry):
        try:
            self.planilla = Planilla(spreadsheet_name_entry, filtro_entry)
        except ValueError as e:
            messagebox.showinfo("Error", str(e))
            return
        self.root = ctk.CTk()
        ctk.set_appearance_mode("dark")
        self.root.title("AppTags")
        self.total_items = 0
        self.items_totales()
        self.item_actual = 1  # Item actual
        try:
            self.ventanas = Ventanas(self.planilla.row_actual.iloc[0], self.planilla.row_actual.iloc[1])
        except:
            self.ventanas = Ventanas("https://www.google.com", "https://www.google.com")
            pass
        self.configurar_tamaño_interfaz()
        self.crear_menu()
        self.crear_botones_interfaz()
        self.dropdown_resultado.trace('w', self.actualizar_observaciones)
        self.actualizar_contador()
        self.actualizar_estado_worker()
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_interfaz)
        self.root.mainloop()

    def configurar_tamaño_interfaz(self):
        self.root.iconbitmap(f"{os.getcwd()}//Iconos//logo.ico")
        self.root.attributes('-topmost', True)
        ventana_configuracion_x = self.root.winfo_screenwidth() // 2 - 150
        ventana_configuracion_y = self.root.winfo_screenheight() // 2 + 200
        self.root.geometry(f"280x210+{ventana_configuracion_x}+{ventana_configuracion_y}")

    def crear_botones_interfaz(self):
        self.estado_worker = ctk.CTkLabel(self.root, text="")
        self.estado_worker.grid(row=4, column=1, padx=8, pady=3, sticky="e")
        self.label_resultado = ctk.CTkLabel(self.root, text="Resultado:")
        self.label_resultado.grid(row=0, column=0, padx=(10,0), pady=(10,5), sticky="w")
        self.resultados = ["Match", "No_Match", "Not_Found"]
        self.dropdown_resultado = tk.StringVar(value="")
        self.menu_resultado = ctk.CTkOptionMenu(self.root, variable=self.dropdown_resultado, values=self.resultados)
        self.menu_resultado.grid(row=0, column=1, padx=(10), pady=(10,5))

        self.label_observacion = ctk.CTkLabel(self.root, text="Observación:")
        self.label_observacion.grid(row=1, column=0, padx=(10, 0), pady=5, sticky="w")
        self.observaciones = {
            "": [""],
            "Match": ["", "Pausada Meli", "Sin stock rival"],
            "No_Match": ["", "Talle", "Color" , "Marca", "Reacondicionado/Usado/Vitrina", "Medidas", "Kit", "Site diferente","Voltaje"," Modelo", "Faltan de datos en publicación",  "Version", "Almacenamiento/Storage",  "Cantidad", "Dif Producto","Sin stock rival", "Cajas Sorpresa","Armas","Genero","Inapropiado/Animales"],
            "Not_Found": ["", "Publicacion Caida MELI", "Publicacion Caida Rival","Sin stock rival"]
        }
        self.observacion_options = self.observaciones[self.resultados[0]]
        self.dropdown_observacion = tk.StringVar(value="")
        self.menu_observacion = ctk.CTkOptionMenu(self.root, variable=self.dropdown_observacion, values=self.observacion_options)
        self.menu_observacion.grid(row=1, column=1, padx=(10), pady=(10,5))

        self.boton_enviar = ctk.CTkButton(self.root, text="Enviar", command=self.enviar , width=80)
        self.boton_enviar.grid(row=3, column=1, padx=5, pady=5, sticky="e")

        self.boton_anterior = ctk.CTkButton(self.root, text="< Anterior", command=self.anterior , width = 80)
        self.boton_anterior.grid(row=3, column=0, padx=5, pady=5, sticky="e")

        self.boton_siguiente = ctk.CTkButton(self.root, text="Siguiente >", command=self.siguiente , width = 80)
        self.boton_siguiente.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.contador_label = ctk.CTkLabel(self.root, text="")
        self.contador_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.fuente_entry_id = ctk.CTkFont(family="Arial", size=13)
        self.entry_id = ctk.CTkEntry(self.root, placeholder_text="Ingresar ID", font=self.fuente_entry_id, width=180)
        self.entry_id.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        try:
            self.entry_id.insert(0 , self.planilla.row_actual.iloc[2])
        except:
            self.entry_id.insert(0 , "")
            pass
        self.entry_id.xview_moveto(1)
        #Atajos
        self.root.bind('<Down>', lambda event: self.siguiente())
        self.root.bind('<Up>', lambda event: self.anterior())
        self.root.bind('<Return>' , lambda event: self.enviar())

    def cambiar_color_mode(self):
        # Obtener el modo actual y cambiarlo
        modo_actual = ctk.get_appearance_mode()
        if modo_actual == "Dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")
        self.root.update()
    
    
    
    def actualizar_estado_worker(self):
        pendientes = self.planilla.tareas_pendientes()
        
        if pendientes > 0:
            texto_estado = f"Tareas pendientes: {pendientes + 1}"
        else:
            texto_estado = "Actualizado"
        
        self.estado_worker.configure(text=texto_estado)
        self.root.after(1000, self.actualizar_estado_worker)

    
    def enviar(self):
        resultado_seleccionado = self.dropdown_resultado.get()
        observacion_seleccionada = self.dropdown_observacion.get()
        id_seleccionado = self.entry_id.get()
        self.planilla.prog_actualizar_celda(resultado_seleccionado, observacion_seleccionada, id_seleccionado)
        self.dropdown_resultado.set("")
        self.dropdown_observacion.set("")
        self.siguiente_o_cerrar()

    
    def siguiente_o_cerrar(self):
        if self.item_actual < self.total_items:
            self.siguiente()
        else:
            # Espera a que se completen todas las tareas pendientes antes de cerrar
            self.planilla.esperar_tasks()
            messagebox.showinfo("Mensaje", "No hay más items")
            self.ventanas.abrir_url(self.ventanas.ventana_1, "https://www.google.com")
            self.ventanas.abrir_url(self.ventanas.ventana_2, "https://www.google.com")
            contador_text = f"No hay items"
            self.contador_label.configure(text=contador_text)
            self.entry_id.delete(0, 'end')
            
    def siguiente(self):
        self.planilla.siguiente_fila()
        url1 = self.planilla.row_actual.iloc[0]
        print(url1)
        url2 = self.planilla.row_actual.iloc[1]
        print(url2)
        self.entry_id.delete(0 , tk.END)
        self.entry_id.insert(0 , self.planilla.row_actual.iloc[2])
        self.entry_id.xview_moveto(1)
        self.ventanas.actualizar_ventanas(url1, url2)
        self.item_actual += 1
        self.actualizar_contador()

    def anterior(self):
        self.planilla.anterior_fila()
        url1 = self.planilla.row_actual.iloc[0]
        url2 = self.planilla.row_actual.iloc[1]
        self.entry_id.delete(0 , tk.END)
        self.entry_id.insert(0 , self.planilla.row_actual.iloc[2])
        self.entry_id.xview_moveto(1)
        self.ventanas.actualizar_ventanas(url1, url2)
        self.item_actual -= 1
        self.actualizar_contador()

    def actualizar_contador(self):
        if self.total_items == 0:
            contador_text = f"No hay items"
            self.contador_label.configure(text=contador_text)
        else:
            contador_text = f"Item {self.item_actual} de {self.total_items}"
            self.contador_label.configure(text=contador_text)

    def crear_menu(self):
        barra_menu = tk.Menu(self.root, bg='gray20', fg='white', bd=0, relief=tk.FLAT)
        self.root.config(menu=barra_menu)  # Asignar la barra de menú a la ventana principal

        # Crear un menú "Archivo"
        menu_archivo = tk.Menu(barra_menu, tearoff=0, bg='gray20', fg='white')
        menu_archivo.add_command(label="Actualizar", command=self.actualizar_datos)
        barra_menu.add_cascade(label="Archivo", menu=menu_archivo)
        # Crear un menú "Editar"
        menu_editar = tk.Menu(barra_menu, tearoff=0, bg='gray20', fg='white')
        menu_editar.add_command(label="Cambiar Tema", command=self.cambiar_color_mode)
        menu_editar.add_command(label="Recuperar Ventanas", command=self.recuperar_ventanas)
        menu_editar.add_command(label="Mostrar fila",command=self.mostrar_fila)
        barra_menu.add_cascade(label="Editar", menu=menu_editar)

    def actualizar_datos(self):
        self.planilla.actualizar_datos()
        self.items_totales()
        self.item_actual = 1
        self.actualizar_contador()
        self.entry_id.delete(0, "end")
        if self.total_items == 0:
            self.ventanas.abrir_url(self.ventanas.ventana_1, "https://www.google.com")
            self.ventanas.abrir_url(self.ventanas.ventana_2, "https://www.google.com")
        else:
            self.ventanas.actualizar_ventanas(self.planilla.row_actual.iloc[0], self.planilla.row_actual.iloc[1])
        try:
            if self.total_items != 0:
                self.entry_id.insert(0 , self.planilla.row_actual.iloc[2])
            else:
                pass
        except:
            self.entry_id.insert(0 , "")
            pass
        
    
    def actualizar_observaciones(self, *args):
        resultado_seleccionado = self.dropdown_resultado.get()
        observacion_options = self.observaciones.get(resultado_seleccionado, [""])

        # Eliminar el menú de observación anterior y crear uno nuevo
        if hasattr(self, 'menu_observacion'):
            self.menu_observacion.grid_forget()
        self.menu_observacion = ctk.CTkOptionMenu(self.root, variable=self.dropdown_observacion, values=observacion_options)
        self.menu_observacion.grid(row=1, column=1, padx=(10), pady=(10,5))
        self.dropdown_observacion.set("")

    def recuperar_ventanas(self):
        self.ventanas.cerrar_ventanas()
        try:
            print(self.total_items)
            if self.total_items == 0:
                url1 = "https://www.google.com"
                url2 = "https://www.google.com"
            else:
                url1=self.planilla.row_actual.iloc[0]
                url2=self.planilla.row_actual.iloc[1]
            self.ventanas = Ventanas(url1,url2)
        except Exception as e:
            print(f"Error al reiniciar las ventanas: {e}")
            self.ventanas = Ventanas("https://www.google.com", "https://www.google.com")


    def cerrar_interfaz(self):
        self.planilla.esperar_tasks()
        self.planilla.close()
        self.ventanas.cerrar_ventanas()
        self.root.destroy()
        

    def items_totales(self):
        self.total_items= 0
        for i in range(len(self.planilla.dataframes)):
            self.total_items += len(self.planilla.dataframes[i][0])
    
    def mostrar_fila(self):
        messagebox.showinfo("Mensaje", f"Estas en la fila {self.planilla.index_actual + 1}")