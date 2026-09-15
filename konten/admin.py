from django.contrib import admin
from .models import UnitKerja, Berita, Kontak, UnitAdminProfile, ProfilDitjen, TimKerja


def get_user_unit(user):
    """Kembalikan UnitKerja milik admin ini, atau None kalau superuser/tidak terikat unit."""
    profile = getattr(user, "unit_profile", None)
    return profile.unit_kerja if profile else None


class UnitScopedAdminMixin:
    """
    Mixin hak akses per direktorat:
    - Superuser -> lihat & kelola semua unit.
    - Admin unit -> hanya lihat & kelola objek milik unitnya sendiri.
    Dipakai di ModelAdmin manapun yang objeknya terhubung ke UnitKerja
    (langsung, atau via field 'unit_kerja').
    """

    def _unit_of(self, obj):
        if isinstance(obj, UnitKerja):
            return obj
        return getattr(obj, "unit_kerja", None)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        unit = get_user_unit(request.user)
        if unit is None:
            return qs.none()
        if self.model is UnitKerja:
            return qs.filter(pk=unit.pk)
        return qs.filter(unit_kerja=unit)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or obj is None:
            return super().has_change_permission(request, obj)
        return self._unit_of(obj) == get_user_unit(request.user)

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or obj is None:
            return super().has_delete_permission(request, obj)
        return self._unit_of(obj) == get_user_unit(request.user)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        # admin unit boleh menambah konten (mis. Berita) untuk unitnya sendiri
        return get_user_unit(request.user) is not None

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and hasattr(obj, "unit_kerja_id"):
            obj.unit_kerja = get_user_unit(request.user)
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Admin unit tidak boleh memilih unit lain lewat dropdown
        if db_field.name == "unit_kerja" and not request.user.is_superuser:
            unit = get_user_unit(request.user)
            kwargs["queryset"] = UnitKerja.objects.filter(pk=unit.pk) if unit else UnitKerja.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class TimKerjaInline(admin.TabularInline):
    """
    Diisi langsung di halaman edit Unit Kerja. Untuk baris Ketua Tim Kerja, biarkan
    'Induk' kosong. Untuk Wakil Ketua, pilih Ketua Tim Kerja terkait di kolom 'Induk'.
    """
    model = TimKerja
    fk_name = "unit_kerja"
    extra = 1
    fields = ("label", "induk", "urutan")
    verbose_name = "Tim Kerja"
    verbose_name_plural = "Tim Kerja (Ketua & Wakil Ketua)"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Batasi pilihan "Induk" hanya ke Tim Kerja level-atas milik unit yang sama
        if db_field.name == "induk":
            parent_id = request.resolver_match.kwargs.get("object_id")
            qs = TimKerja.objects.filter(induk__isnull=True)
            if parent_id:
                qs = qs.filter(unit_kerja_id=parent_id)
            kwargs["queryset"] = qs
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(UnitKerja)
class UnitKerjaAdmin(UnitScopedAdminMixin, admin.ModelAdmin):
    list_display = ("nama", "singkatan", "nama_pejabat", "urutan")
    prepopulated_fields = {"slug": ("nama",)}
    fieldsets = (
        (None, {"fields": ("nama", "slug", "singkatan", "urutan")}),
        ("Bagan struktur (beranda Ditjen)", {"fields": ("nama_pejabat", "jabatan")}),
        ("Tab Beranda Unit (Tusi & Struktur)", {
            "fields": ("deskripsi_beranda", "tusi", "struktur_organisasi_gambar", "struktur_organisasi_keterangan"),
            "description": "Gambar & keterangan di sini cuma dipakai kalau daftar Tim Kerja di bawah masih kosong — "
                           "begitu ada Tim Kerja, bagan otomatis dibuat dari data itu, gambar tidak dipakai lagi.",
        }),
    )
    inlines = [TimKerjaInline]

    def has_add_permission(self, request):
        # Hanya superuser yang boleh menambah/menghapus unit baru (struktur ditjen)
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Berita)
class BeritaAdmin(UnitScopedAdminMixin, admin.ModelAdmin):
    list_display = ("judul", "unit_kerja", "status", "tanggal_publish")
    list_filter = ("status", "unit_kerja")
    search_fields = ("judul", "isi")
    prepopulated_fields = {"slug": ("judul",)}

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.penulis_id:
            obj.penulis = request.user
        super().save_model(request, obj, form, change)


@admin.register(Kontak)
class KontakAdmin(admin.ModelAdmin):
    # Kontak Ditjen: hanya superuser yang mengelola (informasi terpusat, bukan per unit)
    fieldsets = (
        ("Informasi Kontak", {"fields": ("alamat", "telepon", "email", "jam_operasional")}),
        ("Media Sosial (kosongkan yang tidak dipakai)", {
            "fields": ("instagram", "facebook", "twitter_x", "youtube", "tiktok", "whatsapp_group"),
            "description": "Isi dengan link lengkap (termasuk https://). Yang kosong tidak akan tampil di halaman Kontak.",
        }),
    )

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_add_permission(self, request):
        # cegah lebih dari satu baris kontak
        return request.user.is_superuser and not Kontak.objects.exists()


@admin.register(UnitAdminProfile)
class UnitAdminProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "unit_kerja")

    def has_module_permission(self, request):
        return request.user.is_superuser


@admin.register(ProfilDitjen)
class ProfilDitjenAdmin(admin.ModelAdmin):
    # Teks definisi & tupoksi Ditjen: hanya superuser yang mengelola (konten level-Ditjen, bukan per unit)
    fieldsets = (
        ("Panel pembuka beranda", {"fields": ("nama_dirjen", "paragraf_1", "paragraf_2")}),
        ("Tupoksi — kalimat pembuka", {"fields": ("tupoksi_pembuka",)}),
        ("Tupoksi — isi tiap poin (kosongkan yang tidak dipakai)", {
            "fields": ("tupoksi_a", "tupoksi_b", "tupoksi_c", "tupoksi_d", "tupoksi_e", "tupoksi_f", "tupoksi_g"),
            "description": "Setiap poin (a-g) tampil sebagai akordion terpisah di beranda. "
                           "Tulis teks lengkapnya di sini tanpa perlu awalan huruf — huruf ditambahkan otomatis.",
        }),
    )

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_add_permission(self, request):
        # cegah lebih dari satu baris profil
        return request.user.is_superuser and not ProfilDitjen.objects.exists()
