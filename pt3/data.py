with open("data100.txt", "r") as f:
    data = f.read().strip()
    windows = data.split("\n\n")
    for window in windows:
        records = window.split("\n")
        window_size = int(records[0].split(":")[1])
        values = records[1:]
        print(f"Window: {window_size}")
        # retrs, thrput
        vals = [0]
        for value in values:
            for var_id, delta in zip(range(len(vals)), map(float, value.split(". ")[1].split())):
                vals[var_id] += delta
        avg_tput = list(map(lambda v: v/len(values), vals))[0]
        print(f"Average throughput: {avg_tput}")
        print()