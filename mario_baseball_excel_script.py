from pathlib import Path
import json
import csv

profile = input("What is the player's username?")
opponent=input("What is the opponent's username?")
stat_folder = (
    Path.home()
    / "Library"
    / "Application Support"
    / "Project Rio"
    / "StatFiles"
    / "MarioSuperstarBaseball"
)

matchingfiles = []
character_totals = {}

# -------- SETTINGS --------
MIN_AB = 50
MIN_OUTS = 30
# --------------------------

# -------- FIND FILES --------
for file in stat_folder.iterdir():
    filename = file.name
    if profile.lower() in filename.lower() and "decoded" in filename.lower():
        matchingfiles.append(file)

# -------- READ FILES --------
for file in matchingfiles:
    with open(file, "r") as f:
        data = json.load(f)

        home_player = data["Home Player"]
        away_player = data["Away Player"]

        # -------- FILTER: ONLY VS CPU --------
        if profile == home_player and away_player == opponent:
            profile_team = "1"
        elif profile == away_player and home_player == opponent:
            profile_team = "0"
        else:
            continue

        characters = data["Character Game Stats"]

        for _, player in characters.items():
            if player["Team"] != profile_team:
                continue

            character = player["CharID"]
            off = player["Offensive Stats"]
            def_stats = player["Defensive Stats"]

            if character not in character_totals:
                character_totals[character] = {
                    "batting": {},
                    "pitching": {}
                }

            # Batting totals
            for stat_name, value in off.items():
                character_totals[character]["batting"].setdefault(stat_name, 0)
                character_totals[character]["batting"][stat_name] += value

            # Pitching totals
            for stat_name, value in def_stats.items():
                if isinstance(value, (int, float)):
                    character_totals[character]["pitching"].setdefault(stat_name, 0)
                    character_totals[character]["pitching"][stat_name] += value

# -------- PREP LEADERS --------
leaders = {
    "AVG": [], "OBP": [], "SLG": [], "OPS": [],
    "ERA": [], "WHIP": [],
    "H": [], "HR": [], "RBI": [], "AB": [],
    "K": [], "IP_OUTS": []
}

# -------- OPEN CSV --------
with open("mario_stats.csv", "w", newline="") as f:
    writer = csv.writer(f)

    # ===== PLAYER STATS =====
    writer.writerow(["PLAYER STATS"])
    writer.writerow([
        "Character","AB","H","HR","RBI",
        "AVG","OBP","SLG","OPS",
        "Outs","ERA","WHIP","K"
    ])

    for character, data in character_totals.items():
        bat = data["batting"]
        pit = data["pitching"]

        # Batting
        AB = bat.get("At Bats", 0)
        H = bat.get("Hits", 0)
        BB = bat.get("Walks (4 Balls)", 0)
        singles = bat.get("Singles", 0)
        doubles = bat.get("Doubles", 0)
        triples = bat.get("Triples", 0)
        HR = bat.get("Homeruns", 0)

        TB = singles + 2*doubles + 3*triples + 4*HR

        AVG = H / AB if AB > 0 else 0
        OBP = (H + BB) / (AB + BB) if (AB + BB) > 0 else 0
        SLG = TB / AB if AB > 0 else 0
        OPS = OBP + SLG

        # Pitching
        ER = pit.get("Earned Runs", 0)
        outs = pit.get("Outs Pitched", 0)
        hits_allowed = pit.get("Hits Allowed", 0)
        walks = pit.get("Batters Walked", 0)
        K = pit.get("Strikeouts", 0)

        ERA = (ER * 27 / outs) if outs > 0 else 0
        WHIP = ((walks + hits_allowed) / (outs / 3)) if outs > 0 else 0

        writer.writerow([
            character, AB, H, HR, bat.get("RBI", 0),
            round(AVG,3), round(OBP,3), round(SLG,3), round(OPS,3),
            outs, round(ERA,2), round(WHIP,2), K
        ])

        # Leaders
        if AB >= MIN_AB:
            leaders["AVG"].append((character, AVG))
            leaders["OBP"].append((character, OBP))
            leaders["SLG"].append((character, SLG))
            leaders["OPS"].append((character, OPS))

        if outs >= MIN_OUTS:
            leaders["ERA"].append((character, ERA))
            leaders["WHIP"].append((character, WHIP))

        leaders["H"].append((character, H))
        leaders["HR"].append((character, HR))
        leaders["RBI"].append((character, bat.get("RBI", 0)))
        leaders["AB"].append((character, AB))
        leaders["K"].append((character, K))
        leaders["IP_OUTS"].append((character, outs))

    # spacing
    writer.writerow([])
    writer.writerow([])

    # ===== RATE LEADERS =====
    writer.writerow(["RATE LEADERS"])

    def write_section(stat, reverse=True):
        writer.writerow([stat])
        sorted_list = sorted(leaders[stat], key=lambda x: x[1], reverse=reverse)
        for char, val in sorted_list[:10]:
            writer.writerow([char, round(val,3) if isinstance(val, float) else val])
        writer.writerow([])

    write_section("AVG", True)
    write_section("OBP", True)
    write_section("SLG", True)
    write_section("OPS", True)
    write_section("ERA", False)
    write_section("WHIP", False)

    writer.writerow([])
    writer.writerow([])

    # ===== COUNTING LEADERS =====
    writer.writerow(["COUNTING LEADERS"])

    write_section("H", True)
    write_section("HR", True)
    write_section("RBI", True)
    write_section("AB", True)
    write_section("K", True)
    write_section("IP_OUTS", True)

print("Created: mario_stats.csv")
