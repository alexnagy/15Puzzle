import os
import functools
import time
import heapq
from node import Node
from fifteen_puzzle_problem import FifteenPuzzleProblem
import threading


lock = threading.Lock()
event = threading.Event()
node_final = None


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


def hdastar(problem):
    f = memoize(lambda n: n.path_cost + problem.h(n), 'f')
    threads_nr = 4
    # terminate = [False for _ in range(threads_nr)]
    income_buffer = [[] for _ in range(threads_nr)]
    start_node = Node(problem.initial)
    income_buffer[start_node.zbr_hash() % threads_nr].append((f(start_node), start_node))

    threads = []
    for i in range(threads_nr):
        threads.append(threading.Thread(target=hdastrar_thread, args=(problem, income_buffer, i,
                                                                      threads_nr, f)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


def hdastrar_thread(problem, income_buffer, id, threads_nr, f):
    frontier = []
    explored = set()

    while not event.is_set():
        with lock:
            if income_buffer[id]:
                # terminate[id] = False
                while income_buffer[id]:
                    heapq.heappush(frontier, income_buffer[id].pop())

        if not frontier:
            continue

        node = heapq.heappop(frontier)
        node = node[1]

        for exp_f, exp_node in explored:
            if exp_node == node:
                if exp_f < f(node):
                    continue

        if problem.goal_test(node.state):
            event.set()
            global node_final
            node_final = node
            continue

        explored.add((f(node), node))

        for child in node.expand(problem):
            if child == node.parent:
                continue
            zbr = child.zbr_hash() % threads_nr
            if zbr == id:
                heapq.heappush(frontier, (f(child), child))
            else:
                with lock:
                    income_buffer[zbr].append((f(child), child))


def get_tests():
    tests = []
    tests_dir_path = './tests'
    for test_file in os.listdir(tests_dir_path):
        with open(os.path.join(tests_dir_path, test_file)) as f:
            tests.append(tuple(map(int, f.readline().strip().split())))
    return tests


if __name__ == '__main__':
    tests = get_tests()
    problem = FifteenPuzzleProblem(initial=tests[0])
    start = time.time()
    hdastar(problem)
    print(time.time()-start)
    for node in node_final.path():
        print('\n'.join([''.join(['{:4}'.format(node.state[idx+i]) for i in range(4)])
                         for idx in range(0, 16, 4)]), end="\n\n")
