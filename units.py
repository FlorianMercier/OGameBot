"""Create your build order for each planet here"""
# Buildings have to be written in the same language as your server

planet1 = [
    # 'Centrale électrique solaire',
    # 'Mine de métal',
    # 'Mine de cristal'
]
planet2 = [
    # 'Centrale électrique solaire',
    # 'Mine de métal',
    # 'Mine de cristal'
]
planet3 = [
    # 'Centrale électrique solaire',
    # 'Mine de métal',
    # 'Mine de cristal'
]
planet4 = [
    # 'Centrale électrique solaire',
    # 'Mine de métal',
    # 'Mine de cristal'
]
planet5 = [
    # 'Centrale électrique solaire',
    # 'Mine de métal',
    # 'Mine de cristal'
]
planet6 = [
    # 'Centrale électrique solaire',
    # 'Mine de métal',
    # 'Mine de cristal'
]

build_order = [planet1, planet2, planet3, planet4, planet5, planet6]

"""Create your fleet orders"""
# Units have to be written in the same language as your server

attack_fleet_1 = [
    # ('Petit transporteur', 5)
]
attack_fleet_2 = [
    # ('Grand transporteur', 1)
]
explore_fleet_1 = [
    # ('Grand transporteur', 30),
    # ('Petit transporteur', 30),
    # ('Éclaireur', 1),
    # ('Sonde d`espionnage', 1)
]
explore_fleet_2 = [
    # ('Éclaireur', 1),
    # ('Grand transporteur', 999)
]

# 'coordinates':(galaxy, system, position, origin_type, destination_type)
fleet1 = {
    "origin_planet": 0,
    "mission": 1,
    "coordinates": (1, 100, 4, 1, 1),
    "list_ships": attack_fleet_1,
}
fleet2 = {
    "origin_planet": 0,
    "mission": 1,
    "coordinates": (1, 100, 5, 1, 1),
    "list_ships": attack_fleet_1,
}
fleet3 = {
    "origin_planet": 0,
    "mission": 1,
    "coordinates": (1, 100, 6, 1, 1),
    "list_ships": attack_fleet_1,
}
fleet4 = {
    "origin_planet": 1,
    "mission": 1,
    "coordinates": (1, 101, 4, 1, 1),
    "list_ships": attack_fleet_2,
}
fleet5 = {
    "origin_planet": 1,
    "mission": 1,
    "coordinates": (1, 101, 5, 1, 1),
    "list_ships": attack_fleet_2,
}
explo1 = {
    "origin_planet": 0,
    "mission": 15,
    "coordinates": (1, 100, 16, 1, 1),
    "list_ships": explore_fleet_1,
}
explo2 = {
    "origin_planet": 1,
    "mission": 15,
    "coordinates": (1, 101, 16, 1, 1),
    "list_ships": explore_fleet_2,
}
ghost1 = {
    "origin_planet": 0,
    "mission": 1,
    "coordinates": (1, 100, 7, 1, 1),
    "list_ships": [],
}
ghost2 = {
    "origin_planet": 1,
    "mission": 1,
    "coordinates": (1, 100, 8, 1, 1),
    "list_ships": [],
}

# Main fleet list
fleet_order = [fleet1, fleet2, fleet3, fleet4, fleet5, explo1, explo2]
# Ghosting fleet list
ghost_order = [ghost1, ghost2]
