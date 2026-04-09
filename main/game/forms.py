# game/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import GameQuestion, Answer, UserProgress


class RegisterForm(UserCreationForm):
    """
    Форма регистрации нового пользователя
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'example@mail.com'
        })
    )
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите имя пользователя'
        })
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите пароль'
        })
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Повторите пароль'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        """
        Проверка, что email уникальный
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email
    
    def save(self, commit=True):
        """
        Сохранение пользователя с email
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Имя пользователя'
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Пароль'
        })
    )

    error_messages = {
        'invalid_login': 'Неверное имя пользователя или пароль',
        'inactive': 'Аккаунт отключен',
    }


class QuestionForm(forms.Form):
    """
    Форма для ответа на вопрос
    Динамически создаётся в зависимости от вопроса
    """
    answer_id = forms.IntegerField(widget=forms.HiddenInput())
    
    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question = question
        
        # Добавляем поле с выбором ответа (если нужно)
        answers = question.get_answers()
        choices = [(a.id, a.text) for a in answers]
        
        self.fields['answer_choice'] = forms.ChoiceField(
            choices=choices,
            widget=forms.RadioSelect(attrs={'class': 'answer-radio'}),
            label='Выберите ответ'
        )


class GameResetForm(forms.Form):
    """
    Форма для сброса игры
    """
    confirm = forms.BooleanField(
        required=False,
        widget=forms.HiddenInput(),
        initial=True
    )


class AdminQuestionForm(forms.ModelForm):
    """
    Форма для создания/редактирования вопроса в админке
    """
    class Meta:
        model = GameQuestion
        fields = ['text', 'is_final', 'final_message']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'cols': 80}),
            'final_message': forms.Textarea(attrs={'rows': 3, 'cols': 80}),
        }
    
    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) < 5:
            raise forms.ValidationError('Текст вопроса слишком короткий')
        return text


class AdminAnswerForm(forms.ModelForm):
    """
    Форма для создания/редактирования ответа в админке
    """
    class Meta:
        model = Answer
        fields = ['question', 'text', 'next_question', 'image', 'order']
        widgets = {
            'text': forms.TextInput(attrs={'size': 60}),
            'image': forms.TextInput(attrs={'size': 60, 'placeholder': 'game/images/example.jpg'}),
        }
    
    def clean_order(self):
        order = self.cleaned_data.get('order')
        if order < 0:
            raise forms.ValidationError('Порядок не может быть отрицательным')
        return order
    
    def clean(self):
        cleaned_data = super().clean()
        question = cleaned_data.get('question')
        text = cleaned_data.get('text')
        
        # Проверяем, нет ли уже такого ответа у этого вопроса
        if question and text:
            if Answer.objects.filter(question=question, text=text).exclude(id=self.instance.id).exists():
                raise forms.ValidationError('Такой вариант ответа уже существует для этого вопроса')
        
        return cleaned_data


class UserProgressForm(forms.ModelForm):
    """
    Форма для просмотра прогресса пользователя (только для админа)
    """
    class Meta:
        model = UserProgress
        fields = ['user', 'current_question', 'answers_history']
        widgets = {
            'answers_history': forms.Textarea(attrs={'rows': 10, 'cols': 80}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['current_question'].queryset = GameQuestion.objects.all()
        self.fields['current_question'].required = False


class BulkQuestionForm(forms.Form):
    """
    Форма для массового создания вопросов (для админки)
    """
    csv_file = forms.FileField(
        label='CSV файл с вопросами',
        help_text='Формат: текст_вопроса, вариант1, вариант2, вариант3, ...'
    )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            raise forms.ValidationError('Файл должен быть в формате CSV')
        
        if csv_file.size > 1024 * 1024:  # 1MB
            raise forms.ValidationError('Файл слишком большой (максимум 1MB)')
        
        return csv_file