# Globvio CRM Agent Roadmap

## Project

Name: Globvio CRM

Type: Study Abroad CRM

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

### Workflow

* Activity Timeline (Phase 4.1)

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

## [ ] Phase 2.1 Student Documents Module

Features:

* Academic Documents
* Identity Documents
* Language Test Documents
* Financial Documents
* Professional Documents
* Upload
* Review
* Approve
* Reject
* Audit Logging
* Soft Delete
* Restore
* Recycle Bin Integration

---

## [ ] Phase 2.2 Offer Letter Module

Features:

* Conditional Offer
* Unconditional Offer
* Expiry Tracking
* Acceptance Tracking
* Deposit Tracking

---

## [ ] Phase 2.3 Visa Processing Module

Features:

* Visa Workflow
* Appointment Tracking
* Fee Tracking
* Status Tracking
* Decision Tracking

---

## [ ] Phase 2.4 Recycle Bin UI

Features:

* Deleted Records
* Restore
* Audit Trail
* Admin Access

Use existing soft delete backend.

---

## [ ] Phase 3.1 Telecaller Assignment System

Features:

* Assign Lead
* Bulk Assignment
* Round Robin
* Reassignment
* Workload Tracking

---

## [ ] Phase 3.2 Excel Lead Import

Features:

* CSV Import
* XLSX Import
* Column Mapping
* Duplicate Detection
* Assignment During Import
* Import Logs

---

## [ ] Phase 3.3 Counsellor Pipeline

Features:

* Lead Evaluation
* Student Conversion
* Country Recommendation
* Application Readiness

---

## [ ] Phase 3.4 Student Journey Board

Workflow:

Lead
↓
Student
↓
Documents
↓
Application
↓
Offer
↓
Visa
↓
Departure
↓
Arrived

---

## [x] Phase 4.1 Activity Timeline

Status: COMPLETE

Track:

* Lead Events
* Assignment Events
* Student Events
* Document Events
* Offer Events
* Visa Events

---

## [x] Phase 4.2 Task & Follow-Up System

Status: COMPLETE

Task Types:

* Follow-up Call
* Document Collection
* Application Submission
* Offer Review
* Visa Appointment
* General Task

Features:

* Assignment
* Priority
* Due Date
* Status
* Notes
* Dashboard Widgets
* Reminder Support

Roles:

* Telecaller
* Counsellor
* Visa Team
* Admin

---

## [x] Phase 4.3 Advanced Reporting

Status: COMPLETE

Reports:

* Lead Source ROI
* Telecaller Performance
* Counsellor Performance
* Country Performance
* University Performance
* Offer Conversion
* Visa Success Rate
* Revenue

Features:

* Date Filters
* CSV Export
* Excel Export
* Charts

---

## [ ] Phase 4.4 Workflow Automation

Using Celery.

Features:

* Follow-up Reminders
* Missing Document Reminders
* Offer Expiry Alerts
* Visa Appointment Reminders
* Application Deadline Reminders

---

## [ ] Phase 5 Student Portal

Features:

* Document Upload
* Application Tracking
* Offer Tracking
* Visa Tracking
* Activity Timeline

---

## [ ] Phase 6 Communication Hub

Features:

* Call Logs
* Notes
* Email Logs
* WhatsApp Logs
* Unified Communication History

---

## [ ] Phase 7 WhatsApp Integration

Features:

* Follow-up Messages
* Document Reminders
* Offer Reminders
* Visa Updates

---

## [ ] Phase 8 Commercial SaaS

Features:

* Subscription Plans
* Billing
* Usage Limits
* White Label
* Tenant Branding

---

## [ ] Phase 9 AI Layer

Features:

* AI Lead Scoring
* AI Counsellor Assistant
* AI Document Checker
* AI Workflow Suggestions

---

# Execution Rule

Start from the first incomplete phase.

Complete ONE phase only.

Do not start the next phase automatically.

After completion:

* Commit
* Push branch
* Update roadmap status
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
