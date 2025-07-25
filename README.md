# Minecraft Java Protocol: Handshake → Login → Config → Play

> Đây là mô tả quy trình kết nối giữa client Minecraft và server qua giao thức TCP — theo đúng chuẩn protocol Minecraft từ phiên bản 1.7 đến 1.20+.

---

## 1. Tổng quan các giai đoạn (States)

Minecraft Protocol chia thành 6 **protocol states** chính:
```commandline
0 → Handshaking
2 → Login Start
3 → Set compress
4 → Login success
5 → Config
6 → Play
```


Client bắt đầu từ `Handshaking`, sau đó tùy `Next State` sẽ chuyển sang `Status` (nếu ping) hoặc `Login` → `Play`.

---

## 2. Giai đoạn 1: Handshake

Client gửi **Handshake packet** đến server, gồm:

| Field         | Type     | Description                     |
|---------------|----------|---------------------------------|
| Protocol Ver. | VarInt   | Phiên bản protocol              |
| Server Addr   | String   | IP hoặc hostname                |
| Server Port   | Unsigned Short | Port kết nối (default 25565)   |
| Next State    | VarInt   | `1` = Status, `2` = Login       |

**Ví dụ hex (với tên miền `localhost`, port `25565`)**:

```commandline
[Handshake Packet] → ID: 0x00
Protocol Version: 763
Server Address: localhost
Server Port: 25565
Next State: 2 (Login)
```

```python

from encode import encodeString, encodeVarint
import struct

ProtocolVersion = 765  # 1.20.4

address = 'localhost'
port = 25565

handshake = (
        encodeVarint(ProtocolVersion) +
        encodeString(address) +
        struct.pack('>H', port) +
        encodeVarint(2)
)
# handshake packet id là 0x00
handshake = encodeVarint(0x00) + handshake
handshake = encodeVarint(len(handshake)) + handshake

```

---

## 3. Giai đoạn 2: Login

Ngay sau handshake nếu `Next State == 2`, client bước vào phase login:

### 3.1. Client → Server: `Login Start`

| Field    | Type   | Description             |
|----------|--------|-------------------------|
| Name     | String | Tên người chơi (nick)   |
| UUID     | Uuid   | Chỉ dùng trong offline mode |

```commandline
[Login Start] → ID: 0x00
Name: ""
Uuid: ""
```

```python
import uuid
from encode import encodeString, encodeVarint

name = 'kenftr'

Uuid = uuid.uuid3(uuid.NAMESPACE_DNS, f"OfflinePlayer:{name}")
Uuid = Uuid.bytes
login = encodeString(name) + Uuid

# packet login cũng có id là 0x00
login = encodeVarint(0x00) + login
login = encodeVarint(len(login)) + login
```
---

### (Tuỳ server cấu hình):

- Nếu **server Online Mode (mojang auth)**:
  - Server gửi `Encryption Request` (chứa public key và verify token).
  - Client phản hồi `Encryption Response`.
  - Server xác thực UUID với Mojang, rồi gửi `Login Success`.

- Nếu **Offline Mode** (không auth mojang):
  - Bỏ qua phần mã hoá, server gửi `Login Success` luôn.

---

### 3.2. Server → Client: `Set comnpress` `Login Success`

### Set compress
| Field       | Kiểu Dữ Liệu | Mô tả                                                                                                 |
|-------------| ------------ | ----------------------------------------------------------------------------------------------------- |
| `Packet ID` | `VarInt`     | `0x03` (trong phase `Login`)                                                                          |
| `Threshold` | `VarInt`     | Ngưỡng kích thước để nén. Nếu một packet có **length ≥ threshold**, packet đó sẽ được **compressed**. |

Gói Set Compression cho client biết: từ giờ trở đi, packet nào có chiều dài ≥ threshold thì phải nén bằng zlib. Nếu nhỏ hơn, gửi nguyên không nén, nhưng vẫn cần thêm field Uncompressed Length.

```commandline
Packet ID: 0x03
Threshold: 256
```
### Login Success

| Field       | Type   | Description           |
|-------------|--------|-----------------------|
| UUID        | String | UUID người chơi       |
| Username    | String | Tên người chơi xác nhận |

Sau đó, state chuyển từ `Login` → `config`.


### 3.3 Client → Server: ` Login Acknowledged`

Chỉ xuất hiện từ Minecraft 1.20.2 trở lên, đây là gói tin xác nhận cuối cùng từ phía Client trước khi bước sang Configuration Phase hoặc trực tiếp vào Play Phase (tùy phiên bản và server).

| Field              | Kiểu dữ liệu | Mô tả                            |
|--------------------| ------------ | -------------------------------- |
| *(Không có field)* | —            | Đây là packet trống (no payload) |

```commandline
Packet ID: 0x03 (trong state Login)

Direction: Client → Server

Payload: None (chỉ chứa Packet ID)
```

---

## 4: Configuration (từ 1.19.3+)

Phiên bản 1.19.3 trở đi, Mojang bổ sung phase `Configuration` nằm giữa `Login` và `Play`.

**Mục đích:** cho phép client load:
- Registry codec
- Dimension codec
- Custom data pack
- Chat/command settings

Một số packet config tiêu biểu:
- `ServerData`
- `RegistryData`
- `FeatureFlags`
- `FinishConfiguration` → kết thúc phase.

---


## Tóm tắt luồng kết nối

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server

    C->>S: Handshake
    C->>S: Login Start
    S->>C: Login Success
    C->>S: Login Acknowledged ( 1.20.2 +)
    S->>C: Registry / Config (nếu có)
    C->>S: Finish Config
    S->>C: Join Game
