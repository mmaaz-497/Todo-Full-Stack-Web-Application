---
id: 001
title: Phase IV Kubernetes Deployment Specification
stage: spec
date: 2025-12-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: phase-iv-kubernetes-deployment
branch: 001-auth-session-fix
user: Developer
command: /sp.specs
labels: ["kubernetes", "docker", "helm", "minikube", "containerization", "deployment", "infrastructure", "ai-devops"]
links:
  spec: specs/phase-iv-kubernetes-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/phase-iv-kubernetes-deployment/spec.md
tests:
  - N/A (specification phase, no tests)
---

## Prompt

/sp.specs  You are a Spec-Kit Plus expert and Cloud-Native DevOps architect.

Generate COMPLETE, CONSISTENT, and NON-OVERLAPPING specs for **Phase IV: Local Kubernetes Deployment** of a Cloud-Native Todo Chatbot.

STRICT RULES:
- Follow Spec-Kit Plus spec format only
- Do NOT add new product features
- Do NOT modify application logic from todo-ai-chatbot
- Do NOT assume cloud providers (AWS/GCP/Azure)
- Local-only deployment using Minikube
- Specs must be implementation-ready but NOT implementation tasks

PROJECT CONTEXT:
- Application: Cloud-Native Todo Chatbot
- Existing Phase: Phase III (frontend + backend already implemented)
- Goal: Deploy the existing app locally on Kubernetes with basic functionality
- Development approach: Spec-Driven Development
- Tooling: Spec-Kit Plus + Claude CLI

REQUIRED TECHNOLOGY STACK:
- Containerization: Docker
- Docker AI Agent: Gordon (Docker Desktop AI)
- Kubernetes: Minikube
- Package Manager: Helm Charts
- AI DevOps Tools: kubectl-ai, Kagent
- Local environment only (zero-cost learning)

REQUIRED SPECS TO GENERATE:
1. **System Overview Spec**
   - Purpose of Phase IV
   - Scope boundaries (what is included and excluded)

2. **Containerization Spec**
   - Docker image requirements for frontend
   - Docker image requirements for backend
   - Use of Docker AI Agent (Gordon) for assisted Docker operations
   - Fallback behavior if Gordon is unavailable

3. **Local Kubernetes Environment Spec**
   - Minikube setup assumptions
   - Local cluster constraints
   - Namespace and resource isolation rules

4. **Helm Chart Specification**
   - Helm chart structure for frontend
   - Helm chart structure for backend
   - Values, templates, and configurable parameters
   - Replica configuration and service exposure

5. **AI-Assisted Kubernetes Operations Spec**
   - Use cases for kubectl-ai
   - Use cases for Kagent
   - Allowed AI-assisted operations (deploy, scale, diagnose, optimize)
   - Safety and boundary rules for AI agents

6. **Deployment Spec**
   - Local deployment flow using Helm + Minikube
   - Frontend ↔ backend connectivity expectations
   - Environment configuration handling

7. **Observability & Troubleshooting Spec**
   - Pod health checks
   - Failure diagnosis using kubectl-ai
   - Cluster health analysis using Kagent

8. **Non-Goals & Constraints Spec**
   - Explicitly list what this phase will NOT do
   - No cloud hosting
   - No advanced security or production hardening

9. **Spec-Driven Infrastructure Notes**
   - How these specs support future Spec-Driven automation
   - Blueprint readiness for Claude Code Agent skills (conceptual only)

OUTPUT REQUIREMENTS:
- Each spec must be clearly titled
- Use precise, unambiguous language
- No implementation code
- No task breakdowns
- No assumptions beyond what is stated
- Ensure all specs are internally consistent

This output will be used as the single source of truth for `/sp.plan` and `/sp.tasks`.

## Response snapshot

Generated comprehensive Phase IV: Local Kubernetes Deployment specification containing 9 major sections:

**1. System Overview Spec (Sections 1)**
- Purpose: Deploy existing Todo Chatbot to local Kubernetes (Minikube) with zero-cost infrastructure
- IN SCOPE: Docker containerization, Helm charts, Minikube deployment, AI DevOps tools (Gordon, kubectl-ai, Kagent)
- OUT OF SCOPE: Cloud deployments, production hardening, new application features, service mesh, ingress controllers, monitoring stacks, CI/CD pipelines
- Success criteria: All pods running, Phase III functionality preserved, AI tools providing assistance

**2. Containerization Spec (Section 2)**
- Frontend: Multi-stage Dockerfile for Next.js (node:18-alpine base, target <200MB)
- Backend: Multi-stage Dockerfile for Node.js auth-service (node:18-alpine, target <150MB)
- Gordon AI agent integration for Dockerfile generation and optimization
- Fallback to manual Dockerfiles if Gordon unavailable
- Security: Non-root users, no hardcoded secrets, .dockerignore for layer caching

**3. Local Kubernetes Environment Spec (Section 3)**
- Minikube configuration: 2 CPUs, 4GB RAM, Docker driver
- Namespace: todo-app (all components isolated)
- Resource constraints: 512Mi RAM, 500m CPU per pod
- Service exposure: NodePort (30080 frontend, 30081 backend)

