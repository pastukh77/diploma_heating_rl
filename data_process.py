import pandas as pd
import os

def nextHour(current):
  return pd.date_range(start=current, periods=2, freq="H")[1]


def get_room_df(room_id, path):
    temp_act_df = pd.read_csv(f"{path}/{room_id}_temp_act.csv", index_col=0)
    temp_target_df = pd.read_csv(f"{path}/{room_id}_temp_target.csv", index_col=0)
    temp_act_target = pd.merge(temp_act_df, temp_target_df, on="time")
    presence_df = pd.read_csv(f"{path}/{room_id}_presence.csv", index_col=0)
    temp_act_target_presence = pd.merge(temp_act_target, presence_df, on="time")
    temp_act_target_presence = temp_act_target_presence.rename({"state_x": "temp_act", 
        "state_y": "temp_target", "state": "presence"}, axis="columns")
    valve_df = pd.read_csv(f"{path}/{room_id}_valve.csv", index_col=0)
    room_df = pd.merge(valve_df, temp_act_target_presence, on="time").rename({"state": "valve"}, axis="columns")
    room_df["room_id"] = room_id
    return room_df
    
def get_all_rooms(path):
    room_ids = set([x.split("_")[0] for x in os.listdir(path)])
    room_ids = list(filter(lambda x: "." not in x, room_ids))
    room_df = pd.concat([get_room_df(room, path=path) for room in room_ids])
    weather_df = pd.read_csv(f"{path}/weather.csv")
    room_df.time = pd.to_datetime(room_df.time).dt.strftime('%Y-%m-%d %H:%M:%S')
    weather_df.time = pd.to_datetime(weather_df.time).dt.strftime('%Y-%m-%d %H:%M:%S')
    df = pd.merge(room_df, weather_df, on="time")
    lst = []

    for _, row in df.iterrows():
        try:
            # next_calc[row["time"], row["room_id"]] = 
            # print(row["time"], str(nextHour(row["time"])))
            x = list(df[df["time"].eq(str(nextHour(row["time"]))) & df["room_id"].eq(row["room_id"])][["temp_act", "room_id"]].iloc[0])
            lst.append(x + [row["time"]])
        except IndexError:
            pass

    res = pd.merge(df, pd.DataFrame(lst, columns=["next_hour_temp", "room_id", "time"]), on=["time", "room_id"])
    res["temp_delta"] = res["next_hour_temp"] - res["temp_act"]
    return res



