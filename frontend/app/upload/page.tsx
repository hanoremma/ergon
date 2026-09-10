"use client";
import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import Nav from "../components/Nav";
import Footer from "../components/Footer";

type UploadTab = "link" | "pdf" | "image";

function DropZone({
  label,
  accept,
  onFile,
  file,
}: {
  label: string;
  accept: string;
  onFile: (f: File) => void;
  file: File | null;
}) {
  const ref = useRef<HTMLInputElement>(null);
  const [drag, setDrag] = useState(false);

  return (
    <div
      onClick={() => ref.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => {
        e.preventDefault(); setDrag(false);
        const f = e.dataTransfer.files[0];
        if (f) onFile(f);
      }}
      style={{
        border: `1.5px dashed ${drag ? "var(--accent)" : "var(--line)"}`,
        borderRadius: 14, padding: "24px 20px",
        textAlign: "center", cursor: "pointer",
        background: drag ? "var(--accent-soft)" : "#fff",
        transition: "all 0.15s",
      }}
    >
      <input ref={ref} type="file" accept={accept} style={{ display: "none" }}
        onChange={(e) => { const f = e.target.files?.[0]; if (f) onFile(f); }} />
      {file ? (
        <div>
          <div style={{ fontSize: "1.4rem", marginBottom: 4 }}>📄</div>
          <div style={{ fontSize: "0.88rem", fontWeight: 600, color: "var(--ink)" }}>{file.name}</div>
          <div style={{ fontSize: "0.78rem", color: "var(--muted)", marginTop: 2 }}>
            {(file.size / 1024).toFixed(0)} KB — klik untuk ganti
          </div>
        </div>
      ) : (
        <div>
          <div style={{ fontSize: "1.4rem", marginBottom: 6 }}>↑</div>
          <div style={{ fontSize: "0.88rem", color: "var(--ink-soft)" }}>{label}</div>
          <div style={{ fontSize: "0.76rem", color: "var(--muted)", marginTop: 4 }}>
            Klik atau drag & drop
          </div>
        </div>
      )}
    </div>
  );
}

function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{
      background: "#fff", border: "1.5px solid var(--line)",
      borderRadius: 16, padding: "26px 30px", marginBottom: 18,
    }}>
      <h3 style={{
        fontSize: "1rem", fontWeight: 600,
        color: "var(--ink)", marginBottom: 18,
      }}>
        {title}
      </h3>
      {children}
    </div>
  );
}

