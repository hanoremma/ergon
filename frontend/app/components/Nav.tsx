import Link from "next/link";

export default function Nav() {
  return (
    <header style={{
      borderBottom: "1px solid var(--line)",
      background: "rgba(245, 249, 253, 0.92)",
      backdropFilter: "blur(8px)",
      position: "sticky",
      top: 0,
      zIndex: 50,
    }}>
      <div style={{
        maxWidth: 1160,
        margin: "0 auto",
        padding: "0 32px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        height: 64,
      }}>
        <Link href="/" style={{
          fontWeight: 700,
          fontSize: "1.25rem",
          display: "flex",
          alignItems: "center",
          gap: 9,
          color: "var(--ink)",
          letterSpacing: "-0.02em",
        }}>
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <rect width="28" height="28" rx="8" fill="var(--accent)"/>
            <path d="M8 14C8 10.686 10.686 8 14 8C17.314 8 20 10.686 20 14" stroke="white" strokeWidth="2" strokeLinecap="round"/>
            <circle cx="14" cy="18" r="3" fill="white"/>
          </svg>
          Ergon
        </Link>

        <nav style={{ display: "flex", gap: 28, fontSize: "0.9rem", color: "var(--ink-soft)" }}>
          <Link href="/#how" style={{ color: "var(--ink-soft)", fontWeight: 500 }}>Cara kerja</Link>
          <Link href="/#unlock" style={{ color: "var(--ink-soft)", fontWeight: 500 }}>Harga</Link>
          <Link href="/#soon" style={{ color: "var(--ink-soft)", fontWeight: 500 }}>Wawancara AI</Link>
        </nav>

        <Link href="/upload" style={{
          background: "var(--accent)",
          color: "#fff",
          padding: "10px 22px",
          borderRadius: 10,
          fontSize: "0.9rem",
          fontWeight: 600,
          letterSpacing: "-0.01em",
        }}>
          Coba gratis
        </Link>
      </div>
    </header>
  );
}
