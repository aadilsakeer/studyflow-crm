# Globvio CRM Agent Roadmap

## Project

Name: Globvio CRM

Type: Study Abroad CRM SaaS

Stack:

* Backend: Django + DRF
* Frontend: React + Vite + Material UI
* Database: PostgreSQL
* Authentication: JWT + SimpleJWT
* Cache: Redis
* Async Jobs: Celery

---

# Current Status

## Completed

### Platform Foundation

* Authentication
* JWT Security
* JWT Rotation
* JWT Blacklist
* RBAC Framework
* Secondary RBAC
* Tenant Isolation
* Catalog Security
* Environment Configuration

### Security

* Cross-Tenant Leak Fixes
* Serializer Hardening
* Licensing Fail-Closed
* Security Headers

### Infrastructure

* PostgreSQL
* Redis
* Celery Foundation
* Dashboard Analytics

### Data Management

* Soft Delete Framework
* Trash APIs
* Restore APIs
* Recycle Bin

### Admissions Platform

* Student Documents
* Offer Letters
* Visa Processing
* Counsellor Pipeline
* Student Journey Board

### Operations

* Telecaller Assignment
* Excel Lead Import
* Activity Timeline
* Task & Follow-Up System
* Workflow Automation

### Reporting

* Advanced Reporting
* KPI Dashboards
* CSV Export
* Excel Export

### Communication

* Communication Hub
* WhatsApp Integration

### Student Experience

* Student Portal

### SaaS Platform

* SaaS Foundation
* Subscription Plans
* Billing
* Stripe Integration
* Razorpay Integration
* White Label
* Support Desk
* Health Checks

### Launch Status

* SaaS MVP Ready
* Launch Readiness: 96%

---

# Development Principles

Always reuse:

* RBAC
* Tenant Isolation
* Audit Logs
* Soft Delete
* Recycle Bin
* Dashboard Analytics
* Redis
* Celery
* Existing Services
* Existing APIs
* Existing Components
* Existing Status Enums

Never rebuild existing systems.

---

# Remaining Roadmap

## [x] Phase 8.5 Platform Operations

Status: COMPLETE — owner dashboard, tenant ops, subscription ops, support queue, impersonation, activity logs

---

## [x] Phase 8.6 Production Operations

Status: COMPLETE — live payment validation, SMTP, automated backups, monitoring, ops dashboard

---

## [ ] Phase 8.7 Security Operations

### Authentication Security

* Two-Factor Authentication (2FA)
* Password Policy Enforcement
* Session Management Review

### Monitoring

* Login Monitoring
* Suspicious Login Detection
* Security Audit Dashboard

### Administration

* Session Revocation
* User Security Events

---

## [ ] Phase 9 AI Lead Intelligence

### AI Lead Scoring

* Hot
* Warm
* Cold

### Lead Prioritization

* Conversion Probability
* Follow-Up Priority
* Best Leads First

### AI Counsellor Assistant

* Student Summary
* Case Summary
* Recommended Actions
* Email Drafts
* WhatsApp Drafts

---

## [ ] Phase 10 Workflow Builder 2.0

### Workflow Builder

* Trigger
* Condition
* Action

### Automation Examples

* Lead Created
* Document Approved
* Offer Received
* Visa Approved

### Tenant Configurable Workflows

* Custom Automation Rules

---

## [ ] Phase 11 Email Platform

### Templates

* Admission
* Offer
* Visa
* Follow-Up

### Campaigns

* Bulk Email
* Scheduled Email
* Email Tracking

---

## [ ] Phase 12 Knowledge Base

### Internal Knowledge

* SOPs
* Process Guides
* University Guides

### Customer Knowledge Base

* Help Center
* FAQs

---

## [ ] Phase 13 Document Intelligence

### AI Document Analysis

* Passport Validation
* IELTS Expiry Detection
* Missing Document Detection
* Financial Document Validation

---

## [ ] Phase 14 Mobile Apps

### Mobile Applications

* Counsellor App
* Telecaller App
* Student App

---

## [ ] Phase 15 Enterprise Features

### Enterprise Security

* SSO

### Enterprise Platform

* API Keys
* Webhooks
* Custom Domains
* Custom Email Domains

### Enterprise Analytics

* Advanced Analytics
* Enterprise Reporting

---

# Execution Rule

Start from first incomplete phase.

Complete ONE phase only.

Do not start the next phase automatically.

After completion:

* Commit
* Push branch
* Update roadmap
* Report results
* Stop

If blocked:

* Report blocker
* Stop

---

# Success Criteria

* Smallest possible change
* Maximum feature value
* Minimum token consumption
* No duplicate architecture
* Reuse existing systems
* One completed phase at a time
