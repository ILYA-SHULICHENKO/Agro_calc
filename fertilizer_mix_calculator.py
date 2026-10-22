# Применяем

import json

from datetime import datetime

with open("preparations.json", "r", encoding="utf-8") as prep_file:
    prep_db = json.load(prep_file)

output_log = []


def log(text=""):
    print(text)
    output_log.append(text)


log("АГРО-КАЛЬКУЛЯТОР СМЕШИВАНИЯ ХИМИИ (ОФЛАЙН) для КФХ и ЛПХ")
log("=" * 50)
log()

# Метров квадратных в 1 гектаре
METERS_IN_GA = 10000

PERCENTS = 100


def input_setting(input_data, allow_empty=False):
    while True:
        input_line = input(input_data).strip()
        if allow_empty and input_line == "":
            return None

        change_dot = input_line.replace(",", ".")
        try:
            return float(change_dot)
        except ValueError:
            print("Ошибка: введите корректное число.")


while True:
    try:
        input_type = int(
            input("Выберите цифру: 1. Указать Длину х Ширину, 2. Указать га: ")
        )
        if input_type == 1:
            area_length = input_setting("Укажите длину поля в метрах (например 1000): ")
            area_width = input_setting("Укажите ширину поля в метрах (например 2000): ")
            # Рассчет площади
            area = area_length * area_width / METERS_IN_GA
            break

        elif input_type == 2:
            area = input_setting("Укажите площадь га (например 100): ")
            break
        else:
            print("Ошибка! Укажите именно 1 или 2")
    except ValueError:
        print("Ошибка! Сделайте выбор.")

trunk_volume = input_setting("Укажите объем одного бака опрыскивателя в литрах: ")

# Валидация количества баков (от 1 до 4)
while True:
    try:
        trunk_quantity = int(
            input("Укажите количество баков в опрыскивателе (от 1 до 4) шт: ")
        )
        if 1 <= trunk_quantity <= 4:
            break
        else:
            print("Ошибка! Количество баков должно быть от 1 до 4.")
    except ValueError:
        print("Ошибка! Введите целое число.")

water_per_1ga = input_setting("Укажите расход воды на 1 га в литрах: ")

while True:
    multi_choice = input(
        "Укажите номер культуры. 1. Картофель, 2. Зерновые (Пшеница, Ячмень) 3. Подсолнечник, кукуруза: "
    )
    culture_id = multi_choice.strip()

    # Рассчеты
    if culture_id in prep_db:
        break
    else:
        print("Ошибка! Неверный номер культуры. Пожалуйста выберите из списка")

culture_data = prep_db[culture_id]
log(f"\nДоступные препараты для категории '{culture_data['culture_name']}':")
for prep_key, prep_value in culture_data["preparations"].items():
    log(
        f"{prep_key}. {prep_value['name']} (Рекомендуемая норма: {prep_value['rate_per_ha']} л/кг на га)"
    )

while True:
    preparations_list = input("\nВыберите номера удобрений для смеси через запятую: ")
    selected_preparations = [
        preparations_choice.strip()
        for preparations_choice in preparations_list.split(",")
    ]

    all_preparations_valid = True

    # Все ли введенные препараты есть в базе данных
    for prep_id in selected_preparations:
        if prep_id not in culture_data["preparations"]:
            print(
                f"Ошибка: Препарата под номером '{prep_id}' не существует в базе данных для выбранной культуры!"
            )
            all_preparations_valid = False
            break
    if all_preparations_valid:
        break
    else:
        print("Пожалуйста, повторите ввод номеров корректно через запятую.")

# РАСЧЕТ ПАРАМЕТРОВ ПОЛЯ, БАКОВ И ОБЩЕЙ ВОДЫ
# Расчет общего количества воды на все поле
total_water_for_field = area * water_per_1ga

# Общий объем всех баков опрыскивателя вместе
total_machine_volume = trunk_volume * trunk_quantity

# Определение площади, обрабатываемой за ОДНУ полную заправку всей машины (всех баков)
square_per_1machine = total_machine_volume / water_per_1ga

# Сколько необходимо полных заправок машины на всё поле
trunks_quantity_per_area = (area * water_per_1ga) / total_machine_volume

log("\n" + "=" * 50)
log(f"Рассчитанная площадь поля: {area:.2f} га")
log(f"Всего ВОДЫ на всё поле требуется: {total_water_for_field:.1f} л")
log(
    f"Всего потребуется полных заправок опрыскивателя ({trunk_quantity} бак(а) по {trunk_volume} л): {trunks_quantity_per_area:.2f} шт."
)
log(f"Одна заправка машины обрабатывает: {square_per_1machine:.2f} га")
log("=" * 50)

# Цикл настройки дозировок
for prep_id in selected_preparations:
    prep_data = culture_data["preparations"][prep_id]
    prep_name = prep_data["name"]
    recommended_rate = prep_data["rate_per_ha"]
    max_safe_percent = prep_data["max_safe_percent"]

    log(f"\n Настройка для препарата: {prep_name}")
    log(f"Рекомендуемая норма в базе данных: {recommended_rate} л/кг на га")

    # Добавлено: Указание своей дозировки
    user_rate_input = input_setting(
        f"Укажите вашу норму расхода (или нажмите Enter для рекомендуемой {recommended_rate}): ",
        allow_empty=True,
    )

    # Определяем итоговую норму расхода
    prep_rate = recommended_rate if user_rate_input is None else user_rate_input
    # Расчеты на основе выбранной дозировки (prep_rate):
    # Норма на площадь, покрываемую ОДНИМ баком
    square_per_1trunk = trunk_volume / water_per_1ga
    preparations_volume_per_trunk = square_per_1trunk * prep_rate

    # Общее количество конкретного препарата на ВСЮ машину (на все баки сразу за одну заправку)
    total_preparations_volume = square_per_1machine * prep_rate

    # Расчет безопасной концентрации в процентах в одном баке
    preparations_in_trunk = (preparations_volume_per_trunk / trunk_volume) * PERCENTS

    log(f"РЕЗУЛЬТАТ РАСЧЕТА:")
    log(
        f"Налить в КАЖДЫЙ бак (по отдельности): {preparations_volume_per_trunk:.3f} л/кг"
    )
    if trunk_quantity > 1:
        log(
            f"Итого на всю заправку (во все {trunk_quantity} бака(ов)): {total_preparations_volume:.3f} л/кг"
        )
    log(f"Фактическая концентрация в растворе: {preparations_in_trunk:.3f}%")

    # Проверка безопасности смеси по лимиту из JSON
    if preparations_in_trunk > max_safe_percent:
        log(
            f"Внимание! Превышен безопасный порог ({max_safe_percent}%)! Ваша дозировка может сжечь растения."
        )
    else:
        log("Дозировка безопасна для растений.")

while True:
    answer = input("\nХотите сохранить результат в файл? (Да/Нет): ").strip().lower()
    if answer in ("да", "д", "yes", "y"):
        file_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"result_{file_date}.txt"

        try:
            with open(file_name, "w", encoding="utf-8") as f:
                f.write("\n".join(output_log))
            print(f"Результат сохранен в файл: {file_name}")
        except OSError as e:
            print(f"Не удалось сохранить файл: {e}")
        break
    elif answer in ("нет", "н", "no", "n"):
        print("Результат не сохранен.")
        break

    else:
        print("Пожалуйста, ответьте 'Да' или 'Нет'.")
