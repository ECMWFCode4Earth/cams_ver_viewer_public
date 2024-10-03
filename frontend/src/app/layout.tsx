import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AppRouterCacheProvider } from '@mui/material-nextjs/v13-appRouter';

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ECMWF Verification Visualiser",
  description: "Created as a Part of Code4earth2024",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}><AppRouterCacheProvider>{children}</AppRouterCacheProvider></body>
    </html>
  );
}
