# Build Your RAG Skill

> **Archived from:** <https://agentfactory.panaversity.org/docs/Building-Agent-Factories/vector-databases-rag-langchain/build-your-rag-skill>  
> **Wayback snapshot:** 2026-05-16  
> **Status:** retired from the live site — recovered for offline study.

---

Before learning RAG (Retrieval-Augmented Generation)—the architecture that gives AI agents access to your private data—you will **own** a RAG skill.

* * *

## Step 1: Get the Skills Lab​

  1. Go to [github.com/panaversity/claude-code-skills-lab](<https://github.com/panaversity/claude-code-skills-lab>)
  2. Click the green **Code** button
  3. Select **Download ZIP**
  4. Extract the ZIP file
  5. Open the extracted folder in your terminal


    
    
    cd claude-code-skills-lab  
    claude  
    

* * *

## Step 2: Create Your Skill​

Copy and paste this prompt:
    
    
    Using your skill creator skill create a new skill for RAG (Retrieval-Augmented  
    Generation) systems. I will use it to build production RAG pipelines with  
    LangChain and Qdrant vector database - from simple semantic search to advanced  
    patterns like HyDE, CRAG, and Agentic RAG. Use context7 skill to study official  
    LangChain and Qdrant documentation and then build it so no self assumed knowledge.  
    

Claude will:

  1. Fetch official LangChain and Qdrant documentation via Context7
  2. Ask you clarifying questions (chunking strategies, embedding models, retrieval patterns)
  3. Create the complete skill with ingestion pipelines, retrieval patterns, and evaluation templates


Your skill appears at `.claude/skills/rag-deployment/`.

* * *

## Done​

You now own a RAG skill built from official documentation. The rest of this chapter teaches you what it knows—and how to make it better.

**Next: Lesson 1 — Understanding RAG Architecture**