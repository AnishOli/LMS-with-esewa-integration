from django.contrib import admin
from .models import Category, Course, Module, Lesson

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'instructor', 'price', 'created')
    list_filter = ('created', 'category')
    search_fields = ('title', 'overview')

admin.site.register(Category)
admin.site.register(Module)
admin.site.register(Lesson)
