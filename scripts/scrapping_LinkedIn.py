import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configuración para usar Brave
options = Options()
options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
# Descomenta la siguiente línea si deseas ver la ventana del navegador (para depuración)
# options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

service = Service(r"C:\Users\Pablo\OneDrive\Escritorio\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

wait = WebDriverWait(driver, 30)

# Configuración de ruta para guardar el archivo
directorio_guardado = r"C:\Users\Pablo\OneDrive - Universidad Loyola Andalucía\Master\TFM\Ofertas"
puesto = "Ingeniero de datos"
pais = "España"

# Formatear el nombre del archivo reemplazando espacios por guiones bajos
nombre_archivo = f"{puesto.replace(' ', '_')}_{pais.replace(' ', '_')}.txt"
ruta_archivo = os.path.join(directorio_guardado, nombre_archivo)

try:
    # 1. Iniciar sesión en LinkedIn
    driver.get("https://www.linkedin.com/login")
    wait.until(EC.presence_of_element_located((By.ID, "username")))
    driver.find_element(By.ID, "username").send_keys("pablo74213@gmail.com")
    driver.find_element(By.ID, "password").send_keys("MarCaspio41500")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    
    wait.until(EC.presence_of_element_located((By.ID, "global-nav-search")))
    time.sleep(3)  # Tiempo adicional para asegurarse de que la sesión se ha iniciado correctamente

    # 2. Navegar a la búsqueda de empleo
    url_busqueda = (
        f"https://www.linkedin.com/jobs/search/?keywords={puesto.replace(' ', '%20')}"
        f"&location={pais.replace(' ', '%20')}"
    )
    driver.get(url_busqueda)
    time.sleep(5)  # Espera para que se cargue la página de búsqueda

    # 3. Realizar scroll para cargar el contenido (si es necesario)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    print("Se ha cargado la página de búsqueda de empleo.")

    # 4. Esperar a que se cargue el contenedor de ofertas usando el nuevo selector
    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "ul.RLVTwvQwnVBxucGSNGoIBhQZLZnJtkHmrEQQU")
    ))

    print("Se ha cargado el contenedor de ofertas.")

    # Extraer todos los <li> que representan cada oferta
    ofertas = driver.find_elements(By.CSS_SELECTOR, "ul.RLVTwvQwnVBxucGSNGoIBhQZLZnJtkHmrEQQU > li")
    print(f"Se han encontrado {len(ofertas)} ofertas.")

    # Abrir archivo para escritura
    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        for idx, oferta in enumerate(ofertas[:5]):  # Solo las primeras 5 ofertas
            try:
                try:
                    titulo = oferta.find_element(By.CSS_SELECTOR, "a.job-card-container__link").text
                except Exception as e:
                    titulo = "No disponible"
                    print(f"Error al extraer el título de la oferta {idx+1}: {e}")

                try:
                    empresa = oferta.find_element(By.CSS_SELECTOR, "div.artdeco-entity-lockup__subtitle").text
                except Exception as e:
                    empresa = "No especificada"
                    print(f"Error al extraer la empresa de la oferta {idx+1}: {e}")


                # Hacer clic en la oferta para ver los detalles
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", oferta)
                time.sleep(1)
                oferta.click()
                time.sleep(3)  # Esperar a que se cargue la descripción

                # Extraer la descripción de la oferta
                descripcion_elemento = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.jobs-box__html-content.jobs-description-content__text--stretch")
                ))
                descripcion = descripcion_elemento.text

                # Escribir en el archivo
                archivo.write(f"Oferta {idx+1}\n")
                archivo.write(f"Puesto: {titulo}\n")
                archivo.write(f"Empresa: {empresa}\n")
                archivo.write(f"Descripción:\n{descripcion}\n")
                archivo.write(f"{'-'*40}\n")

                print(f"\nOferta {idx+1} guardada en {nombre_archivo}\n")

            except Exception as e:
                print(f"Error al procesar la oferta {idx+1}: {e}")
                continue

except Exception as ex:
    print("Se ha producido un error:", ex)
finally:
    driver.quit()
    print(f"Las ofertas han sido guardadas en: {ruta_archivo}")
