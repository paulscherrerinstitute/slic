
def aligned_pid_and_n(start, n, rm):
    start, stop = aligned_pids(start, n, rm)
    return start, stop - start

def aligned_pids(start, n, rm):
    """
    return start/stop pids aligned to rep rate
    """
#    start -= 1 #TODO: count from zero?
    block_start = (start // rm) + 1 # calc block where start is in, then take following block
    block_stop  = block_start + n
    start = block_start * rm # adjust to actual rep rate (example: recording is at 100 Hz; for a 50 Hz device, 2*n pulses need to be recorded to get n pulses with that device)
    stop  = block_stop  * rm #TODO: check whether upper boundary is excluded (otherwise -1 here)
    return int(start), int(stop)


def align_pid_left(pid, rm):
    return align_pid(pid, rm, 0)

def align_pid_right(pid, rm):
    return align_pid(pid, rm, 1)

def align_pid(pid, rm, block_offset=0):
    block = pid // rm
    block += block_offset
    return block * rm



