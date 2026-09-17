"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";

function useReveal() {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setVisible(true); observer.disconnect(); } },
      { threshold: 0.1 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);
  return { ref, visible };
}

const steps = [
  {
    num: "01", title: "Upload loker & CV",
    desc: "Tempel link, upload PDF, atau screenshot loker. Sertakan juga CV dan portofolio kamu.",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <path d="M12 16V8M12 8L9 11M12 8L15 11" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M20 16.7A4 4 0 0017 9h-1A7 7 0 104 15.3" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
  },
  {
    num: "02", title: "Ergon membaca semuanya",
    desc: "AI mengekstrak syarat loker, meriset perusahaan, dan memetakan pengalamanmu.",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <circle cx="11" cy="11" r="7" stroke="white" strokeWidth="1.8"/>
        <path d="M20 20L17 17" stroke="white" strokeWidth="1.8" strokeLinecap="round"/>
        <path d="M8 11H14M11 8V14" stroke="white" strokeWidth="1.6" strokeLinecap="round"/>
      </svg>
    ),
  },
  {
    num: "03", title: "Lihat skor & saran",
    desc: "Skor kecocokan lengkap dengan alasannya, plus 3 saran perbaikan gratis.",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <path d="M3 17L8 12L11 15L16 9L21 13" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
  },
  {
    num: "04", title: "Kirim CV yang sudah pas",
    desc: "Buka semua saran dan unduh laporan lengkap, siap dikirim ke perusahaan.",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
        <path d="M22 2L11 13M22 2L15 22L11 13L2 9L22 2Z" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
  },
];

const stats = [
  { value: "1.200+", label: "CV dianalisis" },
  { value: "4.8/5", label: "Rating pengguna" },
  { value: "92%", label: "Laporan akurat" },
  { value: "< 60s", label: "Waktu analisis" },
];

