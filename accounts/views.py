from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created! Welcome to EduSpace.')
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email    = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user     = authenticate(username=email, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Welcome back, {email}!')
                return redirect('home')
            messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

# ── PROFILE ─────────────────────────────────────────────────────────────────
@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name',  '').strip()
        user.first_name = first_name
        user.last_name  = last_name
        # Password change
        new_pass   = request.POST.get('new_password', '').strip()
        new_pass2  = request.POST.get('new_password2', '').strip()
        if new_pass:
            if new_pass == new_pass2:
                user.set_password(new_pass)
                update_session_auth_hash(request, user)
                messages.success(request, 'Password updated successfully.')
            else:
                messages.error(request, 'Passwords do not match.')
                return redirect('profile')
        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    return render(request, 'accounts/profile.html', {'user': user})

# ── STUDENT DASHBOARD ────────────────────────────────────────────────────────
@login_required
def student_dashboard(request):
    if request.user.is_instructor:
        return redirect('accounts:instructor_dashboard')
    from enrollments.models import Enrollment
    from quizzes.models import QuizAttempt
    enrollments   = Enrollment.objects.filter(student=request.user, is_active=True).select_related('course', 'course__category')
    quiz_attempts = QuizAttempt.objects.filter(student=request.user).select_related('quiz', 'quiz__module__course').order_by('-completed_at')[:10]
    context = {
        'enrollments':   enrollments,
        'quiz_attempts': quiz_attempts,
        'total_courses': enrollments.count(),
        'passed_quizzes': quiz_attempts.filter(passed=True).count(),
    }
    return render(request, 'accounts/student_dashboard.html', context)

# ── INSTRUCTOR DASHBOARD (accounts-scoped) ───────────────────────────────────
@login_required
def instructor_dashboard(request):
    if not request.user.is_instructor:
        return redirect('accounts:student_dashboard')
    from courses.models import Course
    from enrollments.models import Enrollment, Payment
    courses       = Course.objects.filter(instructor=request.user).prefetch_related('enrollments')
    total_students = Enrollment.objects.filter(course__in=courses, is_active=True).count()
    payments       = Payment.objects.filter(enrollment__course__in=courses, status='COMPLETE')
    total_income   = sum(p.amount for p in payments)
    recent_enrollments = Enrollment.objects.filter(course__in=courses, is_active=True).select_related('student', 'course').order_by('-enrolled_at')[:8]
    context = {
        'courses':            courses,
        'total_students':     total_students,
        'total_income':       total_income,
        'recent_enrollments': recent_enrollments,
        'total_courses':      courses.count(),
    }
    return render(request, 'accounts/instructor_dashboard.html', context)

