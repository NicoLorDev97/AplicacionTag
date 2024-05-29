from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pandas import DataFrame
import queue
import threading
import time
from tkinter import messagebox

class Planilla():
    def __init__(self, spreadsheet_name , valor_filtro):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope)
        self.client = gspread.authorize(creds)
        self.cola_trabajo = queue.Queue()
        self.worker_thread = threading.Thread(target=self.worker)
        self.worker_thread.start()
        self.spreadsheet_name = spreadsheet_name
        self.fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        self.valor_filtro = valor_filtro
        self.today_sheets = self.procesar_hojas() # Atributo para modificar el google sheets
        self.hoja_actual = None # Que hoja estoy mostrando en Ventanas
        self.index_actual = None # Que index estoy mostrando en Ventanas
        self.row_actual = None # Fila que debo mostrar en ventana
        self.obtener_datos()
        self.filtrar_datos()

### ###### ###### ###### ###### ###### ###### ###### ###### ######

#### OBTENCION Y FILTRADO DE DATOS ####  
    
    def obtener_celula(self):
        celulas = self.client.open_by_url('https://docs.google.com/spreadsheets/d/1zZDaemdx5IABjMUAu9rqsgXomFoGBMNbrLFNFfvnTSY/edit#gid=0')
        celulas = celulas.worksheet("Hojas")
        celulas = celulas.get_all_values()
        plani_tag = self.client.open_by_url(str(celulas[int(self.spreadsheet_name) - 1]))
        self.spreadsheet_name = plani_tag.title
        print(self.spreadsheet_name)


    def procesar_hojas(self):
        self.obtener_celula()
        today_sheets = []
        spreadsheet = self.client.open(self.spreadsheet_name)
        all_sheets = spreadsheet.worksheets()
        for sheet in all_sheets:
            if self.fecha_hoy in sheet.title:
                today_sheets.append(sheet)
        if not today_sheets:
            raise ValueError("No se encontraron items")
        return today_sheets
        
    def obtener_datos(self):
        dataframes = []
        for sheet in self.today_sheets:
            dataframes.append([DataFrame(sheet.get_all_values()), sheet.title])
        self.dataframes = dataframes #Atributo para iterar en el objeto Planilla

    def mgl_mobile(self, url):
        if "magazineluiza" in url:
            if "m.magazineluiza" not in url:
                if "www." in url:
                    return url.replace("https://www.", "https://m.")
                else:
                    return url.replace("https://", "https://m.")
        return url

    def filtrar_datos(self):
        try:
            for i, hoja in enumerate(self.dataframes):
                hoja[0].iloc[:, 6] = hoja[0].iloc[:, 6].apply(self.mgl_mobile)
                self.dataframes[i][0] = hoja[0][(hoja[0].iloc[:, 11] == self.valor_filtro) & (hoja[0].iloc[:, 9] == "")].iloc[:, [4, 5, 6, 9, 10, 11]]
            for i in range(len(self.dataframes) - 1):
                if self.dataframes[i][0].empty:
                    self.dataframes.pop(i)
            self.hoja_actual = self.dataframes[0][1]      #Inicializar el atributo de hoja actual
            self.index_actual = self.dataframes[0][0].iloc[0].name #Inicializar el atributo de indice actual
            self.row_actual = self.dataframes[0][0].iloc[0]
            print(self.row_actual.iloc[0])
        except IndexError:
            messagebox.showinfo("Error", "No hay datos actualizados disponibles.")
            pass


    def actualizar_datos(self):
        self.dataframes.clear()
        self.obtener_datos()
        self.filtrar_datos()


### ###### ###### ###### ###### ###### ###### ###### ###### ######

#### ACTUALIZACION Y EJECUCION DE PILA DE TAREAS ####

    def worker(self):
        while True:
            task = self.cola_trabajo.get()
            if task is None:
                break
            func, args = task
            func(*args)
            self.cola_trabajo.task_done()

    def agregar_tarea(self, func, *args):
        self.cola_trabajo.put((func, args))


    def actualizar_celda(self, resultado, observacion, entry_id, today_sheets, hoja_actual , index_actual):
        for sheet in today_sheets:
            if sheet.title == hoja_actual:
                row_index = index_actual + 1
                cell_range = f'A{row_index}:P{row_index}'
                cells = sheet.range(cell_range)
                
                cells[6].value = entry_id
                cells[9].value = resultado
                if observacion:
                    cells[10].value = observacion
                cells[15].value = datetime.now().strftime("%H:%M:%S")


                updated_cells = [cells[6], cells[9], cells[15]]
                if observacion:
                    updated_cells.append(cells[10])
                sheet.update_cells(updated_cells)
                break


    def prog_actualizar_celda(self, resultado, observacion, entry_id):
        
        self.agregar_tarea(self.actualizar_celda, resultado, observacion, entry_id, self.today_sheets, self.hoja_actual , self.index_actual)


    def esperar_tasks(self):
        self.cola_trabajo.join()
    
    #CONSULTA
    def tareas_pendientes(self):
        return self.cola_trabajo.qsize()
    


### FUNCIONES DE ITERACIÓN Y CIERRE ###### ###### ###### ######

    def siguiente_fila(self):
        #En que hoja estoy parado
        for item in self.dataframes:
            if item[1] == self.hoja_actual:
                dataframe = item[0]
                for index, row in dataframe.iterrows():
                    if index > self.index_actual:
                        self.row_actual = row
                        self.index_actual = index
                        break
                    elif index == dataframe.iloc[-1].name:
                        self.siguiente_hoja()
                        break
                break

    def anterior_fila(self):
        # En qué hoja estoy parado
        for item in self.dataframes:
            if item[1] == self.hoja_actual:
                dataframe = item[0]
                for index, row in dataframe[::-1].iterrows():
                    if index < self.index_actual:
                        self.row_actual = row
                        self.index_actual = index
                        break
                    elif index == dataframe.iloc[0].name:
                        self.anterior_hoja()
                        break
                break

    def siguiente_hoja(self):
        for i, hoja in enumerate(self.dataframes):
            if self.hoja_actual == hoja[1]:
                try:
                    lista = self.dataframes[i+1]
                    self.hoja_actual = lista[1]
                    self.row_actual = lista[0].iloc[0]
                    self.index_actual = self.row_actual.name
                except:
                    continue

    def anterior_hoja(self):
        for i, hoja in enumerate(self.dataframes):
            if self.hoja_actual == hoja[1]:
                try:
                    if i > 0:
                        lista = self.dataframes[i-1]
                        self.hoja_actual = lista[1]
                        self.row_actual = lista[0].iloc[-1]
                        self.index_actual = self.row_actual.name
                except:
                    continue

    def close(self):
        self.cola_trabajo.put(None)
        self.worker_thread.join()  