import "server-only";
import { NextResponse } from "next/server";

// Les réponses des routes /api/offres : la base explique elle-même, en
// français, pourquoi une action est refusée (plafond, offre expirée…).

export function offerError(error: { code?: string; message?: string }) {
  const status = error.code === "P0002" ? 404 : error.code === "42501" ? 403 : error.code === "P0001" ? 400 : 500;
  const message =
    status === 500 ? "L'opération n'a pas abouti. Réessayez dans un instant." : (error.message ?? "Action impossible.");
  return NextResponse.json({ error: message }, { status });
}

export function offerId(raw: string): number | null {
  const id = Number(raw);
  return Number.isInteger(id) && id > 0 ? id : null;
}
