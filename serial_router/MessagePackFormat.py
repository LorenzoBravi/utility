from collections import OrderedDict
import struct

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
        elif (first_byte <= 0x7f) or (first_byte >= 0xe0):
            return FixIntFormat.from_bytes(data), len(FixIntFormat.from_bytes(data).to_bytes())
        elif first_byte == 0xcc:
            return UInt8Format.from_bytes(data), 2
        elif first_byte == 0xcd:
            return UInt16Format.from_bytes(data), 3
        elif first_byte == 0xce:
            return UInt32Format.from_bytes(data), 5
        elif first_byte == 0xcf:
            return UInt64Format.from_bytes(data), 9
        elif first_byte == 0xd0:
            return Int8Format.from_bytes(data), 2
        elif first_byte == 0xd1:
            return Int16Format.from_bytes(data), 3
        elif first_byte == 0xd2:
            return Int32Format.from_bytes(data), 5
        elif first_byte == 0xd3:
            return Int64Format.from_bytes(data), 9
        elif first_byte == 0xca:
            return Float32Format.from_bytes(data), 5
        elif first_byte == 0xcb:
            return Float64Format.from_bytes(data), 9
        elif first_byte >= 0xa0 and first_byte <= 0xbf:
            return FixStrFormat.from_bytes(data), (first_byte & 0x1f) + 1
        elif first_byte == 0xd9:
            length = data[1]
            return Str8Format.from_bytes(data), length + 2
        elif first_byte == 0xda:
            length = int.from_bytes(data[1:3], 'big')
            return Str16Format.from_bytes(data), length + 3
        elif first_byte == 0xdb:
            length = int.from_bytes(data[1:5], 'big')
            return Str32Format.from_bytes(data), length + 5
        elif first_byte == 0xc4:
            length = data[1]
            return Bin8Format.from_bytes(data), length + 2
        elif first_byte == 0xc5:
            length = int.from_bytes(data[1:3], 'big')
            return Bin16Format.from_bytes(data), length + 3
        elif first_byte == 0xc6:
            length = int.from_bytes(data[1:5], 'big')
            return Bin32Format.from_bytes(data), length + 5
        elif first_byte >= 0x90 and first_byte <= 0x9f:
            length = first_byte & 0x0f
            return FixArrayFormat.from_bytes(data), length + 1
        elif first_byte == 0xdc:
            length = int.from_bytes(data[1:3], 'big')
            return Array16Format.from_bytes(data), length + 3
        elif first_byte == 0xdd:
            length = int.from_bytes(data[1:5], 'big')
            return Array32Format.from_bytes(data), length + 5
        elif first_byte >= 0x80 and first_byte <= 0x8f:
            length = first_byte & 0x0f
            return FixMapFormat.from_bytes(data), length * 2 + 1
        elif first_byte == 0xde:
            length = int.from_bytes(data[1:3], 'big')
            return Map16Format.from_bytes(data), length * 2 + 3
        elif first_byte == 0xdf:
            length = int.from_bytes(data[1:5], 'big')
            return Map32Format.from_bytes(data), length * 2 + 5
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

