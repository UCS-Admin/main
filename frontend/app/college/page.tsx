export default function CollegePage() {
  return (
    <main className="p-8 space-y-3">
      <h1 className="text-2xl font-semibold">College Dashboard</h1>
      <p>Total applications, pending verifications, and admission analytics overview.</p>
      <ul className="list-disc ml-6 text-sm">
        <li><a className="underline" href="/college/profile">Institute Profile</a></li>
        <li><a className="underline" href="/college/applications">Applications</a></li>
        <li><a className="underline" href="/college/analytics">Analytics</a></li>
      </ul>
    </main>
  );
}
