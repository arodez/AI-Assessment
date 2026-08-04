import "./globals.css";

export const metadata = {
  title: "Community Events Hub",
  description: "Create, browse, and RSVP to community events.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <main>{children}</main>
      </body>
    </html>
  );
}
