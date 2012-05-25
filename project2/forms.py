# -*- coding: utf-8 -*-

from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.forms import ModelForm

from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget, AdminSplitDateTime

from diplom.project2.models import *

import datetime

from pygithub3 import Github

def birthyears():
    now = (datetime.datetime.now()).year
    years = range(now-15,now-75,-1)
    return years

def year_choises():
    now = (datetime.datetime.now()).year
    return {
        (now, now),
        (now+1, now+1),
        (now+2, now+2),
    }

class StudentProfileForm(forms.Form):
    last_name = forms.CharField(widget=forms.TextInput, max_length=30, label=u'Фамилия')
    first_name = forms.CharField(widget=forms.TextInput, max_length=30, label=u'Имя')
    middle_name = forms.CharField(widget=forms.TextInput, max_length=30, label=u'Отчество')
    birthday = forms.DateField(widget=SelectDateWidget(years=birthyears()), label=u'Дата рождения')
    SEX_CHOICES = {
        (True, 'Мужской'),
        (False, 'Женский'),
    }
    sex = forms.ChoiceField(choices=SEX_CHOICES, label=u'Пол')
    SEMESTR_CHOICES = {
        (5, '5'),
        (6, '6'),
    }
    semestr = forms.ChoiceField(choices = SEMESTR_CHOICES, label=u'Семестр')
    specialization = forms.ModelChoiceField(queryset = Specialization.objects.all(),
        label=u'Специализация (направление)')

    phone = forms.RegexField(regex=r'[\d\(\)\-\+]', widget=forms.TextInput,
        required=False,
        max_length=20,
        label=u'Телефон')

class StudentYearMonthForm(forms.Form):
    MONTH_CHOICES = (
        (u'январь', u'январь'),
        (u'июнь', u'июнь'),
        )
    month = forms.ChoiceField(choices=MONTH_CHOICES, label=u'Месяц защиты')
    year = forms.ChoiceField(choices = year_choises(), label=u'Год защиты')
    type = forms.ModelChoiceField(queryset = TypeOfWork.objects.all(), label=u'Тип ВКР')

class StudentRequestForm(forms.Form):
    def __init__(self, interests_data, theme_data, *args, **kwargs):
        super(StudentRequestForm, self).__init__(*args, **kwargs)
        for i in interests_data:
            label = i.name
            self.fields['int_%s' % i.id] = forms.BooleanField(label=label, required=False)
        for t in theme_data:
            label = t.name
            help_text = t.id
            self.fields['the_%s' % t.id] = forms.BooleanField(label=label,
                help_text = help_text,
                required=False)
            
class StudentSpecialMessageForm(forms.Form):
    comments = forms.CharField(widget=forms.Textarea(attrs={'cols': 70, 'rows': 20}),
        label=u'Текст сообщения', required=False)


class ReplySpecialMessageForm(forms.Form):
    theme = forms.ModelChoiceField(queryset = Theme.objects.none, label=u'Тема')
    comments = forms.CharField(widget=forms.Textarea(attrs={'cols': 70, 'rows': 20}),
        label=u'Текст сообщения', required=False)

    def __init__(self, theme_data, *args, **kwargs):
        super(ReplySpecialMessageForm, self).__init__(*args, **kwargs)
        self.fields['theme'].queryset = theme_data

class ThemeForm(ModelForm):
    class Meta:
        model = Theme
        fields = ('name', 'comments', 'initial_data', 'contents', 'consultants')
        widgets = {
            'name': forms.TextInput(attrs={'size':'60'}),
            'comments': forms.Textarea(attrs={'cols': 70, 'rows': 15}),
            'initial_data': forms.TextInput(attrs={'size':'60'}),
            'contents': forms.Textarea(attrs={'cols': 70, 'rows': 15}),
            'consultants': forms.TextInput(attrs={'size':'60'}),
        }
        
class InterestForm(ModelForm):
    class Meta:
        model = Interest
        fields = ('name',)
        widgets = {'name': forms.TextInput(attrs={'size':'60'}),}
        
class EventAddForm(ModelForm):
    class Meta:
        model = Event
        fields = ('series', 'date_and_time', 'endtime')
        widgets = {
            'series': forms.Select(),
            #'date_and_time': forms.SplitDateTimeWidget(),
            'date_and_time': AdminSplitDateTime(),
            'endtime': AdminTimeWidget(),
        }

class SuperEventAddForm(ModelForm):
    class Meta:
        model = Event
        exclude = ('teacher',)
        widgets = {
            'series': forms.Select(),
            'date_and_time': forms.SplitDateTimeWidget()
        }

class EventAddStudentForm(ModelForm):
    class Meta:
        model=EventStudent
        #exclude = ('event', 'number')
        fields = ('student',)
        widgets = {'student': forms.Select()}

class EventAddStudentsForm(forms.Form):
    students = forms.ModelMultipleChoiceField(queryset=Student.objects.all(),
        widget=forms.SelectMultiple,
        label=u'Студенты:', required=True)

"""
class ScoreForm(ModelForm):
    class Meta:
        model=Stage
        #exclude = ('event', 'number')
        fields = ('score',)
        widgets = {'score': forms.Select()}
"""

class GitHubAccountForm(ModelForm):
    class Meta:
        model = GitHubAccount
        fields = ('username','password',)
        widgets = {'password': forms.PasswordInput()}

class GitHubPasswordForm(ModelForm):
    class Meta:
        model = GitHubAccount
        fields = ('password',)
        widgets = {'password': forms.PasswordInput()}

class DiplomaName(forms.Form):
    name = forms.RegexField(regex=r'^[\w]+$', max_length=100,
        label='Имя репозитория',
        error_message='Можете использовать латинские символы, цифры и символ подчеркивания')

class MyModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return u'%s <%s>' % (obj.username, obj.get_full_name())

class NewComposeForm(forms.Form):
    recipient = MyModelMultipleChoiceField(queryset=User.objects.all(),
        widget=forms.SelectMultiple(),
        label=(u"Получатели"))

class StageAdd(ModelForm):
    class Meta:
        model = Stage
        fields = ('name', 'date', 'specialization')
        widgets = {
            'name': forms.Select(),
            'date': AdminDateWidget(),
            'specialization': forms.Select(),
            }