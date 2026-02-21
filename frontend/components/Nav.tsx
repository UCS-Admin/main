export default function Nav() {
  return (
    <nav className="flex gap-4 text-sm bg-white border-b p-3 sticky top-0">
      <a href="/" className="font-semibold">EPC</a>
      <a href="/auth">Login</a>
      <a href="/student">Student</a>
      <a href="/college">College</a>
      <a href="/associate">Associate</a>
      <a href="/admin">Admin</a>
    </nav>
  );
}
