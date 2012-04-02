# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from messages.models import Message

SCORE_CHOICES = {
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
}

"""
def make_upload_path(instance, filename):
    #Generates upload path for FileField
    user = User.objects.get(username=request.user.username)
    return u"uploads/%s/%s" % (user.id, filename)
"""

class Teacher(models.Model):
    user = models.OneToOneField(User)

    middle_name = models.CharField(max_length=30, blank=True)
    position = models.CharField(max_length=30, blank=True)

    sex = models.BooleanField() #true = man

    def __unicode__(self):
        return self.user.get_full_name()

"""
class Secretary(models.Model):
    user = models.OneToOneField(User)
     
    def __unicode__(self):
        return self.user.get_full_name()
"""
    
class Theme(models.Model):
    teacher = models.ForeignKey(Teacher)
    name = models.CharField(max_length=100, unique=True, verbose_name=u'Название')
    comments = models.TextField(blank=True, verbose_name=u'Комментарии') #комментарии для студента для выбора темы

    #исходные данные к работе и консультанты (для документации)
    initial_data = models.TextField(verbose_name=u'Исходные данные (для документации)')
    contents = models.TextField(verbose_name=u'Содержание работы (для документации)')
    consultants = models.TextField(blank=True, verbose_name=u'Консультанты (для документации)')
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class Specialization(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'Специальность')

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class TypeOfWork(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'Тип ВКР')

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]
    
class Student(models.Model):
    # профайл студента
    # diplomnik = true - студент с темой и преподавателем
    user = models.OneToOneField(User)
    
    birthday = models.DateField()
    phone = models.CharField(max_length=20, blank=True)

    middle_name = models.CharField(max_length=30, blank=True)

    sex = models.BooleanField() #true = man

    semestr = models.SmallIntegerField(blank=True)
    specialization = models.ForeignKey(Specialization, null=True, blank=True) #направление

    month = models.CharField(max_length=10, blank=True) #месяц защиты
    year = models.SmallIntegerField(blank=True, null=True) #год защиты
    type_of_work = models.ForeignKey(TypeOfWork, blank=True, null=True) #тип ВКР

    diplomnik = models.BooleanField(default = False)
    theme = models.ForeignKey(Theme, null=True, blank=True)
    
    def __unicode__(self):
        return self.user.get_full_name()

class Interest(models.Model):
    teacher = models.ForeignKey(Teacher)
    name = models.CharField(max_length=100, verbose_name=u'Область интересов')
    
    def __unicode__(self):
        return self.name
    
class Special_message(models.Model):
# специальное сообщение, например запрос на тему преподавателю
# ответ с темой студенту
    message = models.OneToOneField(Message)
    themes = models.ManyToManyField(Theme, null=True, blank=True)
    interests = models.ManyToManyField(Interest, null=True, blank=True)
    """
    MSG_TYPE_CHOICES = (
        ('req', 'Request'),
        ('rep', 'Reply'),
        )
    message_type = models.CharField(max_length=1, choices=MSG_TYPE_CHOICES)
    """
    
class Serie(models.Model):
    """
    Прием id=1. только на него студенты могут самостоятельно записываться
    project.views.event_add
    прием, встреча в чате и т.д.

    также защита, предзащита
    """

    primary_name = models.CharField(max_length=20)
    
    def __unicode__(self):
        return self.primary_name
    
class Event(models.Model):
    series = models.ForeignKey(Serie, verbose_name=u'Вид встречи')
    date_and_time = models.DateTimeField(verbose_name=u'Дата и время начала') #начало
    #date = models.DateField()
    #starttime = models.TimeField()
    endtime = models.TimeField(null=True, blank=True, verbose_name=u'Конец встречи (время)') #конец встречи
    
    teacher = models.ForeignKey(Teacher, null=True, blank=True) #защита/предзащита =null

    #для защиты, предзащиты ...
    specialization = models.ForeignKey(Specialization, blank=True, null=True, verbose_name=u'Направление')

    def __unicode__(self):
        return u'%s. %s' % (self.series.primary_name, self.date_and_time.__str__())

    def get_absolute_url(self):
        return '/event/' + str(self.id)

    class Meta:
        ordering=["date_and_time"]
    
class EventStudent(models.Model):
    event = models.ForeignKey(Event)
    #number = models.SmallIntegerField() # № по порядку
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)

    student = models.ForeignKey(Student, verbose_name=u'Студент')

    def __unicode__(self):
        return u'%s. %s' % (self.event.__unicode__(), self.student.__unicode__())

    class Meta:
        ordering=["date","time"]

class Stage(models.Model):
    # deadlin'ы

    name = models.ForeignKey(Serie)
    student = models.ForeignKey(Student)

    date_and_time = models.DateTimeField(verbose_name=u'Дата и время')

    score = models.SmallIntegerField(null=True, blank=True, max_length=1, choices=SCORE_CHOICES, verbose_name=u'Оценка')

    def __unicode__(self):
        return u'%s. %s' % (self.name.__unicode__(), self.student.__unicode__())

    class Meta:
        ordering=["date_and_time"]

# позже, работа с файлами
"""class Upload(models.Model):
    user = models.ForeignKey(User)
    file = models.FileField(upload_to=make_upload_path)
    category = models.ForeignKey(Category)
    uploaded_date = models.DateTimeField(auto_now_add=True)

class Material(models.Model):
    student = models.ForeignKey(Student)
    name = models.CharField(max_length = 100)
    docfile = models.FileField(upload_to = make_upload_path)
    uploaded_date = models.DateTimeField(auto_now = True)
    
class Project(models.Model):
    student = models.ForeignKey(Student)
    name = models.CharField(max_length = 100)
    prfile = models.FileField(upload_to = make_upload_path)
"""