import hazelcast
import time

if __name__ == "__main__":
    client = hazelcast.HazelcastClient(
        cluster_name="hello-world",
    )

    map = client.get_map("my-distributed-map")
    map.put_if_absent("key", 0).result()
    start_time = time.time()

    for i in range(10000):
        while True:
            val = map.get("key").result()
            new_val = int(val) + 1

            if map.replace_if_same("key", val, new_val).result():
                break
        if i % 1000 == 0:
            print("operation #"+str(i))

    final_value = map.get("key").result()
    print("Total time:", time.time() - start_time)
    print("Final value:", final_value)

    client.shutdown()


