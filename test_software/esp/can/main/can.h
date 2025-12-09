#ifndef CAN_H
#define CAN_H

#define CMD_MASK 0b11111

typedef enum {
    HeartBeat = 1,
    SetPosAxe,
    SetGripState,
    GetPosAxe,
    GetGripState,
    GetError,
    GripDone,
    NUM_CAN_CMD,
} CanCmd;

typedef enum {
    None = 0,
    IncorrectDLC = -1,
    IncorrectArgs = -2,
    NoRTR = -3,
    UnknownErr = -4,
} CanErr;

#endif /* CAN_H */
