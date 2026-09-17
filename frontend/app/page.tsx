import Link from "next/link";
import Nav from "./components/Nav";
import Footer from "./components/Footer";
import DashboardSections from "./components/DashboardSections";

export default function Home() {
  return (
    <div style={{ background: "#fff", minHeight: "100vh", overflowX: "hidden" }}>
      <Nav />

      {/* ── Hero ─────────────────────────────────────────────────────── */}
      <section style={{ position: "relative", overflow: "hidden", background: "#fff", paddingBottom: 0 }}>

        {/* Background gradient blob kiri */}
        <div style={{
          position: "absolute", top: -120, left: -180,
          width: 640, height: 640, borderRadius: "50%",
          background: "radial-gradient(circle, #dbeafe 0%, #eff6ff 45%, transparent 72%)",
          zIndex: 0, pointerEvents: "none",
        }} />
        {/* Background gradient blob kanan */}
        <div style={{
          position: "absolute", top: 40, right: -160,
          width: 520, height: 520, borderRadius: "50%",
          background: "radial-gradient(circle, #bfdbfe 0%, #e0f2fe 40%, transparent 68%)",
          zIndex: 0, pointerEvents: "none",
        }} />
        {/* Bentuk dekoratif — lingkaran kecil */}
        <div style={{
          position: "absolute", top: 60, right: "38%",
          width: 14, height: 14, borderRadius: "50%",
          background: "var(--accent)", opacity: 0.25, zIndex: 0,
        }} />
        <div style={{
          position: "absolute", top: 200, left: "8%",
          width: 8, height: 8, borderRadius: "50%",
          background: "var(--accent)", opacity: 0.3, zIndex: 0,
        }} />
        {/* Kotak outline dekoratif */}
        <div style={{
          position: "absolute", bottom: 60, left: "12%",
          width: 48, height: 48, borderRadius: 10,
          border: "2px solid #bfdbfe", transform: "rotate(18deg)",
          zIndex: 0, opacity: 0.6,
        }} />
        <div style={{
          position: "absolute", top: 100, right: "14%",
          width: 32, height: 32, borderRadius: 8,
          border: "2px solid #93c5fd", transform: "rotate(-12deg)",
          zIndex: 0, opacity: 0.5,
        }} />

        <div style={{
          position: "relative", zIndex: 1,
          maxWidth: 1160, margin: "0 auto", padding: "0 32px",
          display: "grid", gridTemplateColumns: "1fr 1fr",
          gap: 48, alignItems: "center", paddingTop: 72, paddingBottom: 80,
        }}>
          {/* Left — teks */}
          <div>
            {/* Badge */}
            <div style={{
              display: "inline-flex", alignItems: "center", gap: 7,
              background: "linear-gradient(135deg, #eff6ff, #dbeafe)",
              borderRadius: 24, padding: "6px 16px", marginBottom: 28,
              border: "1px solid #bfdbfe",
            }}>
              <span style={{
                width: 7, height: 7, borderRadius: "50%",
                background: "var(--accent)", display: "inline-block",
                boxShadow: "0 0 0 3px #bfdbfe",
              }} />
              <span style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--accent-deep)", letterSpacing: "0.03em" }}>
                AI CV-Fit Scorer & Enhancer
              </span>
            </div>

            <h1 style={{
              fontSize: "3.2rem", lineHeight: 1.1, letterSpacing: "-0.03em",
              color: "#0F2A4A", maxWidth: 520, marginBottom: 0,
            }}>
              Tahu seberapa{" "}
              <span style={{
                background: "linear-gradient(135deg, #1d4ed8, #3b82f6, #0ea5e9)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                backgroundClip: "text",
              }}>
                cocok CV-mu
              </span>
              , sebelum kirim lamaran
            </h1>

            <p style={{ marginTop: 22, fontSize: "1.06rem", maxWidth: 460, color: "#3A5878", lineHeight: 1.7 }}>
              Ergon membaca loker dan CV-mu, lalu memberikan skor kecocokan lengkap dengan alasannya — plus saran yang langsung bisa kamu terapkan.
            </p>

            <div style={{ display: "flex", gap: 14, marginTop: 36, alignItems: "center", flexWrap: "wrap" }}>
              <Link href="/upload" style={{
                background: "linear-gradient(135deg, #1d4ed8, #3b82f6)",
                color: "#fff", padding: "14px 32px", borderRadius: 12,
                fontWeight: 600, fontSize: "0.97rem", letterSpacing: "-0.01em",
                boxShadow: "0 4px 16px rgba(59,130,246,0.35), 0 1px 3px rgba(59,130,246,0.2)",
                display: "inline-block",
              }}>
                Cek kecocokan CV →
              </Link>
              <a href="#how" style={{
                color: "#3A5878", fontWeight: 500, fontSize: "0.93rem",
                display: "flex", alignItems: "center", gap: 6,
                padding: "14px 20px", borderRadius: 12,
                border: "1.5px solid #bfdbfe", background: "#fff",
              }}>
                Lihat cara kerja
              </a>
            </div>

            {/* Social proof */}
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 36 }}>
              {/* Avatar stack */}
              <div style={{ display: "flex" }}>
                {["#3b82f6","#1d4ed8","#0ea5e9","#6366f1"].map((c, i) => (
                  <div key={i} style={{
                    width: 34, height: 34, borderRadius: "50%",
                    background: `linear-gradient(135deg, ${c}, ${c}cc)`,
                    border: "2.5px solid #fff",
                    marginLeft: i === 0 ? 0 : -10,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: "0.68rem", fontWeight: 700, color: "#fff",
                    zIndex: 4 - i, position: "relative",
                  }}>
                    {["AR","BI","CK","DL"][i]}
                  </div>
                ))}
              </div>
              <div>
                <div style={{ display: "flex", gap: 2, marginBottom: 2 }}>
                  {[1,2,3,4,5].map(i => (
                    <svg key={i} width="13" height="13" viewBox="0 0 16 16">
                      <path d="M8 1L9.8 5.8H15L10.9 8.8L12.5 13.6L8 10.5L3.5 13.6L5.1 8.8L1 5.8H6.2Z" fill="#f59e0b"/>
                    </svg>
                  ))}
                </div>
                <span style={{ fontSize: "0.8rem", color: "#3A5878" }}>
                  <strong style={{ color: "#0F2A4A" }}>1.200+</strong> CV sudah dianalisis
                </span>
              </div>
            </div>
          </div>

          {/* Right — Ilustrasi card */}
          <div style={{ position: "relative", height: 420 }}>
            {/* Score floating chip — kiri atas */}
            <div style={{
              position: "absolute", top: 0, left: -10, zIndex: 10,
              background: "linear-gradient(135deg, #1d4ed8, #3b82f6)",
              color: "#fff", borderRadius: 14, padding: "12px 18px",
              display: "flex", alignItems: "center", gap: 9,
              fontSize: "0.88rem", fontWeight: 700,
              boxShadow: "0 8px 24px rgba(59,130,246,0.40)",
            }}>
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M2 12L6 7L9 10L14 3" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Skor 82 — Sangat Cocok
            </div>

            {/* Main card */}
            <div style={{
              position: "absolute", top: 52, left: 10, right: 0, bottom: 20,
              background: "#fff", borderRadius: 24,
              border: "1.5px solid #e0eefb",
              boxShadow: "0 8px 40px rgba(15,42,74,0.10), 0 2px 8px rgba(15,42,74,0.06)",
              overflow: "hidden",
            }}>
              {/* Gradient stripe top */}
              <div style={{
                height: 5,
                background: "linear-gradient(90deg, #1d4ed8, #3b82f6, #0ea5e9)",
              }} />
              {/* Card header */}
              <div style={{
                height: 44, display: "flex", alignItems: "center",
                gap: 6, padding: "0 20px",
                borderBottom: "1px solid #f0f6ff",
                background: "#f8fbff",
              }}>
                {["#fbbf24","#34d399","#60a5fa"].map((c, i) => (
                  <span key={i} style={{ width: 9, height: 9, borderRadius: "50%", background: c }} />
                ))}
                <span style={{ fontSize: "0.75rem", color: "#94a3b8", marginLeft: 8 }}>ergon.ai — Analisis CV</span>
              </div>

              {/* Card body */}
              <div style={{ padding: "20px 24px" }}>
                {/* Candidate row */}
                <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
                  <div style={{
                    width: 44, height: 44, borderRadius: "50%",
                    background: "linear-gradient(135deg, #1d4ed8, #3b82f6)",
                    color: "#fff", display: "flex", alignItems: "center",
                    justifyContent: "center", fontSize: "0.9rem", fontWeight: 700, flexShrink: 0,
                  }}>AR</div>
                  <div>
                    <div style={{ fontSize: "0.9rem", fontWeight: 600, color: "#0F2A4A" }}>Alya Rahmawati</div>
                    <div style={{ fontSize: "0.75rem", color: "#94a3b8" }}>Teknik Informatika · Fresh Graduate</div>
                  </div>
                  <div style={{
                    marginLeft: "auto",
                    background: "linear-gradient(135deg, #eff6ff, #dbeafe)",
                    borderRadius: 20, padding: "4px 12px",
                    fontSize: "0.78rem", fontWeight: 700, color: "#1d4ed8",
                    border: "1px solid #bfdbfe",
                  }}>82%</div>
                </div>

                {/* Gauge SVG */}
                <div style={{ display: "flex", justifyContent: "center", marginBottom: 16 }}>
                  <svg width="120" height="68" viewBox="0 0 120 68">
                    <defs>
                      <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#1d4ed8"/>
                        <stop offset="100%" stopColor="#0ea5e9"/>
                      </linearGradient>
                    </defs>
                    <path d="M14 58A46 46 0 01106 58" stroke="#e0eefb" strokeWidth="9" strokeLinecap="round" fill="none"/>
                    <path d="M14 58A46 46 0 0192 24" stroke="url(#gaugeGrad)" strokeWidth="9" strokeLinecap="round" fill="none"/>
                    <text x="60" y="54" textAnchor="middle" style={{ fontSize: "20px", fontWeight: 800, fill: "#1d4ed8", fontFamily: "Inter, sans-serif" }}>82</text>
                    <text x="60" y="66" textAnchor="middle" style={{ fontSize: "8px", fill: "#94a3b8", fontFamily: "Inter, sans-serif" }}>SKOR KECOCOKAN</text>
                  </svg>
                </div>

                {/* Skills */}
                <div style={{ display: "flex", flexDirection: "column", gap: 7 }}>
                  {[
                    { label: "Python", matched: true },
                    { label: "Machine Learning", matched: true },
                    { label: "SQL", matched: true },
                    { label: "Docker", matched: false },
                  ].map((skill) => (
                    <div key={skill.label} style={{ display: "flex", alignItems: "center", gap: 9 }}>
                      <div style={{
                        width: 18, height: 18, borderRadius: "50%", flexShrink: 0,
                        background: skill.matched ? "#ecfdf5" : "#fef2f2",
                        border: `1.5px solid ${skill.matched ? "#86efac" : "#fca5a5"}`,
                        display: "flex", alignItems: "center", justifyContent: "center",
                      }}>
                        {skill.matched ? (
                          <svg width="9" height="9" viewBox="0 0 10 10" fill="none">
                            <path d="M2 5.5L4 7.5L8 3" stroke="#16a34a" strokeWidth="1.6" strokeLinecap="round"/>
                          </svg>
                        ) : (
                          <svg width="9" height="9" viewBox="0 0 10 10" fill="none">
                            <path d="M3 3L7 7M7 3L3 7" stroke="#dc2626" strokeWidth="1.6" strokeLinecap="round"/>
                          </svg>
                        )}
                      </div>
                      <span style={{ fontSize: "0.8rem", color: skill.matched ? "#0F2A4A" : "#94a3b8", fontWeight: skill.matched ? 500 : 400 }}>{skill.label}</span>
                      {skill.matched && (
                        <div style={{
                          marginLeft: "auto", height: 5, borderRadius: 99,
                          background: "linear-gradient(90deg, #3b82f6, #0ea5e9)",
                          width: `${[88,76,70,0][["Python","Machine Learning","SQL","Docker"].indexOf(skill.label)]}%`,
                          maxWidth: 64,
                        }} />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Free chip — bawah kiri */}
            <div style={{
              position: "absolute", bottom: 0, left: -8, zIndex: 10,
              background: "#fff", borderRadius: 14, padding: "10px 18px",
              display: "flex", alignItems: "center", gap: 9,
              fontSize: "0.83rem", fontWeight: 600, color: "#0F2A4A",
              boxShadow: "0 4px 20px rgba(15,42,74,0.13)",
              border: "1.5px solid #e0eefb",
            }}>
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="8" r="6.4" stroke="#16a34a" strokeWidth="1.5"/>
                <path d="M5.3 8.2L7.1 10L10.6 6" stroke="#16a34a" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              3 saran perbaikan gratis
            </div>
          </div>
        </div>

        {/* Wave separator */}
        <div style={{ lineHeight: 0, marginTop: -2 }}>
          <svg viewBox="0 0 1440 60" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none" style={{ width: "100%", height: 60, display: "block" }}>
            <path d="M0,30 C360,60 1080,0 1440,30 L1440,60 L0,60 Z" fill="#f0f7ff"/>
          </svg>
        </div>
      </section>

      {/* ── Logo strip ───────────────────────────────────────────────── */}
      <section style={{ background: "#f0f7ff", paddingBottom: 48, paddingTop: 8 }}>
        <div style={{ maxWidth: 1160, margin: "0 auto", padding: "0 32px" }}>
          <p style={{ textAlign: "center", fontSize: "0.78rem", fontWeight: 600, color: "#94a3b8", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 24 }}>
            Pelamar kami diterima di
          </p>
          <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 48, flexWrap: "wrap" }}>
            {["Tokopedia", "Gojek", "Traveloka", "Shopee", "BCA Digital"].map((name) => (
              <span key={name} style={{ fontSize: "1rem", fontWeight: 700, color: "#94a3b8", letterSpacing: "-0.01em" }}>{name}</span>
            ))}
          </div>
        </div>
      </section>

      {/* Sections */}
      <div style={{ background: "#fff" }}>
        <div style={{ maxWidth: 1160, margin: "0 auto", padding: "0 32px" }}>
          <DashboardSections />
        </div>
      </div>

      <Footer />
    </div>
  );
}
