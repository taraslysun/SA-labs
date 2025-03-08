import hazelcast
import hazelcast.config
import time

if __name__ == '__main__':

    client = hazelcast.HazelcastClient(
        cluster_name="hello-world",
    )

    queue = client.get_queue("queue")
    for i in range(1, 101):
        while True:
            time.sleep(1)
            if queue.offer(i, timeout=2).result():
                print(f"added {i}")
                break
            else:
                print("queue is full")

client.shutdown()


