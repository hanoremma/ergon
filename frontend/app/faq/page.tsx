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
    <div style={{ background: "var(--bg-page)", minHeight: "100vh" }}>
      <Nav />

      <div style={{ maxWidth: 760, margin: "0 auto", padding: "52px 32px 88px" }}>
        {/* Header */}
        <div style={{ marginBottom: 48 }}>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 7,
            background: "var(--accent-soft)", borderRadius: 20,
            padding: "5px 14px", marginBottom: 16,
            border: "1px solid var(--line)",
          }}>
            <span style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--accent-deep)" }}>Dukungan</span>
          </div>
          <h1 style={{ fontSize: "2rem", fontWeight: 800, color: "var(--ink)", letterSpacing: "-0.025em", marginBottom: 10 }}>
            Pertanyaan yang Sering Diajukan
          </h1>
          <p style={{ fontSize: "0.97rem", color: "var(--ink-soft)", lineHeight: 1.65 }}>
            Tidak menemukan jawaban yang kamu cari? <a href="/contact" style={{ color: "var(--accent)", fontWeight: 500 }}>Hubungi kami</a> langsung.
          </p>
        </div>

        {/* FAQ sections */}
        <div style={{ display: "flex", flexDirection: "column", gap: 40 }}>
          {faqs.map((section) => (
            <div key={section.section}>
              <h2 style={{
                fontSize: "0.76rem", fontWeight: 700, color: "var(--accent)",
                textTransform: "uppercase", letterSpacing: "0.08em",
                marginBottom: 20,
              }}>
                {section.section}
              </h2>
              <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                {section.items.map((item, i) => (
                  <details key={i} style={{
                    background: "#fff",
                    border: "1.5px solid var(--line)",
                    borderRadius: 12,
                    overflow: "hidden",
                  }}>
                    <summary style={{
                      padding: "16px 20px",
                      fontSize: "0.92rem", fontWeight: 600,
                      color: "var(--ink)", cursor: "pointer",
                      listStyle: "none",
                      display: "flex", justifyContent: "space-between", alignItems: "center",
                      userSelect: "none",
                    }}>
                      {item.q}
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ flexShrink: 0, marginLeft: 12 }}>
                        <path d="M4 6L8 10L12 6" stroke="var(--muted)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </summary>
                    <div style={{
                      padding: "0 20px 18px",
                      fontSize: "0.89rem", color: "var(--ink-soft)",
                      lineHeight: 1.7,
                      borderTop: "1px solid var(--line)",
                      paddingTop: 14,
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
          marginTop: 56, background: "var(--bg-hero)",
          border: "1.5px solid var(--line)", borderRadius: 16,
          padding: "28px 32px", textAlign: "center",
        }}>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--ink)", marginBottom: 8 }}>
            Masih ada pertanyaan?
          </h3>
          <p style={{ fontSize: "0.9rem", color: "var(--ink-soft)", marginBottom: 20 }}>
            Tim kami siap membantu kamu melalui email.
          </p>
          <a href="/contact" style={{
            display: "inline-block",
            background: "var(--accent)", color: "#fff",
            padding: "11px 26px", borderRadius: 10,
            fontWeight: 600, fontSize: "0.9rem",
          }}>
            Hubungi kami
          </a>
        </div>
      </div>

      <Footer />
    </div>
  );
}
