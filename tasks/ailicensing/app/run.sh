#!/bin/sh

while [ ! -s flag ]; do
    sleep 0.5
done

exec /app/chatbot
