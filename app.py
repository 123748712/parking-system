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
ser = None
ser_lock = threading.Lock()


# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
def gate_control():
    """시리얼 연결 및 데이터 수신 스레드 (재연결 지원)"""
    global ser
    while True:
        try:
            with ser_lock:
                if ser is None or not ser.is_open:
                    ser = serial.Serial(PORT, BAUD, timeout=1)
                    time.sleep(2)
                    logger.info(f"Connected to Arduino on {PORT}")
            while ser and ser.is_open:
                if ser.in_waiting > 0:
                    data = ser.readline().decode('utf-8').strip()
                    logger.info(f" Received: {data}")
                time.sleep(0.01)
        except serial.SerialException as e:
            logger.error(f"Serial error: {e}")
            with ser_lock:
                if ser and ser.is_open:
                    ser.close()
                ser = None
            time.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected error in gate_control: {e}")
            time.sleep(5)

def read_rfid():
    """시리얼에서 RFID UID를 읽어 latest_rfid에 저장"""
    global latest_rfid
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        time.sleep(2)  # 아두이노 초기화 대기
        print(f"✅ Connected to {PORT}")

        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8', errors='ignore').strip()
                print(data)
                if not data:
                    continue  # 빈 줄이면 무시하고 루프 계속

                with ser_lock:
                    try:
                        jsonData = json.loads(data)
                        rfid_tag = jsonData.get("rfid_tag")
                        spot_id = jsonData.get("spot_id")
                        car_id = check_rfid_match(spot_id, rfid_tag)
                        print(f"차량번호 : {car_id}")
                        ser.write(f"{car_id}\n".encode())
                    except json.JSONDecodeError:
                        print("시리얼 통신 에러 발생")
    except serial.SerialException as e:
        print("❌ Serial Error:", e)
    except KeyboardInterrupt:
        print("\n⛔ RFID 스레드 종료")
        ser.close()

# ================= RFID 체크 함수 =================
def check_rfid_match(spot_id, rfid_tag):
    db = DB(**DB_CONFIG)
    car_id = db.get_registered_rfid(spot_id, rfid_tag)
    
    if car_id != None:
        return car_id
    else:
        return ""


def cleanup():
    """앱 종료 시 시리얼 포트 정리"""
    global ser
    with ser_lock:
        if ser and ser.is_open:
            ser.close()
            logger.info("Serial port closed")

atexit.register(cleanup)

@app.route('/')
def main():
    return render_template('main.html')

@app.route("/gateCtrl", methods=['POST'])
def fn_reqGateCtrl():
    global ser
    db = DB(**DB_CONFIG)
    data = request.get_json()
    action = data.get("action")

    # 입력 검증
    if action not in ["open", "close"]:
        logger.warning(f"잘못된 액션: {action}")
        return jsonify({"error": "잘못된 액션 (open/close만 가능)", "result": {}}), 400

    # 이벤트 타입과 RFID 설정
    event_type = "IN" if action == "open" else "OUT"
    rfid_tag = 0
    serial_action = action

    # DB 로그 삽입
    try:
        result = db.insert_parking_log(event_type)
    except Exception as e:
        logger.error(f"DB insert failed: {e}")
        return jsonify({"error": "로그 저장 실패", "result": {}}), 500

    if not result:
        logger.error("DB insert returned False")
        return jsonify({"error": "로그 저장 실패", "result": {}}), 500

    # 시리얼 전송
    with ser_lock:
        if ser is None or not ser.is_open:
            logger.error("Serial port not connected")
            return jsonify({"error": "시리얼 포트 연결 실패", "result": result}), 500
        try:
            ser.write(f"{serial_action}\n".encode('utf-8'))
            ser.flush()
            logger.info(f"Sent to Arduino: {serial_action}")
            return jsonify({"result": result}), 200
        except Exception as e:
            logger.error(f"Serial write failed: {e}")
            return jsonify({"error": "시리얼 전송 실패", "result": result}), 500


if __name__ == '__main__':
    gete_thread = threading.Thread(target=gate_control, daemon=True)
    gete_thread.start()
    rfid_thread = threading.Thread(target=read_rfid, daemon=True)
    rfid_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=False)
