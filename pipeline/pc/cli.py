"""Ligne de commande : pc download | build | check | bilan.

- `pc download [clés…] [--force]` : sources → data/raw/ (+ manifeste.json) ;
- `pc build` : data/raw/ → data/export/ (dont `chiffres.json` : référentiel saisi + chiffres
  calculés par le pipeline) ; ENTSO-E, s'il a été téléchargé : data/raw/entsoe/ → data/derive/entsoe/
  (non versionné, aucune page ne le lit encore : pc/entsoe_derive.py) ;
- `pc check` : contrôles de cohérence sur data/export/ et les références
  de data/raw/ ; code de retour non nul si un contrôle échoue ;
- `pc bilan` : relevé « En bref » du making-of (transcriptions locales de Claude Code →
  making-of/en-bref.json, agrégats seulement ; à lancer en fin de session).

Spécification des sources et des contrôles : docs/spike/systeme.md.
"""

import argparse
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
RAW = RACINE / "data/raw"
EXPORT = RACINE / "data/export"
DERIVE = RACINE / "data/derive"  # dérivés non publiés, non versionnés (ENTSO-E)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="pc", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="commande", required=True)
    d = sub.add_parser("download", help="télécharge les sources → data/raw/")
    d.add_argument("--raw", type=Path, default=RAW)
    d.add_argument("--force", action="store_true", help="retélécharge aussi les années closes")
    d.add_argument("sources", nargs="*", help="clés de sources (défaut : toutes)")
    b = sub.add_parser("build", help="data/raw/ → data/export/")
    b.add_argument("--raw", type=Path, default=RAW)
    b.add_argument("--export", type=Path, default=EXPORT)
    b.add_argument("--derive", type=Path, default=DERIVE)
    c = sub.add_parser("check", help="bilans qui bouclent, recoupements entre sources")
    c.add_argument("--raw", type=Path, default=RAW)
    c.add_argument("--export", type=Path, default=EXPORT)
    c.add_argument("--derive", type=Path, default=DERIVE)
    sub.add_parser("bilan", help="relevé « En bref » du making-of → making-of/en-bref.json")
    args = ap.parse_args(argv)

    if args.commande == "download":
        from .sources import download
        download(args.raw, args.sources or None, force=args.force)
        return 0
    if args.commande == "build":
        from .build import build
        from . import chiffres
        ref = chiffres.charger()
        erreurs = chiffres.valider(ref)
        if erreurs:
            print("Référentiel des chiffres invalide :\n" + "\n".join(erreurs), file=sys.stderr)
            return 1
        from .export_quand import MODULATION_PUBLIEE, ecretement_du_referentiel, froid_du_referentiel
        modulation = {an: ref.chiffres[cle] for an, cle in MODULATION_PUBLIEE.items() if cle in ref.chiffres}
        sources_calc, chiffres_calc = build(args.raw, args.export, modulation,
                                            ecretement_du_referentiel(ref.chiffres),
                                            froid_du_referentiel(ref.chiffres), ref.chiffres)
        complet = chiffres.fusionner(ref, sources_calc, chiffres_calc)
        erreurs = chiffres.valider(complet)
        if erreurs:
            print("Chiffres calculés invalides :\n" + "\n".join(erreurs), file=sys.stderr)
            return 1
        chiffres.exporter(complet, args.export / "chiffres.json")
        from . import entsoe_derive
        entsoe_derive.construire(args.raw, args.derive)
        return 0
    if args.commande == "check":
        from .check import check
        return check(args.raw, args.export, derive=args.derive)
    if args.commande == "bilan":
        from .bilan import bilan
        res = bilan(RACINE, RACINE / "making-of/en-bref.json")
        print(f"{len(res['sessions'])} session(s) → making-of/en-bref.json")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
