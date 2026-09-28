// Écrans d'information quand quelque chose manque encore.

export function Notice({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <main className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center gap-4 px-6 py-12">
      <h1 className="font-serif text-3xl text-accent">{title}</h1>
      <div className="flex flex-col gap-3 leading-relaxed">{children}</div>
    </main>
  );
}

export function SetupNotice() {
  return (
    <Notice title="Élise n'est pas encore branchée">
      <p>Il manque les réglages de Supabase. Sur Vercel, dans Settings → Environment Variables, ajoutez :</p>
      <ul className="list-disc pl-6 font-mono text-sm">
        <li>NEXT_PUBLIC_SUPABASE_URL</li>
        <li>NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY</li>
      </ul>
      <p>puis redéployez.</p>
    </Notice>
  );
}
