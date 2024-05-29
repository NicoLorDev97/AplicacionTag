import customtkinter as ctk
from Interfaz_trabajo import Interfaz_trabajo
from tkinter import messagebox
from PIL import Image
import os

class InterfazCarga():
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("AppTags")
        self.inicializar_interfaz() 
        self.root.mainloop()

    def inicializar_interfaz(self):
        self.configurar_tamano_interfaz()
        self.crear_componentes_interfaz()

    def configurar_tamano_interfaz(self):
        self.root.iconbitmap(f"{os.getcwd()}//Iconos//logo.ico")
        self.root.attributes('-topmost', True)
        ventana_configuracion_x = self.root.winfo_screenwidth() // 2 - 300
        ventana_configuracion_y = self.root.winfo_screenheight() // 2 - 240
        self.root.geometry(f"600x480+{ventana_configuracion_x}+{ventana_configuracion_y}")
        self.root.resizable(0, 0)

    def crear_componentes_interfaz(self):
        # Carga de imágenes / Iconos
        imagen = Image.open(f"{os.getcwd()}//Iconos//Imagen_GK.png")
        icono_usuario_img = Image.open(f"{os.getcwd()}//Iconos//icono_usuario.png")
        icono_plani_img = Image.open(f"{os.getcwd()}//Iconos//icono_planilla.png")
        img = ctk.CTkImage(dark_image=imagen, light_image=imagen, size=(300, 480))
        usuario_icon = ctk.CTkImage(dark_image=icono_usuario_img, light_image=icono_usuario_img, size=(20,20))
        plani_icon = ctk.CTkImage(dark_image=icono_plani_img, light_image=icono_plani_img, size=(20,20))

        #Imagen del costado
        ctk.CTkLabel(master=self.root, text="", image=img).pack(expand=True, side="left")
        frame = ctk.CTkFrame(master=self.root, width=300, height=480, fg_color="#ffffff")
        frame.pack_propagate(0)
        frame.pack(expand=True, side="right")

        #Titulos
        ctk.CTkLabel(master=frame, text="¡Bienvenido!", text_color="#601E88", anchor="w", justify="left", font=("Arial Bold", 24)).pack(anchor="w", pady=(50, 5), padx=(25, 0))
        ctk.CTkLabel(master=frame, text="Seleccione su Planilla y Usuario de trabajo", text_color="#7E7E7E", anchor="w", justify="left", font=("Arial Bold", 12)).pack(anchor="w", padx=(25, 0))
        ctk.CTkLabel(master=frame, text="  Usuario:", text_color="#601E88", anchor="w", justify="left", font=("Arial Bold", 14), image=usuario_icon, compound="left").pack(anchor="w", pady=(38, 0), padx=(25, 0))
        
        #Inputs
        filtro_entry = ctk.CTkEntry(master=frame, width=225, fg_color="#EEEEEE", border_color="#601E88", border_width=1, text_color="#000000")
        filtro_entry.pack(anchor="w", padx=(25, 0))
        ctk.CTkLabel(master=frame, text="  Planilla:", text_color="#601E88", anchor="w", justify="left", font=("Arial Bold", 14), image=plani_icon, compound="left").pack(anchor="w", pady=(21, 0), padx=(25, 0))
        spreadsheet_name_entry = ctk.CTkEntry(master=frame, width=225, fg_color="#EEEEEE", border_color="#601E88", border_width=1, text_color="#000000")
        spreadsheet_name_entry.pack(anchor="w", padx=(25, 0))
        
        #Confirmar
        ctk.CTkButton(master=frame, text="Confirmar", fg_color="#601E88", hover_color="#E44982", font=("Arial Bold", 12), text_color="#ffffff", width=225, command=lambda: self.generar_salida(spreadsheet_name_entry.get(), filtro_entry.get())).pack(anchor="w", pady=(40, 0), padx=(25, 0))
        self.root.bind('<Return>' , lambda event: self.generar_salida(spreadsheet_name_entry.get(),filtro_entry.get()))

    def generar_salida(self, spreadsheet_name_entry, filtro_entry):
        if not spreadsheet_name_entry or not filtro_entry:
            messagebox.showerror("Error", "Por favor ingrese valores válidos")
        else:
            self.root.destroy()
            trabajo = Interfaz_trabajo(spreadsheet_name_entry, filtro_entry)

if __name__ == "__main__":
    interfaz_carga = InterfazCarga()