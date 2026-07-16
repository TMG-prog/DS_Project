from consistent_hash import ConsistentHashRing

def test_hash_ring():
    print("--- Initializing Hash Ring ---")
    # initialize with specified values from lab instructions (M=512, K=9)
    ring = ConsistentHashRing(slots=512, virtual_servers_per_instance=9)

    # Test 1. Adding Servers
    print("\n[Test 1] Adding physical servers...")
    ring.add_server("Server 1")
    ring.add_server("Server 2")
    ring.add_server("Server 3")
    print(f"Active Replicas: {ring.get_replicas()}")
    print(f"Total allocated slots on ring: {len(ring.ring)} / 512")
    assert len(ring.ring) == 27, "Each of the 3 servers should occupy 9 slots"

    # Test 2. Request Routing
    print("\n[Test 2] Routing random requests clockwise...")
    test_requests = [100027, 100044, 984512, 452135]
    for r_id in test_requests:
        target_slot = ring.hash_request(r_id)
        assigned_server = ring.get_server(r_id)
        print(f"Request {r_id} maps to Slot {target_slot} -> Routed to: {assigned_server}")

    # Test 3. Dynamic Scaling (also testing if integer extraction handles different names cleanly)
    print("\n[Test 3] Scaling Up (Adding S4)...")
    ring.add_server("S4")
    print(f"Updated Replicas: {ring.get_replicas()}")
    print(f"New total slots occupied: {len(ring.ring)}")

    # Test 4. Failure/Removal Handling
    print("\n[Test 4] Simulating node failure (Removing Server 3)...")
    ring.remove_server("Server 3")
    print(f"Remaining Replicas: {ring.get_replicas()}")
    print(f"Remaining slots occupied: {len(ring.ring)}")
    
    # re-route one of the sample requests to make sure system adjusts well
    print(f"Request 100044 now routes to: {ring.get_server(100044)}")
    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    test_hash_ring()
