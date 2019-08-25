import redis

client = redis.StrictRedis(db=3)

for i in range(100000):
    client.set(f"key-{i}", "hello world")
