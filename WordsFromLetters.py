from itertools import permutations
import ctypes
import re
from datetime import datetime

from multiprocessing import Process, current_process, Queue


kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)


class color:
    purple = '\033[95m'
    cyan = '\033[96m'
    darkcyan = '\033[36m'
    blue = '\033[94m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    bold = '\033[1m'
    underline = '\033[4m'
    end = '\033[0m'


def fac(n):
    factorial = 1
    while n > 1:
        factorial *= n
        n -= 1
    return factorial


def PrintFoundWords(foundWords, queue):
    if(not queue.empty()):
        print(color.purple + "\nНайденные слова:" + color.end)
        while not queue.empty():
            print(queue.get())
    elif (len(foundWords) > 0):
        print(color.purple + "\nНайденные слова:" + color.end)
        for x in foundWords:
            print(x)
    else:
        print("\nНи одного слова не найдено")
    print(color.yellow + "=" * 30 + color.end)


def FileSeeking(wordToFind, words, foundWords, printWordWhenFound, queue = 0):
    with open("russian.txt", "r+", encoding='windows-1251') as f:
        f.seek(0)
        y = 0

        for line in f:
            y = y + 1

            if (len(line) - 1 == len(wordToFind)):
                letters = list(line)
                del letters[-1]
                if (sorted(letters) == sorted(wordToFind)):
                    for word in words:
                        if word + "\n" == line:
                            if(current_process().name == 'MainProcess'):
                                foundWords.append(word)
                            else:
                                queue.put(word)

                            if(printWordWhenFound):
                                print(color.red + "Найдено слово: " + word + color.end)


def GeneratingAllVariants(wordToFind, foundWords, whenSeek, printWordWhenFound):
    words = []
    x = 0
    for i in permutations(wordToFind):
        x = x + 1
        words.append(''.join(i))

        percents = (x / fac(len(wordToFind))) * 100

        if(percents % whenSeek == 0):
            FileSeeking(wordToFind, set(words), foundWords, printWordWhenFound)
            words.clear()


def GeneratingHalfVariants(wordToFind, foundWords, whenSeek, printWordWhenFound, queue):
    words = []
    x = 0

    for i in permutations(wordToFind):
        x = x + 1
        words.append(''.join(i))
        percents = (x / (fac(len(wordToFind)) / 2)) * 100

        if(whenSeek == 0):
            if(len(words) > 10000000 - 1 or percents % 2 == 0):
                print("Просмотрено " + color.green + str(x) + color.end + " слов")
                FileSeeking(wordToFind, set(words), foundWords, printWordWhenFound, queue)
                words.clear()
        else:
            if (percents % (whenSeek / 2) == 0):
                print("Создано " + color.green + str(int(percents)) + color.end + "% вариантов")

            if (percents % (whenSeek) == 0):
                FileSeeking(wordToFind, set(words), foundWords, printWordWhenFound, queue)
                words.clear()

        if(percents == 100):
            return


if __name__ == '__main__':
    while(True):
        wordToFind = input("Введите буквы: ")
        wordToFind = re.sub(r'\W', '', wordToFind).lower()
        foundWords = []
        printWordWhenFound = False

        if (len(wordToFind) > 12):
            printWordWhenFound = True
            whenSeek = 0
        elif (len(wordToFind) > 10):
            printWordWhenFound = True
            whenSeek = 10
        elif (len(wordToFind) > 5):
            whenSeek = 20
        else:
            whenSeek = 100

        queue = Queue()
        startTime = datetime.now()
        if(len(wordToFind) > 7):
            wordToFindRvs = wordToFind[::-1]

            proc1 = Process(target=GeneratingHalfVariants, args=(wordToFind, foundWords, whenSeek, printWordWhenFound, queue,))
            proc2 = Process(target=GeneratingHalfVariants, args=(wordToFindRvs, foundWords, whenSeek, printWordWhenFound, queue,))

            proc1.start()
            proc2.start()
            proc1.join()
            proc2.join()
        else:
            GeneratingAllVariants(wordToFind, foundWords, whenSeek, printWordWhenFound)
        print(datetime.now() - startTime)

        PrintFoundWords(foundWords, queue)
