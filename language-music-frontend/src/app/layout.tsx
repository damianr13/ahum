import "./styles/globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Analytics } from "@vercel/analytics/react";
import React from "react";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Ahum.io",
  description: "Learn a language through music",
};

declare global {
  interface Window {
    onSpotifyIframeApiReady: any;
  }
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-900">
        {children}
        <Analytics />
      </body>
    </html>
  );
}
