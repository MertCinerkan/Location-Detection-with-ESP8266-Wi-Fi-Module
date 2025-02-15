import sys
import serial
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QComboBox, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from matplotlib import patches

class SerialThread(QThread):
    data_received = pyqtSignal(str)

    def __init__(self, port_name, baud_rate=115200):
        super().__init__()
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.serial_port = None
        self.running = True

    def run(self):
        try:
            self.serial_port = serial.Serial(self.port_name, self.baud_rate, timeout=1)
            while self.running:
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    if line:
                        self.data_received.emit(line)
        except Exception as e:
            self.data_received.emit(f"Seri port hatası: {e}")

    def stop(self):
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

class RSSIColorGradientGraph(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RSSI Gradient and Signal Visualization")
        self.setGeometry(100, 100, 600, 800)

        # Merkezi widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout
        self.layout = QVBoxLayout(self.central_widget)

        # Port seçimi için comboBox
        self.port_selection = QComboBox()
        self.port_selection.addItems(["COM8", "COM9", "COM10"])
        self.layout.addWidget(self.port_selection)

        # Baud rate seçimi için comboBox
        self.baud_rate_selection = QComboBox()
        self.baud_rate_selection.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.layout.addWidget(self.baud_rate_selection)

        # Bağlantıyı başlat butonu
        self.connect_button = QPushButton("Bağlantıyı Başlat")
        self.connect_button.clicked.connect(self.start_serial_connection)
        self.layout.addWidget(self.connect_button)

        # Grafik için Matplotlib ayarı
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim(0.3, 0.7)
        self.ax.set_ylim(-10, -60)  # Güçlü sinyal (-10) aşağıda, zayıf sinyal (-60) yukarıda

        # Dikey eksende mesafeler (10 cm'den 150 cm'e kadar)
        self.ax.set_yticks(np.linspace(-10, -60, 6))
        self.ax.set_yticklabels(["10 cm", "50 cm", "90 cm", "110 cm", "130 cm", "150 cm"], fontsize=10)

        # Yatay eksen boş
        self.ax.set_xticks([])

        # Eksen çizgileri ve renkleri
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color("gray")
        self.ax.spines['bottom'].set_color("gray")
        self.ax.tick_params(axis='x', colors='black')
        self.ax.tick_params(axis='y', colors='black')

        # Renk kartelası için ayar (soluk halde başlar)
        self.gradient = np.linspace(-60, -10, 100).reshape(100, 1)
        self.image = self.ax.imshow(self.gradient, extent=[0.45, 0.55, -60, -10], aspect='auto', cmap="coolwarm", alpha=0.2)

        # Gelen değeri göstermek için dikdörtgen
        self.highlight_rect = self.ax.add_patch(patches.Rectangle((0.45, -10), 0.1, 0.8, color="red", alpha=0.4))

        # Sağda dinamik RSSI değeri
        self.value_text = self.ax.text(0.58, -10, "", color="black", ha="left", va="center", fontsize=12, weight="bold")

        self.canvas.draw_idle()

        # JSON verilerini saklamak için liste
        self.json_data_list = []

        # JSON Verilerini Kaydet Butonu
        self.save_button = QPushButton("JSON Verilerini Kaydet")
        self.save_button.clicked.connect(self.save_json_data)
        self.layout.addWidget(self.save_button)

        # Log ekranı
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.layout.addWidget(self.log_text)

        self.serial_thread = None

    def start_serial_connection(self):
        port_name = self.port_selection.currentText()
        baud_rate = int(self.baud_rate_selection.currentText())

        if self.serial_thread:
            self.serial_thread.stop()
            self.serial_thread.wait()

        self.serial_thread = SerialThread(port_name, baud_rate)
        self.serial_thread.data_received.connect(self.process_serial_data)
        self.serial_thread.start()
        self.log_text.append(f"Bağlantı başlatıldı: Port={port_name}, Baud Rate={baud_rate}")

    def process_serial_data(self, data):
        try:
            if not data.startswith("{") or not data.endswith("}"):
                self.log_text.append(f"Geçersiz veri formatı atlandı: {data}")
                return

            json_data = json.loads(data)
            self.json_data_list.append(json_data)  # Veriyi kaydetmek için listeye ekle

            rssi = json_data.get("RSSI")
            if rssi is not None:
                # Dikdörtgenin pozisyonunu ve boyutunu güncelle
                rect_height = 0.8
                self.highlight_rect.set_bounds(0.45, rssi - rect_height / 2, 0.1, rect_height)

                # Rengi gelen değere göre ayarla (-20 dBm kırmızı, -60 dBm mavi)
                normalized_value = (rssi + 60) / 50  # -60 mavi, -20 kırmızı
                normalized_value = max(0, min(1, normalized_value))  # Sınırlar arasında tut
                self.highlight_rect.set_color(self.image.cmap(normalized_value))

                # Dinamik metin güncellemesi
                self.value_text.set_position((0.58, rssi))
                self.value_text.set_text(f"{rssi} dBm")

                # Log ekranına JSON verisini yaz
                self.log_text.append(json.dumps(json_data, indent=4))

                self.canvas.draw_idle()
        except json.JSONDecodeError:
            self.log_text.append(f"JSON Ayrıştırma Hatası: {data}")
        except Exception as e:
            self.log_text.append(f"Veri İşleme Hatası: {e}")

    def save_json_data(self):
        """JSON verilerini bir dosyaya kaydet."""
        if not self.json_data_list:
            self.log_text.append("Kaydedilecek veri bulunamadı.")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "JSON Verilerini Kaydet", "", "JSON Files (*.json)", options=options)

        if file_path:
            try:
                with open(file_path, "w") as file:
                    json.dump(self.json_data_list, file, indent=4)
                self.log_text.append(f"Veriler başarıyla {file_path} konumuna kaydedildi.")
            except Exception as e:
                self.log_text.append(f"Veriler kaydedilirken hata oluştu: {e}")

    def closeEvent(self, event):
        if self.serial_thread:
            self.serial_thread.stop()
            self.serial_thread.wait()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RSSIColorGradientGraph()
    window.show()
    sys.exit(app.exec_())
