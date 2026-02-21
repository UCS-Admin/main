export default function AdminPage() {
  return (
    <main className="p-8 space-y-4">
      <h2 className="text-2xl font-semibold">Admin Dashboard</h2>
      <p>Master control for verification, rankings, CRM/finance and question paper ingestion.</p>
      <div className="bg-white p-4 rounded border text-sm space-y-2">
        <p><strong>Question Paper AI Pipeline:</strong> Upload last 10 years PDFs → OCR/Text extraction → format blueprint detection → generate similar papers for student practice.</p>
        <code>POST /admin/past-papers/upload</code><br/>
        <code>POST /admin/past-papers/{'{paper_id}'}/ingest</code>
      </div>
      <ul className="list-disc ml-6 text-sm">
        <li><a className="underline" href="/admin/verification">Verification</a></li>
        <li><a className="underline" href="/admin/rankings">Ranking Management</a></li>
        <li><a className="underline" href="/admin/crm">CRM & Finance</a></li>
      </ul>
    </main>
  );
}
