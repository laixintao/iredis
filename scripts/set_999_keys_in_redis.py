import redis

client = redis.StrictRedis(db=3)

for i in range (1000):
    client.set(f"key-{i}", "hello world")
