"""Relevé « En bref » du making-of : `pc bilan` → making-of/en-bref.json.

Lit les transcriptions locales de Claude Code pour ce dépôt (privées, jamais versionnées) et
n'en écrit que des agrégats : durées, nombres de messages et de signes, jetons, coût équivalent
API. Aucun texte, aucun chemin, aucun identifiant de session n'est exporté.

Définitions (reprises sur le site, section « En bref » du making-of) :

- **session** : une entrée « ## Session N — AAAA-MM-JJ, à partir de HH h MM » de
  making-of/JOURNAL.md. Une transcription est rattachée à la session dont l'heure de début est
  la plus proche de sa première demande de l'auteur ;
- **temps actif** : périodes où la transcription (fil principal et agents) enregistre une
  activité, une pause de plus de `PAUSE` coupant la période ;
- **calcul des modèles** : `totalAPIDuration` du relevé de coût de Claude Code (cumul des
  appels aux modèles, agents compris ; des agents en parallèle comptent chacun) ;
- **commandes** : `totalToolDuration` (outils lancés par l'IA : tests, téléchargements, build) ;
- **réponse de l'auteur** : temps entre la dernière activité du fil principal et la demande
  suivante de l'auteur (ou sa réponse à une question posée par Claude), compté seulement s'il
  est inférieur à `PAUSE`. Un ordre de grandeur, ni borne basse ni borne haute : il peut
  inclure de courtes absences et ignore les relectures plus longues, faites pendant que Claude
  travaille, ou hors session ;
- **signes** : caractères, espaces comprises, des messages tapés par l'auteur et de ses
  réponses libres aux questions de Claude ; un **feuillet** vaut 1 500 signes ;
- **jetons** : `modelUsage` du relevé de coût (produits = sortie, réflexion comprise),
  recoupé avec la somme des réponses des transcriptions (fil principal et agents) : un écart
  de plus de `ECART_MAX` sur les jetons produits par Opus et Sonnet arrête le relevé. Le
  relevé de coût n'est écrit qu'à la clôture d'une conversation : pour une session en cours,
  les jetons viennent des transcriptions seules (sans Haiku, appelé hors transcription), et
  durée des appels, commandes et coût manquent (`incomplet`) ;
- **coût équivalent API** : `totalCostUSD`, calculé par Claude Code au tarif public de l'API ;
  ce n'est pas une facture.

Rattachement : une transcription va à la dernière session du journal commencée avant sa
première activité (tolérance `TOLERANCE`, les heures du journal étant notées à la main).
Seules sont publiées la date de chaque session et des durées, pas d'horaires.
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

PAUSE = timedelta(minutes=30)
TOLERANCE = timedelta(minutes=15)
ECART_MAX = 0.02
MODELES = ("opus", "sonnet", "haiku")
PARIS = ZoneInfo("Europe/Paris")
SIGNES_PAR_FEUILLET = 1500
ENTETE_SESSION = re.compile(
    r"^## Session (\d+) — (\d{4}-\d{2}-\d{2}), à partir de (\d{1,2}) h (\d{2})", re.M
)


def dossier_transcriptions(racine: Path) -> Path:
    """Dossier où Claude Code range les transcriptions de ce dépôt (nom dérivé du chemin)."""
    nom = re.sub(r"[^A-Za-z0-9]", "-", str(racine.resolve()))
    return Path.home() / ".claude" / "projects" / nom


def debuts_sessions(journal: str) -> dict[int, datetime]:
    debuts = {}
    for n, jour, h, m in ENTETE_SESSION.findall(journal):
        local = datetime.fromisoformat(f"{jour}T{int(h):02d}:{m}").replace(tzinfo=PARIS)
        debuts[int(n)] = local.astimezone(timezone.utc)
    return debuts


def _ts(d: dict) -> datetime | None:
    t = d.get("timestamp")
    return datetime.fromisoformat(t.replace("Z", "+00:00")) if isinstance(t, str) else None


def _lignes(f: Path):
    with f.open(encoding="utf-8") as fh:
        for ligne in fh:
            try:
                yield json.loads(ligne)
            except json.JSONDecodeError:
                continue


def _texte(contenu) -> str:
    if isinstance(contenu, str):
        return contenu
    return "".join(b.get("text", "") for b in contenu if b.get("type") == "text")


def _reponses_question(contenu: str, libelles: set[str]) -> tuple[int, int]:
    """(choix parmi les options, signes de réponses libres) d'un résultat AskUserQuestion."""
    choix = signes = 0
    for reponse in re.findall(r'"=\s*"(.*?)"(?:\.|,|\s*$)', contenu, re.S):
        parties = [x.strip() for x in reponse.split(",")]
        if reponse.strip() in libelles or all(x in libelles for x in parties):
            choix += 1  # une ou plusieurs options cochées : rien d'écrit
        else:
            signes += len(reponse)
    return choix, signes


