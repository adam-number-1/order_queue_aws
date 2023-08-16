import requests
import redis


# i could potentialy spawn a new thread everythime i rpop and do the job
# but for symplicity i will keep it single thread... for a while :]


redis_queue_connection = redis.Redis(
    host='localhost', 
    port=6379, 
    decode_responses=True
)


redis_order_connection = redis.Redis(
    host='localhost', 
    port=6379, 
    decode_responses=True
)


def pop_id(redis_con) -> int:
    """Return id if the next order in queue. Block until something appears.

    :param redis_con: redis connection object to queue
    :returns: id of the next order
    """
    _, id = redis_queue_connection.brpop('order_queue', timeout=0)
    id = int(id)
    return id


def process_order(order_id: int, redis_con: redis.Redis) -> str:
    """Return the status of processing an order.
    
    The function checks the ordered items, if there is enough stuff on stock.
    If there is, it will substract according items and will put the status to
    ``done``, otherwise the status is ``failed``.

    :param order_id: the unique id of the order to look up in the order 
                     database.
    :param redis_con: connection object to redis order db
    :returns: 'Done' for success, 'Failed' for failure.
    """


def main(
    redis_queue_connection,
    redis_order_connection
):
    while True:
        # lets block until there is somethign
        order_id: int = pop_id(redis_queue_connection)
        status: str = process_order(order_id, redis_order_connection)

        # time to tell the wsgi how it went
        requests.put(
            'http://localhost:8080', 
            json={
                'id': order_id,
                'status': status
            }
        )

if __name__ == '__main__':
    main(
        redis_queue_connection,
        redis_order_connection
    )


