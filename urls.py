from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
	       path('Login.html', views.Login, name="Login"), 
	       path('Upload.html', views.Upload, name="Upload"),
	       path('OfficialLogin', views.OfficialLogin, name="OfficialLogin"),
	       path('UploadAction', views.UploadAction, name="UploadAction"),
	       path('ViewUpload', views.ViewUpload, name="ViewUpload"),
]