from disk_relations import *
import threading
from threading import Thread
import time

#######################################################################################################
# Locking Stuff
#######################################################################################################
class LockHashTableEntry:
    def __init__(self):
        self.current_transactions_and_locks = list()
        self.waiting_transactions_and_locks = list()

# We will do locking at the level of tuples or above
class LockTable:
    # Different types of locks
    S = 0
    X = 1
    IS = 2
    IX = 3

    # Compatibility matrix
    #compatibility_list = [(IS, IS), (IS, S), (S, IS), (S, S)]
    compatibility_list = [(IS, IS), (IS, S), (S, IS), (S, S), (IX, IX), (IS, IX), (IX, IS)]
    @staticmethod
    def areCompatible(ltype1, ltype2):
        return (ltype1, ltype2) in LockTable.compatibility_list
                
    # Static variables
    lockhashtable = dict()
    condition_objects = dict()
    hashtable_lock = threading.Lock()
    
    @staticmethod
    def woundWait(waiting_transactions_and_locks_list, transaction_id):
        ############################################
        ####
        #### Implement wound-wait here. It is a deadlock prevention technique. 
        ####
        #### Iterate through the waiting transactions_and_locks_list and if there are younger transactions (tID > transaction_id )
        #### 
        #### add them to the abortList. The calling function aborts the younger transactions in the getLock() method.
        ####
        #### returns : list of transaction_ids to be aborted.
        ############################################

        # Return the list of transactions to be aborted (empty if none)
        abortList = []
        for tID,lockType in waiting_transactions_and_locks_list:
            if tID > transaction_id  :
                abortList.append(tID)
        return abortList


    @staticmethod
    def getLock(transaction_id, objectid, locktype):
                print(type(objectid))
                # We will be using condition objects to wait -- let's acquire the condition object for this objectid first
                with LockTable.hashtable_lock:
                        if objectid not in LockTable.lockhashtable:
                                LockTable.lockhashtable[objectid] = LockHashTableEntry()
                                LockTable.condition_objects[objectid] = threading.Condition(LockTable.hashtable_lock)
                        cond = LockTable.condition_objects[objectid]

                # Since the same underlying lock is used by all condition objects, when we have acquired the condition,
                # we have also acquired the hashtable_lock
                with cond:
                        while True:
                                e = LockTable.lockhashtable[objectid]
                                print("lock being asked by :", (transaction_id, objectid, locktype))
                                print("e.waiting_transactions_and_locks", e.waiting_transactions_and_locks)
                                print("e.current_transactions_and_locks",e.current_transactions_and_locks)
                                ##if (transaction_id, locktype) in e.waiting_transactions_and_locks:
                                ##      e.waiting_transactions_and_locks.remove( (transaction_id, locktype) )

                                if not e.current_transactions_and_locks:
                                        print("Transaction {} able to get this lock on {}".format(transaction_id, objectid))
                                        if (transaction_id, locktype) in e.waiting_transactions_and_locks:
                                                e.waiting_transactions_and_locks.remove( (transaction_id, locktype) )
                                        e.current_transactions_and_locks.append((transaction_id, locktype))
                                        return True
                                else:
                                        # If there is anyone else waiting, we will wait as well to prevent the possibility of "starvation"
                                        # We will do this even if we are compatible with the locks that are being held right now
                                        # i.e., if we are asking for a S lock, and there is currently an S lock on the object, we can acquire
                                        # the lock but we won't do so if there is another transaction blocked on this object
                                        if not e.waiting_transactions_and_locks:
                                                # Check if the lock we want is compatible with the locks being current held
                                                compatible = all(LockTable.areCompatible(locktype, ltype) for (tid, ltype) in e.current_transactions_and_locks)
                                                if compatible:
                                                        print("Transaction {}: compatible so able to get this lock on {}".format(transaction_id,  objectid))
                                                        e.current_transactions_and_locks.append((transaction_id, locktype))
                                                        return True
                                                else:
                                                        print("Transaction {}: Unable to get this lock on {}, so waiting".format(transaction_id, objectid))
                                                        e.waiting_transactions_and_locks.append((transaction_id, locktype))

                                        elif not (transaction_id, locktype) in e.waiting_transactions_and_locks:
                                                ### Implement wound-wait
                                                for tID,objID in e.waiting_transactions_and_locks:
                                                        print(tID,objID,transaction_id)
                                                        if tID > transaction_id  :
                                                                print("In If for deletion for tid ,objid,transaction_id",(tID,objID,transaction_id))
                                                                TransactionManager.signalAbortTransaction(tID)
                                                e.waiting_transactions_and_locks.append((transaction_id, locktype))

                                        elif (transaction_id, locktype) in e.waiting_transactions_and_locks:
                                                print("Transaction {}: Someone else is waiting for a lock on {} so waiting".format(transaction_id, objectid))


                                # If the lock has not been granted, we must wait for someone to release the lock
                                cond.wait(15)
                                print("Transaction {}: Notified that the lock has been released, or Time Out -- checking again".format(transaction_id))

                                # When the transaction is awake, there is a possibility that it needs to be aborted
                                if TransactionManager.hasBeenAborted(transaction_id):
                                        # Remove the transaction from the waiting list
                                        e.waiting_transactions_and_locks.remove( (transaction_id, locktype) )
                                        return False



    @staticmethod
    def releaseLock(transaction_id, objectid, locktype):
        cond = LockTable.condition_objects[objectid]
        with cond: 
            print("Transaction {}: Releasing lock on {}".format(transaction_id, objectid))
            e = LockTable.lockhashtable[objectid]
            e.current_transactions_and_locks.remove((transaction_id, locktype))
            if not e.current_transactions_and_locks:
                cond.notifyAll()

    @staticmethod
    def detectDeadlocksAndChooseTransactionsToAbort():
        ############################################
        ####
        #### Your deadlock detection code here -- it should use the lockhashtable to check for deadlocks
        ####
        #### If deadlocks are found, you should create a list of transaction_ids to abort, and return it.
        #### detectDeadlocks() will take care of calling signalAbortTransaction() -- see below
        #### 
        #### Make sure to lock the hash table (using "with" as above) before processing it
        ####
        ############################################

        # Return the list of transactions to be aborted (empty if none)
        #Used the exisiting implementation from \tas\keleher2018projects\2019\project5-transactions\transactions-correct.py
        
        def cycleRemoval():
            visited = []

            def helper(k):
                visited.append(k)
                for x in graph[k]:
                    if x in graph:
                        if x in visited:
                            return k
                        h2 = helper(x)
                        if h2: return h2

                return False
            
            for k in graph.keys():
                h = helper(k)
                if h: return h
                visited = []
            return None

        graph = {}
        for (k, v) in LockTable.lockhashtable.items():
            for w,_ in v.waiting_transactions_and_locks:
                c = set([a[0] for a in v.current_transactions_and_locks])
                if w in graph:
                    graph[w].union(c)
                else:
                    graph[w] = c
        ret = []
        aborted = cycleRemoval()
        while aborted is not None:
            del graph[aborted]
            ret.append(aborted)
            aborted = cycleRemoval()
        print("abort list:",ret)
        return ret

    @staticmethod
    def detectDeadlocks():
        while True:
            print("Running deadlock detection algorithm...")
            time.sleep(10)

            for tid in LockTable.detectDeadlocksAndChooseTransactionsToAbort():
                print("Signaling Transaction {} to abort".format(tid))
                TransactionManager.signalAbortTransaction(tid)

