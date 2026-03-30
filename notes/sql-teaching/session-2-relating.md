---
marp: true
theme: default
paginate: true
---

# Session 2 — SQL Relating
### For Web Dev Students with Python Background
**Source:** Harvard CS50 SQL | cs50.harvard.edu/sql
**Duration:** 1 Hour | 20 min teach → 25 min practice → 15 min test

---

## Session Goals

By the end of this session, students will be able to:

- Understand One-to-Many and Many-to-Many relationships
- Link tables using Primary Keys and Foreign Keys
- Write subqueries (nested queries)
- JOIN multiple tables to get combined results
- Group and filter grouped data with `GROUP BY` and `HAVING`

---

## Minimum Concepts Needed for Web Apps

| Concept | Why Web Apps Need It |
|---------|----------------------|
| One-to-Many | Users → Posts, Teachers → Students |
| Many-to-Many | Students ↔ Courses, Posts ↔ Tags |
| Foreign Key | Connecting tables without duplicating data |
| `JOIN` | Fetch a post AND its author's name in one query |
| `LEFT JOIN` | Show all items even if related data is missing |
| Subquery | "Find posts by authors from Pakistan" |
| `GROUP BY` | Count posts per author, orders per customer |
| `HAVING` | Filter groups: "authors with more than 2 posts" |

---

## The Problem with One Table

Imagine storing author info inside every post row:

| id | title | author_name | author_country | author_email |
|----|-------|-------------|----------------|--------------|
| 1 | Flask Guide | Sara | UAE | sara@x.com |
| 2 | SQL Basics | Sara | UAE | sara@x.com |

**Problems:**
- Sara's email appears in every row she wrote
- If Sara changes email → update 100 rows
- Wasted storage, high risk of inconsistency

**Solution: Separate tables + relationships.**

---

## Lesson Breakdown (20 minutes)

```
00:00 – 02:00   Problem with one table (the "Sara email" example)
02:00 – 06:00   Keys: Primary Key, Foreign Key, Junction Table
06:00 – 09:00   One-to-Many (live ERD drawing)
09:00 – 12:00   Many-to-Many + Junction Table
12:00 – 16:00   JOIN (INNER, LEFT)
16:00 – 18:00   Subqueries
18:00 – 20:00   GROUP BY + HAVING
```

---

## 📺 Watch First — One-to-Many Relationships

> **Before teaching JOINs — show this video (or assign as pre-class homework)**

