#!/usr/bin/env python3
import sys
from collections import OrderedDict

MAX_JP = 16
CP_ORDER = ("TL", "BL", "TR", "BR")

PIN_COUNTS = {
    "R": 2, "C": 2, "L": 2, "V": 2, "I": 2, "D": 2,
    "Q": 3, "J": 3,
    "M": 4,
    "E": 4, "G": 4,
    "F": 2, "H": 2,
}

GROUND_NAMES = {"0", "GND", "gnd"}

CROSS_POINT_BLOCK = [
    "* block symbol definitions",
    ".subckt cross_point A B",
    "R1 A B 60",
    "C1 B 0 16p",
    ".ends cross_point",
]


def is_passthrough(line: str) -> bool:
    s = line.strip()
    return (
        not s
        or s.startswith("*")
        or s.startswith(";")
        or s.startswith(".")
        or s.startswith("+")
    )


def get_pin_count(tokens):
    name = tokens[0]
    kind = name[0].upper()
    if kind not in PIN_COUNTS:
        raise ValueError(
            f"Unsupported element '{name}'. "
            f"Add its pin count to PIN_COUNTS if needed."
        )
    return PIN_COUNTS[kind]


def parse_netlist(lines):
    parsed = []
    for raw in lines:
        line = raw.rstrip("\n")

        if is_passthrough(line):
            parsed.append({"type": "raw", "text": line})
            continue

        tokens = line.split()

        # Leave existing generated cross_points untouched
        if len(tokens) >= 4 and tokens[-1] == "cross_point" and tokens[0].startswith("X§X"):
            parsed.append({"type": "raw", "text": line})
            continue

        pin_count = get_pin_count(tokens)
        parsed.append({
            "type": "element",
            "tokens": tokens[:],
            "pin_count": pin_count,
        })

    return parsed


def collect_used_nodes(parsed):
    used = set()
    for entry in parsed:
        if entry["type"] != "element":
            continue
        tokens = entry["tokens"]
        for i in range(1, 1 + entry["pin_count"]):
            used.add(tokens[i])
    return used


def make_fresh_node_generator(used_nodes):
    n = 1

    def fresh():
        nonlocal n
        while True:
            candidate = f"N{n:03d}"
            n += 1
            if candidate not in used_nodes:
                used_nodes.add(candidate)
                return candidate

    return fresh


def has_cross_point_block(parsed):
    for entry in parsed:
        if entry["type"] != "raw":
            continue
        s = entry["text"].strip().lower()
        if s.startswith(".subckt") and "cross_point" in s.split():
            return True
    return False


def find_last_component_index(parsed):
    last = -1
    for i, entry in enumerate(parsed):
        if entry["type"] == "element":
            last = i
    return last


def transform(parsed):
    used_nodes = collect_used_nodes(parsed)
    fresh_node = make_fresh_node_generator(used_nodes)

    net_uses = OrderedDict()

    for entry_idx, entry in enumerate(parsed):
        if entry["type"] != "element":
            continue

        tokens = entry["tokens"]
        pin_count = entry["pin_count"]

        for tok_idx in range(1, 1 + pin_count):
            net = tokens[tok_idx]
            if net in GROUND_NAMES:
                continue
            net_uses.setdefault(net, []).append((entry_idx, tok_idx))

    out_cross_points = []
    jp_index = 1

    for original_net, uses in net_uses.items():
        if jp_index > MAX_JP:
            raise ValueError(
                f"Ran out of jumper names at net '{original_net}'. "
                f"Need more than JP1..JP{MAX_JP}."
            )

        if len(uses) > len(CP_ORDER):
            raise ValueError(
                f"Net '{original_net}' has {len(uses)} connections, "
                f"but JP{jp_index} only supports {len(CP_ORDER)} positions: "
                f"{', '.join(CP_ORDER)}."
            )

        jp_name = f"JP{jp_index}"

        for use_idx, (entry_idx, tok_idx) in enumerate(uses):
            new_leaf = fresh_node()
            parsed[entry_idx]["tokens"][tok_idx] = new_leaf

            cp_suffix = f"{CP_ORDER[use_idx]}{jp_index}"
            out_cross_points.append(
                f"X§X{cp_suffix} {jp_name} {new_leaf} cross_point"
            )

        jp_index += 1

    rendered = []
    for entry in parsed:
        if entry["type"] == "raw":
            rendered.append(entry["text"])
        else:
            rendered.append(" ".join(entry["tokens"]))

    last_component_index = find_last_component_index(parsed)

    if last_component_index == -1:
        body = []
        trailing = rendered[:]
    else:
        body = rendered[:last_component_index + 1]
        trailing = rendered[last_component_index + 1:]

    final_lines = []
    final_lines.extend(body)

    if out_cross_points:
        final_lines.append("")
        final_lines.extend(out_cross_points)

    if not has_cross_point_block(parsed):
        final_lines.append("")
        final_lines.extend(CROSS_POINT_BLOCK)

    if trailing:
        final_lines.append("")
        final_lines.extend(trailing)

    return final_lines


def main():
    if len(sys.argv) > 2:
        print(f"Usage: {sys.argv[0]} [input.cir]", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) == 2:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            lines = f.readlines()
    else:
        lines = sys.stdin.readlines()

    parsed = parse_netlist(lines)
    result = transform(parsed)

    for line in result:
        print(line)


if __name__ == "__main__":
    '''
    usage:
    python auto_cross_points.py draft.cir > new_draft.cir
    '''
    main()

