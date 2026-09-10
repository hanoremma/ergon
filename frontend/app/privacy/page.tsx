import Nav from "../components/Nav";
import Footer from "../components/Footer";

export default function PrivacyPage() {
  const lastUpdated = "1 Juni 2026";

  return (
    <div style={{ background: "var(--bg-page)", minHeight: "100vh" }}>
      <Nav />

      <div style={{ maxWidth: 760, margin: "0 auto", padding: "52px 32px 88px" }}>
        {/* Header */}
        <div style={{ marginBottom: 40 }}>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 7,
            background: "var(--accent-soft)", borderRadius: 20,
            padding: "5px 14px", marginBottom: 16,
            border: "1px solid var(--line)",
          }}>
            <span style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--accent-deep)" }}>Legal</span>
          </div>
          <h1 style={{ fontSize: "2rem", fontWeight: 800, color: "var(--ink)", letterSpacing: "-0.025em", marginBottom: 10 }}>
            Kebijakan Privasi
          </h1>
          <p style={{ fontSize: "0.86rem", color: "var(--muted)" }}>
            Terakhir diperbarui: {lastUpdated}
          </p>
        </div>

        {/* Notice box */}
        <div style={{
          background: "var(--accent-soft)", border: "1px solid var(--line)",
          borderRadius: 12, padding: "16px 20px", marginBottom: 36,
          display: "flex", gap: 12, alignItems: "flex-start",
        }}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ flexShrink: 0, marginTop: 2 }}>
            <circle cx="8" cy="8" r="6.5" stroke="var(--accent-deep)" strokeWidth="1.4"/>
            <path d="M8 5v4M8 11h.01" stroke="var(--accent-deep)" strokeWidth="1.4" strokeLinecap="round"/>
          </svg>
          <p style={{ fontSize: "0.86rem", color: "var(--accent-deep)", lineHeight: 1.65 }}>
            Kami berkomitmen menjaga privasi data kamu. Halaman ini menjelaskan data apa yang kami kumpulkan, bagaimana kami menggunakannya, dan hak-hak yang kamu miliki.
          </p>
        </div>

        {/* Content */}
        <div style={{ display: "flex", flexDirection: "column", gap: 36 }}>
          {[
            {
              title: "1. Data yang Kami Kumpulkan",
              content: `Ergon mengumpulkan data berikut semata-mata untuk keperluan analisis kecocokan CV:

• **File CV** yang kamu upload (format PDF)
• **Loker** yang kamu masukkan, baik berupa URL, file PDF, maupun screenshot
• **URL portofolio** yang kamu sertakan secara opsional
• **Data teknis** seperti sesi ID anonim dan timestamp permintaan

Kami tidak mengumpulkan nama, alamat email, nomor telepon, atau informasi identitas lainnya kecuali kamu menyertakannya secara sukarela saat menghubungi kami.`,
            },
            {
              title: "2. Bagaimana Kami Menggunakan Data",
              content: `Data yang kamu berikan digunakan hanya untuk:

• Melakukan analisis kecocokan CV terhadap loker yang kamu masukkan
• Menghasilkan skor dan saran perbaikan CV
• Memproses dan memverifikasi transaksi pembayaran (melalui Midtrans)
• Merespons pertanyaan atau laporan yang kamu kirimkan

Kami **tidak** menggunakan data CV kamu untuk melatih model AI, tidak menjualnya kepada pihak ketiga, dan tidak menggunakannya untuk tujuan iklan.`,
            },
            {
              title: "3. Penyimpanan & Keamanan Data",
              content: `Data sesi disimpan di server aman dengan enkripsi in-transit (HTTPS) dan at-rest. Setiap sesi memiliki ID unik anonim — tidak ada data yang dikaitkan dengan identitas pribadi secara langsung.

Data sesi akan dihapus otomatis setelah **30 hari** sejak terakhir diakses. Kamu dapat meminta penghapusan lebih awal kapan saja melalui halaman Hubungi Kami.`,
            },
            {
              title: "4. Berbagi Data dengan Pihak Ketiga",
              content: `Ergon menggunakan layanan pihak ketiga terbatas berikut:

• **Midtrans** — untuk pemrosesan pembayaran. Data yang diteruskan hanya data minimum yang diperlukan untuk transaksi (session ID, nominal). Kebijakan privasi Midtrans berlaku untuk data yang mereka proses.
• **Penyedia AI/LLM** — untuk memproses konten CV dan loker dalam analisis. Data dikirim melalui API terenkripsi dan tidak disimpan oleh penyedia tersebut di luar sesi inferensi.

Kami tidak menjual, menyewakan, atau membagikan data kamu kepada pihak lain untuk tujuan pemasaran.`,
            },
            {
              title: "5. Hak-Hak Kamu",
              content: `Kamu memiliki hak untuk:

• **Mengakses** data yang kami miliki tentang sesimu (dengan menyertakan session ID)
• **Menghapus** data sesimu sebelum masa retensi 30 hari berakhir
• **Mengajukan keberatan** atas pemrosesan data tertentu

Untuk menggunakan hak-hak ini, hubungi kami melalui halaman Hubungi Kami.`,
            },
            {
              title: "6. Cookie & Penyimpanan Lokal",
              content: `Ergon menggunakan penyimpanan lokal browser (localStorage) hanya untuk menyimpan session ID anonim agar kamu bisa mengakses kembali hasil analisis yang sudah dibayar. Tidak ada cookie pelacak pihak ketiga yang digunakan.`,
            },
            {
              title: "7. Perubahan Kebijakan",
              content: `Kami dapat memperbarui kebijakan privasi ini dari waktu ke waktu. Perubahan signifikan akan diberitahukan melalui banner di situs. Tanggal "Terakhir diperbarui" di bagian atas halaman selalu mencerminkan versi terkini.`,
            },
            {
              title: "8. Hubungi Kami",
              content: `Pertanyaan tentang privasi data dapat dikirimkan ke: **halo@ergon.id** atau melalui halaman Hubungi Kami.`,
            },
          ].map((section) => (
            <div key={section.title}>
              <h2 style={{
                fontSize: "1.05rem", fontWeight: 700, color: "var(--ink)",
                letterSpacing: "-0.01em", marginBottom: 12,
              }}>
                {section.title}
              </h2>
              <div style={{
                fontSize: "0.9rem", color: "var(--ink-soft)", lineHeight: 1.8,
                whiteSpace: "pre-line",
              }}>
                {section.content.split("**").map((part, i) =>
                  i % 2 === 1
                    ? <strong key={i} style={{ color: "var(--ink)", fontWeight: 600 }}>{part}</strong>
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
