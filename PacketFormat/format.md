## Không nén
| Field Name  | Field Type	    | Description                         |
|:------------|:---------------|:------------------------------------|
| `Length`    | `VarInt`       | Length of Packet ID + Data          |
| `Packet ID` | `VarInt`       | Tương ứng với protocol_id từ server |
| `Data`      | `Byte Array`   | Dữ liệu bên trong packet            |

## Có nén

| Trường hợp                  | Field Name               | Field Type   | Description                                                     |
| --------------------------- | ------------------------ | ------------ | --------------------------------------------------------------- |
| Luôn có                     | `Packet Length`          | `VarInt`     | Tổng độ dài kể từ `Data Length` đến hết packet                  |
| `size >= threshold` (nén)   | `Data Length`            | `VarInt`     | Độ dài của dữ liệu sau khi giải nén (gồm cả `Packet ID + Data`) |
|                             | `Compressed Packet Data` | `Byte Array` | Dữ liệu đã nén bằng zlib (sau giải nén: `Packet ID + Data`)     |
| `size < threshold` (ko nén) | `Data Length`            | `VarInt`     | Luôn là `0`, báo hiệu **không nén**                             |
|                             | `Packet ID`              | `VarInt`     | Giống như bình thường (chưa nén)                                |
|                             | `Data`                   | `Byte Array` | Dữ liệu như bình thường (không bị nén)                          |

```commandline
VarInt Packet Length (tính từ DataLen trở đi)
VarInt DataLen (chiều dài dữ liệu sau khi giải nén)
Zlib-compressed data:
   └── VarInt PacketID
       PacketData

```


Packet Length: tổng chiều dài từ Data Length trở đi.

Data Length:

-  0 → packet không bị nén

- 0 → phần sau là dữ liệu nén, cần giải nén để lấy Packet ID và Data.
