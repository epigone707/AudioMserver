

def get_sec(time_str):
    """Get seconds from time."""
    count = 0
    for c in time_str:
        if c == ':':
            count += 1
    if count == 2:
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)
    elif count == 1:
        m, s = time_str.split(':')
        return int(m) * 60 + int(s)
    else:
        print(f"invalid duration string: {time_str}")
        return 0

print(get_sec("1:23:34:10"))