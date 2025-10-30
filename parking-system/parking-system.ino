#include "parkingGate.h"
#include "RFID_LCD.h"

#define SERVO 3
RFID_LCD rfidLcd(10, 9, 0x27, 16, 2, "1", 2); // 마지막 2가 부저 핀
ParkingGate gate(SERVO);

void setup() {
    Serial.begin(9600);
    gate.begin();
    rfidLcd.begin();
}

void loop() {
    // 읽을 데이터가 존재한다면
    if(Serial.available()) {
        String input = Serial.readStringUntil('\n');
        input.trim();

        Serial.println(input);

    if (input == "open") {
            gate.openGate();
        } else if (input == "close") {
            gate.closeGate();
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
