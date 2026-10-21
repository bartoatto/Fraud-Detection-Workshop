# Agenda - Partner Domino Training (Life Sciences SCE)

Presenter notes; delete this folder from the project before publishing the template if you prefer attendees not to see it.

**Format:** Day 1 is this life-sciences session (2 hours, branch `life-sciences`). Day 2 is the standard workshop from `main`, unchanged. A life-sciences specialist presents the SCE overview in a separate session beforehand and joins both days.

**Audience:** partner engineers (about 20) who will implement Domino for life-sciences clients. Their clients' users are mostly SAS-first stats programmers (a few use R or Python), so keep Git, flows and AI talk simple.

**Study:** the public CDISC pilot study (CDISCPILOT01), a 254-subject Alzheimer's trial. We use its ADSL dataset only. The same study also drives the reference study repository, so what attendees see here maps onto how a real SCE project is organised.

## Day 1 - Platform primitives on a study (2h)

| Time | Topic | Format |
|------|-------|--------|
| 0:00 | Welcome, what Domino is, how it fits SCE work | Slides |
| 0:10 | Projects (a project is a study), project templates, compute environments, hardware tiers | Slides + demo |
| 0:25 | **Exercise A** - launch a workspace, explore ADSL | Hands-on |
| 0:50 | Data: NetApp Volumes, roles, snapshots and tags, audit trail. Git and version control, kept simple | Slides |
| 1:05 | **Exercise B** - production, QC and compare as Jobs. Talk track: jobs to flows | Hands-on |
| 1:25 | **Exercise C** - publish the Study Review Desk. Talk track: gates | Hands-on |
| 1:50 | Governance policies shown by the presenters; wrap-up and Day 2 preview | Demo |

If it runs long, present Exercise C as a demo, and leave extensions and the coding agent for Day 2 or the specialist.

## How the exercises map to an SCE study

| Workshop | In a real study repository |
|----------|----------------------------|
| `adam/adsl.sas7bdat` on the volume | ADaM datasets built from SDTM, read from a tagged snapshot |
| Exercise B production job | `prod/tfl/*.sas` programs run as batch jobs |
| Exercise B QC job | `qc/tfl/qc_*.sas`, written independently (double programming) |
| Exercise B compare job | PROC COMPARE summary that writes `dominostats.json` |
| Run with `ADSL_SNAPSHOT_TAG` | Reading the SDTM snapshot tag so a run is reproducible |
| Study Review Desk sign-off | Review and approval of deliverables (SOP) |

The reference repository separates DEV (interactive SAS Studio) from PROD (batch jobs) with separate volumes and chains ADaM, QC and compare in Flows. We describe that and do not run it.

## Talk tracks

- **Data:** say NetApp Volumes wherever the generic deck says Datasets, and do not introduce Datasets.
- **Language:** the exercises are Python. Stats programmers will ask about SAS: the same jobs run SAS programs in a SAS Analytics Pro environment (the reference repo is SAS), and `pandas.read_sas` reads their existing `.sas7bdat` files directly. Domino supports SAS Analytics Pro only.
- **Project type:** the workshop uses a DFS project. State that Git-backed projects are recommended for real work.
- **Git:** keep it to best practices. Detailed Git teaching is separate enablement.
- **Flows:** describe a flow as linking jobs together (production, QC, compare, validation) and show what one looks like. Do not run one.
- **Personas:** stats programmer (not a "developer"), study lead (runs many studies, wants an operational view, uses the app), data lead (RBAC, permissions, NetApp Volumes, snapshots, audit trail).
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

Model training, experiments and MLflow, model endpoints, launchers and agents. Day 2 covers whatever the standard workshop covers; check it against the SCE guidance above (for example, drop or soften Datasets, experiments and flows).

## Open items

- Confirm attendees know Python. If not, build the SAS version of Exercise B on the reference programs and use a SAS Analytics Pro environment.
- Get the attendee list and add users.
- The reference repo includes a Pinnacle 21 style validation step and a Clinical Data Explorer extension; decide whether either belongs in the demo.
- The notes for the second half of the planning call were not available when this was written, so check them against this plan.
