import time
import requests

accessToken = "Bearer NTMxMDNiZGYtYTM3YS00ODVlLWFlYTMtZmNiZTNlNDJmNmZlYWM0NzE0Y2UtZjlj_P0A1_935f4b77-0a1c-4d96-bc39-d07643ef6a87" 
responseMessage = ""
roomIdToGetMessages = "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vODgyNDM5NTAtNTI2My0xMWVmLWJjYTctYTE3MGI0ODFlZGZh"

while True:
    time.sleep(1)
    GetParameters = {
        "roomId": roomIdToGetMessages,
        "max": 1
    }

    try:
        r = requests.get("https://webexapis.com/v1/messages",
                         params=GetParameters, 
                         headers={"Authorization": accessToken}
        )
        if r.status_code != 200:
            print(f"Error: Webex Teams API responded with status code {r.status_code}")
            continue  # Skip to the next iteration of the loop

        json_data = r.json()
        if len(json_data["items"]) == 0:
            print("No messages in the room.")
            continue  # Skip to the next iteration if no messages

        message = json_data["items"][0].get("text", "")
        print("Received message: " + message)

        if message.find("/poohwadol ") == 0:
            location = message.split(' ', 1)[1]
        else:
            location = ''
            print("No valid command found.")
            continue  # Skip if the message doesn't contain a valid command

        openweatherGeoAPIGetParameters = {
            "q": location,
            "limit": 1,
            "appid": "b3603150ac4be299b4f54f7886b55378",
        }

        # Request Geocoding data
        try:
            r = requests.get("http://api.openweathermap.org/geo/1.0/direct",
                             params=openweatherGeoAPIGetParameters)
            if r.status_code != 200:
                print(f"Error: OpenWeather API responded with status code {r.status_code}")
                continue  # Skip to the next iteration of the loop

            json_data = r.json()
            if len(json_data) == 0:
                print(f"Location not found for '{location}'")
                continue  # Skip if the location is not found

            locationLat = json_data[0]["lat"]
            locationLng = json_data[0]["lon"]
        except Exception as e:
            print(f"Error during OpenWeather Geocoding API call: {e}")
            continue  # Skip to the next iteration of the loop

        openweatherAPIGetParameters = {
            "lat": locationLat,
            "lon": locationLng,
            "appid": "b3603150ac4be299b4f54f7886b55378",
            "units": "metric"
        }

        # Request Weather data
        try:
            rw = requests.get("https://api.openweathermap.org/data/2.5/weather",
                              params=openweatherAPIGetParameters)
            if rw.status_code != 200:
                print(f"Error: OpenWeather API responded with status code {rw.status_code}")
                continue  # Skip to the next iteration of the loop

            json_data_weather = rw.json()
            if "weather" not in json_data_weather:
                print("No weather data found.")
                continue  # Skip if no weather data is available

            weather_desc = json_data_weather["weather"][0]["description"]
            weather_temp = json_data_weather["main"]["temp"]
        except Exception as e:
            print(f"Error during OpenWeather Weather API call: {e}")
            continue  # Skip to the next iteration of the loop

        responseMessage = "In {} (latitude: {}, longitude: {}), the current weather is '{}' and the temperature is {} degree celsius.\n".format(
            location, locationLat, locationLng, weather_desc, weather_temp
        )
        print("Sending to Webex Teams: " + responseMessage)

        # Post to Webex Teams
        HTTPHeaders = {
            "Authorization": accessToken,
            "Content-Type": "application/json"
        }

        PostData = {
            "roomId": roomIdToGetMessages,
            "text": responseMessage
        }

        try:
            r = requests.post("https://webexapis.com/v1/messages",
                              json=PostData,
                              headers=HTTPHeaders)
            if r.status_code != 200:
                print(f"Error: Webex Teams API responded with status code {r.status_code}")
                continue  # Skip to the next iteration of the loop
        except Exception as e:
            print(f"Error while posting message to Webex Teams: {e}")
            continue  # Skip to the next iteration of the loop

    except Exception as e:
        print(f"Error during the Webex message processing: {e}")
        continue  # Catch any errors and continue the loop
