import Link from "next/link";

export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 text-slate-900">
      <h1 className="text-6xl font-black tracking-tight">404</h1>
      <p className="text-lg text-slate-500">Page not found.</p>
      <Link
        href="/dashboard"
        className="mt-4 rounded-full bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-700"
      >
        Back to Dashboard
      </Link>
    </main>
  );
}
