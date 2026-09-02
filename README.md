# Website Ditjen PHI dan Jamsos (Prototipe)

Website profil kelembagaan Direktorat Jenderal PHI dan Jamsos, mengikuti pola
laman resmi Kemnaker (kemnaker.go.id/unit/phi-jsk). Dibangun dengan Django —
konten dikelola lewat admin panel bawaan, dengan hak akses terpisah per
direktorat.

## Struktur

- **Beranda** — bagan 6 unit kerja, klik untuk masuk ke halaman unit
- **Halaman Unit Kerja** — 4 tab: Beranda, Berita, Tusi, Struktur Organisasi
- **Kontak** — informasi kontak Ditjen
- **Admin (`/admin/`)** — superadmin kelola semua unit; admin direktorat hanya
  kelola unitnya sendiri (Berita, Tusi, Struktur Organisasi)

## Menjalankan secara lokal

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py loaddata unit_kerja_awal    # isi 6 unit kerja awal
python manage.py createsuperuser             # buat akun superadmin Anda

python manage.py runserver
```

Buka `http://localhost:8000/` untuk situs publik, dan `http://localhost:8000/admin/`
untuk panel admin.

> **Catatan:** Nama lengkap 6 direktorat pada `konten/fixtures/unit_kerja_awal.json`
> saya susun berdasarkan singkatan yang ada di rancangan (HKP, KPPHI, PPHI, BMHI,
> Jamsostek dan Faskesja) — mohon dicek dan disesuaikan dengan nomenklatur resmi
> Permenaker sebelum dipakai, karena saya tidak memverifikasinya ke sumber resmi.

## Membuat akun admin per direktorat

Setelah login sebagai superadmin:

1. Buka **Admin → Users** → buat user baru untuk admin direktorat (jangan centang "superuser")
2. Buka **Admin → Profil Admin Unit** → tambah baris baru, hubungkan user tersebut ke satu Unit Kerja
3. User itu sekarang login dan hanya melihat/mengedit Berita, Tusi, dan Struktur Organisasi milik unitnya sendiri

## Struktur folder

```
config/          # pengaturan proyek Django (settings, urls)
konten/          # app utama: models, admin, views, templates
  models.py      # UnitKerja, Berita, Kontak, UnitAdminProfile
  admin.py       # panel admin + logika hak akses per unit
  views.py       # halaman publik
  templates/
  fixtures/      # data awal 6 unit kerja
```

## Deploy ke Railway atau Render (gratis, untuk prototipe)

### Railway
1. Push folder ini ke repository GitHub
2. Buat proyek baru di Railway → "Deploy from GitHub repo"
3. Tambahkan plugin **PostgreSQL** dari Railway — `DATABASE_URL` otomatis terisi
4. Di tab **Variables**, tambahkan `DJANGO_SECRET_KEY` (nilai acak) dan `DJANGO_DEBUG=False`
5. Railway akan menjalankan `Procfile` otomatis (migrate lalu start gunicorn)
6. Setelah deploy pertama, jalankan sekali lewat Railway shell/CLI:
   `python manage.py createsuperuser` dan `python manage.py loaddata unit_kerja_awal`

### Render
1. Push ke GitHub, buat **Web Service** baru di Render, hubungkan repo
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn config.wsgi --bind 0.0.0.0:$PORT`
4. Tambahkan **PostgreSQL** dari Render (gratis, terbatas) — salin connection string ke env var `DATABASE_URL`
5. Set env var `DJANGO_SECRET_KEY` dan `DJANGO_DEBUG=False`
6. Jalankan migrate + createsuperuser sekali lewat Render Shell

## Yang masih perlu diputuskan sebelum jadi situs resmi

- Domain resmi dan hosting sesuai aturan pengadaan pemerintah (bukan tier gratis Railway/Render)
- Verifikasi nomenklatur resmi 6 direktorat ke Permenaker/SOTK terbaru
- Kebijakan retensi data & backup database (SQLite di prototipe ini tidak persisten kalau di-redeploy tanpa volume/Postgres)
- Review keamanan lebih lanjut sebelum publik (rate limiting, captcha di form kalau ada, dsb.)
