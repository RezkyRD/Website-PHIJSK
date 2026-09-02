from django.urls import path
from . import views

app_name = "konten"

urlpatterns = [
    path("", views.beranda, name="beranda"),
    path("kontak/", views.kontak, name="kontak"),
    path("berita/<slug:slug>/", views.berita_detail, name="berita_detail"),
    path("unit/<slug:slug>/", views.unit_detail, name="unit_detail"),
]
