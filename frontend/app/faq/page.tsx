import Nav from "../components/Nav";
import Footer from "../components/Footer";

const faqs = [
  {
    section: "Tentang Ergon",
    items: [
      {
        q: "Apa itu Ergon?",
        a: "Ergon adalah alat analisis kecocokan CV berbasis AI. Kamu cukup memasukkan link atau upload file loker beserta CV-mu, dan Ergon akan memberikan skor kecocokan lengkap beserta saran perbaikan yang spesifik dan actionable.",
      },
      {
        q: "Siapa yang cocok menggunakan Ergon?",
        a: "Ergon cocok untuk siapa saja yang sedang aktif melamar kerja atau magang — mulai dari fresh graduate, mahasiswa tingkat akhir, hingga profesional yang ingin pindah industri.",
      },
      {
        q: "Apakah Ergon menjamin lamaran saya diterima?",
        a: "Tidak. Skor kecocokan Ergon adalah estimasi berbasis analisis teks, bukan jaminan hasil rekrutmen. Keputusan akhir tetap ada di tangan rekruter. Ergon membantu kamu memaksimalkan potensi CV sebelum dikirim.",
      },
    ],
  },
  {
    section: "Cara Kerja",
    items: [
      {
        q: "Bagaimana cara Ergon menghitung skor kecocokan?",
        a: "Ergon menganalisis beberapa dimensi: kecocokan keyword dan skill (30%), kemiripan semantik pengalaman (25%), kesesuaian level seniority (15%), relevansi portofolio (15%), kelengkapan CV (5%), dan sinyal kompetisi (10%). Setiap dimensi diberi bobot dan digabungkan menjadi satu skor akhir.",
      },
      {
        q: "Berapa lama proses analisis berlangsung?",
        a: "Biasanya 15–60 detik, tergantung kompleksitas loker dan CV yang diunggah. Kamu bisa memantau progres analisis secara real-time di halaman hasil.",
      },
      {
        q: "Format file apa yang didukung?",
        a: "Ergon mendukung upload CV dalam format PDF. Untuk loker, kamu bisa memasukkan URL halaman loker, upload PDF job description, atau screenshot loker dalam format PNG, JPG, atau WEBP.",
      },
      {
        q: "Apakah saya perlu membuat akun untuk menggunakan Ergon?",
        a: "Tidak perlu. Kamu bisa langsung upload dan mendapatkan skor kecocokan serta 3 saran teratas tanpa mendaftar sama sekali.",
      },
    ],
  },
  {
    section: "Harga & Pembayaran",
    items: [
      {
        q: "Apa yang bisa saya dapatkan secara gratis?",
        a: "Secara gratis kamu mendapatkan: skor kecocokan keseluruhan, breakdown skor per kategori, dan 3 saran perbaikan CV yang paling berdampak.",
      },
      {
        q: "Apa yang ada di versi berbayar?",
        a: "Dengan membayar Rp 25.000 sekali untuk satu loker, kamu mendapatkan semua saran perbaikan (bukan hanya 3 teratas), estimasi dampak per saran terhadap skor, laporan lengkap hasil analisis dalam format PDF, dan konteks spesifik perusahaan.",
      },
      {
        q: "Apakah pembayaran berlangganan?",
        a: "Tidak. Pembayaran dilakukan sekali per loker. Kamu hanya bayar untuk loker yang ingin kamu buka laporan lengkapnya.",
      },
      {
        q: "Metode pembayaran apa yang tersedia?",
        a: "Pembayaran diproses melalui Midtrans dan mendukung transfer bank (BCA, Mandiri, BNI, BRI), QRIS, GoPay, OVO, ShopeePay, dan kartu kredit/debit.",
      },
      {
        q: "Bagaimana jika pembayaran saya gagal atau tidak terverifikasi?",
        a: "Jika terjadi masalah verifikasi pembayaran, sistem akan otomatis mencoba beberapa kali. Jika masih gagal, hubungi kami melalui halaman Hubungi Kami dengan menyertakan order ID transaksimu.",
      },
    ],
  },
  {
    section: "Privasi & Data",
    items: [
      {
        q: "Apakah data CV saya aman?",
        a: "Ya. Data CV dan loker yang kamu upload hanya digunakan untuk keperluan analisis sesi tersebut. Data tidak dibagikan ke pihak ketiga, tidak digunakan untuk melatih model AI, dan dapat dihapus kapan saja.",
      },
      {
        q: "Berapa lama data saya disimpan?",
        a: "Data sesi disimpan selama 30 hari sejak terakhir diakses, kemudian dihapus otomatis. Kamu juga bisa meminta penghapusan data lebih awal melalui halaman Hubungi Kami.",
      },
    ],
  },
];

