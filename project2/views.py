# -*- coding: utf-8 -*-

import datetime
import calendar as pycalendar
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context, Template
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import login_required

from pymorphy.django_conf import default_morph as morph
from pymorphy.contrib import lastnames_ru

from project2.models import *
from project2.forms import *

import webodt
from webodt import shortcuts

from pygithub3 import Github

from settings import TIME_FOR_ST, DECANAT_EMAIL


def get_us_profile(us):
# принимает объект user, возвращает teacher, student или None
    try:
        return Student.objects.get(user = us)
    except:
        try:
            return Teacher.objects.get(user = us)
        except:
            try:
                return Secretary.objects.get(user = us)
            except:
                return None

def user_student(us):
# принимает объект user, возвращает студент или None 
    try:
        return Student.objects.get(user = us)
    except:
        return None

def main(request):
    return HttpResponseRedirect(reverse('diplom.project2.views.get_profile'))

@login_required    
def get_profile(request, user_id = None):
    if user_id:
        try:
            user = User.objects.get(id = user_id)
        except User.DoesNotExist:
            raise Http404
        prof = get_us_profile(user)
    else:
        user = User.objects.get(username = request.user.username)
        prof = get_us_profile(user)
    
        if not prof:
            # если нет профайла
            if request.method == "POST":
                f = StudentProfileForm(request.POST)
                if not f.is_valid():
                    return render_to_response('registration/create_student_profile.html', {'form':f},
                              context_instance=RequestContext(request))
                else:
                    user.first_name = f.cleaned_data["first_name"]
                    user.last_name = f.cleaned_data["last_name"]
                    user.save()
                    
                    student=Student()
                    student.user = user
                    student.birthday = f.cleaned_data["birthday"]
                    student.phone = f.cleaned_data["phone"]
                    student.middle_name = f.cleaned_data["middle_name"]
                    student.semestr = f.cleaned_data["semestr"]
                    student.specialization = f.cleaned_data["specialization"]
                    #student.month = f.cleaned_data["month"]
                    #student.year = f.cleaned_data["year"]

                    student.save()
                    
                    prof = get_us_profile(user)
                    
                    return render_to_response('registration/profile.html', {'prof':prof},
                                              context_instance=RequestContext(request))
                
            f = StudentProfileForm()
            return render_to_response('registration/create_student_profile.html', {'form':f},
                              context_instance=RequestContext(request))
    
    return render_to_response('registration/profile.html', {'prof':prof}, context_instance=RequestContext(request))

@login_required    
def theme_add(request):
    user = User.objects.get(username = request.user.username)
  
    try:
        prof = Teacher.objects.get(user = user)
    except:
        raise Http404
    
    if request.method == "POST":
        teacher = Theme(teacher = prof)
        f = ThemeForm(request.POST, instance=teacher)
        if not f.is_valid():
            return render_to_response('theme_add.html', {'form':f}, context_instance=RequestContext(request))
        else:
            f.save()
            return HttpResponseRedirect(reverse('diplom.project2.views.get_profile'))
    
    f = ThemeForm()
    return render_to_response('theme_add.html', {'form':f}, context_instance=RequestContext(request))

@login_required    
def theme_edit(request, theme_id):
    user = User.objects.get(username = request.user.username)
    
    try:
        theme = Theme.objects.get(id=theme_id)
        prof = Teacher.objects.get(user = user)
    except:
        raise Http404
    
    if prof != theme.teacher:
        raise Http404
    
    if request.method == "POST":
        f = ThemeForm(request.POST, instance=theme)
        if not f.is_valid():
            return render_to_response('theme_add.html', {'form':f}, context_instance=RequestContext(request))
        else:
            f.save()
            return HttpResponseRedirect(reverse('diplom.project2.views.get_profile'))
       
    f = ThemeForm(instance = theme)
    return render_to_response('theme_add.html', {'form':f}, context_instance=RequestContext(request))

@login_required    
def theme_view(request, theme_id):
    try:
        theme = Theme.objects.get(id = theme_id)
    except:
        raise Http404
    
    return render_to_response('theme_view.html', {'theme':theme}, context_instance=RequestContext(request))

