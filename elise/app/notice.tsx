// Écrans d'information quand quelque chose manque encore.

export function Notice({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <main className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center gap-4 px-6 py-12">
      <h1 className="font-serif text-3xl text-accent">{title}</h1>
      <div className="flex flex-col gap-3 leading-relaxed">{children}</div>
    </main>
  );
}

/** Les réglages du site qui manquent encore sur Vercel. */
export function missingSettings(): string[] {
  const missing: string[] = [];
  if (!process.env.NEXT_PUBLIC_SUPABASE_URL?.trim()) missing.push("NEXT_PUBLIC_SUPABASE_URL");
  if (!process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY?.trim()) missing.push("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY");
  if (!process.env.SUPABASE_SECRET_KEY?.trim()) missing.push("SUPABASE_SECRET_KEY");
  return missing;
}

export function SetupNotice({ missing = missingSettings() }: { missing?: string[] }) {
  return (
    <Notice title="Élise n'est pas encore branchée">
      <p>Il manque des réglages. Sur Vercel, dans Settings → Environment Variables, ajoutez :</p>
      <ul className="list-disc pl-6 font-mono text-sm">
        {missing.map((m) => (
          <li key={m}>{m}</li>
        ))}
      </ul>
      <p>puis redéployez.</p>
    </Notice>
  );
}
