---
marp: true
theme: default
paginate: true
---

# Session 1 — SQL Querying
### For Web Dev Students with Python Background
**Source:** Harvard CS50 SQL | cs50.harvard.edu/sql
**Duration:** 1 Hour | 20 min teach → 25 min practice → 15 min test

---

## Session Goals

By the end of this session, students will be able to:

- Retrieve data from a database table using `SELECT`
- Filter rows using `WHERE`, `LIKE`, `BETWEEN`, and `NULL` checks
- Sort and limit results with `ORDER BY` and `LIMIT`
- Perform calculations using aggregate functions
- Rename output columns using `AS`

---

## Minimum Concepts Needed for Web Apps

| Concept | Why Web Apps Need It |
|---------|----------------------|
| `SELECT` | Fetch users, posts, products |
| `WHERE` | Login check, search, filter |
| `LIKE` | Search bar functionality |
| `ORDER BY` | "Latest posts", "Top rated" |
| `LIMIT` | Pagination |
| `COUNT / AVG` | Dashboard stats, analytics |
| `NULL` checks | Optional fields (bio, avatar) |

---

## The Python → SQL Mental Model

> Students already know Python. Use this bridge.

| Python | SQL Equivalent |
|--------|----------------|
| `list` of dicts | Table |
| Dict key | Column name |
| One dict | One row |
| `for row in data:` | `SELECT` |
| `if row['year'] == 2024` | `WHERE "year" = 2024` |
| `sorted(data, key=...)` | `ORDER BY` |
| `data[:10]` | `LIMIT 10` |
| `len(data)` | `COUNT(*)` |

**Opening question:** *"If you had 1000 blog posts in a Python list, how would you find all posts from 2024 with more than 500 views?"* → Let them answer → Then show SQL does it in 2 lines.

---

## Lesson Breakdown (20 minutes)

```
00:00 – 02:00   Warm-up question + Python bridge analogy
02:00 – 05:00   What is SQL? What is a database?
05:00 – 10:00   SELECT, FROM, LIMIT
10:00 – 15:00   WHERE, AND, OR, NOT, NULL
15:00 – 18:00   LIKE, BETWEEN, ORDER BY
18:00 – 20:00   Aggregate functions + AS
```

---

## What is a Database?

A database is a structured system that lets you:

**Create → Read → Update → Delete** data (CRUD)

SQL = Structured Query Language → the language you use to talk to it.

> Think of it like Excel, but:
> - Handles millions of rows without crashing
> - Multiple people can read/write at the same time
> - You ask for exactly what you need — nothing more

---

## Tool 1 — SELECT + FROM

*"Give me these columns from this table."*

```sql
-- All columns
SELECT * FROM "posts";

-- Specific columns
SELECT "title" FROM "posts";
SELECT "title", "author", "year" FROM "posts";
```

**Teaching tip:** Ask students *"What does `*` mean in Python? (multiplication / args)"* → then explain it means "all" in SQL. Builds memory by contrast.

---

## Tool 2 — LIMIT

*"Only show me the first N rows."*

```sql
SELECT "title" FROM "posts" LIMIT 5;
SELECT "title", "views" FROM "posts" LIMIT 10;
```

**Real-world use:** Every "Latest 5 posts" on a homepage uses `LIMIT`.

---

## Tool 3 — WHERE

*"Only give me rows that match this condition."*

```sql
SELECT "title" FROM "posts" WHERE "year" = 2024;
SELECT "title" FROM "posts" WHERE "year" != 2023;
SELECT "title" FROM "posts" WHERE "views" > 1000;
SELECT "title" FROM "posts" WHERE "published" = 1 AND "year" = 2024;
SELECT "title" FROM "posts" WHERE "year" = 2022 OR "year" = 2024;
```

Comparison operators: `=` `!=` `<>` `<` `>` `<=` `>=`
Logical operators: `AND` `OR` `NOT`

---

## NULL — The Special Case

> NULL does NOT mean zero. It does NOT mean empty string.
> NULL means **"we don't know"**.

```sql
-- Posts with no editor assigned
SELECT "title" FROM "posts" WHERE "editor" IS NULL;

-- Posts that have an editor
SELECT "title" FROM "posts" WHERE "editor" IS NOT NULL;
```

**Common mistake:** Students write `WHERE "editor" = NULL` → this never works.

**Real-world use:** Optional profile fields (bio, phone, avatar) → check with `IS NULL`.

---

## Tool 4 — LIKE

*"Pattern matching — like a simple search."*

```sql
-- Titles containing "python" anywhere
SELECT "title" FROM "posts" WHERE "title" LIKE '%python%';

-- Titles starting with "How"
SELECT "title" FROM "posts" WHERE "title" LIKE 'How%';

-- 4-letter words starting with P, ending in re
SELECT "title" FROM "posts" WHERE "title" LIKE 'P_re';
```

`%` = zero or more characters (wildcard)
`_` = exactly one character

**Real-world use:** Every search bar in a web app uses `LIKE`.

---

## Tool 5 — BETWEEN + ORDER BY

```sql
-- Posts from 2022 to 2024 (inclusive)
SELECT "title" FROM "posts" WHERE "year" BETWEEN 2022 AND 2024;

-- Sort by views, highest first
SELECT "title", "views" FROM "posts" ORDER BY "views" DESC;

-- Sort by year, then by views within same year
SELECT "title" FROM "posts" ORDER BY "year" DESC, "views" DESC;
```

`ASC` = ascending (default) | `DESC` = descending