export default function FAQPage() {
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
        <div style={{
          position: "absolute", top: 20, right: -80,
          width: 280, height: 280, borderRadius: "50%",
          background: "radial-gradient(circle, #bfdbfe 0%, transparent 70%)",
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
            <span style={{ fontSize: "0.78rem", fontWeight: 600, color: "#134E8A", letterSpacing: "0.03em" }}>Dukungan</span>
          </div>
          <h1 style={{ fontSize: "2rem", fontWeight: 800, color: "#0F2A4A", letterSpacing: "-0.03em", marginBottom: 10 }}>
            Pertanyaan yang Sering Diajukan
          </h1>
          <p style={{ fontSize: "0.97rem", color: "#3A5878", lineHeight: 1.65 }}>
            Tidak menemukan jawaban yang kamu cari?{" "}
            <a href="/contact" style={{ color: "#1d4ed8", fontWeight: 600 }}>Hubungi kami</a> langsung.
          </p>
        </div>
      </div>

      <div style={{ maxWidth: 760, margin: "0 auto", padding: "8px 32px 88px" }}>
        {/* FAQ sections */}
        <div style={{ display: "flex", flexDirection: "column", gap: 40 }}>
          {faqs.map((section) => (
            <div key={section.section}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
                <div style={{
                  height: 1, flex: 1,
                  background: "linear-gradient(90deg, #bfdbfe, transparent)",
                }} />
                <span style={{
                  fontSize: "0.72rem", fontWeight: 700, color: "#1d4ed8",
                  textTransform: "uppercase", letterSpacing: "0.08em",
                  background: "linear-gradient(135deg, #eff6ff, #dbeafe)",
                  padding: "4px 14px", borderRadius: 20, border: "1px solid #bfdbfe",
                }}>
                  {section.section}
                </span>
                <div style={{ height: 1, flex: 1, background: "linear-gradient(90deg, transparent, #bfdbfe)" }} />
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
                {section.items.map((item, i) => (
                  <details key={i} style={{
                    background: "#fff",
                    border: "1.5px solid #e0eefb",
                    borderRadius: 14,
                    overflow: "hidden",
                    boxShadow: "0 1px 4px rgba(15,42,74,0.04)",
                  }}>
                    <summary style={{
                      padding: "16px 20px",
                      fontSize: "0.93rem", fontWeight: 600,
                      color: "#0F2A4A", cursor: "pointer",
                      listStyle: "none",
                      display: "flex", justifyContent: "space-between", alignItems: "center",
                      userSelect: "none",
                    }}>
                      {item.q}
                      <div style={{
                        width: 24, height: 24, borderRadius: "50%", flexShrink: 0, marginLeft: 12,
                        background: "#eff6ff", border: "1px solid #bfdbfe",
                        display: "flex", alignItems: "center", justifyContent: "center",
                      }}>
                        <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
                          <path d="M4 6L8 10L12 6" stroke="#1d4ed8" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      </div>
                    </summary>
                    <div style={{
                      padding: "14px 20px 18px",
                      fontSize: "0.9rem", color: "#3A5878",
                      lineHeight: 1.7,
                      borderTop: "1px solid #e0eefb",
                      background: "#f8fbff",
                    }}>
                      {item.a}
                    </div>
                  </details>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div style={{
          marginTop: 56,
          background: "linear-gradient(145deg, #0F2A4A, #1a3a5c)",
          borderRadius: 20, padding: "36px 40px",
          textAlign: "center", position: "relative", overflow: "hidden",
        }}>
          <div style={{
            position: "absolute", top: -40, right: -40,
            width: 200, height: 200, borderRadius: "50%",
            background: "radial-gradient(circle, rgba(59,130,246,0.2) 0%, transparent 70%)",
            pointerEvents: "none",
          }} />
          <h3 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#fff", marginBottom: 8, position: "relative" }}>
            Masih ada pertanyaan?
          </h3>
          <p style={{ fontSize: "0.9rem", color: "rgba(255,255,255,0.6)", marginBottom: 24, position: "relative" }}>
            Tim kami siap membantu kamu melalui email.
          </p>
          <a href="/contact" style={{
            display: "inline-block", position: "relative",
            background: "linear-gradient(135deg, #1d4ed8, #3b82f6)",
            color: "#fff", padding: "12px 28px", borderRadius: 12,
            fontWeight: 600, fontSize: "0.93rem",
            boxShadow: "0 4px 16px rgba(59,130,246,0.4)",
          }}>
            Hubungi kami →
          </a>
        </div>
      </div>

      <Footer />
    </div>
  );
}
