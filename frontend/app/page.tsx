import Link from "next/link";
import Nav from "./components/Nav";
import Footer from "./components/Footer";

export default function Home() {
  return (
    <div style={{ background: "var(--bg-page)", minHeight: "100vh" }}>
      <Nav />

      {/* Hero */}
      <section style={{ background: "var(--bg-hero)", borderRadius: "0 0 40px 40px", paddingBottom: 80 }}>
        <div style={{
          maxWidth: 1160, margin: "0 auto", padding: "0 32px",
          display: "grid", gridTemplateColumns: "1.05fr 0.95fr",
          gap: 56, alignItems: "center", paddingTop: 44,
        }}>
          <div>
            <h1 style={{ fontSize: "3.05rem", maxWidth: 520, fontFamily: "'Space Grotesk', sans-serif", lineHeight: 1.12, letterSpacing: "-0.01em", color: "var(--ink)" }}>
              Tahu dulu seberapa cocok CV-mu, sebelum kirim lamaran
            </h1>
            <p style={{ marginTop: 22, fontSize: "1.08rem", maxWidth: 440, color: "var(--ink-soft)" }}>
              Ergon membaca loker dan CV-mu, lalu kasih skor kecocokan lengkap dengan alasannya — plus saran yang langsung bisa kamu pakai, bukan cuma template CV generik.
            </p>
            <div style={{ display: "flex", gap: 14, marginTop: 32, alignItems: "center" }}>
              <Link href="/upload" style={{
                background: "var(--accent)", color: "#fff",
                padding: "14px 26px", borderRadius: 12,
                fontWeight: 600, fontSize: "0.98rem",
                boxShadow: "0 10px 24px var(--chip-shadow)",
                fontFamily: "'Inter', sans-serif",
              }}>
                Cek kecocokan CV
              </Link>
              <Link href="#how" style={{
                color: "var(--ink)", fontWeight: 500, fontSize: "0.95rem",
                borderBottom: "1.5px solid var(--ink)", paddingBottom: 2,
              }}>
                Lihat cara kerjanya
              </Link>
            </div>
          </div>

          {/* Hero Illustration */}
          <div style={{ position: "relative", height: 400 }}>
            <svg style={{ position: "absolute", top: -38, right: 60, color: "var(--accent)" }}
              width="90" height="70" viewBox="0 0 90 70" fill="none">
              <path d="M4 66C30 66 46 40 46 22C46 10 56 4 70 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeDasharray="1 7"/>
              <path d="M62 2L71 6L66 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>

            {/* Score chip */}
            <div style={{
              position: "absolute", top: -6, right: 0,
              background: "var(--accent)", color: "#fff",
              borderRadius: 14, padding: "10px 16px",
              display: "flex", alignItems: "center", gap: 8,
              fontSize: "0.85rem", fontWeight: 500,
              boxShadow: "0 14px 30px var(--chip-shadow)",
            }}>
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M2 12L6 7L9 10L14 3" stroke="white" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              76% cocok
            </div>

            {/* Browser mockup */}
            <div style={{
              position: "absolute", top: 10, left: 10, right: 40, bottom: 30,
              background: "#fff", borderRadius: 18,
              border: "1.5px solid var(--line)",
              boxShadow: "0 30px 60px -20px rgba(33,29,61,0.18)",
              overflow: "hidden",
            }}>
              <div style={{
                height: 38, display: "flex", alignItems: "center",
                gap: 6, padding: "0 16px",
                borderBottom: "1px solid var(--accent-soft)",
              }}>
                {[0,1,2].map(i => (
                  <span key={i} style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--line)" }} />
                ))}
              </div>
              <div style={{ padding: "26px 28px", display: "flex", gap: 22, alignItems: "center" }}>
                {/* Doc icon */}
                <div style={{ width: 78, height: 96, border: "1.6px solid var(--ink)", borderRadius: 8, padding: "12px 10px", flexShrink: 0 }}>
                  {[70, 100, 55].map((w, i) => (
                    <div key={i} style={{ height: 2.5, background: "var(--line)", borderRadius: 2, marginBottom: 8, width: `${w}%` }} />
                  ))}
                </div>

                {/* Arrow */}
                <svg style={{ color: "var(--muted)", flexShrink: 0 }} width="26" height="14" viewBox="0 0 26 14" fill="none">
                  <path d="M0 7H23M23 7L17 1M23 7L17 13" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>

                {/* Gauge */}
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4, flexShrink: 0 }}>
                  <svg width="88" height="52" viewBox="0 0 88 52" fill="none">
                    <path d="M6 46A38 38 0 0182 46" stroke="var(--line)" strokeWidth="7" strokeLinecap="round"/>
                    <path d="M6 46A38 38 0 0164 15" stroke="var(--accent)" strokeWidth="7" strokeLinecap="round"/>
                  </svg>
                  <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: "1.5rem", color: "var(--accent)", marginTop: -38 }}>76</div>
                  <div style={{ fontSize: "0.72rem", color: "var(--ink-soft)" }}>skor kecocokan</div>
                </div>

                <svg style={{ color: "var(--muted)", flexShrink: 0 }} width="26" height="14" viewBox="0 0 26 14" fill="none">
                  <path d="M0 7H23M23 7L17 1M23 7L17 13" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>

                {/* CV icon */}
                <div style={{ width: 78, height: 96, border: "1.6px solid var(--ink)", borderRadius: 8, padding: "12px 10px", flexShrink: 0 }}>
                  <div style={{ width: 20, height: 20, borderRadius: "50%", border: "1.6px solid var(--ink)", marginBottom: 10 }} />
                  {[0,1].map(i => (
                    <div key={i} style={{ height: 2.5, background: "var(--line)", borderRadius: 2, marginBottom: 8, width: "85%" }} />
                  ))}
                </div>
              </div>
            </div>

            {/* Free chip */}
            <div style={{
              position: "absolute", bottom: 6, left: -18,
              background: "#fff", borderRadius: 14, padding: "10px 16px",
              display: "flex", alignItems: "center", gap: 8,
              fontSize: "0.85rem", fontWeight: 500,
              boxShadow: "0 14px 30px var(--chip-shadow)",
              border: "1px solid var(--accent-soft)",
            }}>
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="8" r="6.4" stroke="var(--success)" strokeWidth="1.5"/>
                <path d="M5.3 8.2L7.1 10L10.6 6" stroke="var(--success)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <span>3 saran perbaikan gratis</span>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how" style={{ padding: "96px 0 88px" }}>
        <div style={{ maxWidth: 1160, margin: "0 auto", padding: "0 32px" }}>
          <div style={{ maxWidth: 560, marginBottom: 56 }}>
            <h2 style={{ fontSize: "2.1rem", fontFamily: "'Space Grotesk', sans-serif", color: "var(--ink)" }}>
              Empat langkah, dari loker sampai CV siap kirim
            </h2>
            <p style={{ marginTop: 14, fontSize: "1.02rem", color: "var(--ink-soft)" }}>
              Semua proses berjalan otomatis di belakang layar — kamu tinggal upload dan baca hasilnya.
            </p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", position: "relative" }}>
            <div style={{
              content: "", position: "absolute", top: 19, left: 0, right: 0,
              height: 1.5, background: "var(--line)", zIndex: 0,
            }} />
            {[
              { num: "1", title: "Upload loker & CV", desc: "Tempel link, upload PDF, atau screenshot loker. Sertakan juga CV dan portofolio kamu." },
              { num: "2", title: "Ergon membaca semuanya", desc: "AI mengekstrak syarat loker, meriset perusahaannya, dan memetakan pengalamanmu." },
              { num: "3", title: "Lihat skor & saran", desc: "Skor kecocokan lengkap dengan alasannya, plus 3 saran perbaikan yang langsung gratis." },
              { num: "4", title: "Kirim CV yang sudah pas", desc: "Buka semua saran dan unduh CV yang sudah disesuaikan, siap dikirim ke perusahaan." },
            ].map((step, i) => (
              <div key={i} style={{ position: "relative", zIndex: 1, paddingRight: 24 }}>
                <div style={{
                  width: 40, height: 40, borderRadius: "50%",
                  background: i === 0 ? "var(--accent)" : "var(--bg-page)",
                  border: i === 0 ? "1.5px solid var(--accent)" : "1.5px solid var(--ink)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600,
                  fontSize: "0.95rem", marginBottom: 22,
                  color: i === 0 ? "#fff" : "var(--ink)",
                }}>
                  {step.num}
                </div>
                <h3 style={{ fontSize: "1.1rem", marginBottom: 10, fontFamily: "'Space Grotesk', sans-serif", color: "var(--ink)" }}>{step.title}</h3>
                <p style={{ fontSize: "0.92rem", color: "var(--ink-soft)" }}>{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Unlock / Monetization */}
      <section id="unlock" style={{
        background: "var(--bg-hero)", padding: "90px 0",
        borderRadius: 40, margin: "0 32px",
      }}>
        <div style={{ maxWidth: 1096, margin: "0 auto", padding: "0 32px" }}>
          <div style={{ maxWidth: 560, marginBottom: 48 }}>
            <h2 style={{ fontSize: "2.1rem", fontFamily: "'Space Grotesk', sans-serif", color: "var(--ink)" }}>
              Mulai gratis, buka semuanya kalau sudah yakin
            </h2>
            <p style={{ marginTop: 14, fontSize: "1.02rem", color: "var(--ink-soft)" }}>
              Skor dan tiga saran teratas selalu gratis. Butuh lebih dari itu, baru bayar.
            </p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1.15fr", gap: 28, alignItems: "stretch" }}>
            {/* Free panel */}
            <div style={{
              background: "#fff", border: "1.5px dashed var(--line)",
              borderRadius: 22, padding: "34px 32px",
            }}>
              <span style={{ fontSize: "0.8rem", color: "var(--ink-soft)", marginBottom: 18, display: "block" }}>Gratis</span>
              <h3 style={{ fontSize: "1.25rem", fontFamily: "'Space Grotesk', sans-serif", color: "var(--ink)", marginBottom: 6 }}>Skor kecocokan penuh</h3>
              <ul style={{ listStyle: "none", margin: "22px 0 0", padding: 0, display: "flex", flexDirection: "column", gap: 12 }}>
                {[
                  "Skor kecocokan & alasannya per kategori",
                  "3 saran perbaikan berdampak paling besar",
                  "Bisa dicoba untuk berapa pun loker",
                ].map((item, i) => (
                  <li key={i} style={{ display: "flex", gap: 10, alignItems: "flex-start", fontSize: "0.94rem", color: "var(--ink-soft)" }}>
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ flexShrink: 0, marginTop: 3 }}>
                      <circle cx="8" cy="8" r="6.4" stroke="var(--success)" strokeWidth="1.5"/>
                      <path d="M5.3 8.2L7.1 10L10.6 6" stroke="var(--success)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* Paid panel */}
            <div style={{
              background: "var(--ink)", borderRadius: 22, padding: "34px 32px",
              position: "relative", overflow: "hidden",
            }}>
              <span style={{ fontSize: "0.8rem", color: "var(--muted)", marginBottom: 18, display: "block" }}>Buka versi lengkap</span>
              <h3 style={{ fontSize: "1.25rem", fontFamily: "'Space Grotesk', sans-serif", color: "#fff", marginBottom: 6 }}>Semua saran + CV yang sudah direvisi</h3>
              <ul style={{ listStyle: "none", margin: "22px 0 0", padding: 0, display: "flex", flexDirection: "column", gap: 12 }}>
                {[
                  "Semua saran perbaikan, bukan cuma 3 teratas",
                  "CV hasil revisi, siap diunduh sebagai PDF/DOCX",
                ].map((item, i) => (
                  <li key={i} style={{ display: "flex", gap: 10, alignItems: "flex-start", fontSize: "0.94rem", color: "#DCD9F5" }}>
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ flexShrink: 0, marginTop: 3 }}>
                      <circle cx="8" cy="8" r="6.4" stroke="#DCD9F5" strokeWidth="1.5"/>
                      <path d="M5.3 8.2L7.1 10L10.6 6" stroke="#DCD9F5" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    {item}
                  </li>
                ))}
              </ul>
              {/* Locked rows */}
              {["Kuantifikasi pencapaian di baris pengalaman kedua", "Susun ulang urutan skill sesuai prioritas loker"].map((text, i) => (
                <div key={i} style={{
                  display: "flex", gap: 10, alignItems: "center",
                  padding: "10px 12px", borderRadius: 10,
                  background: "rgba(255,255,255,0.06)", filter: "blur(0.3px)", marginTop: 8,
                }}>
                  <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
                    <rect x="3.5" y="7" width="9" height="6.5" rx="1.4" stroke="var(--muted)" strokeWidth="1.4"/>
                    <path d="M5.5 7V5A2.5 2.5 0 0110.5 5V7" stroke="var(--muted)" strokeWidth="1.4"/>
                  </svg>
                  <span style={{ fontSize: "0.86rem", color: "var(--muted)" }}>{text}</span>
                </div>
              ))}
              <Link href="/upload" style={{
                background: "var(--accent)", color: "#fff",
                padding: "14px 26px", borderRadius: 12,
                fontWeight: 600, fontSize: "0.98rem",
                boxShadow: "0 10px 24px var(--chip-shadow)",
                display: "inline-block", marginTop: 26,
              }}>
                Buka versi lengkap
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Coming Soon */}
      <section id="soon" style={{ padding: "90px 0" }}>
        <div style={{ maxWidth: 1160, margin: "0 auto", padding: "0 32px" }}>
          <div style={{
            border: "1.5px dashed var(--line)", borderRadius: 22,
            padding: "40px 44px", display: "flex", alignItems: "center",
            gap: 32, background: "#fff",
          }}>
            <div style={{
              width: 64, height: 64, borderRadius: 16,
              background: "var(--accent-soft)",
              display: "flex", alignItems: "center", justifyContent: "center",
              flexShrink: 0, color: "var(--muted)",
            }}>
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
                <rect x="5" y="10" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="1.6"/>
                <path d="M8 10V7a4 4 0 018 0v3" stroke="currentColor" strokeWidth="1.6"/>
              </svg>
            </div>
            <div>
              <span style={{
                display: "inline-block", fontSize: "0.72rem", fontWeight: 600,
                color: "var(--accent-deep)", background: "var(--accent-soft)",
                padding: "4px 10px", borderRadius: 20, marginBottom: 10,
              }}>
                Segera hadir
              </span>
              <h3 style={{ fontSize: "1.2rem", fontFamily: "'Space Grotesk', sans-serif", color: "var(--ink)", marginBottom: 8 }}>
                Latihan wawancara bareng AI
              </h3>
              <p style={{ fontSize: "0.94rem", maxWidth: 520, color: "var(--ink-soft)" }}>
                Ngobrol langsung pakai suara dengan AI yang sudah tahu isi loker, riset perusahaan, dan CV kamu — lengkap dengan feedback di akhir sesi. Fitur ini sedang dibangun dan belum bisa dicoba.
              </p>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