@login_required    
def interest_add(request):
    user = User.objects.get(username = request.user.username)
  
    try:
        prof = Teacher.objects.get(user = user)
    except:
        raise Http404
    
    if request.method == "POST":
        teacher = Interest(teacher = prof)
        f = InterestForm(request.POST, instance = teacher)
        if not f.is_valid():
            return render_to_response('interest_add.html', {'form':f}, context_instance=RequestContext(request))
        else:
            f.save()
            return HttpResponseRedirect(reverse('diplom.project2.views.get_profile'))
    
    f = InterestForm()
    return render_to_response('interest_add.html', {'form':f}, context_instance=RequestContext(request))

@login_required    
def teachers(request):
#выбор студентом темы и/или интересов
    user = User.objects.get(username = request.user.username)
    
#только студент
    try:
        prof = Student.objects.get(user = user)
        if prof.diplomnik:
            raise Http404
    except:
        raise Http404

    teachers = Teacher.objects.all()

    teacher_forms = []
    
    for teacher in teachers:
        one_teacher = {'teacher':teacher, 'form':None}
        interests = Interest.objects.filter(teacher = teacher)
        themes = []
        for t in Theme.objects.filter(teacher = teacher):
            if not t.student_set.count():
                themes.append(t)
        form = StudentRequestForm(interests_data = interests, theme_data = themes)
        one_teacher['form'] = form
        
        teacher_forms.append(one_teacher)
    
    return render_to_response('teachers.html', {'teacher_forms':teacher_forms},
                              context_instance=RequestContext(request))

@login_required    
def teachers_request(request, user_id):
#отправка запроса тичеру
    try:
        teacher = Teacher.objects.get(user = User.objects.get(id=user_id))
    except:
        raise Http404
    
    user = User.objects.get(username = request.user.username)
    
#только студент
    try:
        prof = Student.objects.get(user = user)
        if prof.diplomnik:
            raise Http404
    except:
        raise Http404
    
    interests = Interest.objects.filter(teacher = teacher)
    #themes = Theme.objects.filter(teacher = teacher)
    themes = []
    for t in Theme.objects.filter(teacher = teacher):
        if not t.student_set.count():
            themes.append(t)
    form = StudentRequestForm(data=request.POST, interests_data = interests, theme_data = themes)
    
    interests_req = []
    themes_req = []
    for k in form.data.keys():
        if k[:4] == 'int_':
            interests_req.append(Interest.objects.get(id = str(k[4:])))
        elif k[:4] == 'the_':
            themes_req.append(Theme.objects.get(id = str(k[4:])))

    
    if interests_req.__len__() == 0 and themes_req.__len__() == 0:
        return HttpResponseRedirect(reverse('diplom.project2.views.teachers'))
    
    request.session['interests_req'] = interests_req
    request.session['themes_req'] = themes_req
    
    form2 = StudentSpecialMessageForm()
    
    return render_to_response('teachers_test.html',
                              {'teacher':teacher, 'interests_req':interests_req,
                               'themes_req':themes_req, 'form2':form2},
                              context_instance=RequestContext(request))

@login_required    
def teachers_send_request(request, user_id):
#отправка запроса тичеру
    try:
        teacher = Teacher.objects.get(user = User.objects.get(id=user_id))
    except:
        raise Http404
    
    user = User.objects.get(username = request.user.username)
    
#только студент
    try:
        prof = Student.objects.get(user = user)
        if prof.diplomnik:
            raise Http404
    except:
        raise Http404
      
    if request.method == "POST":
        interests = request.session['interests_req']
        themes = request.session['themes_req']
        
        del request.session['interests_req']
        del request.session['themes_req']
        
        if (not themes) and (not interests):
            return HttpResponseRedirect(reverse('diplom.project2.views.teachers'))
        
        form2 = StudentSpecialMessageForm(request.POST)
        
        if form2.is_valid():
            body = form2.cleaned_data['comments']
            if not body:
                body = ' '
                
            msg = Message(subject = u'Запрос', recipient = teacher.user, sender = user, body = body)
    
            msg.save()  
            
            spec_msg = Special_message()
            spec_msg.message = msg
            spec_msg.save()

            spec_msg.interests = interests
            spec_msg.themes = themes

            spec_msg.save()
            
            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/teachers/request/%s/' % user_id)
    else:
        return HttpResponseRedirect(reverse('diplom.project2.views.teachers'))
        
