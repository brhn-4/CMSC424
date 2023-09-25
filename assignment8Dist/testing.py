from disk_relations import *
from transactions import *
import time
from exampletransactions import *

file_path = "relation1"
if os.path.isfile(file_path):
  os.remove(file_path)
  print("'{}' has been deleted".format(file_path))

#####################################################################################################
####
#### Some testing code
####
#####################################################################################################
# Initial Setup
bpool = BufferPool()
r = Relation('relation1')

# Start the transactions

def testingSnapshot():

	print("\n\n\n\n")
	testingSnapshotWriteSkew()

	print("\n\n\n\n")
	testingSnapshotWriteSkew2()

	print("\n\n\n\n")
	testingSnapshotAggregate()

	print("\n\n\n\n")
	testingSnapshotSlowAbort()

	print("\n\n\n\n")
	testingSnapshotReadYourWrites()

# overlapping transactions, not overlapping writesets: both write one var, then read the next, both see the initial value (impossible w/ serializability)
def testingSnapshotWriteSkew():

	# init 0,1 to zeros, so that we can distinguish from the default "10"'s
	set_r_a("0", "0")
	set_r_a("1", "0")

	t = threading.Thread(target=TransactionSnapshotWriteReadWrite, args=(r, "0", "1", "2", 1))
	t.start()

	time.sleep(.2)

	t = threading.Thread(target=TransactionSnapshotWriteReadWrite, args=(r, "1", "0", "3", 1))
	t.start()

	waitChildren()

	res = (get_r_a("0")=="1") and (get_r_a("1")=="1") and (get_r_a("2")=="0") and (get_r_a("3")=="0")
	print("testingSnapshotWriteSkew returns {}".format(res))
	

# non-overlapping transactions: second should see the other's write
def testingSnapshotWriteSkew2():
	# set_r_a("4", "0")
	# set_r_a("5", "0")

	t = threading.Thread(target=TransactionSnapshotWriteReadWrite, args=(r, "5", "4", "6", 0))
	t.start()

	time.sleep(1)
	
	t = threading.Thread(target=TransactionSnapshotWriteReadWrite, args=(r, "4", "5", "7", 0))
	t.start()

	waitChildren()

	res = (get_r_a("4")=="1") and (get_r_a("5")=="1") and (get_r_a("6")=="10") and (get_r_a("7")=="1")
	print("testingSnapshotWriteSkew2 returns {}".format(res))
	
# also overlapping trans, not overlapping writesets: neither should see the other's write, leading both to change "their" variable to make the sum be 100
def testingSnapshotAggregate():
	t = threading.Thread(target=TransactionSnapshotAggregate, args=(r, "8", "9"))
	t.start()

	time.sleep(0.5)

	t = threading.Thread(target=TransactionSnapshotAggregate, args=(r, "9", "8"))
	t.start()

	waitChildren()

	res = (get_r_a("8")=="90") and (get_r_a("9")=="90")
	print("testingSnapshotAggregate returns {}".format(res))


## two writes to same var, first one is slower to commit and should abort
def testingSnapshotSlowAbort():
	t = threading.Thread(target=TransactionSlowWriter, args=(r, "10", "11", 2))
	t.start()

	t = threading.Thread(target=TransactionSlowWriter, args=(r, "10", "12", 1))
	t.start()
	waitChildren()

	res = (get_r_a("10")=="12")
	print("testingSnapshotSlowAbort returns {}".format(res))


# checking that snapshots read their own writes
def testingSnapshotReadYourWrites():

	# init 0,1 to zeros, so that we can distinguish from the default "10"'s
	set_r_a("0", "0")
	set_r_a("1", "0")

	t = threading.Thread(target=TransactionSnapshotReadYourWrites, args=(r, "0", "1", "4"))
	t.start()

	waitChildren()

	res = (get_r_a("0")=="4") and (get_r_a("1")=="4")
	print("testingSnapshotReadYourWrites returns {}".format(res))
	



def get_r_a(id):
	return r.getTuple(id).getAttribute("A")

def set_r_a(id, val):
	r.getTuple(id).setAttribute("A", val)

def waitChildren():
	main_thread = threading.currentThread()
	for t in threading.enumerate():
		if t is not main_thread:
			t.join()
	
testingSnapshot()

### Start a thread to periodically check for deadlocks
#t = threading.Thread(target=LockTable.detectDeadlocks())
#t.start()

### Wait for all the threads to complete
waitChildren()
BufferPool.writeAllToDisk(r)
