import sys
import asyncio
from googletrans import Translator
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget, QLabel)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Gugyl Translejtor')
        self.setMinimumSize(QSize(640, 480))

        # Main horizontal layout for side-by-side arrangement
        main_layout = QHBoxLayout()

        # Left side - Input
        left_layout = QVBoxLayout()
        left_label = QLabel('Input')
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            'Type here and press Ctrl+Enter to translate')
        self.text_input.textChanged.connect(self.text_changed)

        left_layout.addWidget(left_label)
        left_layout.addWidget(self.text_input)

        # Right side - Output
        right_layout = QVBoxLayout()
        right_label = QLabel('Translation')
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)

        right_layout.addWidget(right_label)
        right_layout.addWidget(self.text_display)

        # Add both sides to main layout
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.text = ''

    async def translate_text(self):
        async with Translator() as translator:
            return await translator.translate(self.text, dest='en')

    def translate_and_display(self):
        if self.text.strip():
            translated = asyncio.run(self.translate_text())
            translated_text = translated.text
            self.text_display.setText(translated_text)

    def text_changed(self):
        # Extract all the text content as a plain string. Returns just a text without any formatting, in contrast to `toHtml()`
        self.text = self.text_input.toPlainText()

    def keyPressEvent(self, event):
        # Translate on Ctrl+Enter
        if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.translate_and_display()
        # Otherwise pass the event to the default handler
        else:
            super().keyPressEvent(event)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
