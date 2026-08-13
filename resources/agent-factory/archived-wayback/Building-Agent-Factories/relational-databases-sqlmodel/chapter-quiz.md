# Chapter 74 Quiz

> **Archived from:** <https://agentfactory.panaversity.org/docs/Building-Agent-Factories/relational-databases-sqlmodel/chapter-quiz>  
> **Wayback snapshot:** 2026-04-22  
> **Status:** retired from the live site — recovered for offline study.

---

Test your understanding of async database patterns. Choose the best answer for each question.

* * *

## Question 1: Async Engine Configuration​

What's wrong with this engine configuration for a production PostgreSQL database?
    
    
    engine = create_async_engine(  
        "postgresql://user:pass@localhost/db",  
        pool_size=5,  
    )  
    

**A)** Missing `echo=True` for logging **B)** Wrong URL format - should be `postgresql+asyncpg://` **C)** Missing `pool_pre_ping=True` **D)** Both B and C

Answer

**D) Both B and C**

The URL must use the async driver (`postgresql+asyncpg://`), and `pool_pre_ping=True` is essential for managed databases to prevent stale connection errors.

* * *

## Question 2: First Normal Form (1NF)​

Which table violates First Normal Form (1NF)?

**A)** A table with `id`, `name`, and `email` columns **B)** A table with a `tags` column containing "bug, urgent, backend" as a single string **C)** A table with a nullable `description` column **D)** A table with an auto-incrementing primary key

Answer

**B) A table with a`tags` column containing "bug, urgent, backend" as a single string**

1NF requires atomic values. Storing multiple tags in a single string violates atomicity. Use a separate tags table or JSONB array (acceptable in modern databases for simple lists).

* * *

## Question 3: Third Normal Form (3NF)​

What's wrong with this table from a normalization perspective?
    
    
    | task_id | title    | assignee_id | assignee_email    |  
    |---------|----------|-------------|-------------------|  
    | 1       | Fix bug  | 5           | john@example.com  |  
    

**A)** Missing primary key **B)** `assignee_email` depends on `assignee_id`, not `task_id` (3NF violation) **C)** Column names are too short **D)** Nothing wrong - this is properly normalized

Answer

**B)`assignee_email` depends on `assignee_id`, not `task_id` (3NF violation)**

3NF requires no transitive dependencies. `assignee_email` depends on `assignee_id`, which depends on `task_id`. Move email to a separate Workers table.

* * *

## Question 4: When to Denormalize​

When is denormalization acceptable?

**A)** Always - normalized tables are too slow **B)** Never - denormalization causes data anomalies **C)** For audit logs that capture state at time of action **D)** When you don't understand foreign keys

Answer

**C) For audit logs that capture state at time of action**

Audit logs should capture data as it was when an action occurred. If you normalize and the worker's name changes later, your audit log would show the wrong name for historical events.

* * *

## Question 5: Session Import​

Which import gives you the correct AsyncSession for SQLModel?

**A)** `from sqlalchemy.ext.asyncio import AsyncSession` **B)** `from sqlmodel.ext.asyncio.session import AsyncSession` **C)** `from sqlmodel import AsyncSession` **D)** `from sqlalchemy.orm import AsyncSession`

Answer

**B)`from sqlmodel.ext.asyncio.session import AsyncSession`**

SQLModel's AsyncSession extends SQLAlchemy's with the `exec()` method that works properly with SQLModel's `select()`.

* * *

## Question 3: JSONB Columns​

How do you correctly define a JSONB list column in SQLModel for PostgreSQL?

**A)** `tags: list[str] = Field(default_factory=list)` **B)** `tags: list[str] = Field(sa_column=Column(JSONB))` **C)** `tags: list[str] = Field(default_factory=list, sa_column=Column(JSONB, nullable=False, server_default="[]"))` **D)** `tags: JSONB = Field(default=[])`

Answer

**C)`tags: list[str] = Field(default_factory=list, sa_column=Column(JSONB, nullable=False, server_default="[]"))`**

You need both the Python default (`default_factory=list`) and the SQLAlchemy column configuration (`sa_column=Column(JSONB, ...)`) with a server default.

* * *

## Question 4: flush() vs commit()​

When should you use `await session.flush()` instead of `await session.commit()`?

**A)** Always use flush(), never commit() **B)** When you need the database-assigned ID before the transaction ends **C)** When you want to roll back changes **D)** When using SQLite instead of PostgreSQL

Answer

**B) When you need the database-assigned ID before the transaction ends**

`flush()` writes to the database (assigning IDs) but keeps the transaction open. This lets you use the ID for related records before the final commit.

* * *

## Question 5: MissingGreenlet Error​

What causes the MissingGreenlet error in async SQLModel code?

**A)** Missing `await` keyword **B)** Accessing a lazy-loaded relationship in async context **C)** Using sync engine instead of async engine **D)** Forgetting to call `session.refresh()`

Answer

**B) Accessing a lazy-loaded relationship in async context**

When you access `task.assignee` without eager loading, SQLAlchemy tries to load it lazily, which requires special greenlet handling that isn't available in standard async contexts.

* * *

## Question 6: N+1 Prevention​

What's the correct pattern to prevent N+1 queries when loading tasks with their assignees?

