# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from registration.forms import RegistrationFormUniqueEmail

from django.contrib.staticfiles.urls import staticfiles_urlpatterns


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'diplom.project2.views.main'),
    
    # django-registration
    url(r'^accounts/', include('registration.urls')),

    url(r'^accounts/profile/$', 'diplom.project2.views.get_profile'),
    url(r'^accounts/profile/(?P<user_id>\d+)/$', 'diplom.project2.views.get_profile'),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^theme/add/$', 'diplom.project2.views.theme_add'),
    url(r'^theme/(?P<theme_id>\d+)/$', 'diplom.project2.views.theme_view'),
    url(r'^theme/(?P<theme_id>\d+)/edit/$', 'diplom.project2.views.theme_edit'),
    
    url(r'^teachers/$', 'diplom.project2.views.teachers'),
    url(r'^teachers/request/(?P<user_id>\d+)/$', 'diplom.project2.views.teachers_request'),
    url(r'^teachers/request/(?P<user_id>\d+)/send/$', 'diplom.project2.views.teachers_send_request'),
    
    url(r'^interest/add/$', 'diplom.project2.views.interest_add'),
    
    url(r'^messages/view/(?P<message_id>[\d]+)/spec/$', 'diplom.project2.views.specmsg_view'),
    url(r'^messages/reply/(?P<message_id>[\d]+)/spec/$', 'diplom.project2.views.specmsg_reply'),
    url(r'^messages/choose/(?P<message_id>[\d]+)/spec/$', 'diplom.project2.views.specmsg_choose'),

    url(r'^messages/', include('messages.urls')),
    
    #url(r'^chat/', include('jqchat.urls')),
    url(r'^chat/', include('chatrooms.urls')),
    
    url(r'^schedule/$', 'diplom.project2.views.schedule'),
    url(r'^schedule/(?P<year>\d+)/(?P<month>\d+)/$', 'diplom.project2.views.schedule'), # year - 4 цифры!!!
    url(r'^event/add/$', 'diplom.project2.views.event_add'),
    url(r'^event/(?P<event_id>\d+)/$', 'diplom.project2.views.event_view'),
    url(r'^event/(?P<event_id>\d+)/join/$', 'diplom.project2.views.event_join'),
    url(r'^event/(?P<event_id>\d+)/addstudent/$', 'diplom.project2.views.event_add_student'),
    url(r'^superevent/add/$', 'diplom.project2.views.super_event_add'),

    url(r'^docs/$', 'diplom.project2.views.docs'),
    url(r'^docs/zadanie/$', 'diplom.project2.views.zadanie'),
    url(r'^docs/zayavlenie/$', 'diplom.project2.views.zayavlenie'),

    url(r'^diplomniks/$', 'diplom.project2.views.diplomniks'),

    url(r'^scores/$', 'diplom.project2.views.set_scores'),

    url(r'^git/$', 'diplom.project2.views.git'),
)

urlpatterns += staticfiles_urlpatterns()