export default function UploadPage() {
  const router = useRouter();
  const [jobTab, setJobTab] = useState<UploadTab>("link");
  const [jobUrl, setJobUrl] = useState("");
  const [jobFile, setJobFile] = useState<File | null>(null);
  const [cvUrl, setCvUrl] = useState("");
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [portfolioUrl, setPortfolioUrl] = useState("");
  const [portfolioFile, setPortfolioFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const canSubmit = jobUrl || jobFile || (jobTab === "image" && jobFile);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!canSubmit) { setError("Masukkan link atau upload file loker terlebih dahulu."); return; }
    setError("");
    setLoading(true);

    try {
      const fd = new FormData();
      if (jobUrl) fd.append("job_url", jobUrl);
      if (jobFile) fd.append("job_file", jobFile);
      if (cvUrl) fd.append("cv_url", cvUrl);
      if (cvFile) fd.append("cv_file", cvFile);
      if (portfolioUrl) fd.append("portfolio_url", portfolioUrl);
      if (portfolioFile) fd.append("portfolio_file", portfolioFile);

      const res = await fetch("http://localhost:8000/api/analyze", {
        method: "POST",
        body: fd,
      });

      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      router.push(`/result/${data.session_id}`);
    } catch (err: any) {
      setError(`Terjadi kesalahan: ${err.message}. Pastikan backend berjalan di port 8000.`);
      setLoading(false);
    }
  }

  const tabStyle = (active: boolean) => ({
    padding: "8px 18px", borderRadius: 8, fontSize: "0.88rem",
    fontWeight: 500, cursor: "pointer", border: "none",
    background: active ? "var(--accent)" : "transparent",
    color: active ? "#fff" : "var(--ink-soft)",
    transition: "all 0.15s",
  });

  const inputStyle = {
    width: "100%", padding: "12px 14px",
    border: "1.5px solid var(--line)", borderRadius: 10,
    fontSize: "0.92rem", fontFamily: "'Inter', sans-serif",
    color: "var(--ink)", background: "#fff",
    outline: "none",
  };

  return (
    <div style={{ background: "var(--bg-page)", minHeight: "100vh" }}>
      <Nav />

      <div style={{ maxWidth: 720, margin: "0 auto", padding: "48px 32px 80px" }}>
        {/* Header */}
        <div style={{ marginBottom: 36 }}>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 7,
            background: "var(--accent-soft)", borderRadius: 20,
            padding: "5px 14px", marginBottom: 18,
            border: "1px solid var(--line)",
          }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--accent)" }} />
            <span style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--accent-deep)", letterSpacing: "0.01em" }}>
              Cek kecocokan CV
            </span>
          </div>
          <h1 style={{
            fontSize: "1.9rem", fontWeight: 700,
            color: "var(--ink)", marginBottom: 10, letterSpacing: "-0.02em",
          }}>
            Upload loker, CV, dan portofoliomu
          </h1>
          <p style={{ color: "var(--ink-soft)", fontSize: "0.97rem", maxWidth: 520, lineHeight: 1.65 }}>
            Skor kecocokan dan 3 saran teratas selalu gratis — tidak perlu daftar atau bayar dulu.
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Job Posting */}
          <SectionCard title="1. Lowongan yang ingin kamu lamar">
            {/* Tabs */}
            <div style={{
              display: "flex", gap: 4, marginBottom: 18,
              background: "var(--accent-soft)", borderRadius: 10, padding: 4,
              width: "fit-content",
            }}>
              {(["link", "pdf", "image"] as UploadTab[]).map((tab) => (
                <button key={tab} type="button" style={tabStyle(jobTab === tab)}
                  onClick={() => setJobTab(tab)}>
                  {tab === "link" ? "Tempel link" : tab === "pdf" ? "Upload PDF" : "Upload gambar"}
                </button>
              ))}
            </div>

            {jobTab === "link" && (
              <div>
                <input
                  style={inputStyle}
                  type="url"
                  placeholder="https://linkedin.com/jobs/... atau link job board lain"
                  value={jobUrl}
                  onChange={(e) => setJobUrl(e.target.value)}
                />
                <p style={{ fontSize: "0.76rem", color: "var(--muted)", marginTop: 6 }}>
                  Masukkan URL halaman loker. Untuk LinkedIn/Glints, sebaiknya gunakan upload PDF karena scraping mungkin terbatas.
                </p>
              </div>
            )}

            {jobTab === "pdf" && (
              <DropZone
                label="Upload PDF loker (job description)"
                accept=".pdf"
                onFile={setJobFile}
                file={jobFile}
              />
            )}

            {jobTab === "image" && (
              <DropZone
                label="Upload screenshot loker (PNG/JPG/WEBP)"
                accept=".png,.jpg,.jpeg,.webp"
                onFile={setJobFile}
                file={jobFile}
              />
            )}
          </SectionCard>

          {/* CV */}
          <SectionCard title="2. CV kamu">
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <div>
                <DropZone
                  label="Upload CV (PDF)"
                  accept=".pdf"
                  onFile={setCvFile}
                  file={cvFile}
                />
              </div>
              <div>
                <div style={{ fontSize: "0.8rem", color: "var(--muted)", marginBottom: 8, textAlign: "center" }}>atau</div>
                <input
                  style={{ ...inputStyle, marginTop: 0 }}
                  type="url"
                  placeholder="Link Google Docs CV kamu"
                  value={cvUrl}
                  onChange={(e) => setCvUrl(e.target.value)}
                />
                <p style={{ fontSize: "0.76rem", color: "var(--muted)", marginTop: 6 }}>
                  Contoh: https://docs.google.com/document/d/...
                </p>
              </div>
            </div>
          </SectionCard>

          {/* Portfolio */}
          <SectionCard title="3. Portofolio (opsional, tapi nilai tambah besar)">
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <DropZone
                label="Upload file portofolio (PDF/gambar)"
                accept=".pdf,.png,.jpg,.jpeg"
                onFile={setPortfolioFile}
                file={portfolioFile}
              />
              <div>
                <input
                  style={inputStyle}
                  type="url"
                  placeholder="Link GitHub, Behance, atau situs personal"
                  value={portfolioUrl}
                  onChange={(e) => setPortfolioUrl(e.target.value)}
                />
                <p style={{ fontSize: "0.76rem", color: "var(--muted)", marginTop: 6 }}>
                  GitHub, Behance, Dribbble, Notion, atau situs personal.
                </p>
              </div>
            </div>
          </SectionCard>

          {/* Privacy note */}
          <div style={{
            background: "var(--accent-soft)", borderRadius: 10,
            padding: "14px 18px", marginBottom: 24,
            display: "flex", gap: 10, alignItems: "flex-start",
          }}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ flexShrink: 0, marginTop: 2 }}>
              <rect x="3.5" y="7" width="9" height="6.5" rx="1.4" stroke="var(--accent-deep)" strokeWidth="1.4"/>
              <path d="M5.5 7V5A2.5 2.5 0 0110.5 5V7" stroke="var(--accent-deep)" strokeWidth="1.4"/>
            </svg>
            <p style={{ fontSize: "0.82rem", color: "var(--accent-deep)" }}>
              Data CV dan lokermu diproses secara aman dan hanya digunakan untuk analisis ini. Kamu bisa menghapus data kapan saja.
            </p>
          </div>

          {error && (
            <div style={{
              background: "#FEF2F2", border: "1px solid #FECACA",
              borderRadius: 10, padding: "12px 16px", marginBottom: 20,
              fontSize: "0.88rem", color: "#DC2626",
            }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !canSubmit}
            style={{
              width: "100%", padding: "15px 24px",
              background: loading || !canSubmit ? "var(--muted)" : "var(--accent)",
              color: "#fff", border: "none", borderRadius: 10,
              fontSize: "1rem", fontWeight: 600,
              cursor: loading || !canSubmit ? "not-allowed" : "pointer",
              transition: "all 0.15s",
              letterSpacing: "-0.01em",
            }}
          >
            {loading ? (
              <span>Menganalisis... ini butuh beberapa detik</span>
            ) : (
              <span>Cek kecocokan CV — gratis</span>
            )}
          </button>

          {loading && (
            <div style={{ marginTop: 16, textAlign: "center" }}>
              <div style={{ fontSize: "0.86rem", color: "var(--ink-soft)", marginBottom: 8 }}>
                Sedang menganalisis loker, CV, dan portofoliomu...
              </div>
              <div style={{
                height: 4, borderRadius: 2, background: "var(--line)",
                overflow: "hidden",
              }}>
                <div style={{
                  height: "100%", background: "var(--accent)",
                  borderRadius: 2, width: "60%",
                  animation: "progress-pulse 1.5s ease-in-out infinite",
                }} />
              </div>
              <style>{`
                @keyframes progress-pulse {
                  0% { width: 10%; }
                  50% { width: 70%; }
                  100% { width: 90%; }
                }
              `}</style>
            </div>
          )}
        </form>
      </div>

      <Footer />
    </div>
  );
}
