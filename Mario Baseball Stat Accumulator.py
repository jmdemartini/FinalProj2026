from pathlib import Path
import json
import csv

profile = input("What is the player's username?")
opponent = input("What is the opponent's username?")

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

MIN_AB = 20
MIN_OUTS = 30


# find files that are readable
for file in stat_folder.iterdir():
    filename = file.name
    if profile.lower() in filename.lower() and "decode" in filename.lower():
        matchingfiles.append(file)

for file in matchingfiles:
    with open(file, "r") as f:
        
        data = json.load(f)

        home_player = data["Home Player"]
        away_player = data["Away Player"]

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

            # initialize character FIRST
            if character not in character_totals:
                character_totals[character] = {
                    "batting": {},
                    "pitching": {},
                    "defense": {
                        "outs_by_position": {},
                        "total_outs": 0,
                        "batter_outs_by_position":{},
                       
                    }
                }

            # ---------------- DEFENSE ----------------
            outs_list = def_stats.get("Outs Per Position", [])
            

            for entry in outs_list:
                for pos, value in entry.items():
                    character_totals[character]["defense"]["outs_by_position"].setdefault(pos, 0)
                    character_totals[character]["defense"]["outs_by_position"][pos] += value
                    character_totals[character]["defense"]["total_outs"] += value
          
                    

            # ---------------- BATTING ----------------
            for stat_name, value in off.items():
                character_totals[character]["batting"].setdefault(stat_name, 0)
                character_totals[character]["batting"][stat_name] += value

            # ---------------- PITCHING ----------------
            for stat_name, value in def_stats.items():
                if isinstance(value, (int, float)):
                    character_totals[character]["pitching"].setdefault(stat_name, 0)
                    character_totals[character]["pitching"][stat_name] += value


#leader list prep
leaders = {
    "AVG": [], "OBP": [], "SLG": [], "OPS": [],
    "ERA": [], "WHIP": [],
    "H": [], "HR": [], "RBI": [], "AB": [],
    "K": [], "IP": [], "K/9":[]
}

with open("mario_stats_sheet.csv", "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow(["PLAYER STATS"])
    writer.writerow([
        "Character","GP","PA","AB","H","BB","HR","RBI",
        "AVG","OBP","SLG","OPS","Pitching",
        "ERA","WHIP","K", "IP", "K/9", "Defensive", "Big Plays", "ORF"
    ])

    for character, data in character_totals.items():
        bat = data["batting"]
        pit = data["pitching"]
        defense = data["defense"]
        batter_outs=defense.get("batter_total_outs", 0)

        # Batting
        AB = bat.get("At Bats", 0)
        H = bat.get("Hits", 0)
        BB = bat.get("Walks (4 Balls)", 0) + bat.get("Walks(Hit)", 0)
        singles = bat.get("Singles", 0)
        doubles = bat.get("Doubles", 0)
        triples = bat.get("Triples", 0)
        HR = bat.get("Homeruns", 0)

        TB = singles + 2*doubles + 3*triples + 4*HR

        AVG = H / AB if AB > 0 else 0
        OBP = (H + BB) / (AB + BB) if (AB + BB) > 0 else 0
        SLG = TB / AB if AB > 0 else 0
        OPS = OBP + SLG
        PA = AB + BB

        # Pitching
        ER = pit.get("Earned Runs", 0)
        outs = pit.get("Outs Pitched", 0)
        hits_allowed = pit.get("Hits Allowed", 0)
        walks = pit.get("Batters Walked", 0)
        K = pit.get("Strikeouts", 0)

        ERA = (ER * 27 / outs) if outs > 0 else 0
        WHIP = ((walks + hits_allowed) / (outs / 3)) if outs > 0 else 0
        INNINGS = outs//3 + .1*(outs%3) if outs > 0 else 0
        Kper9 = round(K/outs*27, 1) if outs > 0 else 0
        GP=batter_outs//27

        # Defensive
        BigPlays = pit.get("Big Plays",0)
        ORF = defense.get("total_outs", 0)
        

        writer.writerow([
            character, GP, PA,AB, H, BB, HR, bat.get("RBI", 0),
            round(AVG,3), round(OBP,3), round(SLG,3), round(OPS,3)," ",
            round(ERA,2), round(WHIP,2), K, INNINGS, Kper9,
            " ", BigPlays, ORF
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
            leaders["K/9"].append((character,Kper9))

        leaders["H"].append((character, H))
        leaders["HR"].append((character, HR))
        leaders["RBI"].append((character, bat.get("RBI", 0)))
        leaders["AB"].append((character, AB))
        leaders["K"].append((character, K))
        leaders["IP"].append((character, outs//3 + outs%3*.1))


    writer.writerow([])
    writer.writerow([])
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
    write_section("K/9", True)

    writer.writerow([])
    writer.writerow([])
    writer.writerow(["COUNTING LEADERS"])

    write_section("H", True)
    write_section("HR", True)
    write_section("RBI", True)
    write_section("AB", True)
    write_section("K", True)
    write_section("IP", True)

print("Created: mario_stats_sheet.csv")
