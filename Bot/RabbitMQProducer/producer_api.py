import logging

from Bot.RabbitMQProducer.rabbitmq_producer import RabbitMQProducer



rabbitmq_producer = None

async def send_request_mq(task_name: str, data: list):
    global rabbitmq_producer

    if not rabbitmq_producer:
        rabbitmq_producer = RabbitMQProducer()
        await rabbitmq_producer.connect()

    request_data = {
        'task': task_name,
        'data': data
    }
    logging.info('Начинается отправка сообщения)')
    response = await rabbitmq_producer.send_message(request_data)

    return response
