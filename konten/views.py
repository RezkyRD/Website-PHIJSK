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
    """Halaman detail satu Informasi — publik bisa berkomentar & membalas komentar (berjenjang),
    tampil langsung tanpa moderasi. Admin/staf yang login otomatis membalas sebagai admin unitnya."""
    berita = get_object_or_404(Berita, slug=slug, status="published")
    is_staff = request.user.is_authenticated and request.user.is_staff

    if request.method == "POST":
        # Honeypot anti-spam: field ini disembunyikan lewat CSS di form, manusia tidak akan mengisinya.
        website = request.POST.get("website", "").strip()
        isi = request.POST.get("isi", "").strip()
        parent_id = request.POST.get("parent_id", "").strip()
        parent = Komentar.objects.filter(id=parent_id, berita=berita).first() if parent_id else None

        if is_staff:
            profile = getattr(request.user, "unit_profile", None)
            if request.user.is_superuser:
                nama = "Admin Ditjen PHI dan Jamsos"
            elif profile:
                nama = f"Admin {profile.unit_kerja.singkatan}"
            else:
                nama = f"Admin ({request.user.username})"
            email = ""
        else:
            nama = request.POST.get("nama", "").strip()[:100]
            email = request.POST.get("email", "").strip()

        if website:
            pass  # terdeteksi bot, diam-diam abaikan tanpa pesan error
        elif not isi or (not is_staff and not nama):
            messages.error(request, "Nama dan komentar wajib diisi.")
        else:
            Komentar.objects.create(
                berita=berita, parent=parent, nama=nama, email=email, isi=isi, is_admin_reply=is_staff,
            )
            messages.success(request, "Komentar Anda berhasil dikirim.")
        return redirect("konten:informasi_detail", slug=berita.slug)

    komentar_root_list = berita.komentar_root()
    return render(
        request,
        "konten/informasi_detail.html",
        {"berita": berita, "komentar_root_list": komentar_root_list, "is_staff": is_staff},
    )


def kontak(request):
    info = Kontak.objects.first()
    return render(request, "konten/kontak.html", {"info": info})
