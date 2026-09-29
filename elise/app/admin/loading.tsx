// Ce qui s'affiche dès qu'on touche un onglet, le temps que la page arrive :
// le changement est visible tout de suite, même si le réseau est lent.
export default function AdminLoading() {
  const block = "rounded-3xl bg-line/60 motion-safe:animate-pulse";
  return (
    <div
      role="status"
      aria-label="Chargement"
      className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-4 py-6 sm:px-6"
    >
      <div className="h-9 w-48 rounded-xl bg-line/60 motion-safe:animate-pulse" />
      <div className="grid gap-4 sm:grid-cols-3">
        <div className={`h-32 ${block}`} />
        <div className={`h-32 ${block}`} />
        <div className={`h-32 ${block}`} />
      </div>
      <div className={`h-64 ${block}`} />
    </div>
  );
}
