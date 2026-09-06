# PRD — Ergon
**AI CV-Fit Scorer & Enhancer untuk Jobseeker**

| | |
|---|---|
| Status | Draft v1 — Full scope (hackathon submission) |
| Tanggal | 6 September 2026 |
| Tech stack wajib | IBM Bob (dev agent), IBM Langflow (orchestrator), MCP (integrasi Bob↔Langflow & Langflow↔tools) |

---

## 1. Ringkasan Produk

Ergon adalah web app yang membaca sebuah lowongan kerja (link/PDF/gambar) beserta CV dan portofolio pengguna, lalu memberi **skor kecocokan** yang bisa dijelaskan (bukan angka ajaib) plus **saran perbaikan CV yang bisa langsung dipakai** — bukan template generik. Model bisnisnya freemium: skor dan 3 saran teratas gratis, sisanya + CV hasil revisi berbayar. Fitur latihan wawancara AI berbasis suara direncanakan sebagai tier premium, dirilis sebagai **"Coming Soon"** pada versi ini.

## 2. Latar Belakang & Masalah

Jobseeker biasanya melamar dengan satu CV generik ke banyak loker tanpa tahu seberapa cocok CV-nya dengan syarat spesifik tiap loker, dan tidak dapat umpan balik konkret kenapa lamaran mereka sering tidak lanjut ke tahap wawancara. Tools CV-checker yang ada kebanyakan hanya cek format/keyword secara dangkal dan tidak mempertimbangkan konteks perusahaan atau portofolio nyata pelamar.

## 3. Tujuan Produk & Metrik Sukses

**Tujuan:**
- Memberi jobseeker gambaran objektif kecocokan CV-nya terhadap loker tertentu, lengkap dengan alasan yang bisa ditindaklanjuti.
- Mengonversi insight tersebut menjadi CV yang sudah diperbaiki dan siap dikirim.
- Membangun jalur monetisasi yang jelas dari fitur analisis ke fitur revisi ke fitur latihan wawancara.

**Metrik keberhasilan (untuk versi pasca-hackathon):**
- % pengguna yang menyelesaikan alur upload → skor keluar (completion rate).
- % pengguna free yang convert ke unlock berbayar.
- Rata-rata kenaikan skor kecocokan setelah CV direvisi (proxy kualitas saran).
- Waktu proses end-to-end dari upload sampai skor tampil (target < 60 detik untuk teks, < 90 detik kalau ada OCR gambar/PDF).

**Kriteria sukses untuk submission hackathon:**
- Bob terbukti dipakai membangun/mengedit flow Langflow via MCP (bukan cuma drag-drop manual).
- Minimal seluruh flow inti (job extraction → parsing CV/portofolio → scoring → suggestion → enhancement) berjalan end-to-end dan bisa didemokan live.
- Fitur interview tampil di UI sebagai "Coming Soon" dengan alasan/konteks yang jelas, tidak sekadar hilang dari produk.

## 4. Target Pengguna

**Persona utama — "Jobseeker Aktif":** fresh graduate hingga mid-level profesional yang aktif melamar ke banyak loker dalam waktu bersamaan, ingin tahu prioritas loker mana yang realistis untuk dikejar, dan ingin CV-nya disesuaikan cepat tanpa menulis ulang dari nol tiap kali melamar.

**Persona sekunder — "Career switcher":** orang yang pindah bidang/industri, butuh bantuan ekstra untuk mengetahui gap skill dan cara memframing pengalaman lama supaya relevan ke loker baru.

## 5. Ruang Lingkup (Full Scope — tidak dipecah jadi MVP)

Semua modul berikut dibangun sekaligus di rilis ini:

| Modul | Termasuk di rilis ini |
|---|---|
| Upload & parsing loker (link/PDF/gambar) | ✅ |
| Riset kontekstual perusahaan (opsional per loker) | ✅ |
| Parsing CV & portofolio (semua tipe file/link) | ✅ |
| Scoring kecocokan + breakdown | ✅ |
| 3 saran perbaikan gratis | ✅ |
| Unlock semua saran + download CV hasil revisi (berbayar) | ✅ |
| Landing page & identitas visual | ✅ |
| Latihan wawancara AI voice | ✅ ditampilkan di UI, berstatus **Coming Soon** (belum bisa dipakai) |

**Di luar scope rilis ini:** pembayaran multi-currency, integrasi ATS pihak ketiga, mobile app native, multi-bahasa selain Indonesia/Inggris.

## 6. User Flow