@login_required 
def specmsg_view(request, message_id):
    """
    доработанный message.view
    
    Shows a single message.``message_id`` argument is required.
    The user is only allowed to see the message, if he is either 
    the sender or the recipient. If the user is not allowed a 404
    is raised. 
    If the user is the recipient and the message is unread 
    ``read_at`` is set to the current datetime.
    """
    user = request.user
    now = datetime.datetime.now()
    message = get_object_or_404(Message, id=message_id)
    
    if (message.sender != user) and (message.recipient != user):
        raise Http404
    if message.read_at is None and message.recipient == user:
        message.read_at = now
        message.save()

    special = message.special_message
    
    student = user_student(user)
    if student and (message.recipient == user):
        theme = special.themes.all()[0]
        return render_to_response('messages/view_spec_stu.html', {
        'message': message,
        'theme': theme,
        }, context_instance=RequestContext(request))

    return render_to_response('messages/view_spec.html', {
        'message': message,
        'special': special,
    }, context_instance=RequestContext(request))

@login_required 
def specmsg_reply(request, message_id, template_name='messages/reply_spec.html'):
    """
    доработанный message.view
    
    Shows a single message.``message_id`` argument is required.
    The user is only allowed to see the message, if he is either 
    the sender or the recipient. If the user is not allowed a 404
    is raised. 
    If the user is the recipient and the message is unread 
    ``read_at`` is set to the current datetime.
    """
    user = request.user
    teacher = get_object_or_404(Teacher, user=user)
    now = datetime.datetime.now()
    parent = get_object_or_404(Message, id=message_id)
    
    if parent.recipient != user:
        raise Http404

    special = parent.special_message

    if special.themes:
        theme_data = special.themes
    else:
        theme_data = Theme.objects.filter(teacher = teacher)

    if request.method == "POST":
        form = ReplySpecialMessageForm(data=request.POST, theme_data=theme_data)
        if form.is_valid():
            body = form.cleaned_data['comments']
            if not body:
                body = ' '
            theme = form.cleaned_data['theme']
                
            msg = Message(subject = u'Тема', recipient = parent.sender, sender = user, body = body)
    
            msg.save()  
            
            spec_msg = Special_message()
            spec_msg.message = msg
            spec_msg.save()
            
            spec_msg.themes.add(theme)
            spec_msg.save()
            
            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/messages/')
            #return render_to_response(template_name, {
            #    'form': form,
            #    }, context_instance=RequestContext(request))
    else:
        form = ReplySpecialMessageForm(theme_data=theme_data)

    return render_to_response(template_name, {
        'form': form,
    }, context_instance=RequestContext(request))

@login_required 
def specmsg_choose(request, message_id):
#выбор темы студент становится дипломник
    user = request.user
    message = get_object_or_404(Message, id=message_id)
    student = user_student(user)
    if student and (message.recipient == user):
        special = message.special_message
        theme = special.themes.all()[0]
        student.theme = theme
        student.diplomnik = True
        student.save()
    else:
        raise Http404
    return HttpResponseRedirect('/')

"""
CALENDAR
"""
def named_month(month_number):
    """
    Return the name of the month, given the number.
    """
    return date(1900, month_number, 1).strftime("%B")

def this_month(request):
    """
    Show calendar of events this month.
    """
    today = datetime.now()
    return calendar(request, today.year, today.month)


def calendar(request, year, month, series_id=None):
    """
    Show calendar of events for a given month of a given year.
    ``series_id``
    The event series to show. None shows all event series.

    """

    my_year = int(year)
    my_month = int(month)
    
    my_calendar_from_month = datetime(my_year, my_month, 1)
    my_calendar_to_month = datetime(my_year, my_month, monthrange(my_year, my_month)[1])

    my_events = Event.objects.filter(date_and_time__gte=my_calendar_from_month).filter(date_and_time__lte=my_calendar_to_month)
    #my_events += Stage.objects.filter(date_and_time__gte=my_calendar_from_month).filter(date_and_time__lte=my_calendar_to_month)
    if series_id:
        my_events = my_events.filter(series=series_id)

    # Calculate values for the calendar controls. 1-indexed (Jan = 1)
    my_previous_year = my_year
    my_previous_month = my_month - 1
    if my_previous_month == 0:
        my_previous_year = my_year - 1
        my_previous_month = 12
    my_next_year = my_year
    my_next_month = my_month + 1
    if my_next_month == 13:
        my_next_year = my_year + 1
        my_next_month = 1
    my_year_after_this = my_year + 1
    my_year_before_this = my_year - 1
    return render_to_response("cal_template.html", { 'events_list': my_events,
                                                        'month': my_month,
                                                        'month_name': named_month(my_month),
                                                        'year': my_year,
                                                        'previous_month': my_previous_month,
                                                        'previous_month_name': named_month(my_previous_month),
                                                        'previous_year': my_previous_year,
                                                        'next_month': my_next_month,
                                                        'next_month_name': named_month(my_next_month),
                                                        'next_year': my_next_year,
                                                        'year_before_this': my_year_before_this,
                                                        'year_after_this': my_year_after_this,
    }, context_instance=RequestContext(request))
