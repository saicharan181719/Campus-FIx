from django import forms
from .models import Issue


class IssueForm(forms.ModelForm):

    class Meta:
        model = Issue

        fields = [
            'title',
            'description',
            'category',
            'location',
            'priority',
            'image',
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Example: Classroom light not working',
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe the issue in detail...',
            }),

            'category': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'location': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'priority': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'image': forms.ClearableFileInput(
                attrs={'class': 'form-control'}
            ),
        }


class IssueUpdateForm(forms.ModelForm):

    class Meta:
        model = Issue

        fields = ['status']

        widgets = {
            'status': forms.Select(
                attrs={'class': 'form-select'}
            ),
        }