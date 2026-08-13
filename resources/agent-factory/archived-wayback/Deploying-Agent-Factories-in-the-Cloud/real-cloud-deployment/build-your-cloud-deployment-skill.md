# Build Your Cloud Deployment Skill

> **Archived from:** <https://agentfactory.panaversity.org/docs/Deploying-Agent-Factories-in-the-Cloud/real-cloud-deployment/build-your-cloud-deployment-skill>  
> **Wayback snapshot:** 2026-04-22  
> **Status:** retired from the live site — recovered for offline study.

---

Before learning real cloud deployment—provisioning Kubernetes clusters on DigitalOcean, Hetzner, and other providers—you'll **own** a multi-cloud deployment skill.

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
    
    
    Using your skill creator skill create a new skill for multi-cloud Kubernetes deployment.  
    I will use it to provision and manage K8s clusters on budget-friendly providers like  
    DigitalOcean (DOKS) and Hetzner (k3s via hetzner-k3s CLI). The skill should cover:  
      
    - DigitalOcean DOKS cluster provisioning with doctl  
    - Hetzner K3s cluster provisioning with hetzner-k3s CLI  
    - Multi-cloud portability (provision → connect → deploy pattern)  
    - Cost comparison and optimization strategies  
      
    Use context7 skill to study official documentation for doctl, hetzner-k3s, and kubectl.  
    Build it from official docs so no self-assumed knowledge.  
    

Claude will:

  1. Fetch official DigitalOcean and Hetzner documentation via Context7
  2. Ask you clarifying questions (cluster size, node pools, cost thresholds)
  3. Create the complete skill with CLI references and deployment templates


Your skill appears at `.claude/skills/multi-cloud-deployer/`.

* * *

## Reflect on Your Skill​

Your `multi-cloud-deployer` skill is now ready. Throughout this chapter, you'll:

  1. **Test it** against real cloud scenarios (provisioning, connecting, deploying)
  2. **Identify gaps** as you learn manual steps
  3. **Improve it** by adding provider-specific patterns


After each lesson, return here to verify: _Does my skill handle what I just learned?_

* * *

**Next: Lesson 1 — Why Real Cloud Deployment Matters**