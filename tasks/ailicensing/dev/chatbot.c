#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <errno.h>
#include <math.h>
#include <regex.h>

#define LICENSE_PATH "./flag"
#define BUFFER_SIZE 1024
#define SECURE_BUFFER_SIZE 2^10


// Function to securely clear the stack
void secure_clear_stack(void *ptr, size_t size) {
    char secubuffer[SECURE_BUFFER_SIZE];
    memset(secubuffer, 0, SECURE_BUFFER_SIZE);
    if (ptr == NULL || size == 0) {
        return;
    }
    volatile unsigned char *p = (volatile unsigned char *)ptr;
    while (size--) {
        *p++ = 0;
    }
}



int check_license(char* license, int len){
    // Ensure license is null-terminated
    if(len <= 0) return 0;
    license[len] = '\0';

    regex_t regex;
    const char *pattern = "^ugra_[A-Za-z0-9_]{2,56}$";
    if (regcomp(&regex, pattern, REG_EXTENDED) != 0) {
        fprintf(stderr, "Could not compile regex\n");
        return 0;
    }

    int reti = regexec(&regex, license, 0, NULL, 0);
    regfree(&regex);

    return (reti == 0);
}


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ctype.h>

#define MAX_LINE_LEN 1024
#define MAX_WORDS_IN_SENTENCE 30  // Максимальное число слов для одного предложения (на случай, если знак окончания не встретится)

// Структура для хранения слова и списка последующих слов.
typedef struct WordNode {
    char *word;
    struct WordNode **nextNodes;  // Динамический массив указателей на следующие слова
    int nextCount;                // Число переходов для данного слова
    int nextCapacity;             // Вместимость массива переходов
    struct WordNode *next;        // Следующий элемент в односвязном списке (словаре)
} WordNode;

// Поиск слова в словаре
WordNode* find_word(WordNode *head, const char *word) {
    while (head) {
        if (strcmp(head->word, word) == 0)
            return head;
        head = head->next;
    }
    return NULL;
}

// Добавление нового слова в словарь
WordNode* add_word(WordNode **head, const char *word) {
    WordNode *newNode = (WordNode *)malloc(sizeof(WordNode));
    if (!newNode) {
        fprintf(stderr, "Ошибка выделения памяти для нового узла.\n");
        exit(EXIT_FAILURE);
    }
    newNode->word = strdup(word);
    newNode->nextNodes = NULL;
    newNode->nextCount = 0;
    newNode->nextCapacity = 0;
    newNode->next = *head;
    *head = newNode;
    return newNode;
}

// Добавление перехода от предыдущего слова к текущему
void add_transition(WordNode *prev, WordNode *current) {
    if (prev->nextCount == prev->nextCapacity) {
        int newCapacity = (prev->nextCapacity == 0) ? 2 : prev->nextCapacity * 2;
        WordNode **temp = realloc(prev->nextNodes, newCapacity * sizeof(WordNode*));
        if (!temp) {
            fprintf(stderr, "Ошибка перераспределения памяти для переходов.\n");
            exit(EXIT_FAILURE);
        }
        prev->nextNodes = temp;
        prev->nextCapacity = newCapacity;
    }
    prev->nextNodes[prev->nextCount] = current;
    prev->nextCount++;
}

// Освобождение памяти, занятой словарём
void free_dictionary(WordNode *head) {
    while (head) {
        WordNode *temp = head;
        head = head->next;
        free(temp->word);
        free(temp->nextNodes);
        free(temp);
    }
}

// Подсчёт числа узлов в словаре
int count_nodes(WordNode *head) {
    int count = 0;
    while (head) {
        count++;
        head = head->next;
    }
    return count;
}

// Случайный выбор узла из словаря
WordNode* pick_random_node(WordNode *dictionary) {
    int count = count_nodes(dictionary);
    if (count == 0)
        return NULL;
    int index = rand() % count;
    WordNode *node = dictionary;
    for (int i = 0; i < index && node; i++) {
        node = node->next;
    }
    return node;
}


int chat_loop(WordNode *dictionary);

