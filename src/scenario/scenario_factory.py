import random
from scenario import Scenario, ScenarioGenerator
from models.threat_collection import SHA
from models.asset_collection import HQ, OilRefinery
from models.weapon_collection import Patriot, Strela

def build_odesa_scenario() -> Scenario:

    sw_corner = (46.462295, 30.701044)
    ne_corner = (46.540112, 30.815411)

    scenario = Scenario(name="Odesa Example", sw_anchor=sw_corner, ne_anchor=ne_corner)
    generator = ScenarioGenerator(420)

    weapons = [
        #Patriot(name="Patriot-1", lat=46.505617, lon=30.687550),
        #Patriot(name="Patriot-2", lat=46.517232, lon=30.701957),
        #Patriot(name="Patriot-3", lat=46.481211, lon=30.703945),
        Strela(name="Strela-1", lat=46.491785, lon=30.761451),
        Strela(name="Strela-2", lat=46.472910, lon=30.762022)
    ]

    #city_1 = generator.generate_asset_cluster(46.495942, 30.682611, 500.0, 5, HQ)
    city_2 = generator.generate_asset_cluster(46.479917, 30.755191, 300.0, 2, HQ)
    #refinery_1 = generator.generate_asset_cluster(46.496107, 30.733333, 200.0, 3, OilRefinery)
    refinery_2 = generator.generate_asset_cluster(46.487460, 30.757546, 300.0, 3, OilRefinery)

    #threats_1 = generator.generate_threat_cluster(46.508980, 30.778131, 600.0, 10, SHA, refinery_1)
    threats_2 = generator.generate_threat_cluster(46.508242, 30.751695, 600.0, 10, SHA, refinery_2)
    #threats_3 = generator.generate_threat_cluster(46.517800, 30.743780, 600.0, 10, SHA, city_1)
    threats_4 = generator.generate_threat_cluster(46.479742, 30.775740, 600.0, 10, SHA, city_2)

    scenario.add_assets(*city_2, *refinery_2)
    scenario.add_threats(*threats_2, *threats_4)
    scenario.add_weapons(*weapons)

    return scenario


def build_parametric_scenario(target_drones: int, ammo_ratio: float, distribution: str, seed: int = 420) -> Scenario:
    """
    Builds a scenario dynamically based on  parameters,
    strictly utilizing cluster-to-cluster API.
    """
    random.seed(seed)

    scenario = Scenario(
        name=f"Parametric_T{target_drones}_R{ammo_ratio}_{distribution}",
        sw_anchor=(46.380000, 30.600000),  # Your updated, wider SW anchor
        ne_anchor=(46.570000, 30.900000)  # Your updated, wider NE anchor
    )

    generator = ScenarioGenerator(seed)

    # 1. Spawn Assets as Distinct Clusters
    asset_clusters = []

    if distribution == "Concentrated":
        # Cluster 0 & 1: Massive high-value hotspots (The 20% that will get 80% of the fire)
        c0 = generator.generate_asset_cluster(46.48, 30.75, 500.0, 4, OilRefinery)
        c1 = generator.generate_asset_cluster(46.50, 30.70, 500.0, 4, HQ)
        # Cluster 2: A large spread of low-value perimeter targets
        c2 = generator.generate_asset_cluster(46.45, 30.80, 2000.0, 12, HQ)

        asset_clusters.extend([c0, c1, c2])
    else:
        # Uniform: 4 distinct clusters of 5 assets spread evenly around the map
        c0 = generator.generate_asset_cluster(46.47, 30.75, 1000.0, 5, HQ)
        c1 = generator.generate_asset_cluster(46.42, 30.70, 1000.0, 5, HQ)
        c2 = generator.generate_asset_cluster(46.52, 30.80, 1000.0, 5, HQ)
        c3 = generator.generate_asset_cluster(46.45, 30.68, 1000.0, 5, HQ)

        asset_clusters.extend([c0, c1, c2, c3])

    # Unpack all clusters and add them to the scenario
    for cluster in asset_clusters:
        scenario.add_assets(*cluster)

    # 2. Spawn Weapons to perfectly match the ammo_ratio (rho)
    target_capacity = int(target_drones * ammo_ratio)
    weapons = []
    current_capacity = 0

    while current_capacity < target_capacity:
        lat, lon = 46.47 + random.uniform(-0.05, 0.05), 30.75 + random.uniform(-0.05, 0.05)
        if random.random() < 0.40:
            w = Patriot(lat=lat, lon=lon, name=f"Patriot-{len(weapons)}")
        else:
            w = Strela(lat=lat, lon=lon, name=f"Strela-{len(weapons)}")
        weapons.append(w)
        current_capacity += w.capacity

    scenario.add_weapons(*weapons)

    # 3. Spawn Threats (Using the Cluster-to-Cluster API)
    threats = []
    drones_spawned = 0

    while drones_spawned < target_drones:
        cluster_size = min(random.randint(5, 15), target_drones - drones_spawned)

        # Target selection math
        if distribution == "Concentrated":
            # 80% chance to attack c0 or c1 (The hotspots). 20% chance to attack c2 (Perimeter)
            target_cluster = random.choices(asset_clusters, weights=[40, 40, 20], k=1)[0]
        else:
            # Uniform chance to attack any of the 4 clusters
            target_cluster = random.choice(asset_clusters)

        spawn_lat = random.choice([46.40, 46.55])
        spawn_lon = random.choice([30.65, 30.85])

        # Pass the ENTIRE target_cluster to your API, just like in Odesa!
        t_cluster = generator.generate_threat_cluster(spawn_lat, spawn_lon, 500.0, cluster_size, SHA, target_cluster)

        threats.extend(t_cluster)
        drones_spawned += cluster_size

    scenario.add_threats(*threats)
    return scenario