"""
END CALENDAR
"""

@login_required    
def schedule(request, year=None, month=None):
    
    user = request.user
    prof = get_us_profile(user)
    
    now = datetime.date.today()
    
    if year == None:
        year = now.year
    year = int(year)
        
    if month == None:
        month = now.month
    month = int(month)
        
    if month == 0:
        year = year-1
        month = 12
        return HttpResponseRedirect('/schedule/%s/%s/' % (year, month))
    if month == 13:
        year = year+1
        month = 1
        return HttpResponseRedirect('/schedule/%s/%s/' % (year, month))
    
    last_day = pycalendar.monthrange(year, month)[1]
    
    event_list = []
    event_month = Event.objects.filter(date_and_time__gte = (datetime.datetime(year,month,1,0,0))).filter(date_and_time__lte=(datetime.datetime(year,month,last_day,23,59)))
    stage_month = Stage.objects.filter(date_and_time__gte = (datetime.datetime(year,month,1,0,0))).filter(date_and_time__lte=(datetime.datetime(year,month,last_day,23,59)))
    
    try:
        if user.student:
            # студенту показать только все event.series.id=1
            # и осдальные ид, куда он записан
            s = Serie.objects.get(id = 1)
            event_list = list(event_month.filter(series = s))
            for evl in event_month.exclude(series = s):
                es = evl.eventstudent_set.filter(student = user.student)
                if es:
                    event_list.append(evl)
            # + встречи без учителей, своего направления
            event_list += list(event_month.filter(specialization=user.student.specialization).exclude(student = user.student))

            event_list += list(stage_month)
    except:
        pass
    
    try:
        if user.teacher:
            # teacher'у только его встречи
            event_list = list(event_month.filter(teacher = prof))
            # +
            event_list += list(event_month.filter(teacher = None))
    except:
        pass
    
    return render_to_response('schedule.html', {
        'year':year,
        'month':month,
        "event_list":event_list
        }, context_instance=RequestContext(request))

@login_required    
def event_view(request, event_id):
    #
    #time_for_st = 30 # минут на одного студента
    # 
     
    event = get_object_or_404(Event, id=int(event_id))
    
    event_students = event.eventstudent_set.all()

    """
    event_students_time = []
    if event_students:
        for k in range(event_students.__len__()):
            est = [event_students.get(number=k), (event.date_and_time + datetime.timedelta(minutes=(TIME_FOR_ST*k)))]
            event_students_time.append(est)
    """

    event_errors=[]
    try:
        event_errors = request.session['event_join_error']
        del request.session['event_join_error']
    except:
        pass
    
    return render_to_response('event_view.html', {
        "errors":event_errors,
        "event":event,
        "event_students":event_students,
        #"event_students_time":event_students_time,
        }, context_instance=RequestContext(request))

@login_required
def event_join(request, event_id):
    # для студента
    # запись на встречу

    event = get_object_or_404(Event, id=int(event_id))
    
    user = request.user
    
    #только студент
    student = get_object_or_404(Student, user=user)
    
    if event.eventstudent_set.all().filter(student = student):
        request.session['event_join_error'] = u'Вы уже записаны!'
        return HttpResponseRedirect('/event/%s/' % event.id)
    
    num = event.eventstudent_set.count()
    if (event.date_and_time + datetime.timedelta(minutes=(TIME_FOR_ST*num))).time() > event.endtime:
        request.session['event_join_error'] = u'Всё уже занято!'
        return HttpResponseRedirect('/event/%s/' % event.id)
    
    eventstudent = EventStudent(
        event=event,
        date=event.date_and_time.date(),
        time=(event.date_and_time + datetime.timedelta(minutes=(TIME_FOR_ST*num))).time(),
        student = student)
    eventstudent.save()
        
    return HttpResponseRedirect('/event/%s/' % event.id)

