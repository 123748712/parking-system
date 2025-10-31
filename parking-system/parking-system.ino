#include "parkingGate.h"
#include "RFID_LCD.h"

#define BUZZER 5
#define LED 7
#define SERVO 3
#define CCTV 6
RFID_LCD rfidLcd(10, 9, 0x27, 16, 2, "1", 2); // 마지막 2가 부저 핀
ParkingGate gate(SERVO);

#define TRIG 4
#define ECHO 8

long duration;
int distance;

bool forward = true;

Servo cctvMoter;
void setup() {
    Serial.begin(9600);
    gate.begin();
    rfidLcd.begin();
    pinMode(LED, OUTPUT);
    pinMode(BUZZER, OUTPUT);
    cctvMoter.attach(CCTV);
    cctvMoter.write(0);
    pinMode(TRIG, OUTPUT);
    pinMode(ECHO, INPUT);
}

unsigned long lastScanTime = 0;
const unsigned long scanInterval = 5000;  // 5초마다 스캔


void loop() {
    if (millis() - lastScanTime >= scanInterval) {
        runCCTVScan();
        lastScanTime = millis();
    }

    // 읽을 데이터가 존재한다면
    if(Serial.available()) {
        String input = Serial.readStringUntil('\n');
        input.trim();

        Serial.println(input);

    if (input == "open") {
            gate.openGate();
            watchCar();
        } else if (input == "close") {
            gate.closeGate();
            watchCar();
        } else if (input.length() == 0) {
            rfidLcd.displayUID("GET OUT");
            rfidLcd.buzz(500);
            delay(100);
        } else {
            rfidLcd.displayUID(input);
            if (input == "INVALID") {
                rfidLcd.buzz(500);
            }
        }
        return;  
    }

    // RFID 카드 인식 처리
    String uid;
    rfidLcd.writeCardUID(uid);
    if (uid.length() > 0 && uid != "0") {
        String jsonData = "{\"rfid_tag\":\"" + uid + "\",\"spot_id\":\"" + rfidLcd.getSpotId() + "\"}";
        Serial.println(jsonData);
    }

    delay(300);
}

void watchCar() {
    for (int i = 0; i < 10; i++) {
        digitalWrite(LED, HIGH);
        tone(BUZZER, 262);
        delay(200);
        digitalWrite(LED, LOW);
        noTone(BUZZER);
        delay(200);
    }
}

void runCCTVScan() {
  int startAngle = forward ? 0 : 180;
  int endAngle = forward ? 180 : 0;
  int step = forward ? 2 : -2;  // 웹과 동일한 2도 단위

  for (int angle = startAngle; forward ? (angle <= endAngle) : (angle >= endAngle); angle += step) {
    cctvMoter.write(angle);
    delay(100);  // 웹과 동일한 100ms 간격

    int dist = getDistance();
    Serial.print(angle);
    Serial.print(",");
    Serial.println(dist == -1 ? 0 : dist);
  }
  forward = !forward;
}

int getDistance() {
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  // 최대 30ms 대기 (약 5m 거리까지 측정 가능)
  long duration = pulseIn(ECHO, HIGH, 30000);

  if (duration == 0) {
    // Serial.println("거리 측정 실패: ECHO 신호 없음");
    return -1;
  }

  int distance = duration * 0.034 / 2;  // cm 단위
  if (distance > 400) return -1;       // 비현실적 거리는 -1 처리
  return distance;
}