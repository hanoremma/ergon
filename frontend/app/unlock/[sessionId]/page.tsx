"use client";
import { useEffect, useState } from "react";
import { useParams, useSearchParams, useRouter } from "next/navigation";
import Nav from "../../components/Nav";
import Footer from "../../components/Footer";

declare global {
  interface Window {
    snap: {
      pay: (token: string, options: { onSuccess: (r: any) => void; onPending: (r: any) => void; onError: (r: any) => void; onClose: () => void }) => void;
    };
  }
}

export default function UnlockPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  // Check if coming back from payment confirmation
  const orderId = searchParams.get("order_id");

  const [step, setStep] = useState<"confirm" | "payment" | "verifying" | "success" | "error">(
    orderId ? "verifying" : "confirm"
  );
  const [clientKey, setClientKey] = useState("");
  const [snapToken, setSnapToken] = useState("");
  const [paymentOrderId, setPaymentOrderId] = useState(orderId || "");
  const [isProduction, setIsProduction] = useState(false);
  const [error, setError] = useState("");

  // Load Midtrans Snap script
  useEffect(() => {
    fetch("http://localhost:8000/api/config/client")
      .then(r => r.json())
      .then(data => {
        setClientKey(data.midtrans_client_key || "Mid-client-jeMHQn4VQjUS3QJG");
        setIsProduction(data.is_production || false);
      })
      .catch(() => {
        setClientKey("Mid-client-jeMHQn4VQjUS3QJG");
      });
  }, []);

  useEffect(() => {
    if (clientKey) {
      const script = document.createElement("script");
      script.src = isProduction
        ? "https://app.midtrans.com/snap/snap.js"
        : "https://app.sandbox.midtrans.com/snap/snap.js";
      script.setAttribute("data-client-key", clientKey);
      document.head.appendChild(script);
    }
  }, [clientKey, isProduction]);

  // Auto-verify if returning from payment
  useEffect(() => {
    if (step === "verifying" && paymentOrderId) {
      verifyPayment(paymentOrderId);
    }
  }, [step, paymentOrderId]);

  async function initPayment() {
    setStep("payment");
    try {
      const res = await fetch("http://localhost:8000/api/payment/init", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });
      if (!res.ok) throw new Error("Gagal membuat transaksi");
      const data = await res.json();

      setSnapToken(data.snap_token);
      setPaymentOrderId(data.order_id);
      setClientKey(data.client_key);

      // Tunggu Snap script load (maks 3 detik)
      const snap = await waitForSnap(3000);

      if (snap && data.snap_token) {
        // ✅ Snap popup — callbacks.finish akan dihormati, tidak perlu redirect
        snap.pay(data.snap_token, {
          onSuccess: () => {
            setStep("verifying");
            verifyPayment(data.order_id);
          },
          onPending: () => {
            setStep("verifying");
            verifyPayment(data.order_id);
          },
          onError: () => {
            setError("Pembayaran gagal. Silakan coba lagi.");
            setStep("error");
          },
          onClose: () => {
            setStep("confirm");
          },
        });
      } else if (data.snap_token) {
        // Fallback: Snap redirect dengan finish_redirect_url sebagai query param
        // Format: https://app.sandbox.midtrans.com/snap/v4/redirection/{token}?finish_redirect_url=...
        const finishUrl = encodeURIComponent(
          `http://localhost:3000/unlock/confirm?order_id=${data.order_id}&session=${sessionId}`
        );
        const snapRedirectUrl = `https://app.sandbox.midtrans.com/snap/v4/redirection/${data.snap_token}?finish_redirect_url=${finishUrl}`;
        window.location.href = snapRedirectUrl;
      } else {
        throw new Error("Tidak mendapat snap token dari backend");
      }
    } catch (err: any) {
      setError(`Gagal memulai pembayaran: ${err.message}`);
      setStep("error");
    }
  }

  function waitForSnap(timeoutMs: number): Promise<typeof window.snap | null> {
    return new Promise((resolve) => {
      if (window.snap) { resolve(window.snap); return; }
      const interval = setInterval(() => {
        if (window.snap) { clearInterval(interval); resolve(window.snap); }
      }, 100);
      setTimeout(() => { clearInterval(interval); resolve(null); }, timeoutMs);
    });
  }

  async function verifyPayment(orderId: string) {
    setStep("verifying");
    // Poll hingga 5x dengan interval 2 detik (total maks ~10 detik)
    // Backend sekarang query Midtrans API langsung sehingga tidak perlu webhook
    for (let attempt = 1; attempt <= 5; attempt++) {
      try {
        const res = await fetch("http://localhost:8000/api/payment/verify", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ order_id: orderId }),
        });
        const data = await res.json();

        if (data.unlocked) {
          setStep("success");
          return;
        }

        // Jika Midtrans masih "pending" (baru selesai bayar), tunggu dan coba lagi
        if (attempt < 5) {
          await new Promise(r => setTimeout(r, 2000));
        }
      } catch (err: any) {
        if (attempt === 5) {
          setError(`Verifikasi gagal: ${err.message}`);
          setStep("error");
          return;
        }
        await new Promise(r => setTimeout(r, 2000));
      }
    }
    // Setelah 5x masih belum unlocked
    setError("Pembayaran terdeteksi tapi butuh waktu lebih lama untuk dikonfirmasi. Tunggu 30 detik lalu klik 'Coba lagi'.");
    setStep("error");
  }

  // ─── Render Steps ────────────────────────────────────────────────────────────

  return (
    <div style={{ background: "var(--bg-page)", minHeight: "100vh" }}>
      <Nav />

      <div style={{ maxWidth: 560, margin: "0 auto", padding: "60px 32px 80px" }}>
        {step === "confirm" && <ConfirmStep onPay={initPayment} />}
        {step === "payment" && <PaymentStep />}
        {step === "verifying" && <VerifyingStep />}
        {step === "success" && <SuccessStep sessionId={sessionId} onView={() => router.push(`/result/${sessionId}`)} />}
        {step === "error" && <ErrorStep error={error} onRetry={() => setStep("confirm")} />}
      </div>

      <Footer />
    </div>
  );
}

