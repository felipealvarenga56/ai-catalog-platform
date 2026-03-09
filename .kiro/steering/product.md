The product of this repository is a experimental/mock/proof of concept to show relevance and gather investment for further development. It must run locally with the below functions running on sample data the will be generated.

Product Specification: Aura Governance Platform
1. Product Vision
Aura is an Intelligent AI & Data Governance platform that bridges the gap between corporate strategy and technical execution. By moving beyond a static registry, Aura acts as an active "concierge" that centralizes project intelligence, evaluates technical feasibility through an AI Wizard, and automates the path to project delivery.

2. Core Funnel Architecture
Phase I: The Catalog (Catálogo)
The Universal Source of Truth. Aura aggregates data from disparate sources (n8n, Lovable, IT, Deep, BI) into a unified repository.

Unified Project Registry: Detailed technical descriptions, ownership, and current status of all internal initiatives.

Cross-Level Accessibility: Information architecture designed to serve both technical squads and C-level stakeholders.

Executive Reporting: One-click generation of impact reports and resource allocation summaries for leadership.

Phase II: The Wizard (Wizard)
The Agentic Advisor. An LLM-powered conversational interface that processes project proposals and inquiries.

Feasibility Analysis: Compares user proposals against the existing Catalog to prevent redundant builds.

Strategic Routing: The Wizard directs the user to the most efficient development path:

Self-Service: Copilot, Lovable, n8n, Alteryx.

Specialized Teams: Deep (AI/Data Science), BI Team.

Strategic Build: Full Squad Development.

Gap Detection: Explicitly flags when no current solution exists ("No solution available today"), triggering a new innovation request.

Phase III: The Delivery (Entrega)
The Last-Mile Enabler. Aura ensures that a recommended solution results in actual access and progress.

Operational Procedures: Automated instructions for the "next step" (e.g., "To access n8n, open a ticket at [link]").

Documentation Support: Provision of guided templates and PDF manuals to assist users in filling out technical or bureaucratic requests.

4. Technical Integration Requirements
Inbound Connectors: API-level integration with n8n and Alteryx workflows to auto-update the Catalog.

Conversational Engine: LLM-based agent capable of understanding Portuguese context while maintaining English-standard documentation.

Identity & Access: Integration with corporate SSO to pre-fill "Delivery" forms based on user hierarchy.
