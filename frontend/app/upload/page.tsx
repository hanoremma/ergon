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
        border: `1.5px dashed ${drag ? "#3b82f6" : "#bfdbfe"}`,
        borderRadius: 14, padding: "24px 20px",
        textAlign: "center", cursor: "pointer",
        background: drag ? "#eff6ff" : "#f8fbff",
        transition: "all 0.15s",
      }}
    >
      <input ref={ref} type="file" accept={accept} style={{ display: "none" }}
        onChange={(e) => { const f = e.target.files?.[0]; if (f) onFile(f); }} />
      {file ? (
        <div>
          <div style={{
            width: 36, height: 36, borderRadius: 10, margin: "0 auto 10px",
            background: "linear-gradient(135deg, #1d4ed8, #3b82f6)",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" stroke="white" strokeWidth="1.8" strokeLinejoin="round"/>
              <path d="M14 2v6h6" stroke="white" strokeWidth="1.8" strokeLinejoin="round"/>
            </svg>
          </div>
          <div style={{ fontSize: "0.88rem", fontWeight: 600, color: "#0F2A4A" }}>{file.name}</div>
          <div style={{ fontSize: "0.78rem", color: "#94a3b8", marginTop: 2 }}>
            {(file.size / 1024).toFixed(0)} KB — klik untuk ganti
          </div>
        </div>
      ) : (
        <div>
          <div style={{
            width: 36, height: 36, borderRadius: 10, margin: "0 auto 10px",
            background: "#e0eefb",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M12 15V4M12 4L9 7M12 4L15 7" stroke="#1d4ed8" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2" stroke="#1d4ed8" strokeWidth="1.8" strokeLinecap="round"/>
            </svg>
          </div>
          <div style={{ fontSize: "0.88rem", color: "#3A5878", fontWeight: 500 }}>{label}</div>
          <div style={{ fontSize: "0.76rem", color: "#94a3b8", marginTop: 4 }}>
            Klik atau drag & drop
          </div>
        </div>
      )}
    </div>
  );
}

function SectionCard({ title, step, children }: { title: string; step: string; children: React.ReactNode }) {
  return (
    <div style={{
      background: "#fff", border: "1.5px solid #e0eefb",
      borderRadius: 20, padding: "28px 30px", marginBottom: 16,
      boxShadow: "0 2px 12px rgba(15,42,74,0.05)",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
        <div style={{
          width: 28, height: 28, borderRadius: 8, flexShrink: 0,
          background: "linear-gradient(135deg, #1d4ed8, #3b82f6)",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: "0.72rem", fontWeight: 700, color: "#fff",
        }}>
          {step}
        </div>
        <h3 style={{ fontSize: "0.97rem", fontWeight: 700, color: "#0F2A4A" }}>
          {title}
        </h3>
      </div>
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

  const tabStyle = (active: boolean): React.CSSProperties => ({
    padding: "8px 18px", borderRadius: 8, fontSize: "0.88rem",
    fontWeight: 500, cursor: "pointer", border: "none",
    background: active ? "linear-gradient(135deg, #1d4ed8, #3b82f6)" : "transparent",
    color: active ? "#fff" : "#3A5878",
    transition: "all 0.15s",
    boxShadow: active ? "0 2px 8px rgba(59,130,246,0.3)" : "none",
  });

  const inputStyle: React.CSSProperties = {
    width: "100%", padding: "12px 14px",
    border: "1.5px solid #bfdbfe", borderRadius: 10,
    fontSize: "0.92rem", fontFamily: "'Inter', sans-serif",
    color: "#0F2A4A", background: "#fff",
    outline: "none",
  };

  return (
    <div style={{ background: "#fff", minHeight: "100vh", overflowX: "hidden" }}>
      <Nav />

      {/* Page header with gradient bg */}
      <div style={{ position: "relative", overflow: "hidden", background: "#fff", paddingBottom: 0 }}>
        <div style={{
          position: "absolute", top: -80, left: -120,
          width: 440, height: 440, borderRadius: "50%",
          background: "radial-gradient(circle, #dbeafe 0%, #eff6ff 50%, transparent 72%)",
          zIndex: 0, pointerEvents: "none",
        }} />
        <div style={{
          position: "absolute", top: 20, right: -80,
          width: 300, height: 300, borderRadius: "50%",
          background: "radial-gradient(circle, #bfdbfe 0%, transparent 70%)",
          zIndex: 0, pointerEvents: "none",
        }} />

        <div style={{ position: "relative", zIndex: 1, maxWidth: 720, margin: "0 auto", padding: "52px 32px 40px" }}>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 7,
            background: "linear-gradient(135deg, #eff6ff, #dbeafe)",
            borderRadius: 24, padding: "6px 16px", marginBottom: 20,
            border: "1px solid #bfdbfe",
          }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#1d4ed8", display: "inline-block", boxShadow: "0 0 0 3px #bfdbfe" }} />
            <span style={{ fontSize: "0.78rem", fontWeight: 600, color: "#134E8A", letterSpacing: "0.03em" }}>
              Cek kecocokan CV
            </span>
          </div>
          <h1 style={{
            fontSize: "2rem", fontWeight: 800,
            color: "#0F2A4A", marginBottom: 10, letterSpacing: "-0.03em",
          }}>
            Upload loker, CV, dan portofoliomu
          </h1>
          <p style={{ color: "#3A5878", fontSize: "0.97rem", maxWidth: 520, lineHeight: 1.65 }}>
            Skor kecocokan dan 3 saran teratas selalu gratis — tidak perlu daftar atau bayar dulu.
          </p>
        </div>
      </div>

      <div style={{ maxWidth: 720, margin: "0 auto", padding: "0 32px 80px" }}>
        <form onSubmit={handleSubmit}>
          {/* Job Posting */}
          <SectionCard title="Lowongan yang ingin kamu lamar" step="1">
            <div style={{
              display: "flex", gap: 4, marginBottom: 18,
              background: "#eff6ff", borderRadius: 10, padding: 4,
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
                <p style={{ fontSize: "0.76rem", color: "#94a3b8", marginTop: 6 }}>
                  Masukkan URL halaman loker. Untuk LinkedIn/Glints, sebaiknya gunakan upload PDF karena scraping mungkin terbatas.
                </p>
              </div>
            )}

            {jobTab === "pdf" && (
              <DropZone label="Upload PDF loker (job description)" accept=".pdf" onFile={setJobFile} file={jobFile} />
            )}
            {jobTab === "image" && (
              <DropZone label="Upload screenshot loker (PNG/JPG/WEBP)" accept=".png,.jpg,.jpeg,.webp" onFile={setJobFile} file={jobFile} />
            )}
          </SectionCard>

          {/* CV */}
          <SectionCard title="CV kamu" step="2">
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <DropZone label="Upload CV (PDF)" accept=".pdf" onFile={setCvFile} file={cvFile} />
              <div>
                <div style={{ fontSize: "0.8rem", color: "#94a3b8", marginBottom: 8, textAlign: "center" }}>atau</div>
                <input
                  style={inputStyle}
                  type="url"
                  placeholder="Link Google Docs CV kamu"
                  value={cvUrl}
                  onChange={(e) => setCvUrl(e.target.value)}
                />
                <p style={{ fontSize: "0.76rem", color: "#94a3b8", marginTop: 6 }}>
                  Contoh: https://docs.google.com/document/d/...
                </p>
              </div>
            </div>
          </SectionCard>

          {/* Portfolio */}
          <SectionCard title="Portofolio (opsional, tapi nilai tambah besar)" step="3">
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              <DropZone label="Upload file portofolio (PDF/gambar)" accept=".pdf,.png,.jpg,.jpeg" onFile={setPortfolioFile} file={portfolioFile} />
              <div>
                <input
                  style={inputStyle}
                  type="url"
                  placeholder="Link GitHub, Behance, atau situs personal"
                  value={portfolioUrl}
                  onChange={(e) => setPortfolioUrl(e.target.value)}
                />
                <p style={{ fontSize: "0.76rem", color: "#94a3b8", marginTop: 6 }}>
                  GitHub, Behance, Dribbble, Notion, atau situs personal.
                </p>
              </div>
            </div>
          </SectionCard>

          {/* Privacy note */}
          <div style={{
            background: "linear-gradient(135deg, #eff6ff, #dbeafe)",
            borderRadius: 12, padding: "14px 18px", marginBottom: 20,
            display: "flex", gap: 10, alignItems: "flex-start",
            border: "1px solid #bfdbfe",
          }}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ flexShrink: 0, marginTop: 2 }}>
              <rect x="3.5" y="7" width="9" height="6.5" rx="1.4" stroke="#134E8A" strokeWidth="1.4"/>
              <path d="M5.5 7V5A2.5 2.5 0 0110.5 5V7" stroke="#134E8A" strokeWidth="1.4"/>
            </svg>
            <p style={{ fontSize: "0.82rem", color: "#134E8A" }}>
              Data CV dan lokermu diproses secara aman dan hanya digunakan untuk analisis ini. Kamu bisa menghapus data kapan saja.
            </p>
          </div>

          {error && (
            <div style={{
              background: "#FEF2F2", border: "1px solid #FECACA",
              borderRadius: 10, padding: "12px 16px", marginBottom: 16,
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
              background: loading || !canSubmit
                ? "#94a3b8"
                : "linear-gradient(135deg, #1d4ed8, #3b82f6)",
              color: "#fff", border: "none", borderRadius: 12,
              fontSize: "1rem", fontWeight: 700,
              cursor: loading || !canSubmit ? "not-allowed" : "pointer",
              transition: "all 0.15s",
              letterSpacing: "-0.01em",
              boxShadow: loading || !canSubmit ? "none" : "0 4px 16px rgba(59,130,246,0.35)",
            }}
          >
            {loading ? "Menganalisis... ini butuh beberapa detik" : "Cek kecocokan CV — gratis →"}
          </button>

          {loading && (
            <div style={{ marginTop: 16, textAlign: "center" }}>
              <div style={{ fontSize: "0.86rem", color: "#3A5878", marginBottom: 10 }}>
                Sedang menganalisis loker, CV, dan portofoliomu...
              </div>
              <div style={{ height: 5, borderRadius: 99, background: "#e0eefb", overflow: "hidden" }}>
                <div style={{
                  height: "100%",
                  background: "linear-gradient(90deg, #1d4ed8, #3b82f6, #0ea5e9)",
                  borderRadius: 99, width: "60%",
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
