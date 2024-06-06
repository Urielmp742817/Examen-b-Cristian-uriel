import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from gpiozero import Button, LED, Servo
import threading
import time

class CircleLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(50, 50)
        self.update_color(False)  # Establecer el color inicial
        self.setAlignment(Qt.AlignCenter)

    def update_color(self, active):
        if active:
            self.setStyleSheet('background-color: green; color: white;')
        else:
            self.setStyleSheet('background-color: red; color: white;')

class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_gpio()

    def init_ui(self):
        self.layout = QGridLayout(self)

        # Entradas
        self.hs01_button = CircleLabel('HS-01')
        self.hs02_button = CircleLabel('HS-02')
        self.hs03_button = QPushButton('HS-03')  # Botón virtual para HS-03
        
        # Salidas
        self.pl01_led = CircleLabel('PL-01')
        self.pl02_led = CircleLabel('PL-02')
        
        # Setup grid
        self.layout.addWidget(QLabel('Entradas'), 0, 0, Qt.AlignCenter)
        self.layout.addWidget(QLabel('Salidas'), 0, 1, Qt.AlignCenter)
        self.layout.addWidget(self.hs01_button, 1, 0, Qt.AlignCenter)
        self.layout.addWidget(self.hs02_button, 2, 0, Qt.AlignCenter)
        self.layout.addWidget(self.hs03_button, 3, 0, Qt.AlignCenter)
        self.layout.addWidget(self.pl01_led, 1, 1, Qt.AlignCenter)
        self.layout.addWidget(self.pl02_led, 2, 1, Qt.AlignCenter)

        self.setWindowTitle('Interfaz de Control')
        self.setGeometry(100, 100, 300, 200)

    def init_gpio(self):
        # Configurar botones físicos
        self.hs01_button_gpio = Button(17)  # GPIO 17 para hs-01
        self.hs02_button_gpio = Button(27)  # GPIO 27 para hs-02
        
        # Configurar Servo en lugar de LED
        self.pl01 = Servo(5)  # GPIO 5 para pl-01
        self.pl02 = LED(6)    # GPIO 6 para pl-02

        # Conectar eventos de botones físicos a métodos
        self.hs01_button_gpio.when_pressed = self.hs01_pressed
        self.hs01_button_gpio.when_released = self.hs_released
        self.hs02_button_gpio.when_pressed = self.hs02_pressed
        self.hs02_button_gpio.when_released = self.hs_released

        # Conectar evento de botón virtual a método
        self.hs03_button.clicked.connect(self.toggle_hs03)

        # Variables para controlar el parpadeo de pl-02
        self.pl02_blinking = False
        self.pl02_thread = threading.Thread(target=self.blink_pl02)

    def hs01_pressed(self):
        self.hs01_button.update_color(True)
        if self.hs03_button.text() == 'HS-03 Activo':  # Solo activa la salida si hs-03 está activo
            self.move_servo(self.pl01, 1)  # Mover servo a posición 1 (máximo)
            self.pl01_led.update_color(True)
            threading.Timer(5, self.deactivate_pl01).start()
        else:
            self.move_servo(self.pl01, 0.5)  # Mover servo a posición intermedia (0.5)
            self.pl01_led.update_color(True)
            threading.Timer(10, self.deactivate_pl01).start()

    def deactivate_pl01(self):
        self.move_servo(self.pl01, -1)  # Mover servo a posición -1 (mínimo)
        self.pl01_led.update_color(False)

    def hs02_pressed(self):
        self.hs02_button.update_color(True)
        if not self.pl02_blinking:
            self.pl02_blinking = True
            if not self.pl02_thread.is_alive():
                self.pl02_thread = threading.Thread(target=self.blink_pl02)
                self.pl02_thread.start()
        else:
            self.pl02_blinking = False
            self.pl02.off()
            self.pl02_led.update_color(False)

    def hs_released(self):
        self.hs01_button.update_color(False)
        self.hs02_button.update_color(False)

    def toggle_hs03(self):
        if self.hs03_button.text() == 'HS-03':  # Comprueba el texto del botón para determinar su estado
            self.hs03_button.setText('HS-03 Activo')
            self.hs03_button.setStyleSheet('background-color: green; color: white;')
        else:
            self.hs03_button.setText('HS-03')
            self.hs03_button.setStyleSheet('background-color: red; color: white;')

    def blink_pl02(self):
        while self.pl02_blinking:
            self.pl02.on()
            self.pl02_led.update_color(True)  # Actualizar color de pl02_led
            time.sleep(3)  # Encender pl-02 durante 3 segundos
            self.pl02.off()
            self.pl02_led.update_color(False)  # Actualizar color de pl02_led
            time.sleep(1)  # Apagar pl-02 durante 1 segundo

    def move_servo(self, servo, position):
        servo.value = position

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VentanaPrincipal()
    window.show()
    sys.exit(app.exec_())
