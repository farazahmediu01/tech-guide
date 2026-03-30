---
marp: true
theme: default
paginate: true
---

# Session 3 — SQL Designing
### For Web Dev Students with Python Background
**Source:** Harvard CS50 SQL | cs50.harvard.edu/sql
**Duration:** 1 Hour | 20 min teach → 25 min practice → 15 min test

---

## Session Goals

By the end of this session, students will be able to:

- Design a database schema from real-world requirements
- Write `CREATE TABLE` statements with proper data types
- Apply column constraints: `NOT NULL`, `UNIQUE`, `CHECK`, `DEFAULT`
- Link tables using `PRIMARY KEY` and `FOREIGN KEY`
- Modify existing tables using `ALTER TABLE`
- Read and inspect schemas using `.schema`

---

## Minimum Concepts Needed for Web Apps

| Concept | Why Web Apps Need It |
|---------|----------------------|
| `CREATE TABLE` | Building your app's database from scratch |
| Data types | Store numbers, text, dates correctly |
| `NOT NULL` | Required fields (username, email) |
| `UNIQUE` | Prevent duplicate emails, usernames |
| `DEFAULT` | Auto timestamps, default status values |
| `CHECK` | Validate status fields ('active'/'inactive') |
| `FOREIGN KEY` | Enforce relationships — no orphan data |
| `ALTER TABLE` | Add columns as app features grow |
| Composite PK | Prevent duplicate enrollments, attendance rows |

---

## Lesson Breakdown (20 minutes)

```
00:00 – 02:00   Warm-up: "Design a student attendance system — what tables?"
02:00 – 07:00   The 5-step design workflow
07:00 – 12:00   CREATE TABLE + data types + constraints
12:00 – 16:00   PRIMARY KEY + FOREIGN KEY (with enforcement)
16:00 – 18:00   ALTER TABLE operations
18:00 – 20:00   .schema inspection + normalization recap
```

---

## The 5-Step Design Workflow

> **Always do this before writing a single line of SQL.**

```
Step 1: Identify entities
        → What "things" exist in this system?
        → Examples: User, Post, Order, Tag, Course

Step 2: Identify relationships
        → How do entities connect? (1:1, 1:Many, Many:Many)

Step 3: Normalize
        → Remove duplication. Each fact stored exactly once.

Step 4: Define types + constraints
        → What data is allowed? What is required?

Step 5: Write the schema
        → CREATE TABLE statements, then test
```

---

## 📺 Watch — Chat App Database Design

> **Show this before the mini project — it's a perfect real-world case study**

