from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import index, user_login, user_logout


urlpatterns = [
    path('login/', user_login , name='login'),
    path('logout/', user_logout , name='logout'),
    path('', index, name='index'),
    
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
