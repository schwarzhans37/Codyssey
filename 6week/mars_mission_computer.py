import random
import json
import time
import platform
import os
import psutil
from datetime import datetime

class DummySensor:
    def __init__(self):
        self.__env_values = {
            'mars_base_internal_temperature': None,
            'mars_base_external_temperature': None,
            'mars_base_internal_humidity': None,
            'mars_base_external_illuminance': None,
            'mars_base_internal_co2': None,
            'mars_base_internal_oxygen': None,
        }

    def set_env(self):
        self.__env_values['mars_base_internal_temperature'] = random.uniform(18, 30)
        self.__env_values['mars_base_external_temperature'] = random.uniform(0, 21)
        self.__env_values['mars_base_internal_humidity'] = random.uniform(50, 60)
        self.__env_values['mars_base_external_illuminance'] = random.uniform(500, 715)
        self.__env_values['mars_base_internal_co2'] = random.uniform(0.02, 0.1)
        self.__env_values['mars_base_internal_oxygen'] = random.uniform(4, 7)

    def get_env(self):
        return self.__env_values.copy()

class MissionComputer:
    def __init__(self):
        self.__env_values = {
            'timestamp': None,
            'mars_base_internal_temperature': None,
            'mars_base_external_temperature': None,
            'mars_base_internal_humidity': None,
            'mars_base_external_illuminance': None,
            'mars_base_internal_co2': None,
            'mars_base_internal_oxygen': None,
        }
        self.__env_log = []
        self.settings = self.read_settings()

    def read_settings(self):
        # 상대경로로 경로를 지정했더니 인식하지 못하는 문제가 발생해 절대경로로 수정 // setting.txt를 현재 py 파일과 같은 위치로 경로 고정
        # setting_file = "setting.txt"
        script_dir = os.path.dirname(os.path.abspath(__file__))
        setting_file = os.path.join(script_dir, "setting.txt")
        
        default_keys = [
            'os', 'os_version', 'cpu_type', 'cpu_cores',
            'memory_total_GB', 'cpu_usage_percent', 'memory_usage_percent'
        ]
        selected_keys = []

        try:
            with open(setting_file, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if line in default_keys:
                            selected_keys.append(line)
        except FileNotFoundError:
            print("[경고] setting.txt 파일이 없어 모든 항목을 출력합니다.")
            return default_keys

        return selected_keys

    def get_sensor_data(self, sensor):
        try:
            start_time = time.time()
            while True:
                sensor.set_env()
                sensor_data = sensor.get_env()

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.__env_values.update({
                    'timestamp': current_time,
                    'mars_base_internal_temperature': sensor_data['mars_base_internal_temperature'],
                    'mars_base_external_temperature': sensor_data['mars_base_external_temperature'],
                    'mars_base_internal_humidity': sensor_data['mars_base_internal_humidity'],
                    'mars_base_external_illuminance': sensor_data['mars_base_external_illuminance'],
                    'mars_base_internal_co2': sensor_data['mars_base_internal_co2'],
                    'mars_base_internal_oxygen': sensor_data['mars_base_internal_oxygen'],
                })

                print(json.dumps(self.__env_values, indent=4, ensure_ascii=False))
                self.__env_log.append(sensor_data)

                if (time.time() - start_time) >= 300:
                    self.print_average()
                    self.__env_log.clear()
                    start_time = time.time()

                time.sleep(5)
        except KeyboardInterrupt:
            print("\nSystem stopped...")

    def print_average(self):
        if not self.__env_log:
            return

        avg_values = {
            key: sum(entry[key] for entry in self.__env_log) / len(self.__env_log)
            for key in self.__env_log[0]
        }

        print("\n[5분 평균 환경 정보]")
        print(json.dumps(avg_values, indent=4, ensure_ascii=False))

    def get_mission_computer_info(self):
        try:
            full_info = {
                'os': platform.system(),
                'os_version': platform.version(),
                'cpu_type': platform.processor(),
                'cpu_cores': os.cpu_count(),
                'memory_total_GB': round(psutil.virtual_memory().total / (1024**3), 2)
            }

            selected_info = {k: full_info[k] for k in self.settings if k in full_info}

            print("\n[미션 컴퓨터 시스템 정보]")
            print(json.dumps(selected_info, indent=4, ensure_ascii=False))
        except Exception as e:
            print(f"[오류] 시스템 정보를 가져오는 중 문제가 발생했습니다: {e}")

    def get_mission_computer_load(self):
        try:
            full_load = {
                'cpu_usage_percent': psutil.cpu_percent(interval=1),
                'memory_usage_percent': psutil.virtual_memory().percent
            }

            selected_load = {k: full_load[k] for k in self.settings if k in full_load}

            print("\n[미션 컴퓨터 실시간 부하 정보]")
            print(json.dumps(selected_load, indent=4, ensure_ascii=False))
        except Exception as e:
            print(f"[오류] 시스템 부하 정보를 가져오는 중 문제가 발생했습니다: {e}")

def main():
    ds = DummySensor()
    runComputer = MissionComputer()

    # 설정 기반 정보 출력
    runComputer.get_mission_computer_info()
    runComputer.get_mission_computer_load()

    # 센서 데이터 수집 (선택 사항)
    # runComputer.get_sensor_data(ds)

if __name__ == "__main__":
    main()
