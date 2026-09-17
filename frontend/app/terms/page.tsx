import Nav from "../components/Nav";
import Footer from "../components/Footer";

export default function TermsPage() {
  const lastUpdated = "1 Juni 2026";

  const sections = [
    {
      title: "1. Penerimaan Syarat",
      content: `Dengan mengakses atau menggunakan layanan Ergon ("Layanan"), kamu menyetujui untuk terikat oleh Syarat & Ketentuan ini. Jika kamu tidak menyetujui salah satu bagian dari syarat ini, kamu tidak diizinkan menggunakan Layanan.

Layanan ini ditujukan untuk pengguna berusia 17 tahun ke atas.`,
    },
    {
      title: "2. Deskripsi Layanan",
      content: `Ergon adalah platform analisis kecocokan CV berbasis kecerdasan buatan. Layanan mencakup:

• Analisis skor kecocokan antara CV dan lowongan kerja
• Saran perbaikan CV yang dipersonalisasi
• Laporan lengkap hasil analisis (untuk pengguna berbayar)
• Akses ke konteks informasi perusahaan relevan

Ergon berhak mengubah, menambah, atau menghentikan fitur Layanan kapan saja tanpa pemberitahuan sebelumnya.`,
    },
    {
      title: "3. Penggunaan yang Diperbolehkan",
      content: `Kamu boleh menggunakan Layanan hanya untuk:

• Keperluan pribadi dalam rangka mencari pekerjaan atau magang
• Mengevaluasi kesesuaian CV kamu terhadap lowongan yang tersedia

Kamu **dilarang** untuk:

• Menggunakan Layanan untuk tujuan komersial atau resale tanpa izin tertulis
• Melakukan scraping, crawling, atau ekstraksi data sistematis dari Layanan
• Mengunggah konten yang melanggar hak cipta, berbahaya, atau menyesatkan
• Mencoba menembus, merusak, atau mengganggu sistem keamanan Layanan`,
    },
    {
      title: "4. Pembayaran & Pengembalian Dana",
      content: `**Biaya layanan:** Rp 25.000 per sesi analisis untuk membuka laporan lengkap. Harga dapat berubah sewaktu-waktu dan berlaku untuk sesi baru setelah perubahan.

**Tidak ada pengembalian dana** untuk pembelian yang telah berhasil diproses, kecuali:
• Terjadi kegagalan teknis di pihak Ergon yang menyebabkan laporan tidak dapat diakses
• Pembayaran berhasil tapi konten laporan tidak tersedia karena kesalahan sistem

Untuk klaim pengembalian dana, hubungi kami dalam **3 hari kerja** setelah transaksi dengan menyertakan order ID.`,
    },
    {
      title: "5. Konten & Hak Kekayaan Intelektual",
      content: `**Konten kamu:** CV, loker, dan portofolio yang kamu unggah tetap menjadi milikmu. Dengan menggunakan Layanan, kamu memberikan Ergon lisensi terbatas, non-eksklusif, untuk memproses konten tersebut semata-mata dalam rangka menyediakan Layanan.

**Konten Ergon:** Seluruh konten yang dihasilkan oleh Ergon — termasuk skor, saran, laporan, dan antarmuka pengguna — adalah milik Ergon dan dilindungi oleh hak cipta. Dilarang mereproduksi atau mendistribusikan konten tersebut tanpa izin tertulis.`,
    },
    {
      title: "6. Batasan Tanggung Jawab",
      content: `Ergon **tidak memberikan jaminan** bahwa:

• Skor kecocokan mencerminkan peluang aktual diterimanya lamaranmu
• Saran yang diberikan akan selalu menghasilkan perbaikan skor atau keberhasilan rekrutmen
• Layanan tersedia tanpa gangguan atau bebas dari kesalahan

Dalam batas yang diizinkan hukum yang berlaku, Ergon tidak bertanggung jawab atas kerugian tidak langsung, insidental, atau konsekuensial yang timbul dari penggunaan Layanan.`,
    },
    {
      title: "7. Perubahan Syarat",
      content: `Ergon berhak mengubah Syarat & Ketentuan ini kapan saja. Perubahan material akan diberitahukan melalui banner di situs minimal 7 hari sebelum berlaku. Melanjutkan penggunaan Layanan setelah perubahan berlaku berarti kamu menyetujui syarat yang diperbarui.`,
    },
    {
      title: "8. Hukum yang Berlaku",
      content: `Syarat & Ketentuan ini tunduk pada hukum yang berlaku di Republik Indonesia. Setiap sengketa yang timbul akan diselesaikan melalui mediasi terlebih dahulu, kemudian melalui pengadilan yang berwenang di Indonesia.`,
    },
    {
      title: "9. Hubungi Kami",
      content: `Pertanyaan mengenai Syarat & Ketentuan dapat dikirimkan ke: **halo@ergon.id** atau melalui halaman Hubungi Kami.`,
    },
  ];

  return (
    <div style={{ background: "#fff", minHeight: "100vh", overflowX: "hidden" }}>
      <Nav />

      {/* Page header */}
      <div style={{ position: "relative", overflow: "hidden", background: "#fff" }}>
        <div style={{
          position: "absolute", top: -80, left: -120,
          width: 440, height: 440, borderRadius: "50%",
          background: "radial-gradient(circle, #dbeafe 0%, #eff6ff 50%, transparent 72%)",
          zIndex: 0, pointerEvents: "none",
        }} />
        <div style={{ position: "relative", zIndex: 1, maxWidth: 760, margin: "0 auto", padding: "52px 32px 40px" }}>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 7,
            background: "linear-gradient(135deg, #eff6ff, #dbeafe)",
            borderRadius: 24, padding: "6px 16px", marginBottom: 20,
            border: "1px solid #bfdbfe",
          }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#1d4ed8", display: "inline-block" }} />
            <span style={{ fontSize: "0.78rem", fontWeight: 600, color: "#134E8A", letterSpacing: "0.03em" }}>Legal</span>
          </div>
          <h1 style={{ fontSize: "2rem", fontWeight: 800, color: "#0F2A4A", letterSpacing: "-0.03em", marginBottom: 10 }}>
            Syarat & Ketentuan
          </h1>
          <p style={{ fontSize: "0.86rem", color: "#94a3b8" }}>
            Terakhir diperbarui: {lastUpdated}
          </p>
        </div>
      </div>

      <div style={{ maxWidth: 760, margin: "0 auto", padding: "8px 32px 88px" }}>
        {/* Notice box */}
        <div style={{
          background: "linear-gradient(135deg, #eff6ff, #dbeafe)",
          border: "1px solid #bfdbfe", borderRadius: 14,
          padding: "16px 20px", marginBottom: 40,
          display: "flex", gap: 12, alignItems: "flex-start",
        }}>
          <div style={{
            width: 30, height: 30, borderRadius: 8, flexShrink: 0,
            background: "#fff", border: "1px solid #bfdbfe",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="6.5" stroke="#1d4ed8" strokeWidth="1.4"/>
              <path d="M8 5v4M8 11h.01" stroke="#1d4ed8" strokeWidth="1.4" strokeLinecap="round"/>
            </svg>
          </div>
          <p style={{ fontSize: "0.86rem", color: "#134E8A", lineHeight: 1.65 }}>
            Dengan menggunakan layanan Ergon, kamu menyetujui syarat dan ketentuan berikut. Baca dengan seksama sebelum melanjutkan.
          </p>
        </div>

        {/* Content */}
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          {sections.map((section) => (
            <div key={section.title} style={{
              background: "#fff", border: "1.5px solid #e0eefb",
              borderRadius: 16, padding: "24px 28px",
              boxShadow: "0 1px 6px rgba(15,42,74,0.04)",
            }}>
              <h2 style={{
                fontSize: "1rem", fontWeight: 700, color: "#0F2A4A",
                letterSpacing: "-0.01em", marginBottom: 12,
                display: "flex", alignItems: "center", gap: 10,
              }}>
                <span style={{
                  width: 6, height: 6, borderRadius: "50%",
                  background: "linear-gradient(135deg, #1d4ed8, #3b82f6)",
                  display: "inline-block", flexShrink: 0,
                }} />
                {section.title}
              </h2>
              <div style={{
                fontSize: "0.9rem", color: "#3A5878", lineHeight: 1.8,
                whiteSpace: "pre-line",
              }}>
                {section.content.split("**").map((part, i) =>
                  i % 2 === 1
                    ? <strong key={i} style={{ color: "#0F2A4A", fontWeight: 700 }}>{part}</strong>
                    : <span key={i}>{part}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <Footer />
    </div>
  );
}
