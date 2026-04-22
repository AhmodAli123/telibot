import os
import resource


class Sandbox:
    @staticmethod
    def apply_limits(max_memory_mb: int = 256, max_cpu_sec: int = 60):
        if hasattr(resource, "setrlimit"):
            mem = max_memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
            resource.setrlimit(resource.RLIMIT_CPU, (max_cpu_sec, max_cpu_sec))

    @staticmethod
    def preexec_fn():
        if hasattr(os, "setsid"):
            os.setsid()
        try:
            Sandbox.apply_limits()
        except Exception:
            pass