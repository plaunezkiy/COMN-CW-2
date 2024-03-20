with open("data.txt", "r") as f:
    data = f.read().strip()
    timeouts = data.split("\n\n")
    for timeout in timeouts:
        records = timeout.split("\n")
        timeout = int(records[0][:-2])
        values = records[1:]
        print(f"Timeout: {timeout}ms")
        # runtime, retrs, thrput
        vals = [0, 0, 0]
        for value in values:
            for var_id, delta in zip(range(len(vals)), map(float, value.split()[1].split("#"))):
                vals[var_id] += delta
        avg_rtime, avg_retries, avg_tput = map(lambda v: v/len(values), vals)
        print(f"Average runtime: {avg_rtime}")
        print(f"Average retries: {avg_retries}")
        print(f"Average throughput: {avg_tput}")
        print()