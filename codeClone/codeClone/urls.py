from django.contrib import admin
from django.urls import path,include
import Clone
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include(Clone.urls))
]