def _modele(nom: str) -> str:
    """Famille du modèle ; tout identifiant non reconnu devient « autre » (jamais publié brut)."""
    return next((k for k in MODELES if k in (nom or "")), "autre")


def _usage_transcription(lignes, cumul: dict) -> None:
    """Ajoute à `cumul` les jetons des réponses d'une transcription (une réponse découpée en
    plusieurs lignes porte le même identifiant : on garde sa dernière ligne)."""
    vus: dict[str, tuple[str, dict]] = {}
    for d in lignes:
        if d.get("type") == "assistant":
            m = d.get("message", {})
            if m.get("id") and m.get("usage"):
                vus[m["id"]] = (_modele(m.get("model", "")), m["usage"])
    for modele, u in vus.values():
        c = cumul.setdefault(modele, dict.fromkeys(
            ("produits", "dont_reflexion", "entree", "lus_en_cache", "ecrits_en_cache"), 0))
        c["produits"] += u.get("output_tokens", 0) or 0
        c["dont_reflexion"] += (u.get("output_tokens_details") or {}).get("thinking_tokens", 0) or 0
        c["entree"] += u.get("input_tokens", 0) or 0
        c["lus_en_cache"] += u.get("cache_read_input_tokens", 0) or 0
        c["ecrits_en_cache"] += u.get("cache_creation_input_tokens", 0) or 0


def periodes(instants: list[datetime]) -> list[tuple[datetime, datetime]]:
    res: list[list[datetime]] = []
    for t in sorted(instants):
        if res and t - res[-1][1] <= PAUSE:
            res[-1][1] = t
        else:
            res.append([t, t])
    return [(a, b) for a, b in res]


