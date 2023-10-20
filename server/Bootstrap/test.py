import time

counter = 0
# with open('numbers.txt', 'w') as file:
while counter < 10:
    file = open("numbers.txt", "a")
    file.write(str(counter) + "\n")
    counter += 1
    file.close()
    time.sleep(10)
