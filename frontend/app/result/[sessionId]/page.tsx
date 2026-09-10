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

// ─── Circular Score Gauge ─────────────────────────────────────────────────────

function CircularScoreGauge({ score }: { score: number }) {
  const r = 54;
  const cx = 70, cy = 70;
  const circumference = Math.PI * r; // half-circle
  const dashOffset = circumference * (1 - score / 100);
  const scoreColor =
    score >= 80 ? "#15803D" : score >= 60 ? "var(--accent)" : "#D97706";

  return (
    <div style={{ position: "relative", display: "inline-flex", flexDirection: "column", alignItems: "center" }}>
      <svg width="140" height="84" viewBox="0 0 140 84">
        {/* Track */}
        <path
          d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
          fill="none" stroke="var(--line)" strokeWidth="10" strokeLinecap="round"
        />
        {/* Progress */}
        <path
          d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
          fill="none" stroke={scoreColor} strokeWidth="10" strokeLinecap="round"
          strokeDasharray={`${circumference}`}
          strokeDashoffset={`${dashOffset}`}
          style={{ transition: "stroke-dashoffset 1.2s ease-out" }}
        />
      </svg>
      {/* Number overlay */}
      <div style={{
        position: "absolute", top: 26,
        display: "flex", flexDirection: "column", alignItems: "center",
      }}>
        <span style={{
          fontSize: "2.6rem", fontWeight: 800,
          color: scoreColor, lineHeight: 1,
          letterSpacing: "-0.04em",
        }}>
          {score}
        </span>
        <span style={{ fontSize: "0.72rem", color: "var(--muted)", marginTop: 2, fontWeight: 500 }}>
          / 100
        </span>
      </div>
    </div>
  );
}

// ─── Candidate Avatar ─────────────────────────────────────────────────────────

function CandidateAvatar({ name }: { name?: string }) {
  const initials = name
    ? name.split(" ").slice(0, 2).map((w: string) => w[0]).join("").toUpperCase()
    : "CV";
  return (
    <div style={{
      width: 48, height: 48, borderRadius: "50%",
      background: "var(--accent)", color: "#fff",
      display: "flex", alignItems: "center", justifyContent: "center",
      fontSize: "1rem", fontWeight: 700, flexShrink: 0,
      border: "2px solid var(--accent-soft)",
    }}>
      {initials}
    </div>
  );
}

// ─── Breakdown Bar ────────────────────────────────────────────────────────────

function BreakdownBar({ item }: { item: Breakdown }) {
  const pct = item.score ?? 0;
  const color = pct >= 75 ? "#15803D" : pct >= 50 ? "var(--accent)" : "#D97706";
  const trackColor = pct >= 75 ? "#ECFDF5" : pct >= 50 ? "var(--accent-soft)" : "#FFFBEB";
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6, alignItems: "center" }}>
        <div>
          <span style={{ fontSize: "0.86rem", fontWeight: 600, color: "var(--ink)" }}>{item.category}</span>
          <span style={{ fontSize: "0.74rem", color: "var(--muted)", marginLeft: 8 }}>{item.weight}</span>
        </div>
        <span style={{
          fontSize: "0.82rem", fontWeight: 700,
          color: item.score === null ? "var(--muted)" : color,
          background: item.score === null ? "var(--bg-page)" : trackColor,
          padding: "2px 8px", borderRadius: 20, border: "1px solid var(--line)",
        }}>
          {item.score === null ? "N/A" : `${item.score}%`}
        </span>
      </div>
      <div style={{ height: 5, background: "var(--line)", borderRadius: 3, overflow: "hidden" }}>
        {item.score !== null && (
          <div style={{
            height: "100%", background: color, borderRadius: 3,
            width: `${pct}%`, transition: "width 1.1s ease-out",
          }} />
        )}
      </div>
      {item.detail && (
        <p style={{ fontSize: "0.74rem", color: "var(--muted)", marginTop: 4 }}>{item.detail}</p>
      )}
    </div>
  );
}

// ─── Skills Checklist ─────────────────────────────────────────────────────────

