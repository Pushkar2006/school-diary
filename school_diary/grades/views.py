from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import diary.models as models
from . import forms
from diary.decorators import teacher_only
from diary import functions
from django.http import HttpResponseForbidden


@login_required(login_url="login")
@teacher_only
def add_student(request, i):
    """
    Function defining the process of adding new student to a grade and confirming it.
    """
    me = request.user.teacher
    if not hasattr(me, 'grade_curated') or me.grade_curated is None:
        return render(request, 'grades/no_grade.html')
    s = models.Students.objects.get(account__email=i)
    if s.grade is None:
        if request.method == "POST":
            grade = me.grade_curated
            s.grade = grade
            # Adding new student to every group in this class.
            groups = models.Groups.objects.filter(grade=grade)
            for group in groups:
                group.students.add(s)
            s.save()
            return redirect('my_grade')
        return render(request, 'grades/add_student.html', {'s': s})
    context = {
        'message': "Вы пытаетесь добавить к себе в класс ученика, который уже состоит в классе."
    }
    return render(request, 'access_denied.html', context)


@login_required(login_url="login")
@teacher_only
def create_grade_page(request):
    if request.method == "POST":
        form = forms.GradeCreationForm(request.POST)
        if form.is_valid():
            grade = form.save()
            mt = models.Teachers.objects.get(account=request.user)
            grade.main_teacher = mt
            grade.save()
            return redirect('my_grade')
        context = {'form': form}
        return render(request, 'grades/add_grade.html', context)
    form = forms.GradeCreationForm()
    context = {'form': form}
    return render(request, 'grades/add_grade.html', context)


@login_required(login_url="login")
@teacher_only
def my_grade(request):
    """
    Page with information about teacher's grade.
    """
    me = request.user.teacher
    if not hasattr(me, 'grade_curated') or me.grade_curated is None:
        return render(request, 'grades/no_grade.html')
    grade = me.grade_curated
    students = grade.students_set.all()
    context = {
        'grade': grade,
        'students': students,
    }
    if "search" in request.GET:
        email = request.GET.get('email')
        fn = request.GET.get('first_name')
        s = request.GET.get('surname')
        if fn or s or email:
            search = models.Students.objects.filter(
                first_name__icontains=fn, surname__icontains=s,
                account__email__icontains=email)
        else:
            search = []
        context['search'] = search

    return render(request, 'grades/my_grade.html', context)


def students_marks(request, student_id):
    teacher = request.user.teacher
    if not hasattr(teacher, 'grade_curated') or teacher.grade_curated is None:
        return render(request, 'grades/no_grade.html')
    student = get_object_or_404(models.Students, pk=student_id)
    if student.grade != teacher.grade_curated:
        return render(request, 'access_denied.html', {
            'message': 'Вы не можете просматривать оценки учеников из другого класса.'
        })
    term = request.GET.get('quarter')
    if term is None:
        current = functions.get_current_quarter()
        term = current if current != 0 else 1
    term = int(term)
    groups = models.Groups.objects.filter(grade=student.grade, students=student)
    all_marks = student.marks_set.filter(lesson__quarter=term)
    if not all_marks:
        return render(request, 'grades/marks.html', {'no_marks': True, 'term': term})

    d = {}
    max_length, total_missed = 0, 0
    for group in groups:
        marks = all_marks.filter(lesson__group=group).order_by("lesson__date")
        if len(marks) > max_length:
            max_length = len(marks)
        data = functions.get_marks_data(marks)
        d[group] = [data[1], data[0], marks]
        total_missed += data[5]

    for group in d:
        d[group].append(range(max_length - len(d[group][2])))

    context = {
        'student': student,
        'd': d,
        'max_length': max_length,
        'total_missed': total_missed,
        'term': term,
    }
    return render(request, 'grades/marks.html', context)


@login_required(login_url="login")
@teacher_only
def delete_student(request, pk: int):
    """
    Function defining the process of deleting a student from a grade and confirming it.

    Args:
        pk - primary key of student to be deleted.
    """
    me = request.user.teacher
    if not hasattr(me, 'grade_curated') or me.grade_curated is None:
        return render(request, 'grades/no_grade.html')
    student = models.Users.objects.get(pk=pk).student
    if student.grade != me.grade_curated:
        return HttpResponseForbidden("Вы пытаетесь удалить ученика из другого класса.")
    if request.method == "POST":
        student.grade = None
        # Prevent this student from displaying in the grade.
        groups = models.Groups.objects.filter(grade=me.grade_curated)
        for group in groups:
            group.students.remove(student)
        student.save()
        return redirect('my_grade')
    return render(request, 'grades/delete_student.html', {'s': student})


@login_required(login_url="login")
@teacher_only
def settings(request):
    me = request.user.teacher
    if not hasattr(me, 'grade_curated') or me.grade_curated is None:
        return render(request, 'grades/no_grade.html')
    if request.method == "POST":
        form = forms.ClassSettingsForm(request.POST, instance=me.grade_curated)
        if form.is_valid():
            form.save()
            return redirect('my_grade')
    form = forms.ClassSettingsForm(instance=me.grade_curated)
    return render(request, 'grades/settings.html', {'form': form})