// ─── Step Components ─────────────────────────────────────────────────────────

function ConfirmStep({ onPay }: { onPay: () => void }) {
  return (
    <div>
      <div style={{ marginBottom: 28 }}>
        <div style={{
          display: "inline-flex", alignItems: "center", gap: 7,
          background: "var(--accent-soft)", borderRadius: 20,
          padding: "5px 14px", marginBottom: 16,
          border: "1px solid var(--line)",
        }}>
          <span style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--accent-deep)", letterSpacing: "0.01em" }}>
            Buka versi lengkap
          </span>
        </div>
        <h1 style={{ fontSize: "1.75rem", fontWeight: 800, color: "var(--ink)", marginBottom: 10, letterSpacing: "-0.025em" }}>
          Semua saran + laporan lengkap siap diunduh
        </h1>
        <p style={{ color: "var(--ink-soft)", lineHeight: 1.65 }}>
          Satu kali bayar untuk loker ini. Tidak perlu berlangganan.
        </p>
      </div>

      {/* What you get */}
      <div style={{
        background: "#fff", border: "1.5px solid var(--line)",
        borderRadius: 16, padding: "24px 26px",
        marginBottom: 18,
      }}>
        <div style={{ fontWeight: 700, color: "var(--ink)", marginBottom: 16, fontSize: "0.9rem", letterSpacing: "-0.01em" }}>
          Yang kamu dapatkan:
        </div>
        {[
          "Semua saran perbaikan CV dengan detail lengkap",
          "Estimasi dampak per saran (+X% ke skor kecocokan)",
          "Laporan lengkap hasil analisis, siap diunduh sebagai PDF",
          "Konteks perusahaan & tips spesifik untuk loker ini",
        ].map((item, i) => (
          <div key={i} style={{ display: "flex", gap: 10, marginBottom: 10, alignItems: "flex-start" }}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ flexShrink: 0, marginTop: 2 }}>
              <circle cx="8" cy="8" r="6.4" stroke="#15803D" strokeWidth="1.5"/>
              <path d="M5.3 8.2L7.1 10L10.6 6" stroke="#15803D" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <span style={{ fontSize: "0.9rem", color: "var(--ink-soft)", lineHeight: 1.55 }}>{item}</span>
          </div>
        ))}
      </div>

      {/* Price & CTA */}
      <div style={{
        background: "var(--ink)", borderRadius: 16, padding: "26px 26px",
      }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginBottom: 6 }}>
          <span style={{
            fontSize: "1.9rem", fontWeight: 800, letterSpacing: "-0.03em",
            color: "#fff",
          }}>
            Rp 25.000
          </span>
          <span style={{ fontSize: "0.82rem", color: "var(--muted)" }}>sekali bayar per loker</span>
        </div>
        <p style={{ fontSize: "0.82rem", color: "#B8D4EE", marginBottom: 20, lineHeight: 1.6 }}>
          Harga berlaku untuk analisis loker ini saja. Setelah bayar, akses tidak terbatas untuk sesi ini.
        </p>
        <button
          onClick={onPay}
          style={{
            width: "100%", padding: "15px",
            background: "var(--accent)", color: "#fff",
            border: "none", borderRadius: 10,
            fontWeight: 600, fontSize: "1rem",
            cursor: "pointer", letterSpacing: "-0.01em",
          }}
        >
          Bayar & Buka Sekarang
        </button>
        <p style={{ fontSize: "0.76rem", color: "var(--muted)", marginTop: 12, textAlign: "center" }}>
          Pembayaran aman via Midtrans · Transfer bank, QRIS, kartu kredit
        </p>
      </div>
    </div>
  );
}

