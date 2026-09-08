# -*- coding: utf-8 -*-
"""Generate the tracker web app (index.html) + seed standings.json.

Injects team metadata + parsed predictions into a static HTML template so the
prediction data is never hand-transcribed. Re-run after editing predictions.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PRED_JSON = os.path.join(ROOT, "Prediction", "predictions.json")

# ---- Team master data (canonical English name is the join key) ----
TEAMS = [
 {"id":"psg","en":"Paris Saint-Germain","ar":"باريس سان جيرمان","cEn":"France","cAr":"فرنسا","pot":1,"ab":"PSG","pat":"vband","c1":"#0B1E4B","c2":"#DA291C","tc":"#FFFFFF"},
 {"id":"bay","en":"Bayern München","ar":"بايرن ميونخ","cEn":"Germany","cAr":"ألمانيا","pot":1,"ab":"BAY","pat":"solid","c1":"#DC052D","c2":"#DC052D","tc":"#FFFFFF"},
 {"id":"rma","en":"Real Madrid","ar":"ريال مدريد","cEn":"Spain","cAr":"إسبانيا","pot":1,"ab":"RMA","pat":"solid","c1":"#F2F2F2","c2":"#F2F2F2","tc":"#00529F"},
 {"id":"liv","en":"Liverpool","ar":"ليفربول","cEn":"England","cAr":"إنجلترا","pot":1,"ab":"LIV","pat":"solid","c1":"#C8102E","c2":"#C8102E","tc":"#FFFFFF"},
 {"id":"int","en":"Inter Milan","ar":"إنتر ميلان","cEn":"Italy","cAr":"إيطاليا","pot":1,"ab":"INT","pat":"stripes","c1":"#0A2A5E","c2":"#0B0B0B","tc":"#FFFFFF"},
 {"id":"mci","en":"Manchester City","ar":"مانشستر سيتي","cEn":"England","cAr":"إنجلترا","pot":1,"ab":"MCI","pat":"solid","c1":"#6CABDD","c2":"#6CABDD","tc":"#12244A"},
 {"id":"ars","en":"Arsenal","ar":"أرسنال","cEn":"England","cAr":"إنجلترا","pot":1,"ab":"ARS","pat":"vband","c1":"#EF0107","c2":"#F2F2F2","tc":"#EF0107"},
 {"id":"bar","en":"Barcelona","ar":"برشلونة","cEn":"Spain","cAr":"إسبانيا","pot":1,"ab":"BAR","pat":"halves","c1":"#004D98","c2":"#A50044","tc":"#FFD700"},
 {"id":"atm","en":"Atlético de Madrid","ar":"أتلتيكو مدريد","cEn":"Spain","cAr":"إسبانيا","pot":1,"ab":"ATM","pat":"stripes","c1":"#F2F2F2","c2":"#CB3524","tc":"#12244A"},
 {"id":"bvb","en":"Borussia Dortmund","ar":"بوروسيا دورتموند","cEn":"Germany","cAr":"ألمانيا","pot":2,"ab":"BVB","pat":"solid","c1":"#FDE100","c2":"#FDE100","tc":"#0B0B0B"},
 {"id":"rom","en":"Roma","ar":"روما","cEn":"Italy","cAr":"إيطاليا","pot":2,"ab":"ROM","pat":"solid","c1":"#8E1F2F","c2":"#8E1F2F","tc":"#F0BC42"},
 {"id":"scp","en":"Sporting CP","ar":"سبورتينغ لشبونة","cEn":"Portugal","cAr":"البرتغال","pot":2,"ab":"SCP","pat":"hoop","c1":"#008057","c2":"#F2F2F2","tc":"#008057"},
 {"id":"avl","en":"Aston Villa","ar":"أستون فيلا","cEn":"England","cAr":"إنجلترا","pot":2,"ab":"AVL","pat":"vband","c1":"#670E36","c2":"#95BFE5","tc":"#670E36"},
 {"id":"por","en":"Porto","ar":"بورتو","cEn":"Portugal","cAr":"البرتغال","pot":2,"ab":"POR","pat":"stripes","c1":"#F2F2F2","c2":"#00428C","tc":"#00428C"},
 {"id":"mun","en":"Manchester United","ar":"مانشستر يونايتد","cEn":"England","cAr":"إنجلترا","pot":2,"ab":"MUN","pat":"solid","c1":"#DA291C","c2":"#DA291C","tc":"#FFE500"},
 {"id":"bru","en":"Club Brugge","ar":"كلوب بروج","cEn":"Belgium","cAr":"بلجيكا","pot":2,"ab":"BRU","pat":"stripes","c1":"#0A2A5E","c2":"#0B0B0B","tc":"#FFFFFF"},
 {"id":"bet","en":"Real Betis","ar":"ريال بيتيس","cEn":"Spain","cAr":"إسبانيا","pot":2,"ab":"BET","pat":"stripes","c1":"#F2F2F2","c2":"#00954C","tc":"#00954C"},
 {"id":"psv","en":"PSV Eindhoven","ar":"بي إس في أيندهوفن","cEn":"Netherlands","cAr":"هولندا","pot":2,"ab":"PSV","pat":"hoop","c1":"#F2F2F2","c2":"#ED1C24","tc":"#ED1C24"},
 {"id":"fey","en":"Feyenoord","ar":"فاينورد","cEn":"Netherlands","cAr":"هولندا","pot":3,"ab":"FEY","pat":"halves","c1":"#CE1B1F","c2":"#F2F2F2","tc":"#CE1B1F"},
 {"id":"lil","en":"Lille","ar":"ليل","cEn":"France","cAr":"فرنسا","pot":3,"ab":"LIL","pat":"hoop","c1":"#F2F2F2","c2":"#E01E13","tc":"#E01E13"},
 {"id":"nap","en":"Napoli","ar":"نابولي","cEn":"Italy","cAr":"إيطاليا","pot":3,"ab":"NAP","pat":"solid","c1":"#12A0D7","c2":"#12A0D7","tc":"#FFFFFF"},
 {"id":"rbl","en":"RB Leipzig","ar":"لايبزيغ","cEn":"Germany","cAr":"ألمانيا","pot":3,"ab":"RBL","pat":"solid","c1":"#F2F2F2","c2":"#F2F2F2","tc":"#DD0741"},
 {"id":"vil","en":"Villarreal","ar":"فياريال","cEn":"Spain","cAr":"إسبانيا","pot":3,"ab":"VIL","pat":"solid","c1":"#FFE667","c2":"#FFE667","tc":"#005187"},
 {"id":"shk","en":"Shakhtar Donetsk","ar":"شاختار دونيتسك","cEn":"Ukraine","cAr":"أوكرانيا","pot":3,"ab":"SHK","pat":"stripes","c1":"#FF6600","c2":"#0B0B0B","tc":"#FFFFFF"},
 {"id":"gal","en":"Galatasaray","ar":"غلطة سراي","cEn":"Türkiye","cAr":"تركيا","pot":3,"ab":"GAL","pat":"halves","c1":"#A90432","c2":"#FBB700","tc":"#FFFFFF"},
 {"id":"fen","en":"Fenerbahçe","ar":"فنربخشة","cEn":"Türkiye","cAr":"تركيا","pot":3,"ab":"FEN","pat":"stripes","c1":"#FFED00","c2":"#14264C","tc":"#14264C"},
 {"id":"bod","en":"Bodø/Glimt","ar":"بودو غليمت","cEn":"Norway","cAr":"النرويج","pot":3,"ab":"BOD","pat":"solid","c1":"#FFD500","c2":"#FFD500","tc":"#0B0B0B"},
 {"id":"vik","en":"Viking","ar":"فايكينغ","cEn":"Norway","cAr":"النرويج","pot":4,"ab":"VIK","pat":"solid","c1":"#003D7C","c2":"#003D7C","tc":"#FFFFFF"},
 {"id":"sla","en":"Slavia Praha","ar":"سلافيا براغ","cEn":"Czechia","cAr":"تشيكيا","pot":4,"ab":"SLA","pat":"halves","c1":"#D31126","c2":"#F2F2F2","tc":"#D31126"},
 {"id":"vfb","en":"VfB Stuttgart","ar":"شتوتغارت","cEn":"Germany","cAr":"ألمانيا","pot":4,"ab":"VFB","pat":"solid","c1":"#F2F2F2","c2":"#F2F2F2","tc":"#E32219"},
 {"id":"aek","en":"AEK Athens","ar":"أيك أثينا","cEn":"Greece","cAr":"اليونان","pot":4,"ab":"AEK","pat":"halves","c1":"#FFD400","c2":"#0B0B0B","tc":"#FFFFFF"},
 {"id":"lsk","en":"LASK","ar":"لاسك","cEn":"Austria","cAr":"النمسا","pot":4,"ab":"LSK","pat":"stripes","c1":"#0B0B0B","c2":"#F2F2F2","tc":"#FFFFFF"},
 {"id":"com","en":"Como","ar":"كومو","cEn":"Italy","cAr":"إيطاليا","pot":4,"ab":"COM","pat":"halves","c1":"#0A2C6E","c2":"#F2F2F2","tc":"#0A2C6E"},
 {"id":"len","en":"Lens","ar":"لانس","cEn":"France","cAr":"فرنسا","pot":4,"ab":"LEN","pat":"stripes","c1":"#FFCD00","c2":"#E30613","tc":"#0B0B0B"},
 {"id":"sab","en":"Sabah","ar":"صباح","cEn":"Azerbaijan","cAr":"أذربيجان","pot":4,"ab":"SAB","pat":"solid","c1":"#1B7A4B","c2":"#1B7A4B","tc":"#FFFFFF"},
 {"id":"slo","en":"Slovan Bratislava","ar":"سلوفان براتيسلافا","cEn":"Slovakia","cAr":"سلوفاكيا","pot":4,"ab":"SLO","pat":"halves","c1":"#F2F2F2","c2":"#1B458F","tc":"#1B458F"},
]

# ---- Load predictions ----
with open(PRED_JSON, encoding="utf-8") as f:
    pred = json.load(f)

# Sanity: every predicted team name must exist in TEAMS
names = {t["en"] for t in TEAMS}
for p in pred["players"]:
    for tn in p["ranking"]:
        if tn not in names:
            raise SystemExit("Unknown team in prediction: " + tn)
    if len(p["ranking"]) != 36:
        raise SystemExit("Player %s has %d teams" % (p["name"], len(p["ranking"])))
print("Predictions OK: %d players" % len(pred["players"]))

# ---- Seed standings.json (provisional: draw order, no matches played) ----
seed = {
    "season": "2026/27",
    "competition": "UEFA Champions League",
    "phase": "League phase",
    "matchday": 0,
    "last_updated": "2026-09-08T19:00:00+03:00",
    "source": "seed (provisional draw order — no matches played yet)",
    "standings": [
        {"rank": i + 1, "team": t["en"], "played": 0, "won": 0, "draw": 0,
         "lost": 0, "gf": 0, "ga": 0, "gd": 0, "points": 0}
        for i, t in enumerate(TEAMS)
    ],
}
standings_path = os.path.join(HERE, "standings.json")
with open(standings_path, "w", encoding="utf-8") as f:
    json.dump(seed, f, ensure_ascii=False, indent=2)
print("Wrote", standings_path)

# ---- Inject into template ----
tpl_path = os.path.join(HERE, "template.html")
with open(tpl_path, encoding="utf-8") as f:
    tpl = f.read()

tpl = tpl.replace("/*__TEAMS__*/", json.dumps(TEAMS, ensure_ascii=False))
tpl = tpl.replace("/*__PRED__*/", json.dumps(pred, ensure_ascii=False))
tpl = tpl.replace("/*__STANDINGS__*/", json.dumps(seed, ensure_ascii=False))

out_path = os.path.join(HERE, "index.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(tpl)
print("Wrote", out_path)
