from django import forms
from aplication.core.models import CommunityPost, PostComment


class CommunityPostForm(forms.ModelForm):
    """Formulario para crear nuevos posts en la comunidad"""
    
    class Meta:
        model = CommunityPost
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'form-control post-textarea',
                'placeholder': '¿Qué quieres compartir con la comunidad?',
                'rows': 4,
                'maxlength': 500
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contenido'].label = ''


class PostCommentForm(forms.ModelForm):
    """Formulario para agregar comentarios a los posts"""
    
    class Meta:
        model = PostComment
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'form-control comment-textarea',
                'placeholder': 'Escribe tu comentario...',
                'rows': 2,
                'maxlength': 300
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contenido'].label = ''