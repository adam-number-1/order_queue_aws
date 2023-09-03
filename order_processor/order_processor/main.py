import requests
import redis

import boto3

# i could potentialy spawn a new thread everythime i rpop and do the job
# but for symplicity i will keep it single thread... for a while :]
# however requests for updating/gettingitems could go asynchronously


def pop_id(redis_con) -> int:
    """Return id if the next order in queue. Block until something appears.

    :param redis_con: redis connection object to queue
    :returns: id of the next order
    """
    _, id = redis_con.brpop('order_queue', timeout=0)
    id = int(id)
    return id


def get_order(order_id: int, dynamo_client) -> dict:
    """REturn the object representing the order.
    
    :param oderd_id: the uid of the order.
    :return: json object of the order.
    """
    response: dict = dynamo_client.get_item(
        TableName='order_table',
        Key={
            'string': {
                'N': f'{order_id}'
            }
        },
        ProjectionExpression='id, cartItems'
    )

    return response


def get_items(id_list: list[int], dynamo_client) -> dict:
    """Return a dictionary from the database, that conforms the 
    ``id:available_quantity`` schema.
    
    :param id_list: list of ids to query from the database.
    :returns: dictionary of the items and their available quantities.
    """
    retrieved_items = {}
    for id in id_list:
        response: dict = dynamo_client.get_item(
            TableName='items_table',
            Key={
                'string': {
                    'N': f'{id}'
                }
            },
            ProjectionExpression='id, availableQuantity'
        )
        retrieved_items[id] = response
    return retrieved_items



def push_new_quantities(items: dict, dynamo_client) -> None:
    """Update quantities of provided items.
    
    :param items: dictionary of items to update their quantity.
    """
    for item_id, item_attrs in items.items():
        av_quant = item_attrs['Item']['availableQuantity']['N']
        _ = dynamo_client.update_item(
            TableName='items_table',
            Key={
                'string': {
                    'N': item_id
                }
            },
            UpdateExpression="SET availabeQuantity = :av",
            ExpressionAttributeValues={
                ':av': {
                    'N': f'{av_quant}'
                }
            },
            ReturnValues='NONE'
        )
    
    

def process_order(
    order_id: int,
    dynamo_client
) -> str:
    """Return the status of processing an order.
    
    The function checks the ordered items, if there is enough stuff on stock.
    If there is, it will substract according items and will put the status to
    ``done``, otherwise the status is ``failed``.

    :param order_id: the unique id of the order to look up in the order 
                     database.
    :param redis_con: connection object to redis order db
    :returns: 'Done' for success, 'Failed' for failure.
    """
    order: dict = get_order(
        order_id,
        dynamo_client
    )
    query_items: list[int] = [
        cart_item['M']['id']['N'] for cart_item in order['Item']['cartItems']['L']
    ]

    available_items = get_items(
        query_items,
        dynamo_client
    )

    # main logic - checking if an order is feasible
    for cart_item in order['Item']['cartItems']['L']:
        item_id: str = cart_item['M']['id']['N']
        item_quant: int = int(cart_item['M']['orderedQuantity']['N'])
        available_item_quant: int = int(
            available_items[item_id]['Item']['availableQuantity']['N']
        )

        if (
            available_item_quant - item_quant < 0
        ):
            return 'Failed'
        available_items[item_id]['Item']['availableQuantity']['N']  = str(
            available_item_quant - item_quant
        )
    
    push_new_quantities(
        available_items,
        dynamo_client
    )
    return 'Done'


def main(
    redis_queue_connection,
    dynamo_client
):
    while True:
        # lets block until there is somethign
        order_id: int = pop_id(redis_queue_connection)
        status: str = process_order(
            order_id,
            dynamo_client
        )

        # time to tell the wsgi how it went
        requests.put(
            'http://localhost:8080', 
            json={
                'id': order_id,
                'status': status
            }
        )


if __name__ == '__main__':
    dynamo_client = boto3.client('dynamodb')
    items_table = dynamo_client.Table('items')
    orders_table = dynamo_client.Table('orders')

    redis_queue_connection = redis.Redis(
        host='localhost', 
        port=6379, 
        decode_responses=True
    )
    main(
        redis_queue_connection,
        dynamo_client
    )