function PaymentStep() {
  return (
    <div style={{ textAlign: "center", padding: "40px 0" }}>
      <div style={{
        width: 56, height: 56, borderRadius: "50%",
        border: "3px solid var(--line)",
        borderTop: "3px solid var(--accent)",
        animation: "spin 0.9s linear infinite",
        margin: "0 auto 24px",
      }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <h2 style={{ fontWeight: 700, color: "var(--ink)", fontSize: "1.25rem", letterSpacing: "-0.01em" }}>
        Memuat halaman pembayaran...
      </h2>
      <p style={{ color: "var(--ink-soft)", marginTop: 8, lineHeight: 1.65 }}>
        Sebentar lagi halaman pembayaran Midtrans akan muncul.
      </p>
    </div>
  );
}

function VerifyingStep() {
  return (
    <div style={{ textAlign: "center", padding: "40px 0" }}>
      <div style={{
        width: 56, height: 56, borderRadius: "50%",
        border: "3px solid var(--line)",
        borderTop: "3px solid var(--accent)",
        animation: "spin 0.9s linear infinite",
        margin: "0 auto 24px",
      }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <h2 style={{ fontWeight: 700, color: "var(--ink)", fontSize: "1.25rem", letterSpacing: "-0.01em" }}>
        Memverifikasi pembayaran...
      </h2>
      <p style={{ color: "var(--ink-soft)", marginTop: 8, lineHeight: 1.65 }}>
        Sedang mengkonfirmasi pembayaranmu dengan Midtrans.
      </p>
    </div>
  );
}

function SuccessStep({ sessionId, onView }: { sessionId: string; onView: () => void }) {
  return (
    <div style={{ textAlign: "center", padding: "40px 0" }}>
      <div style={{
        width: 68, height: 68, borderRadius: "50%",
        background: "#ECFDF5", border: "2px solid #A7F3D0",
        display: "flex", alignItems: "center", justifyContent: "center",
        margin: "0 auto 24px",
      }}>
        <svg width="30" height="30" viewBox="0 0 24 24" fill="none">
          <path d="M5 12L10 17L20 7" stroke="#15803D" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </div>
      <h2 style={{ fontWeight: 800, color: "var(--ink)", fontSize: "1.5rem", marginBottom: 8, letterSpacing: "-0.02em" }}>
        Pembayaran berhasil!
      </h2>
      <p style={{ color: "var(--ink-soft)", marginBottom: 32, lineHeight: 1.65 }}>
        Semua saran dan CV hasil revisi sudah bisa kamu akses.
      </p>
      <button
        onClick={onView}
        style={{
          padding: "14px 32px",
          background: "var(--accent)", color: "#fff",
          border: "none", borderRadius: 10,
          fontWeight: 600, fontSize: "0.96rem",
          cursor: "pointer", letterSpacing: "-0.01em",
        }}
      >
        Lihat semua saran & unduh laporan
      </button>
    </div>
  );
}

function ErrorStep({ error, onRetry }: { error: string; onRetry: () => void }) {
  return (
    <div style={{ textAlign: "center", padding: "40px 0" }}>
      <div style={{
        width: 68, height: 68, borderRadius: "50%",
        background: "#FEF2F2", border: "2px solid #FECACA",
        display: "flex", alignItems: "center", justifyContent: "center",
        margin: "0 auto 24px",
      }}>
        <svg width="30" height="30" viewBox="0 0 24 24" fill="none">
          <path d="M12 8V12M12 16H12.01" stroke="#DC2626" strokeWidth="2.5" strokeLinecap="round"/>
          <circle cx="12" cy="12" r="9" stroke="#DC2626" strokeWidth="2"/>
        </svg>
      </div>
      <h2 style={{ fontWeight: 700, color: "var(--ink)", fontSize: "1.3rem", marginBottom: 8, letterSpacing: "-0.01em" }}>
        Terjadi kendala
      </h2>
      <p style={{ color: "var(--ink-soft)", marginBottom: 32, maxWidth: 380, margin: "0 auto 32px", lineHeight: 1.65 }}>
        {error}
      </p>
      <button
        onClick={onRetry}
        style={{
          padding: "12px 28px",
          background: "var(--accent)", color: "#fff",
          border: "none", borderRadius: 10,
          fontWeight: 600, fontSize: "0.92rem",
          cursor: "pointer", letterSpacing: "-0.01em",
        }}
      >
        Coba lagi
      </button>
    </div>
  );
}
