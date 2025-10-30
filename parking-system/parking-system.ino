#include "parkingGate.h"
#include "RFID_LCD.h"

#define SERVO 3
RFID_LCD rfidLcd(10, 9, 0x27, 16, 2, "1", 2);  // 마지막 2가 부저 핀
ParkingGate gate(SERVO);

void setup() {
  Serial.begin(9600);
  gate.begin();
  rfidLcd.begin();
}

void loop() {
  gate.update();

  String uid;
  rfidLcd.writeCardUID(uid);

  if (uid.length() > 0 && uid != "0") {
    String jsonData = "{\"rfid_tag\":\"" + uid + "\",\"spot_id\":\"" + rfidLcd.getSpotId() + "\"}";
    Serial.println(jsonData);
  }

  if (Serial.available()) {
    String carID = Serial.readStringUntil('\n');
    carID.trim();

    Serial.print("차량번호 : ");
    Serial.println(carID);

    if (carID.length() != 0) {
      rfidLcd.displayUID(carID);

      // 차량번호 불일치 시 부저 울리기
      if (carID == "INVALID") {
        rfidLcd.buzz(500);  // 0.5초 경고음
      }
    } else {
      rfidLcd.displayUID("GET OUT");
      rfidLcd.buzz(500);
    }
  }
  delay(300);
}
