def get_selection(filename):
    output = ""
    with open(filename, "r") as f:
        lines = f.readlines()
    start = False
    for line in lines:
        if line.startswith('~') and not start:
            start = True
            continue

        if start and not line.startswith('~'):
            output += line
            continue
        elif line.startswith('~'):
            break
    return output
