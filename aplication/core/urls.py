from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('escanear/', EvaluacionIAView.as_view(), name='escanear'),
    path('seguimiento/', ProgresoView.as_view(), name='seguimiento'),
    path('comunidad/', comunidad, name='comunidad'),
    path('evaluacion-ia/', evaluacion_ia, name='evaluacion_ia'),

]
