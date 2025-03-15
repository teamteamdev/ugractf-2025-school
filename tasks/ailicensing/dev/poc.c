// program to seek a fd to start of file and read from it
// recieive a file descriptor num from stdin 

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

// #include <errno.h>
// #include <string.h>

#define EXIT_FAILURE 1
#define EXIT_SUCCESS 0


int main(void) {
    int fd;
    char buffer[1024];
    ssize_t bytes;

    printf("Enter file descriptor: ");
    if (scanf("%d", &fd) != 1) {
        fprintf(stderr, "Failed to read file descriptor\n");
        return EXIT_FAILURE;
    }

    if (lseek(fd, 0, SEEK_SET) == -1) {
        perror("lseek");
        return EXIT_FAILURE;
    }

    bytes = read(fd, buffer, sizeof(buffer));
    if (bytes == -1) {
        perror("read");
        return EXIT_FAILURE;
    }

    if (write(STDOUT_FILENO, buffer, bytes) == -1) {
        perror("write");
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
