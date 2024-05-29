import undetected_chromedriver as uc
import threading
import os
from concurrent.futures import ThreadPoolExecutor

class Ventanas():
    def __init__(self, url1, url2):
        options = uc.ChromeOptions()
        path_hound = f"{os.getcwd()}//hound-companion-12"
        path_adblock = f"{os.getcwd()}//adblock"
        path_urban = f"{os.getcwd()}//urban"
        options.add_argument(f'--load-extension={path_hound},{path_adblock},{path_urban}')
        user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"
        options.add_argument(f'user-agent={user_agent}')
        self.ventana_1 = uc.Chrome()
        self.ventana_2 = uc.Chrome(options=options)
        self.configurar_ventanas()
        self.actualizar_ventanas(url1, url2)

    def configurar_ventanas(self):
        screen_width = self.ventana_1.execute_script("return window.screen.availWidth")
        screen_height = self.ventana_1.execute_script("return window.screen.availHeight")
        self.ventana_1.set_window_size(screen_width // 2, screen_height)
        self.ventana_1.set_window_position(0, 0)
        self.ventana_2.set_window_size(screen_width // 2, screen_height)
        self.ventana_2.set_window_position(screen_width // 2, 0)

    def abrir_url(self, ventana, url):
        try:
            ventana.get(url)
        except Exception as e:
            print(f"Error al abrir URL {url}: {str(e)}")

    def actualizar_ventanas(self, url1, url2):
            with ThreadPoolExecutor(max_workers=2) as executor:
                executor.submit(self.abrir_url, self.ventana_1, url1)
                executor.submit(self.abrir_url, self.ventana_2, url2)

    def cerrar_ventanas(self):
        try:
            self.ventana_1.quit()
        except Exception as e:
            print(f"Error al cerrar ventana 1: {e}")
        try:
            self.ventana_2.quit()
        except Exception as e:
            print(f"Error al cerrar ventana 2: {e}")