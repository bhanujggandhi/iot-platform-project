import time


if __name__ == "__main__":
    # with open("../log.txt" , 'a') as f:

    while True:
        f = open("../log.txt", "a")
        log = "[LOG]: Mod_1 " + str(time.time())
        f.write(log + "\n")
        f.close()
        time.sleep(10)
