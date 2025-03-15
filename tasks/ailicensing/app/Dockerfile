FROM alpine

WORKDIR /app
COPY bin/chatbot story.txt run.sh ./

RUN set -eu; \
    apk add --no-cache bash python3 build-base; \
    ln -sf /bin/bash /bin/sh; \
    chmod 4555 chatbot; \
    chmod 0444 story.txt; \
    touch flag; \
    chmod 0400 flag; \
    addgroup -g 1000 user; \
    adduser -G user -H -D -u 1000 user; \
    chmod 555 run.sh

USER user

CMD ["/app/run.sh"]
