import hazelcast

if __name__ == '__main__':
    client = hazelcast.HazelcastClient(
        cluster_name="hello-world",
    )

    queue = client.get_queue("queue")

    while True:
        item = queue.take().result()
        if item is None:
            break
        print(f"taken {item}")
        

    client.shutdown()

