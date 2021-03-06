from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from .managers import UserManager

TYPES = [
    (0, "Root"),
    (1, "Администратор"),
    (2, "Учитель"),
    (3, "Ученик"),
]


GRADES = [
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
    (7, 7),
    (8, 8),
    (9, 9),
    (10, 10),
    (11, 11)
]

LITERAS = [
    ("А", "А"),
    ("Б", "Б"),
    ("В", "В"),
    ("Г", "Г"),
    ("Д", "Д"),
    ("Е", "Е"),
    ("Ж", "Ж"),
    ("З", "З"),
    ("И", "И"),
    ("К", "К")
]


class Users(AbstractBaseUser, PermissionsMixin):
    """
    Base model for any user: admin, student or teacher.

    Attributes:
        email - email of the user
        account_type - set at registration. Can be equal to
        0 (Superuser), 1 (Admin), 2 (Teacher) and 3 (Student)
    """
    email = models.EmailField('Почта', unique=True)
    account_type = models.IntegerField(
        verbose_name="Тип аккаунта", default=3, choices=TYPES)
    is_active = models.BooleanField('Активный', default=True)
    is_staff = models.BooleanField('Администратор', default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['account_type']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def get_username(self):
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Subjects(models.Model):
    name = models.CharField(
        max_length=50, verbose_name="Название",
        unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"

    def __str__(self):
        return self.name


def teacher_avatar_upload(instanse, filename):
    return 'teachers/{}/{}'.format(instanse.pk, filename)


class Teachers(models.Model):
    account = models.OneToOneField(
        Users, on_delete=models.CASCADE, related_name='teacher',
        verbose_name="Пользователь", primary_key=True)
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    surname = models.CharField(max_length=100, verbose_name="Фамилия")
    avatar = models.FileField(
        verbose_name="Файл", blank=True,
        upload_to=teacher_avatar_upload, default='')
    second_name = models.CharField(
        max_length=100, verbose_name="Отчество",
        blank=True, default='')
    subjects = models.ManyToManyField(Subjects, verbose_name="Предметы")

    class Meta:
        ordering = ['surname', 'first_name', 'second_name']
        verbose_name = "Учитель"
        verbose_name_plural = "Учителя"

    def __str__(self):
        return '{} {} {}'.format(
            self.surname, self.first_name, self.second_name)


class Grades(models.Model):
    """
    Model that represents a grade with students.

    Fields:
        id (PK), number (int), letter (str), teachers (MTM), subjects (MTM),
        main_teacher (FK - Teachers)
    """
    number = models.IntegerField(choices=GRADES, verbose_name="Класс")
    letter = models.CharField(max_length=2, choices=LITERAS, verbose_name="Буква")
    teachers = models.ManyToManyField(
        Teachers, verbose_name="Учителя",
        related_name="grades")
    subjects = models.ManyToManyField(Subjects, verbose_name="Предметы")
    main_teacher = models.OneToOneField(
        Teachers, verbose_name='Классный руководитель',
        on_delete=models.SET_NULL, null=True, default=None, related_name='grade_curated')

    class Meta:
        ordering = ['number', 'letter']
        verbose_name = "Класс"
        verbose_name_plural = "Классы"
        unique_together = ('number', 'letter')

    def __str__(self):
        return '{}{}'.format(self.number, self.letter)


class Students(models.Model):
    """
    Model that represents a User with account_type = 3.

    Fields:
        account (OTO -> User, PK),
        first_name (str),
        surname (str),
        second_name (str),
        grade (FK -> Grades)
    """
    account = models.OneToOneField(
        Users, on_delete=models.CASCADE,
        verbose_name="Пользователь", primary_key=True, related_name='student')
    first_name = models.CharField(verbose_name="Имя", max_length=100)
    surname = models.CharField(verbose_name="Фамилия", max_length=100)
    second_name = models.CharField(verbose_name="Отчество", max_length=100, blank=True, default="")
    grade = models.ForeignKey(
        Grades, on_delete=models.SET_NULL, null=True, default=None,
        verbose_name="Класс", blank=True)

    class Meta:
        ordering = ['grade', 'surname', 'first_name', 'second_name']
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"

    def __str__(self):
        return '{} {} {} {}'.format(self.first_name, self.second_name, self.surname, self.grade)


class Administrators(models.Model):
    account = models.OneToOneField(
        Users, on_delete=models.CASCADE,
        verbose_name="Пользователь", primary_key=True, related_name="admin")
    first_name = models.CharField(verbose_name="Имя", max_length=100)
    surname = models.CharField(verbose_name="Фамилия", max_length=100)
    second_name = models.CharField(verbose_name="Отчество", max_length=100, blank=True, default="")

    class Meta:
        verbose_name = "Администратор"
        verbose_name_plural = "Администраторы"

    def __str__(self):
        return '{} {} {}'.format(self.surname, self.first_name, self.second_name)


class Controls(models.Model):
    name = models.CharField(max_length=120, verbose_name='Вид работы')
    weight = models.FloatField(verbose_name='Коэффицент', default=1)

    class Meta:
        verbose_name = "Вид работы"
        verbose_name_plural = "Виды работ"

    def __str__(self):
        return '{} '.format(self.name)


def lesson_upload(instanse, filename):
    return 'homework/{}/{}'.format(instanse.pk, filename)


class Lessons(models.Model):
    date = models.DateField(verbose_name='Дата')
    quarter = models.SmallIntegerField(verbose_name='Четверть', null=True, default=None)
    homework = models.TextField(blank=True, verbose_name='ДЗ')
    theme = models.CharField(max_length=120, verbose_name='Тема')
    group = models.ForeignKey(
        "Groups", on_delete=models.PROTECT,
        verbose_name="Группа", null=True, default=None
    )
    control = models.ForeignKey(Controls, on_delete=models.PROTECT, verbose_name='Контроль')
    h_file = models.FileField(
        null=True, default=None, blank=True,
        verbose_name="Файл", upload_to=lesson_upload)

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ['date']

    def __str__(self):
        return '{} {}'.format(str(self.group), self.date)


class Marks(models.Model):
    # If student is deleted, delete all his marks
    student = models.ForeignKey("Students", on_delete=models.CASCADE, verbose_name="Ученик")
    amount = models.IntegerField(verbose_name="Балл", null=True, default=None)
    # Delete all marks if lesson is deleted
    lesson = models.ForeignKey("Lessons", on_delete=models.CASCADE, verbose_name='Урок')
    comment = models.TextField(blank=True, verbose_name='комментарий', default="")

    class Meta():
        verbose_name_plural = "Оценки"
        ordering = ['lesson']

    def __str__(self):
        return '"{}" {} {}'.format(self.amount, self.lesson, self.student)


class AdminMessages(models.Model):
    date = models.DateTimeField(verbose_name="Время отправки", auto_now_add=True)
    subject = models.CharField(verbose_name="Тема сообщения", max_length=100)
    content = models.TextField(verbose_name="Текст сообщения", max_length=4000)
    sender = models.ForeignKey(
        Users, on_delete=models.CASCADE, verbose_name="Отправитель", null=True, default=None)

    class Meta:
        verbose_name = "Сообщение администратору"
        verbose_name_plural = "Сообщения администратору"
        ordering = ['date', 'subject']

    def __str__(self):
        return self.subject


class Quarters(models.Model):
    number = models.IntegerField(verbose_name="Четверть", choices=(
        (1, "I"), (2, "II"), (3, "III"), (4, "IV")
    ), unique=True)
    begin = models.DateField(verbose_name="Начало четверти")
    end = models.DateField(verbose_name="Конец четверти")

    class Meta:
        verbose_name = "Четверть"
        verbose_name_plural = "Четверти"
        ordering = ['number']

    def __str__(self):
        return "Четверть #{}".format(self.number)

# TODO: When new student is added to grade, add him to group's students


class Groups(models.Model):
    """
    Class that combines grades and subjects.
    """
    grade = models.ForeignKey(
        "Grades", on_delete=models.CASCADE, verbose_name="Класс")
    subject = models.ForeignKey(
        "Subjects", on_delete=models.PROTECT, verbose_name="Предмет")
    students = models.ManyToManyField(
        "Students", verbose_name="Отображаемые ученики")

    def set_default_students(self):
        qs = self.grade.students_set.all()
        self.students.set(qs)

    def __str__(self):
        return "{} - {}".format(self.grade, self.subject)

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"
        unique_together = ("grade", "subject")
