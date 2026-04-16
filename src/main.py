from models import Asset, Threat, Weapon, Scenario

if __name__ == '__main__':
    # === INITIALIZE SCENARIO ===
    scenario = Scenario(name="Example Scenario", width=450.0, height=200.0)

    # === CREATE ENTITIES ===
    hq_1 = Asset(name="HQ-1", x=10.5, y=20.0, value=500_000)
    hq_2 = Asset(name="HQ-2", x=12.5, y=17.5, value=600_000)

    drone_1 = Threat(name="SHA-136-1", x=100.0, y=150.0, target=hq_1)
    drone_2 = Threat(name="SHA-136-2", x=115.0, y=130.0, target=hq_2)

    patriot = Weapon(name="MIM-104-1", x=0.0, y=0.0)

    # === PACK ENTITIES INTO SCENARIO ===
    scenario.add_assets(hq_1, hq_2)
    scenario.add_threats(drone_1, drone_2)
    scenario.add_weapons(patriot)

    # === PRINT SCENARIO DETAILS ===
    print(scenario.details())

    # === PRINT ALL THE THREATS AND THEIR TARGETS ===
    for d in scenario.get_threats():
        print(f"[{d.get_name()}] is targeting [{d.get_target().get_name()}] worth {d.get_target().get_value()}$")
