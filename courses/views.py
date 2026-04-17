from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Category, Lesson
from .forms import CourseForm


def home_view(request):
    courses = Course.objects.select_related('instructor', 'category').all()[:8]
    return render(request, 'home.html', {'courses': courses})

def course_list(request):
    courses = Course.objects.all()
    categories = Category.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses, 'categories': categories})

def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    
    is_enrolled = False
    if request.user.is_authenticated:
        from enrollments.models import Enrollment
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists()
        
    return render(request, 'courses/course_detail.html', {'course': course, 'is_enrolled': is_enrolled})
@login_required
def lesson_detail(request, slug, lesson_id):
    course = get_object_or_404(Course, slug=slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)
    
    from enrollments.models import Enrollment
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists()
    
    if not is_enrolled and not request.user.is_instructor:
        messages.error(request, "You must be enrolled to view this lesson.")
        return redirect('courses:course_detail', slug=course.slug)
        
    return render(request, 'courses/lesson_detail.html', {'course': course, 'lesson': lesson})
@login_required
def instructor_dashboard(request):
    if not request.user.is_instructor:
        messages.error(request, 'Access denied. You are not an instructor.')
        return redirect('home')
    
    courses = Course.objects.filter(instructor=request.user)
    
    # Calculate stats
    from enrollments.models import Enrollment, Payment
    total_students = Enrollment.objects.filter(course__in=courses, is_active=True).count()
    total_income = sum(payment.amount for payment in Payment.objects.filter(enrollment__course__in=courses, status='COMPLETE'))
    
    context = {
        'courses': courses,
        'total_students': total_students,
        'total_income': total_income,
    }
    return render(request, 'courses/instructor_dashboard.html', context)

@login_required
def course_create(request):
    if not request.user.is_instructor:
        return redirect('home')
        
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, 'Course created successfully.')
            return redirect('courses:instructor_dashboard')
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {'form': form, 'action': 'Create'})

@login_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk, instructor=request.user)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully.')
            return redirect('courses:instructor_dashboard')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/course_form.html', {'form': form, 'action': 'Edit', 'course': course})

@login_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk, instructor=request.user)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully.')
        return redirect('courses:instructor_dashboard')
    return render(request, 'courses/course_confirm_delete.html', {'course': course})
