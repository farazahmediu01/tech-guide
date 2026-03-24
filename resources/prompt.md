I am trying to deeply understand **Context Objects and Generics in the OpenAI Agents SDK**, specifically:

* `Agent[TContext]`
* `RunContextWrapper[TContext]` inside tools

I am confused about how these pieces fit together.

1. **Why do we add a context class as a generic when creating an agent (e.g., `Agent[TaskManagerContext]` or `Agent[ShoppingContext]`)?**

   * What is the purpose of generics here?
   * How does this relate to Python generics?
   * What does it actually change in the behavior of the agent?

2. **How does context flow through the system?**

   * Does the Agent provide the context to the Runner?
   * Or does the Runner provide it to the tools?
   * Where does `RunContextWrapper` fit in this pipeline?

3. **How does this design help with memory and state management?**

   * Why can’t we just use normal variables?
   * What problem does this pattern solve in real-world agent systems?

Please explain with:

* A simple mental model
* A step-by-step execution flow example
* simple working code showing realwold examples:

  * Agent creation with generics
  * Runner usage
  * A tool accessing context via `RunContextWrapper`

I want to understand not just *how* it works, but *why this architecture exists*.
