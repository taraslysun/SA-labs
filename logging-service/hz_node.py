import docker

def start_hz_node(ip, port):
    print(f'Starting Hazelcast container on port {ip}:{port}')
    docker_client = docker.from_env()
    
    try:
        docker_client.networks.create('hazelcast-network')
        print("Created hazelcast-network")
    except docker.errors.APIError as e:
        print(f"Network already exists or error creating network: {e}")

    container_name = f'hazelcast-{port}'
    
    # Check if container already exists and remove it
    try:
        old_container = docker_client.containers.get(container_name)
        print(f"Found existing container {container_name}, removing it")
        old_container.stop()
        old_container.remove()
    except docker.errors.NotFound:
        pass
    except Exception as e:
        print(f"Error cleaning up existing container: {e}")
    
    try:
        hz_container = docker_client.containers.run(
            'hazelcast/hazelcast:5.3.8',
            detach=True,
            name=container_name,
            network='hazelcast-network',
            ports={5701: port},
            environment={
                "HZ_CLUSTERNAME": "logs-db",
                "HZ_NETWORK_PUBLICADDRESS": f"{ip}:{port}"
            }
        )
        print(f'Hazelcast container {hz_container.name} is running on port {port}')
        return hz_container
    except Exception as e:
        print(f"Failed to start Hazelcast container: {e}")
        raise
