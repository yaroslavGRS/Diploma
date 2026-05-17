"""
Self-healing Selenium driver з YOLOv8.

Звичайний режим:  find_element(by, value) → стандартний Selenium.
Режим відновлення: якщо Selenium кидає NoSuchElementException,
                   система робить скріншот і запускає YOLOv8 щоб
                   знайти елемент візуально за його типом (кнопка, поле вводу).

Як це працює:
1. Selenium шукає елемент по CSS-селектору або ID.
2. Якщо елемент не знайдено — перехоплюємо помилку.
3. Робимо скріншот всієї сторінки.
4. YOLOv8 аналізує скріншот і повертає список знайдених елементів
   з їх координатами і типами (Button, input, Dropdown).
5. Ми вибираємо потрібний елемент по типу і порядковому номеру.
6. Повертаємо DOM-елемент через document.elementFromPoint().
"""

import os
import time
import numpy as np
import cv2
from ultralytics import YOLO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


# Шлях до натренованої моделі YOLOv8
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'best.pt')

# Папка для збереження візуалізацій bounding boxes
VISUALS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results', 'visuals')

# Кольори для кожного класу (BGR формат для OpenCV)
CLASS_COLORS = {
    'Button':   (0, 200, 0),    # green
    'input':    (255, 100, 0),  # blue
    'Dropdown': (0, 165, 255),  # orange
}

# Відповідність між логічним іменем елемента і класом YOLO + індексом.
# Індекс потрібен коли на сторінці кілька елементів одного типу
# (наприклад, два поля вводу — email і password).
# Елементи сортуються зверху вниз за координатою Y.
ELEMENT_MAP = {
    # Login form
    'email':        ('input', 0),   # перше поле вводу
    'password':     ('input', 1),   # друге поле вводу
    'btn':          ('Button', 0),  # перша кнопка

    # Registration form (3 inputs: name, email, password)
    'reg-name':     ('input', 0),   # перше поле — ім'я
    'reg-email':    ('input', 1),   # друге поле — email
    'reg-password': ('input', 2),   # третє поле — пароль
    'reg-btn':      ('Button', 0),  # кнопка реєстрації
}


