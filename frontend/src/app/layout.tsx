import type { Metadata } from "next";
import { TelegramProvider } from "@/components/TelegramProvider";
import "./globals.css";

export const metadata: Metadata = {
  title: "Каталог",
  description: "Каталог товаров Invix Assessment",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body>
        <TelegramProvider>{children}</TelegramProvider>
      </body>
    </html>
  );
}
