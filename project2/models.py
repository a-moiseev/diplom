# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from messages.models import Message

from bbb.models import Meeting

class GitHubAccount(models.Model):
    username = models.CharField(max_length=30, blank=True, verbose_name="Логин")
    password = models.CharField(max_length=30, blank=True, verbose_name="Пароль")
    #token = models.CharField(max_length=30, blank=True, verbose_name="Token")
    reponame = models.CharField(max_length=30, blank=True, verbose_name="Имя Репозитория")

    def __unicode__(self):
        return self.username

class Teacher(models.Model):
    user = models.OneToOneField(User)
    github = models.OneToOneField(GitHubAccount, null=True, blank=True)

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
    #комментарии для студента для выбора темы
    comments = models.TextField(blank=True, verbose_name=u'Комментарии')

    #исходные данные к работе и консультанты (для документации)
    initial_data = models.TextField(verbose_name=u'Исходные данные (для документации)')
    contents = models.TextField(verbose_name=u'Содержание работы (для документации)')
    consultants = models.TextField(blank=True, verbose_name=u'Консультанты (для документации)')
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class Specialization(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'Направление')

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
    github = models.OneToOneField(GitHubAccount, null=True, blank=True)
    
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
    
class Serie(models.Model):
    """
    Прием id=1. только на него студенты могут самостоятельно записываться
    project.views.event_add
    прием, встреча в чате и т.д.

    videoconf id=3!!!!!!

    """

    primary_name = models.CharField(max_length=20)
    
    def __unicode__(self):
        return self.primary_name

#class EventConf(models.Model):
#    name = models.CharField(max_length=50)
#    attendee_password = models.CharField(max_length=50, null=True, blank=True)
#    moderator_password = models.CharField(max_length=50, null=True, blank=True)
    
class Event(models.Model):
    series = models.ForeignKey(Serie, verbose_name=u'Вид встречи')
    date_and_time = models.DateTimeField(verbose_name=u'Дата и время начала') #начало
    #date = models.DateField()
    #starttime = models.TimeField()
    endtime = models.TimeField(null=True,
        blank=True,
        verbose_name=u'Конец встречи (время)') #конец встречи
    
    teacher = models.ForeignKey(Teacher, null=True, blank=True) #защита/предзащита =null

    meeting = models.ForeignKey(Meeting, null=True, blank=True)

    #для защиты, предзащиты ...
    specialization = models.ForeignKey(Specialization,
        blank=True,
        null=True,
        verbose_name=u'Направление')

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

class StageName(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering=["name"]

class Stage(models.Model):
    # deadlin'ы
    name = models.ForeignKey(StageName, verbose_name=u'Этап')
    date = models.DateTimeField(verbose_name=u'Дата')

    specialization = models.ForeignKey(Specialization,
        blank=True,
        null=True,
        verbose_name=u'Направление')

    def __unicode__(self):
        return u'%s. %s' % (self.name.__unicode__(), self.date.strftime('%d.%m.%Y'))

    class Meta:
        ordering=["date"]

class StagePass(models.Model):
    stage = models.ForeignKey(Stage)
    student = models.ForeignKey(Student)

    stage_pass = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s. %s' % (self.student.__unicode__(), self.stage.__unicode__())
