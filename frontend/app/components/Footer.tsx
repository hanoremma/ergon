import Link from "next/link";

export default function Footer() {
  return (
    <footer style={{
      borderTop: "1px solid #1a2f47",
      marginTop: 40,
      background: "#0a1e33",
      padding: "52px 0 36px",
    }}>
      <div style={{
        maxWidth: 1160,
        margin: "0 auto",
        padding: "0 32px",
      }}>
        {/* Top row */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "1.4fr 1fr 1fr 1fr",
          gap: 40,
          marginBottom: 48,
        }}>
          {/* Brand */}
          <div>
            <div style={{
              display: "flex", alignItems: "center", gap: 9,
              fontWeight: 700, fontSize: "1.15rem",
              color: "#fff", letterSpacing: "-0.02em",
              marginBottom: 12,
            }}>
              <svg width="26" height="26" viewBox="0 0 28 28" fill="none">
                <rect width="28" height="28" rx="8" fill="var(--accent)"/>
                <path d="M8 14C8 10.686 10.686 8 14 8C17.314 8 20 10.686 20 14" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                <circle cx="14" cy="18" r="3" fill="white"/>
              </svg>
              Ergon
            </div>
            <p style={{
              fontSize: "0.86rem", color: "#7FA3C0",
              lineHeight: 1.65, maxWidth: 260,
            }}>
              Analisis kecocokan CV dan loker berbasis AI — bantu kamu melamar lebih tepat sasaran dan percaya diri.
            </p>
          </div>

          {/* Produk */}
          <div>
            <div style={{
              fontSize: "0.76rem", fontWeight: 700, color: "#B8D4EE",
              textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 14,
            }}>
              Produk
            </div>
            <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 10 }}>
              {[
                { label: "Cek kecocokan CV", href: "/upload" },
                { label: "Cara kerja", href: "/#how" },
                { label: "Harga", href: "/#unlock" },
                { label: "Wawancara AI (segera)", href: "/#soon" },
              ].map((item) => (
                <li key={item.href}>
                  <Link href={item.href} style={{
                    fontSize: "0.87rem", color: "#7FA3C0",
                    fontWeight: 400,
                  }}>
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Dukungan */}
          <div>
            <div style={{
              fontSize: "0.76rem", fontWeight: 700, color: "#B8D4EE",
              textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 14,
            }}>
              Dukungan
            </div>
            <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 10 }}>
              {[
                { label: "Pertanyaan umum (FAQ)", href: "/faq" },
                { label: "Hubungi kami", href: "/contact" },
                { label: "Kebijakan privasi", href: "/privacy" },
                { label: "Syarat & ketentuan", href: "/terms" },
              ].map((item) => (
                <li key={item.label}>
                  <Link href={item.href} style={{
                    fontSize: "0.87rem", color: "#7FA3C0",
                    fontWeight: 400,
                  }}>
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Keamanan */}
          <div>
            <div style={{
              fontSize: "0.76rem", fontWeight: 700, color: "#B8D4EE",
              textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 14,
            }}>
              Keamanan & Privasi
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {[
                "Data diproses secara aman",
                "Hapus data kapan saja",
                "Tidak dijual ke pihak ketiga",
              ].map((text) => (
                <div key={text} style={{
                  display: "flex", gap: 8, alignItems: "flex-start",
                  fontSize: "0.85rem", color: "#7FA3C0",
                }}>
                  <span style={{
                    width: 5, height: 5, borderRadius: "50%",
                    background: "#3b82d4", flexShrink: 0, marginTop: 7,
                    display: "inline-block",
                  }} />
                  {text}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom row */}
        <div style={{
          borderTop: "1px solid #1a2f47",
          paddingTop: 24,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: "0.82rem",
          color: "#4a6a85",
          flexWrap: "wrap",
          gap: 12,
        }}>
          <span>© 2026 Ergon. Seluruh hak cipta dilindungi.</span>
          <div style={{ display: "flex", gap: 20, alignItems: "center" }}>
            <span>Pembayaran aman via</span>
            <span style={{
              background: "#132030", border: "1px solid #1a2f47",
              borderRadius: 6, padding: "3px 10px",
              fontSize: "0.8rem", fontWeight: 600, color: "#B8D4EE",
            }}>
              Midtrans
            </span>
            <span style={{
              background: "#132030", border: "1px solid #1a2f47",
              borderRadius: 6, padding: "3px 10px",
              fontSize: "0.8rem", fontWeight: 600, color: "#B8D4EE",
            }}>
              QRIS
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}
