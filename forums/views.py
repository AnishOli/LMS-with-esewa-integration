from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Forum, Thread, Reply
from courses.models import Course

def forum_list(request):
    # Get all forums that have a course
    forums = Forum.objects.all().select_related('course')
    return render(request, 'forums/forum_list.html', {'forums': forums})

def thread_list(request, forum_id):
    forum = get_object_or_404(Forum, id=forum_id)
    threads = forum.threads.all().select_related('author')
    return render(request, 'forums/thread_list.html', {'forum': forum, 'threads': threads})

def thread_detail(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    replies = thread.replies.all().select_related('author')
    return render(request, 'forums/thread_detail.html', {'thread': thread, 'replies': replies})

@login_required
def create_thread(request, forum_id):
    forum = get_object_or_404(Forum, id=forum_id)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            thread = Thread.objects.create(
                forum=forum,
                author=request.user,
                title=title,
                content=content
            )
            messages.success(request, "Question posted successfully!")
            return redirect('forums:thread_detail', thread_id=thread.id)
        messages.error(request, "Both title and content are required.")
    return render(request, 'forums/create_thread.html', {'forum': forum})

@login_required
def create_reply(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Reply.objects.create(
                thread=thread,
                author=request.user,
                content=content
            )
            messages.success(request, "Reply posted successfully!")
            # Update thread's updated_at
            thread.save() # Triggers auto_now
            return redirect('forums:thread_detail', thread_id=thread.id)
        messages.error(request, "Reply content cannot be empty.")
    return redirect('forums:thread_detail', thread_id=thread.id)
