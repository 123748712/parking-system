#include "parkingGate.h"

ParkingGate::ParkingGate(uint8_t servoPin)
    : SERVO_PIN(servoPin), state(0) {
}

void ParkingGate::begin() {
    gateServo.attach(SERVO_PIN);
    gateServo.write(0);  // 초기 서보모터 값 : 0
    command = "";   // 초기값은 공백으로 설정
}

void ParkingGate::update() {
    // 시리얼 통신 기능
    if (Serial.available()) {
        char c = Serial.read();

        if (c == '\n' || c == '\r') {
            command.trim(); // 문자열 좌우 공백 제거
            if (command.length() > 0) {
                Serial.println("받은 데이터 : " + command);

                if (command == "open") {
                    gateServo.write(120);
                    Serial.println("게이트 열림");
                    gateServo.detach();
                    state = 1;
                }
                else if (command == "close") {
                    gateServo.write(0);
                    Serial.println("게이트 닫힘");
                    gateServo.detach();
                    state = 0;
                }
            }
            command = "";
        } else {
            command += c;
        }
    }

    delay(500);
}

void ParkingGate::openGate() {
    gateServo.write(120);
    state = 1;  // 서보모터 상태 1 = 문 열림
}

void ParkingGate::closeGate() {
    gateServo.write(0);
    state = 0;  // 서보모터 상태 0 = 문 닫힘
}
