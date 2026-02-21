import "./globals.css";
import Nav from "../components/Nav";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900">
        <Nav />
        {children}
      </body>
    </html>
  );
}
