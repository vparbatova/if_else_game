from django.db import models
from django.contrib.auth.models import User


class GameQuestion(models.Model):
    text = models.CharField('Текст вопроса', max_length=500)
    image = models.CharField('Путь к картинке вопроса',
                             max_length=200,
                             blank=True,
                             null=True)
    is_first = models.BooleanField('Первый вопрос', default=False)
    is_final = models.BooleanField('Финальный вопрос', default=False)
    final_message = models.TextField('Финальное сообщение', blank=True)

    def get_answers(self):
        return self.answers.all().order_by('order')

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class Answer(models.Model):
    question = models.ForeignKey(GameQuestion, on_delete=models.CASCADE, 
                                 related_name='answers')
    text = models.CharField('Текст ответа', max_length=200)
    next_question = models.ForeignKey(GameQuestion, on_delete=models.SET_NULL,
                                      null=True, blank=True,
                                      related_name='previous_answers')
    image = models.CharField('Путь к картинке', max_length=200,
                             blank=True, null=True)
    order = models.IntegerField('Порядок', default=0)
    emotion_change = models.IntegerField('Изменение эмоционального состояния',
                                         default=0)
    time_change = models.IntegerField('Изменение времени', default=0)

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'
        ordering = ['order']


class UserProgress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='game_progress')
    current_question = models.ForeignKey(GameQuestion,
                                         on_delete=models.SET_NULL,
                                         null=True)
    answers_history = models.JSONField(default=list)
    emotion_score = models.IntegerField('Эмоциональное состояние', default=50)
    time_score = models.IntegerField('Время', default=50)
