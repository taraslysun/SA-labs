import hazelcast

if __name__ == "__main__":
  client = hazelcast.HazelcastClient(
  cluster_name="hello-world", 
  ) 

  # Create a Distributed Map in the cluster
  map = client.get_map("my-distributed-map").blocking() 

  map.put_all({ i:"hello"+str(i) for i in range(1000) })
  print("Map Size:", map.size())