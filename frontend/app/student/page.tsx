export default function StudentPage() {
  return (
    <main className="p-8 space-y-4">
      <h2 className="text-2xl font-semibold">Student Dashboard</h2>
      <div className="grid md:grid-cols-3 gap-4">
        <div className="bg-white border rounded p-4"><h3 className="font-medium">EPC Digital Card</h3><p className="text-sm">QR + EPC ID ready for single-click applications.</p></div>
        <div className="bg-white border rounded p-4"><h3 className="font-medium">Admission Snapshot</h3><p className="text-sm">Pending / Approved / Rejected status view.</p></div>
        <div className="bg-white border rounded p-4"><h3 className="font-medium">Quick Apply</h3><p className="text-sm">Apply to multiple colleges from EPC profile.</p></div>
      </div>
      <div className="bg-white border rounded p-4">
        <h3 className="font-semibold">Question Paper Practice (Last 10 Years)</h3>
        <p className="text-sm mt-1">Admin-uploaded PDFs are AI-read and transformed into similar paper patterns so you can solve timed mock tests daily.</p>
        <div className="mt-3 flex gap-3 text-sm">
          <a href="/student/practice" className="underline text-blue-600">Open Practice Zone</a>
          <a href="/student/profile" className="underline text-blue-600">Profile & Documents</a>
        </div>
      </div>
      <ul className="list-disc ml-6 text-sm">
        <li><a className="underline" href="/student/colleges">College Search & Compare</a></li>
        <li><a className="underline" href="/student/apply">Apply</a></li>
        <li><a className="underline" href="/student/status">Admission Status</a></li>
        <li><a className="underline" href="/student/finance">Finance (fees, loan, scholarship)</a></li>
      </ul>
    </main>
  );
}
