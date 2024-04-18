from aiomqtt.types import PayloadType


class SensorManager:
    def __init__(self):
        self.sensors: dict = dict()

        self.sensors["3C71BF1AC9B4"] = {
            "id": "3C71BF1AC9B4",
            "desc": "3-й этаж, правый холл, рядом с кабинетом 3-21",
            "plan": {"floor": 3, "coords": (0, 0)},
        }

        self.sensors["24DCC345DB74"] = {
            "id": "24DCC345DB74",
            "desc": "3-й этаж, центральный коридор, кабинет 3-1",
            "plan": {"floor": 3, "coords": (0, 0)},
        }

    def get_sensors(self) -> dict:
        return self.sensors

    def get_state(self, sensor_id: str) -> dict:
        if sensor_id not in self.sensors:
            return {}

        return self.sensors[sensor_id].get("state", {})

    def update_state(self, sensor_id: str, property_name: str, property_value: PayloadType) -> bool:
        if sensor_id not in self.sensors:
            return False

        sensor = self.sensors[sensor_id]

        if "state" not in sensor:
            sensor["state"] = dict()

        sensor["state"].update({property_name: property_value})

        return True
