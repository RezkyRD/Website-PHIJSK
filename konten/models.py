from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class UnitKerja(models.Model):
    """6 unit di bawah Ditjen PHI dan Jamsos: Sesditjen, Direktorat HKP, dst."""

    nama = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    singkatan = models.CharField(max_length=30, help_text="Contoh: HKP, KPPHI, PPHI, BMHI")
    urutan = models.PositiveIntegerField(
        default=0, help_text="Urutan tampil di bagan struktur beranda"
    )

    # Tab: BERANDA (unit)
    deskripsi_beranda = models.TextField(
        blank=True, help_text="Ringkasan yang tampil di tab Beranda unit ini"
    )

    # Tab: TUSI
    tusi = models.TextField("Tugas dan Fungsi", blank=True)

    # Tab: STRUKTUR ORGANISASI
    struktur_organisasi_gambar = models.ImageField(
        upload_to="struktur_organisasi/", blank=True, null=True
    )
    struktur_organisasi_keterangan = models.TextField(
        blank=True, help_text="Teks pelengkap/daftar jabatan (opsional)"
    )

    class Meta:
        verbose_name = "Unit Kerja"
        verbose_name_plural = "Unit Kerja"
        ordering = ["urutan", "nama"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nama)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nama


class Berita(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Terbit"),
    ]

    unit_kerja = models.ForeignKey(
        UnitKerja, on_delete=models.CASCADE, related_name="berita_list"
    )
    judul = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    isi = models.TextField()
    gambar = models.ImageField(upload_to="berita/", blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    penulis = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    tanggal_publish = models.DateTimeField(auto_now_add=True)
    tanggal_update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Berita"
        verbose_name_plural = "Berita"
        ordering = ["-tanggal_publish"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.judul)[:200]
            slug = base
            i = 1
            while Berita.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.judul


class Kontak(models.Model):
    """Satu baris saja — informasi kontak Ditjen yang tampil di halaman Kontak."""

    alamat = models.TextField()
    telepon = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    jam_operasional = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Kontak"
        verbose_name_plural = "Kontak"

    def __str__(self):
        return "Informasi Kontak Ditjen PHI dan Jamsos"


class UnitAdminProfile(models.Model):
    """Menghubungkan akun admin ke SATU unit kerja — dasar hak akses per direktorat."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="unit_profile")
    unit_kerja = models.ForeignKey(
        UnitKerja, on_delete=models.CASCADE, related_name="admin_profiles"
    )

    class Meta:
        verbose_name = "Profil Admin Unit"
        verbose_name_plural = "Profil Admin Unit"

    def __str__(self):
        return f"{self.user.username} -> {self.unit_kerja.nama}"
