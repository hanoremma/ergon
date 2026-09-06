import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ergon — AI CV-Fit Scorer & Enhancer",
  description: "Tahu dulu seberapa cocok CV-mu, sebelum kirim lamaran. Ergon membaca loker dan CV-mu, lalu kasih skor kecocokan lengkap dengan alasannya.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
