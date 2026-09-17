import Nav from "../components/Nav";
import Footer from "../components/Footer";

export default function PrivacyPage() {
  const lastUpdated = "1 Juni 2026";

  const sections = [
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
            Kebijakan Privasi
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
            Kami berkomitmen menjaga privasi data kamu. Halaman ini menjelaskan data apa yang kami kumpulkan, bagaimana kami menggunakannya, dan hak-hak yang kamu miliki.
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
