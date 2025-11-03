import sys
import asyncio
from googletrans import Translator, LANGUAGES
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QComboBox)


class LanguageSelector(QWidget):

    def __init__(self, default_lang='eng', recent_langs=None):
        super().__init__()

        if recent_langs is None:
            recent_langs = ['es', 'fr', 'de']

        self.current_lang = default_lang
        self.recent_langs = recent_langs

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Language dropdown
        self.combo = QComboBox()
        self.populate_languages()
        self.combo.setCurrentText(self.get_language_name(default_lang))
        self.combo.currentTextChanged.connect(self.on_combo_changed)

        # Recent language buttons
        self.recent_buttons = []
        for lang_code in recent_langs:
            btn = QPushButton(self.get_language_name(lang_code))
            btn.setProperty('lang_code', lang_code)
            btn.setFlat(True)
            btn.setStyleSheet('''
                QPushButton {
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 5px 10px;
                    background-color: #f8f9fa;
                }
                QPushButton:hover {
                    background-color: #e8e9ea
                }
            ''')
            btn.clicked.connect(self.on_recent_button_clicked)
            self.recent_buttons.append(btn)
            layout.addWidget(btn)

        layout.addWidget(self.combo)
        layout.addStretch()

        self.setLayout(layout)

    def populate_languages(self):
        # Convert LANGUAGES dict to sorted list od (name, code) typles
        lang_list = [(name.capitalize(), code)
                     for code, name in LANGUAGES.items()]
        lang_list.sort()

        for name, code in lang_list:
            self.combo.addItem(name, code)

    def get_language_name(self, code):
        return LANGUAGES.get(code, code).capitalize()

    def get_language_code(self, name):
        for code, lang_name in LANGUAGES.items():
            if lang_name.capitalize() == name:
                return code
        return 'en'

    def on_combo_changed(self, text):
        self.current_lang = self.get_language_code(text)
        self.update_recent_languages(self.current_lang)

    def on_recent_button_clicked(self):
        button = self.sender()
        lang_code = button.property('lang_code')
        self.current_lang = lang_code
        self.combo.setCurrentText(self.get_language_name(lang_code))

    def update_recent_languages(self, lang_code):
        # Remove if already in list
        if lang_code in self.recent_langs:
            self.recent_langs.remove(lang_code)

        # Add to front of list
        self.recent_langs.insert(0, lang_code)

        # Keep only 3 most recent
        self.recent_langs = self.recent_langs[:3]

        # Update button labels and properties
        for i, btn in enumerate(self.recent_buttons):
            if i < len(self.recent_langs):
                lang_code = self.recent_langs[i]
                btn.setText(self.get_language_name(lang_code))
                btn.setProperty('lang_code', lang_code)
                btn.setVisible(True)
            else:
                btn.setVisible(False)

    def get_current_language(self):
        return self.current_lang

    def set_language(self, lang_code):
        self.current_lang = lang_code
        self.combo.setCurrentText(self.get_language_name(lang_code))


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Gugyl Translejtor')
        self.setMinimumSize(QSize(640, 480))

        # Main horizontal layout for side-by-side arrangement
        main_layout = QHBoxLayout()

        # Left side - Input
        left_layout = QVBoxLayout()

        # Source language selector
        left_label = QLabel('Source Language')
        self.source_lang_selector = LanguageSelector(
            default_lang='auto', recent_langs=['auto', 'pl', 'en'])

        # Add "Detect language" option for source
        self.source_lang_selector.combo.insertItem(
            0, 'Detect language', 'auto')
        self.source_lang_selector.combo.setCurrentIndex(0)
        self.source_lang_selector.current_lang = 'auto'

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            'Type here and press Ctrl+Enter to translate')
        self.text_input.textChanged.connect(self.text_changed)

        left_layout.addWidget(left_label)
        left_layout.addWidget(self.source_lang_selector)
        left_layout.addWidget(self.text_input)

        # Right side - Output
        right_layout = QVBoxLayout()

        # Target language selector
        right_label = QLabel('Target Language')
        self.target_lang_selector = LanguageSelector(
            default_lang='en', recent_langs=['en', 'es', 'de'])

        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setPlaceholderText('Translation will appear here')

        right_layout.addWidget(right_label)
        right_layout.addWidget(self.target_lang_selector)
        right_layout.addWidget(self.text_display)

        # Add both sides to main layout
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.text = ''

    async def translate_text(self):
        source_lang = self.source_lang_selector.get_current_language()
        target_lang = self.target_lang_selector.get_current_language()

        async with Translator() as translator:
            # "auto" is the default for source language detection
            result = await translator.translate(self.text, src=source_lang if source_lang != 'auto' else 'auto', dest=target_lang)
            return result

    def translate_and_display(self):
        if self.text.strip():
            try:
                translated = asyncio.run(self.translate_text())
                translated_text = translated.text

                # Show detected language if auto-detect was used
                if self.source_lang_selector.get_current_language() == 'auto':
                    detected = translated.src
                    detected_name = LANGUAGES.get(
                        detected, detected).capitalize()
                    self.text_display.setText(
                        f'[Detected: {detected_name}]\n\n{translated_text}')
                else:
                    self.text_display.setText(translated_text)
            except Exception as e:
                self.text_display.setText(f'Translation error: {str(e)}')

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
