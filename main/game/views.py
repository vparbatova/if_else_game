from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.conf import settings
from .forms import RegisterForm, LoginForm
from .models import GameQuestion, UserProgress, Answer
import os


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            first_question = GameQuestion.objects.first()
            UserProgress.objects.create(user=request.user, current_question=first_question)
            return redirect('question')
    else:
        form = RegisterForm()
    return render(request, 'game/register.html', {'form': form})


@login_required
def question_view(request):
    progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        defaults={
            'current_question': GameQuestion.objects.first(),
            'emotion_score': 50,
            'time_score': 50
        }
    )

    if not progress.current_question:
        first_question = GameQuestion.objects.first()
        if first_question:
            progress.current_question = first_question
            progress.save()

    question = progress.current_question

    if request.method == 'POST':
        answer_id = request.POST.get('answer_id')
        answer = get_object_or_404(Answer, id=answer_id)

        progress.emotion_score = progress.emotion_score + answer.emotion_change
        progress.time_score = progress.time_score + answer.time_change

        history = progress.answers_history
        history.append({
            'question_id': question.id,
            'question_text': question.text,
            'answer_text': answer.text,
            'answer_id': answer.id,
            'emotion_change': answer.emotion_change,
            'time_change': answer.time_change,
            'emotion_after': progress.emotion_score,
            'time_after': progress.time_score
        })
        progress.answers_history = history

        if answer.next_question:
            progress.current_question = answer.next_question
            progress.save()
            return redirect('question')
        else:
            progress.current_question = None
            progress.save()
            return redirect('game_result')

    answers = question.get_answers()
    return render(request, 'game/question.html', {
        'question': question,
        'answers': answers,
        'emotion_score': progress.emotion_score,
        'time_score': progress.time_score
    })


@login_required
def game_result(request):
    progress = request.user.game_progress
    
    emotion = progress.emotion_score
    time_score = progress.time_score

    if emotion >= 70 and time_score >= 70:
        ending_type = 'happy'
        ending_title = '🎉 Счастливый конец! 🎉'
        ending_text = 'Вы прекрасно провели время и остались довольны! Ваше эмоциональное состояние на высоте, а время потрачено с пользой!'
        ending_image = 'game/images/happy_ending.jpg'
    elif emotion >= 70 and time_score < 30:
        ending_type = 'emotional'
        ending_title = '😊 Эмоциональный, но быстрый конец'
        ending_text = 'Вы получили массу эмоций, но время пролетело незаметно! Возможно, стоило бы чуть больше времени уделить процессу.'
        ending_image = 'game/images/emotional_ending.jpg'
    elif emotion < 30 and time_score >= 70:
        ending_type = 'long'
        ending_title = '⏰ Долгий, но спокойный конец'
        ending_text = 'Вы потратили много времени, но остались спокойны. Иногда важнее процесс, чем результат!'
        ending_image = 'game/images/long_ending.jpg'
    else:
        ending_type = 'bad'
        ending_title = '😔 Грустный конец'
        ending_text = 'К сожалению, вы не получили удовольствия и потратили время впустую. В следующий раз стоит выбирать иначе!'
        ending_image = 'game/images/bad_ending.jpg'
    
    # Сбрасываем прогресс после показа концовки (опционально)
    # progress.current_question = GameQuestion.objects.first()
    # progress.emotion_score = 50
    # progress.time_score = 50
    # progress.answers_history = []
    # progress.save()
    
    return render(request, 'game/game_result.html', {
        'ending_title': ending_title,
        'ending_text': ending_text,
        'ending_image': ending_image,
        'ending_type': ending_type,
        'emotion_score': emotion,
        'time_score': time_score
    })


@login_required
def reset_game(request):
    progress = request.user.game_progress
    first_question = GameQuestion.objects.first()
    progress.current_question = first_question
    progress.answers_history = []
    progress.save()
    return redirect('question')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('question')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('question')
    else:
        form = LoginForm()
    
    return render(request, 'game/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')
