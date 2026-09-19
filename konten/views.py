from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import UnitKerja, Berita, Komentar, Kontak, ProfilDitjen


def beranda(request):
    """Halaman utama Ditjen — hero foto gedung, headline Informasi + panel profil/tupoksi (dua kolom), bagan struktur."""
    unit_list = list(UnitKerja.objects.all())
    sekretariat = unit_list[0] if unit_list else None
    direktorat = unit_list[1:] if len(unit_list) > 1 else []
    profil = ProfilDitjen.objects.first()
    headline_list = (
        Berita.objects.filter(status="published")
        .select_related("unit_kerja")
        .order_by("-tanggal_publish")[:5]
    )

    return render(
        request,
        "konten/beranda.html",
        {
            "sekretariat": sekretariat,
            "direktorat": direktorat,
            "profil": profil,
            "tupoksi_items": profil.tupoksi_items() if profil else [],
            "headline_list": headline_list,
        },
    )


def unit_list(request):
    """Halaman daftar Unit Kerja — navigasi untuk memilih direktorat."""
    unit_list = UnitKerja.objects.all()
    return render(request, "konten/unit_list.html", {"unit_list": unit_list})


def unit_detail(request, slug):
    """Halaman unit kerja dengan 2 tab: Beranda (Tusi + Struktur) dan Informasi."""
    unit = get_object_or_404(UnitKerja, slug=slug)
    tab = request.GET.get("tab", "beranda")
    if tab not in {"beranda", "informasi"}:
        tab = "beranda"

    berita_list = None
    tim_kerja_utama = None
    if tab == "informasi":
        berita_list = unit.berita_list.filter(status="published")
    else:
        tim_kerja_utama = unit.tim_kerja_utama()

    tabs = [
        ("beranda", "BERANDA"),
        ("informasi", "INFORMASI"),
    ]
    return render(
        request,
        "konten/unit_detail.html",
        {"unit": unit, "tab": tab, "berita_list": berita_list, "tim_kerja_utama": tim_kerja_utama, "tabs": tabs},
    )


def informasi_detail(request, slug):
    """Halaman detail satu Informasi — bisa dilihat publik & menerima komentar (perlu disetujui admin dulu)."""
    berita = get_object_or_404(Berita, slug=slug, status="published")

    if request.method == "POST":
        # Honeypot anti-spam: field ini disembunyikan lewat CSS di form, manusia tidak akan mengisinya.
        website = request.POST.get("website", "").strip()
        nama = request.POST.get("nama", "").strip()
        isi = request.POST.get("isi", "").strip()
        email = request.POST.get("email", "").strip()

        if website:
            pass  # terdeteksi bot, diam-diam abaikan tanpa pesan error
        elif not nama or not isi:
            messages.error(request, "Nama dan komentar wajib diisi.")
        else:
            Komentar.objects.create(berita=berita, nama=nama[:100], email=email, isi=isi)
            messages.success(request, "Komentar Anda terkirim dan akan tampil setelah disetujui admin.")
        return redirect("konten:informasi_detail", slug=berita.slug)

    komentar_list = berita.komentar_disetujui()
    return render(
        request,
        "konten/informasi_detail.html",
        {"berita": berita, "komentar_list": komentar_list},
    )


def kontak(request):
    info = Kontak.objects.first()
    return render(request, "konten/kontak.html", {"info": info})
