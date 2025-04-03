import hashlib
import json
import logging

from Bot.RabbitMQProducer.rabbitmq_producer import RabbitMQProducer
from Bot.RedisClient.redis_client import get_redis_client

rabbitmq_producer = None

async def send_request_mq(task_name: str, data: list):
    global rabbitmq_producer

    cache_key = generate_cache_key(task_name, data)

    try:
        redis = await get_redis_client()

        cached_result = await redis.get(cache_key)

        if cached_result:
            logging.info(f"Cache hit for key: {cache_key}")
            return json.loads(cached_result)
        else:
            logging.info(f"Cache miss for key: {cache_key}")
            if not rabbitmq_producer:
                rabbitmq_producer = RabbitMQProducer()
                await rabbitmq_producer.connect()

            request_data = {
                'task': task_name,
                'data': data
            }
            logging.info('Начинается отправка сообщения')
            response = await rabbitmq_producer.send_message(request_data)

            # Сохраняем результат в кеше
            await redis.setex(cache_key, 900, json.dumps(response))

            return response
    except Exception as e:
        logging.error(f'Ошибка при кешировании или отправке запроса: {e}')

    # if not rabbitmq_producer:
    #     rabbitmq_producer = RabbitMQProducer()
    #     await rabbitmq_producer.connect()
    #
    # request_data = {
    #     'task': task_name,
    #     'data': data
    # }
    # logging.info('Начинается отправка сообщения)')
    # response = await rabbitmq_producer.send_message(request_data)
    #
    # #await rabbitmq_producer.close()
    # return response

def generate_cache_key(task_name: str, data: list):
    data_string = json.dumps(data, sort_keys=True)
    key = f"{task_name}:{hashlib.md5(data_string.encode()).hexdigest()}"
    return key


async def update_cache(user_id: int):
    redis = await get_redis_client()
    cache_key = generate_cache_key('admin_bot.tasks.get_group_number', [user_id])
    await redis.delete(cache_key)