@login_required
def event_add(request):
    #добавить встречу
    
    user = request.user
    #только тичер
    prof = get_object_or_404(Teacher, user=user)

    if request.method == "POST":
        teacher = Event(teacher = prof)
        form = EventAddForm(request.POST, instance = teacher)
        if form.is_valid():   # добавить проверки времени
            event = form.save()
            if event.series.id != 1:
                return HttpResponseRedirect('/event/%s/addstudent/' % event.id)
            return HttpResponseRedirect('/schedule/')
    else:
        form = EventAddForm()
    
    tit = u'Добавление встречи'
    
    return render_to_response('form.html', {
        'tit':tit,
        'form':form,
        }, context_instance=RequestContext(request))


@login_required
def super_event_add(request):
    user = request.user
    #только тичер
    prof = get_object_or_404(Teacher, user=user)

    if request.method == "POST":
        form = SuperEventAddForm(request.POST)
        if form.is_valid():   # добавить проверки времени
            form.save()
            return HttpResponseRedirect('/schedule/')
    else:
        form = SuperEventAddForm()

    tit = u'Добавление защиты/предзащиты'

    return render_to_response('form.html', {
        'tit':tit,
        'form':form,
        }, context_instance=RequestContext(request))


@login_required
def event_add_student(request, event_id):
    #преподаватель добавляет студента к встрече
    #для очной встречи или встречи в чате
    
    event = get_object_or_404(Event, id=int(event_id))
    
    user = request.user
    #только тичер
    prof = get_object_or_404(Teacher, user = user)
   
    if request.method == "POST":
        event_num = EventStudent(
            event=event,
            date=event.date_and_time.date(),
            time=event.date_and_time.time(),
            )
        form = EventAddStudentForm(request.POST, instance = event_num)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/schedule/')
    else:
        form = EventAddStudentForm()
        
    tit = u'Назначить встречу студенту'
    
    return render_to_response('form.html', {
        'tit':tit,
        'form':form,
        }, context_instance=RequestContext(request))

@login_required
def docs(request):
    user = request.user
    student = get_object_or_404(Student, user=user)
    if not student.diplomnik:
        raise Http404

    if (not student.year) or (not student.month) or (not student.type_of_work_id):
        if request.method == "POST":
            form = StudentYearMonthForm(request.POST)
            if form.is_valid():
                student.year = form.cleaned_data['year']
                student.month = form.cleaned_data['month']
                student.type_of_work = form.cleaned_data['type']
                student.save()
                HttpResponseRedirect(reverse('diplom.project2.views.docs'))

        form = StudentYearMonthForm()
        tit = u'Документация'
        help_text = u'Введите недостающие данные.'

        return render_to_response('form.html', {
            'tit':tit,
            'form':form,
            'help_text':help_text,
            }, context_instance=RequestContext(request))

    #teacher = student.theme.teacher

    last_name = (lastnames_ru.inflect(morph, user.last_name.upper(), u'рд,ед,мр')).capitalize()
    first_name = (morph.inflect_ru(user.first_name.upper(), u'рд,ед,имя', u'С')).capitalize()
    middle_name = (morph.inflect_ru(student.middle_name.upper(), u'рд,ед,отч', u'С')).capitalize()

    from_student_full_name = u'%s %s %s' % (last_name,first_name,middle_name)

    return render_to_response('docs.html',
            {'student':student,
             'from_student_full_name':from_student_full_name},
        context_instance=RequestContext(request))

@login_required
def zadanie(request):
    # для студента
    template = webodt.ODFTemplate('zadanie_na_vipusknuyu_rabotu.odt')

    user = request.user
    student = get_object_or_404(Student, user=user)
    theme = student.theme
    teacher = theme.teacher

    context = dict(
        student_full_name = u'%s %s %s' % (user.last_name, user.first_name, student.middle_name),
        theme = theme,
        teacher = teacher,
        theme_contents = theme.contents.splitlines(),
        teacher_initials = u'%s %s.%s.' % (teacher.user.last_name.capitalize(),
                                           teacher.user.first_name[0].capitalize(),
                                           teacher.middle_name[0].capitalize()),
        student_initials = u'%s %s.%s.' % (user.last_name.capitalize(),
                                           user.first_name[0].capitalize(),
                                           student.middle_name[0].capitalize()),
    )

    return shortcuts.render_to_response('zadanie_na_vipusknuyu_rabotu.odt', context)

