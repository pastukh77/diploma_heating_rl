import requests

def get_cop(temp_outside):
    return 0.012 * temp_outside ** 2 + 0.1421 * temp_outside + 3.2578

def valve_effectiveness(df, valve, temp, eps=0.35):
    valve_df = df[df["valve"] == valve]
    valve_df = valve_df[valve_df["temp_act"].ge(temp - eps) & valve_df["temp_act"].le(temp + eps)]
    return valve_df["temp_delta"].mean() + 0.1

def get_temp(date_temp, latitude=49.80273462880719, longitude=23.99999116287077):
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={latitude}&longitude={longitude}&start_date={date_temp}&end_date={date_temp}&hourly=temperature_2m"
    response = requests.get(url)
    time_temp_dict = dict(zip(response.json()['hourly']['time'], response.json()['hourly']['temperature_2m']))
    time_temp_dict = dict(map(lambda key: (key.replace("T", " ")  + ":00", time_temp_dict[key]), time_temp_dict))
    return time_temp_dict

valve_multiplier = {17: 0.9, 18: 0.7, 20: 0.5}


