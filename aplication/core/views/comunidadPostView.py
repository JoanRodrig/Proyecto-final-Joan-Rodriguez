from django.views.generic import ListView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import redirect
from aplication.core.models import CommunityPost, PostLike, PostComment
from aplication.core.forms.ComPostForm import CommunityPostForm, PostCommentForm


class ComunidadView(LoginRequiredMixin, ListView):
    """Vista principal de la comunidad usando ListView"""
    model = CommunityPost
    template_name = 'core/comunidad.html'
    context_object_name = 'posts'
    paginate_by = 10
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('usuario').prefetch_related(
            'comentarios__usuario', 'post_likes'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommunityPostForm()
        context['comment_form'] = PostCommentForm()
        
        # Obtener posts que el usuario ha dado like
        if self.request.user.is_authenticated:
            user_likes = PostLike.objects.filter(
                usuario=self.request.user,
                post__in=context['page_obj']
            ).values_list('post_id', flat=True)
            context['user_likes'] = list(user_likes)
        else:
            context['user_likes'] = []
            
        return context
    
    

class CrearPostView(LoginRequiredMixin, CreateView):
    form_class = CommunityPostForm
    success_url = reverse_lazy('comunidad')
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, '¡Tu publicación ha sido creada exitosamente!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Hubo un error al crear tu publicación.')
        return super().form_invalid(form)




class ToggleLikeView(LoginRequiredMixin, View):
    """Vista para manejar likes usando View"""
    
    def post(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        post = get_object_or_404(CommunityPost, id=post_id)
        
        like, created = PostLike.objects.get_or_create(
            usuario=request.user,
            post=post
        )
        
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        
        likes_count = post.post_likes.count()
        
        return JsonResponse({
            'liked': liked,
            'likes_count': likes_count
        })




class AgregarComentarioView(LoginRequiredMixin, View):
    """Vista para agregar comentarios usando View"""
    
    def post(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        post = get_object_or_404(CommunityPost, id=post_id)
        form = PostCommentForm(request.POST)
        
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.post = post
            comentario.usuario = request.user
            comentario.save()
            
            return JsonResponse({
                'success': True,
                'comentario': {
                    'id': comentario.id,
                    'contenido': comentario.contenido,
                    'usuario': comentario.usuario.username,
                    'fecha': comentario.created_at.strftime('%d/%m/%Y %H:%M')
                },
                'comments_count': post.comments_count
            })
        
        return JsonResponse({
            'success': False,
            'errors': form.errors
        })




class ObtenerComentariosView(LoginRequiredMixin, View):
    """Vista para obtener comentarios usando View"""
    
    def get(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        post = get_object_or_404(CommunityPost, id=post_id)
        comentarios = post.comentarios.select_related('usuario').order_by('created_at')
        
        comentarios_data = [{
            'id': comentario.id,
            'contenido': comentario.contenido,
            'usuario': comentario.usuario.username,
            'fecha': comentario.created_at.strftime('%d/%m/%Y %H:%M')
        } for comentario in comentarios]
        
        return JsonResponse({
            'comentarios': comentarios_data,
            'count': len(comentarios_data)
        })




class EliminarPostView(LoginRequiredMixin, View):
    """Vista para eliminar posts usando View"""
    
    def post(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        post = get_object_or_404(CommunityPost, id=post_id, usuario=request.user)
        post.delete()
        
        messages.success(request, 'Tu publicación ha sido eliminada.')
        return redirect('comunidad')




class EliminarComentarioView(LoginRequiredMixin, View):
    """Vista para eliminar comentarios usando View"""
    
    def post(self, request, *args, **kwargs):
        comment_id = kwargs.get('comment_id')
        comentario = get_object_or_404(PostComment, id=comment_id, usuario=request.user)
        post_id = comentario.post.id
        comentario.delete()
        
        return JsonResponse({
            'success': True,
            'post_id': post_id,
            'comments_count': comentario.post.comments_count
        })