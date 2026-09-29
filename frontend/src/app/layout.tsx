import type { Metadata } from "next";
import "./globals.css";
import "leaflet/dist/leaflet.css";
import { ChatAssistant } from "@/components/ChatAssistant";

export const metadata: Metadata = { title: "SpringVyra — Watershed intelligence", description: "Mountain spring monitoring and recharge planning" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}<ChatAssistant /></body></html>;
}
