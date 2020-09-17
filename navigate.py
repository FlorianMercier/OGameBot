import time
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options


class Nav:
    """Class to navigate and perform actions on OGame website"""

    # Class parameters
    RESSOURCES_LIST = ["metal", "crystal", "deuterium", "energy"]
    COMPONENTS_LIST = ["supplies", "facilities", "research", "shipyard", "defenses"]
    NUMBER_OF_SECONDS = [1, 60, 3600, 86400, 604800]
    DELAY = 5
    RETRY_MAX = 3
    MESSAGE = "Je suis là, il n'y aura aucune ressource sur ma planète lors de ton attaque."

    def __init__(self, login):
        """Init chrome driver"""
        # Add AddBlock extension
        path_to_extension = r"D:\Documents\workspace\project_2\1.28.4_3"
        chrome_options = Options()
        chrome_options.add_argument("load-extension=" + path_to_extension)
        # Create chrome webdriver
        driverLocation = r".\chromedriver.exe"
        self.driver = webdriver.Chrome(driverLocation, options=chrome_options)
        self.driver.create_options()
        # Create waiting condition
        self.wait = WebDriverWait(self.driver, self.DELAY)
        # Closing the data tab
        self.close_new_tab()
        # Set intern paramaters
        self.LOGIN = login

    def close_new_tab(self):
        """Close the tab right after the current tab"""
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def connect_to_account(self):
        """Log a chrome browser to your account or sign on if connection has been lost"""
        # Go to the game lobby
        self.driver.get("https://lobby.ogame.gameforge.com/fr_FR/hub")
        # Check if the account is already checked in or not
        try:
            # Wait for the lobby to be fully loaded
            loginRegisterTabs = self.wait.until(
                EC.visibility_of_element_located((By.ID, "loginRegisterTabs"))
            )
            # Select the login box to enter id
            loginRegisterTabs.find_element_by_tag_name("span").click()
            # Enter email and password
            loginRegisterTabs.find_element_by_name("email").send_keys(
                self.LOGIN["EMAIL"]
            )
            loginRegisterTabs.find_element_by_name("password").send_keys(
                self.LOGIN["PASSWORD"]
            )
            # Click on the login button
            loginRegisterTabs.find_element_by_class_name("button-primary").click()
        except Exception:
            pass
        # Log to server menu
        try:
            # Wait for game menu to be fully loaded
            joinGame = self.wait.until(
                EC.visibility_of_element_located((By.ID, "joinGame"))
            )
            # Click on the play button
            joinGame.find_element_by_class_name("button-primary").click()
        except Exception:
            raise Exception("No Internet")
        # Chose server and log to the game
        try:
            # Wait for the server menu to be fully loaded
            accountlist = self.wait.until(
                EC.visibility_of_element_located((By.ID, "accountlist"))
            )
            # Select your universe
            universe_list = accountlist.find_elements_by_class_name("rt-tr-group")
            for universe in universe_list:
                server_name = universe.find_element_by_class_name("server-name-cell")
                if server_name.text == self.LOGIN["UNIVERSE"]:
                    #  When windows is small, this tab needs to be opened
                    server_name.click()
                    time.sleep(0.5)
                    universe.find_element_by_class_name("btn-primary").click()
                    time.sleep(1)
                    break
        except Exception:
            raise Exception("Cannot find universe")
        # Switch back to the first tab
        try:
            self.close_new_tab()
        except Exception:
            raise Exception("Tab issue")
        # Load the main page of your account
        try:
            self.load_page("overview")
        except Exception:
            raise Exception("No Internet")
        # Close chatbox that could cover game button
        try:
            # Wait for the game account to be fully loaded
            chat = self.wait.until(EC.presence_of_element_located((By.ID, "chatBar")))
            # Close the friend list at the bottom if open, could cause issue to click later on
            if (
                chat.find_element_by_class_name("cb_playerlist_box").get_attribute(
                    "style"
                )
                == "display: block;"
            ):
                chat.click()
        except Exception:
            pass

    def convert_resource_to_int(self, str_ressource):
        """Remove the decimal part of ressource and convert string into int"""
        return int(str_ressource.split(".")[0])

    def get_resources(self):
        """Retreive every ressources amount"""
        resources_dict = dict()
        for resources in self.RESSOURCES_LIST:
            resources_dict[resources] = self.convert_resource_to_int(
                self.driver.find_element_by_id("resources_" + resources).get_attribute(
                    "data-raw"
                )
            )
        return resources_dict

    def load(self, address):
        """Load and wait for a page"""
        self.driver.get(address)
        self.wait.until(EC.visibility_of_element_located((By.ID, "menuTable")))

    def load_address(self, address):
        retry = 0
        while retry <= self.RETRY_MAX:
            try:
                self.load(address)
                return True
            except Exception:
                retry += 1
                self.connect_to_account()
        return False

    def load_page(self, component, planet_id=0):
        """Load a specific page of a given planet and try to reconnect if the page is not loaded"""
        address = "https://{0}.ogame.gameforge.com/game/index.php?page=ingame&component={1}".format(
            self.LOGIN["CODE"], component
        )
        if planet_id != 0:
            address += "&cp={}".format(planet_id)
        retry = 0
        while retry <= self.RETRY_MAX:
            try:
                self.load(address)
                return True
            except Exception:
                retry += 1
                self.connect_to_account()
        return False

    def get_planet_dictionary(self):
        """Get every planet name, id and coord of the account"""
        planet_list_dictionary = dict()
        planet_list = self.driver.find_elements_by_class_name("smallplanet")
        for planet in planet_list:
            planet_dictionary = dict()
            planet_dictionary["id"] = planet.get_attribute("id").split("-")[1]
            planet_dictionary["coord"] = planet.find_element_by_class_name(
                "planet-koords"
            ).text
            planet_list_dictionary[
                planet.find_element_by_class_name("planet-name").text
            ] = planet_dictionary
        return planet_list_dictionary

    def get_unit_info(self, component, planet_id):
        """Retreive category, component, id, type and value of every unit from a given page"""
        self.load_page(component, planet_id)
        unit_dictionary = dict()
        try:
            unit_group = self.driver.find_element_by_id("technologies")
            category = "technologies"
        except EC.NoSuchElementException:
            unit_group = self.driver.find_element_by_id("producers")
            category = "producers"

        unit_list = unit_group.find_elements_by_tag_name("li")
        for unit in unit_list:
            unit_name = unit.get_attribute("aria-label")
            data_id = unit.get_attribute("data-technology")
            try:
                value = unit.find_element_by_class_name("level").get_attribute(
                    "data-value"
                )
                type = "level"
            except EC.NoSuchElementException:
                value = unit.find_element_by_class_name("amount").get_attribute(
                    "data-value"
                )
                type = "amount"
            unit_info = {
                "category": category,
                "component": component,
                "id": data_id,
                "type": type,
                "value": int(value),
            }
            unit_dictionary[unit_name] = unit_info

        return unit_dictionary

    def get_unit_dictionary(self, planet_id):
        """Retreive every unit information"""
        unit_dictionary = dict()
        for component in self.COMPONENTS_LIST:
            unit_dictionary.update(self.get_unit_info(component, planet_id))
        return unit_dictionary

    def get_resources_rate(self, planet_id):
        """Retreive every ressource production rate"""
        self.load_address(
            "https://{0}.ogame.gameforge.com/game/index.php?page=resourceSettings&cp={1}".format(
                self.LOGIN["CODE"], planet_id
            )
        )
        element = self.driver.find_element_by_class_name("summary")
        resources_info_list = element.find_elements_by_class_name("tooltipCustom")
        resources_info_dict = {
            name: int(value.text.replace(".", ""))
            for name, value in zip(self.RESSOURCES_LIST, resources_info_list)
        }
        return resources_info_dict

    def convert_string_time(self, string_time):
        """Convert time string into seconds"""
        time, i = 0, 0
        for time_item in string_time.split()[::-1]:
            time += int(time_item[:-1]) * self.NUMBER_OF_SECONDS[i]
            i += 1
        return time

    def check_if_busy(self):
        """Check if a building or a research is already going on, blocking the current production"""
        countdown = 0
        try:
            production = self.driver.find_element_by_id(
                "productionboxbuildingcomponent"
            )
            string_time = production.find_element_by_id("buildingCountdown").text
            countdown = self.convert_string_time(string_time)
        except EC.NoSuchElementException:
            pass
        try:
            production = self.driver.find_element_by_id(
                "productionboxresearchcomponent"
            )
            string_time = production.find_element_by_id("researchCountdown").text
            countdown = self.convert_string_time(string_time)
        except EC.NoSuchElementException:
            pass
        return countdown

    def get_countdown(self):
        """Retreive the countdown of the current building unit"""
        countdown = self.wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "countdown"))
        )
        return int(countdown.get_attribute("data-end"))- int(
            countdown.get_attribute("data-start")
        )

    def upgrade_unit(self, planet_id, unit_name, unit, amount):
        """Build unit on the given planet, and at the given amount if possible"""
        # Go to the unit page
        self.load_page(unit["component"], planet_id)

        # Check if a building is not already beeing built
        countdown = self.check_if_busy()
        if countdown > 0:
            return (
                False,
                countdown,
                " cannot be upgraded, a unit is already beeing built, next try in {}s".format(
                    str(countdown)
                ),
            )

        # Get the unit details
        unit_group = self.driver.find_element_by_id(unit["category"])
        selector = '[aria-label="{}"]'.format(unit_name)
        unit_group.find_element_by_css_selector(selector).click()
        # Wait for the unit detail to be fully loaded
        unit_info = self.wait.until(
            EC.visibility_of_element_located((By.ID, "technologydetails"))
        )
        data_id = unit_info.get_attribute("data-technology-id")
        # Check the selected unit is the right one
        if data_id != unit["id"]:
            return (False, -1, " Error")

        # Compute needed ressources, Unit can be an amount type or a level type
        resources_needed = {"metal": 0, "crystal": 0, "deuterium": 0, "energy": 0}
        # Get price of the unit, For ships and defenses multiply by number
        cost_list = unit_info.find_element_by_class_name(
            "costs"
        ).find_elements_by_tag_name("li")
        for cost in cost_list:
            resources_name = cost.get_attribute("class").split()[1]
            resources_quantity = cost.get_attribute("data-value")
            resources_needed[resources_name] = int(resources_quantity) * amount
        # Get planet resources
        resources = self.get_resources()
        # Check if resource are enough to upgrade unit(s)
        for name, quantity in resources_needed.items():
            if quantity > 0 and quantity > resources[name]:
                countdown = (
                    (quantity - resources[name])
                    / self.get_resources_rate(planet_id)[name]
                ) * 3600
                return (
                    False,
                    countdown,
                    " cannot be upgraded, {0} more {1} is needed, next try in {2}s".format(
                        quantity - resources[name], name, str(countdown)
                    ),
                )

        # When needed write the amount of units to build
        if unit["type"] == "amount":
            build_amount = unit_info.find_element_by_id("build_amount")
            build_amount.send_keys(amount)
        # Upgrade unit(s)
        unit_info.find_element_by_class_name("upgrade").click()
        # Get the construction time in a try to prevent unit to be built again
        try:
            countdown = self.get_countdown()
        except Exception:
            countdown = 0

        return (True, countdown, " has been built successfully.")

    def load_fleet_content(self, retry=0):
        """UNUSED - Open the information list on the fleet events"""
        if retry <= self.RETRY_MAX:
            try:
                self.driver.find_element_by_id("messages_collapsed").click()
                self.wait.until(
                    EC.visibility_of_element_located((By.ID, "eventContent"))
                )
                return True
            except Exception:
                self.load_page("overview")
                if self.load_fleet_content(retry + 1):
                    return True
                else:
                    return False
        else:
            return False

    def get_fleet_events(self):
        """Retreive all fleet information"""
        self.load_page("overview&ajax=1")
        fleet_event_list = self.driver.find_element_by_id(
            "eventContent"
        ).find_elements_by_class_name("eventFleet")

        list_event = list()
        for event in fleet_event_list:
            mission_type = int(event.get_attribute("data-mission-type"))
            remaining_time = event.find_element_by_class_name("countDown").text
            arrival_time = event.find_element_by_class_name("arrivalTime").text
            origin_planet_name = event.find_element_by_class_name("originFleet").text
            origin_planet_coord = event.find_element_by_class_name("coordsOrigin").text
            detail_fleet = event.find_element_by_class_name("detailsFleet").text
            destination_planet_name = event.find_element_by_class_name("destFleet").text
            destination_planet_coord = event.find_element_by_class_name(
                "destCoords"
            ).text
            try:
                player_id = (
                    event.find_element_by_class_name("sendMail")
                    .find_element_by_class_name("js_openChat")
                    .get_attribute("data-playerid")
                )
            except Exception:
                player_id = ""

            list_event.append(
                {
                    "detail_fleet": detail_fleet,
                    "origin_planet_name": origin_planet_name,
                    "origin_planet_coord": origin_planet_coord,
                    "destination_planet_name": destination_planet_name,
                    "destination_planet_coord": destination_planet_coord,
                    "remaining_time": remaining_time,
                    "arrival_time": arrival_time,
                    "mission_type": mission_type,
                    "player_id": player_id,
                }
            )
        return list_event

    def send_message_enemy(self, player_id):
        """Send a message to an enemy"""
        self.load_address(
            "https://{0}.ogame.gameforge.com/game/index.php??page=chat&playerId={1}".format(
                self.LOGIN["CODE"], player_id
            )
        )
        text_area = self.driver.find_element_by_class_name("new_msg_textarea")
        text_area.send_keys(self.MESSAGE)
        self.driver.find_element_by_class_name("send_new_msg").click()

    def click(self, button):
        """Click on a button and scroll if necessary"""
        button.location_once_scrolled_into_view
        button.click()

    def send_ship(self, ship, amount):
        """Fill the given number of given ship to send"""
        unit = self.driver.find_element_by_id("technologies").find_element_by_xpath(
            '//li[@aria-label="{}"]'.format(ship)
        )
        max_amount = int(
            unit.find_element_by_class_name("amount").get_attribute("data-value")
        )
        unit.find_element_by_tag_name("input").send_keys(min(amount, max_amount))

    def is_free_fleet_slot(self, mission):
        """Check if a slot is free for expedition or any other type of mission"""
        list_tooltips = self.driver.find_element_by_class_name(
            "fleetStatus"
        ).find_elements_by_class_name("tooltip")
        slots = list_tooltips[0].text.split(":")[1].split("/")
        expeditions = list_tooltips[1].text.split(":")[1].split(" ")[1].split("/")

        if mission == 15:
            return int(slots[0]) < int(slots[1]) and int(expeditions[0]) < int(
                expeditions[1]
            )
        else:
            return int(slots[0]) < int(slots[1])

    def get_fleet_countdown(self, mission):
        """Return the amount of time of the next fleet to arrive to destination"""
        min = 0
        event_list = self.get_fleet_events()
        if len(event_list) > 0:
            min = self.convert_string_time(event_list[0]["remaining_time"])
            for event in event_list:
                remaining_time = self.convert_string_time(event["remaining_time"])
                if remaining_time < min:
                    min = remaining_time
        return min

    def send_fleet(
        self,
        mission,
        coordinates,
        planet_id,
        list_ships=None,
        ghosting=False,
        return_time=None,
        speed=10,
    ):
        """Send the given fleet to the given destination from the given planet to execute the given mission"""
        # Get coordinates information
        (galaxy, system, position, origin_type, destination_type) = coordinates
        # Load the address with all mission params so form is pre filled
        address = (
            "https://{0}.ogame.gameforge.com/game/index.php?page=ingame&component=fleetdispatch".format(
                self.LOGIN["CODE"]
            )
            + "&mission="
            + str(mission)
            + "&position="
            + str(position)
            + "&type="
            + str(origin_type)
            + "&galaxy="
            + str(galaxy)
            + "&system="
            + str(system)
            + "&type="
            + str(destination_type)
            + "&cp="
            + str(planet_id)
        )
        self.load_address(address)
        # Check if a slot is free to send a new fleet
        if self.is_free_fleet_slot(mission):
            # If no ship list is given send all ships on the planet
            if list_ships is None:
                self.click(self.driver.find_element_by_id("sendall"))
                list_ships = ["All Ships"]
            else:
                for ship, amount in list_ships:
                    self.send_ship(ship, amount)
            # Chose the speed of the fleet
            self.click(self.driver.find_element_by_id("continueToFleet2"))
            speed_bar = self.wait.until(
                EC.visibility_of_element_located((By.CLASS_NAME, "steps"))
            )
            if return_time is not None:
                string_time = self.driver.find_element_by_id("returnTime").text
                while speed > 1 and return_time.is_after_string(string_time):
                    speed -= 1
                    self.click(
                        speed_bar.find_element_by_xpath(
                            '//div[@data-step="{}"]'.format(speed)
                        )
                    )
                    string_time = self.driver.find_element_by_id("returnTime").text
            else:
                self.click(
                    speed_bar.find_element_by_xpath(
                        '//div[@data-step="{}"]'.format(speed)
                    )
                )
            # Chose the resources to bring with the fleet
            self.click(
                self.wait.until(
                    EC.visibility_of_element_located((By.ID, "continueToFleet3"))
                )
            )
            if ghosting:
                self.click(
                    self.wait.until(
                        EC.visibility_of_element_located((By.ID, "allresources"))
                    )
                )
            # Select the right mission it should be preselected anyway
            self.click(
                self.wait.until(
                    EC.visibility_of_element_located(
                        (By.ID, "missionButton{}".format(mission))
                    )
                )
            )
            # Send the fleet
            self.click(
                self.wait.until(EC.visibility_of_element_located((By.ID, "sendFleet")))
            )
            # Wait to be back at the first step page before doing an other action
            self.wait.until(
                EC.visibility_of_element_located((By.ID, "continueToFleet2"))
            )
            message = "The fleet has been sent to [{0}:{1}:{2}] : {3}.".format(
                str(galaxy), str(system), str(position), list_ships
            )
            return True, 0, message
        else:
            countdown = self.get_fleet_countdown(mission)
            return (
                False,
                countdown,
                "No slot available to send, next try in {}s".format(str(countdown)),
            )
