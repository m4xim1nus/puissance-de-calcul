"""Ligne de commande : pc download | build | check.

- `pc download [clés…] [--force]` : sources → data/raw/ (+ manifeste.json) ;
- `pc build` : data/raw/ → data/export/ ;
- `pc check` : contrôles de cohérence sur data/export/ et les références
  de data/raw/ ; code de retour non nul si un contrôle échoue.

Spécification des sources et des contrôles : docs/spike/systeme.md.
"""

import argparse
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
RAW = RACINE / "data/raw"
EXPORT = RACINE / "data/export"


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
    c = sub.add_parser("check", help="bilans qui bouclent, recoupements entre sources")
    c.add_argument("--raw", type=Path, default=RAW)
    c.add_argument("--export", type=Path, default=EXPORT)
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
        chiffres.exporter(ref, args.export / "chiffres.json")
        build(args.raw, args.export)
        return 0
    if args.commande == "check":
        from .check import check
        return check(args.raw, args.export)
    return 0


if __name__ == "__main__":
    sys.exit(main())
