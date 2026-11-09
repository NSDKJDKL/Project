import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Colors
    BG_COLOR = RGBColor(18, 19, 22)        # #121316
    CARD_BG = RGBColor(30, 32, 38)         # #1e2026
    CARD_BORDER = RGBColor(48, 52, 62)     # #30343e
    MINT = RGBColor(0, 230, 118)           # #00e676 (Theme color)
    CYAN = RGBColor(56, 189, 248)          # #38bdf8
    WHITE = RGBColor(241, 245, 249)        # #f1f5f9
    MUTED = RGBColor(148, 163, 184)        # #94a3b8
    ACCENT_RED = RGBColor(239, 68, 68)     # #ef4444
    FONT_FAMILY = "Segoe UI"

    def apply_bg(slide):
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = BG_COLOR

    def add_header(slide, tag_text, title_text):
        # Category Tag
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11), Inches(0.4))
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        tf_tag.margin_left = tf_tag.margin_top = tf_tag.margin_right = tf_tag.margin_bottom = 0
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag_text.upper()
        p_tag.font.name = FONT_FAMILY
        p_tag.font.size = Pt(11)
        p_tag.font.bold = True
        p_tag.font.color.rgb = MINT

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.5), Inches(0.6))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.name = FONT_FAMILY
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = WHITE

    def create_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.2)
        return shape

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    apply_bg(s1)

    # Top Tag
    tag_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(10), Inches(0.5))
    tf = tag_box.text_frame
    p = tf.paragraphs[0]
    p.text = "ИНДИВИДУАЛЬНЫЙ ПРОЕКТ • МОДУЛЬ PYQT • 2026"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = MINT

    # Big Title
    title_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(11), Inches(1.8))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "Симулятор Майнинг-Фермы"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = WHITE

    # Subtitle
    sub_box = s1.shapes.add_textbox(Inches(1.0), Inches(2.9), Inches(11), Inches(0.8))
    tf = sub_box.text_frame
    p = tf.paragraphs[0]
    p.text = "Десктопное приложение с реляционной базой данных SQLite3 и симуляцией реальной физики оборудования"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(18)
    p.font.color.rgb = MUTED

    # Bottom Info Cards
    info_data = [
        ("АВТОР ПРОЕКТА", "Виталий\nЯндекс.Лицей"),
        ("ТЕХНОЛОГИИ", "Python 3.13 • PyQt6\nSQLite3 • PyInstaller"),
        ("АРХИТЕКТУРА", "4 таблицы БД (CRUD)\n16 интерактивных слотов"),
        ("СТАТУС", "Полностью завершён\nСобран в .exe файл")
    ]
    card_w = Inches(2.65)
    card_h = Inches(1.6)
    for idx, (head, val) in enumerate(info_data):
        c_left = Inches(1.0 + idx * 2.85)
        create_card(s1, c_left, Inches(4.5), card_w, card_h)
        tb = s1.shapes.add_textbox(c_left + Inches(0.2), Inches(4.7), card_w - Inches(0.4), card_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = head
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = CYAN

        p2 = tf.add_paragraph()
        p2.text = val
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(13)
        p2.font.color.rgb = WHITE
        p2.space_before = Pt(6)

    # ==========================================
    # SLIDE 2: Idea & Relevance
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    apply_bg(s2)
    add_header(s2, "01 / Идея и актуальность", "Почему именно симулятор фермы и в чём его отличие?")

    cards_s2 = [
        ("Проблема обычных симуляторов", 
         "❌ Большинство учебных кликеров примитивны:\n"
         "• Бесконечное нажатие без инженерного смысла\n"
         "• Отсутствие аппаратных ограничений\n"
         "• Быстро теряется интерес из-за отсутствия баланса",
         ACCENT_RED),
        ("Решение: Инженерная физика",
         "⚡ Настоящие законы работы оборудования:\n"
         "• Балансировка блоков питания (ватты)\n"
         "• Нагрев видеокарт и охлаждение кулерами\n"
         "• Троттлинг при >90°C и риск перегрева при 100°C",
         MINT),
        ("Решение: Живая экономика",
         "📈 Динамическая финансовая модель:\n"
         "• Плавающий курс BTC на бирже каждые 3 сек\n"
         "• Износ деталей и платный расчётный ремонт\n"
         "• Оплата электроэнергии и продажа со склада",
         CYAN)
    ]
    for idx, (title, desc, acc) in enumerate(cards_s2):
        c_left = Inches(0.8 + idx * 3.95)
        create_card(s2, c_left, Inches(1.8), Inches(3.8), Inches(4.8))

        tb = s2.shapes.add_textbox(c_left + Inches(0.3), Inches(2.1), Inches(3.2), Inches(4.2))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(17)
        p1.font.bold = True
        p1.font.color.rgb = acc

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(13.5)
        p2.font.color.rgb = WHITE
        p2.space_before = Pt(14)

    # ==========================================
    # SLIDE 3: Goals & Tasks
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    apply_bg(s3)
    add_header(s3, "02 / Цель и задачи", "Что планировалось сделать и какие задачи были решены")

    # Goal banner
    create_card(s3, Inches(0.8), Inches(1.6), Inches(11.73), Inches(1.2), bg_color=RGBColor(24, 38, 30), border_color=MINT)
    tb_goal = s3.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(11.1), Inches(0.8))
    tf = tb_goal.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "ГЛАВНАЯ ЦЕЛЬ РАЗРАБОТКИ"
    p1.font.name = FONT_FAMILY
    p1.font.size = Pt(11)
    p1.font.bold = True
    p1.font.color.rgb = MINT
    p2 = tf.add_paragraph()
    p2.text = "Создать десктопное приложение с удобным интерфейсом на PyQt6 и реляционной базой данных SQLite3, объединяющее симуляцию «железа» и биржевую торговлю."
    p2.font.name = FONT_FAMILY
    p2.font.size = Pt(14)
    p2.font.color.rgb = WHITE

    # 4 Tasks
    tasks = [
        ("1. Проектирование БД", "Разработка 4 реляционных таблиц SQLite3 со связями Foreign Key, транзакциями commit/rollback и реализацией полного CRUD."),
        ("2. Разработка GUI", "Создание вкладок (Ферма, Магазин, Склад, Биржа), стойки 4х4 на QGridLayout, диалоговых окон и лог-терминала."),
        ("3. Игровой движок", "Математическая модель расчёта хешрейта, ватт, температурной динамики, разгона (50–150%) и алгоритма биржевых котировок."),
        ("4. Экспорт и сборка", "Формирование отчётов в CSV (UTF-8-SIG) и TXT, сборка в автономный исполняемый .exe файл через PyInstaller.")
    ]
    for idx, (t_title, t_desc) in enumerate(tasks):
        col = idx % 2
        row = idx // 2
        t_left = Inches(0.8 + col * 5.95)
        t_top = Inches(3.1 + row * 1.95)
        create_card(s3, t_left, t_top, Inches(5.75), Inches(1.75))

        tb = s3.shapes.add_textbox(t_left + Inches(0.3), t_top + Inches(0.25), Inches(5.15), Inches(1.3))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = t_title
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(16)
        p1.font.bold = True
        p1.font.color.rgb = CYAN

        p2 = tf.add_paragraph()
        p2.text = t_desc
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(12.5)
        p2.font.color.rgb = WHITE
        p2.space_before = Pt(6)

    # ==========================================
    # SLIDE 4: Architecture & Stack
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    apply_bg(s4)
    add_header(s4, "03 / Архитектура проекта", "Модульная структура по стандартам промышленной разработки")

    # Left: Stack overview
    create_card(s4, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8))
    tb_st = s4.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(3.0), Inches(4.2))
    tf = tb_st.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "СТЕК ТЕХНОЛОГИЙ"
    p1.font.name = FONT_FAMILY
    p1.font.size = Pt(16)
    p1.font.bold = True
    p1.font.color.rgb = MINT

    stack_items = [
        ("Python 3.13", "Современный стабильный интерпретатор"),
        ("PyQt6 (Qt Widgets)", "Полнофункциональный GUI-фреймворк"),
        ("SQLite3", "Реляционная встраиваемая СУБД"),
        ("PyInstaller", "Сборка в автономный дистрибутив .exe"),
        ("PEP 8 & Flake8", "Строгое соблюдение стандартов чистоты кода")
    ]
    for s_name, s_sub in stack_items:
        p_item = tf.add_paragraph()
        p_item.text = f"• {s_name}"
        p_item.font.name = FONT_FAMILY
        p_item.font.size = Pt(13)
        p_item.font.bold = True
        p_item.font.color.rgb = WHITE
        p_item.space_before = Pt(10)

        p_sub = tf.add_paragraph()
        p_sub.text = f"   {s_sub}"
        p_sub.font.name = FONT_FAMILY
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = MUTED

    # Right: 4 Modules
    modules = [
        ("main.py (26 строк)", "Точка входа", "Инициализация QApplication, создание объекта DatabaseManager, запуск AuthWindow и передача активного профиля в главное окно."),
        ("database.py (353 строки)", "Слой данных (DAO)", "Класс DatabaseManager: создание схемы, транзакции, методы покупки, ремонта, пересчёта начислений и выборки инвентаря."),
        ("dialogs.py (238 строк)", "Диалоговые окна", "AuthWindow (вход, создание профиля, аватарки), OverclockDialog (стенд разгона и ремонта) и AdminEditorWindow (добавление товаров)."),
        ("main_window.py (585 строк)", "Главное окно", "Класс MainWindow: управление вкладками, сетка слотов 4х4, таймеры симуляции, обработка хоткеев и выгрузка отчетов.")
    ]
    for idx, (m_file, m_role, m_desc) in enumerate(modules):
        m_top = Inches(1.8 + idx * 1.25)
        create_card(s4, Inches(4.7), m_top, Inches(7.8), Inches(1.15))

        tb_m = s4.shapes.add_textbox(Inches(5.0), m_top + Inches(0.12), Inches(7.2), Inches(0.9))
        tf_m = tb_m.text_frame
        tf_m.word_wrap = True
        p_m = tf_m.paragraphs[0]
        p_m.text = f"{m_file} — "
        p_m.font.name = FONT_FAMILY
        p_m.font.size = Pt(14)
        p_m.font.bold = True
        p_m.font.color.rgb = CYAN

        run_role = p_m.add_run()
        run_role.text = m_role
        run_role.font.color.rgb = MINT
        run_role.font.size = Pt(13)

        p_desc = tf_m.add_paragraph()
        p_desc.text = m_desc
        p_desc.font.name = FONT_FAMILY
        p_desc.font.size = Pt(11.5)
        p_desc.font.color.rgb = WHITE
        p_desc.space_before = Pt(2)

    # ==========================================
    # SLIDE 5: Database Schema
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    apply_bg(s5)
    add_header(s5, "04 / База данных", "4 нормализованные таблицы SQLite со связями Foreign Key")

    tables = [
        ("таблица: profiles", [
            ("id", "INTEGER PK AUTOINCREMENT"),
            ("username", "TEXT NOT NULL"),
            ("balance", "REAL ($ стартовый 200.0)"),
            ("crypto_balance", "REAL (BTC добыча)"),
            ("avatar", "TEXT (путь к фото)"),
            ("theme", "TEXT (HEX цвет темы)")
        ]),
        ("таблица: catalog", [
            ("id", "INTEGER PK AUTOINCREMENT"),
            ("name", "TEXT (GTX 1050, 4090...)"),
            ("category", "TEXT (GPU, Cooler, PSU)"),
            ("hashrate", "REAL (MH/s скорость)"),
            ("watts / heat", "INTEGER / REAL (ватты, °C)"),
            ("price", "REAL (цена в магазине)")
        ]),
        ("таблица: inventory", [
            ("id", "INTEGER PK AUTOINCREMENT"),
            ("profile_id", "INTEGER (FK -> profiles.id)"),
            ("hardware_id", "INTEGER (FK -> catalog.id)"),
            ("slot_index", "INTEGER (-1 склад, 0-15 ферма)"),
            ("overclock", "INTEGER (разгон 50-150%)"),
            ("condition", "REAL (износ 0-100%)")
        ]),
        ("таблица: transactions", [
            ("id", "INTEGER PK AUTOINCREMENT"),
            ("profile_id", "INTEGER (FK -> profiles.id)"),
            ("time", "TEXT (YYYY-MM-DD HH:MM)"),
            ("type", "TEXT (BUY, SELL, REPAIR...)"),
            ("amount", "REAL (сумма операции)"),
            ("btc_rate", "REAL (курс на момент сделки)")
        ])
    ]
    for idx, (t_name, t_fields) in enumerate(tables):
        c_left = Inches(0.8 + idx * 2.95)
        create_card(s5, c_left, Inches(1.8), Inches(2.8), Inches(4.2))

        tb = s5.shapes.add_textbox(c_left + Inches(0.2), Inches(1.95), Inches(2.4), Inches(3.9))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = t_name
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = CYAN

        for f_name, f_type in t_fields:
            p_f = tf.add_paragraph()
            p_f.text = f"• {f_name}"
            p_f.font.name = FONT_FAMILY
            p_f.font.size = Pt(11)
            p_f.font.bold = True
            p_f.font.color.rgb = WHITE
            p_f.space_before = Pt(4)

            p_t = tf.add_paragraph()
            p_t.text = f"   {f_type}"
            p_t.font.name = FONT_FAMILY
            p_t.font.size = Pt(9.5)
            p_t.font.color.rgb = MUTED

    # Bottom ACID Banner
    create_card(s5, Inches(0.8), Inches(6.15), Inches(11.73), Inches(0.8), bg_color=RGBColor(24, 38, 30), border_color=MINT)
    tb_acid = s5.shapes.add_textbox(Inches(1.1), Inches(6.25), Inches(11.1), Inches(0.6))
    tf = tb_acid.text_frame
    p = tf.paragraphs[0]
    p.text = "🛡️ Безопасность данных: Все финансовые операции (покупка, продажа, ремонт) защищены транзакциями с commit/rollback. Используются параметризованные запросы для исключения SQL-инъекций."
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11.5)
    p.font.color.rgb = WHITE

    # ==========================================
    # SLIDE 6: Gameplay & Physics
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    apply_bg(s6)
    add_header(s6, "05 / Игровой процесс", "Стойка 4×4 и расчёт инженерных параметров")

    # Left: Screenshot if exists
    img_path = r"c:\Users\Admin\Desktop\Project\screenshot_farm.png"
    if os.path.exists(img_path):
        s6.shapes.add_picture(img_path, Inches(0.8), Inches(1.8), width=Inches(5.8))
    else:
        create_card(s6, Inches(0.8), Inches(1.8), Inches(5.8), Inches(4.8))

    # Right: Physics Mechanics Cards
    phys_cards = [
        ("⚡ Балансировка питания (БП)", 
         "Каждая видеокарта требует ватты (напр. RTX 4090 — 450W). Базовая стойка даёт 400W. Дополнительные блоки питания (500W, 850W) ставятся прямо в сетку. При превышении лимита майнинг автоматически обесточивается."),
        ("🌡️ Тепловыделение и троттлинг",
         "Кулеры и СВО отводят тепло (-3°C ... -16°C). Прогресс-бар меняет цвет (зелёный -> оранжевый -> красный). При температуре >90°C падает хешрейт в 2 раза, а при 100°C срабатывает аварийная продувка."),
        ("⌨️ Интерактивность и хоткеи",
         "16 слотов кликабельны на QGridLayout. Добавлены горячие клавиши: [Пробел] — принудительная продувка, [1/2/3] — режимы мощности (0.8x/1.0x/1.3x), [F5] — быстрая продажа крипты на бирже.")
    ]
    for idx, (p_title, p_desc) in enumerate(phys_cards):
        c_top = Inches(1.8 + idx * 1.65)
        create_card(s6, Inches(6.9), c_top, Inches(5.6), Inches(1.5))

        tb = s6.shapes.add_textbox(Inches(7.1), c_top + Inches(0.15), Inches(5.2), Inches(1.2))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = p_title
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = MINT

        p2 = tf.add_paragraph()
        p2.text = p_desc
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(11)
        p2.font.color.rgb = WHITE
        p2.space_before = Pt(4)

    # ==========================================
    # SLIDE 7: Economy & Trading
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    apply_bg(s7)
    add_header(s7, "06 / Экономика и торговля", "Магазин, склад, разгонный стенд и биржа")

    econ_cards = [
        ("🛒 Магазин и Склад",
         "• Таблицы QTableWidget с сортировкой и фильтрами\n"
         "• Категории: GPU, Cooler, PSU\n"
         "• Быстрая установка детали двойным кликом по ячейке\n"
         "• Продажа ненужного оборудования за 70% цены"),
        ("🔧 Инженерный стенд",
         "• Открывается по клику на установленную карту\n"
         "• Разгон QSlider от 50% до 150%\n"
         "• Расчёт износа от режима мощности и нагрева\n"
         "• Платный ремонт по динамической формуле износа"),
        ("💱 Биржа криптовалют",
         "• Плавающий курс BTC ($40k-$90k) каждые 3 сек\n"
         "• Мгновенная продажа накопленного Bitcoin\n"
         "• Таблица всей истории финансовых транзакций\n"
         "• Списание платы за свет пропорционально ваттам"),
        ("📄 Экспорт отчётов",
         "• Меню «Файл» в верхнем баре приложения\n"
         "• Экспорт истории в .csv (UTF-8-SIG для Excel)\n"
         "• Генерация техпаспорта фермы в .txt\n"
         "• Скрытая админ-панель добавления новых товаров")
    ]
    for idx, (e_title, e_desc) in enumerate(econ_cards):
        col = idx % 2
        row = idx // 2
        c_left = Inches(0.8 + col * 5.95)
        c_top = Inches(1.8 + row * 2.5)
        create_card(s7, c_left, c_top, Inches(5.75), Inches(2.3))

        tb = s7.shapes.add_textbox(c_left + Inches(0.3), c_top + Inches(0.2), Inches(5.15), Inches(1.9))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = e_title
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(16)
        p1.font.bold = True
        p1.font.color.rgb = CYAN

        p2 = tf.add_paragraph()
        p2.text = e_desc
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(12)
        p2.font.color.rgb = WHITE
        p2.space_before = Pt(8)

    # ==========================================
    # SLIDE 8: Challenges & Solutions
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    apply_bg(s8)
    add_header(s8, "07 / Трудности и решения", "С какими инженерными проблемами столкнулся при разработке")

    challenges = [
        ("Проблема: Слишком быстрый заработок",
         "Сложность: В первой версии множитель хешрейта приносил сотни долларов в секунду, и игрок покупал топ-карты за пару минут.",
         "Решение: Пересчитал баланс — снизил базовый коэффициент добычи до 0.0000001 BTC/сек, а стартовый баланс игрока выставил в $200. Появилась реальная прогрессия."),
        ("Проблема: Обход лимитов питания",
         "Сложность: При двойном клике из таблицы склада мощная карта устанавливалась в ферму без проверки остатка мощности БП.",
         "Решение: Вынес функцию подсчёта get_power_info(), привязал валидацию к обоим способам установки и внедрил автоотключение фермы при перегрузке в game_tick()."),
        ("Проблема: «Кракозябры» в Excel при экспорте",
         "Сложность: Стандартный экспорт CSV в utf-8 открывался в Excel с повреждёнными русскими символами, а запятая ломала столбцы.",
         "Решение: Применил кодировку utf-8-sig (с BOM-байтом) и символ ';' в качестве разделителя колонок — теперь отчёт идеально открывается в любом табличном редакторе.")
    ]
    for idx, (ch_title, ch_prob, ch_sol) in enumerate(challenges):
        c_top = Inches(1.8 + idx * 1.65)
        create_card(s8, Inches(0.8), c_top, Inches(11.73), Inches(1.5))

        tb = s8.shapes.add_textbox(Inches(1.1), c_top + Inches(0.15), Inches(11.1), Inches(1.2))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = ch_title
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(15)
        p1.font.bold = True
        p1.font.color.rgb = ACCENT_RED

        p2 = tf.add_paragraph()
        p2.text = ch_prob
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(11.5)
        p2.font.color.rgb = MUTED
        p2.space_before = Pt(3)

        p3 = tf.add_paragraph()
        p3.text = f"✅ {ch_sol}"
        p3.font.name = FONT_FAMILY
        p3.font.size = Pt(12)
        p3.font.bold = True
        p3.font.color.rgb = MINT
        p3.space_before = Pt(3)

    # ==========================================
    # SLIDE 9: Results & Future
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    apply_bg(s9)
    add_header(s9, "08 / Итоги и планы", "Чему научился в проекте и как его можно развивать дальше")

    # Left: Results
    create_card(s9, Inches(0.8), Inches(1.8), Inches(5.75), Inches(4.8))
    tb_res = s9.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(5.15), Inches(4.2))
    tf = tb_res.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "ИТОГИ РАЗРАБОТКИ"
    p1.font.name = FONT_FAMILY
    p1.font.size = Pt(18)
    p1.font.bold = True
    p1.font.color.rgb = MINT

    res_items = [
        "Полностью рабочий симулятор (1064 строки чистого кода по стандарту PEP 8)",
        "Освоен стек PyQt6: сетки слотов, вкладки, таблицы, кастомные диалоги, хоткеи",
        "Освоена работа с SQLite3: транзакции ACID, сложные выборки JOIN, агрегаты",
        "Собран автономный исполняемый файл .exe (35 МБ) через PyInstaller",
        "Исходный код и релиз опубликованы на GitHub: github.com/NSDKJDKL/Project"
    ]
    for it in res_items:
        p = tf.add_paragraph()
        p.text = f"✓  {it}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(12.5)
        p.font.color.rgb = WHITE
        p.space_before = Pt(10)

    # Right: Future Plans
    create_card(s9, Inches(6.8), Inches(1.8), Inches(5.73), Inches(4.8))
    tb_fut = s9.shapes.add_textbox(Inches(7.1), Inches(2.1), Inches(5.15), Inches(4.2))
    tf_fut = tb_fut.text_frame
    tf_fut.word_wrap = True
    p1 = tf_fut.paragraphs[0]
    p1.text = "ПЛАНЫ НА БУДУЩЕЕ"
    p1.font.name = FONT_FAMILY
    p1.font.size = Pt(18)
    p1.font.bold = True
    p1.font.color.rgb = CYAN

    fut_items = [
        ("Мультивалютность", "Добавление добычи альтернативных монет (Ethereum, Kaspa, Monero) с разными алгоритмами."),
        ("Интерактивные графики", "Отображение графиков биржевого курса и доходности фермы в реальном времени (PyQtGraph)."),
        ("Звуковое оформление", "Звуки шума кулеров при разгоне, аварийный зуммер при перегрузке БП и перегреве."),
        ("Случайные события", "Рандомные события (скачки напряжения в сети, поломка вентилятора, памп/дамп монеты на бирже).")
    ]
    for f_title, f_desc in fut_items:
        p_ft = tf_fut.add_paragraph()
        p_ft.text = f"🚀 {f_title}"
        p_ft.font.name = FONT_FAMILY
        p_ft.font.size = Pt(13)
        p_ft.font.bold = True
        p_ft.font.color.rgb = WHITE
        p_ft.space_before = Pt(10)

        p_fd = tf_fut.add_paragraph()
        p_fd.text = f"   {f_desc}"
        p_fd.font.name = FONT_FAMILY
        p_fd.font.size = Pt(11.5)
        p_fd.font.color.rgb = MUTED

    output_path = r"c:\Users\Admin\Desktop\Project\presentation.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to {output_path}")

if __name__ == "__main__":
    build_presentation()
