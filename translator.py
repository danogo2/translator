import sys
import asyncio
from googletrans import Translator, LANGUAGES
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit,
                             QVBoxLayout, QHBoxLayout, QWidget, QLabel,
                             QPushButton, QComboBox)

BUTTON_STYLE = '''
    QPushButton {
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 5px 10px;
        background-color: #f8f9fa;
    }
    QPushButton:hover {
        background-color: #e8e9ea
    }
'''


class LanguageSelector(QWidget):
    '''Widget containing language dropdown and recent language buttons'''

    def __init__(self, default_lang='en', recent_langs=None):
        super().__init__()

        if recent_langs is None:
            recent_langs = ['es', 'fr', 'de']

        self.current_lang = default_lang  # lang code like: 'en', 'pl'
        self.recent_langs = recent_langs

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

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
            btn.setStyleSheet(BUTTON_STYLE)
            btn.clicked.connect(self.on_recent_button_clicked)
            self.recent_buttons.append(btn)
            self.layout.addWidget(btn)

        self.layout.addWidget(self.combo)
        self.layout.addStretch()

        self.setLayout(self.layout)

    def populate_languages(self):
        '''Add all available languages to dropdown'''
        # Convert LANGUAGES dict to sorted list of (name, code) tuples
        lang_list = [(name.capitalize(), code)
                     for code, name in LANGUAGES.items()]
        lang_list.sort()

        for name, code in lang_list:
            self.combo.addItem(name, code)

    def get_language_name(self, code):
        '''Get language name from code'''
        return LANGUAGES.get(code, code).capitalize()

    def get_language_code(self, name):
        '''Get language code from name'''
        for code, lang_name in LANGUAGES.items():
            if lang_name.capitalize() == name:
                return code
        return 'auto'

    def on_combo_changed(self, selected_lang_name):
        '''Handle dropdown selection'''
        self.current_lang = self.get_language_code(selected_lang_name)
        if self.current_lang != 'auto':
            self.update_recent_languages(self.current_lang)

    def on_recent_button_clicked(self):
        '''Handle recent language button click'''
        button = self.sender()  # returns which widget triggered the signal, it's crucial since all 3 recent buttons have 'clicked' signal connected to the same slot (on_recent_button_clicked) and 'clicked' signal doesn't send the button object automatically
        lang_code = button.property('lang_code')
        self.current_lang = lang_code
        self.combo.setCurrentText(self.get_language_name(lang_code))

    def update_recent_languages(self, lang_code):
        '''Update recent lanugages list and buttons'''
        # Remove if already in list to avoid duplicates (in case it is in 2nd position/index=1, truncating the list with [:3] won't get rid of it)
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
        '''Get currently selected language code'''
        return self.current_lang

    def set_language(self, lang_code):
        '''Set language programmatically'''
        self.current_lang = lang_code
        self.combo.setCurrentText(self.get_language_name(lang_code))


class LanguageSelectorSource(LanguageSelector):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add "Detect language" option for source
        self.combo.insertItem(
            0, 'Detect language', 'auto')
        self.combo.setCurrentIndex(0)
        self.current_lang = 'auto'
        # Add "Detect language" button
        btn_detect = QPushButton('Detect language')
        btn_detect.setProperty('lang_code', 'auto')
        btn_detect.setFlat(True)
        btn_detect.setStyleSheet('''
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
        btn_detect.clicked.connect(self.on_detect_button_clicked)
        self.layout.insertWidget(0, btn_detect)

    def on_detect_button_clicked(self):
        self.current_lang = 'auto'
        self.combo.setCurrentText('Detect language')


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
        self.source_lang_selector = LanguageSelectorSource(
            default_lang='auto', recent_langs=['en', 'pl', 'de'])

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            'Type here and press Ctrl+Enter to translate')
        self.text_input.textChanged.connect(self.on_text_changed)

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
        '''Translate text using selected languages'''
        source_lang = self.source_lang_selector.get_current_language()
        target_lang = self.target_lang_selector.get_current_language()

        async with Translator() as translator:
            # "auto" is the default for source language detection
            result = await translator.translate(
                self.text,
                src=source_lang if source_lang != 'auto' else 'auto',
                dest=target_lang
            )
            return result

    def translate_and_display(self):
        '''Perform translation and display result'''
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

    def on_text_changed(self):
        '''Update text variable when input changes'''
        # Extract all the text content as a plain string. Returns just a text without any formatting, in contrast to `toHtml()`
        self.text = self.text_input.toPlainText()

    def keyPressEvent(self, event):
        '''Handle keyboard shortcuts'''
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
