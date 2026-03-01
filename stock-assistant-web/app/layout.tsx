import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "🇮🇳 Indian Stock Market AI Assistant",
  description:
    "AI-powered stock market assistant for NSE & BSE. Get live prices, technical analysis, fundamentals, and market news.",
  keywords: [
    "Indian stocks",
    "NSE",
    "BSE",
    "Nifty 50",
    "stock analysis",
    "AI assistant",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-[#0a0e1a] text-gray-50 antialiased`}>
        {children}
      </body>
    </html>
  );
}