export default function DashboardSections() {
  const how = useReveal();
  const statsRef = useReveal();
  const pricing = useReveal();
  const interview = useReveal();

  return (
    <div style={{ display: "flex", flexDirection: "column" }}>

      {/* ── Stats bar ─────────────────────────────────────────────── */}
      <section style={{ padding: "64px 0 56px" }}>
        <div
          ref={statsRef.ref}
          style={{
            display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 2,
            background: "linear-gradient(135deg, #1d4ed8 0%, #2563eb 50%, #0ea5e9 100%)",
            borderRadius: 20, overflow: "hidden",
            opacity: statsRef.visible ? 1 : 0,
            transform: statsRef.visible ? "translateY(0)" : "translateY(24px)",
            transition: "opacity 0.6s ease, transform 0.6s ease",
          }}
        >
          {stats.map((s, i) => (
            <div key={i} style={{
              padding: "32px 28px",
              background: i % 2 === 0 ? "rgba(255,255,255,0.06)" : "transparent",
              textAlign: "center",
              borderRight: i < 3 ? "1px solid rgba(255,255,255,0.12)" : "none",
            }}>
              <div style={{ fontSize: "2rem", fontWeight: 800, color: "#fff", letterSpacing: "-0.04em", marginBottom: 6 }}>
                {s.value}
              </div>
              <div style={{ fontSize: "0.84rem", color: "rgba(255,255,255,0.7)", fontWeight: 500 }}>
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Cara kerja ─────────────────────────────────────────────── */}
      <section id="how" style={{ padding: "16px 0 88px", position: "relative" }}>
        {/* Dekorasi bg */}
        <div style={{
          position: "absolute", top: -40, right: -80,
          width: 360, height: 360, borderRadius: "50%",
          background: "radial-gradient(circle, #eff6ff 0%, transparent 70%)",
          zIndex: 0, pointerEvents: "none",
        }} />

        <div ref={how.ref} style={{ position: "relative", zIndex: 1 }}>
          {/* Label + heading */}
          <div style={{ textAlign: "center", maxWidth: 560, margin: "0 auto 56px" }}>
            <div style={{
              display: "inline-block", fontSize: "0.75rem", fontWeight: 700,
              color: "#1d4ed8", background: "linear-gradient(135deg, #eff6ff, #dbeafe)",
              padding: "5px 16px", borderRadius: 24, marginBottom: 18,
              border: "1px solid #bfdbfe", letterSpacing: "0.05em", textTransform: "uppercase",
            }}>
              Cara kerja
            </div>
            <h2 style={{ fontSize: "2rem", color: "#0F2A4A", lineHeight: 1.2, letterSpacing: "-0.025em" }}>
              Empat langkah, dari loker sampai CV siap kirim
            </h2>
            <p style={{ marginTop: 14, fontSize: "0.97rem", color: "#3A5878", lineHeight: 1.65 }}>
              Semua proses berjalan otomatis — kamu tinggal upload dan baca hasilnya.
            </p>
          </div>

          {/* Steps grid */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 16, position: "relative" }}>
            {/* Connector line */}
            <div style={{
              position: "absolute", top: 28, left: "12.5%", right: "12.5%",
              height: 2,
              background: "linear-gradient(90deg, #1d4ed8, #3b82f6, #0ea5e9)",
              zIndex: 0, opacity: 0.2, borderRadius: 99,
            }} />

            {steps.map((step, i) => (
              <div key={i} style={{
                position: "relative", zIndex: 1,
                opacity: how.visible ? 1 : 0,
                transform: how.visible ? "translateY(0)" : "translateY(24px)",
                transition: `opacity 0.5s ease ${0.1 + i * 0.12}s, transform 0.5s ease ${0.1 + i * 0.12}s`,
              }}>
                <div style={{
                  background: "#fff",
                  border: "1.5px solid #e0eefb",
                  borderRadius: 20,
                  padding: "28px 24px",
                  height: "100%",
                  boxShadow: i === 0 ? "0 8px 24px rgba(29,78,216,0.12)" : "0 2px 8px rgba(15,42,74,0.05)",
                  position: "relative",
                  overflow: "hidden",
                }}>
                  {/* Top accent for first card */}
                  {i === 0 && (
                    <div style={{
                      position: "absolute", top: 0, left: 0, right: 0, height: 3,
                      background: "linear-gradient(90deg, #1d4ed8, #3b82f6)",
                    }} />
                  )}
                  <div style={{
                    width: 48, height: 48, borderRadius: 14, marginBottom: 20,
                    background: i === 0
                      ? "linear-gradient(135deg, #1d4ed8, #3b82f6)"
                      : "linear-gradient(135deg, #3b82f6, #0ea5e9)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    boxShadow: `0 4px 12px rgba(59,130,246,${i === 0 ? "0.4" : "0.2"})`,
                  }}>
                    {step.icon}
                  </div>
                  <div style={{ fontSize: "0.7rem", fontWeight: 700, color: "#94a3b8", letterSpacing: "0.06em", marginBottom: 8 }}>
                    {step.num}
                  </div>
                  <h3 style={{ fontSize: "1rem", marginBottom: 10, color: "#0F2A4A", fontWeight: 700, lineHeight: 1.3 }}>
                    {step.title}
                  </h3>
                  <p style={{ fontSize: "0.88rem", color: "#3A5878", lineHeight: 1.65 }}>{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Harga ───────────────────────────────────────────────────── */}
      <section id="unlock" style={{ padding: "16px 0 88px", position: "relative" }}>
        {/* Gradient bg */}
        <div style={{
          position: "absolute", inset: 0,
          background: "linear-gradient(180deg, #fff 0%, #f0f7ff 60%, #fff 100%)",
          zIndex: 0,
        }} />
        <div style={{
          position: "absolute", top: 0, left: -100,
          width: 400, height: 400, borderRadius: "50%",
          background: "radial-gradient(circle, #dbeafe 0%, transparent 70%)",
          zIndex: 0, pointerEvents: "none",
        }} />

        <div ref={pricing.ref} style={{ position: "relative", zIndex: 1 }}>
          <div style={{ textAlign: "center", maxWidth: 560, margin: "0 auto 56px" }}>
            <div style={{
              display: "inline-block", fontSize: "0.75rem", fontWeight: 700,
              color: "#1d4ed8", background: "linear-gradient(135deg, #eff6ff, #dbeafe)",
              padding: "5px 16px", borderRadius: 24, marginBottom: 18,
              border: "1px solid #bfdbfe", letterSpacing: "0.05em", textTransform: "uppercase",
            }}>
              Harga
            </div>
            <h2 style={{ fontSize: "2rem", color: "#0F2A4A", lineHeight: 1.2, letterSpacing: "-0.025em" }}>
              Mulai gratis, buka semuanya kalau sudah yakin
            </h2>
            <p style={{ marginTop: 14, fontSize: "0.97rem", color: "#3A5878", lineHeight: 1.65 }}>
              Skor dan tiga saran teratas selalu gratis. Butuh lebih dari itu, baru bayar.
            </p>
          </div>

          <div style={{
            display: "grid", gridTemplateColumns: "1fr 1.1fr", gap: 20, alignItems: "stretch",
            opacity: pricing.visible ? 1 : 0,
            transform: pricing.visible ? "translateY(0)" : "translateY(24px)",
            transition: "opacity 0.55s ease 0.1s, transform 0.55s ease 0.1s",
          }}>
            {/* Free card */}
            <div style={{
              background: "#fff", border: "1.5px solid #e0eefb",
              borderRadius: 24, padding: "36px 32px",
              boxShadow: "0 2px 12px rgba(15,42,74,0.06)",
            }}>
              <div style={{
                display: "inline-block", fontSize: "0.74rem", fontWeight: 600,
                color: "#3A5878", background: "#f0f7ff",
                padding: "4px 14px", borderRadius: 20, marginBottom: 24,
                border: "1px solid #e0eefb",
              }}>
                Gratis
              </div>
              <div style={{ fontSize: "2.4rem", fontWeight: 800, color: "#0F2A4A", letterSpacing: "-0.05em", lineHeight: 1, marginBottom: 6 }}>
                Rp 0
              </div>
              <p style={{ fontSize: "0.84rem", color: "#94a3b8", marginBottom: 28 }}>Tidak perlu kartu kredit.</p>

              <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: 14 }}>
                {[
                  "Skor kecocokan & alasannya per kategori",
                  "3 saran perbaikan berdampak paling besar",
                  "Bisa dicoba untuk berapa pun loker",
                ].map((item) => (
                  <li key={item} style={{ display: "flex", gap: 10, alignItems: "flex-start", fontSize: "0.92rem", color: "#3A5878" }}>
                    <div style={{
                      width: 20, height: 20, borderRadius: "50%",
                      background: "#ecfdf5", border: "1.5px solid #86efac",
                      display: "flex", alignItems: "center", justifyContent: "center",
                      flexShrink: 0, marginTop: 1,
                    }}>
                      <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                        <path d="M2 5.5L4 7.5L8 3" stroke="#16a34a" strokeWidth="1.5" strokeLinecap="round"/>
                      </svg>
                    </div>
                    {item}
                  </li>
                ))}
              </ul>

              <Link href="/upload" style={{
                display: "block", textAlign: "center", marginTop: 32,
                padding: "13px 24px", borderRadius: 12,
                border: "1.5px solid #bfdbfe", color: "#1d4ed8",
                fontWeight: 600, fontSize: "0.94rem", background: "#fff",
              }}>
                Mulai gratis
              </Link>
            </div>

            {/* Paid card */}
            <div style={{
              background: "linear-gradient(145deg, #0F2A4A 0%, #1a3a5c 50%, #0e2240 100%)",
              borderRadius: 24, padding: "36px 32px",
              position: "relative", overflow: "hidden",
              boxShadow: "0 16px 48px rgba(15,42,74,0.25)",
            }}>
              {/* Glow effect */}
              <div style={{
                position: "absolute", top: -60, right: -60,
                width: 220, height: 220, borderRadius: "50%",
                background: "radial-gradient(circle, rgba(59,130,246,0.25) 0%, transparent 70%)",
                pointerEvents: "none",
              }} />
              <div style={{
                position: "absolute", bottom: -80, left: -40,
                width: 280, height: 280, borderRadius: "50%",
                background: "radial-gradient(circle, rgba(14,165,233,0.15) 0%, transparent 70%)",
                pointerEvents: "none",
              }} />

              <div style={{ position: "relative", zIndex: 1 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
                  <div style={{
                    fontSize: "0.74rem", fontWeight: 600,
                    color: "rgba(255,255,255,0.55)", background: "rgba(255,255,255,0.1)",
                    padding: "4px 14px", borderRadius: 20,
                  }}>
                    Buka versi lengkap
                  </div>
                  <div style={{
                    fontSize: "0.72rem", fontWeight: 700,
                    color: "#fbbf24", background: "rgba(251,191,36,0.15)",
                    padding: "4px 12px", borderRadius: 20, border: "1px solid rgba(251,191,36,0.3)",
                  }}>
                    ⭐ Paling populer
                  </div>
                </div>

                <div style={{ fontSize: "2.4rem", fontWeight: 800, color: "#fff", letterSpacing: "-0.05em", lineHeight: 1, marginBottom: 4 }}>
                  Rp 25.000
                </div>
                <p style={{ fontSize: "0.84rem", color: "rgba(255,255,255,0.45)", marginBottom: 28 }}>
                  Sekali bayar per loker · Tidak perlu berlangganan
                </p>

                <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: 12 }}>
                  {[
                    "Semua saran perbaikan, bukan cuma 3 teratas",
                    "Laporan lengkap, siap diunduh sebagai PDF",
                  ].map((item) => (
                    <li key={item} style={{ display: "flex", gap: 10, alignItems: "flex-start", fontSize: "0.92rem", color: "#B8D4EE" }}>
                      <div style={{
                        width: 20, height: 20, borderRadius: "50%",
                        background: "rgba(59,130,246,0.2)", border: "1.5px solid rgba(59,130,246,0.4)",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        flexShrink: 0, marginTop: 1,
                      }}>
                        <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                          <path d="M2 5.5L4 7.5L8 3" stroke="#93c5fd" strokeWidth="1.5" strokeLinecap="round"/>
                        </svg>
                      </div>
                      {item}
                    </li>
                  ))}
                </ul>

                {/* Locked preview items */}
                <div style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 8 }}>
                  {["Kuantifikasi pencapaian di baris pengalaman kedua", "Susun ulang urutan skill sesuai prioritas loker"].map((text) => (
                    <div key={text} style={{
                      display: "flex", gap: 10, alignItems: "center",
                      padding: "10px 14px", borderRadius: 10,
                      background: "rgba(255,255,255,0.05)",
                      border: "1px solid rgba(255,255,255,0.08)",
                    }}>
                      <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
                        <rect x="3.5" y="7" width="9" height="6.5" rx="1.4" stroke="rgba(255,255,255,0.3)" strokeWidth="1.4"/>
                        <path d="M5.5 7V5A2.5 2.5 0 0110.5 5V7" stroke="rgba(255,255,255,0.3)" strokeWidth="1.4"/>
                      </svg>
                      <span style={{ fontSize: "0.82rem", color: "rgba(255,255,255,0.3)", filter: "blur(2px)", userSelect: "none" }}>{text}</span>
                    </div>
                  ))}
                </div>

                <Link href="/upload" style={{
                  display: "block", textAlign: "center", marginTop: 28,
                  padding: "14px 24px", borderRadius: 12,
                  background: "linear-gradient(135deg, #1d4ed8, #3b82f6)",
                  color: "#fff", fontWeight: 700, fontSize: "0.96rem",
                  boxShadow: "0 4px 20px rgba(59,130,246,0.4)",
                }}>
                  Buka versi lengkap →
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Wawancara AI ────────────────────────────────────────────── */}
      <section id="soon" style={{ padding: "16px 0 96px", position: "relative" }}>
        <div ref={interview.ref}>
          <div style={{ textAlign: "center", maxWidth: 560, margin: "0 auto 48px" }}>
            <div style={{
              display: "inline-block", fontSize: "0.75rem", fontWeight: 700,
              color: "#1d4ed8", background: "linear-gradient(135deg, #eff6ff, #dbeafe)",
              padding: "5px 16px", borderRadius: 24, marginBottom: 18,
              border: "1px solid #bfdbfe", letterSpacing: "0.05em", textTransform: "uppercase",
            }}>
              Wawancara AI
            </div>
            <h2 style={{ fontSize: "2rem", color: "#0F2A4A", lineHeight: 1.2, letterSpacing: "-0.025em" }}>
              Latihan wawancara bareng AI
            </h2>
            <p style={{ marginTop: 14, fontSize: "0.97rem", color: "#3A5878", lineHeight: 1.65 }}>
              Ngobrol langsung pakai suara dengan AI yang sudah tahu isi loker, CV kamu — lengkap dengan feedback di akhir sesi.
            </p>
          </div>

          <div style={{
            background: "linear-gradient(145deg, #0F2A4A, #1a3a5c)",
            borderRadius: 28, padding: "48px 52px",
            position: "relative", overflow: "hidden",
            opacity: interview.visible ? 1 : 0,
            transform: interview.visible ? "translateY(0)" : "translateY(24px)",
            transition: "opacity 0.6s ease 0.1s, transform 0.6s ease 0.1s",
          }}>
            {/* Decorative blobs */}
            <div style={{
              position: "absolute", top: -80, right: -60,
              width: 320, height: 320, borderRadius: "50%",
              background: "radial-gradient(circle, rgba(59,130,246,0.2) 0%, transparent 70%)",
              pointerEvents: "none",
            }} />
            <div style={{
              position: "absolute", bottom: -60, left: -40,
              width: 260, height: 260, borderRadius: "50%",
              background: "radial-gradient(circle, rgba(14,165,233,0.15) 0%, transparent 70%)",
              pointerEvents: "none",
            }} />

            <div style={{ position: "relative", zIndex: 1, display: "flex", gap: 56, alignItems: "center", flexWrap: "wrap" }}>
              {/* Icon */}
              <div style={{
                width: 80, height: 80, borderRadius: 24, flexShrink: 0,
                background: "linear-gradient(135deg, rgba(59,130,246,0.3), rgba(14,165,233,0.2))",
                border: "1.5px solid rgba(59,130,246,0.3)",
                display: "flex", alignItems: "center", justifyContent: "center",
              }}>
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none">
                  <path d="M12 2a3 3 0 013 3v6a3 3 0 01-6 0V5a3 3 0 013-3z" stroke="#93c5fd" strokeWidth="1.6"/>
                  <path d="M19 10a7 7 0 01-14 0M12 19v3M9 22h6" stroke="#93c5fd" strokeWidth="1.6" strokeLinecap="round"/>
                </svg>
              </div>

              <div style={{ flex: 1 }}>
                <span style={{
                  display: "inline-block", fontSize: "0.72rem", fontWeight: 700,
                  color: "#fbbf24", background: "rgba(251,191,36,0.15)",
                  padding: "4px 12px", borderRadius: 20, marginBottom: 16,
                  border: "1px solid rgba(251,191,36,0.3)",
                }}>
                  Segera hadir
                </span>
                <div style={{ display: "flex", gap: 40, flexWrap: "wrap" }}>
                  {[
                    { label: "Berbasis suara", desc: "Simulasi wawancara real-time" },
                    { label: "Kontekstual", desc: "Tahu isi CV & loker kamu" },
                    { label: "Ada feedback", desc: "Review lengkap di akhir sesi" },
                  ].map((f, i) => (
                    <div key={f.label} style={{
                      opacity: interview.visible ? 1 : 0,
                      transform: interview.visible ? "translateY(0)" : "translateY(16px)",
                      transition: `opacity 0.45s ease ${0.25 + i * 0.1}s, transform 0.45s ease ${0.25 + i * 0.1}s`,
                    }}>
                      <div style={{ fontSize: "0.92rem", fontWeight: 700, color: "#fff", marginBottom: 4 }}>{f.label}</div>
                      <div style={{ fontSize: "0.82rem", color: "rgba(255,255,255,0.5)" }}>{f.desc}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
}
