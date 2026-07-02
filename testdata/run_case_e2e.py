"""E2E: 5 echte Kundenfälle durch die Plattform spielen (Lead -> Upload -> KI-Screening)."""
import requests, json, sys, time, pathlib

API = "https://live-demo-fix.preview.emergentagent.com"
DATA = pathlib.Path("/app/testdata")

CASES = [
    {"n": 1, "name": "Fall Eins Dzhuma", "email": "fall1.test@stk-aachen.de", "country": "Indien", "course": "G-Kurs", "lang": "A2",
     "docs": [("Fall_1/Dzhuma_Pass.pdf", "passport"), ("Fall_1/HZB_Schule.pdf", "school_certificate"),
              ("Fall_1/HZB_Uni.pdf", "university_certificate"), ("Fall_1/telc_C1_Hochschule.pdf", "language_certificate")]},
    {"n": 2, "name": "Fall Zwei Indien", "email": "fall2.test@stk-aachen.de", "country": "Indien", "course": "T-Kurs", "lang": None,
     "docs": [("Fall_2/dokument_1.jpeg", "other"), ("Fall_2/image.jpg", "other")]},
    {"n": 3, "name": "Fall Drei Ukraine", "email": "fall3.test@stk-aachen.de", "country": "Ukraine", "course": "G-Kurs", "lang": "B2",
     "docs": [("Fall_3/Passport_Front_Back.pdf", "passport"), ("Fall_3/12th_Grade_Marks.pdf", "school_certificate"),
              ("Fall_3/APS_Certificate.pdf", "aps_certificate"), ("Fall_3/TELC_B2.pdf", "language_certificate")]},
    {"n": 4, "name": "Fall Vier Marokko", "email": "fall4.test@stk-aachen.de", "country": "Marokko", "course": "M-Kurs", "lang": None,
     "docs": [("Fall_4/1000252644.jpg", "other"), ("Fall_4/1000252645.jpg", "other"), ("Fall_4/1000252647.jpg", "other"),
              ("Fall_4/1000252721.jpg", "other"), ("Fall_4/1000253143.jpg", "other")]},
    {"n": 5, "name": "Fall Fuenf Indonesien", "email": "fall5.test@stk-aachen.de", "country": "Indonesien", "course": "T-Kurs", "lang": None,
     "docs": [("Fall_5/paspor.pdf", "passport"), ("Fall_5/skl_navinuel.pdf", "school_certificate"),
              ("Fall_5/Zertifikate_digital.pdf", "language_certificate")]},
]

def staff_session():
    s = requests.Session()
    r = s.post(f"{API}/api/auth/login", json={"email": "staff@studienkolleg-aachen.de", "password": "DevSeed@2026!"})
    r.raise_for_status()
    s.headers["X-CSRF-Token"] = s.cookies.get("csrf_token", "")
    return s

def main():
    s = staff_session()
    results = []
    for c in CASES:
        print(f"\n===== FALL {c['n']} ({c['country']}, {c['course']}) =====")
        r = requests.post(f"{API}/api/leads/ingest", json={
            "full_name": c["name"], "email": c["email"], "country": c["country"],
            "area_interest": "studienkolleg", "course_type": c["course"],
            "degree_country": c["country"], "language_level": c["lang"],
            "source": "e2e_case_test", "notes": f"Testfall {c['n']} aus Kundenunterlagen",
        })
        print("lead ingest:", r.status_code, r.text[:200])
        if r.status_code != 200:
            results.append((c["n"], "LEAD_FAIL", r.status_code)); continue
        app_id = r.json().get("application_id")
        if not app_id:
            # Duplikat: App suchen
            apps = s.get(f"{API}/api/applications", params={"search": c["email"]}).json()
            items = apps if isinstance(apps, list) else apps.get("items", [])
            app_id = items[0]["id"] if items else None
        print("application_id:", app_id)
        if not app_id:
            results.append((c["n"], "NO_APP", None)); continue

        up_ok, up_fail = 0, 0
        for rel, dtype in c["docs"]:
            p = DATA / rel
            with open(p, "rb") as fh:
                ct = "application/pdf" if p.suffix == ".pdf" else "image/jpeg"
                r2 = s.post(f"{API}/api/applications/{app_id}/documents/upload",
                            files={"file": (p.name, fh, ct)}, data={"doc_type": dtype}, timeout=120)
            ok = r2.status_code == 200
            up_ok += ok; up_fail += (not ok)
            print(f"  upload {p.name} [{dtype}]: {r2.status_code}" + ("" if ok else f" -> {r2.text[:200]}"))

        t0 = time.time()
        r3 = s.post(f"{API}/api/applications/{app_id}/ai-screen", timeout=300)
        dt = time.time() - t0
        if r3.status_code == 200:
            j = r3.json()
            print(f"  KI-Screening OK ({dt:.0f}s): complete={j.get('is_complete')} stage={j.get('suggested_stage')} "
                  f"anabin={j.get('anabin_category')} provider={j.get('ai_provider')}")
            summ = (j.get("summary") or j.get("report") or "")
            print("  Summary:", str(summ)[:300])
            results.append((c["n"], "OK", {"uploads": f"{up_ok}/{up_ok+up_fail}", "stage": j.get("suggested_stage"),
                                            "complete": j.get("is_complete"), "app_id": app_id, "secs": round(dt)}))
        else:
            print(f"  KI-Screening FAIL {r3.status_code}: {r3.text[:300]}")
            results.append((c["n"], "SCREEN_FAIL", r3.status_code))
        time.sleep(3)

    print("\n===== ERGEBNIS =====")
    for r in results:
        print(r)

if __name__ == "__main__":
    main()
