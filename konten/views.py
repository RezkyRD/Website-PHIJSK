from django.shortcuts import render, get_object_or_404
from .models import UnitKerja, Berita, Kontak


def beranda(request):
    """Halaman utama Ditjen — memuat bagan struktur unit yang bisa diklik."""
    unit_list = UnitKerja.objects.all()
    berita_terbaru = Berita.objects.filter(status="published")[:6]
    return render(
        request,
        "konten/beranda.html",
        {"unit_list": unit_list, "berita_terbaru": berita_terbaru},
    )


def unit_detail(request, slug):
    """Halaman unit kerja dengan 4 tab: Beranda, Berita, Tusi, Struktur Organisasi."""
    unit = get_object_or_404(UnitKerja, slug=slug)
    tab = request.GET.get("tab", "beranda")
    if tab not in {"beranda", "berita", "tusi", "struktur"}:
        tab = "beranda"

    berita_list = None
    if tab == "berita":
        berita_list = unit.berita_list.filter(status="published")

    tabs = [
        ("beranda", "BERANDA"),
        ("berita", "BERITA"),
        ("tusi", "TUSI"),
        ("struktur", "STRUKTUR ORGANISASI"),
    ]
    return render(
        request,
        "konten/unit_detail.html",
        {"unit": unit, "tab": tab, "berita_list": berita_list, "tabs": tabs},
    )


def berita_detail(request, slug):
    berita = get_object_or_404(Berita, slug=slug, status="published")
    return render(request, "konten/berita_detail.html", {"berita": berita})


def kontak(request):
    info = Kontak.objects.first()
    return render(request, "konten/kontak.html", {"info": info})
