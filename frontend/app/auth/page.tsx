export default function AuthPage() {
  return (
    <main className="p-8 max-w-xl mx-auto space-y-4">
      <h1 className="text-2xl font-semibold">Login / Signup</h1>
      <div className="bg-white border rounded p-4 space-y-3">
        <input className="w-full border rounded px-3 py-2" placeholder="Email" />
        <input className="w-full border rounded px-3 py-2" placeholder="OTP / Password" />
        <select className="w-full border rounded px-3 py-2">
          <option>STUDENT</option>
          <option>COLLEGE</option>
          <option>ASSOCIATE</option>
          <option>ADMIN</option>
        </select>
        <button className="bg-blue-600 text-white rounded px-4 py-2">Continue</button>
      </div>
    </main>
  );
}