```
[Landing Page]
     ↓ klik "Coba gratis"
[Form Upload] — loker (link/PDF/gambar) + CV (PDF/link) + portofolio (file/link)
     ↓
[Loading state] — job extraction, company intel, cv/portfolio parsing berjalan paralel
     ↓
[Dashboard Hasil]
   ├─ Skor kecocokan + breakdown per kategori
   ├─ 3 saran perbaikan (terbuka, gratis)
   ├─ Saran selanjutnya (terkunci/blur) → CTA "Buka versi lengkap"
   └─ Banner "Latihan wawancara AI — Segera hadir" (non-interaktif)
     ↓ (jika bayar)
[Unlocked View]
   ├─ Semua saran perbaikan terbuka
   └─ Tombol "Unduh CV hasil revisi" (PDF/DOCX)
```

## 7. Requirement Fungsional per Modul

### 7.1 Upload & Job Extraction
- Pengguna bisa memasukkan loker dalam 3 bentuk: link, upload PDF, upload gambar (screenshot).
- Sistem mengekstrak: nama perusahaan, posisi, seniority, requirement hard/soft skill, tanggung jawab, lokasi, rentang gaji (jika ada), deadline, jumlah pelamar & kuota (opsional, best-effort).
- Jika ekstraksi gagal/data tidak lengkap, sistem menampilkan field yang berhasil didapat dan menandai field yang tidak ditemukan — bukan gagal total.

### 7.2 Company Intelligence (opsional per loker)
- Sistem mencari berita/produk terbaru perusahaan terkait untuk memperkaya konteks saran CV dan (nanti) bahan pertanyaan wawancara.
- Bersifat best-effort; jika tidak ada informasi relevan, bagian ini disembunyikan dari hasil, bukan ditampilkan kosong.

### 7.3 CV & Portfolio Parsing
- Menerima CV dalam PDF atau link (Google Docs dsb).
- Menerima portofolio dalam format apa pun (PDF, gambar, link GitHub/Behance/situs pribadi).
- Output: struktur riwayat kerja, pendidikan, skill, achievement (dengan flag "belum terkuantifikasi" bila relevan), dan daftar proyek portofolio dengan relevansinya ke loker.

### 7.4 Scoring & Breakdown
- Skor kecocokan komposit dari: kecocokan keyword/skill, kecocokan semantik pengalaman, kesesuaian level, relevansi portofolio, dan (jika data tersedia) sinyal kompetisi.
- Ditampilkan sebagai rentang kualitatif + breakdown per kategori, bukan angka presisi tunggal, disertai disclaimer bahwa ini estimasi, bukan jaminan hasil rekrutmen.

### 7.5 Saran Perbaikan & Paywall
- Sistem menghasilkan daftar saran, diranking berdasarkan estimasi dampak ke skor.
- 3 saran berdampak terbesar ditampilkan penuh secara gratis.
- Saran lain ditampilkan sebagai judul + preview terkunci (blur), detail hanya muncul setelah unlock.
- Setelah unlock: pengguna bisa memilih saran mana yang diterapkan, lalu generate & unduh CV hasil revisi (PDF/DOCX).

### 7.6 Latihan Wawancara AI (Coming Soon)
- Ditampilkan sebagai bagian tetap dari produk (bukan disembunyikan), berlabel "Segera hadir", non-klikable, dengan deskripsi singkat apa yang akan didapat pengguna nanti (voice, real-time, memakai konteks loker+CV+skor yang sudah ada).
- Tidak ada backend real-time voice yang perlu berfungsi pada rilis ini.

## 8. Requirement Non-Fungsional

- **Privasi data:** CV, portofolio, dan hasil ekstraksi loker adalah data pribadi; wajib dienkripsi saat disimpan, dan pengguna bisa menghapus datanya.
- **Keandalan ekstraksi:** setiap tahap ekstraksi (loker/CV/portofolio) harus punya fallback ketika parsing gagal sebagian, tidak boleh membuat seluruh alur gagal total.
- **Kejujuran klaim:** semua istilah terkait skor harus dibingkai sebagai estimasi/kecocokan, tidak boleh memakai kata "peluang diterima" atau sejenisnya yang terkesan menjamin hasil.
- **Kepatuhan scraping:** prioritaskan input dari upload pengguna sendiri (PDF/screenshot) dibanding scraping otomatis ke job board yang melarangnya di ToS.
- **Performa:** hasil skor tampil dalam waktu wajar (target di bagian metrik); tampilkan status progres per tahap selama diproses, jangan layar kosong.

