class MessagePackFormat:
    def __init__(self):
        pass

    def to_bytes(self):
        raise NotImplementedError("This method should be implemented by subclasses")

    @staticmethod
    def from_bytes(data):
        raise NotImplementedError("This method should be implemented by subclasses")

    @staticmethod
    def from_bytes_with_size(data):
        first_byte = data[0]
        if first_byte == 0xc0:
            return NilFormat.from_bytes(data), 1
        elif first_byte in [0xc2, 0xc3]:
            return BoolFormat.from_bytes(data), 1
        elif (first_byte <= 0x7f) or (first_byte >= 0xe0) or first_byte in [0xcc, 0xcd, 0xce, 0xcf, 0xd0, 0xd1, 0xd2, 0xd3]:
            return IntFormat.from_bytes(data), len(IntFormat.from_bytes(data).to_bytes())
        elif first_byte in [0xca, 0xcb]:
            return FloatFormat.from_bytes(data), len(FloatFormat.from_bytes(data).to_bytes())
        elif (first_byte >= 0xa0 and first_byte <= 0xbf) or first_byte in [0xd9, 0xda, 0xdb]:
            return StrFormat.from_bytes(data), len(StrFormat.from_bytes(data).to_bytes())
        elif first_byte in [0xc4, 0xc5, 0xc6]:
            return BinFormat.from_bytes(data), len(BinFormat.from_bytes(data).to_bytes())
        elif (first_byte >= 0x90 and first_byte <= 0x9f) or first_byte in [0xdc, 0xdd]:
            return ArrayFormat.from_bytes(data), len(ArrayFormat.from_bytes(data).to_bytes())
        elif (first_byte >= 0x80 and first_byte <= 0x8f) or first_byte in [0xde, 0xdf]:
            return MapFormat.from_bytes(data), len(MapFormat.from_bytes(data).to_bytes())
        elif first_byte in [0xd4, 0xd5, 0xd6, 0xd7, 0xd8, 0xc7, 0xc8, 0xc9]:
            return ExtFormat.from_bytes(data), len(ExtFormat.from_bytes(data).to_bytes())
        raise ValueError("Unknown format")


class NilFormat(MessagePackFormat):
    def __init__(self):
        super().__init__()

    def to_bytes(self):
        return bytes([0xc0])

    @staticmethod
    def from_bytes(data):
        if data[0] == 0xc0:
            return NilFormat()
        raise ValueError("Invalid NilFormat")


