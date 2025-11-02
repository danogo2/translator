import asyncio
from googletrans import Translator


async def translate_text():
    translator = Translator()
    result = await translator.translate('Dzień dobry! Co słychać?')
    return result


result = asyncio.run(translate_text())
print('Result:', result)
