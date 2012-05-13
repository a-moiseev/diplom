from django.contrib import admin
from diplom.project2.models import *
from diplom.bbb.models import *

admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Theme)
admin.site.register(Serie)
admin.site.register(Event)
admin.site.register(EventStudent)
admin.site.register(Special_message)
admin.site.register(Specialization)
admin.site.register(StageName)
admin.site.register(Stage)
admin.site.register(StagePass)
admin.site.register(TypeOfWork)
admin.site.register(GitHubAccount)

admin.site.register(Meeting)