class SelfHealingDriver:
    """
    Обгортка над Selenium WebDriver з візуальним відновленням через YOLOv8.
    """

    def __init__(self, headless: bool = True):
        options = Options()
        if headless:
            options.add_argument('--headless=new')
        # Фіксований розмір вікна гарантує стабільні координати елементів.
        options.add_argument('--window-size=1280,800')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        self._driver = webdriver.Chrome(options=options)

        # Завантажуємо натреновану модель YOLOv8 один раз при старті.
        self._model = YOLO(MODEL_PATH)

        # Статистика для таблиці результатів.
        self.stats = {'normal': 0, 'healed': 0, 'failed': 0}

        # Час виконання: скільки секунд витрачено на звичайний пошук vs YOLOv8
        self.timing = {'normal': 0.0, 'yolo': 0.0}

        os.makedirs(VISUALS_DIR, exist_ok=True)

    # ------------------------------------------------------------------
    # Публічний інтерфейс
    # ------------------------------------------------------------------

    def get(self, url: str):
        self._driver.get(url)

    def quit(self):
        self._driver.quit()

    @property
    def current_url(self):
        return self._driver.current_url

    def find_element(self, by, value: str, element_id: str = None):
        """
        Спочатку пробуємо звичайний Selenium.
        При NoSuchElementException — запускаємо YOLOv8.

        Параметри
        ---------
        by          : константа selenium.webdriver.common.by.By
        value       : рядок селектора
        element_id  : логічне ім'я елемента (ключ у ELEMENT_MAP).
                      Якщо не вказано — використовується value.
        """
        if element_id is None:
            element_id = value

        t0 = time.perf_counter()
        try:
            element = self._driver.find_element(by, value)
            self.timing['normal'] += time.perf_counter() - t0
            self.stats['normal'] += 1
            return element

        except NoSuchElementException:
            self.timing['normal'] += time.perf_counter() - t0
            print(f"  [self-healing] '{value}' не знайдено — запускаємо YOLOv8")
            t1 = time.perf_counter()
            healed = self._yolo_find(element_id)
            self.timing['yolo'] += time.perf_counter() - t1
            if healed:
                self.stats['healed'] += 1
                return healed
            self.stats['failed'] += 1
            raise

    def send_keys_to(self, by, value: str, text: str, element_id: str = None):
        """Знайти елемент і ввести текст."""
        el = self.find_element(by, value, element_id=element_id)
        el.clear()
        el.send_keys(text)

    def click(self, by, value: str, element_id: str = None):
        """Знайти елемент і клікнути."""
        el = self.find_element(by, value, element_id=element_id)
        el.click()

    def save_detection_visual(self, filename: str, title: str = ""):
        """
        Робить скріншот поточної сторінки, запускає YOLOv8 на ньому
        і зберігає зображення з намальованими bounding boxes навколо
        всіх знайдених елементів.

        Використовується для генерації ілюстрацій до дипломної роботи.
        Зберігає файл у results/visuals/<filename>.png
        """
        png_bytes  = self._driver.get_screenshot_as_png()
        screenshot = cv2.imdecode(
            np.frombuffer(png_bytes, np.uint8), cv2.IMREAD_COLOR
        )

        results = self._model(screenshot, conf=0.3, verbose=False)
        detected = 0

        # Малюємо bounding box і підпис для кожного знайденого елемента
        for box in results[0].boxes:
            class_name = self._model.names[int(box.cls)]
            confidence = float(box.conf)
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            color = CLASS_COLORS.get(class_name, (200, 200, 200))

            # Рамка навколо елемента (товщина 2px)
            cv2.rectangle(screenshot, (x1, y1), (x2, y2), color, 2)

            # Підпис з назвою класу і впевненістю
            label = f"{class_name} {confidence:.2f}"
            (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
            cv2.rectangle(screenshot, (x1, y1 - lh - 6), (x1 + lw + 4, y1), color, -1)
            cv2.putText(
                screenshot, label, (x1 + 2, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1
            )
            detected += 1

        # Додаємо інформаційну панель знизу зображення
        h, w = screenshot.shape[:2]
        panel = np.zeros((60, w, 3), dtype=np.uint8)
        panel[:] = (40, 40, 40)  # темно-сірий фон

        info_title = title if title else filename
        info_text  = f"YOLOv8 detected: {detected} elements"

        cv2.putText(panel, info_title, (12, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 1)
        cv2.putText(panel, info_text, (12, 48),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (100, 220, 100), 1)

        # Легенда кольорів праворуч
        legend_x = w - 280
        for i, (cls, color) in enumerate(CLASS_COLORS.items()):
            lx = legend_x + i * 90
            cv2.rectangle(panel, (lx, 18), (lx + 14, 32), color, -1)
            cv2.putText(panel, cls, (lx + 18, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

        screenshot = np.vstack([screenshot, panel])

        path = os.path.join(VISUALS_DIR, f"{filename}.png")
        cv2.imwrite(path, screenshot)
        print(f"  [visual] збережено → {path}")
        return path

    # ------------------------------------------------------------------
    # Візуальне відновлення через YOLOv8
    # ------------------------------------------------------------------

    def _yolo_find(self, element_id: str):
        """
        Робить скріншот сторінки, запускає YOLOv8 і повертає
        DOM-елемент за координатами знайденого об'єкта.

        YOLOv8 повертає bounding box у форматі [x1, y1, x2, y2].
        Ми беремо центр box і передаємо його в document.elementFromPoint().
        """
        if element_id not in ELEMENT_MAP:
            print(f"  [self-healing] '{element_id}' відсутній у ELEMENT_MAP")
            return None

        yolo_class, index = ELEMENT_MAP[element_id]

        # Робимо скріншот сторінки і конвертуємо в numpy array для YOLO.
        png_bytes = self._driver.get_screenshot_as_png()
        screenshot = cv2.imdecode(
            np.frombuffer(png_bytes, np.uint8), cv2.IMREAD_COLOR
        )

        # Запускаємо YOLOv8 детекцію.
        # conf=0.3 — мінімальна впевненість 30% (достатньо для UI елементів).
        results = self._model(screenshot, conf=0.3, verbose=False)

        # Збираємо всі детекції потрібного класу, сортуємо зверху вниз.
        detections = []
        for box in results[0].boxes:
            class_name = self._model.names[int(box.cls)]
            if class_name == yolo_class:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = float(box.conf)
                detections.append((y1, x1, y2, x2, confidence))

        # Сортуємо за координатою Y — від верху до низу сторінки.
        detections.sort(key=lambda d: d[0])

        if index >= len(detections):
            print(
                f"  [self-healing] знайдено {len(detections)} елементів "
                f"класу '{yolo_class}', потрібен індекс {index}"
            )
            return None

        y1, x1, y2, x2, confidence = detections[index]

        # Центр знайденого bounding box.
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        print(
            f"  [self-healing] '{element_id}' знайдено як '{yolo_class}' "
            f"в позиції ({cx}, {cy}), впевненість={confidence:.2f}"
        )

        # Повертаємо DOM-елемент за координатами.
        element = self._driver.execute_script(
            "return document.elementFromPoint(arguments[0], arguments[1]);",
            cx, cy
        )
        return element