**[Database Design for Chat Application](https://www.youtube.com/watch?v=xL_tYrEcP9M)**

Key ideas to discuss after watching:
- A chat app has: **Users, Conversations, Messages**
- A conversation has **many messages** (1:Many)
- A conversation has **many participants** (Many:Many → needs junction table)
- Messages belong to a user AND a conversation (two FKs)
- Timestamps are critical — `DEFAULT CURRENT_TIMESTAMP`

**Discussion question:** *"Before writing any SQL — draw the ERD for WhatsApp. What tables do you see?"*

---

## Data Types in SQLite

| Type | Use For | Example |
|------|---------|---------|
| `INTEGER` | IDs, counts, boolean (0/1) | `user_id`, `published` |
| `REAL` | Decimals, prices | `rating`, `price` |
| `TEXT` | Names, emails, content | `username`, `bio` |
| `NUMERIC` | Dates, timestamps | `created_at`, `birthdate` |
| `BLOB` | Raw files (rare in web apps) | Profile photo binary |

**Tip:** When in doubt, use `TEXT` for strings and `NUMERIC` for dates.

---

## Column Constraints

| Constraint | What It Does | Example |
|-----------|-------------|---------|
| `NOT NULL` | Field is required — cannot be empty | `"email" TEXT NOT NULL` |
| `UNIQUE` | No two rows can share this value | `"username" TEXT UNIQUE` |
| `DEFAULT x` | Auto-fill value if not provided | `DEFAULT CURRENT_TIMESTAMP` |
| `CHECK(...)` | Reject invalid values | `CHECK("role" IN ('admin','user'))` |
| `PRIMARY KEY` | Unique row identifier | `PRIMARY KEY("id")` |
| `FOREIGN KEY` | Links to another table's PK | `FOREIGN KEY("user_id") REFERENCES "users"("id")` |

---

## CREATE TABLE — Full Example

```sql
CREATE TABLE "users" (
    "id"        INTEGER,
    "username"  TEXT    NOT NULL UNIQUE,
    "email"     TEXT    NOT NULL UNIQUE,
    "role"      TEXT    NOT NULL DEFAULT 'reader'
                CHECK("role" IN ('admin', 'editor', 'reader')),
    "joined_at" NUMERIC NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY("id")
);
```

**Read this line by line with students:**
- `id` → auto-increment integer, unique identifier
- `username` → required AND must be unique across all users
- `role` → required, defaults to 'reader', only 3 valid values
- `joined_at` → auto-fills with current date/time on insert

---

## FOREIGN KEY — Enforcing Relationships

```sql
CREATE TABLE "posts" (
    "id"        INTEGER,
    "title"     TEXT    NOT NULL,
    "content"   TEXT,
    "published" INTEGER NOT NULL DEFAULT 0,
    "author_id" INTEGER NOT NULL,
    "created_at" NUMERIC NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY("id"),
    FOREIGN KEY("author_id") REFERENCES "users"("id")
);
```

**What this enforces:**
- You cannot insert a post with an `author_id` that doesn't exist in `users`
- If you try → database throws an error
- This prevents "orphan" data — posts with no real author

---

## Composite Primary Key

Used in junction tables where no single column is unique — but the **combination** is.

```sql
CREATE TABLE "post_tags" (
    "post_id" INTEGER NOT NULL,
    "tag_id"  INTEGER NOT NULL,
    PRIMARY KEY("post_id", "tag_id"),
    FOREIGN KEY("post_id") REFERENCES "posts"("id"),
    FOREIGN KEY("tag_id")  REFERENCES "tags"("id")
);
```

**Why:** A post can appear many times (for different tags). A tag can appear many times (for different posts). But the same post+tag combination should only appear ONCE.

---

## ALTER TABLE — Evolving Your Schema

As your app grows, you'll need to change tables:

```sql
-- Rename a table
ALTER TABLE "posts" RENAME TO "articles";

-- Add a new column
ALTER TABLE "articles" ADD COLUMN "views" INTEGER DEFAULT 0;

-- Rename a column
ALTER TABLE "articles" RENAME COLUMN "content" TO "body";

-- Remove a column
ALTER TABLE "articles" DROP COLUMN "body";

-- Delete entire table (careful!)
DROP TABLE "articles";
```

**Teaching tip:** DROP TABLE is permanent. It cannot be undone. Always backup first.

---

## Inspect Your Schema

```sql
-- See all tables in the database
.tables

-- See the full CREATE statement for all tables
.schema

-- See the CREATE statement for one table
.schema users
```

Use `.schema` to verify your design looks exactly as intended before inserting data.

---

## Real-World Example 1 — Chat Application

Based on the YouTube video reference:

```sql
CREATE TABLE "users" (
    "id"       INTEGER,
    "username" TEXT NOT NULL UNIQUE,
    "joined"   NUMERIC DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY("id")
);

CREATE TABLE "conversations" (
    "id"      INTEGER,
    "created" NUMERIC DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY("id")
);

CREATE TABLE "participants" (  -- M:M junction
    "user_id"         INTEGER NOT NULL,
    "conversation_id" INTEGER NOT NULL,
    PRIMARY KEY("user_id", "conversation_id"),
    FOREIGN KEY("user_id")         REFERENCES "users"("id"),
    FOREIGN KEY("conversation_id") REFERENCES "conversations"("id")
);

CREATE TABLE "messages" (
    "id"              INTEGER,
    "content"         TEXT NOT NULL,
    "sent_at"         NUMERIC DEFAULT CURRENT_TIMESTAMP,
    "sender_id"       INTEGER NOT NULL,
    "conversation_id" INTEGER NOT NULL,
    PRIMARY KEY("id"),
    FOREIGN KEY("sender_id")       REFERENCES "users"("id"),
    FOREIGN KEY("conversation_id") REFERENCES "conversations"("id")
);
```

---

## Real-World Example 2 — E-Commerce (Customer → Orders)

```sql
CREATE TABLE "customers" (
    "id"    INTEGER,
    "name"  TEXT    NOT NULL,
    "email" TEXT    NOT NULL UNIQUE,
    PRIMARY KEY("id")
);

CREATE TABLE "products" (
    "id"    INTEGER,
    "name"  TEXT NOT NULL,
    "price" REAL NOT NULL CHECK("price" > 0),
    PRIMARY KEY("id")
);

CREATE TABLE "orders" (
    "id"          INTEGER,
    "customer_id" INTEGER NOT NULL,
    "placed_at"   NUMERIC DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY("id"),
    FOREIGN KEY("customer_id") REFERENCES "customers"("id")
);

CREATE TABLE "order_items" (  -- M:M junction with extra column
    "order_id"   INTEGER NOT NULL,
    "product_id" INTEGER NOT NULL,
    "quantity"   INTEGER NOT NULL DEFAULT 1 CHECK("quantity" > 0),
    PRIMARY KEY("order_id", "product_id"),
    FOREIGN KEY("order_id")   REFERENCES "orders"("id"),
    FOREIGN KEY("product_id") REFERENCES "products"("id")
);
```

---

## Hands-On Practice — Mini Project (25 minutes)

**Design a Student Attendance System** from scratch.

**Requirements (read aloud):**
- Students have a name and email
- Teachers have a name and subject
- Classes have a name, a teacher, and a date
- Students attend classes — mark each as: present, absent, or late

**Step 1 (5 min):** Draw the ERD on paper
- What are the entities?
- What type of relationship exists between Students and Classes?
- Where do the foreign keys go?

**Step 2 (15 min):** Write the full schema (CREATE TABLE statements)

**Step 3 (5 min):** Test by inserting 2 students, 1 teacher, 2 classes, 3 attendance records

---

## Reference Solution

```sql
CREATE TABLE "students" (
    "id"    INTEGER,
    "name"  TEXT NOT NULL,
    "email" TEXT NOT NULL UNIQUE,
    PRIMARY KEY("id")
);

CREATE TABLE "teachers" (
    "id"      INTEGER,
    "name"    TEXT NOT NULL,
    "subject" TEXT NOT NULL,
    PRIMARY KEY("id")
);

CREATE TABLE "classes" (
    "id"         INTEGER,
    "name"       TEXT NOT NULL,
    "teacher_id" INTEGER NOT NULL,
    "date"       NUMERIC NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY("id"),
    FOREIGN KEY("teacher_id") REFERENCES "teachers"("id")
);

CREATE TABLE "attendance" (
    "student_id" INTEGER NOT NULL,
    "class_id"   INTEGER NOT NULL,
    "status"     TEXT NOT NULL
                 CHECK("status" IN ('present', 'absent', 'late')),
    PRIMARY KEY("student_id", "class_id"),
    FOREIGN KEY("student_id") REFERENCES "students"("id"),
    FOREIGN KEY("class_id")   REFERENCES "classes"("id")
);
```

---

## What Good Design Looks Like vs Bad

| ❌ Bad Design | ✅ Good Design |
|--------------|----------------|
| Store author name inside posts table | Separate `authors` table with FK |
| No constraints on email | `NOT NULL UNIQUE` on email |
| Status as free text | `CHECK("status" IN ('active','inactive'))` |
| No timestamps | `DEFAULT CURRENT_TIMESTAMP` on created_at |
| One giant table with 30 columns | Normalized tables with clear relationships |
| No FOREIGN KEY | Add `REFERENCES` to enforce data integrity |
| Composite PK missing in junction | Always add `PRIMARY KEY(col1, col2)` |

---

## Common Mistakes Beginners Make

| Mistake | Example | Fix |
|---------|---------|-----|
| Forgetting `NOT NULL` | Email can be NULL | Add `NOT NULL` to required fields |
| No `UNIQUE` on email | Two users with same email | Add `UNIQUE` constraint |
| Wrong CHECK syntax | `CHECK role = 'admin'` | `CHECK("role" IN ('admin','user'))` |
| Skipping FOREIGN KEY | author_id with no REFERENCES | Always add `REFERENCES` clause |
| Missing junction table | Trying 1 column for M:M | Create a proper junction table |
| Forgetting composite PK | Duplicate attendance rows | `PRIMARY KEY("student_id", "class_id")` |
| DROP TABLE in production | Data gone forever | Always backup before dropping |

---

## Teaching Tips

- **Step 1 is ALWAYS drawing.** Never let students write SQL before they've drawn the ERD on paper.
- **Use the chat app video.** It shows a complete real-world design decision process — more valuable than a textbook example.
- **Build the bad version first.** Show a single bloated table → then show why it breaks → then redesign it.
- **CHECK is underused.** Emphasize it prevents an entire category of bugs at the database level.
- **Composite PK confusion is common.** Draw two columns forming one unique key — like a coordinate (x,y).
- **ALTER TABLE is daily work.** Tell students: every app you ever work on will need schema changes.

---

## Session 3 Test (15 minutes)

1. What is normalization? Why does it matter?
2. What does `NOT NULL` do? Give a real example.
3. What does `CHECK()` do? Write an example.
4. What is the difference between `PRIMARY KEY` and `FOREIGN KEY`?
5. When would you use a composite primary key? Give a real example.
6. Write a `CREATE TABLE` for a "comments" table: id, content (required), posted_at (auto timestamp), author_id (links to users)
7. How do you add a "views" column (default 0) to an existing "posts" table?

---

## Answer Key

1. Normalization = removing duplication. Each fact is stored once, in one table. Prevents update anomalies.
2. `NOT NULL` forces a value — cannot be left empty. Example: `"email" TEXT NOT NULL` — every user must have an email.
3. `CHECK` validates values before storing. Example: `CHECK("status" IN ('active','inactive'))` — rejects any other value.
4. `PRIMARY KEY` = unique identifier for rows in THIS table. `FOREIGN KEY` = reference to the PK in ANOTHER table.
5. When two columns together form a unique identity. Example: `attendance(student_id, class_id)` — same student can't attend same class twice.
6. `CREATE TABLE "comments" ("id" INTEGER, "content" TEXT NOT NULL, "posted_at" NUMERIC DEFAULT CURRENT_TIMESTAMP, "author_id" INTEGER NOT NULL, PRIMARY KEY("id"), FOREIGN KEY("author_id") REFERENCES "users"("id"));`
7. `ALTER TABLE "posts" ADD COLUMN "views" INTEGER DEFAULT 0;`

---

## 3-Session Summary Reference Card

```
Session 1 — QUERYING
  SELECT, FROM, WHERE, LIKE, BETWEEN, ORDER BY, LIMIT
  NULL handling, Aggregate functions, AS

Session 2 — RELATING
  Primary Key, Foreign Key, Junction Table
  JOIN (INNER, LEFT), Subqueries
  GROUP BY, HAVING, Set Operations (UNION, INTERSECT, EXCEPT)

Session 3 — DESIGNING
  5-Step Design Workflow
  CREATE TABLE, SQLite Data Types
  NOT NULL, UNIQUE, DEFAULT, CHECK
  PRIMARY KEY, FOREIGN KEY, Composite PK
  ALTER TABLE, DROP TABLE, .schema
```

---

## Tools Setup for Classroom

| Tool | Purpose | Install |
|------|---------|---------|
| **DB Browser for SQLite** | Best visual GUI for beginners | sqlitebrowser.org |
| **SQLiteOnline.com** | Zero install — use in browser | sqliteonline.com |
| **CS50.dev** | Official CS50 cloud environment | cs50.dev |

**Recommended for Aptech classroom:** SQLiteOnline.com — no installation needed, works on any machine.

---

## Next Steps for Students

You now know the foundation of SQL:
- **Query** existing data
- **Relate** tables together
- **Design** a database from scratch

**To build web apps, combine this with:**
- Python: `sqlite3` module or SQLAlchemy ORM
- Django: models.py generates SQL automatically
- Flask: SQLAlchemy or Flask-SQLAlchemy

**Practice challenge:** Design the database for Instagram.
*Entities to start with: Users, Posts, Comments, Likes, Followers*
