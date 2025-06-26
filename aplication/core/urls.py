from django.urls import path
from aplication.core.views.indexView import  index
from aplication.core.views.evaluacionView import  EvaluacionIAView
from aplication.core.views.progresoView import  ProgresoView
from aplication.core.views.comunidadPostView import  *

urlpatterns = [
    path('', index, name='index'),
    path('evaluacion-ia/', EvaluacionIAView.as_view(), name='evaluacion_ia'),
    path('progreso/', ProgresoView.as_view(), name='progreso'),
    path('comunidad/',ComunidadView.as_view(), name='comunidad'),
    # Gestión de posts
    path('comunidad/crear_post/', CrearPostView.as_view(), name='crear_post'),
    path('comunidad/toggle_like/<int:post_id>/', ToggleLikeView.as_view(), name='toggle_like'),
    path('comunidad/agregar_comentario/<int:post_id>/', AgregarComentarioView.as_view(), name='agregar_comentario'),
    path('comunidad/obtener_comentarios/<int:post_id>/', ObtenerComentariosView.as_view(), name='obtener_comentarios'),
    path('comunidad/eliminar_post/<int:post_id>/', EliminarPostView.as_view(), name='eliminar_post'),
    path('comunidad/eliminar_comentario/<int:comment_id>/', EliminarComentarioView.as_view(), name='eliminar_comentario'),
]
