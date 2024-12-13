from django.contrib import admin
from django.urls import path,include
from Clone import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
   path("",views.home,name="home"),
   path("contact",views.contactus,name="contact"),
   path("about",views.about,name="about"),
   path("main",views.main,name="main"),
   path('upload-python-files/', views.upload_python_files, name='upload_python_files'),


]




urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

