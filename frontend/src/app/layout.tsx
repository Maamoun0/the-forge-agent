import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "The Forge | AI Agentic Factory",
  description: "Self-healing, multi-agent autonomous software engineering system.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-[#030712] text-white antialiased`}>
        {children}
      </body>
    </html>
  );
}
