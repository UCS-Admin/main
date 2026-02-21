export default function Home() {
  return (
    <main className="p-8 space-y-6">
      <section>
        <h1 className="text-3xl font-bold">EPC Digital Admission Portal</h1>
        <p className="text-slate-600 mt-2">End-to-end admission workflow for Students, Colleges, Associates, and Admin with AI-powered question paper practice.</p>
      </section>
      <section className="grid md:grid-cols-2 gap-4">
        <div className="bg-white border rounded p-4">
          <h2 className="font-semibold">How EPC Works</h2>
          <ul className="list-disc ml-6 mt-2 text-sm">
            <li>Student creates profile and applies using EPC ID.</li>
            <li>College verifies docs and updates admission status.</li>
            <li>Admin monitors verification, rankings, and finance.</li>
            <li>Students practice past 10-year papers from dashboard.</li>
          </ul>
        </div>
        <div className="bg-white border rounded p-4">
          <h2 className="font-semibold">College Rankings</h2>
          <p className="text-sm mt-2">Integrated NIRF, QS, THE, and NAAC updates with search and compare support.</p>
        </div>
      </section>
    </main>
  );
}
