import time

file_name = 'log.txt'
file = open(file_name, 'w')
file_info = "1\n" \
            "2\n" \
            "3\n" \
            "4\n" \
            "5\n" \
            "2\n"
file.write(file_info)
file.close()
a = time.time()
file = open(file_name, 'r+')
file.seek(0, 0)
for i in range(2):
    line_new = '1000\n'
    file.write(line_new)

file.close()
print(time.time() - a)
