import hashlib
import json
import logging

from admin_bot.RabbitMQProducer.rabbitmq_producer import RabbitMQProducer
from admin_bot.RedisClient.redis_client import get_redis_client

rabbitmq_producer = None

logging.basicConfig(
    level=logging.INFO,  # Или DEBUG, если нужно больше деталей
    format='%(asctime)s %(levelname)s:%(name)s:%(message)s'
)

async def send_request_mq(task_name: str, data: list):
    global rabbitmq_producer

    # Получаем версию для данного типа задач (например, для админ-бота можно использовать task_name или общий префикс)
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

            if response is not None:
                await redis.setex(cache_key, 60, json.dumps(response))

            return response
    except Exception as e:
        logging.error(f'Ошибка при кешировании или отправке запроса: {e}')

def generate_cache_key(task_name: str, data: list):
    data_string = json.dumps(data, sort_keys=True)
    key = f"{task_name}:{hashlib.md5(data_string.encode()).hexdigest()}"
    return key

async def update_cache(user_id: int):
    redis = await get_redis_client()
    cache_key = generate_cache_key('admin_bot.tasks.get_faculty_id', [user_id])
    await redis.delete(cache_key)