"""Relevé « En bref » : transcriptions synthétiques, aucune donnée réelle."""

import json
from datetime import datetime, timedelta, timezone

from pc import bilan


def _ecrire(f, lignes):
    f.write_text("\n".join(json.dumps(x) for x in lignes) + "\n", encoding="utf-8")


def _t(minutes):
    return (datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc) + timedelta(minutes=minutes)).isoformat()


def test_debuts_sessions_heure_de_paris():
    journal = "## Session 1 — 2026-11-25, à partir de 23 h 03 · x\n\n## Session 2 — 2026-07-01, à partir de 9 h 10 · y\n"
    d = bilan.debuts_sessions(journal)
    assert d[1] == datetime(2026, 11, 25, 22, 3, tzinfo=timezone.utc)  # UTC+1 en hiver
    assert d[2] == datetime(2026, 7, 1, 7, 10, tzinfo=timezone.utc)  # UTC+2 en été


def test_periodes_coupees_par_une_pause():
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    p = bilan.periodes([t0, t0 + timedelta(minutes=20), t0 + timedelta(minutes=120)])
    assert len(p) == 2 and p[0][1] - p[0][0] == timedelta(minutes=20)


def test_reponse_question_choix_et_texte_libre():
    contenu = 'The user answered: "Q1 ?"="A. Oui", "Q2 ?"="ni l\'un ni l\'autre". Read the answers.'
    assert bilan._reponses_question(contenu, {"A. Oui", "B. Non"}) == (1, len("ni l'un ni l'autre"))


def test_analyser_transcription(tmp_path):
    f = tmp_path / "s.jsonl"
    humain = {"kind": "human"}
    _ecrire(f, [
        {"type": "user", "timestamp": _t(0), "origin": humain, "promptSource": "typed",
         "message": {"content": "abcde"}},
        {"type": "assistant", "timestamp": _t(10), "message": {"content": [
            {"type": "tool_use", "id": "q1", "name": "AskUserQuestion",
             "input": {"questions": [{"options": [{"label": "A"}, {"label": "B"}]}]}}]}},
        {"type": "user", "timestamp": _t(14), "message": {"content": [
            {"type": "tool_result", "tool_use_id": "q1", "content": 'answered: "Q"="A".'}]}},
        {"type": "assistant", "timestamp": _t(20), "message": {"content": [{"type": "text", "text": "ok"}]}},
        # 25 min plus tard : compté ; puis une demande 3 h après : hors temps de réponse.
        {"type": "user", "timestamp": _t(45), "origin": humain, "promptSource": "typed",
         "message": {"content": [{"type": "text", "text": "xyz"}]}},
        {"type": "assistant", "timestamp": _t(50), "message": {"content": []}},
        {"type": "user", "timestamp": _t(230), "origin": humain, "promptSource": "typed",
         "message": {"content": "1234"}},
        {"type": "assistant", "timestamp": _t(231), "message": {
            "id": "m1", "model": "claude-opus-5-5", "content": [],
            "usage": {"output_tokens": 10, "output_tokens_details": {"thinking_tokens": 4}}}},
        {"type": "user", "timestamp": _t(232), "origin": humain, "promptSource": "typed",
         "message": {"content": "/clear"}},
        {"type": "cost-state", "totalAPIDuration": 600000, "totalToolDuration": 120000,
         "totalCostUSD": 1.234, "modelUsage": {"claude-opus-5-5": {"outputTokens": 10},
                                               "fournisseur-x:compte-123": {"outputTokens": 1}}},
    ])
    a = bilan.analyser_transcription(f)
    assert a["messages_auteur"] == 3
    assert a["signes_auteur"] == 5 + 3 + 4
    assert a["choix_auteur"] == 1
    assert a["reponse_auteur_min"] == 4 + 25  # question (4 min) + demande après 25 min
    assert a["actif_min"] == 52  # 0 → 50, puis 230 → 232
    assert a["calcul_modeles_min"] == 10 and a["commandes_min"] == 2
    assert a["jetons"]["opus"]["produits"] == 10 and a["cout_api_usd"] == 1.23
    assert "autre" in a["jetons"] and not any("compte" in k for k in a["jetons"])
    assert a["incomplet"] is False


