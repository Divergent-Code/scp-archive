import type { Metadata } from "next";
import "./globals.css";
import Header from "./header";

export const metadata: Metadata = {
  title: "SCP Foundation Archive",
  description:
    "An interactive archive of the SCP Foundation universe. Browse SCPs, tales, and GOI formats with an AI guide.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Header />
        <main className="container" style={{ paddingTop: 24, paddingBottom: 48 }}>
          {children}
        </main>
      </body>
    </html>
  );
}