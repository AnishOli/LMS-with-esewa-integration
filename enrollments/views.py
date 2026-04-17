from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from courses.models import Course
from .models import Enrollment, Payment
import hmac
import hashlib
import base64
import json
import uuid

@login_required
def enroll(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists():
        messages.info(request, "You are already enrolled in this course.")
        return redirect('courses:course_detail', slug=course.slug)

    # Free course
    if course.price == 0:
        Enrollment.objects.create(student=request.user, course=course)
        messages.success(request, f"Successfully enrolled in {course.title}!")
        return redirect('courses:course_detail', slug=course.slug)

    # Paid course - create Pending Enrollment and Payment
    enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course, defaults={'is_active': False})
    
    transaction_uuid = f"enroll_{enrollment.id}_{uuid.uuid4().hex[:6]}"
    
    if hasattr(enrollment, 'payment'):
        payment = enrollment.payment
        payment.status = 'PENDING'
        payment.transaction_uuid = transaction_uuid
        payment.save()
    else:
        payment = Payment.objects.create(
            enrollment=enrollment, 
            amount=course.price,
            transaction_uuid=transaction_uuid
        )

    amount = str(payment.amount)
    product_code = settings.ESEWA_MERCHANT_CODE
    secret_key = settings.ESEWA_SECRET_KEY

    message = f"total_amount={amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    hmac_sha256 = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
    signature = base64.b64encode(hmac_sha256).decode('utf-8')

    success_url = request.build_absolute_uri('/enrollments/esewa/success/')
    failure_url = request.build_absolute_uri('/enrollments/esewa/failure/')

    context = {
        'amount': amount,
        'transaction_uuid': transaction_uuid,
        'product_code': product_code,
        'signature': signature,
        'success_url': success_url,
        'failure_url': failure_url,
        'course': course
    }

    return render(request, 'enrollments/checkout.html', context)

@login_required
def esewa_success(request):
    encoded_data = request.GET.get('data')
    if not encoded_data:
        messages.error(request, "Invalid payment response.")
        return redirect('home')
        
    try:
        decoded_data = base64.b64decode(encoded_data).decode('utf-8')
        payload = json.loads(decoded_data)
        
        transaction_uuid = payload.get('transaction_uuid')
        status_esewa = payload.get('status')
        
        if status_esewa != 'COMPLETE':
            messages.error(request, "Payment was not completed.")
            return redirect('home')

        # Verify signature
        message = f"transaction_code={payload.get('transaction_code')},status={payload.get('status')},total_amount={payload.get('total_amount')},transaction_uuid={payload.get('transaction_uuid')},product_code={settings.ESEWA_MERCHANT_CODE},signed_field_names={payload.get('signed_field_names')}"
        hmac_sha256 = hmac.new(settings.ESEWA_SECRET_KEY.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
        expected_signature = base64.b64encode(hmac_sha256).decode('utf-8')
        
        if payload.get('signature') != expected_signature:
            messages.error(request, "Invalid payment signature.")
            return redirect('home')

        payment = Payment.objects.get(transaction_uuid=transaction_uuid)
        payment.status = 'COMPLETE'
        payment.save()
        
        enrollment = payment.enrollment
        enrollment.is_active = True
        enrollment.save()
        
        messages.success(request, f"Payment successful! You are now enrolled in {enrollment.course.title}.")
        return redirect('courses:course_detail', slug=enrollment.course.slug)

    except Exception as e:
        messages.error(request, "Payment verification failed.")
        return redirect('home')

@login_required
def esewa_failure(request):
    messages.error(request, "Payment was cancelled or failed.")
    return redirect('home')
