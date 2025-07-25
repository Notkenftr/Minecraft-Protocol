from encodeVarint import encodeVarint
def encodeString(string):
    string_bytes = string.encode('utf-8')
    return encodeVarint(len(string_bytes)) + string_bytes