class BoolFormat(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        return bytes([0xc3 if self.value else 0xc2])

    @staticmethod
    def from_bytes(data):
        if data[0] == 0xc2:
            return BoolFormat(False)
        elif data[0] == 0xc3:
            return BoolFormat(True)
        raise ValueError("Invalid BoolFormat")


class IntFormat(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        if 0 <= self.value <= 127:
            return bytes([self.value])
        elif -32 <= self.value < 0:
            return bytes([self.value & 0xff])
        elif 0 <= self.value <= 0xff:
            return bytes([0xcc, self.value])
        elif 0 <= self.value <= 0xffff:
            return bytes([0xcd]) + self.value.to_bytes(2, 'big')
        elif 0 <= self.value <= 0xffffffff:
            return bytes([0xce]) + self.value.to_bytes(4, 'big')
        elif 0 <= self.value <= 0xffffffffffffffff:
            return bytes([0xcf]) + self.value.to_bytes(8, 'big')
        elif -128 <= self.value < 0:
            return bytes([0xd0, self.value & 0xff])
        elif -32768 <= self.value < 0:
            return bytes([0xd1]) + self.value.to_bytes(2, 'big', signed=True)
        elif -2147483648 <= self.value < 0:
            return bytes([0xd2]) + self.value.to_bytes(4, 'big', signed=True)
        elif -9223372036854775808 <= self.value < 0:
            return bytes([0xd3]) + self.value.to_bytes(8, 'big', signed=True)
        else:
            raise ValueError("Integer value out of range")

    @staticmethod
    def from_bytes(data):
        first_byte = data[0]
        if first_byte <= 0x7f:  # Positive fixint
            return IntFormat(first_byte)
        elif first_byte >= 0xe0:  # Negative fixint
            return IntFormat(first_byte - 0x100)
        elif first_byte == 0xcc:  # uint 8
            return IntFormat(data[1])
        elif first_byte == 0xcd:  # uint 16
            return IntFormat(int.from_bytes(data[1:3], 'big'))
        elif first_byte == 0xce:  # uint 32
            return IntFormat(int.from_bytes(data[1:5], 'big'))
        elif first_byte == 0xcf:  # uint 64
            return IntFormat(int.from_bytes(data[1:9], 'big'))
        elif first_byte == 0xd0:  # int 8
            return IntFormat(int.from_bytes(data[1:2], 'big', signed=True))
        elif first_byte == 0xd1:  # int 16
            return IntFormat(int.from_bytes(data[1:3], 'big', signed=True))
        elif first_byte == 0xd2:  # int 32
            return IntFormat(int.from_bytes(data[1:5], 'big', signed=True))
        elif first_byte == 0xd3:  # int 64
            return IntFormat(int.from_bytes(data[1:9], 'big', signed=True))
        raise ValueError("Invalid IntFormat")


class FloatFormat(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        import struct
        if isinstance(self.value, float):
            if struct.calcsize('f') == 4:
                return bytes([0xca]) + struct.pack('>f', self.value)
            else:
                return bytes([0xcb]) + struct.pack('>d', self.value)
        else:
            raise ValueError("Value must be a float")

    @staticmethod
    def from_bytes(data):
        import struct
        first_byte = data[0]
        if first_byte == 0xca:  # float 32
            return FloatFormat(struct.unpack('>f', data[1:5])[0])
        elif first_byte == 0xcb:  # float 64
            return FloatFormat(struct.unpack('>d', data[1:9])[0])
        raise ValueError("Invalid FloatFormat")


class StrFormat(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        utf8_bytes = self.value.encode('utf-8')
        length = len(utf8_bytes)
        if length <= 31:
            return bytes([0xa0 | length]) + utf8_bytes
        elif length <= 0xff:
            return bytes([0xd9, length]) + utf8_bytes
        elif length <= 0xffff:
            return bytes([0xda]) + length.to_bytes(2, 'big') + utf8_bytes
        elif length <= 0xffffffff:
            return bytes([0xdb]) + length.to_bytes(4, 'big') + utf8_bytes
        else:
            raise ValueError("String length out of range")

    @staticmethod
    def from_bytes(data):
        first_byte = data[0]
        if first_byte >= 0xa0 and first_byte <= 0xbf:  # fixstr
            length = first_byte & 0x1f
            return StrFormat(data[1:1+length].decode('utf-8'))
        elif first_byte == 0xd9:  # str 8
            length = data[1]
            return StrFormat(data[2:2+length].decode('utf-8'))
        elif first_byte == 0xda:  # str 16
            length = int.from_bytes(data[1:3], 'big')
            return StrFormat(data[3:3+length].decode('utf-8'))
        elif first_byte == 0xdb:  # str 32
            length = int.from_bytes(data[1:5], 'big')
            return StrFormat(data[5:5+length].decode('utf-8'))
        raise ValueError("Invalid StrFormat")


class BinFormat(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        length = len(self.value)
        if length <= 0xff:
            return bytes([0xc4, length]) + self.value
        elif length <= 0xffff:
            return bytes([0xc5]) + length.to_bytes(2, 'big') + self.value
        elif length <= 0xffffffff:
            return bytes([0xc6]) + length.to_bytes(4, 'big') + self.value
        else:
            raise ValueError("Binary length out of range")

    @staticmethod
    def from_bytes(data):
        first_byte = data[0]
        if first_byte == 0xc4:  # bin 8
            length = data[1]
            return BinFormat(data[2:2+length])
        elif first_byte == 0xc5:  # bin 16
            length = int.from_bytes(data[1:3], 'big')
            return BinFormat(data[3:3+length])
        elif first_byte == 0xc6:  # bin 32
            length = int.from_bytes(data[1:5], 'big')
            return BinFormat(data[5:5+length])
        raise ValueError("Invalid BinFormat")


class ArrayFormat(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        length = len(self.value)
        if length <= 15:
            return bytes([0x90 | length]) + b''.join([item.to_bytes() for item in self.value])
        elif length <= 0xffff:
            return bytes([0xdc]) + length.to_bytes(2, 'big') + b''.join([item.to_bytes() for item in self.value])
        elif length <= 0xffffffff:
            return bytes([0xdd]) + length.to_bytes(4, 'big') + b''.join([item.to_bytes() for item in self.value])
        else:
            raise ValueError("Array length out of range")

    @staticmethod
    def from_bytes(data):
        first_byte = data[0]
        if first_byte >= 0x90 and first_byte <= 0x9f:  # fixarray
            length = first_byte & 0x0f
            elements = []
            offset = 1
            for _ in range(length):
                element, size = MessagePackFormat.from_bytes_with_size(data[offset:])
                elements.append(element)
                offset += size
            return ArrayFormat(elements)
        elif first_byte == 0xdc:  # array 16
            length = int.from_bytes(data[1:3], 'big')
            elements = []
            offset = 3
            for _ in range(length):
                element, size = MessagePackFormat.from_bytes_with_size(data[offset:])
                elements.append(element)
                offset += size
            return ArrayFormat(elements)
        elif first_byte == 0xdd:  # array 32
            length = int.from_bytes(data[1:5], 'big')
            elements = []
            offset = 5
            for _ in range(length):
                element, size = MessagePackFormat.from_bytes_with_size(data[offset:])
                elements.append(element)
                offset += size
            return ArrayFormat(elements)
        raise ValueError("Invalid ArrayFormat")


class MapFormat(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        length = len(self.value)
        if length <= 15:
            return bytes([0x80 | length]) + b''.join([key.to_bytes() + val.to_bytes() for key, val in self.value.items()])
        elif length <= 0xffff:
            return bytes([0xde]) + length.to_bytes(2, 'big') + b''.join([key.to_bytes() + val.to_bytes() for key, val in self.value.items()])
        elif length <= 0xffffffff:
            return bytes([0xdf]) + length.to_bytes(4, 'big') + b''.join([key.to_bytes() + val.to_bytes() for key, val in self.value.items()])
        else:
            raise ValueError("Map length out of range")

    @staticmethod
    def from_bytes(data):
        first_byte = data[0]
        if first_byte >= 0x80 and first_byte <= 0x8f:  # fixmap
            length = first_byte & 0x0f
            map_items = {}
            offset = 1
            for _ in range(length):
                key, key_size = MessagePackFormat.from_bytes_with_size(data[offset:])
                offset += key_size
                value, value_size = MessagePackFormat.from_bytes_with_size(data[offset:])
                offset += value_size
                map_items[key.value] = value
            return MapFormat(map_items)
        elif first_byte == 0xde:  # map 16
            length = int.from_bytes(data[1:3], 'big')
            map_items = {}
            offset = 3
            for _ in range(length):
                key, key_size = MessagePackFormat.from_bytes_with_size(data[offset:])
                offset += key_size
                value, value_size = MessagePackFormat.from_bytes_with_size(data[offset:])
                offset += value_size
                map_items[key.value] = value
            return MapFormat(map_items)
        elif first_byte == 0xdf:  # map 32
            length = int.from_bytes(data[1:5], 'big')
            map_items = {}
            offset = 5
            for _ in range(length):
                key, key_size = MessagePackFormat.from_bytes_with_size(data[offset:])
                offset += key_size
                value, value_size = MessagePackFormat.from_bytes_with_size(data[offset:])
                offset += value_size
                map_items[key.value] = value
            return MapFormat(map_items)
        raise ValueError("Invalid MapFormat")


class ExtFormat(MessagePackFormat):
    def __init__(self, type, data):
        super().__init__()
        self.type = type
        self.data = data

    def to_bytes(self):
        length = len(self.data)
        if length == 1:
            return bytes([0xd4, self.type]) + self.data
        elif length == 2:
            return bytes([0xd5, self.type]) + self.data
        elif length == 4:
            return bytes([0xd6, self.type]) + self.data
        elif length == 8:
            return bytes([0xd7, self.type]) + self.data
        elif length == 16:
            return bytes([0xd8, self.type]) + self.data
        elif length <= 0xff:
            return bytes([0xc7, length, self.type]) + self.data
        elif length <= 0xffff:
            return bytes([0xc8]) + length.to_bytes(2, 'big') + bytes([self.type]) + self.data
        elif length <= 0xffffffff:
            return bytes([0xc9]) + length.to_bytes(4, 'big') + bytes([self.type]) + self.data
        else:
            raise ValueError("Extension data length out of range")

    @staticmethod
    def from_bytes(data):
        first_byte = data[0]
        if first_byte == 0xd4:  # fixext 1
            return ExtFormat(data[1], data[2:3])
        elif first_byte == 0xd5:  # fixext 2
            return ExtFormat(data[1], data[2:4])
        elif first_byte == 0xd6:  # fixext 4
            return ExtFormat(data[1], data[2:6])
        elif first_byte == 0xd7:  # fixext 8
            return ExtFormat(data[1], data[2:10])
        elif first_byte == 0xd8:  # fixext 16
            return ExtFormat(data[1], data[2:18])
        elif first_byte == 0xc7:  # ext 8
            length = data[1]
            return ExtFormat(data[2], data[3:3+length])
        elif first_byte == 0xc8:  # ext 16
            length = int.from_bytes(data[1:3], 'big')
            return ExtFormat(data[3], data[4:4+length])
        elif first_byte == 0xc9:  # ext 32
            length = int.from_bytes(data[1:5], 'big')
            return ExtFormat(data[5], data[6:6+length])
        raise ValueError("Invalid ExtFormat")


# Example usage for serialization
nil_format = NilFormat()
print(nil_format.to_bytes())

bool_format_true = BoolFormat(True)
print(bool_format_true.to_bytes())

int_format = IntFormat(255)
print(int_format.to_bytes())

float_format = FloatFormat(3.14)
print(float_format.to_bytes())

str_format = StrFormat("Hello")
print(str_format.to_bytes())

bin_format = BinFormat(b'\x01\x02\x03')
print(bin_format.to_bytes())

array_format = ArrayFormat([IntFormat(1), IntFormat(2), IntFormat(3)])
print(array_format.to_bytes())

map_format = MapFormat({StrFormat("key"): IntFormat(1)})
print(map_format.to_bytes())

ext_format = ExtFormat(1, b'\x01\x02\x03')
print(ext_format.to_bytes())

# Example usage for deserialization
data = bytes([0xc0])
nil_format = NilFormat.from_bytes(data)
print(type(nil_format))

data = bytes([0xc3])
bool_format = BoolFormat.from_bytes(data)
print(type(bool_format), bool_format.value)

data = bytes([0xcc, 0xff])
int_format = IntFormat.from_bytes(data)
print(type(int_format), int_format.value)

data = bytes([0xca, 0x40, 0x49, 0x0f, 0xdb])
float_format = FloatFormat.from_bytes(data)
print(type(float_format), float_format.value)

data = bytes([0xa5]) + b"Hello"
str_format = StrFormat.from_bytes(data)
print(type(str_format), str_format.value)

data = bytes([0xc4, 0x03, 0x01, 0x02, 0x03])
bin_format = BinFormat.from_bytes(data)
print(type(bin_format), bin_format.value)

data = bytes([0x93, 0x01, 0x02, 0x03])
array_format = ArrayFormat.from_bytes(data)
print(type(array_format), [el.value for el in array_format.value])

data = bytes([0x81, 0xa3, 0x6b, 0x65, 0x79, 0x01])
map_format = MapFormat.from_bytes(data)
print(type(map_format), {k: v.value for k, v in map_format.value.items()})

data = bytes([0xd4, 0x01, 0x02])
ext_format = ExtFormat.from_bytes(data)
print(type(ext_format), ext_format.type, ext_format.data)
