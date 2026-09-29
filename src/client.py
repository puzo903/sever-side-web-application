import socket
import xmlrpc.client

HEADER_SIZE = 5


def recvall(sock: socket.socket, n: int):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            raise ConnectionError("Разрыв соединения")
        data.extend(packet)
    return bytes(data)


class RPCClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        self.addr = (host, port)

    def _call(self, opcode: int, *args) -> dict:
        body = xmlrpc.client.dumps(args, methodname="call")
        body_bytes = body.encode("utf-8")
        size = len(body_bytes)

        size_bytes = size.to_bytes(4, "little")
        op_bytes = opcode.to_bytes(1, "little")
        header = size_bytes + op_bytes

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
            tcp_sock.connect(self.addr)
            tcp_sock.sendall(header + body_bytes)

            res_header = recvall(tcp_sock, HEADER_SIZE)
            res_size = int.from_bytes(res_header[2:5], "little")
            res_body_bytes = recvall(tcp_sock, res_size)

            res_body = res_body_bytes.decode("utf-8")
            return xmlrpc.client.loads(res_body)[0][0]

    def create_member(self, ip: str, ua: str):
        return self._call(1, ip, ua)

    def create_instruction(self, arg: str, mem: int, desc: str, st: str):
        return self._call(2, arg, mem, desc, st)

    def create_response(self, *args):
        return self._call(3, *args)

    def get_all_members(self):
        return self._call(4)

    def get_all_instructions(self):
        return self._call(5)

    def get_all_responses(self):
        return self._call(6)

    def get_member(self, uid: int):
        return self._call(7, uid)

    def get_instruction(self, uid: int):
        return self._call(8, uid)

    def get_response(self, uid: int):
        return self._call(9, uid)

    def edit_member(self, *args):
        return self._call(10, *args)

    def edit_instruction(self, *args):
        return self._call(11, *args)

    def edit_response(self, *args):
        return self._call(12, *args)

    def join_data(self):
        return self._call(13)
