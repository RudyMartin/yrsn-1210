# Storage & Event Bus Options Explained

## 🔍 Key Distinction

**Redis is NOT for memristive storage!** They serve completely different purposes:

- **Redis** = **Event Bus** (messaging/communication between components)
- **Memristors** = **Constraint Weight Management** (physical devices for adaptive constraints)

---

## 📊 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    YSRN SYSTEM LAYERS                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PERSISTENCE LAYER (Data Storage)                          │
│  ├── ChromaDB (vector embeddings)                          │
│  ├── File-based (JSONL files)                              │
│  └── In-memory (testing)                                   │
│                                                             │
│  EVENT BUS LAYER (Communication)                           │
│  ├── Redis (distributed messaging) ← THIS IS WHERE REDIS IS │
│  ├── Kafka (enterprise messaging)                          │
│  └── In-memory (single-process)                            │
│                                                             │
│  MEMRISTOR LAYER (Constraint Weights)                      │
│  ├── Physical memristors (hardware)                        │
│  └── Virtual memristors (software simulation)              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Persistence Layer (Data Storage)

### Purpose
**Store context embeddings and metadata** - This is where your actual data lives.

### Options

#### 1. **ChromaDB** (Vector Database) ✅ Recommended for Production
- **What:** Vector database optimized for similarity search
- **Stores:** Context embeddings, metadata, documents
- **Use Case:** Production systems, similarity search
- **Setup:** Local file or remote server
- **Cost:** Free (open source)

```python
# Configuration
YSRN_DB_TYPE=chromadb
YSRN_DB_PATH=./data/chroma
```

#### 2. **File-based** (JSONL Files)
- **What:** Simple file storage using JSONL format
- **Stores:** Contexts in text files
- **Use Case:** Local development, simple deployments
- **Setup:** Just specify a directory
- **Cost:** Free

```python
# Configuration
YSRN_DB_TYPE=file
YSRN_DB_PATH=./data/files
```

#### 3. **In-Memory** (Testing)
- **What:** Python dictionary in RAM
- **Stores:** Contexts temporarily
- **Use Case:** Unit tests, quick prototyping
- **Setup:** No setup needed
- **Cost:** Free (but data lost on restart)

```python
# Configuration
YSRN_DB_TYPE=in_memory
```

### Logic for Choosing

| Scenario | Recommended Option | Reason |
|----------|-------------------|--------|
| Production | ChromaDB | Fast similarity search, scalable |
| Development | File-based | Simple, no server needed |
| Testing | In-memory | Fast, isolated, no cleanup |

---

## 📡 Event Bus Layer (Communication)

### Purpose
**Decoupled communication between components** - Components publish/subscribe to events without knowing about each other.

### Options

#### 1. **In-Memory** (Current Default) ✅ Works for Single Process
- **What:** Python dictionary storing event handlers
- **Use Case:** Single-process applications, testing
- **Limitation:** Doesn't work across multiple processes/servers
- **Setup:** No setup needed
- **Cost:** Free

```python
# Configuration
YSRN_EVENT_BUS_TYPE=in_memory
```

**How it works:**
```python
# Component A publishes event
await event_bus.publish(ContextRetrievedEvent(...))

# Component B receives event (same process)
# But Component C on another server won't receive it!
```

#### 2. **Redis** (Distributed) ⚠️ Not Yet Implemented
- **What:** Redis Pub/Sub for distributed messaging
- **Use Case:** Multiple servers, microservices, distributed systems
- **Benefit:** Works across processes, servers, containers
- **Setup:** Requires Redis server
- **Cost:** Free (open source)

```python
# Configuration
YSRN_EVENT_BUS_TYPE=redis
YSRN_EVENT_BUS_HOST=localhost
YSRN_EVENT_BUS_PORT=6379
```

**How it works:**
```python
# Server A publishes event
await event_bus.publish(ContextRetrievedEvent(...))

# Server B receives event (different server!)
# Server C receives event (another server!)
# All servers in the cluster get the event
```

#### 3. **Kafka** (Enterprise) ⚠️ Not Yet Implemented
- **What:** Apache Kafka for high-throughput messaging
- **Use Case:** Large-scale systems, high message volume
- **Benefit:** Very scalable, persistent message queue
- **Setup:** Requires Kafka cluster
- **Cost:** Free (open source, but complex setup)

```python
# Configuration
YSRN_EVENT_BUS_TYPE=kafka
YSRN_EVENT_BUS_HOST=localhost
YSRN_EVENT_BUS_PORT=9092
YSRN_EVENT_BUS_TOPIC=ysrn_events
```

### Logic for Choosing

| Scenario | Recommended Option | Reason |
|----------|-------------------|--------|
| Single server | In-memory | Simple, no dependencies |
| Multiple servers | Redis | Distributed, easy setup |
| High volume | Kafka | Scalable, persistent |

### Why Redis for Event Bus?

**Redis is NOT storage** - it's a **message broker**:

```
Component A → Redis Pub/Sub → Component B
              (messaging)      (receives event)
```

