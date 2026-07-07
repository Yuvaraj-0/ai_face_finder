import time

store = {}

class RateLimiter:

    def check(self, ip: str):
        now = time.time()
        window = 60
        limit = 5

        if ip not in store:
            store[ip] = []

        store[ip] = [t for t in store[ip] if now - t < window]

        if len(store[ip]) >= limit:
            return False

        store[ip].append(now)
        return True