from log import log


class Observer:
    """Class to watch and store data of any new fleet event occuring"""

    def __init__(self, planet_list, nav):
        """Init the observer with the list of every planet"""
        self.list_event = []
        self.nav = nav
        self.list_coord = [planet.planet_coord for planet in planet_list]
        self.mission = {
            1: "attack",
            2: "",
            3: "transport",
            4: "station",
            5: "",
            6: "",
            7: "colonize",
            8: "recycle",
            9: "",
            10: "",
            11: "",
            12: "",
            13: "",
            14: "",
            15: "explore",
        }

    def is_in(self, new_event, list_event):
        """Check if a given event is in a given event list"""
        for event in list_event:
            if (
                new_event["origin_planet_coord"] == event["origin_planet_coord"]
                and new_event["destination_planet_coord"]
                == event["destination_planet_coord"]
                and new_event["arrival_time"] == event["arrival_time"]
                and new_event["mission_type"] == event["mission_type"]
                and new_event["detail_fleet"] == event["detail_fleet"]
            ):
                return False
        return True

    def is_my_fleet(self, event):
        """Check if the fleet is mine"""
        for coord in self.list_coord:
            if event["origin_planet_coord"] == coord:
                return True
        return False

    def is_under_attack(self, event):
        """Check if it is an attack comming from an enemy"""
        return event["mission_type"] == 1 and not self.is_my_fleet(event)

    def check_new_event(self):
        """Watch the fleet list for any new event, to notify attacks and to check if any event is over"""
        new_event_list = self.nav.get_fleet_events()
        for new_event in new_event_list:
            if self.is_in(new_event, self.list_event):
                self.list_event.append(new_event)
                if not self.is_my_fleet(new_event):
                    log(
                        "{} ship(s) from ({}, {}) to ({}, {}) arriving in {} at {} to {}".format(
                            new_event["detail_fleet"],
                            new_event["origin_planet_name"],
                            new_event["origin_planet_coord"],
                            new_event["destination_planet_name"],
                            new_event["destination_planet_coord"],
                            new_event["remaining_time"],
                            new_event["arrival_time"],
                            self.mission[new_event["mission_type"]],
                        )
                    )
                if self.is_under_attack(new_event):
                    self.nav.send_message_enemy(new_event["player_id"])

        is_event_over = False
        for old_event in self.list_event:
            if self.is_in(old_event, new_event_list):
                self.list_event.remove(old_event)
                is_event_over = True
        return is_event_over
