import math

class ConsistentHashRing:
    def __init__(self, slots=512, virtual_servers_per_instance=9):  # default values of the instruction's specifications
        # initialize an empty ring of size M
        self.M = slots
        self.K = virtual_servers_per_instance
        # this ring maps slots (index 0 to M-1) to their physical server hostnames
        self.ring = {}
        # keep track of active physical servers
        self.physical_servers = set()

    # place incoming client requests onto specific ring slots using a hash function
    # Formula: H(i) = i^2 + 2i + 17 (mod M)
    def hash_request(self, request_id):
        i = int(request_id)
        return (i**2 + 2*i + 17) % self.M

    # place a virtual server instance on a specific ring slot using hash function
    # Formula: Φ(i, j) = i^2 + j^2 + 2j + 25 (mod M)
    def hash_virtual_server(self, server_id_numeric, replica_idx):
        i = int(server_id_numeric)
        j = int(replica_idx)
        return (i**2 + j**2 + 2*j + 25) % self.M

    # helper function to extract numeric IDs from server hostnames
    # falls back to a hash of the string if no numeric ID is present
    def _extract_numeric_id(self, server_hostname):
        digits = ''.join(filter(str.isdigit, server_hostname))
        if digits:
            return int(digits)
        return sum(ord(char) for char in server_hostname)

    # maps K virtual instances of a physical server onto the ring, with linear probing for collision handling
    def add_server(self, server_hostname):
        if server_hostname in self.physical_servers:
            return
        
        self.physical_servers.add(server_hostname)
        server_numeric_id = self._extract_numeric_id(server_hostname)

        for j in range(self.K):
            slot = self.hash_virtual_server(server_numeric_id, j)
            
            # collision handling
            initial_slot = slot
            while slot in self.ring:
                slot = (slot + 1) % self.M
                if slot == initial_slot:
                    raise MemoryError("Consistent Hash Ring is completely full!")
            
            self.ring[slot] = server_hostname

    # removes all virtual instance slot allocations for a physical server
    def remove_server(self, server_hostname):
        if server_hostname not in self.physical_servers:
            return
        
        self.physical_servers.remove(server_hostname)
        # clear all slots associated with this server
        slots_to_remove = [slot for slot, owner in self.ring.items() if owner == server_hostname]
        for slot in slots_to_remove:
            del self.ring[slot]

    # finds the nearest active server slot in the ring (going clockwise from the request slot)
    def get_server(self, request_id):
        if not self.ring:
            return None

        request_slot = self.hash_request(request_id)
        
        # traversal of the ring
        for offset in range(self.M):
            current_slot = (request_slot + offset) % self.M
            if current_slot in self.ring:
                return self.ring[current_slot]
            
        return None

    # returns list of currently tracked physical servers
    def get_replicas(self):
        return list(self.physical_servers)
