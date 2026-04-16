from models import Asset, Threat, Weapon

if __name__ == '__main__':
    hq_1 = Asset(name="HQ-1", x=10.5, y=20.0, value=500_000)
    hq_2 = Asset(name="HQ-2", x=12.5, y=17.5, value=600_000)

    drone_1 = Threat(name="SHA-136-1", x=100.0, y=150.0, target=hq_1)
    drone_2 = Threat(name="SHA-136-2", x=115.0, y=130.0, target=hq_2)

    patriot = Weapon(name="MIM-104-1", x=0.0, y=0.0)

    print(f"[{drone_1.get_name()}] is targeting [{drone_1.target.get_name()}] worth {drone_1.target.get_value()}$")
    print(f"[{drone_2.get_name()}] is targeting [{drone_2.target.get_name()}] worth {drone_2.target.get_value()}$")
