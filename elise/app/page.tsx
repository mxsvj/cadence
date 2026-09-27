// Page d'attente de l'étape 1. Elle sera remplacée par la conversation.
export default function Home() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-4 px-6 text-center">
      <h1 className="font-serif text-5xl text-accent">Élise</h1>
      <p className="max-w-sm text-muted">
        Quelqu&apos;un à qui parler, qui se souvient de vous.
        <br />
        La conversation arrive bientôt.
      </p>
    </main>
  );
}
