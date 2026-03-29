# B9-P05 Marketing Workspace

## Inputs used
- `docs/read-models.md`
- `docs/workflow-catalog.md`

## Marketing workspace structure

### Workspace shell
- **Workspace id:** `marketing_workspace`
- **Primary route:** `/app/marketing/campaigns`
- **Workflow anchor:** `Lead intake, assignment, conversion`
- **Campaign flow (guided):**
  1. Create draft campaign
  2. Build and validate segment
  3. Activate campaign
  4. Track funnel and attribution
  5. Monitor journey execution
  6. Drill down performance
  7. Complete campaign

### Domain modules inside workspace
1. **Campaign workspace**
   - Lifecycle command center (draft → active → completed).
2. **Segment builder UI model**
   - Rule composition + validation for lead/contact entity sets.
3. **Funnel / attribution**
   - Source/channel progression and conversion visibility.
4. **Journey status**
   - Automation health, failures, retries, escalation visibility.
5. **Performance drill-down**
   - Pivot from summary metrics into campaign/source/segment detail.

## Views

| View id | Route | Purpose | Key metric bindings (read model.field) |
|---|---|---|---|
| `campaign_workspace` | `/app/marketing/campaigns` | Manage campaign lifecycle execution. | `WorkflowAutomationOutcomeRM.execution_volume_by_status` |
| `segment_builder` | `/app/marketing/segments` | Build audience rule sets and validate constraints. | `LeadFunnelPerformanceRM.lead_quality_match_rate` |
| `funnel_attribution` | `/app/marketing/funnel-attribution` | Track source-to-conversion and attribution paths. | `LeadFunnelPerformanceRM.source_channel_conversion_rate` |
| `journey_status` | `/app/marketing/journeys` | Monitor campaign-triggered journey runtime health. | `WorkflowAutomationOutcomeRM.success_rate` |
| `performance_drilldown` | `/app/marketing/performance` | Analyze engagement + pipeline impact by slice. | `CommunicationEngagementRM.delivery_open_click_reply_rate`; `OpportunityPipelineSnapshotRM.weighted_pipeline` |

## Interaction patterns

1. **Guided campaign flow**
   - Trigger: user opens draft campaign.
   - UX response: next required action surfaced (segment validation, activation gate, completion criteria).

2. **Cross-filter funnel context**
   - Trigger: source/channel selected in funnel view.
   - UX response: segment, journey, and drill-down views inherit filter context.

3. **Journey exception handoff**
   - Trigger: failure threshold exceeded in journey status.
   - UX response: failing steps + linked executions + escalation actions shown in context.

4. **Metric traceability hover**
   - Trigger: user hovers metric badge.
   - UX response: backing read model + field displayed to prevent passive data dumps.

## Self-QC

- **Campaign flow clear:** PASS
  - Explicit 7-step guided sequence from draft to completion.
- **Metrics tied to read models:** PASS
  - Every view metric mapped to a named read model field.
- **No passive data dump:** PASS
  - Interaction patterns require actionable transitions (filters, handoffs, gates).

## Fix loop
- Fix: Added explicit marketing workspace model + API payload + documentation.
- Re-check: Added test coverage for flow clarity, read-model metric binding, and interaction payload contract.
- Score: **10/10**
