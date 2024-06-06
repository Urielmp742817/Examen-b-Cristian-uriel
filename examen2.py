import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from gpiozero import Button, LED

class CircleLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(50, 50)
        self.setStyleSheet('background-color: red; color: white;')
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
        self.hs03_button = CircleLabel('HS-03')
        
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
        self.hs01_button.mousePressEvent = self.update_hs01
        self.hs01_button.mouseReleaseEvent = lambda event: self.hs01_button.update_color(False)
        self.hs02_button.mousePressEvent = self.toggle_hs02
        self.hs02_button.mouseReleaseEvent = lambda event: self.hs02_button.update_color(False)
        self.hs03_button.mousePressEvent = self.toggle_hs03
        
        self.hs01 = Button(17)  # Asumiendo GPIO 17 para hs-01
        self.hs02 = Button(27)  # Asumiendo GPIO 27 para hs-02
        self.pl01 = LED(5)  # Asumiendo GPIO 5 para pl-01
        self.pl02 = LED(6)  # Asumiendo GPIO 6 para pl-02

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_outputs)
        self.timer.start(100)  # Actualizar cada 100 ms

        self.pl02_timer = QTimer()
        self.pl02_timer.timeout.connect(self.toggle_pl02)
        self.pl02_state = False  # Estado inicial apagado
        self.pl02_active = False  # Para controlar el estado de la secuencia

    def update_hs01(self, event):
        self.hs01_button.update_color(True)
        if self.hs03_button.styleSheet().find('background-color: green') != -1:
            self.pl01.on()
            QTimer.singleShot(5000, lambda: self.pl01.off())
        else:
            self.pl01.on()
            QTimer.singleShot(10000, lambda: self.pl01.off())

    def toggle_hs02(self, event):
        self.hs02_button.update_color(True)
        if self.pl02_active:
            self.stop_pl02_sequence()
        else:
            self.start_pl02_sequence()

    def start_pl02_sequence(self):
        self.pl02_active = True
        self.pl02_state = True
        self.pl02.on()
        self.pl02_led.update_color(True)
        self.pl02_timer.start(3000)  # Comienza la secuencia de 3 segundos encendido

    def stop_pl02_sequence(self):
        self.pl02_active = False
        self.pl02_timer.stop()
        self.pl02.off()
        self.pl02_led.update_color(False)
        self.pl02_state = False

    def toggle_pl02(self):
        if not self.pl02_active:
            return
        if self.pl02_state:
            self.pl02.off()
            self.pl02_led.update_color(False)
            self.pl02_state = False
            self.pl02_timer.start(1000)  # 1 segundo apagado
        else:
            self.pl02.on()
            self.pl02_led.update_color(True)
            self.pl02_state = True
            self.pl02_timer.start(3000)  # 3 segundos encendido

    def toggle_hs03(self, event):
        current_color = self.hs03_button.styleSheet().find('background-color: green')
        self.hs03_button.update_color(False if current_color != -1 else True)

    def update_outputs(self):
        self.pl01_led.update_color(self.pl01.is_lit)
        self.pl02_led.update_color(self.pl02.is_lit)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VentanaPrincipal()
    window.show()
    sys.exit(app.exec_())
