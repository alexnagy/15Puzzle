import functools
import threading
import time
import os
from priority_queue import TSPriorityQueue
from fifteen_puzzle_problem import FifteenPuzzleProblem
from node import Node
from mpi4py import MPI


def memoize(fn, slot=None, maxsize=32):
    """Memoize fn: make it remember the computed value for any argument list.
    If slot is specified, store result in that slot of first argument.
    If slot is false, use lru_cache for caching the values."""
    if slot:
        def memoized_fn(obj, *args):
            if hasattr(obj, slot):
                return getattr(obj, slot)
            else:
                val = fn(obj, *args)
                setattr(obj, slot, val)
                return val
    else:
        @functools.lru_cache(maxsize=maxsize)
        def memoized_fn(*args):
            return fn(*args)

    return memoized_fn


def recv_thread():
    global is_done, frontier
    while not is_done:
        status = MPI.Status()
        recv_node = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
        if recv_node:
            frontier.put(recv_node)

        if status.tag == STOP:
            print("[Worker %d] Received STOP signal" % rank)
            with lock:
                is_done = True


def hdastrar_worker():
    explored = set()

    print("[Worker %d] Starting recv thread" % rank)
    recv_th = threading.Thread(target=recv_thread)
    recv_th.start()

    global is_done, nr_workers
    while not is_done:
        if frontier.empty():
            continue

        node = frontier.get()

        for exp_f, exp_node in explored:
            if exp_node == node:
                if exp_f < f(node):
                    continue

        if problem.goal_test(node.state):
            print("[Worker %d] Found goal state %s" % (rank, node))
            for nr in range(nr_workers):
                print("[Worker %d] Sending STOP to %d" % (rank, nr))
                comm.send(None, dest=nr, tag=STOP)
            print("[Worker %d] Sending %s to my master" % (rank, node))
            comm.send(node, dest=0)
            continue

        explored.add((f(node), node))

        for child in node.expand(problem):
            if child == node.parent:
                continue
            zbr = child.zbr_hash() % (nr_workers-1) + 1
            if zbr == rank:
                frontier.put(child)
            else:
                with lock:
                    comm.send(child, dest=zbr)


def get_tests():
    tests = []
    tests_dir_path = './tests'
    for test_file in os.listdir(tests_dir_path):
        with open(os.path.join(tests_dir_path, test_file)) as f:
            tests.append(tuple(map(int, f.readline().strip().split())))
    return tests


if __name__ == '__main__':
    nr_workers = 4
    is_done = False
    income_buffer = []
    lock = threading.Lock()
    STOP = 10

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    tests = get_tests()
    problem = FifteenPuzzleProblem(initial=tests[1])
    f = memoize(lambda n: n.path_cost + problem.h(n), 'f')

    if rank == 0:
        print("[Master] Started")
        start_time = time.time()
        start_node = Node(problem.initial)
        zbr = start_node.zbr_hash() % (nr_workers - 1) + 1
        print("[Master] Sending %s to %s" % (start_node, zbr))
        comm.send(start_node, dest=zbr)
        comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG)
        final_node = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG)
        print("[Master] Received %s" % final_node)
        total_time = time.time() - start_time
        for node in final_node.path():
            print('\n'.join([''.join(['{:4}'.format(node.state[idx + i]) for i in range(4)])
                             for idx in range(0, 16, 4)]), end="\n\n")
        print("[Master] Ended in %s seconds" % total_time)
    else:
        print("[Worker %d] Started" % rank)
        frontier = TSPriorityQueue()
        frontier.set_f(f)
        hdastrar_worker()
        print("[Worker %d] Ended" % rank)

