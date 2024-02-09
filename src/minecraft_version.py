ADDED_EULA = "1.7.10"

def get_min(a: str, b: str):
    a = a.split("-")[0].split("_")[0]
    b = b.split("-")[0].split("_")[0]
    a_major, a_minor, *a_patch = map(int, a.split("."))
    b_major, b_minor, *b_patch = map(int, b.split("."))
    if a_major < b_major:
        return a
    elif a_major > b_major:
        return b
    elif a_minor < b_minor:
        return a
    elif a_minor > b_minor:
        return b
    else:
        if not a_patch:
            a_patch = 0
        else:
            a_patch = a_patch[0]
        if not b_patch:
            b_patch = 0
        else:
            b_patch = b_patch[0]

        if a_patch < b_patch:
            return a
        elif a_patch > b_patch:
            return b
    return a