## 9. Arsitektur & Tech Stack (ringkas — detail di dokumen arsitektur terpisah)

- **IBM Bob** — dev agent untuk membangun kode aplikasi *dan* untuk menyusun/mengedit flow Langflow secara terprogram lewat **Langflow MCP Client for coding agents**.
- **IBM Langflow** — orchestrator 6 flow inti: `job_extraction`, `company_intel`, `cv_portfolio_parsing`, `scoring_and_suggestions`, `cv_enhancement`, `interview_practice` (flow terakhir dibangun tapi belum dipasang ke UI produksi karena statusnya Coming Soon).
- **IBM watsonx.ai / Granite** — LLM & embedding backbone di dalam flow Langflow.
- **MCP servers** — `job-scraper-mcp`, `company-intel-mcp`, `resume-parser-mcp`, `portfolio-analyzer-mcp`, `scoring-engine-mcp`, `cv-generator-mcp`, `payment-mcp`, disiapkan sejak awal (lihat dokumen arsitektur untuk detail kontrak tiap tool).
- **Frontend** — Next.js/React, styling sesuai design system di bagian 10.

## 10. Desain & UX

- **Identitas visual:** lavender lembut (`#E7E3FC` / `#FBFAFF`) sebagai base, ungu (`#5B4FE5`) sebagai satu-satunya aksen kuat, ilustrasi line-art (bukan foto stok) untuk semua visual pendukung.
- **Tipografi:** Space Grotesk untuk headline, Inter untuk body/UI.
- **Prinsip UI paywall:** free vs berbayar dibedakan lewat treatment visual (panel terbuka vs panel gelap dengan baris terkunci/blur), bukan dua kartu identik.
- **Prinsip fitur belum tersedia:** elemen "Coming Soon" harus tetap terlihat di alur utama (bukan disembunyikan total) tapi divisualkan berbeda (border putus-putus, badge, non-interaktif) supaya tidak disalahartikan sebagai fitur yang sudah jalan.
- Referensi halaman yang sudah dibuat: landing page (`ergon-landing.html`).

**Halaman yang perlu dibangun:**
1. Landing page — *sudah dibuat*.
2. Form upload (loker + CV + portofolio).
3. Dashboard hasil (skor, breakdown, saran, banner coming soon).
4. Halaman unlock/paywall & konfirmasi pembayaran.
5. Halaman unduh CV hasil revisi.

## 11. Model Monetisasi

| Tier | Isi | Model harga |
|---|---|---|
| Free | Skor + breakdown penuh, 3 saran teratas | Gratis, tanpa batas jumlah loker |
| Unlock per-loker | Semua saran + download CV hasil revisi | Bayar sekali per analisis loker |
| Premium (Coming Soon) | Semua di atas + latihan wawancara AI voice | Akan diumumkan saat fitur rilis |

## 12. Risiko & Mitigasi

| Risiko | Mitigasi |
|---|---|
| Klaim skor disalahpahami sebagai jaminan diterima | Framing bahasa "estimasi kecocokan", selalu sertakan breakdown & disclaimer |
| Scraping job board melanggar ToS | Prioritaskan upload manual (PDF/screenshot) sebagai jalur utama |
| Data CV/portofolio sensitif | Enkripsi penyimpanan, opsi hapus data oleh pengguna |
| Fitur Coming Soon menimbulkan ekspektasi tanggal rilis yang tidak realistis | Deskripsi Coming Soon tidak mencantumkan tanggal pasti |
| Ekstraksi loker/CV gagal sebagian | Desain fallback: tampilkan field yang berhasil, tandai yang gagal, jangan block seluruh alur |

## 13. Asumsi

- Pengguna bersedia mengunggah CV & portofolio asli (bukan data anonim) demi hasil analisis yang akurat.
- Untuk demo hackathon, sumber loker yang diuji lebih diarahkan ke upload PDF/screenshot ketimbang scraping live ke job board besar, untuk menghindari masalah ToS saat demo.
- Model LLM (watsonx/Granite) tersedia dan dikonfigurasi sebagai global variable di Langflow sebelum flow dijalankan.

## 14. Lampiran

- Dokumen arsitektur & spesifikasi MCP server: *rancangan-cv-fit-ai.md* (percakapan sebelumnya).
- Spesifikasi 6 flow Langflow (job_extraction, company_intel, cv_portfolio_parsing, scoring_and_suggestions, cv_enhancement, interview_practice): lihat riwayat percakapan bagian rancangan Langflow.
- Landing page: *ergon-landing.html*.
