# 15Puzzle

The current project presents a parallelized and a distributed solution for solving solving the 15 puzzle problem. We implemented an interesting algorithm named Hash Distributed A* which was developed by Yuu David Jinnai and works in the following way:
- each thread/process has its own open list and closed list
- created nodes will be pushed to its owner
- the owner is decided by hash function shared with all threads
- as the pushing is asynchronous task, it takes no synchonization overhead.

HDA* algorithm in Pseudo code:

HDA*(start, goal)

  incomebuffer[start.zobrist] = {start}
  terminate = {false, false, false,...}
  incumbent = very big atomic integer
  
  initiate threads

    id = getThreadId
    closedlist  = empty
    openlist    = empty
    outgobuffer = {empty, empty, empty,...}

    while true

      if incomebuffer[id] is not empty
        lock(incomebuffer)
        tmp = incomebuffer.retrieveAll
        incomebuffer.clear
        unlock()
      
      if (openlist is empty) or (openlist.f < incumbent)
        terminate[id] = true
        if terminate is all true
	  break
        else
	  continue

      n = open.pop

      duplicate = closed.find(n)      
      if duplicate exist
        if duplicate.f <= n.f
          discard n as duplicate
          continue
      
      if n is goal state
        newPath = getPath(n)
        if newPath.length < incumbent
	  incumbent = newPath.length
          path = newPath
        continue

      closed.add(n)

      for all possible operation op for n
        if op == n.pastop
          continue
        
        nextEdge = apply(n, op)
	
        zobrist = nextEdge.zobrist
        if zobrist == id
          open.push(next)
        else if incomebuffer[zobrist].trylock
          lock(incomebuffer[zobrist])
          incomebuffer[zobrist].push(nextEdge)
          incomebuffer[zobrist].push(outgobuffer[zobrist])
          unlock(incomebuffer[zobrist])
          outgobuffer[zobrist].clear
        else 
          outgobuffer[zobrist].push(nextEdge)
       
  return path
  
Tests:
Multi-threaded:
Initial state:
1   2   3   4
5   6   7   8
9  10   0  11
13  14  15  12

Time elapsed until finding goal state:
0.10312438011169434 seconds

Initial state:
2   3   8   6
1  10   4  11
5  14   9  12
13   0   7  15

Time elapsed until finding goal state:
13.882763624191284 seconds

MPI:
Initial state:
1   2   3   4
5   6   7   8
9  10   0  11
13  14  15  12

Time elapsed until finding goal state:
0.13830304145812988 seconds

Initial state:
2   3   8   6
1  10   4  11
5  14   9  12
13   0   7  15

Time elapsed until finding goal state:
8.812147617340088 seconds

