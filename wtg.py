import requests

city = "Pune"
url = f"https://wttr.in/{city}?format=j1"

response = requests.get(url)
data = response.json()

# Extract details
current = data["current_condition"][0]
temp = current["temp_C"]
condition = current["weatherDesc"][0]["value"]

print(f"Location: {city}")
print(f"Temperature: {temp}°C")
print(f"Condition: {condition}")