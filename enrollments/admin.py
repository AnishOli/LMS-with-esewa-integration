from django.contrib import admin
from .models import Enrollment, Payment

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'is_active')
    list_filter = ('is_active', 'enrolled_at')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_uuid', 'enrollment', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