def analyser_transcription(f: Path) -> dict:
    """Agrégats d'une transcription principale et de ses agents."""
    instants: list[datetime] = []
    derniere_activite: datetime | None = None
    demandes: list[datetime] = []
    reponse = timedelta()
    messages = signes = choix = 0
    questions: dict[str, tuple[datetime, set[str]]] = {}
    cout = None
    usage: dict[str, dict] = {}
    principales = list(_lignes(f))
    _usage_transcription(principales, usage)
    for d in principales:
        t = _ts(d)
        typ = d.get("type")
        if typ == "cost-state":
            cout = d
            continue
        if t is None or typ not in ("user", "assistant", "system", "attachment"):
            continue
        instants.append(t)
        origine = d.get("origin") if isinstance(d.get("origin"), dict) else {}
        contenu = d.get("message", {}).get("content") if typ in ("user", "assistant") else None
        if typ == "user" and origine.get("kind") == "human":
            if _texte(contenu).lstrip().startswith(("/", "<command-")):
                continue  # commande tapée (/clear…), pas une demande
            messages += 1
            demandes.append(t)
            if d.get("promptSource") == "typed":
                signes += len(_texte(contenu))
            if derniere_activite and t - derniere_activite <= PAUSE:
                reponse += t - derniere_activite
        elif typ == "assistant" and isinstance(contenu, list):
            for b in contenu:
                if b.get("type") == "tool_use" and b.get("name") == "AskUserQuestion":
                    libelles = {
                        o.get("label", "").strip()
                        for q in b.get("input", {}).get("questions", [])
                        for o in q.get("options", [])
                    }
                    questions[b.get("id")] = (t, libelles)
        elif typ == "user" and isinstance(contenu, list):
            for b in contenu:
                if b.get("type") == "tool_result" and b.get("tool_use_id") in questions:
                    pose, libelles = questions.pop(b["tool_use_id"])
                    c, s = _reponses_question(_texte(b.get("content") or ""), libelles)
                    choix += c
                    signes += s
                    if t - pose <= PAUSE:
                        reponse += t - pose
        if typ in ("assistant", "system") or (typ == "user" and origine.get("kind") != "human"):
            derniere_activite = t

    agents = {"opus": 0, "sonnet": 0, "haiku": 0, "autre": 0}
    dossier = f.with_suffix("") / "subagents"
    for meta in sorted(dossier.glob("*.meta.json")) if dossier.is_dir() else []:
        # Modèle réellement utilisé (réponses de l'agent), à défaut celui demandé au lancement.
        m = json.loads(meta.read_text(encoding="utf-8"))
        modele = str(m.get("model") or "")
        jsonl = meta.with_name(meta.name.replace(".meta.json", ".jsonl"))
        if jsonl.exists():
            lignes_agent = list(_lignes(jsonl))
            _usage_transcription(lignes_agent, usage)
            for d in lignes_agent:
                if t := _ts(d):
                    instants.append(t)
                if d.get("type") == "assistant":
                    modele = str(d.get("message", {}).get("model") or modele)
        agents[_modele(modele)] += 1

    if cout:
        jetons: dict[str, dict] = {}
        for modele, u in sorted((cout.get("modelUsage") or {}).items()):
            c = jetons.setdefault(_modele(modele), dict.fromkeys(
                ("produits", "dont_reflexion", "entree", "lus_en_cache", "ecrits_en_cache"), 0))
            c["produits"] += u.get("outputTokens", 0)
            c["dont_reflexion"] += u.get("thinkingTokens", 0)
            c["entree"] += u.get("inputTokens", 0)
            c["lus_en_cache"] += u.get("cacheReadInputTokens", 0)
            c["ecrits_en_cache"] += u.get("cacheCreationInputTokens", 0)
        verifier_recoupement(jetons, usage, f.name)
    else:
        jetons = usage
    actives = periodes(instants)
    return {
        "premiere_activite": actives[0][0] if actives else None,
        "incomplet": cout is None,
        "periodes": actives,
        "actif_min": round(sum((b - a for a, b in actives), timedelta()).total_seconds() / 60),
        "reponse_auteur_min": round(reponse.total_seconds() / 60),
        "messages_auteur": messages,
        "choix_auteur": choix,
        "signes_auteur": signes,
        "agents": {k: v for k, v in agents.items() if v},
        "calcul_modeles_min": round((cout or {}).get("totalAPIDuration", 0) / 60000),
        "commandes_min": round((cout or {}).get("totalToolDuration", 0) / 60000),
        "jetons": jetons,
        "cout_api_usd": round((cout or {}).get("totalCostUSD", 0), 2) if cout else None,
    }


def verifier_recoupement(releve: dict, transcriptions: dict, nom: str) -> None:
    """Le relevé de coût de Claude Code doit retrouver les jetons produits des transcriptions
    (Opus, Sonnet) : sinon il couvre autre chose que cette conversation (compteur cumulé sur
    plusieurs conversations, transcription tronquée) et le relevé s'arrête."""
    for modele in ("opus", "sonnet"):
        a = releve.get(modele, {}).get("produits", 0)
        b = transcriptions.get(modele, {}).get("produits", 0)
        if max(a, b) and abs(a - b) / max(a, b) > ECART_MAX:
            raise SystemExit(
                f"Relevé de coût et transcriptions divergent ({modele}, {nom}) : {a} contre {b} "
                "jetons produits ; vérifier ce que couvre le relevé avant de publier.")


def _additionner(a: dict, b: dict) -> dict:
    """Somme récursive de deux agrégats (nombres et dictionnaires de nombres)."""
    res = dict(a)
    for k, v in b.items():
        if isinstance(v, dict):
            res[k] = _additionner(res.get(k, {}), v)
        elif isinstance(v, bool):
            res[k] = bool(res.get(k)) or v
        elif isinstance(v, (int, float)) and v is not None:
            res[k] = round((res.get(k) or 0) + v, 2)
        elif k not in res:
            res[k] = v
    return res


