def encodeVarint(value: int) -> bytes:
    result = bytearray()
    while True:
        temp = value & 0x7F
        value >>= 7
        if value != 0:
            temp |= 0x80
        result.append(temp)
        if value == 0:
            break
    return bytes(result)
