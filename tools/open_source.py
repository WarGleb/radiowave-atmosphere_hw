"""Открывает источник из задания на нужной странице.

Примеры:
  python tools/open_source.py --list dz1          # источники задания и ссылки на них
  python tools/open_source.py dz1 2 309           # источник [2], печатная страница 309
  python tools/open_source.py dz1 2 309 --offset 20   # если в вашем файле другое смещение

Как работает:
  0. Сначала показывает лист справки из excerpts/ (формулы по этому месту источника),
     он работает без интернета и без книги.
  1. Ищет файл источника в папке sources/ рядом с репозиторием (или в папке из переменной
     SOURCES_DIR) по шаблону из tools/sources_manifest.csv. Файлы вы получаете сами законным
     путём: библиотека вуза, открытый доступ, издательство, запрос автору (см. HOWTO_sources.md).
     Скрипт ничего не скачивает.
  2. PDF открывается в браузере сразу на странице (печатная страница + смещение из таблицы).
     Другие форматы (DjVu и т. п.) открываются программой по умолчанию: перейдите на указанную страницу.
  3. Если файла нет, открывается онлайн-доступ в таком порядке:
       а) читалка открытого источника на нужной странице (если задан reader_url в таблице);
       б) DOI или ссылка из таблицы; если настроен прокси вашей библиотеки (EZproxy),
          ссылка открывается через него, и вы входите под своей учётной записью вуза;
       в) поиск книги по ISBN в каталоге: вашей библиотеки (LIBRARY_CATALOG) или WorldCat.
     Всегда печатается, какую печатную страницу искать.
Настройка библиотеки (один раз, необязательно): создайте tools/library.ini (в git не попадает):
    [library]
    proxy = https://ezp-prod1.hul.harvard.edu/login?url=
    catalog = https://hollis.harvard.edu/primo-explore/search?query=any,contains,{q}&vid=HVD2
или задайте переменные окружения LIBRARY_PROXY и LIBRARY_CATALOG ({q} заменяется на ISBN или название).
Адреса прокси и каталога возьмите на сайте вашей библиотеки: у каждого вуза они свои.
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


def online_targets(r, printed_page):
    """Список (описание, url) в порядке предпочтения."""
    proxy, catalog = library_settings()
    out = []
    if r.get("reader_url"):
        leaf = printed_page + int(r.get("reader_offset") or 0)
        out.append(("читалка открытого источника", r["reader_url"].format(leaf=leaf, page=printed_page)))
    direct = ("https://doi.org/" + r["doi"]) if r.get("doi") else r.get("link", "")
    if direct:
        if proxy:
            out.append(("через прокси вашей библиотеки", proxy + direct))
        out.append(("ссылка на источник", direct))
    q = r.get("isbn") or r.get("title", "")
    if q:
        if catalog:
            out.append(("каталог вашей библиотеки", catalog.format(q=urllib.parse.quote(q))))
        if r.get("isbn"):
            out.append(("WorldCat (где взять книгу)", "https://search.worldcat.org/search?q=bn:" + r["isbn"]))
    return out


def show_excerpt(dz, n, page):
    """Печатает раздел листа справки excerpts/<dz>_*.md, заголовок которого ссылается на [n, ... с. page]."""
    shown = False
    for md in sorted((HERE.parent / "excerpts").glob(f"{dz}_*.md")):
        text = md.read_text(encoding="utf-8")
        for block in re.split(r"(?m)^(?=### )", text):
            m = re.match(r"### \[(\d+),[^\]]*?с\. (\d+)(?:[–-](\d+))?", block)
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
    if r["note"]:
        print("примечание:", r["note"])
    if path:
        if path.suffix.lower() == ".pdf":
            url = path.resolve().as_uri() + f"#page={target}"
            print("открываю:", url)
            if not a.dry_run:
                webbrowser.open(url)
        else:
            print("открываю программой по умолчанию:", path, f"-> перейдите на страницу {target}")
            if not a.dry_run:
                if hasattr(os, "startfile"):
                    os.startfile(str(path))          # Windows
                else:
                    webbrowser.open(path.resolve().as_uri())
        return 0
    print("Файл источника в папке sources/ не найден (шаблон:", r["file_glob"] + ").")
    targets = online_targets(r, a.page)
    if not targets:
        print("Ссылок в таблице нет: найдите книгу в библиотеке; нужна страница", a.page)
        return 0
    print(f"Нужна печатная страница {a.page}. Варианты доступа:")
    for i, (what, url) in enumerate(targets, 1):
        print(f"  {i}. {what}: {url}")
    if not library_settings()[0]:
        print("Совет: если у вашего вуза есть доступ к электронным ресурсам, задайте прокси библиотеки (см. tools/open_source.py, раздел «Настройка»).")
    if not a.dry_run:
        webbrowser.open(targets[0][1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
