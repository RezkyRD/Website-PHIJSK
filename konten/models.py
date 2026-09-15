from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class UnitKerja(models.Model):
    """6 unit di bawah Ditjen PHI dan Jamsos: Sesditjen, Direktorat HKP, dst."""

    nama = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    singkatan = models.CharField(max_length=30, help_text="Contoh: HKP, KPPHI, PPHI, BMHI")
    nama_pejabat = models.CharField(
        max_length=150, blank=True, help_text="Nama pejabat yang menjabat (tampil di bagan struktur beranda)"
    )
    jabatan = models.CharField(
        max_length=100, blank=True, help_text="Contoh: Sekretaris Ditjen PHI-JSK, Direktur Bina Mediator..."
    )
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

    def tim_kerja_utama(self):
        """Daftar Ketua Tim Kerja (level atas) beserta Wakil Ketua di bawahnya masing-masing."""
        return self.tim_kerja_list.filter(induk__isnull=True).prefetch_related("anggota")


class TimKerja(models.Model):
    """
    Struktur tim kerja internal per unit — 2 level pakai relasi ke diri sendiri:
    - induk kosong -> ini "Ketua Tim Kerja" (level atas)
    - induk terisi -> ini "Wakil Ketua Tim Kerja", anak dari salah satu baris di atas
    Digambar sebagai bagan (bukan gambar statis) di tab Beranda unit, dan bisa diedit
    langsung di halaman admin Unit Kerja (inline) tanpa perlu bikin ulang gambar PowerPoint.
    """

    unit_kerja = models.ForeignKey(UnitKerja, on_delete=models.CASCADE, related_name="tim_kerja_list")
    induk = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="anggota",
        help_text="Kosongkan untuk Ketua Tim Kerja. Isi (pilih Ketua Tim Kerja yang sesuai) untuk Wakil Ketua.",
    )
    label = models.CharField(
        max_length=255,
        help_text="Contoh: 'Ketua Tim Kerja pembinaan hubungan kerja' atau 'wakil ketua Tim Kerja bidang ...'",
    )
    urutan = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Tim Kerja"
        verbose_name_plural = "Tim Kerja"
        ordering = ["urutan", "id"]

    def __str__(self):
        return f"{self.unit_kerja.singkatan} — {self.label}"


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

    instagram = models.URLField(blank=True, help_text="Link lengkap, contoh: https://instagram.com/kemnaker")
    facebook = models.URLField(blank=True, help_text="Link lengkap, contoh: https://facebook.com/kemnaker")
    twitter_x = models.URLField("X (Twitter)", blank=True, help_text="Link lengkap, contoh: https://x.com/kemnaker")
    youtube = models.URLField(blank=True, help_text="Link lengkap, contoh: https://youtube.com/@kemnaker")
    tiktok = models.URLField(blank=True, help_text="Link lengkap, contoh: https://tiktok.com/@kemnaker")
    whatsapp_group = models.URLField("Channel WhatsApp", blank=True, help_text="Link undangan channel, contoh: https://whatsapp.com/channel/xxxxxxxxxxxxx")

    class Meta:
        verbose_name = "Kontak"
        verbose_name_plural = "Kontak"

    def __str__(self):
        return "Informasi Kontak Ditjen PHI dan Jamsos"

    def sosmed_items(self):
        """Daftar sosmed yang terisi saja, masing-masing dengan label & warna brand untuk tombol di halaman Kontak."""
        brands = [
            ("instagram", self.instagram, "Instagram", "#E1306C"),
            ("facebook", self.facebook, "Facebook", "#1877F2"),
            ("twitter_x", self.twitter_x, "X (Twitter)", "#000000"),
            ("youtube", self.youtube, "YouTube", "#FF0000"),
            ("tiktok", self.tiktok, "TikTok", "#000000"),
            ("whatsapp_group", self.whatsapp_group, "Channel WhatsApp", "#25D366"),
        ]
        return [
            {"key": key, "url": url, "label": label, "color": color}
            for key, url, label, color in brands if url
        ]


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


class ProfilDitjen(models.Model):
    """Satu baris saja — teks definisi & tupoksi Ditjen yang tampil di panel beranda."""

    nama_dirjen = models.CharField(
        max_length=150, blank=True, help_text="Nama pejabat Direktur Jenderal (tampil di puncak bagan)"
    )
    paragraf_1 = models.TextField(
        blank=True, help_text="Paragraf definisi Ditjen (kalimat pertama panel beranda)"
    )
    paragraf_2 = models.TextField(
        blank=True, help_text="Paragraf kedua (tentang kepemimpinan Ditjen)"
    )
    tupoksi_pembuka = models.CharField(
        max_length=300, blank=True,
        help_text="Kalimat pembuka sebelum daftar poin, contoh: '...menyelenggarakan fungsi:'",
    )
    tupoksi_a = models.TextField("Tupoksi — poin a", blank=True)
    tupoksi_b = models.TextField("Tupoksi — poin b", blank=True)
    tupoksi_c = models.TextField("Tupoksi — poin c", blank=True)
    tupoksi_d = models.TextField("Tupoksi — poin d", blank=True)
    tupoksi_e = models.TextField("Tupoksi — poin e", blank=True)
    tupoksi_f = models.TextField("Tupoksi — poin f", blank=True)
    tupoksi_g = models.TextField("Tupoksi — poin g", blank=True)

    class Meta:
        verbose_name = "Profil Ditjen"
        verbose_name_plural = "Profil Ditjen"

    def __str__(self):
        return "Profil Ditjen PHI dan Jamsos (Beranda)"

    def tupoksi_items(self):
        """Daftar poin tupoksi yang terisi, masing-masing sudah punya huruf (a, b, c, ...) sendiri.
        Setiap poin tersimpan di field terpisah, jadi tidak bisa tercampur akibat editan admin."""
        judul_singkat = {
            "a": "Perumusan kebijakan",
            "b": "Pelaksanaan kebijakan",
            "c": "Penyusunan norma, standar, prosedur dan kriteria",
            "d": "Pemberian bimbingan teknis dan supervisi",
            "e": "Pelaksanaan evaluasi dan pelaporan",
            "f": "Pelaksanaan administrasi",
            "g": "Pelaksanaan fungsi lain yang diberikan oleh Menteri",
        }
        items = []
        for huruf in "abcdefg":
            isi = getattr(self, f"tupoksi_{huruf}")
            if isi:
                items.append({"letter": huruf, "title": judul_singkat[huruf], "full": isi})
        return items
