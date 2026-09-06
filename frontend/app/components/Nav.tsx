import Link from "next/link";

export default function Nav() {
  return (
    <header style={{
      borderBottom: "1px solid var(--accent-soft)",
      background: "var(--bg-page)",
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
          fontFamily: "'Space Grotesk', sans-serif",
          fontWeight: 700,
          fontSize: "1.35rem",
          display: "flex",
          alignItems: "center",
          gap: 8,
          color: "var(--ink)",
        }}>
          <span style={{
            width: 9,
            height: 9,
            borderRadius: "50%",
            background: "var(--accent)",
            display: "inline-block",
          }} />
          Ergon
        </Link>

        <nav style={{ display: "flex", gap: 32, fontSize: "0.95rem", color: "var(--ink-soft)" }}>
          <Link href="/#how" style={{ color: "var(--ink-soft)" }}>Cara kerja</Link>
          <Link href="/#unlock" style={{ color: "var(--ink-soft)" }}>Harga</Link>
          <Link href="/#soon" style={{ color: "var(--ink-soft)" }}>Latihan wawancara</Link>
        </nav>

        <Link href="/upload" style={{
          background: "var(--ink)",
          color: "#fff",
          padding: "10px 20px",
          borderRadius: 10,
          fontSize: "0.92rem",
          fontWeight: 500,
        }}>
          Coba gratis
        </Link>
      </div>
    </header>
  );
}
