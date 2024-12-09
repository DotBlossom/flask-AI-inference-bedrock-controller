FROM python:3.9-slim


## 배포 환경에선 제거
# 빌드 시에 MongoDB 연결 정보를 전달받을 ARG 변수 정의
#ARG MONGO_URL

# 환경 변수 설정
#ENV MONGO_URL=$MONGO_URL


WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["flask", "run", "--host=0.0.0.0", "--port=5050"] 

