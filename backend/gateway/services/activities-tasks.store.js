const { randomUUID } = require('crypto');

const LINKABLE_ENTITY_TYPES = new Set(['lead', 'contact', 'account', 'opportunity', 'case', 'message_thread']);
const TASK_STATUS = new Set(['open', 'in_progress', 'completed', 'canceled']);
const TASK_PRIORITY = new Set(['low', 'normal', 'high', 'urgent']);

const activityStore = [];
const taskStore = [];

function nowIso() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
}

function parseIso(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

function normalizeActivityCreate(payload, auth) {
  const errors = [];

  if (!LINKABLE_ENTITY_TYPES.has(payload.entity_type)) {
    errors.push({ field: 'entity_type', reason: 'unsupported_entity_type' });
  }

  if (typeof payload.entity_id !== 'string' || !payload.entity_id.trim()) {
    errors.push({ field: 'entity_id', reason: 'must_be_non_empty_string' });
  }

  if (typeof payload.event_type !== 'string' || !payload.event_type.trim()) {
    errors.push({ field: 'event_type', reason: 'must_be_non_empty_string' });
  }

  if (payload.event_time && !parseIso(payload.event_time)) {
    errors.push({ field: 'event_time', reason: 'must_be_valid_rfc3339_timestamp' });
  }

  if (payload.payload_json && (typeof payload.payload_json !== 'object' || payload.payload_json === null || Array.isArray(payload.payload_json))) {
    errors.push({ field: 'payload_json', reason: 'must_be_json_object' });
  }

  if (errors.length > 0) {
    return { errors };
  }

  return {
    data: {
      activity_id: `act_${randomUUID()}`,
      tenant_id: auth.tenant_id,
      actor_user_id: payload.actor_user_id || auth.sub,
      entity_type: payload.entity_type,
      entity_id: payload.entity_id,
      event_type: payload.event_type,
      event_time: payload.event_time || nowIso(),
      payload_json: payload.payload_json || {},
      source_service: payload.source_service || 'api_gateway',
      created_at: nowIso(),
    },
  };
}

function computeDefaultDueAt(priority, startsAtIso) {
  const startsAt = parseIso(startsAtIso) || new Date();
  const dueAt = new Date(startsAt);

  if (priority === 'urgent') dueAt.setHours(dueAt.getHours() + 2);
  else if (priority === 'high') dueAt.setHours(dueAt.getHours() + 4);
  else if (priority === 'normal') dueAt.setDate(dueAt.getDate() + 1);
  else dueAt.setDate(dueAt.getDate() + 3);

  return dueAt.toISOString().replace(/\.\d{3}Z$/, 'Z');
}

function pickAssignee(candidateUserIds = [], fallbackUserId) {
  if (candidateUserIds.length === 0) {
    return fallbackUserId;
  }

  const openTaskCountByUser = new Map(candidateUserIds.map((id) => [id, 0]));
  for (const task of taskStore) {
    if (task.status !== 'completed' && task.status !== 'canceled' && openTaskCountByUser.has(task.assigned_user_id)) {
      openTaskCountByUser.set(task.assigned_user_id, openTaskCountByUser.get(task.assigned_user_id) + 1);
    }
  }

  return candidateUserIds.reduce((selected, current) => {
    if (!selected) return current;
    return openTaskCountByUser.get(current) < openTaskCountByUser.get(selected) ? current : selected;
  }, null);
}

function normalizeTaskCreate(payload, auth) {
  const errors = [];

  if (!LINKABLE_ENTITY_TYPES.has(payload.entity_type)) {
    errors.push({ field: 'entity_type', reason: 'unsupported_entity_type' });
  }

  if (typeof payload.entity_id !== 'string' || !payload.entity_id.trim()) {
    errors.push({ field: 'entity_id', reason: 'must_be_non_empty_string' });
  }

  if (typeof payload.title !== 'string' || !payload.title.trim()) {
    errors.push({ field: 'title', reason: 'must_be_non_empty_string' });
  }

  if (payload.priority && !TASK_PRIORITY.has(payload.priority)) {
    errors.push({ field: 'priority', reason: 'invalid_priority' });
  }

  if (payload.status && !TASK_STATUS.has(payload.status)) {
    errors.push({ field: 'status', reason: 'invalid_status' });
  }

  if (payload.starts_at && !parseIso(payload.starts_at)) {
    errors.push({ field: 'starts_at', reason: 'must_be_valid_rfc3339_timestamp' });
  }

  if (payload.due_at && !parseIso(payload.due_at)) {
    errors.push({ field: 'due_at', reason: 'must_be_valid_rfc3339_timestamp' });
  }

  if (payload.candidate_user_ids && !Array.isArray(payload.candidate_user_ids)) {
    errors.push({ field: 'candidate_user_ids', reason: 'must_be_array' });
  }

  if (errors.length > 0) {
    return { errors };
  }

  const startsAt = payload.starts_at || nowIso();
  const priority = payload.priority || 'normal';

  const selectedAssignee = payload.assigned_user_id
    || pickAssignee(payload.candidate_user_ids || [], payload.entity_owner_user_id || auth.sub);

  const dueAt = payload.due_at || computeDefaultDueAt(priority, startsAt);

  if (new Date(dueAt) < new Date(startsAt)) {
    return { errors: [{ field: 'due_at', reason: 'must_be_greater_than_or_equal_to_starts_at' }] };
  }

  return {
    data: {
      task_id: `tsk_${randomUUID()}`,
      tenant_id: auth.tenant_id,
      entity_type: payload.entity_type,
      entity_id: payload.entity_id,
      title: payload.title,
      description: payload.description || '',
      status: payload.status || 'open',
      priority,
      assigned_user_id: selectedAssignee,
      created_by_user_id: auth.sub,
      starts_at: startsAt,
      due_at: dueAt,
      completed_at: null,
      assignment_method: payload.assigned_user_id
        ? 'explicit'
        : (Array.isArray(payload.candidate_user_ids) && payload.candidate_user_ids.length > 0 ? 'least_loaded_candidate' : 'entity_owner_fallback'),
      created_at: nowIso(),
      updated_at: nowIso(),
    },
  };
}

function createActivity(payload, auth) {
  const result = normalizeActivityCreate(payload, auth);
  if (result.errors) return result;
  activityStore.push(result.data);
  return { data: result.data };
}

function listActivities(tenantId, { entity_type: entityType, entity_id: entityId } = {}) {
  return activityStore.filter(
    (activity) => activity.tenant_id === tenantId
      && (!entityType || activity.entity_type === entityType)
      && (!entityId || activity.entity_id === entityId),
  );
}

function createTask(payload, auth) {
  const result = normalizeTaskCreate(payload, auth);
  if (result.errors) return result;
  taskStore.push(result.data);
  return { data: result.data };
}

function listTasks(tenantId, { entity_type: entityType, entity_id: entityId, status } = {}) {
  return taskStore.filter(
    (task) => task.tenant_id === tenantId
      && (!entityType || task.entity_type === entityType)
      && (!entityId || task.entity_id === entityId)
      && (!status || task.status === status),
  );
}

function rescheduleTask(taskId, tenantId, { starts_at: startsAt, due_at: dueAt }) {
  const task = taskStore.find((row) => row.task_id === taskId && row.tenant_id === tenantId);
  if (!task) return { notFound: true };

  const parsedStartsAt = startsAt ? parseIso(startsAt) : parseIso(task.starts_at);
  const parsedDueAt = dueAt ? parseIso(dueAt) : parseIso(task.due_at);

  if (!parsedStartsAt || !parsedDueAt) {
    return { errors: [{ field: 'starts_at/due_at', reason: 'must_be_valid_rfc3339_timestamp' }] };
  }

  if (parsedDueAt < parsedStartsAt) {
    return { errors: [{ field: 'due_at', reason: 'must_be_greater_than_or_equal_to_starts_at' }] };
  }

  task.starts_at = parsedStartsAt.toISOString().replace(/\.\d{3}Z$/, 'Z');
  task.due_at = parsedDueAt.toISOString().replace(/\.\d{3}Z$/, 'Z');
  task.updated_at = nowIso();

  return { data: task };
}

module.exports = {
  createActivity,
  listActivities,
  createTask,
  listTasks,
  rescheduleTask,
};
