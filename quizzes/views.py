from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Quiz, Question, Answer, QuizAttempt

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check enrollment
    from enrollments.models import Enrollment
    if not request.user.is_instructor and not Enrollment.objects.filter(student=request.user, course=quiz.module.course, is_active=True).exists():
        messages.error(request, "You must be enrolled to take this quiz.")
        return redirect('courses:course_detail', slug=quiz.module.course.slug)

    questions = quiz.questions.all()
    
    if request.method == 'POST':
        total_questions = questions.count()
        correct_answers = 0
        
        for q in questions:
            selected_ans_id = request.POST.get(f'question_{q.id}')
            if selected_ans_id:
                try:
                    ans = Answer.objects.get(id=selected_ans_id, question=q)
                    if ans.is_correct:
                        correct_answers += 1
                except Answer.DoesNotExist:
                    pass
                    
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        passed = score >= quiz.passing_score
        
        attempt = QuizAttempt.objects.create(
            student=request.user,
            quiz=quiz,
            score=score,
            passed=passed
        )
        
        return redirect('quizzes:quiz_result', attempt_id=attempt.id)
        
    return render(request, 'quizzes/take_quiz.html', {'quiz': quiz, 'questions': questions})

@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    return render(request, 'quizzes/quiz_result.html', {'attempt': attempt})
