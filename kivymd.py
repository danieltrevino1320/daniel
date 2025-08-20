from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.list import OneLineListItem
from kivy.lang import Builder
import json, os

# -------------------
# MODELO
# -------------------
DATA_FILE = "cuentas.json"

class Cuenta:
    def __init__(self, numero, nombre, saldo=0):
        self.numero = numero
        self.nombre = nombre
        self.saldo = saldo

    def ingreso(self, monto):
        self.saldo += monto

    def egreso(self, monto):
        if monto <= self.saldo:
            self.saldo -= monto
            return True
        return False

    def to_dict(self):
        return {"numero": self.numero, "nombre": self.nombre, "saldo": self.saldo}

class BancoModel:
    def __init__(self):
        self.cuentas = []
        self.cargar()

    def cargar(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.cuentas = [Cuenta(**c) for c in data]
        else:
            # Cuentas iniciales
            self.cuentas = [
                Cuenta(1, "Cuenta A", 1000),
                Cuenta(2, "Cuenta B", 2000),
                Cuenta(3, "Cuenta C", 1500),
            ]
            self.guardar()

    def guardar(self):
        with open(DATA_FILE, "w") as f:
            json.dump([c.to_dict() for c in self.cuentas], f, indent=4)

    def get_cuentas(self):
        return self.cuentas

    def get_cuenta(self, numero):
        for c in self.cuentas:
            if c.numero == numero:
                return c
        return None

# -------------------
# CONTROLADOR
# -------------------
class BancoController:
    def __init__(self):
        self.model = BancoModel()

    def listar_cuentas(self):
        return self.model.get_cuentas()

    def hacer_ingreso(self, numero, monto):
        cuenta = self.model.get_cuenta(numero)
        if cuenta:
            cuenta.ingreso(monto)
            self.model.guardar()
            return True
        return False

    def hacer_egreso(self, numero, monto):
        cuenta = self.model.get_cuenta(numero)
        if cuenta and cuenta.egreso(monto):
            self.model.guardar()
            return True
        return False

# -------------------
# VISTA (KV Language)
# -------------------
KV = '''
ScreenManager:
    MenuScreen:
    OperacionScreen:

<MenuScreen>:
    name: "menu"

    BoxLayout:
        orientation: "vertical"
        MDToolbar:
            title: "Sistema Bancario"
            elevation: 10

        ScrollView:
            MDList:
                id: lista_cuentas

        MDRaisedButton:
            text: "Actualizar"
            pos_hint: {"center_x": 0.5}
            on_release: app.mostrar_cuentas()

<OperacionScreen>:
    name: "operacion"
    cuenta_num: 0

    BoxLayout:
        orientation: "vertical"
        MDToolbar:
            id: titulo
            title: "Operación"
            left_action_items: [["arrow-left", lambda x: app.ir_menu()]]

        MDTextField:
            id: monto
            hint_text: "Ingrese monto"
            input_filter: "int"
            mode: "rectangle"

        BoxLayout:
            size_hint_y: None
            height: "56dp"
            spacing: 10
            MDRaisedButton:
                text: "Ingresar"
                on_release: app.ingreso(root.cuenta_num, monto.text)
            MDRaisedButton:
                text: "Egresar"
                on_release: app.egreso(root.cuenta_num, monto.text)
'''

class MenuScreen(Screen):
    pass

class OperacionScreen(Screen):
    cuenta_num = 0

# -------------------
# APLICACIÓN PRINCIPAL
# -------------------
class BancoApp(MDApp):
    def build(self):
        self.controller = BancoController()
        return Builder.load_string(KV)

    def on_start(self):
        self.mostrar_cuentas()

    def mostrar_cuentas(self):
        lista = self.root.get_screen("menu").ids.lista_cuentas
        lista.clear_widgets()
        for c in self.controller.listar_cuentas():
            item = OneLineListItem(
                text=f"{c.numero} - {c.nombre}: ${c.saldo}",
                on_release=lambda x, cuenta=c: self.ir_operacion(cuenta)
            )
            lista.add_widget(item)

    def ir_operacion(self, cuenta):
        op_screen = self.root.get_screen("operacion")
        op_screen.cuenta_num = cuenta.numero
        op_screen.ids.titulo.title = f"Cuenta {cuenta.numero} - {cuenta.nombre}"
        self.root.current = "operacion"

    def ir_menu(self):
        self.root.current = "menu"
        self.mostrar_cuentas()

    def ingreso(self, numero, monto):
        if monto.isdigit():
            self.controller.hacer_ingreso(numero, int(monto))
            self.ir_menu()

    def egreso(self, numero, monto):
        if monto.isdigit():
            self.controller.hacer_egreso(numero, int(monto))
            self.ir_menu()

if __name__ == "__main__":
    BancoApp().run()
