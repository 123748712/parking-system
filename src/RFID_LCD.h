#ifndef RFID_LCD_H
#define RFID_LCD_H

#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Arduino.h>

class RFID_LCD {
public:
    // 생성자: RFID 핀과 LCD 주소, LCD 크기 동적 설정
    RFID_LCD(uint8_t ssPin, uint8_t rstPin, uint8_t lcdAddr = 0x27, uint8_t lcdCols = 16, uint8_t lcdRows = 2, String spot_id = "", uint8_t buzzerPin = 2);

    void begin();                       // RFID, LCD 초기화
    bool readCardUID(String &uidStr);   // 카드 UID 읽기
    String writeCardUID(String &uidStr); // 카드 UID 읽기 & 반환
    void displayUID(const String &uidStr); // LCD에 UID 표시
    String getSpotId();

    void buzz(int duration_ms);             // 부저 울리기

private:
    MFRC522 *mfrc;
    LiquidCrystal_I2C *lcd;

    uint8_t _ssPin;
    uint8_t _rstPin;
    uint8_t _lcdAddr;
    uint8_t _lcdCols;
    uint8_t _lcdRows;
    String _spot_id;

// 추가
    uint8_t _buzzerPin; 

};

#endif

