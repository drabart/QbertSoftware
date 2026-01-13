#pragma once

#include <cstdint>
#include <cstring>
#include <type_traits>

template<typename T>
static inline void write_le(uint8_t* dest, T value) {
    std::memcpy(dest, &value, sizeof(T));
}

template <typename T>
T read_le(const uint8_t* p) {
    using U = std::conditional_t<(sizeof(T) == 4), uint32_t,
              std::conditional_t<(sizeof(T) == 8), uint64_t,
              uint16_t>>;

    U tmp = 0;
    for (size_t i = 0; i < sizeof(T); i++) {
        tmp |= U(p[i]) << (8 * i);
    }

    T out;
    std::memcpy(&out, &tmp, sizeof(T));
    return out;
}
