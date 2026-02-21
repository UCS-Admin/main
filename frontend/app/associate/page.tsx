export default function AssociatePage() {
  return (
    <main className="p-8 space-y-3">
      <h1 className="text-2xl font-semibold">Associate Dashboard</h1>
      <p>Lead conversion status, referrals, and earnings summary.</p>
      <ul className="list-disc ml-6 text-sm">
        <li><a className="underline" href="/associate/leads">Lead Management</a></li>
        <li><a className="underline" href="/associate/commission">Commission</a></li>
      </ul>
    </main>
  );
}
