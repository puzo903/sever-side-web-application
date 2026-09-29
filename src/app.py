import datetime

members = []
instructions = []
responses = []

OFFSET_MINUTES = 9
SECONDS_IN_MINUTE = 60


def get_next_id(table: list) -> int:
    if not table:
        return 0
    return max(table, key=lambda e: e["id"])["id"] + 1


def create_entity(entity: dict, table: list) -> dict:
    time_int = int(datetime.datetime.now().timestamp())
    entity["created"] = time_int
    entity["id"] = get_next_id(table)
    table.append(entity)
    return entity


def create_member(ip: str, user_agent: str) -> dict:
    return create_entity({"ip": ip, "user_agent": user_agent}, members)


def create_instruction(arg: str, mem: int, desc: str, st: str) -> dict:
    return create_entity(
        {"argument": arg, "member": mem, "description": desc, "state": st},
        instructions,
    )


def create_response(
    res: str, st: str, err: str, inst: int, ch: int, dur: int
) -> dict:
    return create_entity(
        {
            "response": res,
            "state": st,
            "error": err,
            "instruction": inst,
            "cache_hit": ch,
            "duration": dur,
        },
        responses,
    )


def get_all_members() -> list:
    return members


def get_all_instructions() -> list:
    return instructions


def get_all_responses() -> list:
    return responses


def get_by_id(uid: int, table: list) -> dict:
    for row in table:
        if row["id"] == uid:
            return row
    return {}


def get_member(uid: int) -> dict:
    return get_by_id(uid, members)


def get_instruction(uid: int) -> dict:
    return get_by_id(uid, instructions)


def get_response(uid: int) -> dict:
    return get_by_id(uid, responses)


def edit_member(uid: int, ip: str, user_agent: str) -> dict:
    member = get_member(uid)
    if member:
        member["ip"] = ip
        member["user_agent"] = user_agent
    return member


def edit_instruction(uid: int, arg: str, mem: int, desc: str, st: str) -> dict:
    inst = get_instruction(uid)
    if inst:
        inst["argument"] = arg
        inst["member"] = mem
        inst["description"] = desc
        inst["state"] = st
    return inst


def edit_response(
    uid: int, res: str, st: str, err: str, inst: int, ch: int, dur: int
) -> dict:
    response_item = get_response(uid)
    if response_item:
        response_item["response"] = res
        response_item["state"] = st
        response_item["error"] = err
        response_item["instruction"] = inst
        response_item["cache_hit"] = ch
        response_item["duration"] = dur
    return response_item


def join_data() -> list:
    result = []
    current_time = int(datetime.datetime.now().timestamp())
    offset = current_time - OFFSET_MINUTES * SECONDS_IN_MINUTE
    for i in instructions:
        if i["created"] >= offset:
            for r in responses:
                if i["id"] == r["instruction"]:
                    result.append(
                        {
                            "description": i["description"],
                            "cache_hit": r["cache_hit"],
                            "response": r["response"],
                        }
                    )
    return result


def repl_create(cmd: list):
    """Handle create commands in REPL."""
    if cmd[1] == "member":
        print(create_member(cmd[2], cmd[3]))
    elif cmd[1] == "instruction":
        print(create_instruction(cmd[2], int(cmd[3]), cmd[4], cmd[5]))
    elif cmd[1] == "response":
        print(
            create_response(
                cmd[2], cmd[3], cmd[4], int(cmd[5]), int(cmd[6]), int(cmd[7])
            )
        )


def repl_edit(cmd: list):
    if cmd[1] == "member":
        print(edit_member(int(cmd[2]), cmd[3], cmd[4]))
    elif cmd[1] == "instruction":
        print(
            edit_instruction(int(cmd[2]), cmd[3], int(cmd[4]), cmd[5], cmd[6])
        )
    elif cmd[1] == "response":
        print(
            edit_response(
                int(cmd[2]),
                cmd[3],
                cmd[4],
                cmd[5],
                int(cmd[6]),
                int(cmd[7]),
                int(cmd[8]),
            )
        )


def repl_get_all(cmd: list):
    if cmd[1] == "members":
        print(get_all_members())
    elif cmd[1] == "instructions":
        print(get_all_instructions())
    elif cmd[1] == "responses":
        print(get_all_responses())


def repl_get(cmd: list):
    if cmd[1] == "member":
        print(get_member(int(cmd[2])))
    elif cmd[1] == "instruction":
        print(get_instruction(int(cmd[2])))
    elif cmd[1] == "response":
        print(get_response(int(cmd[2])))


def repl_join(cmd: list):
    print(join_data())


DISPATCHER = {
    "create": repl_create,
    "edit": repl_edit,
    "get_all": repl_get_all,
    "get": repl_get,
    "join": repl_join,
}


def run_repl():
    while True:
        try:
            line = input("> ")
            if line == "exit":
                break
            cmd = line.split()
            if cmd and cmd[0] in DISPATCHER:
                DISPATCHER[cmd[0]](cmd)
        except EOFError:
            break
        except Exception as error_msg:
            print(error_msg)


if __name__ == "__main__":
    run_repl()
