import sys
from playwright.sync_api import sync_playwright, Page, expect

class AparcarePlaywrightApp:
    page: Page
    
    def __enter__(self):
        self.playwright = sync_playwright().start()
        chromium = self.playwright.chromium
        self.browser = chromium.launch()
        self.page = self.browser.new_page()
        self.page.goto("https://aparcare.com/#/login")
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.browser.close()
        self.playwright.stop()

    def accept_cookies(self):
        self.page.get_by_role("button", name="De acuerdo").click()

    def login(self, city, email, password):
        self.page.get_by_role("button", name="Escoge tu ciudad").click()
        self.page.get_by_text(city).click()
        self.page.get_by_placeholder("E-mail").fill(email)
        self.page.get_by_placeholder("Contraseña").fill(password)

        self.page.get_by_role("button", name="Iniciar sesión").click()
        expect(self.page).to_have_url("https://aparcare.com/#/ticket")

    def exists(self, element):
        try:
            element.wait_for(timeout=1000)
            return True
        except: return False

    def renovate_ticket(self, car):
        self.page.get_by_role("combobox").filter(has_text="-- Seleccione una zona IGUALADA--").select_option("VEHICLE 0 EMISIONS")
        self.page.get_by_text("Seleccione un vehículo").click()
        self.page.get_by_text(car).click()
        self.page.get_by_role("button", name="Max").click()
        expect(self.page.get_by_text("1 h. 30 m.")).to_be_visible()
        self.page.get_by_role("button", name="Obtener ticket").click()
        expect(self.page.get_by_text("Importe pago - 0.00€")).to_be_visible()
        self.page.get_by_role("button", name="Comprar").click()
        double_confirmation_button = self.page.get_by_role("button", name="Comprar")
        if (self.exists(double_confirmation_button)):
            double_confirmation_button.click()

    def confirm_renovated(self):
        expect(self.page.get_by_text("Comprobante de estacionamiento")).to_be_visible()
        start_time = self.page.locator(".row", has=self.page.get_by_text("Inicio ticket:")).inner_text()
        end_time = self.page.locator(".row", has=self.page.get_by_text("Final ticket:")).inner_text()
        email = self.page.locator(".row", has=self.page.get_by_text("E-mail:")).inner_text()
        print(start_time)
        print(end_time)
        print(email)

    def run(self, city, email, password, car):
        self.accept_cookies()
        self.login(city, email, password)
        self.renovate_ticket(car)
        self.confirm_renovated()

def main(argv):
    if len(argv) != 4:
        print("Usage: python3 renovate_ticket.py <city> <email> <password> <car>")
        exit()
    city, email, password, car = argv
    with AparcarePlaywrightApp() as app:
        app.run(city, email, password, car)

if __name__ == "__main__":
    main([i for i in sys.argv[1:] if i])
