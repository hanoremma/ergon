"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Nav from "../../components/Nav";
import Footer from "../../components/Footer";

// ─── Types ────────────────────────────────────────────────────────────────────

type Breakdown = {
  category: string;
  score: number | null;
  weight: string;
  detail?: string;
};

type Suggestion = {
  rank: number;
  title: string;
  detail: string;
  impact: string;
  category?: string;
  effort?: string;
  free: boolean;
};

type Result = {
  session_id: string;
  unlocked: boolean;
  job_data: Record<string, any>;
  company_data: Record<string, any> | null;
  scoring: {
    overall_score: number;
    label: string;
    range: string;
    disclaimer: string;
    breakdown: Breakdown[];
  };
  suggestions_free: Suggestion[];
  suggestions_locked_preview: { rank: number; title: string; impact?: string }[];
  suggestions_full: Suggestion[] | null;
};

// ─── Score Gauge SVG ──────────────────────────────────────────────────────────

function ScoreGauge({ score }: { score: number }) {
  // Arc from 180° to 0° (half circle), arc length depends on score
  const r = 52;
  const cx = 66, cy = 66;
  const circumference = Math.PI * r; // half circle
  const dashOffset = circumference * (1 - score / 100);

  return (
    <svg width="132" height="78" viewBox="0 0 132 78">
      <path
        d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
        fill="none" stroke="var(--line)" strokeWidth="9" strokeLinecap="round"
      />
      <path
        d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
        fill="none" stroke="var(--accent)" strokeWidth="9" strokeLinecap="round"
        strokeDasharray={`${circumference}`}
        strokeDashoffset={`${dashOffset}`}
        style={{ transition: "stroke-dashoffset 1s ease-out" }}
      />
    </svg>
  );
}

// ─── Breakdown Bar ────────────────────────────────────────────────────────────

function BreakdownBar({ item }: { item: Breakdown }) {
  const pct = item.score ?? 0;
  const color = pct >= 75 ? "var(--success)" : pct >= 50 ? "var(--accent)" : "#F59E0B";
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
        <div>
          <span style={{ fontSize: "0.88rem", fontWeight: 500, color: "var(--ink)" }}>{item.category}</span>
          <span style={{ fontSize: "0.76rem", color: "var(--muted)", marginLeft: 8 }}>{item.weight}</span>
        </div>
        <span style={{ fontSize: "0.88rem", fontWeight: 600, color: item.score === null ? "var(--muted)" : color }}>
          {item.score === null ? "N/A" : `${item.score}%`}
        </span>
      </div>
      <div style={{ height: 6, background: "var(--line)", borderRadius: 3, overflow: "hidden" }}>
        {item.score !== null && (
          <div style={{
            height: "100%", background: color, borderRadius: 3,
            width: `${pct}%`, transition: "width 1s ease-out",
          }} />
        )}
      </div>
      {item.detail && (
        <p style={{ fontSize: "0.76rem", color: "var(--muted)", marginTop: 4 }}>{item.detail}</p>
      )}
    </div>
  );
}

// ─── Suggestion Card ──────────────────────────────────────────────────────────