class FixIntFormat(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        if 0 <= self.value <= 127:
            return bytes([self.value])
        elif -32 <= self.value < 0:
            return bytes([self.value & 0xff])
        else:
            raise ValueError("FixInt value out of range")

    @staticmethod
    def from_bytes(data):
        first_byte = data[0]
        if first_byte <= 0x7f:  # Positive fixint
            return FixIntFormat(first_byte)
        elif first_byte >= 0xe0:  # Negative fixint
            return FixIntFormat(first_byte - 0x100)
        raise ValueError("Invalid FixIntFormat")

class UInt8Format(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        return bytes([0xcc, self.value])

    @staticmethod
    def from_bytes(data):
        return UInt8Format(data[1])

class UInt16Format(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        return bytes([0xcd]) + self.value.to_bytes(2, 'big')

    @staticmethod
    def from_bytes(data):
        return UInt16Format(int.from_bytes(data[1:3], 'big'))

class UInt32Format(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        return bytes([0xce]) + self.value.to_bytes(4, 'big')

    @staticmethod
    def from_bytes(data):
        return UInt32Format(int.from_bytes(data[1:5], 'big'))

class UInt64Format(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        return bytes([0xcf]) + self.value.to_bytes(8, 'big')

    @staticmethod
    def from_bytes(data):
        return UInt64Format(int.from_bytes(data[1:9], 'big'))

class Int8Format(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        return bytes([0xd0, self.value & 0xff])

    @staticmethod
    def from_bytes(data):
        return Int8Format(int.from_bytes(data[1:2], 'big', signed=True))

class Int16Format(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        return bytes([0xd1]) + self.value.to_bytes(2, 'big', signed=True)

    @staticmethod
    def from_bytes(data):
        return Int16Format(int.from_bytes(data[1:3], 'big', signed=True))

class Int32Format(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        return bytes([0xd2]) + self.value.to_bytes(4, 'big', signed=True)

    @staticmethod
    def from_bytes(data):
        return Int32Format(int.from_bytes(data[1:5], 'big', signed=True))

class Int64Format(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        return bytes([0xd3]) + self.value.to_bytes(8, 'big', signed=True)

    @staticmethod
    def from_bytes(data):
        return Int64Format(int.from_bytes(data[1:9], 'big', signed=True))

class Float32Format(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        return bytes([0xca]) + struct.pack('>f', self.value)

    @staticmethod
    def from_bytes(data):
        return Float32Format(struct.unpack('>f', data[1:5])[0])

class Float64Format(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        return bytes([0xcb]) + struct.pack('>d', self.value)

    @staticmethod
    def from_bytes(data):
        return Float64Format(struct.unpack('>d', data[1:9])[0])

class FixStrFormat(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        utf8_bytes = self.value.encode('utf-8')
        length = len(utf8_bytes)
        if length > 31:
            raise ValueError("FixStr length out of range")
        return bytes([0xa0 | length]) + utf8_bytes

    @staticmethod
    def from_bytes(data):
        length = data[0] & 0x1f
        return FixStrFormat(data[1:1+length].decode('utf-8'))

class Str8Format(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        utf8_bytes = self.value.encode('utf-8')
        length = len(utf8_bytes)
        if length > 0xff:
            raise ValueError("Str8 length out of range")
        return bytes([0xd9, length]) + utf8_bytes

    @staticmethod
    def from_bytes(data):
        length = data[1]
        return Str8Format(data[2:2+length].decode('utf-8'))

class Str16Format(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        utf8_bytes = self.value.encode('utf-8')
        length = len(utf8_bytes)
        if length > 0xffff:
            raise ValueError("Str16 length out of range")
        return bytes([0xda]) + length.to_bytes(2, 'big') + utf8_bytes

    @staticmethod
    def from_bytes(data):
        length = int.from_bytes(data[1:3], 'big')
        return Str16Format(data[3:3+length].decode('utf-8'))

class Str32Format(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        utf8_bytes = self.value.encode('utf-8')
        length = len(utf8_bytes)
        if length > 0xffffffff:
            raise ValueError("Str32 length out of range")
        return bytes([0xdb]) + length.to_bytes(4, 'big') + utf8_bytes

    @staticmethod
    def from_bytes(data):
        length = int.from_bytes(data[1:5], 'big')
        return Str32Format(data[5:5+length].decode('utf-8'))

class Bin8Format(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        length = len(self.value)
        if length > 0xff:
            raise ValueError("Bin8 length out of range")
        return bytes([0xc4, length]) + self.value

    @staticmethod
    def from_bytes(data):
        length = data[1]
        return Bin8Format(data[2:2+length])

class Bin16Format(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        length = len(self.value)
        if length > 0xffff:
            raise ValueError("Bin16 length out of range")
        return bytes([0xc5]) + length.to_bytes(2, 'big') + self.value

    @staticmethod
    def from_bytes(data):
        length = int.from_bytes(data[1:3], 'big')
        return Bin16Format(data[3:3+length])

class Bin32Format(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        length = len(self.value)
        if length > 0xffffffff:
            raise ValueError("Bin32 length out of range")
        return bytes([0xc6]) + length.to_bytes(4, 'big') + self.value

    @staticmethod
    def from_bytes(data):
        length = int.from_bytes(data[1:5], 'big')
        return Bin32Format(data[5:5+length])

class FixArrayFormat(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        length = len(self.value)
        if length > 15:
            raise ValueError("FixArray length out of range")
        return bytes([0x90 | length]) + b''.join([item.to_bytes() for item in self.value])

    @staticmethod
    def from_bytes(data):
        length = data[0] & 0x0f
        elements = []
        offset = 1
        for _ in range(length):
            element, size = MessagePackFormat.from_bytes_with_size(data[offset:])
            elements.append(element)
            offset += size
        return FixArrayFormat(elements)

class Array16Format(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        length = len(self.value)
        if length > 0xffff:
            raise ValueError("Array16 length out of range")
        return bytes([0xdc]) + length.to_bytes(2, 'big') + b''.join([item.to_bytes() for item in self.value])

    @staticmethod
    def from_bytes(data):
        length = int.from_bytes(data[1:3], 'big')
        elements = []
        offset = 3
        for _ in range(length):
            element, size = MessagePackFormat.from_bytes_with_size(data[offset:])
            elements.append(element)
            offset += size
        return Array16Format(elements)

class Array32Format(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        length = len(self.value)
        if length > 0xffffffff:
            raise ValueError("Array32 length out of range")
        return bytes([0xdd]) + length.to_bytes(4, 'big') + b''.join([item.to_bytes() for item in self.value])

    @staticmethod
    def from_bytes(data):
        length = int.from_bytes(data[1:5], 'big')
        elements = []
        offset = 5
        for _ in range(length):
            element, size = MessagePackFormat.from_bytes_with_size(data[offset:])
            elements.append(element)
            offset += size
        return Array32Format(elements)

class FixMapFormat(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        length = len(self.value)
        if length > 15:
            raise ValueError("FixMap length out of range")
        return bytes([0x80 | length]) + b''.join([key.to_bytes() + val.to_bytes() for key, val in self.value.items()])

    @staticmethod
    def from_bytes(data):
        length = data[0] & 0x0f
        map_items = OrderedDict()
        offset = 1
        for _ in range(length):
            key, key_size = MessagePackFormat.from_bytes_with_size(data[offset:])
            offset += key_size
            value, value_size = MessagePackFormat.from_bytes_with_size(data[offset:])
            offset += value_size
            map_items[key.value] = value
        return FixMapFormat(map_items)

class Map16Format(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        length = len(self.value)
        if length > 0xffff:
            raise ValueError("Map16 length out of range")
        return bytes([0xde]) + length.to_bytes(2, 'big') + b''.join([key.to_bytes() + val.to_bytes() for key, val in self.value.items()])

    @staticmethod
    def from_bytes(data):
        length = int.from_bytes(data[1:3], 'big')
        map_items = OrderedDict()
        offset = 3
        for _ in range(length):
            key, key_size = MessagePackFormat.from_bytes_with_size(data[offset:])
            offset += key_size
            value, value_size = MessagePackFormat.from_bytes_with_size(data[offset:])
            offset += value_size
            map_items[key.value] = value
        return Map16Format(map_items)

class Map32Format(MessagePackFormat):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def to_bytes(self):
        length = len(self.value)
        if length > 0xffffffff:
            raise ValueError("Map32 length out of range")
        return bytes([0xdf]) + length.to_bytes(4, 'big') + b''.join([key.to_bytes() + val.to_bytes() for key, val in self.value.items()])

    @staticmethod
    def from_bytes(data):
        length = int.from_bytes(data[1:5], 'big')
        map_items = OrderedDict()
        offset = 5
        for _ in range(length):
            key, key_size = MessagePackFormat.from_bytes_with_size(data[offset:])
            offset += key_size
            value, value_size = MessagePackFormat.from_bytes_with_size(data[offset:])
            offset += value_size
            map_items[key.value] = value
        return Map32Format(map_items)

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

fixint_format = FixIntFormat(127)
print(fixint_format.to_bytes())

uint8_format = UInt8Format(255)
print(uint8_format.to_bytes())

uint16_format = UInt16Format(65535)
print(uint16_format.to_bytes())

uint32_format = UInt32Format(4294967295)
print(uint32_format.to_bytes())

uint64_format = UInt64Format(18446744073709551615)
print(uint64_format.to_bytes())

int8_format = Int8Format(-128)
print(int8_format.to_bytes())

int16_format = Int16Format(-32768)
print(int16_format.to_bytes())

int32_format = Int32Format(-2147483648)
print(int32_format.to_bytes())

int64_format = Int64Format(-9223372036854775808)
print(int64_format.to_bytes())

float32_format = Float32Format(3.14)
print(float32_format.to_bytes())

float64_format = Float64Format(3.14)
print(float64_format.to_bytes())

fixstr_format = FixStrFormat("Hello")
print(fixstr_format.to_bytes())

str8_format = Str8Format("Hello" * 10)
print(str8_format.to_bytes())

str16_format = Str16Format("Hello" * 100)
print(str16_format.to_bytes())

str32_format = Str32Format("Hello" * 1000)
print(str32_format.to_bytes())

bin8_format = Bin8Format(b'\x01\x02\x03')
print(bin8_format.to_bytes())

bin16_format = Bin16Format(b'\x01\x02' * 100)
print(bin16_format.to_bytes())

bin32_format = Bin32Format(b'\x01\x02' * 1000)
print(bin32_format.to_bytes())

fixarray_format = FixArrayFormat([FixIntFormat(1), FixIntFormat(2), FixIntFormat(3)])
print(fixarray_format.to_bytes())

array16_format = Array16Format([FixIntFormat(i) for i in range(20)])
print(array16_format.to_bytes())

array32_format = Array32Format([FixIntFormat(i) for i in range(30000)])
print(array32_format.to_bytes())

fixmap_format = FixMapFormat(OrderedDict({FixStrFormat("key"): FixIntFormat(1)}))
print(fixmap_format.to_bytes())

map16_format = Map16Format(OrderedDict({FixStrFormat(f"key{i}"): FixIntFormat(i) for i in range(20)}))
print(map16_format.to_bytes())

map32_format = Map32Format(OrderedDict({FixStrFormat(f"key{i}"): FixIntFormat(i) for i in range(30000)}))
print(map32_format.to_bytes())

ext_format = ExtFormat(1, b'\x01\x02\x03')
print(ext_format.to_bytes())

# Example usage for deserialization
data = bytes([0xc0])
nil_format = NilFormat.from_bytes(data)
print(type(nil_format))

data = bytes([0xc3])
bool_format = BoolFormat.from_bytes(data)
print(type(bool_format), bool_format.value)

data = bytes([0x7f])
fixint_format = FixIntFormat.from_bytes(data)
print(type(fixint_format), fixint_format.value)

data = bytes([0xcc, 0xff])
uint8_format = UInt8Format.from_bytes(data)
print(type(uint8_format), uint8_format.value)

data = bytes([0xcd, 0xff, 0xff])
uint16_format = UInt16Format.from_bytes(data)
print(type(uint16_format), uint16_format.value)

data = bytes([0xce, 0xff, 0xff, 0xff, 0xff])
uint32_format = UInt32Format.from_bytes(data)
print(type(uint32_format), uint32_format.value)

data = bytes([0xcf, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
uint64_format = UInt64Format.from_bytes(data)
print(type(uint64_format), uint64_format.value)

data = bytes([0xd0, 0x80])
int8_format = Int8Format.from_bytes(data)
print(type(int8_format), int8_format.value)

data = bytes([0xd1, 0x80, 0x00])
int16_format = Int16Format.from_bytes(data)
print(type(int16_format), int16_format.value)

data = bytes([0xd2, 0x80, 0x00, 0x00, 0x00])
int32_format = Int32Format.from_bytes(data)
print(type(int32_format), int32_format.value)

data = bytes([0xd3, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
int64_format = Int64Format.from_bytes(data)
print(type(int64_format), int64_format.value)

data = bytes([0xca, 0x40, 0x49, 0x0f, 0xdb])
float32_format = Float32Format.from_bytes(data)
print(type(float32_format), float32_format.value)

data = bytes([0xcb, 0x40, 0x09, 0x21, 0xfb, 0x54, 0x44, 0x2d, 0x18])
float64_format = Float64Format.from_bytes(data)
print(type(float64_format), float64_format.value)

data = bytes([0xa5]) + b"Hello"
fixstr_format = FixStrFormat.from_bytes(data)
print(type(fixstr_format), fixstr_format.value)

data = bytes([0xd9, 0x1e]) + b"Hello" * 6
str8_format = Str8Format.from_bytes(data)
print(type(str8_format), str8_format.value)

data = bytes([0xda, 0x01, 0xf4]) + b"Hello" * 100
str16_format = Str16Format.from_bytes(data)
print(type(str16_format), str16_format.value)

data = bytes([0xdb, 0x00, 0x00, 0x0c, 0x80]) + b"Hello" * 1000
str32_format = Str32Format.from_bytes(data)
print(type(str32_format), str32_format.value)

data = bytes([0xc4, 0x03, 0x01, 0x02, 0x03])
bin8_format = Bin8Format.from_bytes(data)
print(type(bin8_format), bin8_format.value)

data = bytes([0xc5, 0x00, 0x0a]) + b'\x01\x02' * 5
bin16_format = Bin16Format.from_bytes(data)
print(type(bin16_format), bin16_format.value)

data = bytes([0xc6, 0x00, 0x00, 0x07, 0xd0]) + b'\x01\x02' * 500
bin32_format = Bin32Format.from_bytes(data)
print(type(bin32_format), bin32_format.value)

data = bytes([0x93, 0x01, 0x02, 0x03])
fixarray_format = FixArrayFormat.from_bytes(data)
print(type(fixarray_format), [el.value for el in fixarray_format.value])

data = bytes([0xdc, 0x00, 0x14]) + bytes(range(20))
array16_format = Array16Format.from_bytes(data)
print(type(array16_format), [el.value for el in array16_format.value])

data = bytes([0xdd, 0x00, 0x00, 0x75, 0x30]) + bytes(range(30000))
array32_format = Array32Format.from_bytes(data)
print(type(array32_format), [el.value for el in array32_format.value])

data = bytes([0x81, 0xa3, 0x6b, 0x65, 0x79, 0x01])
fixmap_format = FixMapFormat.from_bytes(data)
print(type(fixmap_format), {k: v.value for k, v in fixmap_format.value.items()})

data = bytes([0xde, 0x00, 0x14]) + b''.join([bytes([0xa4]) + f'key{i}'.encode() + bytes([i]) for i in range(20)])
map16_format = Map16Format.from_bytes(data)
print(type(map16_format), {k: v.value for k, v in map16_format.value.items()})

data = bytes([0xdf, 0x00, 0x00, 0x75, 0x30]) + b''.join([bytes([0xa4]) + f'key{i}'.encode() + bytes([i]) for i in range(30000)])
map32_format = Map32Format.from_bytes(data)
print(type(map32_format), {k: v.value for k, v in map32_format.value.items()})

data = bytes([0xd4, 0x01, 0x02])
ext_format = ExtFormat.from_bytes(data)
print(type(ext_format), ext_format.type, ext_format.data)
