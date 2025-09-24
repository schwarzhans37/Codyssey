import random
import datetime
import csv

# [수행과제1] DummySensor 클래스 생성
class DummySensor:
    def __init__(self):
        # [수행과제2] env_values 사전 객체 추가
        self.env_values = {
            'mars_base_internal_temperature': None, # 화성 기지 내부 온도
            'mars_base_external_temperature': None, # 화성 기지 외부 온도
            'mars_base_internal_humidity': None,    # 화성 기지 내부 습도
            'mars_base_external_illuminance': None, # 화성 기지 외부 광량
            'mars_base_internal_co2': None,         # 화성 기지 내부 이산화탄소 농도
            'mars_base_internal_oxygen': None,      # 화성 기지 내부 산소 농도
        }
        
    # [수행과제3] 더미 데이터 값 랜덤 생성
    def set_env(self):
        self.env_values['mars_base_internal_temperature'] = random.uniform(18, 30)      # 단위 : °C
        self.env_values['mars_base_external_temperature'] = random.uniform(0, 21)       # 단위 : °C
        self.env_values['mars_base_internal_humidity'] = random.uniform(50, 60)         # 단위 : %
        self.env_values['mars_base_external_illuminance'] = random.uniform(500, 715)    # 단위 : W/m2
        self.env_values['mars_base_internal_co2'] = random.uniform(0.02, 0.1)           # 단위 : %
        self.env_values['mars_base_internal_oxygen'] = random.uniform(4, 7)             # 단위 : %
    
    # [수행과제4] env_values의 값을 return 하는 메소드 & 로그를 CSV 파일에 기록  
    def get_env(self):
        log_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = [
            log_time,
            round(self.env_values['mars_base_internal_temperature'], 2),
            round(self.env_values['mars_base_external_temperature'], 2),
            round(self.env_values['mars_base_internal_humidity'], 2),
            round(self.env_values['mars_base_external_illuminance'], 2),
            round(self.env_values['mars_base_internal_co2'], 4),
            round(self.env_values['mars_base_internal_oxygen'], 2)
        ]
        
        log_file = "4week/mars_env_log.csv"
        header = [
            "Timestamp", "Internal Temperature (°C)", "External Temperature (°C)",
            "Internal Humidity (%)", "External Illuminance (W/m²)", "Internal CO2 (%)", "Internal O2 (%)"
        ]
        
        # CSV 파일에 로그 기록 (파일이 존재하지 않으면 헤더 추가)
        try:
            with open(log_file, "r", encoding='utf-8') as f:
                file_exists = True
        except FileNotFoundError:
            file_exists = False
        
        with open(log_file, "a", newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='\t')
            if not file_exists:
                writer.writerow(header)
            writer.writerow(log_entry)
        
        return self.env_values
    
ds = DummySensor()  # DummySensor 인스턴스 생성
ds.set_env()        # 환경 데이터 설정
print(ds.get_env()) # 환경 데이터 출력 및 CSV 파일 기록