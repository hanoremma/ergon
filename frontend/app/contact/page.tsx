"use client";
import { useState } from "react";
import Nav from "../components/Nav";
import Footer from "../components/Footer";

export default function ContactPage() {
  const [sent, setSent] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", subject: "", message: "" });

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSent(true);
  }

  const inputStyle: React.CSSProperties = {
    width: "100%", padding: "12px 14px",
    border: "1.5px solid #bfdbfe", borderRadius: 10,
    fontSize: "0.92rem", color: "#0F2A4A", background: "#fff",
    outline: "none", fontFamily: "inherit",
    boxSizing: "border-box",
  };

  const labelStyle: React.CSSProperties = {
    display: "block", fontSize: "0.84rem", fontWeight: 600,
    color: "#0F2A4A", marginBottom: 7,
  };

  return (
    <div style={{ background: "#fff", minHeight: "100vh", overflowX: "hidden" }}>
      <Nav />

      {/* Page header */}
      <div style={{ position: "relative", overflow: "hidden", background: "#fff" }}>
        <div style={{
          position: "absolute", top: -80, left: -120,
          width: 440, height: 440, borderRadius: "50%",
          background: "radial-gradient(circle, #dbeafe 0%, #eff6ff 50%, transparent 72%)",
          zIndex: 0, pointerEvents: "none",
        }} />
        <div style={{
          position: "absolute", top: 20, right: -80,
          width: 280, height: 280, borderRadius: "50%",
          background: "radial-gradient(circle, #bfdbfe 0%, transparent 70%)",
          zIndex: 0, pointerEvents: "none",
        }} />
        <div style={{ position: "relative", zIndex: 1, maxWidth: 760, margin: "0 auto", padding: "52px 32px 40px" }}>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 7,
            background: "linear-gradient(135deg, #eff6ff, #dbeafe)",
            borderRadius: 24, padding: "6px 16px", marginBottom: 20,
            border: "1px solid #bfdbfe",
          }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#1d4ed8", display: "inline-block" }} />
            <span style={{ fontSize: "0.78rem", fontWeight: 600, color: "#134E8A", letterSpacing: "0.03em" }}>Dukungan</span>
          </div>
          <h1 style={{ fontSize: "2rem", fontWeight: 800, color: "#0F2A4A", letterSpacing: "-0.03em", marginBottom: 10 }}>
            Hubungi Kami
          </h1>
          <p style={{ fontSize: "0.97rem", color: "#3A5878", lineHeight: 1.65 }}>
            Ada pertanyaan, masukan, atau kendala pembayaran? Isi formulir di bawah dan kami akan membalas dalam 1×24 jam kerja.
          </p>
        </div>
      </div>

      <div style={{ maxWidth: 760, margin: "0 auto", padding: "8px 32px 88px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1.8fr", gap: 28, alignItems: "start" }}>

          {/* Info panel */}
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {[
              {
                icon: (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                    <path d="M4 4h16v16H4V4z" rx="2" stroke="#1d4ed8" strokeWidth="1.6"/>
                    <path d="M4 4l8 9 8-9" stroke="#1d4ed8" strokeWidth="1.6" strokeLinejoin="round"/>
                  </svg>
                ),
                title: "Email",
                value: "halo@ergon.id",
              },
              {
                icon: (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="9" stroke="#1d4ed8" strokeWidth="1.6"/>
                    <path d="M12 7v5l3 3" stroke="#1d4ed8" strokeWidth="1.6" strokeLinecap="round"/>
                  </svg>
                ),
                title: "Waktu respons",
                value: "1×24 jam kerja",
              },
              {
                icon: (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2C8.134 2 5 5.134 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.866-3.134-7-7-7z" stroke="#1d4ed8" strokeWidth="1.6"/>
                    <circle cx="12" cy="9" r="2.5" stroke="#1d4ed8" strokeWidth="1.6"/>
                  </svg>
                ),
                title: "Lokasi",
                value: "Indonesia",
              },
            ].map((item) => (
              <div key={item.title} style={{
                background: "#fff", border: "1.5px solid #e0eefb",
                borderRadius: 14, padding: "16px 18px",
                display: "flex", gap: 14, alignItems: "flex-start",
                boxShadow: "0 2px 8px rgba(15,42,74,0.05)",
              }}>
                <div style={{
                  width: 38, height: 38, borderRadius: 10,
                  background: "linear-gradient(135deg, #eff6ff, #dbeafe)",
                  border: "1px solid #bfdbfe",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  flexShrink: 0,
                }}>
                  {item.icon}
                </div>
                <div>
                  <div style={{ fontSize: "0.78rem", color: "#94a3b8", fontWeight: 500, marginBottom: 3 }}>{item.title}</div>
                  <div style={{ fontSize: "0.9rem", fontWeight: 700, color: "#0F2A4A" }}>{item.value}</div>
                </div>
              </div>
            ))}

            {/* FAQ link */}
            <div style={{
              background: "linear-gradient(135deg, #eff6ff, #dbeafe)",
              border: "1.5px solid #bfdbfe", borderRadius: 14, padding: "18px 18px",
            }}>
              <div style={{ fontSize: "0.86rem", fontWeight: 700, color: "#0F2A4A", marginBottom: 6 }}>
                Cek FAQ dulu?
              </div>
              <p style={{ fontSize: "0.82rem", color: "#3A5878", marginBottom: 14, lineHeight: 1.6 }}>
                Pertanyaan umum sudah terjawab di halaman FAQ kami.
              </p>
              <a href="/faq" style={{
                fontSize: "0.84rem", fontWeight: 700, color: "#1d4ed8",
                display: "flex", alignItems: "center", gap: 5,
              }}>
                Lihat FAQ
                <svg width="13" height="13" viewBox="0 0 14 14" fill="none">
                  <path d="M3 7H11M11 7L7.5 3.5M11 7L7.5 10.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </a>
            </div>
          </div>

          {/* Form */}
          <div style={{
            background: "#fff", border: "1.5px solid #e0eefb",
            borderRadius: 20, padding: "32px 30px",
            boxShadow: "0 4px 20px rgba(15,42,74,0.07)",
          }}>
            {sent ? (
              <div style={{ textAlign: "center", padding: "40px 0" }}>
                <div style={{
                  width: 64, height: 64, borderRadius: "50%",
                  background: "linear-gradient(135deg, #ecfdf5, #d1fae5)",
                  border: "2px solid #86efac",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  margin: "0 auto 20px",
                }}>
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
                    <path d="M5 12L10 17L20 7" stroke="#16a34a" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <h3 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#0F2A4A", marginBottom: 8 }}>
                  Pesan terkirim!
                </h3>
                <p style={{ fontSize: "0.9rem", color: "#3A5878", lineHeight: 1.65 }}>
                  Terima kasih sudah menghubungi kami. Kami akan membalas dalam 1×24 jam kerja.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSubmit}>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
                  <div>
                    <label style={labelStyle}>Nama</label>
                    <input
                      name="name" required value={form.name} onChange={handleChange}
                      placeholder="Nama lengkap kamu"
                      style={inputStyle}
                    />
                  </div>
                  <div>
                    <label style={labelStyle}>Email</label>
                    <input
                      name="email" type="email" required value={form.email} onChange={handleChange}
                      placeholder="email@kamu.com"
                      style={inputStyle}
                    />
                  </div>
                </div>

                <div style={{ marginBottom: 16 }}>
                  <label style={labelStyle}>Topik</label>
                  <select
                    name="subject" value={form.subject} onChange={handleChange}
                    style={{ ...inputStyle, appearance: "none" as React.CSSProperties["appearance"], backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1L6 6L11 1' stroke='%231d4ed8' stroke-width='1.5' stroke-linecap='round'/%3E%3C/svg%3E\")", backgroundRepeat: "no-repeat", backgroundPosition: "right 14px center" }}
                  >
                    <option value="">Pilih topik</option>
                    <option value="payment">Masalah pembayaran</option>
                    <option value="result">Masalah hasil analisis</option>
                    <option value="data">Permintaan hapus data</option>
                    <option value="feedback">Masukan & saran</option>
                    <option value="other">Lainnya</option>
                  </select>
                </div>

                <div style={{ marginBottom: 22 }}>
                  <label style={labelStyle}>Pesan</label>
                  <textarea
                    name="message" required value={form.message} onChange={handleChange}
                    placeholder="Ceritakan kendala atau pertanyaan kamu secara detail..."
                    rows={5}
                    style={{ ...inputStyle, resize: "vertical" as React.CSSProperties["resize"], minHeight: 120 }}
                  />
                </div>

                <button type="submit" style={{
                  width: "100%", padding: "14px",
                  background: "linear-gradient(135deg, #1d4ed8, #3b82f6)",
                  color: "#fff", border: "none", borderRadius: 12,
                  fontWeight: 700, fontSize: "0.96rem",
                  cursor: "pointer", letterSpacing: "-0.01em",
                  fontFamily: "inherit",
                  boxShadow: "0 4px 16px rgba(59,130,246,0.35)",
                }}>
                  Kirim pesan →
                </button>
              </form>
            )}
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
