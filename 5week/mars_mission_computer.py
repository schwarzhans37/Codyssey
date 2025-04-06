import random
import json
import time
from datetime import datetime

# 🧩[수행과제 4] DummySensor 클래스 정의
class DummySensor:
    def __init__(self):
        self.__env_values = {       # 외부에서 원시 데이터 값을 수정할 경우를 방지하고자 캡슐화(private 처리)
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
        # Dict는 가변 객체이기 때문에, 참조값이 외부로 전달되면 의도치 않게 수정될 가능성이 있음. 이를 .copy를 통해 방어함.

# 🧩[수행과제 1] MissionComputer 클래스 정의
class MissionComputer:
    def __init__(self):
        # 🧩[수행과제 2] Dict 객체 & env_values 속성
        self.__env_values = {       # 외부에서 원시 데이터 값을 수정할 경우를 방지하고자 캡슐화(private 처리)
            # 🧩[수행과제 3] env_values 속성 구현                 
            'timestamp': None,
            'mars_base_internal_temperature': None,
            'mars_base_external_temperature': None,
            'mars_base_internal_humidity': None,
            'mars_base_external_illuminance': None,
            'mars_base_internal_co2': None,
            'mars_base_internal_oxygen': None,
        }
        self.__env_log = [] # 5분 평균 계산용 리스트

    # 🧩[수행과제 5, 6] get_sensor_data() 메소드 구현
    def get_sensor_data(self, sensor):
        try:
            start_time = time.time()
            
            while True:
                sensor.set_env()                    # DummySensor 내부에서 새로운 랜덤 데이터를 생성시키기기
                sensor_data = sensor.get_env()      # 생성된 데이터를 읽어와 반환

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                self.__env_values.update({          # update를 사용한 이유는 따로 정리 "update_vs_assignment.md" 참조
                    'timestamp': current_time,
                    'mars_base_internal_temperature': sensor_data['mars_base_internal_temperature'],
                    'mars_base_external_temperature': sensor_data['mars_base_external_temperature'],
                    'mars_base_internal_humidity': sensor_data['mars_base_internal_humidity'],
                    'mars_base_external_illuminance': sensor_data['mars_base_external_illuminance'],
                    'mars_base_internal_co2': sensor_data['mars_base_internal_co2'],
                    'mars_base_internal_oxygen': sensor_data['mars_base_internal_oxygen'],
                })

                print(json.dumps(self.__env_values, indent=4, ensure_ascii=False))  # json.dump()는 모든 문자를 ASCII로만 표현하려고 하는 특징이 있음
                                                                                    # indent 들여쓰기(칸) // ensure_ascii = False 한글 깨짐 방지
                self.__env_log.append(sensor_data)
                
                # 🧩[보너스 과제 2] 5분마다 평균 출력
                if (time.time() - start_time) >= 300:
                    self.print_average()
                    self.__env_log.clear()
                    start_time = time.time()
                    
                time.sleep(5)
        
        # 🧩[보너스 과제1]
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

def main():
    # DummySensor 인스턴스 생성
    ds = DummySensor()

    # MissionComputer 인스턴스 생성
    RunComputer = MissionComputer()

    # 센서 데이터 수집 시작
    RunComputer.get_sensor_data(ds)

if __name__ == "__main__":
    main()