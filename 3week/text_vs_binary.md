## 1️⃣ 텍스트 파일 (Text File)
### ✔ 개념
- 사람이 읽을 수 있는 형식으로 저장된 파일.
- `.txt`, `.csv`, `.json`, `.xml` 같은 형식으로 사용됨.
- 데이터는 **문자열(UTF-8, ASCII 등 인코딩)** 로 저장됨.

### ✔ 장점
- ✅ **사람이 읽고 수정하기 쉬움** → 텍스트 편집기로 열 수 있음.
- ✅ **호환성이 높음** → OS나 프로그램에 관계없이 사용 가능.
- ✅ **디버깅이 쉬움** → 데이터가 깨져도 일부 내용을 확인할 수 있음.

### ✔ 단점
- ❌ **저장 용량이 큼** → 같은 데이터를 저장할 때 이진 파일보다 크기가 클 수 있음.
- ❌ **읽기/쓰기 속도가 느림** → 숫자 데이터를 문자열로 변환하는 과정이 필요함.
- ❌ **구조적인 데이터 처리 어려움** → 바이너리 데이터(예: 이미지, 오디오) 저장이 어려움.

---

## 2️⃣ 이진 파일 (Binary File)
### ✔ 개념
- 사람이 직접 읽을 수 없는 형식으로 저장된 파일.
- `.bin`, `.exe`, `.jpg`, `.mp3`, `.dat` 등의 형식이 포함됨.
- **0과 1의 바이너리(이진) 데이터로 저장됨** → CPU가 직접 해석 가능.

### ✔ 장점
- ✅ **저장 용량이 작음** → 데이터를 압축된 형태로 저장 가능.
- ✅ **처리 속도가 빠름** → CPU가 직접 해석하므로 변환 과정이 없음.
- ✅ **모든 종류의 데이터 저장 가능** → 이미지, 소리, 실행 파일까지 저장 가능.

### ✔ 단점
- ❌ **사람이 직접 읽거나 수정할 수 없음** → 전용 프로그램이 필요함.
- ❌ **파일이 깨지면 복구가 어려움** → 일부만 깨져도 전체 파일이 손상될 수 있음.
- ❌ **플랫폼 종속적일 수 있음** → 다른 운영체제나 프로그램에서 읽을 수 없을 수도 있음.

---

## 📌 정리 (비교 표)

| 구분        | 텍스트 파일 | 이진 파일 |
|------------|------------|------------|
| **읽기 방식** | 사람이 읽을 수 있음 | 사람이 읽을 수 없음 |
| **저장 크기** | 크기가 큼 | 크기가 작음 |
| **처리 속도** | 느림 | 빠름 |
| **수정 가능 여부** | 쉽게 수정 가능 | 직접 수정 어려움 |
| **호환성** | OS/프로그램에 관계없이 사용 가능 | 특정 프로그램이 필요할 수 있음 |
| **데이터 저장 유형** | 문자열 (텍스트) 저장 | 모든 데이터 저장 가능 (텍스트, 이미지, 오디오 등) |

---

