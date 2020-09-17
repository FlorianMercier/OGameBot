from manager import Manager

# Write your id
login = {
    "EMAIL": "YOUR_EMAIL",
    "PASSWORD": "YOUR_PASSWORD",
    "CODE": "YOUR_CODE",
    "UNIVERSE": "YOUR_UNIVERSE",
}

# Initialize and start the OGame Manager
empire = Manager(login)
empire.start()
