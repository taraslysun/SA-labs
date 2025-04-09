
import docker

def start_hz_node(ip, port):
    print(f'Starting Hazelcast container on port {ip}:{port}')
    docker_client = docker.from_env()
    try:
        docker_client.networks.create('hazelcast-network')
    except docker.errors.APIError:
        pass

    container_name = f'hazelcast-{port}'
    hz_container = docker_client.containers.run(
        'hazelcast/hazelcast:5.3.8',
        detach=True,
        name=container_name,
        network='hazelcast-network',
        ports={"5701" : port},
        environment={"HZ_CLUSTERNAME":"logs-db",
                    #  "HZ_NETWORK_PUBLICADDRESS":f"{ip}:{port}"
                    }
    )
    print(f'Hazelcast container {hz_container.name} is running on port {port}')
    return hz_container
