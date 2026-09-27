import random
from datetime import datetime, timedelta

def generate_random_date(start_str: str, end_str: str) -> str:
    """Generate a random ISO date string between two dates."""
    start = datetime.strptime(start_str, "%Y-%m-%d")
    end = datetime.strptime(end_str, "%Y-%m-%d")
    delta = end - start
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, 86400)
    res = start + timedelta(days=random_days, seconds=random_seconds)
    return res.strftime("%Y-%m-%d %H:%M:%S")

FIRST_NAMES = [
    "Aarav", "Ananya", "Rajesh", "Priya", "Vikram", "Sunita", "Rohan", "Kavita", "Amit", 
    "Neha", "Arjun", "Pooja", "Suresh", "Anita", "Rahul", "Meera", "Sanjay", "Deepika", 
    "Deepak", "Ritu", "Aditya", "Shweta", "Manoj", "Divya", "Dev", "Anjali", "Karthik", 
    "Swati", "Vishal", "Lakshmi", "Preeti", "Alok", "Niharika", "Tarun", "Bhavna"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Gupta", "Kumar", "Singh", "Reddy", "Joshi", "Mehta", 
    "Rao", "Iyer", "Nair", "Chatterjee", "Das", "Sen", "Agarwal", "Bansal", "Deshmukh", 
    "Kulkarni", "Mukherjee", "Bhat", "Pillai", "Malhotra", "Kapoor", "Nanda", "Saxena", 
    "Chaudhary", "Trivedi", "Jha", "Mishra", "Hegde", "Shetty", "Desai", "Dutta"
]

CITIES_BY_REGION = {
    "North India": [("Delhi", "DL"), ("Gurugram", "HR"), ("Noida", "UP"), ("Chandigarh", "PB"), ("Jaipur", "RJ"), ("Lucknow", "UP")],
    "South India": [("Bengaluru", "KA"), ("Chennai", "TN"), ("Hyderabad", "TS"), ("Kochi", "KL"), ("Visakhapatnam", "AP")],
    "West India": [("Mumbai", "MH"), ("Pune", "MH"), ("Ahmedabad", "GJ"), ("Surat", "GJ"), ("Nagpur", "MH")],
    "East & Central India": [("Kolkata", "WB"), ("Bhubaneswar", "OD"), ("Patna", "BR"), ("Indore", "MP"), ("Ranchi", "JH")],
    "North East India": [("Guwahati", "AS"), ("Shillong", "ML"), ("Imphal", "MN"), ("Agartala", "TR")]
}
