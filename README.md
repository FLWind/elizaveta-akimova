# Портфолио Елизаветы Акимовой

Hugo + тема [Gallery](https://github.com/nicokaiser/hugo-theme-gallery), закреплённая сабмодулем.

| Язык | Сайт | Конфигурация | Результат сборки | rclone remote |
| --- | --- | --- | --- | --- |
| Русский | https://akimova.ru/ | `config/akimova.ru.toml` | `public/akimova.ru/` | `akimova-ru:` |
| English | https://akimova.pro/ | `config/akimova.pro.toml` | `public/akimova.pro/` | `akimova-en:` |
| 简体中文 | https://akimova.asia/ | `config/akimova.asia.toml` | `public/akimova.asia/` | `akimova-cn:` |

Китайская версия использует упрощённые иероглифы (`zh-CN`). Имя автора —
**Elizabeth Akimova**, почта — **elizabeth@akimova.pro**, как в английской версии.

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
./build.sh          # все три версии
./build.sh ru       # только akimova.ru
./build.sh en       # только akimova.pro
./build.sh cn       # только akimova.asia (также поддерживается ./build.sh zh)
python3 scripts/check_site.py  # проверка всех трёх готовых production-сборок
```

Скрипт работает из любой текущей папки. Устаревшие файлы внутри каталога
собираемого сайта удаляются; исходники не затрагиваются.

Локальный просмотр (каждая команда запускается в своём терминале):

```bash
./akimova.ru.sh     # http://localhost:10013/
./akimova.pro.sh    # http://localhost:10014/
./akimova.asia.sh   # http://localhost:10015/
```

Дополнительные параметры Hugo можно передать скрипту, например `./akimova.ru.sh --buildDrafts`.
После локального просмотра перед публикацией заново выполните `./build.sh`:
Hugo server использует локальные URL.

### Публикация

Создайте в `rclone config` подключения **akimova-ru**, **akimova-en** и **akimova-cn**.
Корень каждого подключения должен указывать непосредственно на web-root
соответствующего домена, куда нужно положить `index.html`.
Пароли и настройки подключений хранятся в локальной конфигурации rclone, не в Git.

```bash
./build.sh
./publish.sh --dry-run   # показать план без изменения файлов на хостинге
./publish.sh             # опубликовать все три сайта
```

`publish.sh` сначала проверяет все три сборки, ссылки языковых версий, иконки и наличие
всех трёх подключений. Затем выполняет `rclone sync --delete-after`:
файлы, отсутствующие в локальной сборке, удаляются с хостинга после передачи.
Служебные каталоги `cgi-bin/` и `.well-known/` исключены из синхронизации и удаления.
Синхронизации последовательные: при сетевой ошибке следующие сайты могут остаться
на предыдущей версии; после устранения ошибки повторите публикацию.

Windows-скрипт `build.cmd` собирает все три версии. Для локального просмотра есть
`akimova.ru.cmd`, `akimova.pro.cmd` и `akimova.asia.cmd`.

## Языковые версии и метаданные

Каждый сайт имеет собственный `baseURL` и canonical на своём домене.
В `<head>` опубликованы взаимные `hreflang="ru"`, `hreflang="en"` и `hreflang="zh-CN"`, включая ссылку
на текущую версию. `x-default` указывает на английскую страницу. В шапке есть
переключатель RU / EN / 中文, сохраняющий текущую страницу.

Сборки раздельные, поэтому `.Translations` Hugo недоступен. Соответствия определяются
по файлам с одинаковым именем и языковыми суффиксами: `index.ru.md` / `index.en.md` /
`index.zh.md`, аналогично для `_index` и `about`. Китайский язык в Hugo обозначен
ключом `zh`, а HTML и hreflang используют `zh-CN`. **URL-путь переводов должен совпадать**:
не задавайте разные `slug` или `url` для переводов. Домены и локали хранятся в
`data/languages.toml`; при смене домена обновите также соответствующий `baseURL`
и таблицу `DOMAINS` в `scripts/check_site.py`.

Подписи кнопок, счётчиков и навигации переведены через `i18n/`. Китайские подписи
изображений находятся в `resources` соответствующего `index.zh.md`. Изображения
общие для всех языков; добавляя работу, укажите её подпись во всех трёх файлах.

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