def _git(racine: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=racine, capture_output=True, text=True,
                          check=True).stdout


def releve_depot(racine: Path) -> dict:
    fichiers = _git(racine, "ls-files").splitlines()

    def lignes(pred) -> int:
        n = 0
        for f in fichiers:
            p = racine / f
            if pred(f) and p.is_file():
                n += sum(1 for _ in p.open(encoding="utf-8", errors="replace"))
        return n

    def signes(pred) -> int:
        return sum(len((racine / f).read_text(encoding="utf-8")) for f in fichiers
                   if pred(f) and (racine / f).is_file())

    est_test = lambda f: "/tests/" in f or ".test." in f  # noqa: E731
    return {
        "commits": int(_git(racine, "rev-list", "--count", "HEAD").strip()),
        "lignes_python": lignes(lambda f: f.startswith("pipeline/") and f.endswith(".py")
                                and not est_test(f)),
        "lignes_site": lignes(lambda f: f.startswith("site/src/")
                              and f.endswith((".ts", ".svelte", ".css")) and not est_test(f)),
        "lignes_tests": lignes(lambda f: est_test(f) and f.endswith((".py", ".ts"))),
        "signes_brief": signes(lambda f: f == "docs/BRIEF.md"),
        # Pages lues sur le site : enquêtes, méthode, message, making-of, textes du simulateur.
        "signes_pages_site": signes(est_page_site),
        # Rapports de travail versionnés (spikes, relectures, spécifications), non publiés en page.
        "signes_rapports": signes(
            lambda f: f.endswith(".md") and f.startswith("docs/") and f != "docs/BRIEF.md"
            and not est_page_site(f)),
    }


def est_page_site(f: str) -> bool:
    return f.endswith(".md") and (
        f.startswith(("docs/enquetes/", "making-of/", "site/src/"))
        or f in ("docs/METHODO.md", "docs/MESSAGE.md"))


def bilan(racine: Path, sortie: Path, transcriptions: Path | None = None) -> dict:
    dossier = transcriptions or dossier_transcriptions(racine)
    debuts = debuts_sessions((racine / "making-of/JOURNAL.md").read_text(encoding="utf-8"))
    if not debuts:
        raise SystemExit("Aucune entrée « ## Session N — … » dans making-of/JOURNAL.md")
    par_session: dict[int, dict] = {}
    for f in sorted(dossier.glob("*.jsonl")):
        a = analyser_transcription(f)
        debut = a.pop("premiere_activite")
        a.pop("periodes")
        if debut is None:
            continue
        avant = [k for k in debuts if debuts[k] <= debut + TOLERANCE]
        n = max(avant, key=lambda k: debuts[k]) if avant else min(debuts)
        s = par_session.setdefault(n, {"date": debut.astimezone(PARIS).date().isoformat()})
        par_session[n] = _additionner(s, a)
    sessions = [{"numero": n, **par_session[n]} for n in sorted(par_session)]
    total: dict = {}
    for s in sessions:
        total = _additionner(total, {k: v for k, v in s.items()
                                     if k not in ("numero", "date")})
    total["feuillets_auteur"] = round(total.get("signes_auteur", 0) / SIGNES_PAR_FEUILLET, 1)
    depot = releve_depot(racine)
    depot["feuillets_brief"] = round(depot["signes_brief"] / SIGNES_PAR_FEUILLET, 1)
    depot["feuillets_pages_site"] = round(depot["signes_pages_site"] / SIGNES_PAR_FEUILLET)
    depot["feuillets_rapports"] = round(depot["signes_rapports"] / SIGNES_PAR_FEUILLET)
    res = {
        "releve": datetime.now(PARIS).isoformat(timespec="minutes"),
        "pause_min": int(PAUSE.total_seconds() / 60),
        "signes_par_feuillet": SIGNES_PAR_FEUILLET,
        "sessions": sessions,
        "total": total,
        "depot": depot,
    }
    sortie.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return res
