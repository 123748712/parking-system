from flask import Flask, request, jsonify, render_template
from db.db_helper import DB, DB_CONFIG
import serial
import time
import threading
import logging
import atexit
import json

app = Flask(__name__)

PORT = 'COM6' 
BAUD = 9600
# ser = serial.Serial(PORT, BAUD, timeout=1)
ser_lock = threading.Lock()

# 한개의 listener로 threading 처리
def serial_listener():
    global ser
    try:
        time.sleep(2)  # 아두이노 초기화 대기
        print(f" Connected to {PORT}")
        while True:
            data = ""
            with ser_lock:
                if ser.in_waiting > 0:
                    data = ser.readline().decode('utf-8', errors='ignore').strip()
                    print("수신된 데이터:", data)

            # 데이터가 없다면 계속
            if not data:
                continue

            # 게이트 명령 처리
            if data == 'open' or data == 'close':
                print("게이트 명령 처리 진행중 :::::::::")
                insert_parking_log(data)
                continue

            try:
                if "," in data:
                    angle_str, dist_str = data.split(",")
                    angle = int(angle_str)
                    distance = int(dist_str)
                    with radar_data_lock:
                        radar_data.append((angle, distance))
                        if len(radar_data) > 2:  # 최근 100개만 유지
                            radar_data.pop(0)
            except ValueError:
                print("⚠️ 레이더 데이터 파싱 실패:", data)

            # RFID 데이터 처리
            try:
                jsonData = json.loads(data)
                rfid_tag = jsonData.get("rfid_tag")
                spot_id = jsonData.get("spot_id")
                car_id = check_rfid_match(spot_id, rfid_tag)
                print(f"차량번호 : {car_id}")
                with ser_lock:
                    ser.write(f"{car_id}\n".encode())
            except json.JSONDecodeError:
                print("⚠️ JSON 파싱 실패:", data)

    except serial.SerialException as e:
        print("시리얼 통신 에러")
    except KeyboardInterrupt:
        print("시리얼 종료")
        ser.close()

# 주차 로그 쌓기
def insert_parking_log(action):
    db = DB(**DB_CONFIG)
    event_type = "IN" if action == "open" else "OUT"
    try:
        result = db.insert_parking_log(event_type)
        print(f"저장 완료 : {result}")
    except Exception as e:
        print(f"저장 실패: {e}")


# ================= RFID 체크 함수 =================
def check_rfid_match(spot_id, rfid_tag):
    db = DB(**DB_CONFIG)
    car_id = db.get_registered_rfid(spot_id, rfid_tag)
    
    if car_id != None:
        return car_id
    else:
        return ""
    

@app.route('/')
def main():
    return render_template('main.html')

@app.route("/gateCtrl", methods=['POST'])
def fn_reqGateCtrl():
    global ser
    data = request.get_json()
    action = data.get("action")

    if action not in ["open", "close"]:
        return jsonify({"error": "잘못된 액션"}), 400

    # 시리얼로 명령 전송
    with ser_lock:
        if ser and ser.is_open:
            try:
                ser.write(f"{action}\n".encode())
                ser.flush()
                return jsonify({"result": "명령 전송 완료"}), 200
            except Exception as e:
                return jsonify({"error": "시리얼 전송 실패"}), 500
        else:
            return jsonify({"error": "시리얼 포트 연결 실패"}), 500

radar_data = []  # (angle, distance) 튜플 리스트
radar_data_lock = threading.Lock()


@app.route("/radar.do", methods=["GET"])
def get_radar_data():
    with radar_data_lock:
        return jsonify(radar_data)

@app.route("/radar", methods=["GET"])
def radar():
    return render_template('radar.html')
    


if __name__ == '__main__':
    listener_thread = threading.Thread(target=serial_listener, daemon=True)
    listener_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=False)
