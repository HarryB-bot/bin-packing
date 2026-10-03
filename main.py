"""
AIML431 — Project 1: Resource Allocation
==============================================

Instructions:
  1. Read and understand the problem description in the assignment PDF.
  2. Implement the TODO sections below.
  3. Run:  python3 main.py
  4. The program reads containers.txt, vm_types.txt, pm_capacity.txt
     and outputs the solution obtained by the FF&BF/FF heuristic.
"""

import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


# ╔═══════════════════════════════════════════════════════════════╗
# ║  Provided functions — DO NOT modify                          ║
# ╚═══════════════════════════════════════════════════════════════╝

def read_containers(path=None):
    """Read container sizes from a text file.
    
    Returns: list of ints, in the order they appear in the file.
    """
    if path is None:
        path = os.path.join(DATA_DIR, "containers.txt")
    with open(path) as f:
        sizes = [int(x.strip()) for x in f.readline().strip().split(",") if x.strip()]
    return sizes


def read_vm_types(path=None):
    """Read VM type names and capacities from a text file.
    
    Returns: list of (type_name, capacity) tuples.
    """
    if path is None:
        path = os.path.join(DATA_DIR, "vm_types.txt")
    types = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            name, cap = line.split(",")
            types.append((name.strip(), int(cap.strip())))
    return types


def read_pm_capacity(path=None):
    """Read the PM capacity from a text file.
    
    Returns: int.
    """
    if path is None:
        path = os.path.join(DATA_DIR, "pm_capacity.txt")
    with open(path) as f:
        return int(f.readline().strip())


def first_fit_heuristic():
    # Level 1: containers go into vms
    ctns = read_containers()
    # VM types are already in order but this is just for cases where they aren't
    vm_types = sorted(read_vm_types(), key=lambda x : x[1])
    pm_capacity = read_pm_capacity()
    vms = []
    # Go through all containers and add them to vms
    for cid, size in enumerate(ctns, start=1):
        # Var for if container has been placed
        placed = False
        for vm in vms:
            name = vm[0]
            cap = vm[1]
            used = vm[2]
            # add container if vm has space
            if used + size <= cap:
                vm[2] += size
                vm[3].append((cid, size))
                placed = True
                break
        # No room for container? Find a vm to add then
        if not placed:
            for name, cap in vm_types:
                if cap >= size:
                    new_vm = [name, cap, size, [(cid, size)]]
                    vms.append(new_vm)
                    break
    print(format_vm_list(vms))
    # Level 2: vms to pms
    pms = []
    # Go through all the vms and add them to pms
    for vm in vms:
        vm_cap = vm[1]
        # Get rid of used category for pm output method
        vm_info = (vm[0], vm[1], vm[3])
        placed = False
        # Go through pms
        for pm in pms:
            used = pm[0]
            # Does the vm fit in the pm?
            if used + vm_cap <= pm_capacity:
                pm[0] += vm_cap
                pm[1].append(vm_info)
                placed = True
                break
        if not placed:
            new_pm = [vm_cap, [vm_info]]
            pms.append(new_pm)
    print(format_pm_list(pms, pm_capacity))


def best_fit_heuristic():
    # Level 1: container to vms
    ctns = read_containers()
    # VM types are already in order but this is just for cases where they aren't
    vm_types = sorted(read_vm_types(), key=lambda x : x[1])
    pm_capacity = read_pm_capacity()
    vms = []
    # Go through all containers and add them to vms
    for cid, size in enumerate(ctns, start=1):
        best_vm = None
        min_rem = float("inf")
        # Go through
        for vm in vms:
            cap = vm[1]
            used = vm[2]
            if used + size <= cap:
                remain = cap - (used + size)
                if remain < min_rem:
                    min_rem = remain
                    best_vm = vm
        # Best vm found, add container to vm
        if best_vm is not None:
            best_vm[2] += size
            best_vm[3].append((cid, size))
        # No space or no vms exist, create new vm
        else:
            for name, cap in vm_types:
                if cap >= size:
                    new_vm = [name, cap, size, [(cid, size)]]
                    vms.append(new_vm)
                    break
    print(format_vm_list(vms))
    # Level 2: vms go into pms
    pms = []
    # Go through all the vms and add them to pms
    for vm in vms:
        vm_cap = vm[1]
        # Get rid of used category for pm output method
        vm_info = (vm[0], vm[1], vm[3])

        best_pm = None
        # Set min to big number
        min_rem = float("inf")
        for pm in pms:
            used = pm[0]
            # Does the vm fit in the pm?
            if used + vm_cap <= pm_capacity:
                remain = pm_capacity - (used + vm_cap)
                # Is the current pm the best fit?
                if remain < min_rem:
                    min_rem = remain
                    best_pm = pm
        if best_pm is not None:
            best_pm[0] += vm_cap
            best_pm[1].append(vm_info)
        else:
            pms.append([vm_cap, [vm_info]])
    print(format_pm_list(pms, pm_capacity))


def format_vm_list(vms):
    """Format Level 1 VM allocation for display."""
    lines = []
    for i, (name, cap, _, items) in enumerate(vms, 1):
        items_str = ", ".join(f"c{cid}:{size}" for cid, size in items)
        lines.append(f"    v{i}: ({name}, Cap={cap})  [{items_str}]")
    lines.append(f"    ==> Total VMs used: {len(vms)}")
    return "\n".join(lines)


def format_pm_list(pms, pm_cap):
    """Format Level 2 PM allocation for display."""
    lines = []
    total_containers = 0
    for pi, (used, vm_list) in enumerate(pms, 1):
        parts = []
        for vname, vcap, clist in vm_list:
            total_containers += len(clist)
            inner = " + ".join(f"c{cid}:{size}" for cid, size in clist)
            parts.append(f"({vname}, Cap={vcap})[{inner}]")
        lines.append(f"    p{pi}: [used={used}/{pm_cap}]  " + ", ".join(parts))
    lines.append(f"    ==> Total PMs used: {len(pms)}")
    lines.append(f"    ==> Containers allocated: {total_containers}")
    return "\n".join(lines)


def main():
    """Main driver — reads data, runs heuristic, prints output."""
    containers = read_containers()
    vm_types = read_vm_types()
    pm_capacity = read_pm_capacity()

    print("=" * 65)
    print("  Question 1 — FF&BF/FF Heuristic")
    print("=" * 65)
    print(f"  Containers: {containers}")
    print(f"  VM types:   {vm_types}")
    print(f"  PM capacity: {pm_capacity}")
    print()

    # First fit
    first_fit_heuristic()

    # Best fit
    print("=" * 65)
    print("  Question 2 — BF&BF/BF Heuristic")
    print("=" * 65)
    best_fit_heuristic()
    

if __name__ == "__main__":
    main()
