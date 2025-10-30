#ifndef PARKING_GATE_H
#define PARKING_GATE_H

#include <Servo.h>
#include <Arduino.h>

class ParkingGate {
public:
    ParkingGate(uint8_t servoPin);
    void begin();
    void update();

private:
    void openGate();
    void closeGate();

    Servo gateServo;
    uint8_t SERVO_PIN;
    int state;  // 0 = closed, 1 = open
    String command;
};

#endif
