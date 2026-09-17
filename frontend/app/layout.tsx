import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ergon — AI CV-Fit Scorer & Enhancer",
  description: "Tahu dulu seberapa cocok CV-mu, sebelum kirim lamaran. Ergon membaca loker dan CV-mu, lalu kasih skor kecocokan lengkap dengan alasannya.",
  icons: {
    icon: "/logo-ergon.png",
    shortcut: "/logo-ergon.png",
    apple: "/logo-ergon.png",
  },
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
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
