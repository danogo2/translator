import sys
import asyncio
from googletrans import Translator
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QVBoxLayout, QWidget, QLabel


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Gugyl Translejtor')
        self.setMinimumSize(QSize(640, 480))

        layout = QVBoxLayout()

        text_input = QLineEdit()
        text_input.setMaxLength(30)
        text_input.setPlaceholderText('Type here and press Enter to translate')
        text_input.returnPressed.connect(self.return_pressed)
        text_input.textEdited.connect(self.text_edited)

        self.text_display = QLabel('')

        layout.addWidget(text_input)
        layout.addWidget(self.text_display)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.text = ''

    async def translate_text(self):
        async with Translator() as translator:
            return await translator.translate(self.text, dest='en')

    def return_pressed(self):
        translated = asyncio.run(self.translate_text())
        translated_text = translated.text

        self.text_display.setText(translated_text)

    def text_edited(self, s):
        self.text = s


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
