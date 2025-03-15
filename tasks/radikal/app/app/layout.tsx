import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Радикал-Формула',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <header className="container">
          <div style={{ padding: '1rem 0', borderBottom: '1px solid #eaeaea' }}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={process.env.basePath + "/radikal.png"} alt="Радикал-Фото" />
          </div>
        </header>
        <main className="container" style={{ padding: '2rem 1rem', minHeight: 'calc(100vh - 200px)' }}>
          {children}
        </main>
        <footer style={{ padding: '2rem 0', borderTop: '1px solid #eaeaea', textAlign: 'center' }}>
          <div className="container">
            <p>&copy; {new Date().getFullYear()} Радикал-Формула 2005-2025</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
