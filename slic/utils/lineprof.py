import sys
import time
import linecache
from collections import defaultdict


class LineProfiler:

    def __init__(self):
        self.timings = defaultdict(lambda: defaultdict(int)) # one per file with timing per lineno/line
        self.prev_time = None
        self.prev_frame = None
        self.prev_lineno = None

    def __enter__(self):
        sys.settrace(self.tracer)
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        sys.settrace(None)

    def tracer(self, frame, event, _arg):
        now = time.perf_counter()
        if self.prev_time is not None:
            filename = self.prev_frame.f_code.co_filename
            lineno = self.prev_lineno
            line = linecache.getline(filename, lineno).rstrip("\n")
            key = (lineno, line)
            delta = now - self.prev_time
            self.timings[filename][key] += delta
        self.prev_time = now
        self.prev_frame = frame
        self.prev_lineno = frame.f_lineno
        return self.tracer

    def print(self, fname):
        entries = self.timings[fname]
        print(f"\nFile: {fname}")
        for (lineno, line), timing in sorted(entries.items()):
            print(f"{lineno:4} {timing*1e3:8.3f} ms | {line}")

    def print_all(self):
        for fname in sorted(self.timings):
            self.print(fname)



