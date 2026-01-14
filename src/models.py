from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SheetRow:
    row_index: int  # 1-based index in Google Sheets
    annonce_lbc: str
    lien_annonce: str
    photos: str
    dossier_photos: str
    categorie: str
    pieces: str
    objet: str
    marques: str
    modele: str
    quantite: str
    etat: str
    prix_neuf_unite: str
    prix_total: str
    prix_demande_unite: str
    prix_total_demande: str
    status: str
    a_publier: str

    def should_publish(self) -> bool:
        ap = (self.a_publier or "").strip().lower()
        status = (self.status or "").strip().lower()
        lien = (self.lien_annonce or "").strip()

        ap_ok = ap in {"oui", "true", "1", "x", "yes"}
        status_ok = status in {"en vente", ""}  # adapt if you use other statuses
        lien_ok = lien == ""

        return ap_ok and status_ok and lien_ok


def parse_eur_amount(value: str) -> int | None:
    """
    Convert a French-formatted EUR cell to an integer amount in euros.
    Examples:
      "240,00  €" -> 240
      "104,30  €" -> 104 (rounded down)
      "-" or "" -> None
    """
    s = (value or "").strip().replace("€", "").replace("\u00a0", " ")
    s = s.replace(" ", "")
    if s in {"", "-", "–"}:
        return None

    # Keep digits, comma, dot
    allowed = set("0123456789,.")
    s = "".join(ch for ch in s if ch in allowed)
    if s == "":
        return None

    # French uses comma decimals
    s = s.replace(",", ".")
    try:
        f = float(s)
    except ValueError:
        return None
    return int(f)


def build_title(row: SheetRow) -> str:
    title = (row.annonce_lbc or "").strip()
    if title:
        return title
    # Fallback: Objet + Marque + Modèle
    parts = [row.objet, row.marques, row.modele]
    parts = [
        p.strip() for p in parts if (p or "").strip() and p.strip() not in {"-", "—"}
    ]
    return " - ".join(parts)[:70] or "Annonce"


def build_description(row: SheetRow) -> str:
    lines = []

    def add(label: str, val: str) -> None:
        v = (val or "").strip()
        if v and v not in {"-", "—"}:
            lines.append(f"{label}: {v}")

    add("Objet", row.objet)
    add("Marque", row.marques)
    add("Modèle", row.modele)
    add("État", row.etat)
    add("Quantité", row.quantite)
    add("Pièce", row.pieces)
    add("Catégorie (source)", row.categorie)

    pn = parse_eur_amount(row.prix_neuf_unite)
    if pn is not None:
        lines.append(f"Prix neuf (unité): {pn} €")

    pt = parse_eur_amount(row.prix_total)
    if pt is not None:
        lines.append(f"Prix neuf (total): {pt} €")

    pdu = parse_eur_amount(row.prix_demande_unite)
    if pdu is not None:
        lines.append(f"Prix demandé (unité): {pdu} €")

    ptd = parse_eur_amount(row.prix_total_demande)
    if ptd is not None:
        lines.append(f"Prix demandé (total): {ptd} €")

    # Add your own seller notes here if needed
    return "\n".join(lines).strip()
