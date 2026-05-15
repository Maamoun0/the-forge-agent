# ⚒️ The Forge
### High-Scale Software Orchestration & Automation

**Ahmed Maamoun** • *Systems Architect*

---

## 🏗️ The Infrastructure
**The Forge** is more than just a task runner. It's a central nervous system for complex software delivery. I engineered this platform to bridge the gap between raw scripts and executable, monitored workflows.

---

## 📸 System Overview
<div align="center">
  <img src="screenshots/home.png" alt="Entry Portal" width="100%" />
</div>

<br/>

| Orchestration Dashboard | Activity Telemetry |
| :--- | :--- |
| <img src="screenshots/dashboard.png" width="400" /> | <img src="screenshots/activity.png" width="400" /> |

---

## 🛠 Key Systems
*   **Orchestration Engine:** Design multi-stage pipelines with visual feedback.
*   **Real-Time Telemetry:** Stream logs and performance metrics via high-speed WebSockets.
*   **Resource Tracking:** Granular monitoring of CPU, Memory, and execution costs.
*   **Secret Management:** Built-in vault for secure API and CI/CD integrations.

---

## 🧠 Engineering Journal: Ensuring Data Integrity
When you're running automated tasks across multiple servers, the biggest risk is **Network Partitioning** (the task runs twice because the server "lost" the first confirmation).

**My solution:** I developed a custom **Idempotency Layer** using Redis and PostgreSQL. Every task execution is wrapped in a transactional block with a unique "Execution ID". If a worker retries a task, the layer checks the global state and instantly resumes or skips the task based on its last known atomic status. This ensures that no matter how many times a system fails, the final state is always correct.

---

## 🧬 Technology Blueprint
*   **Core:** Next.js (Frontend) & Node.js (Controller)
*   **Workers:** Python for heavy-lift automation tasks
*   **State:** PostgreSQL (Persistence) & Redis (Real-time Pub/Sub)

---

### 👨‍💻 Connect & Build
**Ahmed Maamoun**
[GitHub](https://github.com/Maamoun0) | [LinkedIn](https://linkedin.com/in/your-linkedin-profile)

*Orchestrating the future, one node at a time.*
