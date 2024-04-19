from aiomqtt.types import PayloadType


class SensorManager:
    # TODO: Заменить на создание списка объектов Sensor с омощью pydantic
    def __init__(self, sensors: dict):
        self.sensors: dict = sensors
        self.__initialize_sensors_state({"status": "down", "liquid": 0})

    def __initialize_sensors_state(self, state: dict) -> None:
        for sensor in self.sensors.values():
            if "state" not in sensor:
                sensor["state"] = dict()
            sensor["state"].update(state)

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