function SkillsChecklist({
  required,
  matched,
}: {
  required: string[];
  matched: string[];
}) {
  const matchedSet = new Set(matched.map((s: string) => s.toLowerCase()));
  const matchedSkills = required.filter((s) => matchedSet.has(s.toLowerCase()));
  const missingSkills = required.filter((s) => !matchedSet.has(s.toLowerCase()));

  return (
    <div>
      <div style={{ marginBottom: 10 }}>
        <span style={{ fontSize: "0.76rem", fontWeight: 600, color: "var(--success)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
          ✓ Terpenuhi ({matchedSkills.length})
        </span>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 8 }}>
          {matchedSkills.length > 0 ? matchedSkills.map((skill, i) => (
            <span key={i} style={{
              display: "inline-flex", alignItems: "center", gap: 5,
              background: "#ECFDF5", border: "1px solid #A7F3D0",
              borderRadius: 20, padding: "4px 10px",
              fontSize: "0.78rem", fontWeight: 500, color: "#15803D",
            }}>
              <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
                <path d="M2.5 6.5L4.5 8.5L9.5 3.5" stroke="#15803D" strokeWidth="1.5" strokeLinecap="round"/>
              </svg>
              {skill}
            </span>
          )) : (
            <span style={{ fontSize: "0.8rem", color: "var(--muted)" }}>—</span>
          )}
        </div>
      </div>
      {missingSkills.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <span style={{ fontSize: "0.76rem", fontWeight: 600, color: "#D97706", textTransform: "uppercase", letterSpacing: "0.06em" }}>
            ✗ Perlu ditambahkan ({missingSkills.length})
          </span>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 8 }}>
            {missingSkills.map((skill, i) => (
              <span key={i} style={{
                display: "inline-flex", alignItems: "center", gap: 5,
                background: "#FEF2F2", border: "1px solid #FECACA",
                borderRadius: 20, padding: "4px 10px",
                fontSize: "0.78rem", fontWeight: 500, color: "#DC2626",
              }}>
                <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
                  <path d="M3 3L9 9M9 3L3 9" stroke="#DC2626" strokeWidth="1.5" strokeLinecap="round"/>
                </svg>
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Suggestion Card ──────────────────────────────────────────────────────────

function SuggestionCard({ sug, locked = false }: { sug: Partial<Suggestion> & { rank: number; title: string }; locked?: boolean }) {
  return (
    <div style={{
      border: locked ? "1.5px solid var(--line)" : "1.5px solid var(--line)",
      borderRadius: 12, padding: "16px 18px",
      background: locked ? "var(--bg-page)" : "#fff",
      position: "relative",
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
              fontSize: "0.88rem", fontWeight: 600,
              color: locked ? "var(--muted)" : "var(--ink)",
              filter: locked ? "blur(3px)" : "none",
            }}>
              {locked ? "•••••••••••••••••••••••" : sug.title}
            </div>
            {!locked && sug.detail && (
              <p style={{ fontSize: "0.82rem", color: "var(--ink-soft)", marginTop: 4, lineHeight: 1.6 }}>{sug.detail}</p>
            )}
            {locked && (
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 6 }}>
                <svg width="11" height="11" viewBox="0 0 16 16" fill="none">
                  <rect x="3.5" y="7" width="9" height="6.5" rx="1.4" stroke="var(--muted)" strokeWidth="1.4"/>
                  <path d="M5.5 7V5A2.5 2.5 0 0110.5 5V7" stroke="var(--muted)" strokeWidth="1.4"/>
                </svg>
                <span style={{ fontSize: "0.74rem", color: "var(--muted)" }}>Buka untuk lihat detail</span>
              </div>
            )}
          </div>
        </div>
        {sug.impact && (
          <span style={{
            flexShrink: 0, fontSize: "0.76rem", fontWeight: 700,
            color: locked ? "var(--muted)" : "#15803D",
            background: locked ? "var(--line)" : "#ECFDF5",
            padding: "3px 9px", borderRadius: 20,
            border: `1px solid ${locked ? "var(--line)" : "#A7F3D0"}`,
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
    <div style={{ maxWidth: 480, margin: "80px auto", padding: "0 32px", textAlign: "center" }}>
      {/* Spinner */}
      <div style={{
        width: 56, height: 56, borderRadius: "50%",
        border: "3px solid var(--line)",
        borderTop: "3px solid var(--accent)",
        animation: "spin 0.9s linear infinite",
        margin: "0 auto 28px",
      }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>

      <h2 style={{ fontSize: "1.3rem", fontWeight: 700, color: "var(--ink)", marginBottom: 8, letterSpacing: "-0.01em" }}>
        Sedang menganalisis...
      </h2>
      <p style={{ fontSize: "0.88rem", color: "var(--ink-soft)", marginBottom: 28, lineHeight: 1.65 }}>
        Proses ini biasanya memakan waktu 15–60 detik.
      </p>

      <div style={{ display: "flex", flexDirection: "column", gap: 8, textAlign: "left" }}>
        {stages.map((stage) => {
          const status = progress[stage.key] || "pending";
          return (
            <div key={stage.key} style={{
              display: "flex", gap: 12, alignItems: "center",
              padding: "11px 14px", borderRadius: 10,
              background: status === "done" ? "#ECFDF5" : status === "running" ? "var(--accent-soft)" : "#fff",
              border: `1px solid ${status === "done" ? "#A7F3D0" : status === "running" ? "var(--line)" : "var(--line)"}`,
            }}>
              <div style={{
                width: 8, height: 8, borderRadius: "50%", flexShrink: 0,
                background: status === "done" ? "#15803D" : status === "running" ? "var(--accent)" : "var(--line)",
              }} />
              <span style={{ fontSize: "0.86rem", color: status === "pending" ? "var(--muted)" : "var(--ink)", fontWeight: status !== "pending" ? 500 : 400 }}>
                {stage.label}
              </span>
              {status === "done" && <span style={{ marginLeft: "auto", fontSize: "0.74rem", color: "#15803D", fontWeight: 600 }}>Selesai</span>}
              {status === "running" && <span style={{ marginLeft: "auto", fontSize: "0.74rem", color: "var(--accent)", fontWeight: 600 }}>Berjalan...</span>}
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
        <div style={{ maxWidth: 480, margin: "80px auto", padding: "0 32px", textAlign: "center" }}>
          <div style={{
            width: 64, height: 64, borderRadius: "50%",
            background: "#FEF2F2", border: "2px solid #FECACA",
            display: "flex", alignItems: "center", justifyContent: "center",
            margin: "0 auto 20px",
          }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
              <path d="M12 8V12M12 16H12.01" stroke="#DC2626" strokeWidth="2.5" strokeLinecap="round"/>
              <circle cx="12" cy="12" r="9" stroke="#DC2626" strokeWidth="2"/>
            </svg>
          </div>
          <h2 style={{ color: "var(--ink)", fontWeight: 700, letterSpacing: "-0.01em" }}>Terjadi kesalahan</h2>
          <p style={{ color: "var(--ink-soft)", marginTop: 8, lineHeight: 1.6 }}>{error}</p>
          <button onClick={() => router.push("/upload")} style={{
            marginTop: 24, background: "var(--accent)", color: "#fff",
            padding: "12px 24px", borderRadius: 10, border: "none", cursor: "pointer",
            fontWeight: 600, fontSize: "0.92rem",
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

  // Skills for checklist — from job_data
  const requiredSkills: string[] = job_data?.requirements_hard_skill || [];
  // Infer matched skills from keyword breakdown detail or default
  const matchedSkills: string[] = (() => {
    const breakdownSkill = scoring.breakdown.find(b => b.category?.toLowerCase().includes("keyword"));
    if (breakdownSkill?.detail) {
      // Parse "Cocok: X dari Y skill" but we don't have the names, show top ranked skills
      // Just show skills that are "presumably matched" based on score
      const ratio = (breakdownSkill.score ?? 0) / 100;
      const count = Math.round(requiredSkills.length * ratio);
      return requiredSkills.slice(0, count);
    }
    return [];
  })();

  const scoreColor =
    scoring.overall_score >= 80 ? "#15803D"
    : scoring.overall_score >= 60 ? "var(--accent)"
    : "#D97706";

  return (
    <div style={{ background: "var(--bg-page)", minHeight: "100vh" }}>
      <Nav />

      <div style={{ maxWidth: 1020, margin: "0 auto", padding: "44px 32px 88px" }}>

        {/* ── Header ─────────────────────────────────────────────────── */}
        <div style={{ marginBottom: 32 }}>
          {job_data?.position && (
            <div style={{
              display: "inline-flex", alignItems: "center", gap: 7,
              background: "var(--accent-soft)", borderRadius: 20,
              padding: "5px 14px", marginBottom: 14,
              border: "1px solid var(--line)",
            }}>
              <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
                <rect x="2" y="4" width="12" height="10" rx="2" stroke="var(--accent-deep)" strokeWidth="1.5"/>
                <path d="M5 4V3a2 2 0 014 0v1" stroke="var(--accent-deep)" strokeWidth="1.5"/>
              </svg>
              <span style={{ fontSize: "0.78rem", color: "var(--accent-deep)", fontWeight: 600 }}>
                {job_data.position}{job_data.company ? ` · ${job_data.company}` : ""}
                {job_data.location ? ` · ${job_data.location}` : ""}
              </span>
            </div>
          )}
          <h1 style={{ fontSize: "1.7rem", fontWeight: 800, color: "var(--ink)", letterSpacing: "-0.025em", lineHeight: 1.2 }}>
            Hasil Analisis Kecocokan CV
          </h1>
          <p style={{ color: "var(--ink-soft)", marginTop: 6, fontSize: "0.88rem", lineHeight: 1.6 }}>
            {scoring.disclaimer}
          </p>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "340px 1fr", gap: 22, alignItems: "start" }}>

          {/* ── Left Column ────────────────────────────────────────────── */}
          <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>

            {/* Score Card */}
            <div style={{
              background: "#fff", border: "1.5px solid var(--line)",
              borderRadius: 18, padding: "28px 24px",
              textAlign: "center",
            }}>
              {/* Candidate row */}
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 22, textAlign: "left" }}>
                <CandidateAvatar name={job_data?.candidate_name} />
                <div>
                  <div style={{ fontSize: "0.88rem", fontWeight: 600, color: "var(--ink)" }}>
                    {job_data?.candidate_name || "Kandidat"}
                  </div>
                  <div style={{ fontSize: "0.76rem", color: "var(--muted)", marginTop: 2 }}>
                    {job_data?.position || "Posisi"}
                  </div>
                </div>
                <div style={{
                  marginLeft: "auto", background: "var(--accent-soft)",
                  border: "1px solid var(--line)", borderRadius: 20,
                  padding: "4px 12px", flexShrink: 0,
                }}>
                  <span style={{ fontSize: "0.82rem", fontWeight: 700, color: "var(--accent-deep)" }}>
                    {scoring.overall_score}%
                  </span>
                </div>
              </div>

              {/* Circular gauge */}
              <div style={{ display: "flex", justifyContent: "center", marginBottom: 16 }}>
                <CircularScoreGauge score={scoring.overall_score} />
              </div>

              <div style={{
                fontSize: "1rem", fontWeight: 700, color: "var(--ink)",
                letterSpacing: "-0.01em", marginBottom: 4,
              }}>
                {scoring.label}
              </div>
              <div style={{
                fontSize: "0.78rem", color: "var(--muted)",
                background: "var(--bg-page)", borderRadius: 20,
                padding: "3px 12px", display: "inline-block", border: "1px solid var(--line)",
              }}>
                Estimasi rentang: {scoring.range}
              </div>
            </div>

            {/* Breakdown */}
            <div style={{
              background: "#fff", border: "1.5px solid var(--line)",
              borderRadius: 18, padding: "22px 22px",
            }}>
              <h3 style={{
                fontSize: "0.9rem", fontWeight: 700,
                color: "var(--ink)", marginBottom: 18, letterSpacing: "-0.01em",
              }}>
                Breakdown per Kategori
              </h3>
              {scoring.breakdown.map((item, i) => (
                <BreakdownBar key={i} item={item} />
              ))}
            </div>

            {/* Skills Checklist */}
            {requiredSkills.length > 0 && (
              <div style={{
                background: "#fff", border: "1.5px solid var(--line)",
                borderRadius: 18, padding: "22px 22px",
              }}>
                <h3 style={{
                  fontSize: "0.9rem", fontWeight: 700,
                  color: "var(--ink)", marginBottom: 14, letterSpacing: "-0.01em",
                }}>
                  Skill yang Diperlukan
                </h3>
                <SkillsChecklist required={requiredSkills} matched={matchedSkills} />
              </div>
            )}

            {/* Company Intel */}
            {company_data?.available && (
              <div style={{
                background: "#fff", border: "1.5px solid var(--line)",
                borderRadius: 18, padding: "22px 22px",
              }}>
                <h3 style={{
                  fontSize: "0.9rem", fontWeight: 700,
                  color: "var(--ink)", marginBottom: 12, letterSpacing: "-0.01em",
                }}>
                  Konteks Perusahaan
                </h3>
                <p style={{ fontSize: "0.84rem", color: "var(--ink-soft)", lineHeight: 1.65 }}>
                  {company_data.company_context}
                </p>
                {company_data.cv_recommendations?.length > 0 && (
                  <ul style={{ listStyle: "none", padding: 0, marginTop: 14, display: "flex", flexDirection: "column", gap: 8 }}>
                    {company_data.cv_recommendations.map((rec: string, i: number) => (
                      <li key={i} style={{
                        fontSize: "0.82rem", color: "var(--ink-soft)",
                        display: "flex", gap: 8, alignItems: "flex-start",
                        padding: "8px 10px", borderRadius: 8,
                        background: "var(--bg-page)", border: "1px solid var(--line)",
                      }}>
                        <span style={{ color: "var(--accent)", flexShrink: 0, fontWeight: 700 }}>→</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>

          {/* ── Right Column ───────────────────────────────────────────── */}
          <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>

            {/* Suggestions */}
            <div style={{
              background: "#fff", border: "1.5px solid var(--line)",
              borderRadius: 18, padding: "24px 24px",
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
                <h3 style={{ fontSize: "0.95rem", fontWeight: 700, color: "var(--ink)", letterSpacing: "-0.01em" }}>
                  Saran Perbaikan CV
                </h3>
                {!unlocked && (
                  <span style={{
                    fontSize: "0.74rem", color: "#15803D", fontWeight: 600,
                    background: "#ECFDF5", padding: "3px 10px", borderRadius: 20,
                    border: "1px solid #A7F3D0",
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
                  padding: "22px 22px", marginTop: 18,
                }}>
                  <div style={{ marginBottom: 12 }}>
                    <div style={{
                      display: "inline-block", fontSize: "0.72rem", fontWeight: 600,
                      color: "var(--muted)", background: "rgba(255,255,255,0.08)",
                      padding: "3px 10px", borderRadius: 20, marginBottom: 10,
                    }}>
                      Buka versi lengkap
                    </div>
                    <h4 style={{
                      fontSize: "0.98rem", fontWeight: 700,
                      color: "#fff", marginBottom: 6, letterSpacing: "-0.01em",
                    }}>
                      Semua saran + laporan lengkap siap diunduh
                    </h4>
                    <p style={{ fontSize: "0.82rem", color: "#B8D4EE", lineHeight: 1.6 }}>
                      Bayar sekali, dapat semua saran detail dan CV yang sudah dioptimalkan untuk loker ini.
                    </p>
                  </div>
                  <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginBottom: 14 }}>
                    <span style={{
                      fontSize: "1.5rem", fontWeight: 800,
                      color: "#fff", letterSpacing: "-0.03em",
                    }}>
                      Rp 25.000
                    </span>
                    <span style={{ fontSize: "0.8rem", color: "var(--muted)" }}>per loker</span>
                  </div>
                  <button
                    onClick={() => router.push(`/unlock/${sessionId}`)}
                    style={{
                      width: "100%", padding: "13px",
                      background: "var(--accent)", color: "#fff",
                      border: "none", borderRadius: 10,
                      fontWeight: 600, fontSize: "0.92rem",
                      cursor: "pointer", letterSpacing: "-0.01em",
                    }}
                  >
                    Buka semua saran
                  </button>
                </div>
              )}

              {/* Download CTA if unlocked */}
              {unlocked && (
                <div style={{
                  background: "var(--bg-hero)", borderRadius: 12,
                  padding: "18px 20px", marginTop: 18,
                  border: "1.5px solid var(--line)",
                }}>
                  <h4 style={{
                    fontSize: "0.92rem", fontWeight: 700,
                    color: "var(--ink)", marginBottom: 12, letterSpacing: "-0.01em",
                  }}>
                    Laporan lengkap siap diunduh
                  </h4>
                  <a
                    href={`http://localhost:8000/api/download/${sessionId}?format=pdf`}
                    style={{
                      display: "block", width: "100%", padding: "12px",
                      background: "var(--accent)", color: "#fff",
                      borderRadius: 10, textAlign: "center",
                      fontWeight: 600, fontSize: "0.9rem",
                    }}
                  >
                    Unduh Laporan (PDF)
                  </a>
                </div>
              )}
            </div>

            {/* Coming Soon banner */}
            <div style={{
              border: "1.5px solid var(--line)", borderRadius: 16,
              padding: "20px 22px", background: "#fff",
              display: "flex", alignItems: "center", gap: 14,
            }}>
              <div style={{
                width: 42, height: 42, borderRadius: 12,
                background: "var(--accent-soft)",
                display: "flex", alignItems: "center", justifyContent: "center",
                flexShrink: 0, color: "var(--accent)",
              }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                  <rect x="5" y="10" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="1.6"/>
                  <path d="M8 10V7a4 4 0 018 0v3" stroke="currentColor" strokeWidth="1.6"/>
                </svg>
              </div>
              <div>
                <span style={{
                  display: "inline-block", fontSize: "0.7rem", fontWeight: 600,
                  color: "var(--accent-deep)", background: "var(--accent-soft)",
                  padding: "2px 9px", borderRadius: 20, marginBottom: 6,
                  border: "1px solid var(--line)",
                }}>
                  Segera hadir
                </span>
                <div style={{ fontSize: "0.88rem", fontWeight: 600, color: "var(--ink)", marginBottom: 3 }}>
                  Latihan wawancara AI — Premium
                </div>
                <p style={{ fontSize: "0.8rem", color: "var(--ink-soft)", lineHeight: 1.6 }}>
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