def test_recoupement_releve_transcriptions():
    bilan.verifier_recoupement({"opus": {"produits": 1000}}, {"opus": {"produits": 990}}, "x")
    try:
        bilan.verifier_recoupement({"opus": {"produits": 2000}}, {"opus": {"produits": 1000}}, "x")
    except SystemExit as e:
        assert "divergent" in str(e)
    else:
        raise AssertionError("un relevé cumulé sur deux conversations doit arrêter le relevé")


def test_session_en_cours_jetons_des_transcriptions(tmp_path):
    f = tmp_path / "s.jsonl"
    _ecrire(f, [
        {"type": "user", "timestamp": _t(0), "origin": {"kind": "human"},
         "promptSource": "typed", "message": {"content": "go"}},
        {"type": "assistant", "timestamp": _t(1), "message": {
            "id": "m1", "model": "claude-opus-5-5", "content": [], "usage": {"output_tokens": 7}}},
        {"type": "assistant", "timestamp": _t(1), "message": {
            "id": "m1", "model": "claude-opus-5-5", "content": [], "usage": {"output_tokens": 7}}},
    ])
    a = bilan.analyser_transcription(f)
    assert a["incomplet"] is True and a["cout_api_usd"] is None
    assert a["jetons"]["opus"]["produits"] == 7  # une réponse en deux lignes compte une fois


def test_choix_multiples():
    assert bilan._reponses_question('"Q"="A, B".', {"A", "B"}) == (1, 0)


def test_aucun_chemin_ni_texte_exporte(tmp_path):
    racine = tmp_path / "depot"
    (racine / "making-of").mkdir(parents=True)
    (racine / "making-of/JOURNAL.md").write_text(
        "## Session 1 — 2026-01-01, à partir de 10 h 00 · x\n", encoding="utf-8")
    import subprocess
    subprocess.run(["git", "init", "-q"], cwd=racine, check=True)
    subprocess.run(["git", "add", "."], cwd=racine, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"],
                   cwd=racine, check=True)
    tr = tmp_path / "tr"
    tr.mkdir()
    _ecrire(tr / "s.jsonl", [{"type": "user", "timestamp": _t(0), "origin": {"kind": "human"},
                              "promptSource": "typed", "message": {"content": "SECRET-TEXTE"}}])
    bilan.bilan(racine, racine / "making-of/en-bref.json", tr)
    sortie = (racine / "making-of/en-bref.json").read_text(encoding="utf-8")
    assert "SECRET-TEXTE" not in sortie and str(tmp_path) not in sortie
    assert json.loads(sortie)["total"]["messages_auteur"] == 1


def test_rattachement_derniere_session_commencee(tmp_path):
    racine = tmp_path / "depot"
    (racine / "making-of").mkdir(parents=True)
    # 9 h 00 UTC = 10 h Paris (hiver). Session 2 à 13 h Paris ; transcription ouverte à 12 h 30
    # Paris : plus proche de la session 2, mais commencée avant elle (au-delà de la tolérance de
    # 15 min) → session 1.
    (racine / "making-of/JOURNAL.md").write_text(
        "## Session 1 — 2026-01-01, à partir de 10 h 05 · a\n"
        "## Session 2 — 2026-01-01, à partir de 13 h 00 · b\n", encoding="utf-8")
    import subprocess
    subprocess.run(["git", "init", "-q"], cwd=racine, check=True)
    subprocess.run(["git", "add", "."], cwd=racine, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"],
                   cwd=racine, check=True)
    tr = tmp_path / "tr"
    tr.mkdir()
    h = {"origin": {"kind": "human"}, "promptSource": "typed", "message": {"content": "x"}}
    _ecrire(tr / "a.jsonl", [{"type": "user", "timestamp": _t(0), **h}])      # 10 h 00 (tolérance)
    _ecrire(tr / "b.jsonl", [{"type": "user", "timestamp": _t(150), **h}])    # 12 h 30
    _ecrire(tr / "c.jsonl", [{"type": "user", "timestamp": _t(185), **h}])    # 13 h 05
    res = bilan.bilan(racine, racine / "making-of/en-bref.json", tr)
    assert [(s["numero"], s["messages_auteur"]) for s in res["sessions"]] == [(1, 2), (2, 1)]
    assert "debut" not in res["sessions"][0] and res["sessions"][0]["date"] == "2026-01-01"
