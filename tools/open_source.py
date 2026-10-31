"""Открывает источник из задания на нужной странице.
Примеры:
python tools/open_source.py --list dz1          # источники задания и ссылки на них
python tools/open_source.py dz1 2 309           # источник [2], печатная страница 309
python tools/open_source.py dz1 2 309 --offset 20   # если в вашем файле другое смещение

Как работает:
1. Показывает лист справки из excerpts/ (формулы по этому месту источника).
2. Ищет файл источника в папке sources/ по шаблону из tools/sources_manifest.csv.
3. Если файл найден, открывает его локально на нужной странице.
4. Если файл НЕ найден, автоматически открывает Sci-Hub с DOI или ссылкой этого источника,
   чтобы студент мог быстро скачать его вручную.

Только стандартная библиотека Python 3.8+.
"""
import argparse
import configparser
import csv
import fnmatch
import os
import pathlib
import re
import sys
import urllib.parse
import webbrowser

HERE = pathlib.Path(__file__).resolve().parent
MANIFEST = HERE / "sources_manifest.csv"

def load(dz):
    with open(MANIFEST, encoding="utf-8", newline="") as f:
        return [r for r in csv.DictReader(f, delimiter=";") if r["dz"] == dz]

def library_settings():
    """Прокси и каталог библиотеки: переменные окружения, иначе tools/library.ini."""
    proxy = os.environ.get("LIBRARY_PROXY", "")
    catalog = os.environ.get("LIBRARY_CATALOG", "")
    ini = HERE / "library.ini"
    if ini.is_file() and not (proxy and catalog):
        cp = configparser.ConfigParser()
        cp.read(ini, encoding="utf-8")
        proxy = proxy or cp.get("library", "proxy", fallback="")
        catalog = catalog or cp.get("library", "catalog", fallback="")
    return proxy.strip(), catalog.strip()

def show_excerpt(dz, n, page):
    """Печатает раздел листа справки excerpts/<dz>*.md, заголовок которого ссылается на [n, ... с. page]."""
    shown = False
    for md in sorted((HERE.parent / "excerpts").glob(f"{dz}*.md")):
        text = md.read_text(encoding="utf-8")
        for block in re.split(r"(?m)^(?=### )", text):
            m = re.match(r"### \[(\d+),[^\]]*с\. (\d+)(?:\s*[–-]\s*(\d+))?", block)
            if not m or int(m.group(1)) != n:
                continue
            lo, hi = int(m.group(2)), int(m.group(3) or m.group(2))
            if lo <= page <= hi:
                print(f"--- лист справки ({md.name}) ---")
                print(block.strip())
                print("--- конец листа справки ---")
                shown = True
    return shown

def find_file(pattern):
    base = pathlib.Path(os.environ.get("SOURCES_DIR", HERE.parent / "sources"))
    if not base.is_dir():
        return None
    for p in sorted(base.rglob("*")):
        if p.is_file() and fnmatch.fnmatch(p.name, pattern):
            return p
    return None

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dz", nargs="?", help="задание, например dz1")
    ap.add_argument("n", nargs="?", type=int, help="номер источника в списке задания")
    ap.add_argument("page", nargs="?", type=int, help="печатная страница")
    ap.add_argument("--offset", type=int, help="сколько прибавить к печатной странице в вашем файле")
    ap.add_argument("--list", metavar="DZ", help="показать источники задания")
    ap.add_argument("--dry-run", action="store_true", help="только напечатать, что будет открыто")
    
    a = ap.parse_args(argv)

    if a.list:
        for r in load(a.list):
            print(f"[{r['n']}] {r['title']}\n    ссылка: {r['link'] or '—'}\n    файл ищется по шаблону: {r['file_glob']}")
        return 0

    if not (a.dz and a.n and a.page):
        ap.print_usage()
        return 2

    rows = [r for r in load(a.dz) if int(r["n"]) == a.n]
    if not rows:
        print(f"В таблице нет источника [{a.n}] для {a.dz}. Список: --list {a.dz}")
        return 1

    r = rows[0]
    offset = a.offset if a.offset is not None else int(r["page_offset"] or 0)
    target = a.page + offset
    path = find_file(r["file_glob"])

    if not show_excerpt(a.dz, a.n, a.page):
        print(f"(в листах справки excerpts/ для [{a.n}, с. {a.page}] ничего нет)")
    
    print(f"[{a.n}] {r['title']}")
    print(f"печатная страница {a.page} -> страница в файле {target} (смещение {offset:+d})")
    if r.get("note"):
        print("примечание:", r["note"])

    # 1. Если файл найден локально — открываем его
    if path:
        if path.suffix.lower() == ".pdf":
            url = path.resolve().as_uri() + f"#page={target}"
            print("открываю локальный файл:", url)
            if not a.dry_run:
                webbrowser.open(url)
        else:
            print("открываю программой по умолчанию:", path, f"-> перейдите на страницу {target}")
            if not a.dry_run:
                if hasattr(os, "startfile"):
                    os.startfile(str(path))  # Windows
                else:
                    webbrowser.open(path.resolve().as_uri())
        return 0

    # 2. Если файл НЕ найден локально — упрощенный поиск через Sci-Hub
    print("Файл источника в папке sources/ не найден (шаблон:", r["file_glob"] + ").")
    
    doi = r.get("doi", "").strip()
    link = r.get("link", "").strip()
    
    # Приоритет: DOI, если его нет — прямая ссылка
    search_query = doi if doi else link

    if search_query:
        # Используем sci-hub.se (основной рабочий домен, можно заменить на .ru или .st при блокировках)
        sci_hub_url = f"https://sci-hub.se/{urllib.parse.quote(search_query)}"
        print(f"\n[!] Открываю Sci-Hub для скачивания: {sci_hub_url}")
        print("Совет: если домен .se недоступен в вашем регионе, замените его на .ru или .st в строке кода выше.")
        if not a.dry_run:
            webbrowser.open(sci_hub_url)
    else:
        print("\n[!] Нет DOI или прямой ссылки для поиска в Sci-Hub.")
        print("Пожалуйста, найдите источник вручную через библиотечный каталог или поисковую систему.")

    return 0

if __name__ == "__main__":
    sys.exit(main())
