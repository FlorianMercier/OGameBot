class Planet:
    """Class to store data of one planet and get functions to build"""

    def __init__(self, name, planet_info, nav):
        """Create plannet builder, get every level and amount of buildings, unit and research"""
        self.name = name
        self.planet_id = planet_info["id"]
        self.planet_coord = planet_info["coord"]
        self.nav = nav
        self.__build_list = self.nav.get_unit_dictionary(self.planet_id)

    def build(self, unit_name, amount=1):
        """Build the given unit and update planet data"""
        unit = self.__build_list[unit_name]
        self.__build_list.update(
            self.nav.get_unit_info(unit["component"], self.planet_id)
        )
        # Build the building or unit
        (updated, cooldown, message) = self.nav.upgrade_unit(
            self.planet_id, unit_name, unit, amount
        )
        return (updated, cooldown, message)
