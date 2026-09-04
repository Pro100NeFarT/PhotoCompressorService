# PhotoCompressorService

Локальна Windows-служба для стиснення та конвертації фото (WEBP → JPEG, зменшення
розміру/розширення), яку 1С викликає звичайним HTTP-запитом перед записом картинки
в базу.

Повна документація, API, приклад коду BSL, налаштування — у [docs/README.md](docs/README.md).

## Швидкий старт

1. Завантажити останній інсталятор із [Releases](../../releases).
2. Запустити від імені адміністратора.
3. Відкрити `http://127.0.0.1:8788/` — головна сторінка з живим прикладом і
   інструментом перевірки.

## Розробка

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements-dev.txt
.venv\Scripts\python service_main.py
```

Збірка exe та інсталятора — див. [docs/README.md](docs/README.md).
