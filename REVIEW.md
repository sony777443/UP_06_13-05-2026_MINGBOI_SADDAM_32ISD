# ✅ Проверка пройдена — `parser.py`

_Проверено: 2026-05-13 10:17_

Все 10 шагов выполнены верно:

- ✅ Шаг 1: `response.json()["data"]["id"]`
- ✅ Шаг 2: `response.json()["data"]["folders"]`
- ✅ Шаг 3: `folder["title"]`
- ✅ Шаг 4 (цикл корпусов): `schedule_folder["folders"]`
- ✅ Шаг 4 (сравнение корпуса): `korpus["title"]`
- ✅ Шаг 4 (цикл файлов): `korpus["files"]`
- ✅ Шаг 4 (file_id): `f["id"]`
- ✅ Шаг 4 (course): `f["title"]`
- ✅ Шаг 4 (src): `f["src"]`
- ✅ Шаг 4 (ext): `f.get("ext", "xlsx")`

Отлично! Можно двигаться дальше — интегрировать парсер в Telegram-бота.
