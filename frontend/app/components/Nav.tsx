import Link from "next/link";
import Image from "next/image";

export default function Nav() {
  return (
    <header style={{
      borderBottom: "1px solid #e0eefb",
      background: "rgba(255, 255, 255, 0.92)",
      backdropFilter: "blur(12px)",
      position: "sticky",
      top: 0,
      zIndex: 50,
      boxShadow: "0 1px 12px rgba(15,42,74,0.06)",
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
          fontSize: "1.2rem",
          display: "flex",
          alignItems: "center",
          gap: 9,
          color: "#0F2A4A",
          letterSpacing: "-0.025em",
        }}>
          <Image
            src="/logo-ergon-box.png"
            alt="Ergon logo"
            width={36}
            height={36}
            style={{ borderRadius: 8 }}
            priority
          />
          Ergon
        </Link>

        <nav style={{ display: "flex", gap: 24, fontSize: "0.9rem" }}>
          <Link href="/#how" style={{ color: "#3A5878", fontWeight: 500 }}>Cara kerja</Link>
          <Link href="/#unlock" style={{ color: "#3A5878", fontWeight: 500 }}>Harga</Link>
          <Link href="/#soon" style={{ color: "#3A5878", fontWeight: 500 }}>Wawancara AI</Link>
        </nav>

        <Link href="/upload" style={{
          background: "linear-gradient(135deg, #1d4ed8, #3b82f6)",
          color: "#fff",
          padding: "10px 22px",
          borderRadius: 10,
          fontSize: "0.9rem",
          fontWeight: 600,
          letterSpacing: "-0.01em",
          boxShadow: "0 2px 10px rgba(59,130,246,0.30)",
        }}>
          Coba gratis
        </Link>
      </div>
    </header>
  );
}
