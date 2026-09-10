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
      { threshold: 0.12 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);
  return { ref, visible };
}

const steps = [
  { num: "1", title: "Upload loker & CV", desc: "Tempel link, upload PDF, atau screenshot loker. Sertakan juga CV dan portofolio kamu." },
  { num: "2", title: "Ergon membaca semuanya", desc: "AI mengekstrak syarat loker, meriset perusahaan, dan memetakan pengalamanmu." },
  { num: "3", title: "Lihat skor & saran", desc: "Skor kecocokan lengkap dengan alasannya, plus 3 saran perbaikan gratis." },
  { num: "4", title: "Kirim CV yang sudah pas", desc: "Buka semua saran dan unduh laporan lengkap, siap dikirim ke perusahaan." },
];

export default function DashboardSections() {
  const how = useReveal();
  const pricing = useReveal();
  const interview = useReveal();

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>

      {/* ── Cara kerja ─────────────────────────────────────────────── */}
      <section id="how" style={{ padding: "96px 0 88px" }}>
        <div
          ref={how.ref}
          style={{
            opacity: how.visible ? 1 : 0,
            transform: how.visible ? "translateY(0)" : "translateY(32px)",
            transition: "opacity 0.65s ease, transform 0.65s ease",
          }}
        >
          <div style={{ maxWidth: 480, marginBottom: 52 }}>
            <div style={{
              display: "inline-block", fontSize: "0.76rem", fontWeight: 700,
              color: "var(--accent)", background: "var(--accent-soft)",
              padding: "4px 12px", borderRadius: 20, marginBottom: 16,
              border: "1px solid var(--line)", letterSpacing: "0.04em",
            }}>
              Cara kerja
            </div>
            <h2 style={{ fontSize: "1.9rem", color: "var(--ink)", lineHeight: 1.2, letterSpacing: "-0.02em" }}>
              Empat langkah, dari loker sampai CV siap kirim
            </h2>
            <p style={{ marginTop: 14, fontSize: "0.97rem", color: "var(--ink-soft)", lineHeight: 1.65 }}>
              Semua proses berjalan otomatis — kamu tinggal upload dan baca hasilnya.
            </p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", position: "relative", gap: 8 }}>
            <div style={{
              position: "absolute", top: 19, left: 20, right: 20,
              height: 1.5, background: "var(--line)", zIndex: 0,
            }} />
            {steps.map((step, i) => (
              <div
                key={i}
                style={{
                  position: "relative", zIndex: 1, paddingRight: 20,
                  opacity: how.visible ? 1 : 0,
                  transform: how.visible ? "translateY(0)" : "translateY(20px)",
                  transition: `opacity 0.5s ease ${0.15 + i * 0.1}s, transform 0.5s ease ${0.15 + i * 0.1}s`,
                }}
              >
                <div style={{
                  width: 40, height: 40, borderRadius: "50%",
                  background: i === 0 ? "var(--accent)" : "#fff",
                  border: i === 0 ? "none" : "1.5px solid var(--line)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontWeight: 700, fontSize: "0.92rem", marginBottom: 20,
                  color: i === 0 ? "#fff" : "var(--ink-soft)",
                }}>
                  {step.num}
                </div>
                <h3 style={{ fontSize: "1rem", marginBottom: 8, color: "var(--ink)", fontWeight: 600 }}>{step.title}</h3>
                <p style={{ fontSize: "0.9rem", color: "var(--ink-soft)", lineHeight: 1.6 }}>{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Divider */}
      <div style={{ height: 1, background: "var(--line)", margin: "0" }} />

      {/* ── Harga ───────────────────────────────────────────────────── */}
      <section id="unlock" style={{ padding: "96px 0 88px" }}>
        <div
          ref={pricing.ref}
          style={{
            opacity: pricing.visible ? 1 : 0,
            transform: pricing.visible ? "translateY(0)" : "translateY(32px)",
            transition: "opacity 0.65s ease, transform 0.65s ease",
          }}
        >
          <div style={{ maxWidth: 480, marginBottom: 52 }}>
            <div style={{
              display: "inline-block", fontSize: "0.76rem", fontWeight: 700,
              color: "var(--accent)", background: "var(--accent-soft)",
              padding: "4px 12px", borderRadius: 20, marginBottom: 16,
              border: "1px solid var(--line)", letterSpacing: "0.04em",
            }}>
              Harga
            </div>
            <h2 style={{ fontSize: "1.9rem", color: "var(--ink)", lineHeight: 1.2, letterSpacing: "-0.02em" }}>
              Mulai gratis, buka semuanya kalau sudah yakin
            </h2>
            <p style={{ marginTop: 14, fontSize: "0.97rem", color: "var(--ink-soft)", lineHeight: 1.65 }}>
              Skor dan tiga saran teratas selalu gratis. Butuh lebih dari itu, baru bayar.
            </p>
          </div>

          <div
            style={{
              display: "grid", gridTemplateColumns: "1fr 1.15fr", gap: 24, alignItems: "stretch",
              opacity: pricing.visible ? 1 : 0,
              transform: pricing.visible ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 0.55s ease 0.15s, transform 0.55s ease 0.15s",
            }}
          >
            {/* Free */}
            <div style={{
              background: "#fff", border: "1.5px solid var(--line)",
              borderRadius: 20, padding: "32px 30px",
            }}>
              <div style={{
                display: "inline-block", fontSize: "0.76rem", fontWeight: 600,
                color: "var(--ink-soft)", background: "var(--bg-page)",
                padding: "4px 12px", borderRadius: 20, marginBottom: 20,
                border: "1px solid var(--line)",
              }}>
                Gratis
              </div>
              <h3 style={{ fontSize: "1.2rem", color: "var(--ink)", marginBottom: 6, fontWeight: 700 }}>Skor kecocokan penuh</h3>
              <ul style={{ listStyle: "none", margin: "20px 0 0", padding: 0, display: "flex", flexDirection: "column", gap: 12 }}>
                {[
                  "Skor kecocokan & alasannya per kategori",
                  "3 saran perbaikan berdampak paling besar",
                  "Bisa dicoba untuk berapa pun loker",
                ].map((item) => (
                  <li key={item} style={{ display: "flex", gap: 10, alignItems: "flex-start", fontSize: "0.92rem", color: "var(--ink-soft)" }}>
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ flexShrink: 0, marginTop: 3 }}>
                      <circle cx="8" cy="8" r="6.4" stroke="#15803D" strokeWidth="1.5"/>
                      <path d="M5.3 8.2L7.1 10L10.6 6" stroke="#15803D" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* Paid */}
            <div style={{
              background: "var(--ink)", borderRadius: 20, padding: "32px 30px",
              position: "relative", overflow: "hidden",
            }}>
              <div style={{
                display: "inline-block", fontSize: "0.76rem", fontWeight: 600,
                color: "var(--muted)", background: "rgba(255,255,255,0.08)",
                padding: "4px 12px", borderRadius: 20, marginBottom: 20,
              }}>
                Buka versi lengkap
              </div>
              <h3 style={{ fontSize: "1.2rem", color: "#fff", marginBottom: 6, fontWeight: 700 }}>Semua saran + laporan lengkap hasil analisis</h3>

              {/* Price display */}
              <div style={{ margin: "20px 0 4px", display: "flex", alignItems: "baseline", gap: 8 }}>
                <span style={{ fontSize: "2.2rem", fontWeight: 800, color: "#fff", letterSpacing: "-0.04em", lineHeight: 1 }}>
                  Rp 25.000
                </span>
                <span style={{ fontSize: "0.82rem", color: "var(--muted)" }}>sekali bayar per loker</span>
              </div>
              <p style={{ fontSize: "0.8rem", color: "var(--muted)", marginBottom: 20 }}>
                Tidak perlu berlangganan.
              </p>

              <ul style={{ listStyle: "none", margin: "0 0 0", padding: 0, display: "flex", flexDirection: "column", gap: 12 }}>
                {[
                  "Semua saran perbaikan, bukan cuma 3 teratas",
                  "Laporan lengkap, siap diunduh sebagai PDF",
                ].map((item) => (
                  <li key={item} style={{ display: "flex", gap: 10, alignItems: "flex-start", fontSize: "0.92rem", color: "#B8D4EE" }}>
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ flexShrink: 0, marginTop: 3 }}>
                      <circle cx="8" cy="8" r="6.4" stroke="#B8D4EE" strokeWidth="1.5"/>
                      <path d="M5.3 8.2L7.1 10L10.6 6" stroke="#B8D4EE" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    {item}
                  </li>
                ))}
              </ul>
              {["Kuantifikasi pencapaian di baris pengalaman kedua", "Susun ulang urutan skill sesuai prioritas loker"].map((text) => (
                <div key={text} style={{
                  display: "flex", gap: 10, alignItems: "center",
                  padding: "10px 12px", borderRadius: 8,
                  background: "rgba(255,255,255,0.06)", marginTop: 8,
                  filter: "blur(0.3px)",
                }}>
                  <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
                    <rect x="3.5" y="7" width="9" height="6.5" rx="1.4" stroke="var(--muted)" strokeWidth="1.4"/>
                    <path d="M5.5 7V5A2.5 2.5 0 0110.5 5V7" stroke="var(--muted)" strokeWidth="1.4"/>
                  </svg>
                  <span style={{ fontSize: "0.84rem", color: "var(--muted)" }}>{text}</span>
                </div>
              ))}
              <Link href="/upload" style={{
                background: "var(--accent)", color: "#fff",
                padding: "14px 26px", borderRadius: 10,
                fontWeight: 600, fontSize: "0.96rem",
                display: "inline-block", marginTop: 24,
              }}>
                Buka versi lengkap
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Divider */}
      <div style={{ height: 1, background: "var(--line)" }} />

      {/* ── Wawancara AI ────────────────────────────────────────────── */}
      <section id="soon" style={{ padding: "96px 0 88px" }}>
        <div
          ref={interview.ref}
          style={{
            opacity: interview.visible ? 1 : 0,
            transform: interview.visible ? "translateY(0)" : "translateY(32px)",
            transition: "opacity 0.65s ease, transform 0.65s ease",
          }}
        >
          <div style={{ maxWidth: 480, marginBottom: 52 }}>
            <div style={{
              display: "inline-block", fontSize: "0.76rem", fontWeight: 700,
              color: "var(--accent)", background: "var(--accent-soft)",
              padding: "4px 12px", borderRadius: 20, marginBottom: 16,
              border: "1px solid var(--line)", letterSpacing: "0.04em",
            }}>
              Wawancara AI
            </div>
            <h2 style={{ fontSize: "1.9rem", color: "var(--ink)", lineHeight: 1.2, letterSpacing: "-0.02em" }}>
              Latihan wawancara bareng AI
            </h2>
            <p style={{ marginTop: 14, fontSize: "0.97rem", color: "var(--ink-soft)", lineHeight: 1.65 }}>
              Ngobrol langsung pakai suara dengan AI yang sudah tahu isi loker, riset perusahaan, dan CV kamu — lengkap dengan feedback di akhir sesi.
            </p>
          </div>

          <div
            style={{
              border: "1.5px solid var(--line)", borderRadius: 20,
              padding: "40px 44px", background: "#fff",
              display: "flex", alignItems: "center", gap: 44,
              opacity: interview.visible ? 1 : 0,
              transform: interview.visible ? "translateY(0)" : "translateY(20px)",
              transition: "opacity 0.55s ease 0.15s, transform 0.55s ease 0.15s",
            }}
          >
            <div style={{
              width: 72, height: 72, borderRadius: 20, flexShrink: 0,
              background: "var(--accent-soft)", color: "var(--accent)",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <rect x="5" y="10" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="1.6"/>
                <path d="M8 10V7a4 4 0 018 0v3" stroke="currentColor" strokeWidth="1.6"/>
              </svg>
            </div>
            <div>
              <span style={{
                display: "inline-block", fontSize: "0.72rem", fontWeight: 600,
                color: "var(--accent-deep)", background: "var(--accent-soft)",
                padding: "3px 10px", borderRadius: 20, marginBottom: 14,
                border: "1px solid var(--line)",
              }}>
                Segera hadir
              </span>
              <div style={{ display: "flex", gap: 32, flexWrap: "wrap" }}>
                {[
                  { label: "Berbasis suara", desc: "Simulasi wawancara real-time" },
                  { label: "Kontekstual", desc: "Tahu isi CV & loker kamu" },
                  { label: "Ada feedback", desc: "Review lengkap di akhir sesi" },
                ].map((f, i) => (
                  <div
                    key={f.label}
                    style={{
                      opacity: interview.visible ? 1 : 0,
                      transform: interview.visible ? "translateY(0)" : "translateY(12px)",
                      transition: `opacity 0.45s ease ${0.3 + i * 0.1}s, transform 0.45s ease ${0.3 + i * 0.1}s`,
                    }}
                  >
                    <div style={{ fontSize: "0.9rem", fontWeight: 700, color: "var(--ink)", marginBottom: 3 }}>{f.label}</div>
                    <div style={{ fontSize: "0.82rem", color: "var(--muted)" }}>{f.desc}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
}
