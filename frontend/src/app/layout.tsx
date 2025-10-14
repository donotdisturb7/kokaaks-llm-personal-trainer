import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ChatProvider } from "@/contexts/ChatContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "KovaaK's AI Personal Trainer",
  description: "AI-powered aim training assistant",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <div className="min-h-screen bg-background text-foreground">
          <ChatProvider>
            {children}
          </ChatProvider>
        </div>
      </body>
    </html>
  );
}