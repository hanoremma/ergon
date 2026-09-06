export default function Footer() {
  return (
    <footer style={{
      padding: "48px 0 60px",
      borderTop: "1px solid var(--accent-soft)",
      marginTop: 40,
    }}>
      <div style={{
        maxWidth: 1160,
        margin: "0 auto",
        padding: "0 32px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        fontSize: "0.86rem",
        color: "var(--muted)",
      }}>
        <span>© 2026 Ergon</span>
        <span>Dibuat untuk membantu pencari kerja melamar lebih tepat sasaran</span>
      </div>
    </footer>
  );
}