---

## Tool 6 — Aggregate Functions + AS

*"Do math on your data."*

```sql
SELECT COUNT(*) FROM "posts";
SELECT COUNT("editor") FROM "posts";          -- ignores NULLs
SELECT COUNT(DISTINCT "author") FROM "posts"; -- unique count
SELECT AVG("views") FROM "posts";
SELECT MAX("views") FROM "posts";
SELECT MIN("views") FROM "posts";
SELECT SUM("views") FROM "posts";
SELECT ROUND(AVG("views"), 0) AS "average views" FROM "posts";
```

**`AS` renames the output column** — important for readability in APIs.

---

## Real-World Examples

### Blog Platform
```sql
-- Homepage: latest 5 published posts
SELECT "title", "author" FROM "posts"
WHERE "published" = 1
ORDER BY "created_at" DESC LIMIT 5;

-- Search bar
SELECT "title" FROM "posts" WHERE "title" LIKE '%flask%';

-- Dashboard stat
SELECT COUNT(*) AS "total posts" FROM "posts";
SELECT AVG("views") AS "avg views" FROM "posts";
```

### User Authentication
```sql
-- Login check (always hash passwords — this is simplified)
SELECT * FROM "users" WHERE "email" = 'ali@email.com';

-- Find users with incomplete profiles
SELECT "username" FROM "users" WHERE "bio" IS NULL;
```

---

## Hands-On Practice (25 minutes)

Paste this into DB Browser or SQLiteOnline.com:

```sql
CREATE TABLE "posts" (
  "id" INTEGER, "title" TEXT, "author" TEXT,
  "year" INTEGER, "views" INTEGER, "editor" TEXT
);
INSERT INTO "posts" VALUES
  (1, 'Python Basics', 'Ali', 2022, 1500, 'Sara'),
  (2, 'How to use Flask', 'Sara', 2023, 3200, NULL),
  (3, 'Python for Web Dev', 'Ali', 2024, 800, 'Omar'),
  (4, 'JavaScript vs Python', 'Omar', 2024, 5100, NULL),
  (5, 'SQL in 3 Hours', 'Sara', 2024, 420, 'Ali'),
  (6, 'How Databases Work', 'Ali', 2022, 670, NULL);
```

---

## Exercises (solve in order)

1. Show all post titles
2. Show titles and authors of posts from 2024
3. Show the 3 most viewed posts (title + views)
4. Show posts with "Python" anywhere in the title
5. Show posts that have no editor assigned
6. Show posts from 2022 to 2023, sorted by views descending
7. Show the average views across all posts (rounded to 0 decimals)
8. Count how many posts were written by 'Ali'
9. Show the title of the single most viewed post
10. Show all distinct authors in the table

---

## Common Mistakes Beginners Make

| Mistake | Wrong | Correct |
|---------|-------|---------|
| NULL comparison | `WHERE "editor" = NULL` | `WHERE "editor" IS NULL` |
| Case sensitivity | `select title from posts` (works but bad habit) | `SELECT "title" FROM "posts"` |
| Forgetting quotes | `WHERE title = python` | `WHERE "title" = 'python'` |
| Wrong wildcard | `LIKE 'python'` (exact match) | `LIKE '%python%'` |
| AVG on NULL | Forgetting NULLs are skipped | Use `IS NOT NULL` to be explicit |
| `COUNT(col)` vs `COUNT(*)` | Assuming they're the same | `COUNT(col)` skips NULLs |

---

## Teaching Tips

- **Analogy first, syntax second.** Show the Python equivalent before showing SQL.
- **Run every query live.** Don't show static output — type and execute in front of the class.
- **Ask before telling.** *"What do you think happens if we add `DESC` here?"*
- **Break WHERE conditions progressively.** Start with one condition, then add `AND`/`OR`.
- **NULL is always confusing.** Spend extra 2 minutes here — it trips up even senior devs.
- **Make aggregates tangible.** *"This is exactly what your analytics dashboard calls."*

---

## Session 1 Test (15 minutes)

1. What does `SELECT *` mean?
2. Write a query to find all posts with more than 1000 views.
3. What is the difference between `=` and `LIKE`?
4. What does NULL mean in SQL? How do you filter for it?
5. Write a query to count posts published in 2024.
6. What does `ORDER BY "views" DESC` do?
7. What is the difference between `COUNT(*)` and `COUNT("editor")`?
8. Write a query to show the title of the post with the highest views.

---

## Answer Key

1. Select all columns from the table
2. `SELECT "title" FROM "posts" WHERE "views" > 1000;`
3. `=` is exact match. `LIKE` allows wildcards (`%`, `_`) for patterns.
4. NULL = unknown/missing. Filter with `IS NULL` or `IS NOT NULL` — never `= NULL`
5. `SELECT COUNT(*) FROM "posts" WHERE "year" = 2024;`
6. Sorts results from highest to lowest views
7. `COUNT(*)` counts all rows. `COUNT("editor")` skips rows where editor is NULL.
8. `SELECT "title" FROM "posts" ORDER BY "views" DESC LIMIT 1;`

---

## What's Next — Session 2

> *"We have one table. But real apps have 10, 20, 50 tables that talk to each other. How?"*

Session 2 covers:
- One-to-Many and Many-to-Many relationships
- JOINs — connecting tables
- Subqueries — queries inside queries
- GROUP BY + HAVING — aggregation per group

**Homework:** Find one website you use daily. Try to guess: what tables does its database have?
