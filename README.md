# ⚒️ The Forge: Software Orchestration Platform

**Architected and Developed by:** Ahmed Maamoun

---

## 📖 Overview

The Forge is a next-generation software orchestration and professional workflow platform. Designed for high-scale automation and precision execution, it transforms complex project requirements into structured, executable results. By connecting advanced frontend interfaces with robust backend automation, The Forge acts as a central nervous system for software delivery pipelines.

---

## 📸 Platform Previews

<div align="center">
  <img src="screenshots/home.png" alt="Homepage / Entry" width="800" />
</div>
<br/>
<div align="center">
  <img src="screenshots/dashboard.png" alt="Orchestration Dashboard" width="400" />
  <img src="screenshots/activity.png" alt="Activity Logs" width="400" />
</div>

---

## ✨ Core Engineering Features

- **Workflow Automation Engine:** Visually design and execute complex multi-stage tasks.
- **Real-Time Telemetry:** Live activity logs and pipeline statuses streamed via WebSockets.
- **Resource Management:** Granular tracking of compute usage, task execution times, and failure rates.
- **Secure Integration Layer:** Built-in secret management for connecting third-party APIs and CI/CD pipelines safely.

---

## 🧠 Technical Challenges I Overcame

Orchestrating disparate microservices into a cohesive workflow engine is inherently complex:

1. **Idempotent Task Execution:**
   - *Challenge:* When executing automated workflows, a network failure halfway through could result in duplicate data if the workflow is blindly retried.
   - *Solution:* I designed the backend execution engine around idempotency keys. Every node in a workflow generates a unique deterministic hash based on its inputs and position. The database strictly enforces uniqueness on these keys, ensuring that even if a workflow restarts mid-execution, completed tasks are instantly bypassed, preventing any side effects.
2. **Real-time Log Aggregation:**
   - *Challenge:* Streaming thousands of log lines per second from background worker nodes to the React frontend without freezing the browser thread.
   - *Solution:* I utilized Redis Pub/Sub to decouple the workers from the WebSocket server. On the client side, I implemented a custom React hook leveraging `requestAnimationFrame` to batch DOM updates every 100ms, effectively throttling the render cycle while maintaining a smooth, real-time feel for the user.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend Platform** | Next.js, React, Tailwind CSS |
| **Backend & Orchestration** | Node.js, Python (Worker Nodes) |
| **Data Layer** | PostgreSQL, Redis (Pub/Sub & Queues) |

---

## 🚀 Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Maamoun0/the-forge.git
   cd the-forge
   ```

2. **Launch with Docker:**
   ```bash
   docker-compose up --build -d
   ```

*(Requires `.env` configuration for database credentials)*

---

## 👨‍💻 Author

**Ahmed Maamoun**
- GitHub: [@Maamoun0](https://github.com/Maamoun0)
- LinkedIn: [Ahmed Maamoun](https://linkedin.com/in/your-linkedin-profile)

Engineered with surgical precision by Ahmed Maamoun.
