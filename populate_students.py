import random
from django.contrib.auth.models import User
from accounts.models import Department, AcademicGroup, Course, StudentProfile

# 1. Список 237 группы (20 человек)
students_237 = [
    "Бударин Роман Игоревич",
    "Говорухин Даниил Андреевич",
    "Домашнев Игорь Дмитриевич",
    "Каверина Дарья Сергеевна",
    "Калиниченко Владимир Константинович",
    "Каширская Вероника Александровна",
    "Кочугуров Иван Игоревич",
    "Куликов Егор Вячеславович",
    "Лопандин Тимур Константинович",
    "Львова Арина Андреевна",
    "Малофеева Мария Дмитриевна",
    "Марченко Вероника Владимировна",
    "Мигда Данил Кириллович",
    "Новиков Данила Андреевич",
    "Павлинов Даниил Алексеевич",
    "Приходько Кира Сергеевна",
    "Филяков Иван Александрович",
    "Чекмарева Варвара Сергеевна",
    "Шафиев Марсель Ренатович",
    "Эренценов Санджи Мингиянович",
]

# 2. Список 234 группы (25 человек)
students_234 = [
    "Баранов Данила Витальевич",
    "Борисов Матвей Алексеевич",
    "Васильев Михаил Андреевич",
    "Вахаев Ибрагим Азаматович",
    "Галяутдинов Данис Радикович",
    "Зеньков Вячеслав Олегович",
    "Калиниченко Ирина Борисовна",
    "Карабунарлы Алёна Игоревна",
    "Кислая Дарья Владимировна",
    "Кияница Екатерина Николаевна",
    "Кулик Артём Игоревич",
    "Лазарев Михаил Юрьевич",
    "Марков Степан Дмитриевич",
    "Медведева Азалия Ильдаровна",
    "Молоканова Анастасия Александровна",
    "Олухов Максим Иванович",
    "Пантелеева Полина Сергеевна",
    "Пасько Артём Игоревич",
    "Сажин Иван Петрович",
    "Санникова Екатерина Сергеевна",
    "Сдобников Александр Сергеевич",
    "Стороженко Борис Денисович",
    "Тихонова Алина Александровна",
    "Чепиков Тимофей Романович",
    "Шихобалов Илья Глебович",
]

translit_dict = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "e",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
}


def to_translit(text):
    res = []
    for char in text.lower():
        res.append(translit_dict.get(char, char))
    return "".join(res)


# Настраиваем факультеты
dept_it, _ = Department.objects.get_or_create(name="Информационные технологии")
dept_pm, _ = Department.objects.get_or_create(name="Прикладная математика")

# Создаем / обновляем академические группы
group_237, _ = AcademicGroup.objects.get_or_create(
    name="М3О-237БВ-25", defaults={"department": dept_it}
)
group_237.department = dept_it
group_237.save()

group_234, _ = AcademicGroup.objects.get_or_create(
    name="М3О-234БВ-25", defaults={"department": dept_pm}
)
group_234.department = dept_pm
group_234.save()

available_courses = list(Course.objects.all())


def add_students_to_group(students_list, target_group):
    count = 0
    for fio in students_list:
        parts = fio.split()
        last_name = parts[0]
        first_name = parts[1] if len(parts) > 1 else ""

        username_base = f"{to_translit(last_name)}_{to_translit(first_name)[:1]}"
        username = username_base
        idx = 1
        while (
            User.objects.filter(username=username)
            .exclude(last_name=last_name, first_name=first_name)
            .exists()
        ):
            username = f"{username_base}{idx}"
            idx += 1

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "email": f"{username}@edu.mai.ru",
            },
        )
        if created:
            user.set_password("maiStudent2026!")
            user.save()

        profile, _ = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                "department": target_group.department,
                "academic_group": target_group,
            },
        )
        profile.department = target_group.department
        profile.academic_group = target_group
        profile.save()

        if available_courses:
            assigned = random.sample(
                available_courses, min(len(available_courses), random.randint(2, 4))
            )
            profile.courses.set(assigned)

        count += 1
    return count


total_237 = add_students_to_group(students_237, group_237)
total_234 = add_students_to_group(students_234, group_234)

print(f"Добавлено студентов в М3О-237БВ-25: {total_237}")
print(f"Добавлено студентов в М3О-234БВ-25: {total_234}")
print(f"Всего обработано: {total_237 + total_234}")
