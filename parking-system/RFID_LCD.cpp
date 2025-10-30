#include "RFID_LCD.h"
// 생성자
RFID_LCD::RFID_LCD(uint8_t ssPin, uint8_t rstPin, uint8_t lcdAddr, uint8_t lcdCols, uint8_t lcdRows, String spot_id, uint8_t buzzerPin)
: _ssPin(ssPin), _rstPin(rstPin), _lcdAddr(lcdAddr), _lcdCols(lcdCols), _lcdRows(lcdRows), _spot_id(spot_id), _buzzerPin(buzzerPin) {
    mfrc = new MFRC522(_ssPin, _rstPin);
    lcd  = new LiquidCrystal_I2C(_lcdAddr, _lcdCols, _lcdRows);
}

// 초기화
void RFID_LCD::begin() {
    SPI.begin();
    mfrc->PCD_Init();
    lcd->init();
    lcd->backlight();
    lcd->setCursor(0, 0);
    lcd->print("RFID Ready");

    pinMode(_buzzerPin, OUTPUT); // 부저 핀 초기화
}

// 카드 UID 읽기 (bool 반환)
bool RFID_LCD::readCardUID(String &uidStr) {
    if (!mfrc->PICC_IsNewCardPresent() || !mfrc->PICC_ReadCardSerial())
        return false;

    uidStr = "";
    for (byte i = 0; i < 4; i++) {
        uidStr += String(mfrc->uid.uidByte[i]);
        if (i < 3) uidStr += "-";
    }
    return true;
}

// 카드 UID 읽기 & 문자열 반환
String RFID_LCD::writeCardUID(String &uidStr) {
    if (!mfrc->PICC_IsNewCardPresent() || !mfrc->PICC_ReadCardSerial())
        return "0";

    uidStr = "";
    for (byte i = 0; i < 4; i++) {
        uidStr += String(mfrc->uid.uidByte[i]);
        if (i < 3) uidStr += "-";
    }

    return uidStr;
}

// LCD에 UID 출력
void RFID_LCD::displayUID(const String &uidStr) {
    lcd->clear();
    lcd->setCursor(0, 0);
    lcd->print("Card UID:");
    lcd->setCursor(0, 1);
    lcd->print(uidStr);
}

String RFID_LCD::getSpotId() {

    return _spot_id;
}


// 부저 울리기
void RFID_LCD::buzz(int duration_ms) {
    digitalWrite(_buzzerPin, HIGH);
    delay(duration_ms);
    digitalWrite(_buzzerPin, LOW);
}

