"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve as static_serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('konten.urls')),
]

# Foto/berkas upload (media) selalu dilayani, termasuk saat DEBUG=False di produksi.
# CATATAN: django.conf.urls.static.static() TIDAK dipakai di sini karena fungsi itu
# secara internal no-op (tidak menambah rute apa pun) kalau settings.DEBUG=False,
# apa pun kondisinya di kode kita. Jadi kita panggil view serve() langsung, melewati
# pengecekan DEBUG bawaan itu.
# Untuk situs skala kecil ini caranya cukup memadai; kalau traffic-nya besar nanti,
# sebaiknya pindah ke penyimpanan cloud terpisah (S3-compatible dsb).
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),
]
