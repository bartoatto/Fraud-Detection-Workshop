# Agenda - Partner Domino Training (Life Sciences SCE)

Presenter notes; delete this folder from the project before publishing the template if you prefer attendees not to see it.

**Format:** Day 1 is this trimmed session (2 hours, branch `partner-sce`). Day 2 is the standard workshop from `main`, unchanged. A life-sciences specialist presents the SCE overview in a separate session beforehand and joins both days to answer life-sciences questions.

**Audience:** partner engineers (about 20) who will implement Domino for life-sciences clients. Their clients' users are mostly SAS-first stats programmers, so keep Git, flows and AI talk simple.

## Day 1 - Platform primitives (2h)

| Time | Topic | Format |
|------|-------|--------|
| 0:00 | Welcome, what Domino is, how it fits SCE work | Slides |
| 0:10 | Projects (a project is a study), project templates, compute environments, hardware tiers | Slides + demo |
| 0:25 | **Exercise A** - launch a workspace, explore and clean the data | Hands-on |
| 0:50 | Data: NetApp Volumes, snapshots, RBAC, audit trail. Git and version control, kept simple | Slides |
| 1:05 | **Exercise B** - data engineering as a Job. Talk track: jobs to flows | Hands-on |
| 1:25 | **Exercise C** - publish the Transaction Review Desk. Talk track: app approval gates | Hands-on |
| 1:50 | Governance policies shown by the presenters; wrap-up and Day 2 preview | Demo |

There is no model training in this session. If it runs long, present Exercise C as a demo, and leave extensions and the coding agent for Day 2 or the specialist.

## Talk tracks

- **Data:** say NetApp Volumes wherever the generic deck says Datasets, and do not introduce Datasets.
- **Project type:** the workshop uses a DFS project. State that Git-backed projects are recommended for real work.
- **Git:** keep it to best practices. Detailed Git teaching is separate enablement.
- **Flows:** describe a flow as linking jobs together and show what one looks like. Do not run one.
- **Personas:** stats programmer (not a "developer"), study lead (runs many studies, wants an operational view), data lead (RBAC, permissions, NetApp Volumes, snapshots, audit trail).
- **Governance:** policy = SOP, bundle = deliverable. Approvals are linear and the sign-off trail is what matters. Gates on policies are available on cloud. Show a sample policy and approve it from the presenter screen; share it afterwards.
- **After each feature:** one slide on how our SCE customers use it.

## Glossary

| Domino term | Say instead |
|-------------|-------------|
| Project | Study (a unit of work such as a drug or therapeutic area) |
| Policy | SOP (standard operating procedure) |
| Bundle | Deliverable |
| Dataset | NetApp Volume (for this audience) |

## Not covered on Day 1

Model training, experiments and MLflow, model endpoints, launchers and agents are not in this session. Day 2 covers whatever the standard workshop covers; check it against the SCE guidance above (for example, drop or soften Datasets, experiments and flows).

## Open items

- Confirm attendees know Python. If not, prepare SAS or R versions of the exercises; legacy SAS code is available internally.
- Get the attendee list and add users.
- The notes for the second half of the planning call were not available when this was written, so check them against this plan.
