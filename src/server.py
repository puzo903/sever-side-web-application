"""TCP RPC Server for Variant 18."""
import socket
import xmlrpc.client
import logging
from app import (
    create_member, create_instruction, create_response,
    get_all_members, get_all_instructions, get_all_responses,
    get_member, get_instruction, get_response,
    edit_member, edit_instruction, edit_response, join_data
)

logging.basicConfig(filename='journal.log', level=logging.INFO)

FUNCS = {
    1: create_member, 2: create_instruction, 3: create_response,
    4: get_all_members, 5: get_all_instructions, 6: get_all_responses,
    7: get_member, 8: get_instruction, 9: get_response,
    10: edit_member, 11: edit_instruction, 12: edit_response,
    13: join_data
}

HEADER_SIZE = 5
SIZE_OFFSET_START = 0
SIZE_OFFSET_END = 4
OPCODE_INDEX = 4

RES_OPCODE_END = 2
RES_SIZE_END = 5


def process_request(conn: socket.socket) -> bool:
    """Process single RPC request over TCP."""
    header = conn.recv(HEADER_SIZE)
    if not header or len(header) < HEADER_SIZE:
        return False

    size = int.from_bytes(header[SIZE_OFFSET_START:SIZE_OFFSET_END], 'little')
    opcode = header[OPCODE_INDEX]
    body = conn.recv(size).decode('utf-8')

    args, _ = xmlrpc.client.loads(body)
    try:
        result = FUNCS[opcode](*args)
    except Exception as error_msg:
        result = str(error_msg)

    out_body = xmlrpc.client.dumps((result,), methodresponse=True)
    out_body_bytes = out_body.encode('utf-8')
    out_size = len(out_body_bytes)

    opcode_bytes = opcode.to_bytes(2, 'little')
    size_bytes = out_size.to_bytes(3, 'little')
    res_header = opcode_bytes + size_bytes

    conn.sendall(res_header + out_body_bytes)
    logging.info("Opcode: %d, Size: %d", opcode, out_size)
    return True


def run_server():
    """Run TCP server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_socket.bind(('127.0.0.1', 8000))
        tcp_socket.listen()
        while True:
            conn, _ = tcp_socket.accept()
            with conn:
                process_request(conn)


if __name__ == '__main__':
    run_server()