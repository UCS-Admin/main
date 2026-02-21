export default function Page() {
  return (
    <main className="p-8 space-y-3">
      <h1 className="text-2xl font-semibold">Question Paper Practice Zone</h1>
      <p>Solve last 10 years papers uploaded by admin. AI extracts format and creates similar papers with timer mode.</p>
      <div className="bg-white border rounded p-4 text-sm">
        <p>Practice Flow:</p>
        <ol className="list-decimal ml-6">
          <li>Select chapter or full paper.</li>
          <li>Start timed mock test.</li>
          <li>Submit and view answer key + weak chapter analytics.</li>
        </ol>
      </div>
    </main>
  );
}
