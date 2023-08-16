import redis

# this comes in separate module, so i can python -im run this and try stuff

redis_connection = redis.Redis(
    host='localhost', 
    port=6379, 
    decode_responses=True
)