**[Database Design: One-to-Many Relationships (7 Steps)](https://www.youtube.com/watch?v=-C2olg3SfvU)**

Key ideas from this video to reinforce in class:
- One entity "owns" many others (one author, many posts)
- The "many" side holds the foreign key — NOT the "one" side
- Always draw the relationship before writing any SQL
- Step-by-step: identify entities → identify cardinality → place the foreign key

**Discussion after video:** *"In our blog — which side is 'one' and which is 'many'? Where does the foreign key go?"*

---

## Keys — The Glue of Relational Databases

```
Primary Key (PK)
  → Unique identifier for each row in a table
  → Like a student ID card — no two students have the same one
  → One per table. Never repeats. Never NULL.

Foreign Key (FK)
  → The primary key of ANOTHER table, stored here
  → Creates the link between two tables
  → Can repeat (many posts can have the same author_id)

Junction Table
  → A third table used to handle Many-to-Many
  → Contains two foreign keys, one from each related table
```

---

## One-to-Many Relationship

**Example:** One Author writes Many Posts

```
authors                    posts
┌────┬──────┐             ┌────┬──────────────┬───────────┐
│ id │ name │             │ id │ title        │ author_id │
├────┼──────┤             ├────┼──────────────┼───────────┤
│  1 │ Ali  │ ←──────┐   │  1 │ Python Basics│     1     │
│  2 │ Sara │ ←───┐  └──→│  2 │ Web Dev Tips │     1     │
└────┴──────┘     └─────→│  3 │ Flask Guide  │     2     │
                          └────┴──────────────┴───────────┘
```

The FK (`author_id`) lives on the **"many" side** (posts).

**Other real-world examples:**
- One Customer → Many Orders
- One Teacher → Many Students
- One Classroom → Many Assignments

---

## 📺 Watch Next — Many-to-Many Relationships

> **Show this video before teaching junction tables**

**[How to Correctly Define Many-to-Many Relationships](https://www.youtube.com/watch?v=1eUn6lsZ7c4)**

Key ideas to reinforce:
- You CANNOT put a foreign key on either side alone
- You need a **junction table** (also called a join table or bridge table)
- The junction table holds FK from both sides
- Example: Students ↔ Courses → `enrollments` table in the middle

**Discussion after video:** *"What would the junction table for Posts ↔ Tags look like?"*

---

## Many-to-Many Relationship

**Example:** Posts have many Tags. Tags belong to many Posts.

```
posts                  post_tags              tags
┌────┬──────────┐     ┌─────────┬────────┐   ┌────┬──────────┐
│ id │ title    │     │ post_id │ tag_id │   │ id │ name     │
├────┼──────────┤     ├─────────┼────────┤   ├────┼──────────┤
│  1 │ Python.. │────→│    1    │   1    │←──│  1 │ python   │
│  2 │ Flask...  │    │    1    │   2    │←──│  2 │ web      │
└────┴──────────┘    │    2    │   2    │   │  3 │ sql      │
                      └─────────┴────────┘   └────┴──────────┘
```

**Other real-world examples:**
- Students ↔ Courses (enrollment)
- Users ↔ Groups (membership)
- Products ↔ Orders (order_items)
- Actors ↔ Movies

---

## Subqueries — A Query Inside a Query

*"Answer question B first, use that to answer question A."*

```sql
-- "Find all posts by authors from Pakistan"
SELECT "title" FROM "posts"
WHERE "author_id" IN (
    SELECT "id" FROM "authors"
    WHERE "country" = 'Pakistan'
);
```

**How it works:**
1. Inner query runs first → returns a list of IDs
2. Outer query uses that list in its `WHERE`

**Python analogy:**
```python
pk_authors = [a['id'] for a in authors if a['country'] == 'Pakistan']
posts = [p for p in posts if p['author_id'] in pk_authors]
```

---

## JOIN — Merge Two Tables

*"Combine rows from two tables where a condition matches."*

```sql
-- INNER JOIN: only rows that exist in BOTH tables
SELECT "posts"."title", "authors"."name"
FROM "posts"
JOIN "authors" ON "posts"."author_id" = "authors"."id";
```

```sql
-- LEFT JOIN: all posts, even if author is missing (NULL)
SELECT "posts"."title", "authors"."name"
FROM "posts"
LEFT JOIN "authors" ON "posts"."author_id" = "authors"."id";
```

| JOIN Type | Returns |
|-----------|---------|
| `JOIN` / `INNER JOIN` | Only matching rows in both tables |
| `LEFT JOIN` | All rows from left + matches from right |
| `RIGHT JOIN` | All rows from right + matches from left |
| `FULL JOIN` | All rows from both tables |

---

## JOIN — Real-World Walkthrough

**Scenario:** Show each post with its author's name and country.

```sql
SELECT
    "posts"."title",
    "authors"."name"    AS "author",
    "authors"."country" AS "from"
FROM "posts"
JOIN "authors" ON "posts"."author_id" = "authors"."id";
```

**Result:**
| title | author | from |
|-------|--------|------|
| Python Basics | Ali | Pakistan |
| Flask Guide | Sara | UAE |

**Teaching tip:** Draw this on the board as two overlapping circles (Venn diagram). INNER JOIN = the overlap only.

---

## GROUP BY + HAVING

```sql
-- How many posts has each author written?
SELECT "author_id", COUNT(*) AS "post_count"
FROM "posts"
GROUP BY "author_id";

-- Only authors with more than 1 post
SELECT "author_id", COUNT(*) AS "post_count"
FROM "posts"
GROUP BY "author_id"
HAVING COUNT(*) > 1;
```

**Rule:** `WHERE` filters individual rows. `HAVING` filters groups.

**Real-world use:** "Show customers who placed more than 3 orders."

---

## Set Operations — Combining Result Lists

```sql
-- People who are BOTH authors AND editors
SELECT "name" FROM "authors"
INTERSECT
SELECT "name" FROM "editors";

-- Everyone who is an author OR an editor (no duplicates)
SELECT "name" FROM "authors"
UNION
SELECT "name" FROM "editors";

-- Authors who are NOT editors
SELECT "name" FROM "authors"
EXCEPT
SELECT "name" FROM "editors";
```

---

## Real-World Example — Customer Orders

```sql
-- Show each order with customer name (JOIN)
SELECT "orders"."id", "customers"."name", "orders"."total"
FROM "orders"
JOIN "customers" ON "orders"."customer_id" = "customers"."id";

-- Customers who haven't ordered yet (LEFT JOIN + NULL check)
SELECT "customers"."name"
FROM "customers"
LEFT JOIN "orders" ON "customers"."id" = "orders"."customer_id"
WHERE "orders"."id" IS NULL;

-- Total spent per customer (GROUP BY)
SELECT "customer_id", SUM("total") AS "total_spent"
FROM "orders"
GROUP BY "customer_id"
HAVING SUM("total") > 1000;
```

---

## Hands-On Practice (25 minutes)

```sql
CREATE TABLE "authors" (
  "id" INTEGER PRIMARY KEY, "name" TEXT, "country" TEXT
);
CREATE TABLE "posts" (
  "id" INTEGER PRIMARY KEY, "title" TEXT, "views" INTEGER, "author_id" INTEGER
);
CREATE TABLE "tags" (
  "id" INTEGER PRIMARY KEY, "name" TEXT
);
CREATE TABLE "post_tags" ("post_id" INTEGER, "tag_id" INTEGER);

INSERT INTO "authors" VALUES (1,'Ali','Pakistan'),(2,'Sara','UAE'),(3,'Omar','Pakistan');
INSERT INTO "posts" VALUES
  (1,'Python Basics',1500,1),(2,'Flask Guide',3200,2),
  (3,'SQL in 3 Hours',420,2),(4,'JS vs Python',5100,3),(5,'Web Dev Tips',800,1);
INSERT INTO "tags" VALUES (1,'python'),(2,'web'),(3,'sql'),(4,'javascript');
INSERT INTO "post_tags" VALUES (1,1),(1,2),(2,2),(3,3),(4,1),(4,4),(5,2);
```

---

## Exercises (solve in order)

1. Show each post title with its author's name (JOIN)
2. Show all authors and their posts — include authors with no posts (LEFT JOIN)
3. Using a subquery: find all posts by authors from Pakistan
4. Show how many posts each author has written (GROUP BY + COUNT)
5. Show only authors with more than 1 post (HAVING)
6. Find all tags used by post 1 (subquery + IN)
7. Show titles of all posts tagged 'python' (multi-join)
8. Show average views per author, only where avg > 1000

**Bonus:** What is the most-tagged post? (GROUP BY on post_tags)

---

## Common Mistakes Beginners Make

| Mistake | Example | Fix |
|---------|---------|-----|
| WHERE instead of HAVING | `WHERE COUNT(*) > 2` | `HAVING COUNT(*) > 2` |
| Wrong JOIN direction | LEFT JOIN returns unexpected NULLs | Draw table order before writing |
| Missing ON condition | `JOIN "authors"` (no ON clause) | Always specify `ON table.fk = table.pk` |
| Ambiguous column names | `SELECT "id"` when both tables have `id` | `SELECT "posts"."id"` |
| Forgetting junction table | Trying to link posts and tags directly | Always need a middle table for M:M |
| Subquery returns multiple rows | Using `=` instead of `IN` | `WHERE "id" IN (SELECT ...)` |

---

## Teaching Tips

- **Draw before you code.** Always sketch the two tables and the link between them on the board first.
- **Venn diagram for JOINs.** INNER = overlap. LEFT = left circle + overlap.
- **"Where does the FK go?"** Ask students for every new relationship before revealing the answer.
- **Use the Customer→Orders example.** Every student has shopped online — this makes it instantly real.
- **Show the problem first.** Show what happens with duplicated data in one table → then show the fix.
- **Play the YouTube videos as visual anchors.** Pause at key diagrams and ask: *"Which side has the FK?"*

---

## Session 2 Test (15 minutes)

1. What is a Foreign Key? Where does it go in a One-to-Many relationship?
2. What is the difference between `JOIN` and `LEFT JOIN`?
3. What does `GROUP BY` do? Give a real example.
4. What is the difference between `WHERE` and `HAVING`?
5. Write a query: show the title of all posts by 'Sara' using a subquery.
6. What is a junction table and when do you need one?
7. Write a query: show each author's name and how many posts they have written.

---

## Answer Key

1. FK = a reference to the PK of another table. It lives on the "many" side. (posts.author_id → authors.id)
2. `JOIN` returns only matching rows. `LEFT JOIN` returns all rows from the left table, even with no match.
3. `GROUP BY` groups rows by a column value and lets you aggregate per group. Example: posts per author.
4. `WHERE` filters individual rows before grouping. `HAVING` filters after grouping.
5. `SELECT "title" FROM "posts" WHERE "author_id" = (SELECT "id" FROM "authors" WHERE "name" = 'Sara');`
6. A junction table holds two FKs and is used when two entities have a Many-to-Many relationship.
7. `SELECT "authors"."name", COUNT("posts"."id") AS "post_count" FROM "authors" JOIN "posts" ON "authors"."id" = "posts"."author_id" GROUP BY "authors"."id";`

---

## What's Next — Session 3

> *"We know how to read data. We know how tables relate. Now — how do we BUILD a database the right way?"*

Session 3 covers:
- `CREATE TABLE` with proper types and constraints
- NOT NULL, UNIQUE, CHECK, DEFAULT
- Primary and Foreign Key constraints
- `ALTER TABLE` — modifying existing tables
- Mini project: design an attendance system from scratch
