import json
import os
from typing import Any

import openpyxl
import requests


BASE_URL = 'https://spo-13.mskobr.ru'
PAGE_PATH = '/uchashimsya/raspisanie-kanikuly'
KORPUS = 'Корпус Ярославский'
CACHE_FILE = 'cache_index.json'


def parse_schedule_files() -> list[dict[str, Any]]:
    """Возвращает список файлов расписания в нужном корпусе."""
    response = requests.post(BASE_URL + '/v1/api/page/id', json={'path': PAGE_PATH})
    response.raise_for_status()
    page_id = response.json()['data']['id']

    response = requests.get(BASE_URL + f'/v1/api/folder_and_file/list/{page_id}')
    response.raise_for_status()
    folders = response.json()['data']['folders']

    schedule_folder: dict[str, Any] | None = None
    for folder in folders:
        if 'расписание учебных' in folder["title"].lower():
            schedule_folder = folder
            break

    if schedule_folder is None:
        return []

    files: list[dict[str, Any]] = []
    for korpus in schedule_folder["folders"]:
        if korpus["title"] != KORPUS:
            continue
        for f in korpus["files"]:
            title = str(f["title"]).strip()
            if not title:
                continue
            try:
                course = int(str(f["title"])[0])
            except (ValueError, TypeError):
                continue

            files.append({
                'file_id': int(f['id']),
                'course': course,
                'title': title,
                'src': str(f['src']),
                'ext': str(f.get('ext', 'xlsx')),
                'url': BASE_URL + str(f['src']),
            })
    return files


def is_new_file(file_id: int, src: str) -> bool:
    if not os.path.exists(CACHE_FILE):
        return True

    with open(CACHE_FILE, encoding='utf-8') as f:
        cache = json.load(f)

    return bool(cache.get(str(file_id)) != src)


def cache_file(file_id: int, course: int, src: str, url: str, ext: str) -> str:
    folder = f'c{course}'
    os.makedirs(folder, exist_ok=True)

    file_path: str = os.path.join(folder, f'kurs{course}.{ext}')
    response = requests.get(url)
    response.raise_for_status()

    with open(file_path, 'wb') as f:
        f.write(response.content)

    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, encoding='utf-8') as f:
            cache = json.load(f)

    cache[str(file_id)] = src
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

    return file_path


def normalize_cell_value(value: Any) -> str:
    if value is None:
        return ''
    text = str(value).strip()
    return text if text and text.lower() != 'none' else ''


def parse_xlsx_schedule(file_path: str, max_lines: int = 500) -> str:
    """Парсит XLSX и возвращает текстовое расписание."""
    wb = openpyxl.load_workbook(file_path, data_only=True)
    lines: list[str] = []

    for sheet in wb.worksheets:
        lines.append(f'Лист: {sheet.title}')
        for row in sheet.iter_rows(values_only=True):
            cleaned = [normalize_cell_value(cell) for cell in row if normalize_cell_value(cell)]
            if not cleaned:
                continue
            if len(cleaned) == 1:
                lines.append(cleaned[0])
            else:
                lines.append(' | '.join(cleaned))
            if len(lines) >= max_lines:
                lines.append('... расписание сокращено, отправлен файл.')
                return '\n'.join(lines)
        lines.append('')

    return '\n'.join(lines).strip()


def download_schedule_file(url: str, destination: str) -> str:
    os.makedirs(os.path.dirname(destination) or '.', exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    with open(destination, 'wb') as f:
        f.write(response.content)
    return destination


if __name__ == '__main__':
    files = parse_schedule_files()
    print(f'Найдено файлов ({KORPUS}): {len(files)}\n')

    for f in files:
        if is_new_file(f['file_id'], f['src']):
            path = cache_file(f['file_id'], f['course'], f['src'], f['url'], f['ext'])
            print(f'Скачан: {path}  ({f["url"]})')
        else:
            print(f'Без изменений: c{f["course"]}/kurs{f["course"]}.{f["ext"]}')
