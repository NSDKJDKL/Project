import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_clean_deck():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Clean, bright color palette inspired by the reference
    BG_WHITE = RGBColor(255, 255, 255)         # Pure white
    TEXT_MAIN = RGBColor(17, 24, 39)           # Very dark charcoal (#111827)
    TEXT_MUTED = RGBColor(75, 85, 99)          # Slate gray (#4B5563)
    ACCENT_GREEN = RGBColor(16, 185, 129)      # Emerald / fresh green (#10B981)
    PILL_BG = RGBColor(236, 253, 245)          # Soft light green tint (#ECFDF5)
    PILL_BORDER = RGBColor(167, 243, 208)      # Soft green border (#A7F3D0)
    PILL_TEXT = RGBColor(4, 120, 87)           # Deep forest green (#047857)
    CARD_BG = RGBColor(249, 250, 251)          # Light warm gray (#F9FAFB)
    CARD_BORDER = RGBColor(229, 231, 235)      # Light border (#E5E7EB)

    FONT_FAMILY = "Segoe UI"

    def apply_bg(slide):
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = BG_WHITE

        # Subtle elegant green top-right accent shape (like in reference)
        accent = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, Inches(10.5), Inches(-1.5), Inches(4.5), Inches(4.5)
        )
        accent.fill.solid()
        accent.fill.fore_color.rgb = RGBColor(236, 253, 245)
        accent.line.fill.background()

    def add_pill(slide, left, top, text):
        # Pill tag badge
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, Inches(len(text) * 0.11 + 0.5), Inches(0.42))
        shape.fill.solid()
        shape.fill.fore_color.rgb = PILL_BG
        shape.line.color.rgb = PILL_BORDER
        shape.line.width = Pt(1)

        tf = shape.text_frame
        tf.word_wrap = False
        tf.margin_left = tf.margin_right = Inches(0.15)
        tf.margin_top = tf.margin_bottom = Inches(0.05)
        p = tf.paragraphs[0]
        p.text = text
        p.font.name = FONT_FAMILY
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = PILL_TEXT
        return shape

    def add_header(slide, pill_text, title_text, subtitle_text=""):
        add_pill(slide, Inches(0.8), Inches(0.5), pill_text)

        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.0), Inches(11.5), Inches(0.6))
        tf = title_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = FONT_FAMILY
        p.font.size = Pt(26)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN

        if subtitle_text:
            p_sub = tf.add_paragraph()
            p_sub.text = subtitle_text
            p_sub.font.name = FONT_FAMILY
            p_sub.font.size = Pt(13)
            p_sub.font.color.rgb = TEXT_MUTED
            p_sub.space_before = Pt(4)

    def add_framed_image(slide, img_path, left, top, width, height=None):
        if not os.path.exists(img_path):
            return None
        # Subtle outer container border
        pic = slide.shapes.add_picture(img_path, left, top, width=width, height=height)
        return pic

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    apply_bg(s1)

    add_pill(s1, Inches(1.0), Inches(1.2), "ИНДИВИДУАЛЬНЫЙ ПРОЕКТ • ЯНДЕКС.ЛИЦЕЙ")

    # Title
    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(6.5), Inches(1.5))
    tf = t_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p1 = tf.paragraphs[0]
    p1.text = "Симулятор\nмайнинг-фермы"
    p1.font.name = FONT_FAMILY
    p1.font.size = Pt(38)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_MAIN

    p_sub = tf.add_paragraph()
    p_sub.text = "Mining Farm Simulator"
    p_sub.font.name = FONT_FAMILY
    p_sub.font.size = Pt(20)
    p_sub.font.bold = True
    p_sub.font.color.rgb = ACCENT_GREEN
    p_sub.space_before = Pt(6)

    # Description
    desc_box = s1.shapes.add_textbox(Inches(1.0), Inches(3.7), Inches(5.8), Inches(1.2))
    tf_d = desc_box.text_frame
    tf_d.word_wrap = True
    tf_d.margin_left = tf_d.margin_top = tf_d.margin_right = tf_d.margin_bottom = 0
    p_d = tf_d.paragraphs[0]
    p_d.text = "Десктопное приложение с реляционной базой данных SQLite3 и симуляцией реальной физики серверного оборудования."
    p_d.font.name = FONT_FAMILY
    p_d.font.size = Pt(14)
    p_d.font.color.rgb = TEXT_MUTED

    # Bottom Pills
    add_pill(s1, Inches(1.0), Inches(5.2), "Автор: Виталий")
    add_pill(s1, Inches(2.9), Inches(5.2), "Стек: Python 3.13 • PyQt6 • SQLite3")
    add_pill(s1, Inches(6.5), Inches(5.2), "Год: 2026")

    # Right side: Screenshot Showcase
    add_framed_image(s1, "shot_farm.png", Inches(7.3), Inches(1.3), Inches(5.3))

    # ==========================================
    # SLIDE 2: Concept & Real Physics
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    apply_bg(s2)
    add_header(s2, "КОНЦЕПЦИЯ ПРОЕКТА", "Отказ от кликера в пользу физики и экономики", "Почему симулятор построен на аппаратных ограничениях")

    concepts = [
        ("1. Энергобаланс и блоки питания",
         "Каждое устройство потребляет ватты (напр. RTX 4090 — 450W). Базовая ферма имеет лимит 400W. Чтобы расширять стойку, игрок обязан докупать и ставить блоки питания (500W, 850W). При превышении лимита майнинг автоматически обесточивается."),
        ("2. Тепловыделение и троттлинг",
         "Видеокарты выделяют тепло, которое компенсируют кулеры и системы водяного охлаждения. Шкала температуры меняет цвет от зелёного к красному. При нагреве выше 90°C включается троттлинг (падение хешрейта на 50%), а при 100°C — аварийная продувка."),
        ("3. Разгон, износ и платный ремонт",
         "Каждую видеокарту можно разогнать от 50% до 150%, что увеличивает доход, но кратно ускоряет износ. Стоимость ремонта рассчитывается по математической формуле от процента повреждений и магазинной стоимости детали.")
    ]
    for idx, (c_head, c_body) in enumerate(concepts):
        c_left = Inches(0.8 + idx * 3.95)
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c_left, Inches(2.1), Inches(3.8), Inches(4.7))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1)

        tb = s2.shapes.add_textbox(c_left + Inches(0.25), Inches(2.35), Inches(3.3), Inches(4.2))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p_h = tf.paragraphs[0]
        p_h.text = c_head
        p_h.font.name = FONT_FAMILY
        p_h.font.size = Pt(15)
        p_h.font.bold = True
        p_h.font.color.rgb = ACCENT_GREEN

        p_b = tf.add_paragraph()
        p_b.text = c_body
        p_b.font.name = FONT_FAMILY
        p_b.font.size = Pt(12)
        p_b.font.color.rgb = TEXT_MUTED
        p_b.space_before = Pt(12)

    # ==========================================
    # SLIDE 3: Main Rack 4x4
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    apply_bg(s3)
    add_header(s3, "ОСНОВНОЙ ЭКРАН", "Интерактивная стойка 4×4", "Центральный интерфейс управления оборудованием фермы")

    # Left: Screenshot
    add_framed_image(s3, "shot_farm.png", Inches(0.8), Inches(2.0), Inches(5.8))

    # Right: Description points
    r_box = s3.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.5), Inches(4.8))
    tf_r = r_box.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_top = tf_r.margin_right = tf_r.margin_bottom = 0

    points_s3 = [
        ("16 интерактивных слотов", "Сетка построена на QGridLayout. Клик по пустому слоту открывает диалог установки детали из инвентаря, клик по занятому — инженерный стенд."),
        ("Мониторинг питания и перегрузки", "Виджет в шапке отслеживает текущее потребление и лимит (напр. 2550 / 500 W). При превышении срабатывает блокировка майнинга."),
        ("Индикатор температуры", "QProgressBar с цветовыми порогами (зелёный до 75°C, оранжевый до 90°C, красный при перегреве)."),
        ("Горячие клавиши", "Пробел — принудительная продувка кулерами; клавиши 1, 2, 3 — переключение режимов мощности (0.8x, 1.0x, 1.3x); F5 — быстрая продажа крипты."),
        ("Лог-терминал", "QTextBrowser с временными метками и цветным выделением ключевых игровых событий.")
    ]
    for idx, (title, desc) in enumerate(points_s3):
        p_t = tf_r.paragraphs[0] if idx == 0 else tf_r.add_paragraph()
        p_t.text = f"• {title}"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_MAIN
        if idx > 0:
            p_t.space_before = Pt(8)

        p_d = tf_r.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 4: Profiles & Personalization
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    apply_bg(s4)
    add_header(s4, "СИСТЕМА ПРОФИЛЕЙ", "Авторизация и персонализация", "Сохранение игрового прогресса и кастомизация")

    add_framed_image(s4, "shot_auth.png", Inches(0.8), Inches(2.2), Inches(5.4))

    r_box4 = s4.shapes.add_textbox(Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.8))
    tf4 = r_box4.text_frame
    tf4.word_wrap = True
    tf4.margin_left = tf4.margin_top = tf4.margin_right = tf4.margin_bottom = 0

    points_s4 = [
        ("Мультипрофильность", "Возможность выбора существующего игрока из выпадающего списка QComboBox или создание нового профиля в SQLite."),
        ("Загрузка аватара", "Выбор изображения через системный диалог QFileDialog с автоматическим масштабированием и центрированием через QPixmap."),
        ("Система промокодов", "Встроенная активация кодов (YANDEX, START, 2026) для получения стартового капитала через QInputDialog."),
        ("Персонализация темы", "Выбор акцентного цвета интерфейса фермы через QColorDialog с сохранением в таблицу profiles.")
    ]
    for idx, (title, desc) in enumerate(points_s4):
        p_t = tf4.paragraphs[0] if idx == 0 else tf4.add_paragraph()
        p_t.text = f"• {title}"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(14)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_MAIN
        if idx > 0:
            p_t.space_before = Pt(12)

        p_d = tf4.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 5: Overclock & Maintenance
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    apply_bg(s5)
    add_header(s5, "ИНЖЕНЕРНЫЙ СТЕНД", "Разгон и обслуживание оборудования", "Индивидуальная настройка каждой установленной карты")

    add_framed_image(s5, "shot_overclock.png", Inches(0.8), Inches(2.4), Inches(5.5))

    r_box5 = s5.shapes.add_textbox(Inches(6.9), Inches(2.0), Inches(5.6), Inches(4.8))
    tf5 = r_box5.text_frame
    tf5.word_wrap = True
    tf5.margin_left = tf5.margin_top = tf5.margin_right = tf5.margin_bottom = 0

    points_s5 = [
        ("Модальный диалог управления", "Открывается кликом по любой рабочей ячейке стойки (OverclockDialog). Отображает модель, категорию и текущее состояние."),
        ("Ползунок разгона (50% – 150%)", "Горизонтальный слайдер QSlider. Увеличивает скорость хешрейта, но пропорционально ускоряет нагрев и темп износа."),
        ("Индикатор техсостояния", "QProgressBar со значением от 0 до 100%. При нулевом состоянии карта перестаёт приносить доход до ремонта."),
        ("Расчёт стоимости ремонта", "Динамическая формула: max(5.0, round(wear * (price / 100.0) * 0.35, 2)). Учитывает класс карты и процент повреждения."),
        ("Перемещение на склад", "Кнопка «На склад» освобождает ячейку стойки и меняет slot_index на -1.")
    ]
    for idx, (title, desc) in enumerate(points_s5):
        p_t = tf5.paragraphs[0] if idx == 0 else tf5.add_paragraph()
        p_t.text = f"• {title}"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_MAIN
        if idx > 0:
            p_t.space_before = Pt(8)

        p_d = tf5.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 6: Shop & Warehouse
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    apply_bg(s6)
    add_header(s6, "КАТАЛОГ И СКЛАД", "Магазин и инвентарь комплектующих", "Полный цикл закупки, хранения и вторичной продажи")

    add_framed_image(s6, "shot_shop.png", Inches(0.8), Inches(1.9), Inches(3.6))
    add_framed_image(s6, "shot_inv.png", Inches(4.7), Inches(1.9), Inches(3.6))

    r_box6 = s6.shapes.add_textbox(Inches(8.7), Inches(1.9), Inches(3.8), Inches(4.8))
    tf6 = r_box6.text_frame
    tf6.word_wrap = True
    tf6.margin_left = tf6.margin_top = tf6.margin_right = tf6.margin_bottom = 0

    points_s6 = [
        ("Табличные представления", "QTableWidget в режимах SelectRows и NoEditTriggers для надёжности."),
        ("Фильтрация товаров", "Выпадающий список категорий: GPU (видеокарты), Cooler (кулеры) и PSU (блоки питания)."),
        ("Быстрая установка", "Двойной клик по строке на складе мгновенно монтирует деталь в свободный слот стойки с валидацией БП."),
        ("Вторичная продажа", "Возможность продать ненужную деталь со склада за 70% от магазинной цены со списанием из базы.")
    ]
    for idx, (title, desc) in enumerate(points_s6):
        p_t = tf6.paragraphs[0] if idx == 0 else tf6.add_paragraph()
        p_t.text = f"• {title}"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_MAIN
        if idx > 0:
            p_t.space_before = Pt(10)

        p_d = tf6.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 7: Exchange & Export
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    apply_bg(s7)
    add_header(s7, "БИРЖА И ОТЧЁТЫ", "Криптовалютная биржа и экспорт данных", "Торговля, история операций и выгрузка отчётов")

    add_framed_image(s7, "shot_exchange.png", Inches(0.8), Inches(2.0), Inches(5.8))

    r_box7 = s7.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.5), Inches(4.8))
    tf7 = r_box7.text_frame
    tf7.word_wrap = True
    tf7.margin_left = tf7.margin_top = tf7.margin_right = tf7.margin_bottom = 0

    points_s7 = [
        ("Плавающий курс Bitcoin", "Курс колеблется в коридоре $40 000 – $90 000 каждые 3 секунды по таймеру QTimer."),
        ("Мгновенная конвертация", "Кнопка «Продать всю крипту» пересчитывает баланс по текущей биржевой цене."),
        ("История транзакций", "Журнал всех операций (покупка, продажа, ремонт, электроэнергия) в таблице QTableWidget."),
        ("Экспорт в CSV (Excel)", "Выгрузка в файл CSV с кодировкой utf-8-sig (BOM-байт) и разделителем ';' для корректного открытия в Microsoft Excel."),
        ("Техпаспорт фермы (TXT)", "Генерация текстового паспорта со списком установленного оборудования, его износом и слотами.")
    ]
    for idx, (title, desc) in enumerate(points_s7):
        p_t = tf7.paragraphs[0] if idx == 0 else tf7.add_paragraph()
        p_t.text = f"• {title}"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_MAIN
        if idx > 0:
            p_t.space_before = Pt(8)

        p_d = tf7.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 8: Database & Architecture
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    apply_bg(s8)
    add_header(s8, "АРХИТЕКТУРА И SQLITE", "Реляционная база данных и админ-панель", "Схема данных, транзакции и скрытое окно администратора")

    add_framed_image(s8, "shot_admin.png", Inches(0.8), Inches(2.2), Inches(4.5))

    r_box8 = s8.shapes.add_textbox(Inches(5.8), Inches(1.9), Inches(6.7), Inches(5.0))
    tf8 = r_box8.text_frame
    tf8.word_wrap = True
    tf8.margin_left = tf8.margin_top = tf8.margin_right = tf8.margin_bottom = 0

    points_s8 = [
        ("4 нормализованные таблицы", "profiles (игроки), catalog (товары магазина), inventory (склад и ферма), transactions (журнал)."),
        ("Целостность данных (Foreign Key)", "Таблицы inventory и transactions связаны с profiles и catalog внешними ключами."),
        ("Транзакционность (ACID)", "Все изменения баланса и инвентаря защищены блоками commit / rollback. Параметризованные SQL-запросы."),
        ("Скрытая админ-панель", "Вызывается из меню по паролю 'admin'. Форма QFormLayout с полями QDoubleSpinBox и QSpinBox позволяет добавлять новые видеокарты и кулеры в магазин без ручной правки базы данных.")
    ]
    for idx, (title, desc) in enumerate(points_s8):
        p_t = tf8.paragraphs[0] if idx == 0 else tf8.add_paragraph()
        p_t.text = f"• {title}"
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_MAIN
        if idx > 0:
            p_t.space_before = Pt(10)

        p_d = tf8.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(11.5)
        p_d.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 9: Project Results & Completion
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    apply_bg(s9)
    add_header(s9, "ИТОГИ РАЗРАБОТКИ", "Результаты проекта", "Завершённый и опубликованный продукт")

    res_cards = [
        ("Чистый код и стандарты",
         "• 1064 строки чистого кода на Python 3.13\n"
         "• Разделение на 4 независимых модуля\n"
         "• 100% соответствие стандарту PEP 8\n"
         "• Пройдена строгая проверка линтером Flake8"),
        ("Автономная сборка (.exe)",
         "• Приложение упаковано через PyInstaller\n"
         "• Единый файл main.exe размером 35.8 МБ\n"
         "• Запускается на чистой Windows без Python\n"
         "• Все зависимости PyQt6 включены в сборку"),
        ("Открытый репозиторий",
         "• Исходный код загружен на GitHub\n"
         "• Репозиторий: github.com/NSDKJDKL/Project\n"
         "• Настроен .gitignore и requirements.txt\n"
         "• Подробная документация в README.md")
    ]
    for idx, (r_head, r_body) in enumerate(res_cards):
        c_left = Inches(0.8 + idx * 3.95)
        card = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c_left, Inches(2.0), Inches(3.8), Inches(3.8))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1)

        tb = s9.shapes.add_textbox(c_left + Inches(0.25), Inches(2.25), Inches(3.3), Inches(3.3))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p_h = tf.paragraphs[0]
        p_h.text = r_head
        p_h.font.name = FONT_FAMILY
        p_h.font.size = Pt(15)
        p_h.font.bold = True
        p_h.font.color.rgb = ACCENT_GREEN

        p_b = tf.add_paragraph()
        p_b.text = r_body
        p_b.font.name = FONT_FAMILY
        p_b.font.size = Pt(12)
        p_b.font.color.rgb = TEXT_MUTED
        p_b.space_before = Pt(12)

    # Bottom Farewell Banner
    banner = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.1), Inches(11.73), Inches(0.8))
    banner.fill.solid()
    banner.fill.fore_color.rgb = PILL_BG
    banner.line.color.rgb = PILL_BORDER
    banner.line.width = Pt(1)

    tb_b = s9.shapes.add_textbox(Inches(1.1), Inches(6.25), Inches(11.1), Inches(0.5))
    tf_b = tb_b.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = "Спасибо за внимание! Готов ответить на вопросы по проекту."
    p_b.font.name = FONT_FAMILY
    p_b.font.size = Pt(14)
    p_b.font.bold = True
    p_b.font.color.rgb = PILL_TEXT
    p_b.alignment = PP_ALIGN.CENTER

    out_file = r"c:\Users\Admin\Desktop\Project\presentation.pptx"
    prs.save(out_file)
    print(f"Clean deck successfully saved to {out_file}")

if __name__ == "__main__":
    build_clean_deck()
