from navigate import Nav
from planet import Planet
from observer import Observer
import time
from log import log
from date import Date
import units
from threading import Thread, Lock


class Manager:
    """Class to create and manage the different threads controlling the account"""

    # Class Parameters
    DELAY = 300
    ERROR_DELAY = 10

    def __init__(self, login):
        """Init account manager, loggin, parse empire"""
        # Create Selenium WebDriver
        self.navigate = Nav(login)
        # Connect to given account
        try:
            self.navigate.connect_to_account()
            log("OGameBot Logged in")
        except Exception as exc:
            log(exc)
        self.planet_list = self.get_planet_list()
        # Get build orders and fleet orders
        self.all_build_orders = units.build_order
        self.all_fleet_orders = units.fleet_order
        self.all_ghost_order = units.ghost_order
        # Init mutex and threads list
        self.mutex = Lock()
        self.thread_pool = list()
        # INIT TIME EVENT VARIABLES
        self.time_to_start_ghost = Date([23, 0, 0])
        self.time_to_end_ghost = Date([8, 0, 0]).get_next_day()
        # Init the building thread for each planet
        for planet, build_order in zip(self.planet_list, self.all_build_orders):
            self.thread_pool.append(
                Thread(target=self.build, args=(planet, build_order))
            )
        # Init the watcher thread
        self.thread_pool.append(
            Thread(target=self.check_new_event, args=(self.planet_list,))
        )
        # Init the farming and exploring thread
        self.thread_pool.append(
            Thread(target=self.send_fleet, args=(self.all_fleet_orders,))
        )
        # Init the event boolean
        self.is_event_over = False

    def start(self):
        """Run the thread, start building, watching for attacks and sending fleet"""
        for thread in self.thread_pool:
            thread.start()
        for thread in self.thread_pool:
            thread.join()

    def get_planet_list(self):
        """Create and store a planet builder for each planet of the empire"""
        planet_list = list()
        planet_dictionary = self.navigate.get_planet_dictionary()
        for planet_name, planet_info in planet_dictionary.items():
            planet_list.append(Planet(planet_name, planet_info, self.navigate))
        return planet_list

    def wait_countdown_or_event(self, countdown):
        self.is_event_over = False
        ending_time = time.time() + countdown
        is_waiting = True
        while is_waiting:
            if self.is_event_over or time.time() > ending_time:
                is_waiting = False
                self.is_event_over = False
            else:
                time.sleep(1)

    def build(self, planet, build_order):
        """Build every unit of the given list for the given planet"""
        for unit in build_order:
            updated = False
            countdown = 0
            while not updated:
                try:
                    self.mutex.acquire()
                    (updated, countdown, message) = planet.build(unit)
                    self.mutex.release()
                    log(unit + message)
                    if not updated:
                        self.wait_countdown_or_event(countdown)
                except Exception:
                    self.mutex.release()
                    countdown = self.ERROR_DELAY
                    print("ERROR build")
                    self.navigate.connect_to_account()

    def check_new_event(self, planet_list):
        """Watch periodically for any new incoming fleet"""
        fleet_observer = Observer(planet_list, self.navigate)
        while True:
            try:
                self.mutex.acquire()
                self.is_event_over = fleet_observer.check_new_event()
            except Exception:
                print("ERROR check_new_event")
            finally:
                self.mutex.release()
                time.sleep(self.DELAY)

    def send_fleet(self, fleet_order):
        """Send attacks and exploration"""
        while True:
            for fleet in fleet_order:
                sent = False
                countdown = 0
                while not sent:
                    try:
                        self.mutex.acquire()
                        if self.time_to_start_ghost.is_now():
                            (sent, countdown, message) = self.ghost_all_fleet()
                        else:
                            (sent, countdown, message) = self.navigate.send_fleet(
                                fleet["mission"],
                                fleet["coordinates"],
                                self.planet_list[fleet["origin_planet"]].planet_id,
                                fleet["list_ships"],
                            )
                        log(message)
                    except Exception:
                        print("ERROR send_fleet")
                        countdown = self.ERROR_DELAY
                    finally:
                        self.mutex.release()
                        time.sleep(countdown)

    def ghost_all_fleet(self):
        """Ghost all fleet on every planet"""
        for fleet in self.all_ghost_order:
            sent = False
            countdown = 0
            while not sent:
                try:
                    (sent, countdown, message) = self.navigate.send_fleet(
                        fleet["mission"],
                        fleet["coordinates"],
                        self.planet_list[fleet["origin_planet"]].planet_id,
                        fleet["list_ships"],
                        True,
                        self.time_to_end_ghost,
                    )
                except Exception:
                    print("ERROR ghost_all_fleet")
                finally:
                    time.sleep(countdown)
        self.time_to_start_ghost.get_next_day()
        self.time_to_end_ghost.get_next_day()
        return True, 0, "All Fleet have been ghosted"
