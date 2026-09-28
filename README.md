# Портфолио Елизаветы Акимовой

Hugo + тема [Gallery](https://github.com/nicokaiser/hugo-theme-gallery), закреплённая сабмодулем.

| Язык | Сайт | Конфигурация | Результат сборки | rclone remote |
| --- | --- | --- | --- | --- |
| Русский | https://akimova.ru/ | `config/akimova.ru.toml` | `public/akimova.ru/` | `akimova-ru:` |
| English | https://akimova.pro/ | `config/akimova.pro.toml` | `public/akimova.pro/` | `akimova-en:` |

## Fedora / Linux

Нужен **Hugo Extended** (тема использует SCSS), Git, Python 3 и rclone.
Проверенная версия Hugo: **0.166.0 Extended**. Тема рассчитана на Hugo 0.123.0+;
на новых версиях возможны предупреждения об устаревающих API самой темы.

```bash
sudo dnf install git hugo python3 rclone
git clone --recurse-submodules https://github.com/FLWind/elizaveta-akimova.git
cd elizaveta-akimova
hugo version
```

Для уже скачанного репозитория:

```bash
git pull --ff-only
git submodule update --init --recursive
```

В выводе `hugo version` должно быть `+extended`.

### Сборка

```bash
./build.sh          # обе версии
./build.sh ru       # только akimova.ru
./build.sh en       # только akimova.pro
python3 scripts/check_site.py  # проверка обеих готовых production-сборок
```

Скрипт работает из любой текущей папки. Устаревшие файлы внутри каталога
собираемого сайта удаляются; исходники не затрагиваются.

Локальный просмотр (каждая команда запускается в своём терминале):

```bash
./akimova.ru.sh     # http://localhost:10013/
./akimova.pro.sh    # http://localhost:10014/
```

Дополнительные параметры Hugo можно передать скрипту, например `./akimova.ru.sh --buildDrafts`.
После локального просмотра перед публикацией заново выполните `./build.sh`:
Hugo server использует локальные URL.

### Публикация

Создайте в `rclone config` подключения **akimova-ru** и **akimova-en**.
Корень каждого подключения должен указывать непосредственно на web-root
соответствующего домена, куда нужно положить `index.html`.
Пароли и настройки подключений хранятся в локальной конфигурации rclone, не в Git.

```bash
./build.sh
./publish.sh --dry-run   # показать план без изменения файлов на хостинге
./publish.sh             # опубликовать оба сайта
```

`publish.sh` сначала проверяет обе сборки, ссылки языковых версий, иконки и наличие
обоих подключений. Затем выполняет `rclone sync --delete-after`:
файлы, отсутствующие в локальной сборке, удаляются с хостинга после передачи.
Служебные каталоги `cgi-bin/` и `.well-known/` исключены из синхронизации и удаления.
Синхронизации последовательные: при сетевой ошибке второй сайт может остаться
на предыдущей версии; после устранения ошибки повторите публикацию.

Windows-скрипты `build.cmd`, `akimova.ru.cmd`, `akimova.pro.cmd` также сохранены.

## Языковые версии и метаданные

Каждый сайт имеет собственный `baseURL` и canonical на своём домене.
В `<head>` опубликованы взаимные `hreflang="ru"` и `hreflang="en"`, включая ссылку
на текущую версию. `x-default` указывает на английскую страницу. В шапке есть
переключатель RU / EN, сохраняющий текущую страницу.

Сборки раздельные, поэтому `.Translations` Hugo недоступен. Соответствия определяются
по парным файлам `index.ru.md` / `index.en.md`, `_index.ru.md` / `_index.en.md`
и `about.ru.md` / `about.en.md`. **URL-путь парных страниц должен совпадать**:
не задавайте разные `slug` или `url` для переводов. Домены и локали хранятся в
`data/languages.toml`; при смене домена обновите также соответствующий `baseURL`
и таблицу `DOMAINS` в `scripts/check_site.py`.

Проверка перед публикацией выявляет отсутствие перевода, несовпадающие пути,
неверные canonical/hreflang, сломанные локальные ссылки и отсутствие иконок.
Для 404 и страниц с `private: true` выставляется `noindex`; hreflang не добавляется.

Оформление шапки и метаданные переопределены в `layouts/partials/`, стили —
в `assets/css/custom.css`. Сам сабмодуль темы не изменён. `head.html` и `opengraph.html`
основаны на одноимённых шаблонах Gallery (MIT); при обновлении темы сравните их
с новой версией. `layouts/robots.txt` добавляет ссылку на sitemap своего домена.

## Иконки Æ

Исходник — `static/favicon.svg`: лигатура **Æ (U+00C6)** с засечками,
начертание DejaVu Serif Bold, переведённое в векторные контуры без зависимости
от установленных шрифтов. Цвет знака — кремовый `#f5f0e8`, фон — тёмный `#171923`.

В репозитории уже есть SVG, ICO (16/32/48 px), PNG (16/32/48/96 px),
Apple touch icon (180 px), web app icons (192/512 px), отдельная maskable-иконка
512 px с безопасными полями и `site.webmanifest`. Обычная сборка Hugo не требует
графических инструментов.

После изменения SVG можно пересоздать растровые варианты:

```bash
sudo dnf install inkscape python3-pillow
python3 scripts/generate_icons.py
./build.sh
```
