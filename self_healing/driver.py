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
import numpy as np
import cv2
from ultralytics import YOLO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


# Шлях до натренованої моделі YOLOv8
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'best.pt')

# Відповідність між логічним іменем елемента і класом YOLO + індексом.
# Індекс потрібен коли на сторінці кілька елементів одного типу
# (наприклад, два поля вводу — email і password).
# Елементи сортуються зверху вниз за координатою Y.
ELEMENT_MAP = {
    'email':    ('input', 0),   # перше поле вводу зверху
    'password': ('input', 1),   # друге поле вводу
    'btn':      ('Button', 0),  # перша кнопка
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

        try:
            element = self._driver.find_element(by, value)
            self.stats['normal'] += 1
            return element

        except NoSuchElementException:
            print(f"  [self-healing] '{value}' не знайдено — запускаємо YOLOv8")
            healed = self._yolo_find(element_id)
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
