from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Department, AcademicGroup, Course
from .forms import DepartmentForm, AcademicGroupForm, CourseForm


def is_methodist(user):
    return user.is_authenticated and (
        user.groups.filter(name="Методист").exists() or user.is_superuser
    )


@login_required
def profile(request):
    return render(request, "profile.html", {"is_methodist": is_methodist(request.user)})


# --- ФАКУЛЬТЕТЫ ---
@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(
        request,
        "department_list.html",
        {
            "departments": departments,
            "is_methodist": is_methodist(request.user),
        },
    )


@login_required
@user_passes_test(is_methodist)
def department_create(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("department_list")
    else:
        form = DepartmentForm()
    return render(
        request, "object_form.html", {"form": form, "title": "Добавление факультета"}
    )


@login_required
@user_passes_test(is_methodist)
def department_update(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == "POST":
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect("department_list")
    else:
        form = DepartmentForm(instance=department)
    return render(
        request, "object_form.html", {"form": form, "title": "Изменение факультета"}
    )


@login_required
@user_passes_test(is_methodist)
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == "POST":
        department.delete()
        return redirect("department_list")
    return render(
        request,
        "object_confirm_delete.html",
        {"object": department, "title": "Удаление факультета"},
    )


# --- УЧЕБНЫЕ ГРУППЫ ---
@login_required
def academic_group_list(request):
    groups = AcademicGroup.objects.all()
    return render(
        request,
        "group_list.html",
        {
            "groups": groups,
            "is_methodist": is_methodist(request.user),
        },
    )


@login_required
@user_passes_test(is_methodist)
def academic_group_create(request):
    if request.method == "POST":
        form = AcademicGroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("academic_group_list")
    else:
        form = AcademicGroupForm()
    return render(
        request,
        "object_form.html",
        {"form": form, "title": "Добавление учебной группы"},
    )


@login_required
@user_passes_test(is_methodist)
def academic_group_update(request, pk):
    group = get_object_or_404(AcademicGroup, pk=pk)
    if request.method == "POST":
        form = AcademicGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect("academic_group_list")
    else:
        form = AcademicGroupForm(instance=group)
    return render(
        request, "object_form.html", {"form": form, "title": "Изменение учебной группы"}
    )


@login_required
@user_passes_test(is_methodist)
def academic_group_delete(request, pk):
    group = get_object_or_404(AcademicGroup, pk=pk)
    if request.method == "POST":
        group.delete()
        return redirect("academic_group_list")
    return render(
        request,
        "object_confirm_delete.html",
        {"object": group, "title": "Удаление учебной группы"},
    )


# --- КУРСЫ ---
@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(
        request,
        "course_list.html",
        {
            "courses": courses,
            "is_methodist": is_methodist(request.user),
        },
    )


@login_required
@user_passes_test(is_methodist)
def course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("course_list")
    else:
        form = CourseForm()
    return render(
        request, "object_form.html", {"form": form, "title": "Добавление курса"}
    )


@login_required
@user_passes_test(is_methodist)
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect("course_list")
    else:
        form = CourseForm(instance=course)
    return render(
        request, "object_form.html", {"form": form, "title": "Изменение курса"}
    )


@login_required
@user_passes_test(is_methodist)
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        course.delete()
        return redirect("course_list")
    return render(
        request,
        "object_confirm_delete.html",
        {"object": course, "title": "Удаление курса"},
    )


import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from .models import Department, AcademicGroup, Course, StudentProfile


@login_required
def dashboard_view(request):
    total_students = StudentProfile.objects.count()
    total_courses = Course.objects.count()
    total_departments = Department.objects.count()
    total_groups = AcademicGroup.objects.count()

    dept_filter = request.GET.get("department")

    courses_qs = Course.objects.all()
    groups_qs = AcademicGroup.objects.all()

    if dept_filter and dept_filter.isdigit():
        courses_qs = courses_qs.filter(department_id=dept_filter)
        groups_qs = groups_qs.filter(department_id=dept_filter)

    # 1. Популярность курсов (по числу студентов)
    courses_stats = courses_qs.annotate(students_count=Count("students")).order_by(
        "-students_count"
    )[:6]
    course_labels = [c.title for c in courses_stats]
    course_data = [c.students_count for c in courses_stats]

    # 2. Распределение по группам
    groups_stats = groups_qs.annotate(students_count=Count("students"))
    group_labels = [g.name for g in groups_stats]
    group_data = [g.students_count for g in groups_stats]

    # 3. Распределение студентов по факультетам (исправлено поле students)
    dept_stats = Department.objects.annotate(students_count=Count("students"))
    dept_labels = [d.name for d in dept_stats]
    dept_percentages = [
        (
            min(100, int((d.students_count / total_students * 100)))
            if total_students > 0
            else 0
        )
        for d in dept_stats
    ]

    # 4. Динамика регистраций учетных записей
    users = User.objects.order_by("date_joined")
    user_timeline_labels = [u.date_joined.strftime("%d.%m") for u in users]
    user_timeline_data = list(range(1, len(user_timeline_labels) + 1))

    context = {
        "total_students": total_students,
        "total_courses": total_courses,
        "total_departments": total_departments,
        "total_groups": total_groups,
        "all_departments": Department.objects.all(),
        "selected_department": (
            int(dept_filter) if (dept_filter and dept_filter.isdigit()) else ""
        ),
        "chart_course_labels": json.dumps(course_labels),
        "chart_course_data": json.dumps(course_data),
        "chart_group_labels": json.dumps(group_labels),
        "chart_group_data": json.dumps(group_data),
        "chart_dept_labels": json.dumps(dept_labels),
        "chart_dept_percentages": json.dumps(dept_percentages),
        "chart_user_labels": json.dumps(user_timeline_labels),
        "chart_user_data": json.dumps(user_timeline_data),
    }
    return render(request, "dashboard.html", context)


@login_required
def student_list_view(request):
    group_filter = request.GET.get("group")
    students = StudentProfile.objects.select_related(
        "user", "academic_group", "department"
    ).prefetch_related("courses")

    if group_filter:
        students = students.filter(academic_group__name=group_filter)

    groups = AcademicGroup.objects.all()
    return render(
        request,
        "student_list.html",
        {
            "students": students,
            "groups": groups,
            "selected_group": group_filter or "",
        },
    )
