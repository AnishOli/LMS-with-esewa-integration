from django.contrib import admin
from .models import Forum, Thread, Reply

admin.site.register(Forum)
admin.site.register(Thread)
admin.site.register(Reply)
