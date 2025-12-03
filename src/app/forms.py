"""Forms for DJGramm."""

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, Post, PostImage, Profile, User


class RegistrationForm(UserCreationForm):
    """User registration form with email."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        """Validate email is unique."""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class ProfileForm(forms.ModelForm):
    """Profile edit form."""

    class Meta:
        model = Profile
        fields = ["full_name", "bio", "avatar"]
        widgets = {
            "bio": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Tell us about yourself..."}
            ),
        }


class PostForm(forms.ModelForm):
    """Post creation/edit form."""

    class Meta:
        model = Post
        fields = ["caption"]
        widgets = {
            "caption": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Write a caption...",
                    "maxlength": 2200,
                }
            ),
        }


class PostImageForm(forms.ModelForm):
    """Single image upload form."""

    class Meta:
        model = PostImage
        fields = ["image"]


# Formset for multiple images
PostImageFormSet = forms.inlineformset_factory(
    Post,
    PostImage,
    form=PostImageForm,
    extra=6,  # Extra empty forms for new images
    max_num=10,
    can_delete=True,
    validate_max=True,
)


class CommentForm(forms.ModelForm):
    """Comment form."""

    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "rows": 2,
                    "placeholder": "Add a comment...",
                    "maxlength": 500,
                    "class": "comment-input",
                }
            ),
        }
