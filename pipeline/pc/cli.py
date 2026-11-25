"""Ligne de commande : pc download | build | check.

Les sources sont spécifiées à l'issue du spike (docs/SOURCES.md) ; tant
qu'aucune n'est branchée, download et build ne font rien et le disent.
"""

import argparse
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
RAW = RACINE / "data/raw"
EXPORT = RACINE / "data/export"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="pc", description=__doc__)
    sub = ap.add_subparsers(dest="commande", required=True)
    d = sub.add_parser("download", help="télécharge les sources → data/raw/")
    d.add_argument("--raw", type=Path, default=RAW)
    d.add_argument("sources", nargs="*", help="clés de sources (défaut : toutes)")
    b = sub.add_parser("build", help="data/raw/ → data/export/")
    b.add_argument("--raw", type=Path, default=RAW)
    b.add_argument("--export", type=Path, default=EXPORT)
    c = sub.add_parser("check", help="bilans qui bouclent, recoupements entre sources")
    c.add_argument("--export", type=Path, default=EXPORT)
    args = ap.parse_args(argv)

    if args.commande in ("download", "build"):
        print(f"pc {args.commande} : aucune source branchée pour l'instant (étape 1, spike).")
        return 0
    if args.commande == "check":
        print("pc check : aucun contrôle enregistré pour l'instant.")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