// Генерация предложения-ответа с использованием всего запроса пользователя.
// Функция токенизирует запрос, ищет все слова, присутствующие в словаре, и выводит их подряд
// через пробел (первое слово при этом с заглавной буквы). После этого цепь Маркова дополняет предложение,
// начиная с последнего найденного слова.
void generate_sentence_based_on_question(WordNode *dictionary, const char *question) {
    if (!dictionary) {
        printf("Нет обучающих данных.\n");
        return;
    }

    // Копия запроса для токенизации.
    char questionCopy[MAX_LINE_LEN];
    strncpy(questionCopy, question, MAX_LINE_LEN);
    questionCopy[MAX_LINE_LEN - 1] = '\0';

    // Токенизация запроса по разделителям: пробел, табуляция, перевод строки и знаки препинания.
    const char delimitersForQuestion[] = " \t\r\n,.!?";
    char *token = strtok(questionCopy, delimitersForQuestion);

    // Массив для хранения найденных слов, присутствующих в словаре.
    WordNode *seedNodes[100];
    int seedCount = 0;

    while (token != NULL && seedCount < 100) {
        WordNode *found = find_word(dictionary, token);
        if (found != NULL)
            seedNodes[seedCount++] = found;
        token = strtok(NULL, delimitersForQuestion);
    }

    WordNode *current = NULL;
    // Если найдены слова из запроса, выводим их подряд через пробел.
    if (seedCount > 0) {
        for (int i = 0; i < seedCount; i++) {
            // Если это первое слово, приводим первую букву к заглавной.
            if (i == 0) {
                char *firstWord = strdup(seedNodes[i]->word);
                if (firstWord) {
                    firstWord[0] = toupper(firstWord[0]);
                    printf("%s ", firstWord);
                    free(firstWord);
                } else {
                    printf("%s ", seedNodes[i]->word);
                }
            } else {
                printf("%s ", seedNodes[i]->word);
            }
        }
        // Берем последнее слово из запроса как отправную точку для дальнейшей генерации.
        current = seedNodes[seedCount - 1];
    } else {
        // Если ни одно слово не найдено, выбираем случайное слово из всего словаря.
        current = pick_random_node(dictionary);
        if (current != NULL) {
            char *firstWord = strdup(current->word);
            if (firstWord) {
                firstWord[0] = toupper(firstWord[0]);
                printf("%s ", firstWord);
                free(firstWord);
            } else {
                printf("%s ", current->word);
            }
        }
    }

    int wordCounter = seedCount > 0 ? seedCount : 1;

    // Дополняем предложение, используя цепь Маркова, начиная с текущего слова.
    while (wordCounter < MAX_WORDS_IN_SENTENCE) {
        int len = strlen(current->word);
        if (len > 0) {
            char lastChar = current->word[len - 1];
            if (lastChar == '.' || lastChar == '!' || lastChar == '?')
                break;
        }
        if (current->nextCount == 0)
            break;
        int nextIndex = rand() % current->nextCount;
        current = current->nextNodes[nextIndex];
        printf("%s ", current->word);
        wordCounter++;
    }

    printf("\n");
}

int main_lic() {
    FILE *fp = fopen("story.txt", "r");
    if (!fp) {
        fprintf(stderr, "Ошибка: невозможно открыть файл story.txt\n");
        return EXIT_FAILURE;
    }

    // Инициализация генератора случайных чисел.
    srand((unsigned int)time(NULL));

    WordNode *dictionary = NULL;
    WordNode *prevNode = NULL;
    char line[MAX_LINE_LEN];
    // Используем разделители – пробельные символы, чтобы сохранить пунктуацию в словах.
    const char delimitersForFile[] = " \t\r\n";

    // Чтение обучающего текста из файла построчно и построение модели цепи Маркова.
    while (fgets(line, sizeof(line), fp) != NULL) {
        char *token = strtok(line, delimitersForFile);
        while (token != NULL) {
            // Поиск или добавление слова в словарь.
            WordNode *currentNode = find_word(dictionary, token);
            if (!currentNode)
                currentNode = add_word(&dictionary, token);

            // Если предыдущее слово существует, добавляем переход.
            if (prevNode != NULL)
                add_transition(prevNode, currentNode);

            prevNode = currentNode;
            token = strtok(NULL, delimitersForFile);
        }
    }
    fclose(fp);
    int res = 0;
    printf("Чат-бот (введите \"exit\" для выхода):\n");
    while (res != 1) {
        res = chat_loop(dictionary);
    }
    // Освобождение памяти, занятой словарём.
    free_dictionary(dictionary);
    return 0;
}
int chat_loop(WordNode *dictionary) {
    // Интерактивный цикл чат-бота.
    char userInput[256];

    printf("Вы: \n\t");
    if(gets(userInput) == NULL) {
        return 1;
    }
    userInput[strcspn(userInput, "\n")] = '\0';
    if (strcmp(userInput, "exit") == 0)
        return 1;

    printf("Бот: \n\t");
    generate_sentence_based_on_question(dictionary, userInput);

    return 0;

}







int main() {

    setvbuf(stdout, NULL, _IONBF, 0);
    printf("Reading license...\n");

    int fd = open(LICENSE_PATH, O_RDONLY);
    if (fd == -1) {
        fprintf(stderr, "Error opening %s: %s\n", LICENSE_PATH, strerror(errno));
        return 1;
    }
    FILE *license_file = fdopen(fd, "r");

    char license_buffer[BUFFER_SIZE];
    memset(license_buffer, 0, BUFFER_SIZE);

    if (fgets(license_buffer, sizeof(license_buffer), license_file) == NULL) {
        fprintf(stderr, "Error reading %s: %s\n", LICENSE_PATH, strerror(errno));
        close(fd);
        return 1;
    }

    if (strcmp(license_buffer, "-----BEGIN AI CHATBOT LICENSE-----\n") != 0) {
        fprintf(stderr, "Invalid license.\n");
        close(fd);
        return 1;
    }

    if (fgets(license_buffer, sizeof(license_buffer), license_file) == NULL) {
        fprintf(stderr, "Error reading %s: %s\n", LICENSE_PATH, strerror(errno));
        close(fd);
        return 1;
    }

    // License is expected to end with newline
    if (!check_license(license_buffer, strlen(license_buffer) - 1)) {
        fprintf(stderr, "Invalid license.\n");
        close(fd);
        return 1;
    }

    secure_clear_stack(license_buffer, BUFFER_SIZE);


    uid_t ruid;
    ruid = getuid();
    // euid = geteuid();
    // Drop privileges permanently
    if (setuid(ruid) == -1) {
        fprintf(stderr, "Failed to drop privileges: %s\n", strerror(errno));
        return 1;
    }

    // printf("Enter some data: \n");
    // printf("Enter some data: \n");
    // char data[20];
    // memset(data, 0, 20);

    // // Read user input

    // gets(data);

    // printf("You entered: %s\n", data);

    // return 1;
    return main_lic();
}
