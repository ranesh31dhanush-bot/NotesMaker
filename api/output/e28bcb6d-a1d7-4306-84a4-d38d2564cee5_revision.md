**10-Minute Rapid Revision Sheet: Node.js Event Loop and Call Stack vs Callback Queue vs Microtask Queue**

**Event Loop Phases:**

1. **Timers**: `setTimeout()`, `setInterval()` (minimum delay, not exact timing)
2. **Pending Callbacks**: System-level callbacks (e.g., TCP, file system errors)
3. **Idle/Prepare**: Internal Node.js phase (not interacted with directly)
4. **Poll**: Executes I/O callbacks (e.g., file read, DB response), waits for new I/O events (MOST IMPORTANT)
5. **Check**: `setImmediate()` callbacks
6. **Close Callbacks**: Socket close events, cleanup events

**Memory Trick:** Associate each phase with a keyword:
	* Timers: ⏰ (alarm clocks)
	* Poll: 📦 (waiting for delivery)
	* Check: ⚡ (run immediates now)

**Call Stack vs Callback Queue vs Microtask Queue:**

1. **Call Stack**: Execution engine, where functions are executed (LIFO)
2. **Callback Queue**: Stores `setTimeout`, `setInterval`, I/O callbacks, `setImmediate`
3. **Microtask Queue**: High-priority async tasks (Promise.then(), Promise.catch(), queueMicrotask(), process.nextTick())

**Priority Order:**

1. Call Stack
2. process.nextTick()
3. Microtask Queue (Promises)
4. Callback Queue (Timers, I/O)

**Golden Rules:**

1. If stack is not empty, nothing runs.
2. After stack is empty, run all microtasks.
3. Then, take one callback from the callback queue.

**Mental Model:** Visualize the priority order as a stack with queues:
	[ Call Stack ]
      ↓
	[ process.nextTick Queue ]
      ↓
	[ Microtask Queue ]
      ↓
	[ Callback Queue ]

**Real-World Analogy:** Chef cooking, urgent VIP orders, and normal orders.

**Key Takeaways:**

* Node.js event loop has 6 phases, each with its own queue.
* Poll phase controls the flow.
* Call Stack, Microtask Queue, and Callback Queue have different priorities.
* process.nextTick() has the highest priority in Node.js.

**Revision Time:** 10 minutes

**Recall Questions:**

1. What are the 6 phases of the Node.js event loop?
2. What is the purpose of the Poll phase?
3. What is the difference between Call Stack, Microtask Queue, and Callback Queue?
4. What is the priority order of these queues?
5. What is the purpose of process.nextTick() in Node.js?

**Answer Key:**

1. Timers, Pending Callbacks, Idle/Prepare, Poll, Check, Close Callbacks
2. Executes I/O callbacks, waits for new I/O events
3. Call Stack: execution engine, Microtask Queue: high-priority async, Callback Queue: lower-priority async
4. Call Stack, process.nextTick(), Microtask Queue, Callback Queue
5. Highest priority in Node.js, even higher than microtasks