**Benefits:**
- ✅ Decoupled components (don't know about each other)
- ✅ Works across multiple servers
- ✅ Fast (in-memory messaging)
- ✅ Simple setup (single Redis server)

---

## 🔬 Memristor Layer (Constraint Weights)

### Purpose
**Adaptive constraint weight management** - NOT storage, but constraint importance tuning.

### What are Memristors?

**Memristors are physical devices** (or software simulations) that:
- Store constraint weights as **resistance values**
- Adapt weights based on **voltage pulses** (training signals)
- Provide **non-volatile** weight storage (persists when powered off)
- Enable **analog tuning** (continuous weight values)

### NOT Storage for Data!

Memristors are **NOT** for storing:
- ❌ Context embeddings
- ❌ Query results
- ❌ Database records

Memristors are **FOR** storing:
- ✅ Constraint weights (importance values)
- ✅ Learning state (how important each constraint is)
- ✅ Adaptive parameters (that change during training)

### Options

#### 1. **Virtual Memristor** (Software Simulation) ✅ Current
- **What:** Software model of memristor behavior
- **Use Case:** Development, testing, simulation
- **Stores:** Constraint weights in memory/disk
- **Setup:** No hardware needed

```python
# Virtual memristor for constraint weights
memristor = VirtualMemristor()
weight = memristor.get_constraint_weight()  # Returns 0.0 to 1.0
```

#### 2. **Physical Memristor** (Hardware) ⚠️ Future
- **What:** Actual memristor hardware devices
- **Use Case:** Embedded systems, edge devices
- **Stores:** Constraint weights in physical resistance
- **Setup:** Requires memristor hardware

```python
# Physical memristor interface
memristor = PhysicalMemristorInterface(device_id="memristor_1")
resistance = memristor.read_resistance(index=0)  # Read from hardware
```

### How Memristors Work

```
Training Signal (voltage pulse)
    ↓
Memristor Device
    ↓
Resistance Changes (R_on → R_off)
    ↓
Constraint Weight Updates (0.0 → 1.0)
    ↓
Affects Query Processing
```

**Example:**
- Low resistance (R_on) = High constraint importance (weight = 1.0)
- High resistance (R_off) = Low constraint importance (weight = 0.0)
- Voltage pulses during training change resistance
- Resistance maps to constraint weights

---

## 🔄 Complete Data Flow

### Query Processing Flow

```
1. Query comes in
   ↓
2. Encoder creates embedding (OpenAI/Sentence Transformers)
   ↓
3. Persistence searches for similar contexts (ChromaDB/File)
   ↓
4. YSRN Engine classifies contexts (R/S/N decomposition)
   ↓
5. Event Bus publishes "ContextRetrieved" event (Redis/In-memory)
   ↓
6. Other components react to event (decoupled)
```

### Constraint Weight Flow

```
1. Training signal arrives
   ↓
2. Memristor receives voltage pulse
   ↓
3. Resistance changes (physical or virtual)
   ↓
4. Constraint weight updated
   ↓
5. Weight affects query processing
```

---

## 📋 Configuration Examples

### Example 1: Single Server (Development)
```bash
# Storage: File-based (simple)
YSRN_DB_TYPE=file
YSRN_DB_PATH=./data

# Event Bus: In-memory (single process)
YSRN_EVENT_BUS_TYPE=in_memory

# Memristor: Virtual (software)
# (No config needed - uses virtual memristor by default)
```

### Example 2: Distributed System (Production)
```bash
# Storage: ChromaDB (vector search)
YSRN_DB_TYPE=chromadb
YSRN_DB_PATH=./data/chroma

# Event Bus: Redis (distributed messaging)
YSRN_EVENT_BUS_TYPE=redis
YSRN_EVENT_BUS_HOST=redis-server
YSRN_EVENT_BUS_PORT=6379

# Memristor: Virtual (or physical if hardware available)
# (No config needed)
```

### Example 3: High-Scale System
```bash
# Storage: ChromaDB cluster
YSRN_DB_TYPE=chromadb
YSRN_DB_HOST=chromadb-cluster
YSRN_DB_PORT=8000

# Event Bus: Kafka (high throughput)
YSRN_EVENT_BUS_TYPE=kafka
YSRN_EVENT_BUS_HOST=kafka-cluster
YSRN_EVENT_BUS_PORT=9092

# Memristor: Physical (if hardware available)
# (Would require hardware interface)
```

---

## 🎯 Decision Matrix

### When to Use What?

#### Persistence (Data Storage)
- **ChromaDB:** Production, need similarity search
- **File:** Development, simple deployments
- **In-memory:** Testing only

#### Event Bus (Communication)
- **In-memory:** Single server, testing
- **Redis:** Multiple servers, microservices
- **Kafka:** High volume, enterprise scale

#### Memristor (Constraint Weights)
- **Virtual:** Always (unless you have physical hardware)
- **Physical:** Embedded systems with memristor chips

---

## ❓ Common Questions

### Q: Is Redis for storing my data?
**A:** No! Redis is for **event messaging**, not data storage. Use ChromaDB or file-based for data.

### Q: Can I use Redis for memristive storage?
**A:** No! Memristors are physical devices (or software models) for constraint weights, not a storage system.

### Q: What stores my context embeddings?
**A:** The **Persistence Layer** (ChromaDB, File, or In-memory) stores embeddings.

### Q: What does Redis do then?
**A:** Redis (when implemented) will be the **Event Bus** - it routes events between components.

### Q: Where are constraint weights stored?
**A:** Constraint weights come from **Memristors** (virtual or physical), not from Redis or persistence layer.

---

## 📚 Summary

| Component | Purpose | Options | Current Status |
|-----------|---------|---------|----------------|
| **Persistence** | Store embeddings/data | ChromaDB, File, In-memory | ✅ All implemented |
| **Event Bus** | Component communication | In-memory, Redis, Kafka | ✅ In-memory done, Redis/Kafka TODO |
| **Memristor** | Constraint weights | Virtual, Physical | ✅ Virtual exists, Physical TODO |

**Key Takeaway:** Redis is for **messaging** (Event Bus), NOT for data storage or memristive storage!

---

*Storage & Event Bus Explained - December 2025*