function SuggestionCard({ sug, locked = false }: { sug: Partial<Suggestion> & { rank: number; title: string }; locked?: boolean }) {
  return (
    <div style={{
      border: locked ? "1.5px solid var(--line)" : "1.5px solid var(--accent-soft)",
      borderRadius: 12, padding: "16px 18px",
      background: locked ? "var(--bg-page)" : "#fff",
      position: "relative",
      filter: locked ? "blur(0)" : "none",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
        <div style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
          <span style={{
            width: 24, height: 24, borderRadius: "50%", flexShrink: 0,
            background: locked ? "var(--line)" : "var(--accent)",
            color: "#fff", display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "0.7rem", fontWeight: 700,
          }}>
            {sug.rank}
          </span>
          <div>
            <div style={{
              fontSize: "0.9rem", fontWeight: 600, color: locked ? "var(--muted)" : "var(--ink)",
              filter: locked ? "blur(3px)" : "none",
            }}>
              {locked ? "•••••••••••••••••••••••" : sug.title}
            </div>
            {!locked && sug.detail && (
              <p style={{ fontSize: "0.84rem", color: "var(--ink-soft)", marginTop: 4 }}>{sug.detail}</p>
            )}
            {locked && (
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 6 }}>
                <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
                  <rect x="3.5" y="7" width="9" height="6.5" rx="1.4" stroke="var(--muted)" strokeWidth="1.4"/>
                  <path d="M5.5 7V5A2.5 2.5 0 0110.5 5V7" stroke="var(--muted)" strokeWidth="1.4"/>
                </svg>
                <span style={{ fontSize: "0.76rem", color: "var(--muted)" }}>Buka untuk lihat detail</span>
              </div>
            )}
          </div>
        </div>
        {sug.impact && (
          <span style={{
            flexShrink: 0, fontSize: "0.78rem", fontWeight: 600,
            color: locked ? "var(--muted)" : "var(--success)",
            background: locked ? "var(--line)" : "#ECFDF5",
            padding: "3px 9px", borderRadius: 20,
            filter: locked ? "blur(3px)" : "none",
          }}>
            {locked ? "+?%" : sug.impact}
          </span>
        )}
      </div>
    </div>
  );
}

// ─── Loading State ────────────────────────────────────────────────────────────

