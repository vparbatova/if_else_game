# game/admin.py
from django.contrib import admin
from .models import GameQuestion, Answer, UserProgress


class AnswerInlineAdmin(admin.TabularInline):
    model = Answer
    extra = 3
    fields = ['text', 'next_question', 'image', 'order',
              'emotion_change', 'time_change']
    ordering = ['order']
    fk_name = 'question'


@admin.register(GameQuestion)
class GameQuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'is_final']
    list_filter = ['is_final']
    search_fields = ['text']
    inlines = [AnswerInlineAdmin]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'text', 'next_question', 'order']
    list_filter = ['question']
    search_fields = ['text']
    list_editable = ['order']


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_question']
    search_fields = ['user__username']
    readonly_fields = ['answers_history']
