import Link from "next/link";
import Nav from "./components/Nav";
import Footer from "./components/Footer";
import DashboardSections from "./components/DashboardSections";

export default function Home() {
  return (
    <div style={{ background: "var(--bg-page)", minHeight: "100vh" }}>
      <Nav />

      {/* Hero */}
      <section style={{
        background: "var(--bg-hero)",
        borderRadius: "0 0 40px 40px",
        paddingBottom: 88,
        overflow: "hidden",
      }}>
        <div style={{
          maxWidth: 1160, margin: "0 auto", padding: "0 32px",
          display: "grid", gridTemplateColumns: "1.1fr 0.9fr",
          gap: 60, alignItems: "center", paddingTop: 52,
        }}>
          <div>
            {/* Badge */}
            <div style={{
              display: "inline-flex", alignItems: "center", gap: 7,
              background: "var(--accent-soft)", borderRadius: 20,
              padding: "5px 14px", marginBottom: 22,
              border: "1px solid var(--line)",
            }}>
              <span style={{
                width: 6, height: 6, borderRadius: "50%",
                background: "var(--accent)", display: "inline-block",
              }} />
              <span style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--accent-deep)", letterSpacing: "0.02em" }}>
                Analisis Kecocokan CV & Loker
              </span>
            </div>

            <h1 style={{
              fontSize: "2.8rem", maxWidth: 500,
              lineHeight: 1.15, letterSpacing: "-0.025em",
              color: "var(--ink)",
            }}>
              Tahu dulu seberapa cocok CV-mu, sebelum kirim lamaran
            </h1>
            <p style={{ marginTop: 20, fontSize: "1.05rem", maxWidth: 440, color: "var(--ink-soft)", lineHeight: 1.65 }}>
              Ergon membaca loker dan CV-mu, lalu memberikan skor kecocokan lengkap dengan alasannya — plus saran yang langsung bisa kamu terapkan.
            </p>
            <div style={{ display: "flex", gap: 14, marginTop: 34, alignItems: "center" }}>
              <Link href="/upload" style={{
                background: "var(--accent)", color: "#fff",
                padding: "14px 28px", borderRadius: 10,
                fontWeight: 600, fontSize: "0.96rem",
                letterSpacing: "-0.01em",
              }}>
                Cek kecocokan CV
              </Link>
              <a href="#how" style={{
                color: "var(--ink-soft)", fontWeight: 500, fontSize: "0.92rem",
                display: "flex", alignItems: "center", gap: 6,
              }}>
                Lihat cara kerjanya
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M3 7H11M11 7L7.5 3.5M11 7L7.5 10.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </a>
            </div>
          </div>

          {/* Hero Card Illustration */}
          <div style={{ position: "relative", height: 380, paddingTop: 40 }}>
            {/* Score chip — top right */}
            <div style={{
              position: "absolute", top: 0, right: 0,
              background: "var(--accent)", color: "#fff",
              borderRadius: 12, padding: "10px 16px",
              display: "flex", alignItems: "center", gap: 8,
              fontSize: "0.84rem", fontWeight: 600,
              boxShadow: "0 8px 20px var(--chip-shadow)",
            }}>
              <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
                <path d="M2 12L6 7L9 10L14 3" stroke="white" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Skor 82 — Sangat Cocok
            </div>

            {/* Main card */}
            <div style={{
              position: "absolute", top: 50, left: 0, right: 32, bottom: 20,
              background: "#fff", borderRadius: 20,
              border: "1.5px solid var(--line)",
              overflow: "hidden",
              boxShadow: "0 4px 24px rgba(15, 42, 74, 0.08)",
            }}>
              {/* Card header */}
              <div style={{
                height: 40, display: "flex", alignItems: "center",
                gap: 6, padding: "0 16px",
                borderBottom: "1px solid var(--line)",
                background: "var(--bg-page)",
              }}>
                {[0,1,2].map(i => (
                  <span key={i} style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--line)" }} />
                ))}
              </div>

              {/* Card body */}
              <div style={{ padding: "20px 22px" }}>
                {/* Candidate row */}
                <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 18 }}>
                  <div style={{
                    width: 40, height: 40, borderRadius: "50%",
                    background: "var(--accent)", color: "#fff",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: "0.9rem", fontWeight: 700, flexShrink: 0,
                  }}>
                    AR
                  </div>
                  <div>
                    <div style={{ fontSize: "0.88rem", fontWeight: 600, color: "var(--ink)" }}>Alya Rahmawati</div>
                    <div style={{ fontSize: "0.76rem", color: "var(--muted)" }}>Teknik Informatika · 2025</div>
                  </div>
                  <div style={{
                    marginLeft: "auto", background: "var(--accent-soft)",
                    borderRadius: 20, padding: "3px 10px",
                    fontSize: "0.76rem", fontWeight: 600, color: "var(--accent-deep)",
                  }}>82%</div>
                </div>

                {/* Circular score */}
                <div style={{ display: "flex", justifyContent: "center", marginBottom: 14 }}>
                  <svg width="100" height="60" viewBox="0 0 100 60">
                    <path d="M10 50A40 40 0 0190 50" stroke="var(--line)" strokeWidth="7" strokeLinecap="round" fill="none"/>
                    <path d="M10 50A40 40 0 0177 18" stroke="var(--accent)" strokeWidth="7" strokeLinecap="round" fill="none"/>
                    <text x="50" y="46" textAnchor="middle" style={{ fontSize: "18px", fontWeight: 700, fill: "var(--accent)" }}>82</text>
                  </svg>
                </div>

                {/* Skill checklist */}
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  {[
                    { label: "Python", matched: true },
                    { label: "Machine Learning", matched: true },
                    { label: "SQL", matched: true },
                    { label: "Docker", matched: false },
                    { label: "Kubernetes", matched: false },
                  ].map((skill, i) => (
                    <div key={i} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <div style={{
                        width: 16, height: 16, borderRadius: "50%", flexShrink: 0,
                        background: skill.matched ? "#ECFDF5" : "#FEF2F2",
                        border: `1.5px solid ${skill.matched ? "#A7F3D0" : "#FECACA"}`,
                        display: "flex", alignItems: "center", justifyContent: "center",
                      }}>
                        {skill.matched ? (
                          <svg width="8" height="8" viewBox="0 0 10 10" fill="none">
                            <path d="M2 5.5L4 7.5L8 3" stroke="#15803D" strokeWidth="1.5" strokeLinecap="round"/>
                          </svg>
                        ) : (
                          <svg width="8" height="8" viewBox="0 0 10 10" fill="none">
                            <path d="M3 3L7 7M7 3L3 7" stroke="#DC2626" strokeWidth="1.5" strokeLinecap="round"/>
                          </svg>
                        )}
                      </div>
                      <span style={{ fontSize: "0.78rem", color: skill.matched ? "var(--ink)" : "var(--muted)" }}>{skill.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Free chip — bottom left */}
            <div style={{
              position: "absolute", bottom: 0, left: -12,
              background: "#fff", borderRadius: 12, padding: "10px 16px",
              display: "flex", alignItems: "center", gap: 8,
              fontSize: "0.82rem", fontWeight: 500, color: "var(--ink)",
              boxShadow: "0 4px 16px var(--chip-shadow)",
              border: "1px solid var(--line)",
            }}>
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="8" r="6.4" stroke="var(--success)" strokeWidth="1.5"/>
                <path d="M5.3 8.2L7.1 10L10.6 6" stroke="var(--success)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              3 saran perbaikan gratis
            </div>
          </div>
        </div>
      </section>

      {/* Sections: Cara kerja / Harga / Wawancara AI — dengan scroll reveal */}
      <div style={{ maxWidth: 1160, margin: "0 auto", padding: "0 32px" }}>
        <DashboardSections />
      </div>

      <Footer />
    </div>
  );
}
