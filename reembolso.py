import time
from playwright.sync_api import Playwright, sync_playwright
from datetime import datetime
import locale
from fastapi import FastAPI, Response, status
import uvicorn

app = FastAPI()
contador = 1

def takescreenshot(page, error=None):
    global contador
    timestamp = datetime.now().strftime("%Y-%m-%d:%H:%M:%S")
    if error is None:
        page.screenshot(path=f"paso_{contador}_{timestamp}.png")
    else:
        page.screenshot(path=f"error_{contador}_{timestamp}_ERROR.png")
    print(f"DEBUG: paso {contador}")
    contador += 1

def run_playwright() -> bool:
    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
    mes = datetime.now().strftime("%B")
    anio = datetime.now().year

    browser = None
    context = None
    try:
        with sync_playwright() as playwright:
            print("Iniciando navegador...")
            browser = playwright.firefox.launch(headless=True)
            print("Navegador iniciado.")
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            print("Contexto creado.")
            page = context.new_page()
            page.set_default_timeout(30000)
            page.goto("https://login.helpseguros.cl/login")
            time.sleep(3)
            page.get_by_label("RUT").fill("xxx")
            page.get_by_label("Contraseña").click()
            page.get_by_label("Contraseña").fill("xxx")
            takescreenshot(page)
            page.get_by_role("button", name="INGRESAR").click()
            time.sleep(20)
            takescreenshot(page)
            page.get_by_role("link", name="Mis reembolsos").click()
            page.get_by_role("link", name="Solicitar reembolso").click()
            page.locator("#pandoraBox").content_frame.get_by_label("Open calendar").click()
            page.locator("#pandoraBox").content_frame.get_by_label(f"1 de {mes} de {anio}", exact=True).click()
            page.locator("#pandoraBox").content_frame.get_by_text("arrow_drop_down").click()
            page.locator("#pandoraBox").content_frame.get_by_text("AO").click()
            takescreenshot(page)
            page.locator("#pandoraBox").content_frame.get_by_role("button", name="Iniciar chevron_right").click()
            page.locator("#pandoraBox").content_frame.get_by_text("Consulta Médica").click()
            frame = page.frame_locator("#pandoraBox")
            upload = frame.locator("app-upload-file", has_text="cloud_upload Liquidación o")
            upload.locator('input[type="file"]').set_input_files("MONITOREO-GERENCIA-SISTEMAS.pdf")
            time.sleep(3)
            takescreenshot(page)
            upload = frame.locator("app-upload-file", has_text="cloud_upload Boleta - Voucher")
            upload.locator('input[type="file"]').set_input_files("MONITOREO-GERENCIA-SISTEMAS.png")
            time.sleep(3)
            takescreenshot(page)
            page.locator("#pandoraBox").content_frame.get_by_role("button", name="Continuar chevron_right").click()
            page.locator("#pandoraBox").content_frame.get_by_text("AO", exact=True).click()
            takescreenshot(page)
            page.locator("#pandoraBox").content_frame.get_by_role("button", name="Continuar chevron_right").click()
            page.locator("#pandoraBox").content_frame.get_by_text("Acepto los Términos y").click()
            page.locator("#pandoraBox").content_frame.get_by_label("Close").click()
            time.sleep(3)
            takescreenshot(page)
        return True
    except Exception as e:
        print(f"Error: {e}")
        if 'page' in locals():
            takescreenshot(page, error=True)
        return False
    #finally:
        #if context:
        #    context.close()
        #if browser:
        #    browser.close()

@app.get("/run-reembolso")
def run_reembolso(response: Response):
    success = run_playwright()
    if success:
        response.status_code = status.HTTP_200_OK
        return {"message": "Proceso completado correctamente"}
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": "Error en el proceso"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