**A)** `await session.exec(select(Task).join(Worker))` **B)** `await session.exec(select(Task).options(selectinload(Task.assignee)))` **C)** `await session.exec(select(Task)).all(); [await session.get(Worker, t.assignee_id) for t in tasks]` **D)** `await session.exec(select(Task, Worker))`

Answer

**B)`await session.exec(select(Task).options(selectinload(Task.assignee)))`**

`selectinload` loads the related workers in a single additional query using an IN clause, preventing N+1 queries.

* * *

## Question 7: unique() Requirement​

Why must you call `result.unique().all()` when using selectinload?

**A)** To remove null values **B)** To deduplicate parent objects that may appear multiple times **C)** To sort results **D)** To convert to a list

Answer

**B) To deduplicate parent objects that may appear multiple times**

`selectinload` can create duplicate parent objects in the result set. `unique()` removes these duplicates.

* * *

## Question 8: Self-Referential Relationships​

What's required in `sa_relationship_kwargs` for a self-referential parent relationship?

**A)** `{"lazy": "selectin"}` **B)** `{"remote_side": "Task.id"}` **C)** `{"cascade": "all, delete-orphan"}` **D)** `{"uselist": False}`

Answer

**B)`{"remote_side": "Task.id"}`**

For self-referential relationships, `remote_side` tells SQLAlchemy which side is the "one" in the one-to-many relationship.

* * *

## Question 9: Multiple Foreign Keys​

When a model has two foreign keys to the same table, what must you specify?

**A)** Different table names **B)** `sa_relationship_kwargs={"foreign_keys": "[Model.field_id]"}` **C)** `Relationship(secondary=...)` **D)** `back_populates` with unique names

Answer

**B)`sa_relationship_kwargs={"foreign_keys": "[Model.field_id]"}`**

When there are multiple FKs to the same table, SQLAlchemy can't determine which FK each relationship uses without explicit specification.

* * *

## Question 10: Transaction Rollback​

What's wrong with this error handling pattern?
    
    
    try:  
        session.add(task)  
        await session.commit()  
    except IntegrityError:  
        raise HTTPException(400, "Error")  
    

**A)** Missing `await` before `session.add()` **B)** Should catch `SQLAlchemyError` instead **C)** Missing `await session.rollback()` before raising **D)** HTTPException should be 500

Answer

**C) Missing`await session.rollback()` before raising**

After an error, you must rollback to return the session to a clean state. Without rollback, subsequent operations on the session may fail or behave unexpectedly.

* * *

## Question 11: Alembic Model Import​

Why must all models be imported in Alembic's env.py?

**A)** To make migrations run faster **B)** So autogenerate can detect tables by comparing metadata **C)** To enable downgrade operations **D)** For type checking

Answer

**B) So autogenerate can detect tables by comparing metadata**

Alembic compares `SQLModel.metadata` to the database schema. If models aren't imported, they're not registered in metadata, and Alembic won't see them.

* * *

## Question 12: Async Alembic​

What command initializes Alembic with async support?

**A)** `alembic init alembic` **B)** `alembic init -t async alembic` **C)** `alembic init --async alembic` **D)** `alembic init alembic --driver=asyncpg`

Answer

**B)`alembic init -t async alembic`**

The `-t async` flag uses the async template, which configures env.py for async database operations.

* * *

## Question 13: expire_on_commit​

What problem does `expire_on_commit=False` solve?

**A)** Prevents database connections from expiring **B)** Allows attribute access after commit without MissingGreenlet **C)** Makes commits faster **D)** Prevents automatic rollback

Answer

**B) Allows attribute access after commit without MissingGreenlet**

By default, SQLAlchemy expires attributes after commit, requiring a reload that triggers lazy loading. With `expire_on_commit=False`, attributes remain accessible.

* * *

## Question 14: Session Scope​

Why should each FastAPI request get its own database session?

**A)** Performance optimization **B)** Isolation - concurrent requests don't share transaction state **C)** Memory management **D)** Type safety

Answer

**B) Isolation - concurrent requests don't share transaction state**

Sharing sessions across requests means one request's uncommitted changes are visible to another, and errors in one request can corrupt another's session state.

* * *

## Question 15: Pool Pre-Ping​

Why is `pool_pre_ping=True` essential for cloud databases?

**A)** Improves query performance **B)** Enables connection pooling **C)** Detects and replaces stale connections before use **D)** Reduces connection count

Answer

**C) Detects and replaces stale connections before use**

Cloud databases often close idle connections. `pool_pre_ping` tests connections before use, replacing dead ones so your first query doesn't fail with "connection closed."

* * *

## Scoring​

Score| Assessment  
---|---  
16-18| Excellent - ready for production database work  
13-15| Good - review weak areas  
10-12| Fair - revisit core lessons  
Below 10| Review chapter and practice exercises  
  
## Next Steps​

If you scored below 16, revisit these lessons:

  * **Questions 1 wrong** : Review L03 (Engine Setup)
  * **Questions 2-4 wrong** : Review L02 (Database Design & Normalization)
  * **Questions 5-7 wrong** : Review L04 (Models) and L05 (Sessions)
  * **Questions 8-9 wrong** : Review L06 (CRUD Operations)
  * **Questions 10-13 wrong** : Review L08 (Relationships)
  * **Questions 14-16 wrong** : Review L09 (Transactions) and L10 (Migrations)
  * **Questions 17-18 wrong** : Review L03 (Engine Setup) and L05 (Sessions)