**4. Helm Chart Specification (Section 4)**
- Frontend chart: Deployment, Service, ConfigMap templates with parameterized values.yaml
- Backend chart: Adds Secret for DATABASE_URL, AUTH_SECRET, GEMINI_API_KEY
- Templating: Full _helpers.tpl for labels, names, selectors
- Health probes: Liveness and readiness for both components

**5. AI-Assisted Kubernetes Operations Spec (Section 5)**
- kubectl-ai: Natural language kubectl commands (logs, describe, scale, debug)
- Kagent: Cluster health analysis, resource optimization, troubleshooting
- Safety rules: Read-only by default, confirmation required for destructive ops, namespace scoping
- Prohibited: Cluster-wide deletes, RBAC changes, node operations

**6. Deployment Spec (Section 6)**
- 7-step deployment flow: Minikube start → Docker build → Secret creation → Helm install → Verification → Access → Validation
- Frontend-backend connectivity: NodePort from browser (not Service DNS due to client-side limitation)
- Environment config: ConfigMaps for non-sensitive, Secrets for credentials

**7. Observability & Troubleshooting Spec (Section 7)**
- Health probes: HTTP GET to /api/health (frontend), /health (backend)
- kubectl-ai diagnostics: Pod failures (Pending, ImagePullBackOff, CrashLoopBackOff)
- Kagent analysis: Cluster health, resource recommendations, performance diagnostics

**8. Non-Goals & Constraints Spec (Section 8)**
- Explicitly excluded: Cloud providers, Ingress, service mesh, monitoring (Prometheus/Grafana), GitOps, autoscaling, production security (mTLS, network policies), application code changes
- Zero cloud costs requirement
- Learning-focused, not production-ready

**9. Spec-Driven Infrastructure Notes (Section 9)**
- Future automation: Terraform IaC, spec-to-manifest generation, automated testing
- Conceptual skills: /sp.k8s-deploy, /sp.k8s-troubleshoot, /sp.k8s-optimize
- Current limitation: Manual execution only (automated skills are future work)

**Additional Sections:**
- 10. Acceptance Criteria: Functional (pods running, Phase III features work), technical (multi-stage builds, secrets management), AI tooling (Gordon/kubectl-ai/Kagent validated)
- 11. Risks & Mitigations: Docker build failures, Minikube resource exhaustion, ImagePullPolicy misconfiguration, Service DNS issues
- 12. Open Questions: Database deployment strategy (Neon vs in-cluster), frontend-backend communication approach, health endpoint availability, AI tool installation status
- Appendix A: Version matrix (Docker 24.x+, Minikube 1.30.0+, Helm 3.10.0+, kubectl 1.28.x+)
- Appendix B: Command reference (Minikube, Docker, Helm, kubectl, kubectl-ai, Kagent)
- Appendix C: Expected file structure (Dockerfiles, charts/, k8s/, updated README)

**Key Design Decisions:**
- Database: External Neon (no in-cluster PostgreSQL by default)
- Service exposure: NodePort (learning-focused, not production Ingress)
- AI tools: Assistive only, human-in-the-loop confirmation required
- Image registry: Minikube's Docker daemon (no push/pull overhead)
- Resource limits: Conservative (512Mi RAM per pod) due to 4GB total constraint

**Spec Completeness:**
✅ Non-overlapping (clear boundaries between containerization, orchestration, deployment)
✅ Implementation-ready (sufficient detail for /sp.plan and /sp.tasks)
✅ No application logic changes (preserves Phase III functionality)
✅ Local-only (zero cloud costs)
✅ Internally consistent (all sections reference same architecture)

## Outcome

- ✅ Impact: Complete Phase IV specification created (15,000+ words, 12 sections, 3 appendices). Ready for /sp.plan execution.
- 🧪 Tests: N/A (specification phase, testing occurs during implementation)
- 📁 Files: Created specs/phase-iv-kubernetes-deployment/spec.md (single comprehensive specification file)
- 🔁 Next prompts: /sp.plan (generate implementation plan), then /sp.tasks (generate task breakdown)
- 🧠 Reflection: Specification successfully balances learning objectives (AI DevOps tools, Kubernetes concepts) with practical constraints (local-only, resource-limited Minikube). Clear separation between infrastructure deployment (Phase IV scope) and application development (Phase III, out of scope). Open questions identified for clarification during planning phase.

## Evaluation notes (flywheel)

- Failure modes observed: None. Specification generated successfully without errors or ambiguities.
- Graders run and results (PASS/FAIL):
  - Completeness: PASS (all 9 required specs included)
  - Consistency: PASS (no contradictions between sections)
  - Implementation-readiness: PASS (sufficient detail for planning and tasking)
  - Scope adherence: PASS (no application logic changes, local-only deployment)
- Prompt variant (if applicable): N/A (initial specification generation)
- Next experiment (smallest change to try): During /sp.plan phase, validate open questions (database strategy, health endpoint availability, AI tool installation status) and incorporate answers into implementation plan.
