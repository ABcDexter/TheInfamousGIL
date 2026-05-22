import threading

shared_list = []

def append_items():
    for _ in range(10**5):
        shared_list.append(1)

threads = []
for _ in range(4):
    t = threading.Thread(target=append_items)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("Expected length:", 4 * 10**5)
print("Actual length:  ", len(shared_list))