import Link from "next/link";
import Image from "next/image";

export default function Footer() {
  return (
    <footer style={{
      position: "relative",
      overflow: "hidden",
      marginTop: 40,
      background: "linear-gradient(160deg, #0a1628 0%, #0f2040 50%, #0a1e33 100%)",
      padding: "60px 0 0",
    }}>
      {/* Gradient blobs dekoratif */}
      <div style={{
        position: "absolute", top: -60, left: -80,
        width: 360, height: 360, borderRadius: "50%",
        background: "radial-gradient(circle, rgba(29,78,216,0.18) 0%, transparent 70%)",
        pointerEvents: "none",
      }} />
      <div style={{
        position: "absolute", top: 40, right: -60,
        width: 280, height: 280, borderRadius: "50%",
        background: "radial-gradient(circle, rgba(14,165,233,0.12) 0%, transparent 70%)",
        pointerEvents: "none",
      }} />

      <div style={{ position: "relative", zIndex: 1, maxWidth: 1160, margin: "0 auto", padding: "0 32px" }}>
        {/* Top row */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "1.4fr 1fr 1fr 1fr",
          gap: 40,
          marginBottom: 52,
        }}>
          {/* Brand */}
          <div>
            <div style={{
              display: "flex", alignItems: "center", gap: 9,
              fontWeight: 700, fontSize: "1.15rem",
              color: "#fff", letterSpacing: "-0.025em",
              marginBottom: 14,
            }}>
              <Image src="/logo-ergon.png" alt="Ergon icon" width={32} height={32} />
              Ergon
            </div>
            <p style={{
              fontSize: "0.86rem", color: "rgba(255,255,255,0.45)",
              lineHeight: 1.7, maxWidth: 260,
            }}>
              Analisis kecocokan CV dan loker berbasis AI — bantu kamu melamar lebih tepat sasaran dan percaya diri.
            </p>

            {/* CTA kecil */}
            <Link href="/upload" style={{
              display: "inline-flex", alignItems: "center", gap: 7,
              marginTop: 20,
              background: "linear-gradient(135deg, #1d4ed8, #3b82f6)",
              color: "#fff", padding: "9px 18px", borderRadius: 10,
              fontSize: "0.84rem", fontWeight: 600,
              boxShadow: "0 3px 12px rgba(59,130,246,0.35)",
            }}>
              Coba gratis
              <svg width="12" height="12" viewBox="0 0 14 14" fill="none">
                <path d="M3 7H11M11 7L7.5 3.5M11 7L7.5 10.5" stroke="white" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </Link>
          </div>

          {/* Produk */}
          <div>
            <div style={{
              fontSize: "0.7rem", fontWeight: 700, color: "rgba(255,255,255,0.35)",
              textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 16,
            }}>
              Produk
            </div>
            <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 11 }}>
              {[
                { label: "Cek kecocokan CV", href: "/upload" },
                { label: "Cara kerja", href: "/#how" },
                { label: "Harga", href: "/#unlock" },
                { label: "Wawancara AI (segera)", href: "/#soon" },
              ].map((item) => (
                <li key={item.href}>
                  <Link href={item.href} style={{
                    fontSize: "0.87rem", color: "rgba(255,255,255,0.5)",
                    fontWeight: 400, transition: "color 0.15s",
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
              fontSize: "0.7rem", fontWeight: 700, color: "rgba(255,255,255,0.35)",
              textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 16,
            }}>
              Dukungan
            </div>
            <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 11 }}>
              {[
                { label: "Pertanyaan umum (FAQ)", href: "/faq" },
                { label: "Hubungi kami", href: "/contact" },
                { label: "Kebijakan privasi", href: "/privacy" },
                { label: "Syarat & ketentuan", href: "/terms" },
              ].map((item) => (
                <li key={item.label}>
                  <Link href={item.href} style={{
                    fontSize: "0.87rem", color: "rgba(255,255,255,0.5)",
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
              fontSize: "0.7rem", fontWeight: 700, color: "rgba(255,255,255,0.35)",
              textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 16,
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
                  display: "flex", gap: 9, alignItems: "flex-start",
                  fontSize: "0.85rem", color: "rgba(255,255,255,0.5)",
                }}>
                  <div style={{
                    width: 16, height: 16, borderRadius: "50%", flexShrink: 0, marginTop: 1,
                    background: "rgba(59,130,246,0.2)", border: "1px solid rgba(59,130,246,0.35)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                  }}>
                    <svg width="8" height="8" viewBox="0 0 10 10" fill="none">
                      <path d="M2 5.5L4 7.5L8 3" stroke="#60a5fa" strokeWidth="1.5" strokeLinecap="round"/>
                    </svg>
                  </div>
                  {text}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom row */}
        <div style={{
          borderTop: "1px solid rgba(255,255,255,0.07)",
          padding: "20px 0 28px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: "0.82rem",
          color: "rgba(255,255,255,0.25)",
          flexWrap: "wrap",
          gap: 12,
        }}>
          <span>© 2026 Ergon. Seluruh hak cipta dilindungi.</span>
          <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
            <span>Pembayaran aman via</span>
            {["Midtrans", "QRIS"].map((name) => (
              <span key={name} style={{
                background: "rgba(255,255,255,0.06)",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 6, padding: "3px 10px",
                fontSize: "0.8rem", fontWeight: 600,
                color: "rgba(255,255,255,0.45)",
              }}>
                {name}
              </span>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
