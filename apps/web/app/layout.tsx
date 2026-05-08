import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import { DM_Sans, Newsreader } from "next/font/google";
import "./globals.css";

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-dm",
  display: "swap",
});

const newsreader = Newsreader({
  subsets: ["latin"],
  variable: "--font-newsreader",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Memory Layer · Persistent context for agents",
  description:
    "Postgres-native memory infrastructure: hybrid retrieval, tenant isolation, and an operator console — built for production-minded teams.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html lang="en" className={`${dmSans.variable} ${newsreader.variable}`}>
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}
