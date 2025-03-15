CC = musl-gcc
CFLAGS = -Wall -fno-stack-protector -fno-PIE -O0
# Static linking with no garbage collection of sections, and whole-archive wrapping for libc and libm.
LDFLAGS = -static -Wl,-no-gc-sections \
          -Wl,--whole-archive -lc -Wl,--no-whole-archive \
          -Wl,--whole-archive -lm -Wl,--no-whole-archive
TARGET = chatbot

all: $(TARGET)

$(TARGET): chatbot.c
	$(CC) $(CFLAGS) -o $(TARGET) chatbot.c $(LDFLAGS)
	sudo chown root:root $(TARGET)
	sudo chmod 4755 $(TARGET)

clean:
	sudo rm -f $(TARGET)

.PHONY: all clean