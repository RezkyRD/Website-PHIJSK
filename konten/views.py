from django.shortcuts import render, get_object_or_404
from .models import UnitKerja, Berita, Kontak, ProfilDitjen


def beranda(request):
    """Halaman utama Ditjen — hero foto gedung, panel profil/tupoksi (akordion), bagan struktur."""
    semua_unit = list(UnitKerja.objects.all())
    profil = ProfilDitjen.objects.first()

    return render(
        request,
        "konten/beranda.html",
        {
            "semua_unit": semua_unit,
            "profil": profil,
            "tupoksi_items": profil.tupoksi_items() if profil else [],
        },
    )


def unit_list(request):
    """Halaman daftar Unit Kerja — navigasi untuk memilih direktorat."""
    unit_list = UnitKerja.objects.all()
    return render(request, "konten/unit_list.html", {"unit_list": unit_list})


def unit_detail(request, slug):
    """Halaman unit kerja dengan 2 tab: Beranda (Tusi + Struktur) dan Berita."""
    unit = get_object_or_404(UnitKerja, slug=slug)
    tab = request.GET.get("tab", "beranda")
    if tab not in {"beranda", "berita"}:
        tab = "beranda"

    berita_list = None
    if tab == "berita":
        berita_list = unit.berita_list.filter(status="published")

    tabs = [
        ("beranda", "BERANDA"),
        ("berita", "BERITA"),
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