function LoadingDashboard({ progress }: { progress: Record<string, string> }) {
  const stages = [
    { key: "job_extraction", label: "Menganalisis loker" },
    { key: "company_intel", label: "Meriset perusahaan" },
    { key: "cv_parsing", label: "Membaca CV & portofolio" },
    { key: "scoring", label: "Menghitung kecocokan" },
  ];

  return (
    <div style={{ maxWidth: 520, margin: "80px auto", padding: "0 32px", textAlign: "center" }}>
      {/* Animated gauge placeholder */}
      <div style={{
        width: 100, height: 100, borderRadius: "50%",
        border: "3px solid var(--accent-soft)",
        borderTop: "3px solid var(--accent)",
        animation: "spin 1s linear infinite",
        margin: "0 auto 32px",
      }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>

      <h2 style={{ fontSize: "1.4rem", fontFamily: "'Space Grotesk', sans-serif", color: "var(--ink)", marginBottom: 8 }}>
        Sedang menganalisis...
      </h2>
      <p style={{ fontSize: "0.9rem", color: "var(--ink-soft)", marginBottom: 32 }}>
        Proses ini biasanya memakan waktu 15–60 detik.
      </p>

      <div style={{ display: "flex", flexDirection: "column", gap: 10, textAlign: "left" }}>
        {stages.map((stage) => {
          const status = progress[stage.key] || "pending";
          return (
            <div key={stage.key} style={{
              display: "flex", gap: 12, alignItems: "center",
              padding: "12px 16px", borderRadius: 10,
              background: status === "done" ? "#ECFDF5" : status === "running" ? "var(--accent-soft)" : "var(--bg-page)",
              border: `1px solid ${status === "done" ? "#A7F3D0" : status === "running" ? "var(--line)" : "var(--line)"}`,
            }}>
              <div style={{
                width: 8, height: 8, borderRadius: "50%", flexShrink: 0,
                background: status === "done" ? "var(--success)" : status === "running" ? "var(--accent)" : "var(--muted)",
              }} />
              <span style={{ fontSize: "0.88rem", color: status === "pending" ? "var(--muted)" : "var(--ink)" }}>
                {stage.label}
              </span>
              {status === "done" && <span style={{ marginLeft: "auto", fontSize: "0.76rem", color: "var(--success)" }}>Selesai</span>}
              {status === "running" && <span style={{ marginLeft: "auto", fontSize: "0.76rem", color: "var(--accent)" }}>Berjalan...</span>}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function ResultPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [status, setStatus] = useState<"loading" | "processing" | "complete" | "error">("loading");
  const [progress, setProgress] = useState<Record<string, string>>({});
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState("");

  // Poll for status
  useEffect(() => {
    if (!sessionId) return;
    let timer: ReturnType<typeof setTimeout>;

    async function poll() {
      try {
        const res = await fetch(`http://localhost:8000/api/analyze/${sessionId}/status`);
        if (!res.ok) throw new Error(`Status ${res.status}`);
        const data = await res.json();
        setProgress(data.progress || {});

        if (data.status === "complete") {
          setStatus("complete");
          const resultRes = await fetch(`http://localhost:8000/api/analyze/${sessionId}/result`);
          if (!resultRes.ok) throw new Error("Gagal mengambil hasil");
          const resultData = await resultRes.json();
          setResult(resultData);
        } else if (data.status === "error") {
          setStatus("error");
          setError(data.error || "Terjadi kesalahan saat analisis");
        } else {
          setStatus("processing");
          timer = setTimeout(poll, 2500);
        }
      } catch (err: any) {
        // Backend not available - show demo data
        console.warn("Backend not available, showing demo data");
        setStatus("complete");
        setResult(getDemoResult(sessionId));
      }
    }

    poll();
    return () => clearTimeout(timer);
  }, [sessionId]);

  if (status === "loading" || status === "processing") {
    return (
      <div style={{ background: "var(--bg-page)", minHeight: "100vh" }}>
        <Nav />
        <LoadingDashboard progress={progress} />
        <Footer />
      </div>
    );
  }

  if (status === "error") {
    return (
      <div style={{ background: "var(--bg-page)", minHeight: "100vh" }}>
        <Nav />
        <div style={{ maxWidth: 520, margin: "80px auto", padding: "0 32px", textAlign: "center" }}>
          <h2 style={{ color: "var(--ink)", fontFamily: "'Space Grotesk', sans-serif" }}>Terjadi kesalahan</h2>
          <p style={{ color: "var(--ink-soft)", marginTop: 8 }}>{error}</p>
          <button onClick={() => router.push("/upload")} style={{
            marginTop: 24, background: "var(--accent)", color: "#fff",
            padding: "12px 24px", borderRadius: 10, border: "none", cursor: "pointer",
          }}>
            Coba lagi
          </button>
        </div>
        <Footer />
      </div>
    );
  }

  if (!result) return null;

  const { scoring, suggestions_free, suggestions_locked_preview, suggestions_full, job_data, company_data, unlocked } = result;
  const allSuggestions = unlocked && suggestions_full ? suggestions_full : [
    ...suggestions_free,
    ...suggestions_locked_preview.map(s => ({ ...s, detail: "", impact: s.impact || "", category: "", effort: "", free: false })),
  ];

  return (
    <div style={{ background: "var(--bg-page)", minHeight: "100vh" }}>
      <Nav />

      <div style={{ maxWidth: 1000, margin: "0 auto", padding: "48px 32px 80px" }}>
        {/* Header */}
        <div style={{ marginBottom: 36 }}>
          {job_data?.position && (
            <div style={{
              display: "inline-flex", alignItems: "center", gap: 8,
              background: "var(--accent-soft)", borderRadius: 8,
              padding: "6px 14px", marginBottom: 12,
            }}>
              <span style={{ fontSize: "0.8rem", color: "var(--accent-deep)", fontWeight: 500 }}>
                {job_data.position}{job_data.company ? ` — ${job_data.company}` : ""}
              </span>
            </div>
          )}
          <h1 style={{ fontSize: "1.8rem", fontFamily: "'Space Grotesk', sans-serif", color: "var(--ink)" }}>
            Hasil analisis kecocokan CV
          </h1>
          <p style={{ color: "var(--ink-soft)", marginTop: 6, fontSize: "0.9rem" }}>
            {scoring.disclaimer}
          </p>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1.4fr", gap: 24, alignItems: "start" }}>
          {/* Left: Score */}
          <div>
            {/* Score Card */}
            <div style={{
              background: "var(--bg-hero)", borderRadius: 22,
              padding: "32px", marginBottom: 20, textAlign: "center",
            }}>
              <div style={{ position: "relative", display: "inline-block" }}>
                <ScoreGauge score={scoring.overall_score} />
                <div style={{
                  position: "absolute", bottom: 4, left: "50%",
                  transform: "translateX(-50%)",
                  fontFamily: "'Space Grotesk', sans-serif",
                  fontWeight: 700, fontSize: "2.4rem",
                  color: "var(--accent)",
                }}>
                  {scoring.overall_score}
                </div>
              </div>
              <div style={{
                fontFamily: "'Space Grotesk', sans-serif",
                fontSize: "1.1rem", fontWeight: 600,
                color: "var(--ink)", marginTop: 8,
              }}>
                {scoring.label}
              </div>
              <div style={{ fontSize: "0.82rem", color: "var(--muted)", marginTop: 4 }}>
                Estimasi rentang: {scoring.range}
              </div>
            </div>

            {/* Breakdown */}
            <div style={{
              background: "#fff", border: "1.5px solid var(--line)",
              borderRadius: 18, padding: "24px",
            }}>
              <h3 style={{
                fontSize: "0.95rem", fontFamily: "'Space Grotesk', sans-serif",
                color: "var(--ink)", marginBottom: 20,
              }}>
                Breakdown per kategori
              </h3>
              {scoring.breakdown.map((item, i) => (
                <BreakdownBar key={i} item={item} />
              ))}
            </div>

            {/* Company Intel */}
            {company_data?.available && (
              <div style={{
                background: "#fff", border: "1.5px solid var(--line)",
                borderRadius: 18, padding: "24px", marginTop: 20,
              }}>
                <h3 style={{
                  fontSize: "0.95rem", fontFamily: "'Space Grotesk', sans-serif",
                  color: "var(--ink)", marginBottom: 12,
                }}>
                  Konteks perusahaan
                </h3>
                <p style={{ fontSize: "0.86rem", color: "var(--ink-soft)", lineHeight: 1.6 }}>
                  {company_data.company_context}
                </p>
                {company_data.cv_recommendations?.length > 0 && (
                  <ul style={{ listStyle: "none", padding: 0, marginTop: 12, display: "flex", flexDirection: "column", gap: 6 }}>
                    {company_data.cv_recommendations.map((rec: string, i: number) => (
                      <li key={i} style={{ fontSize: "0.82rem", color: "var(--ink-soft)", display: "flex", gap: 6 }}>
                        <span style={{ color: "var(--accent)", flexShrink: 0 }}>→</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>

          {/* Right: Suggestions */}
          <div>
            <div style={{
              background: "#fff", border: "1.5px solid var(--line)",
              borderRadius: 18, padding: "28px",
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
                <h3 style={{ fontSize: "1rem", fontFamily: "'Space Grotesk', sans-serif", color: "var(--ink)" }}>
                  Saran perbaikan CV
                </h3>
                {!unlocked && (
                  <span style={{
                    fontSize: "0.76rem", color: "var(--success)",
                    background: "#ECFDF5", padding: "3px 9px", borderRadius: 20, fontWeight: 500,
                  }}>
                    3 teratas gratis
                  </span>
                )}
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {allSuggestions.map((sug, i) => (
                  <SuggestionCard
                    key={i}
                    sug={sug}
                    locked={!sug.free && !unlocked}
                  />
                ))}
              </div>

              {/* Paywall CTA */}
              {!unlocked && (
                <div style={{
                  background: "var(--ink)", borderRadius: 14,
                  padding: "24px", marginTop: 20,
                }}>
                  <div style={{ marginBottom: 12 }}>
                    <div style={{ fontSize: "0.78rem", color: "var(--muted)", marginBottom: 4 }}>
                      Buka versi lengkap
                    </div>
                    <h4 style={{
                      fontSize: "1rem", fontFamily: "'Space Grotesk', sans-serif",
                      color: "#fff", marginBottom: 6,
                    }}>
                      Semua saran + CV hasil revisi siap download
                    </h4>
                    <p style={{ fontSize: "0.84rem", color: "#DCD9F5", lineHeight: 1.5 }}>
                      Bayar sekali, dapat semua saran detail dan CV yang sudah dioptimalkan untuk loker ini.
                    </p>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 16 }}>
                    <span style={{
                      fontSize: "1.6rem", fontWeight: 700,
                      fontFamily: "'Space Grotesk', sans-serif", color: "#fff",
                    }}>
                      Rp 25.000
                    </span>
                    <span style={{ fontSize: "0.82rem", color: "var(--muted)" }}>per loker</span>
                  </div>
                  <button
                    onClick={() => router.push(`/unlock/${sessionId}`)}
                    style={{
                      width: "100%", padding: "14px",
                      background: "var(--accent)", color: "#fff",
                      border: "none", borderRadius: 10,
                      fontWeight: 600, fontSize: "0.95rem",
                      cursor: "pointer", fontFamily: "'Space Grotesk', sans-serif",
                      boxShadow: "0 8px 20px rgba(91,79,229,0.3)",
                    }}
                  >
                    Buka semua saran
                  </button>
                </div>
              )}

              {/* Download CTA if unlocked */}
              {unlocked && (
                <div style={{
                  background: "var(--bg-hero)", borderRadius: 14,
                  padding: "20px", marginTop: 20,
                  border: "1.5px solid var(--line)",
                }}>
                  <h4 style={{
                    fontSize: "0.95rem", fontFamily: "'Space Grotesk', sans-serif",
                    color: "var(--ink)", marginBottom: 8,
                  }}>
                    CV hasil revisi siap diunduh
                  </h4>
                  <div style={{ display: "flex", gap: 10 }}>
                    <a
                      href={`http://localhost:8000/api/download/${sessionId}?format=pdf`}
                      style={{
                        flex: 1, padding: "12px", background: "var(--accent)",
                        color: "#fff", borderRadius: 10, textAlign: "center",
                        fontWeight: 600, fontSize: "0.9rem",
                        display: "block",
                      }}
                    >
                      Unduh PDF
                    </a>
                    <a
                      href={`http://localhost:8000/api/download/${sessionId}?format=docx`}
                      style={{
                        flex: 1, padding: "12px", background: "#fff",
                        color: "var(--ink)", borderRadius: 10, textAlign: "center",
                        fontWeight: 600, fontSize: "0.9rem",
                        border: "1.5px solid var(--line)", display: "block",
                      }}
                    >
                      Unduh DOCX
                    </a>
                  </div>
                </div>
              )}
            </div>

            {/* Coming Soon banner */}
            <div style={{
              border: "1.5px dashed var(--line)", borderRadius: 18,
              padding: "22px 24px", marginTop: 20,
              background: "#fff",
              display: "flex", alignItems: "center", gap: 16,
            }}>
              <div style={{
                width: 44, height: 44, borderRadius: 12,
                background: "var(--accent-soft)",
                display: "flex", alignItems: "center", justifyContent: "center",
                flexShrink: 0, color: "var(--muted)",
              }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <rect x="5" y="10" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="1.6"/>
                  <path d="M8 10V7a4 4 0 018 0v3" stroke="currentColor" strokeWidth="1.6"/>
                </svg>
              </div>
              <div>
                <span style={{
                  display: "inline-block", fontSize: "0.7rem", fontWeight: 600,
                  color: "var(--accent-deep)", background: "var(--accent-soft)",
                  padding: "3px 9px", borderRadius: 20, marginBottom: 6,
                }}>
                  Segera hadir
                </span>
                <div style={{ fontSize: "0.9rem", fontWeight: 600, color: "var(--ink)", marginBottom: 4 }}>
                  Latihan wawancara AI — Premium
                </div>
                <p style={{ fontSize: "0.82rem", color: "var(--ink-soft)" }}>
                  Latihan wawancara berbasis suara menggunakan konteks loker & CV ini. Belum tersedia.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}

// ─── Demo Data (for when backend is not available) ───────────────────────────

function getDemoResult(sessionId: string): Result {
  return {
    session_id: sessionId,
    unlocked: false,
    job_data: {
      company: "PT Teknologi Maju",
      position: "Senior Product Manager",
      seniority: "senior",
      requirements_hard_skill: ["Product Roadmap", "Data Analysis", "SQL", "Figma", "OKR"],
      location: "Jakarta (Hybrid)",
    },
    company_data: {
      available: true,
      company_context: "PT Teknologi Maju baru saja mendapatkan pendanaan Series B sebesar $12M dan sedang dalam fase scaling produk mereka. Mereka membutuhkan PM senior untuk memimpin ekspansi ke pasar Southeast Asia.",
      cv_recommendations: [
        "Sebutkan pengalaman scaling produk ke pasar baru jika ada",
        "Highlight pengalaman bekerja dengan tim lintas fungsi (cross-functional)",
      ],
    },
    scoring: {
      overall_score: 72,
      label: "Sedang–Tinggi",
      range: "65–78%",
      disclaimer: "Estimasi berbasis kecocokan CV & loker, bukan jaminan hasil rekrutmen.",
      breakdown: [
        { category: "Keyword & Skill Coverage", score: 78, weight: "30%", detail: "Cocok: 4 dari 5 skill yang dibutuhkan" },
        { category: "Kecocokan Semantik Pengalaman", score: 70, weight: "25%", detail: "Kemiripan pengalaman dengan tanggung jawab loker" },
        { category: "Kesesuaian Level (Seniority)", score: 85, weight: "15%", detail: "CV: 5 tahun pengalaman | Loker: senior" },
        { category: "Relevansi Portofolio", score: 60, weight: "15%", detail: "Berdasarkan portofolio yang diunggah" },
        { category: "Kelengkapan & Kualitas CV", score: 65, weight: "5%", detail: "Beberapa achievement belum terukur" },
        { category: "Sinyal Kompetisi", score: null, weight: "10%", detail: "Data tidak tersedia" },
      ],
    },
    suggestions_free: [
      {
        rank: 1, title: "Tambahkan metrik kuantitatif ke pencapaian",
        detail: "Ubah 'meningkatkan engagement produk' menjadi 'meningkatkan MAU 35% dalam 3 bulan Q1 2025'. Loker ini fokus pada hasil terukur.",
        impact: "+8%", category: "experience", effort: "rendah", free: true,
      },
      {
        rank: 2, title: "Tambahkan keyword ATS yang hilang: SQL & OKR",
        detail: "Dua keyword krusial di job description ini tidak ditemukan di CV: 'SQL' dan 'OKR'. Jika kamu menguasainya, tambahkan secara eksplisit di bagian Skills dan beri contoh penggunaan.",
        impact: "+6%", category: "skill", effort: "rendah", free: true,
      },
      {
        rank: 3, title: "Perkuat professional summary untuk posisi senior",
        detail: "Tulis 2-3 kalimat yang langsung menyebutkan: level senior, domain product management, dan satu pencapaian terbesar yang relevan dengan posisi ini.",
        impact: "+5%", category: "format", effort: "sedang", free: true,
      },
    ],
    suggestions_locked_preview: [
      { rank: 4, title: "Susun ulang urutan skill sesuai prioritas loker", impact: "+4%" },
      { rank: 5, title: "Format ulang bullet pengalaman dengan pola STAR", impact: "+4%" },
      { rank: 6, title: "Tambahkan proyek portofolio yang relevan", impact: "+3%" },
    ],
    suggestions_full: null,
  };
}
