# forms.py
from django import forms
from .models import Skill, Booking, Review  # Add Review to imports
from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Your password must contain at least 8 characters.'
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Enter the same password as before, for verification.'
    )
    
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'role', 'bio')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
        help_texts = {
            'username': 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
            'email': 'Required. Enter a valid email address.',
            'role': 'Select whether you want to be a learner or skill sharer.',
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'description', 'duration', 'category', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'duration': forms.NumberInput(attrs={'min': 15, 'max': 240}),
        }
        help_texts = {
            'duration': 'Duration in minutes (minimum 15, maximum 240)',
            'is_available': 'Uncheck this if you want to temporarily hide this skill',
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'booking_date', 
            'booking_time',
            'swap_skill_name',
            'swap_skill_description',
            'swap_skill_duration',
            'swap_skill_category'
        ]
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'booking_time': forms.TimeInput(attrs={'type': 'time'}),
            'swap_skill_description': forms.Textarea(attrs={'rows': 4}),
            'swap_skill_duration': forms.NumberInput(attrs={'min': 15, 'max': 240}),
        }
        help_texts = {
            'swap_skill_duration': 'Duration in minutes (minimum 15, maximum 240)',
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'space-x-2'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'class': 'w-full'})
        }
        help_texts = {
            'rating': 'Rate your experience from 1 to 5 stars',
            'comment': 'Share your experience and feedback'
        }

