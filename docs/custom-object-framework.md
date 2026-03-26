# Custom Object Framework Specification

## Purpose
This document defines a framework for introducing custom objects into the CRM while preserving compatibility with the existing domain model and preventing schema conflicts.

## Design Principles
- **Domain model alignment:** Every custom object and field must map cleanly to existing domain boundaries (tenant, module, ownership, and lifecycle).
- **Conflict prevention:** Names, API keys, and persistence artifacts must be globally unique within a tenant scope.
- **Runtime extensibility:** New objects and fields should be created without code redeploys.
- **Safety and consistency:** Validation and relationship constraints must be enforceable at write time.

## 1) Custom Object Creation

### 1.1 Object Definition
A custom object is a user-defined entity with metadata and runtime-managed fields.

Required definition attributes:
- `object_key` (string, immutable): machine-readable identifier (example: `project_milestone`).
- `display_name` (string): human-readable label.
- `description` (string, optional).
- `module_scope` (enum): domain area where the object belongs (example: Sales, Support).
- `ownership_model` (enum): user-owned, team-owned, org-owned.
- `lifecycle_state` (enum): draft, active, deprecated, archived.

### 1.2 Creation Workflow
1. Receive object definition request.
2. Run conflict checks:
   - reserved keyword check,
   - existing object key check,
   - API route/name collision check.
3. Persist object metadata.
4. Create baseline system fields (`id`, `created_at`, `updated_at`, `created_by`, `updated_by`, `tenant_id`).
5. Publish object descriptor to metadata cache/registry.

### 1.3 Domain Integration Requirements
- Each object must reference a valid `module_scope` recognized by the domain model.
- Ownership and visibility must reuse existing authorization primitives.
- Lifecycle transitions must be auditable using the platform audit/event model.

## 2) Dynamic Fields

### 2.1 Field Types
Supported dynamic field categories:
- scalar: `text`, `long_text`, `number`, `decimal`, `boolean`, `date`, `datetime`
- structured: `json`
- constrained: `enum`, `multi_enum`
- references: `lookup` (foreign object record reference)

### 2.2 Field Metadata
Each dynamic field definition includes:
- `field_key` (immutable, unique within object)
- `label`
- `type`
- `required` (boolean)
- `default_value` (optional)
- `index_hint` (none, standard, unique)
- `is_searchable` (boolean)
- `is_filterable` (boolean)
- `is_sortable` (boolean)

### 2.3 Field Lifecycle
- Add field: available immediately for new writes; backfill strategy optional.
- Update field: non-breaking updates only (label/help/index hints allowed).
- Type migrations: require background migration plan and compatibility mode.
- Delete field: soft-delete metadata first, then purge data after retention window.

## 3) Validation Rules

### 3.1 Validation Layers
1. **Schema-level validation**
   - type conformance
   - required field enforcement
   - max length / precision checks
2. **Rule-level validation**
   - regex/pattern constraints
   - numeric/date ranges
   - conditional requirements (if X then Y required)
3. **Cross-entity validation**
   - referential integrity for lookups
   - relationship cardinality constraints

### 3.2 Rule Definition Model
Validation rules are metadata-driven and versioned.

Rule attributes:
- `rule_id`
- `object_key`
- `target_field_keys`
- `expression` (declarative DSL)
- `error_code`
- `error_message`
- `severity` (error/warning)
- `status` (active/inactive)

### 3.3 Execution Semantics
- Execute on create and update.
- Hard-fail transaction on `error` severity.
- Return structured violation payload for API/UI consumers.
- Emit validation metrics and audit entries.

## 4) Relationships

### 4.1 Relationship Types
- **One-to-many:** parent object to multiple child records.
- **Many-to-one:** child references single parent.
- **Many-to-many:** link table/object with dual lookups.
- **Polymorphic lookup (optional):** single reference field targeting multiple object types.

### 4.2 Relationship Definition
Relationship metadata includes:
- `relationship_key`
- `source_object_key`
- `target_object_key`
- `cardinality`
- `on_delete` policy (restrict, cascade, nullify)
- `bidirectional` (boolean)

### 4.3 Integrity Guarantees
- Lookup writes must verify target record existence and tenant match.
- Delete actions must honor `on_delete` policy.
- Circular dependency detection required at relationship creation.
- Relationship changes must be versioned and audited.

## 5) Storage Model

### 5.1 Logical Storage Strategy
Use a hybrid model:
- **Metadata tables:** store object/field/rule/relationship definitions.
- **Record storage:** store custom object rows in a generic record table with typed value columns and/or JSON payload.
- **Index storage:** maintain secondary indexes for searchable/filterable fields.

### 5.2 Recommended Physical Model
Core tables (illustrative):
- `custom_objects` (object metadata)
- `custom_object_fields` (field metadata)
- `custom_object_rules` (validation metadata)
- `custom_object_relationships` (relationship metadata)
- `custom_object_records` (record envelope: `id`, `object_key`, `tenant_id`, system fields)
- `custom_object_values` (EAV/typed values or JSON segments)

### 5.3 Partitioning and Performance
- Partition by `tenant_id` and/or `object_key` for scale.
- Keep high-selectivity fields indexed based on `index_hint`.
- Support metadata caching with invalidation on publish.
- Enforce query guardrails (max joins, max filter complexity).

## 6) Domain Model Integration and Conflict Avoidance

### 6.1 Domain Model Integration
- Register each custom object in the same domain catalog used by first-class entities.
- Reuse domain services for:
  - authorization,
  - audit logging,
  - event emission,
  - search indexing.
- Ensure custom objects participate in existing API conventions (pagination, filtering, sorting, versioning).

### 6.2 No Schema Conflicts
Conflict checks must run during object/field creation and update:
- object key uniqueness within tenant
- field key uniqueness within object
- reserved keyword blacklist
- collision checks against system fields and core entity keys
- index name uniqueness
- API route and event name uniqueness

If any conflict is detected:
- reject the change atomically,
- return deterministic error code,
- include conflicting artifact reference in error payload.

## 7) Governance and Change Control
- All metadata mutations must be versioned.
- Support dry-run validation for planned changes.
- Provide migration playbooks for breaking changes.
- Maintain full audit history for compliance.

## 8) Minimal API Contract (Illustrative)
- `POST /api/v1/custom-objects` — create object.
- `POST /api/v1/custom-objects/{objectKey}/fields` — create field.
- `POST /api/v1/custom-objects/{objectKey}/rules` — create validation rule.
- `POST /api/v1/custom-objects/{objectKey}/relationships` — define relationship.
- `POST /api/v1/custom-objects/{objectKey}/records` — create record.
- `PATCH /api/v1/custom-objects/{objectKey}/records/{id}` — update record.

## 9) Acceptance Criteria
- Custom objects can be created and managed without redeployments.
- Dynamic fields are enforceable with typed validation.
- Validation rules run consistently on writes.
- Relationships maintain referential integrity.
- Storage model supports scalability and tenant isolation.
- Domain model integration is explicit and complete.
- Schema conflict prevention is deterministic and testable.
