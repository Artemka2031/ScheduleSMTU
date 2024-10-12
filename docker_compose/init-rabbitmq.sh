#!/bin/bash
# Команда для создания виртуальных хостов
rabbitmqctl add_vhost general_vhost
# Настройка прав для пользователей
rabbitmqctl set_permissions -p general_vhost rabbitmq ".*" ".*" ".*"