@login_required
def zayavlenie(request):
    # для студента
    template = webodt.ODFTemplate('zayavlenie_na_vipusknuyu_rabotu.odt')

    user = request.user
    student = get_object_or_404(Student, user=user)
    theme = student.theme
    teacher = theme.teacher

    if student.sex:
        last_name = (lastnames_ru.inflect(morph, user.last_name.upper(), u'рд,ед,мр')).capitalize()
    else:
        last_name = (lastnames_ru.inflect(morph, user.last_name.upper(), u'рд,ед,жр')).capitalize()
    first_name = (morph.inflect_ru(user.first_name.upper(), u'рд,ед,имя', u'С')).capitalize()
    middle_name = (morph.inflect_ru(student.middle_name.upper(), u'рд,ед,отч', u'С')).capitalize()

    from_student_full_name = u'%s %s %s' % (last_name,first_name,middle_name)

    in_month=(morph.inflect_ru(student.month.upper(), u'пр')).lower()

    work_type = ''
    for s in student.type_of_work.name.split():
        work_type += (morph.inflect_ru(s.upper(), u'рд,ед')).lower() + ' '

    to_teacher_position = ''
    for s in teacher.position.split():
        to_teacher_position += (morph.inflect_ru(s.upper(), u'вн,ед')).lower() + ' '
    if teacher.sex:
        to_teacher_last_name = (lastnames_ru.inflect(morph, teacher.user.last_name.upper(), u'вн,ед,мр')).capitalize()
    else:
        to_teacher_last_name = (lastnames_ru.inflect(morph, teacher.user.last_name.upper(), u'вн,ед,жр')).capitalize()

    context = dict(
        from_student_full_name=from_student_full_name,
        work_type=work_type,
        in_month=in_month,
        theme = theme,
        teacher = teacher,
        student = student,
        theme_contents = theme.contents,
        to_teacher_position = to_teacher_position,
        to_teacher_initials = u'%s %s.%s.' % (to_teacher_last_name,
                                           teacher.user.first_name[0].capitalize(),
                                           teacher.middle_name[0].capitalize()),
        student_initials = u'%s %s.%s.' % (user.last_name.capitalize(),
                                           user.first_name[0].capitalize(),
                                           student.middle_name[0].capitalize()),
    )

    return shortcuts.render_to_response('zayavlenie_na_vipusknuyu_rabotu.odt', context)

@login_required
def diplomniks(request):
    user = request.user
    teacher = get_object_or_404(Teacher, user=user)

    diplomniks = []
    for t in Theme.objects.filter(teacher=teacher):
        if t.student_set.count():
            diplomniks.append(t.student_set.all()[0])
    
    return render_to_response('diplomniks.html', {'diplomniks':diplomniks},
        context_instance=RequestContext(request))

@login_required
def set_scores(request):
    user = request.user
    teacher = get_object_or_404(Teacher, user=user)

    teacher_students = list(Student.objects.filter(theme__in=(list(Theme.objects.filter(teacher=teacher)))))
    stages = Stage.objects.filter(score__isnull=True).\
        filter(student__in=teacher_students).\
        filter(date__lte=(datetime.datetime.now().date())).order_by('name','date')

    if request.method=="POST":
        for stage in stages:
            sform=ScoreForm(data=request.POST, prefix=stage.id)
            if sform.is_valid():
                stage.score=sform.cleaned_data['score']
                stage.save()

        return render_to_response('test2.html', {
            'stages':stages,
            },
            context_instance=RequestContext(request))

    score_forms=[]
    for stage in stages:
        sform=ScoreForm(prefix=stage.id)
        sf = [stage, sform]
        score_forms.append(sf)

    return render_to_response('test.html', {
        'score_forms':score_forms,
        },
        context_instance=RequestContext(request))

@login_required
def git(request):
    user = request.user
    prof = get_us_profile(user)

    try:
        if not prof.github.id:
            raise Http404
    except:
        raise Http404

    gh=Github(login=prof.github.username, password=prof.github.password)
    gh_user = gh.users.get()
    gh_repos = gh.repos.list().all()

    return render_to_response('gittest.html', {
        #'git_user':gh.users.get(),
        'git_login':gh_user.login,
        'git_url':gh_user.html_url,
        'git_repos':gh_repos,
        },
        context_instance=RequestContext(request))