class TransactionManager:
    tm_lock = threading.Lock()
    last_transaction_id = 0
    abortlist = list()

    @staticmethod
    def startTransaction():
        with TransactionManager.tm_lock:
            TransactionManager.last_transaction_id += 1
            return TransactionManager.last_transaction_id

    @staticmethod
    def hasBeenAborted(transaction_id):
        with TransactionManager.tm_lock:
            return transaction_id in TransactionManager.abortlist

    @staticmethod
    def signalAbortTransaction(transaction_id):
        with TransactionManager.tm_lock:
            TransactionManager.abortlist.append(transaction_id)


class TransactionState:
    SERIALIZABLE = 0
    SNAPSHOT_ISO = 1

    def __init__(self):
        self.transaction_id = TransactionManager.startTransaction()
        self.locks = list()
        self.mode = TransactionState.SERIALIZABLE

        # set up per-transaction storage for SNAPSHOT_ISO
        # YOUR CODE HERE
        self.snapshot = dict()
        self.writebuffer = dict()
        self.writeset = set()


    def setMode(self, mode):
        self.mode = mode
    
    # for SNAPSHOT_ISO
    def takeSnapshot(self, rel, attr, reads):
        self.snapshot[rel] = dict()

        for read in reads:
            self.snapshot[rel][(attr,read)] = (rel.getTuple(read)).getAttribute(attr)


    def getAttribute(self, rel, id, attr):
        # modify for SNAPSHOT_ISO
        if self.mode == TransactionState.SNAPSHOT_ISO:
            if rel in self.writebuffer:
                if (attr,id) in self.writebuffer[rel]:
                    return self.writebuffer[rel][(attr,id)]
                else:
                    return self.snapshot[rel][(attr,id)]

            else:
                return self.snapshot[rel][(attr,id)]
        tup = rel.getTuple(id)
        return tup.getAttribute(attr)
    
    def setAttribute(self, rel, id, attr, newval):
        # modify for SNAPSHOT_ISO
        # print "SET ATTRIBUTE {}, id {}, attr {}, k {}".format(rel, id, attr, newval)
        if self.mode == TransactionState.SNAPSHOT_ISO:
            if rel not in self.writebuffer:
                self.writebuffer[rel] =  dict()
            
            self.writebuffer[rel][(attr,id)] = newval
        
            self.writeset.add((rel,attr,id))
        else:
            tup = rel.getTuple(id)
            tup.setAttribute(attr, newval)
        print("trans {} WRITING {}/{} for id {}".format(self.transaction_id, attr, newval, id))



    def abortTransaction(self):
        print("Aborting transaction {}".format(self.transaction_id))
        ###
        ### NEED TO UNDO ALL THE CHANGES HERE FOR THIS TO BE COMPLETE -- IMPLEMENTED AS PART OF LOG MANAGER FOR NEXT ASSIGNMENT
        ###
        for [objectid, locktype] in reversed(self.locks):
            LockTable.releaseLock(self.transaction_id, objectid, locktype)

  
  
    # return true if committed
    def commitTransaction(self):
        print("Committing transaction {}, wb: {}".format(self.transaction_id, self.writebuffer))
        if self.mode == TransactionState.SNAPSHOT_ISO:
            #tup = rel.getTuple(id)
            #tup.setAttribute(attr, newval)
            #(rel,attr,id)
            for write in self.writeset:

                if write[0].getTuple(write[2]).getAttribute(write[1]) != self.snapshot[write[0]][(write[1],write[2])]:
                    self.abortTransaction()
                    return False
            for valid in self.writeset:
                tup = valid[0].getTuple(valid[2])
                tup.setAttribute(valid[1], self.writebuffer[valid[0]][(valid[1],valid[2])])
      




        for [objectid, locktype] in reversed(self.locks):
            LockTable.releaseLock(self.transaction_id, objectid, locktype)

        return True


    def getLock(self, objectid, locktype):
        if LockTable.getLock(self.transaction_id, objectid, locktype):
            self.locks.append([objectid, locktype])
            return True
        else:
            self.abortTransaction()
            return False

    def getXLockRelation(self, relation):
        return [relation.fileName, LockTable.X] in self.locks or self.getLock(relation.fileName, LockTable.X)

    def getSLockRelation(self, relation):
        return [relation.fileName, LockTable.S] in self.locks or self.getLock(relation.fileName, LockTable.S)

    def getXLockTuple(self, relation, primary_id):
        if [relation.fileName, LockTable.IX] not in self.locks and [relation.fileName, LockTable.X] not in self.locks:
            return self.getLock(relation.fileName, LockTable.IX) and self.getLock(primary_id, LockTable.X)
        else:
            return self.getLock(primary_id, LockTable.X)

    def getSLockTuple(self, relation, primary_id):
        if [relation.fileName, LockTable.IS] not in self.locks and [relation.fileName, LockTable.S] not in self.locks:
            return self.getLock(relation.fileName, LockTable.IS) and self.getLock(primary_id, LockTable.S)
        else:
            return self.getLock(primary_id, LockTable.S)
