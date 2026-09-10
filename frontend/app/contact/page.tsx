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
    // In production this would POST to a backend endpoint
    setSent(true);
  }

  const inputStyle: React.CSSProperties = {
    width: "100%", padding: "12px 14px",
    border: "1.5px solid var(--line)", borderRadius: 10,
    fontSize: "0.92rem", color: "var(--ink)", background: "#fff",
    outline: "none", fontFamily: "inherit",
    boxSizing: "border-box",
  };

  const labelStyle: React.CSSProperties = {
    display: "block", fontSize: "0.84rem", fontWeight: 600,
    color: "var(--ink)", marginBottom: 7,
  };

  return (
    <div style={{ background: "var(--bg-page)", minHeight: "100vh" }}>
      <Nav />

      <div style={{ maxWidth: 760, margin: "0 auto", padding: "52px 32px 88px" }}>
        {/* Header */}
        <div style={{ marginBottom: 40 }}>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 7,
            background: "var(--accent-soft)", borderRadius: 20,
            padding: "5px 14px", marginBottom: 16,
            border: "1px solid var(--line)",
          }}>
            <span style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--accent-deep)" }}>Dukungan</span>
          </div>
          <h1 style={{ fontSize: "2rem", fontWeight: 800, color: "var(--ink)", letterSpacing: "-0.025em", marginBottom: 10 }}>
            Hubungi Kami
          </h1>
          <p style={{ fontSize: "0.97rem", color: "var(--ink-soft)", lineHeight: 1.65 }}>
            Ada pertanyaan, masukan, atau kendala pembayaran? Isi formulir di bawah dan kami akan membalas dalam 1×24 jam kerja.
          </p>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1.8fr", gap: 32, alignItems: "start" }}>

          {/* Info panel */}
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {[
              {
                icon: (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                    <path d="M4 4h16v16H4V4z" rx="2" stroke="var(--accent)" strokeWidth="1.6"/>
                    <path d="M4 4l8 9 8-9" stroke="var(--accent)" strokeWidth="1.6" strokeLinejoin="round"/>
                  </svg>
                ),
                title: "Email",
                value: "halo@ergon.id",
              },
              {
                icon: (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="9" stroke="var(--accent)" strokeWidth="1.6"/>
                    <path d="M12 7v5l3 3" stroke="var(--accent)" strokeWidth="1.6" strokeLinecap="round"/>
                  </svg>
                ),
                title: "Waktu respons",
                value: "1×24 jam kerja",
              },
              {
                icon: (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2C8.134 2 5 5.134 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.866-3.134-7-7-7z" stroke="var(--accent)" strokeWidth="1.6"/>
                    <circle cx="12" cy="9" r="2.5" stroke="var(--accent)" strokeWidth="1.6"/>
                  </svg>
                ),
                title: "Lokasi",
                value: "Indonesia",
              },
            ].map((item) => (
              <div key={item.title} style={{
                background: "#fff", border: "1.5px solid var(--line)",
                borderRadius: 12, padding: "16px 18px",
                display: "flex", gap: 14, alignItems: "flex-start",
              }}>
                <div style={{
                  width: 36, height: 36, borderRadius: 9,
                  background: "var(--accent-soft)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  flexShrink: 0,
                }}>
                  {item.icon}
                </div>
                <div>
                  <div style={{ fontSize: "0.78rem", color: "var(--muted)", fontWeight: 500, marginBottom: 3 }}>{item.title}</div>
                  <div style={{ fontSize: "0.88rem", fontWeight: 600, color: "var(--ink)" }}>{item.value}</div>
                </div>
              </div>
            ))}

            {/* FAQ link */}
            <div style={{
              background: "var(--bg-hero)", border: "1.5px solid var(--line)",
              borderRadius: 12, padding: "16px 18px",
            }}>
              <div style={{ fontSize: "0.84rem", fontWeight: 600, color: "var(--ink)", marginBottom: 6 }}>
                Cek FAQ dulu?
              </div>
              <p style={{ fontSize: "0.82rem", color: "var(--ink-soft)", marginBottom: 12, lineHeight: 1.6 }}>
                Pertanyaan umum sudah terjawab di halaman FAQ kami.
              </p>
              <a href="/faq" style={{
                fontSize: "0.84rem", fontWeight: 600, color: "var(--accent)",
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
            background: "#fff", border: "1.5px solid var(--line)",
            borderRadius: 18, padding: "28px 30px",
          }}>
            {sent ? (
              <div style={{ textAlign: "center", padding: "32px 0" }}>
                <div style={{
                  width: 60, height: 60, borderRadius: "50%",
                  background: "#ECFDF5", border: "2px solid #A7F3D0",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  margin: "0 auto 20px",
                }}>
                  <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                    <path d="M5 12L10 17L20 7" stroke="#15803D" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <h3 style={{ fontSize: "1.15rem", fontWeight: 700, color: "var(--ink)", marginBottom: 8 }}>
                  Pesan terkirim!
                </h3>
                <p style={{ fontSize: "0.9rem", color: "var(--ink-soft)", lineHeight: 1.65 }}>
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
                    style={{ ...inputStyle, appearance: "none" as any, backgroundImage: "url(\"data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1L6 6L11 1' stroke='%237FA3C0' stroke-width='1.5' stroke-linecap='round'/%3E%3C/svg%3E\")", backgroundRepeat: "no-repeat", backgroundPosition: "right 14px center" }}
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
                    style={{ ...inputStyle, resize: "vertical" as any, minHeight: 120 }}
                  />
                </div>

                <button type="submit" style={{
                  width: "100%", padding: "13px",
                  background: "var(--accent)", color: "#fff",
                  border: "none", borderRadius: 10,
                  fontWeight: 600, fontSize: "0.96rem",
                  cursor: "pointer", letterSpacing: "-0.01em",
                  fontFamily: "inherit",
                }}>
                  Kirim pesan
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
