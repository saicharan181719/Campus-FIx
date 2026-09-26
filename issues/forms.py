from django import forms
from accounts.models import User
from .models import Issue, Category, Location


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
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.Select(attrs={
                'class': 'form-select'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }


class IssueUpdateForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class AdminIssueUpdateForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['status', 'assigned_to']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['assigned_to'].queryset = User.objects.filter(
            role='maintenance',
            is_active=True
        )

        self.fields['assigned_to'].required = False
        self.fields['assigned_to'].empty_label = 'Unassigned'
    
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category description',
                'rows': 4,
            }),
        }

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = [
            'block',
            'building',
            'room',
            'area',
        ]

        widgets = {
            'block': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter block',
            }),
            'building': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter building',
            }),
            'room': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter room',
            }),
            'area': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter area',
            }),
        }