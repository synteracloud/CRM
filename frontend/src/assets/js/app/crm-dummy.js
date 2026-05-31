/* Pakistan CRM — Dummy Data (single source of truth for all pages) */
/* All data mirrors the exact API response envelope: { data: [...], meta: { count, total, limit, offset } } */

window.CRM_DUMMY = (function () {
  'use strict';

  const USERS = [
    { id: 'u-001', display_name: 'Ahmed Raza',       email: 'ahmed.raza@crm.pk',    role: 'sales_rep',     avatar: 'avatar1' },
    { id: 'u-002', display_name: 'Sana Malik',       email: 'sana.malik@crm.pk',    role: 'sales_rep',     avatar: 'avatar2' },
    { id: 'u-003', display_name: 'Bilal Khan',       email: 'bilal.khan@crm.pk',    role: 'sales_manager', avatar: 'avatar3' },
    { id: 'u-004', display_name: 'Fatima Sheikh',    email: 'fatima.sheikh@crm.pk', role: 'sales_rep',     avatar: 'avatar4' },
    { id: 'u-005', display_name: 'Usman Farooq',     email: 'usman.farooq@crm.pk',  role: 'sales_manager', avatar: 'avatar5' },
  ];

  const LEADS = [
    { lead_id:'l-001', contact_name:'Tariq Mehmood',    contact_phone_e164:'+923011234567', contact_email:'tariq.mehmood@example.com',    stage:'new',         source:'whatsapp',  owner_id:'u-001', priority:'hot',  estimated_value:150000, currency:'PKR', created_at:'2026-05-04T08:00:00Z', updated_at:'2026-05-04T09:00:00Z' },
    { lead_id:'l-002', contact_name:'Nadia Hussain',    contact_phone_e164:'+923219876543', contact_email:'nadia.hussain@example.com',    stage:'qualifying',  source:'web',       owner_id:'u-002', priority:'warm', estimated_value:85000,  currency:'PKR', created_at:'2026-05-03T10:30:00Z', updated_at:'2026-05-04T07:00:00Z' },
    { lead_id:'l-003', contact_name:'Kamran Iqbal',     contact_phone_e164:'+923331122334', contact_email:'kamran.iqbal@example.com',     stage:'qualifying',  source:'referral',  owner_id:'u-001', priority:'hot',  estimated_value:320000, currency:'PKR', created_at:'2026-05-02T09:15:00Z', updated_at:'2026-05-04T11:00:00Z' },
    { lead_id:'l-004', contact_name:'Zara Ahmed',       contact_phone_e164:'+923451234567', contact_email:'zara.ahmed@example.com',       stage:'proposal',    source:'manual',    owner_id:'u-003', priority:'hot',  estimated_value:200000, currency:'PKR', created_at:'2026-04-30T14:00:00Z', updated_at:'2026-05-03T16:00:00Z' },
    { lead_id:'l-005', contact_name:'Imran Butt',       contact_phone_e164:'+923001111222', contact_email:'imran.butt@example.com',       stage:'negotiation', source:'campaign',  owner_id:'u-002', priority:'hot',  estimated_value:500000, currency:'PKR', created_at:'2026-04-28T11:00:00Z', updated_at:'2026-05-02T10:00:00Z' },
    { lead_id:'l-006', contact_name:'Rabia Chaudhry',   contact_phone_e164:'+923123334455', contact_email:'rabia.chaudhry@example.com',   stage:'won',         source:'web',       owner_id:'u-004', priority:'warm', estimated_value:95000,  currency:'PKR', created_at:'2026-04-25T09:00:00Z', updated_at:'2026-05-01T13:00:00Z' },
    { lead_id:'l-007', contact_name:'Hassan Mirza',     contact_phone_e164:'+923049988776', contact_email:'hassan.mirza@example.com',     stage:'lost',        source:'import',    owner_id:'u-005', priority:'cold', estimated_value:60000,  currency:'PKR', created_at:'2026-04-20T08:30:00Z', updated_at:'2026-04-29T09:00:00Z' },
    { lead_id:'l-008', contact_name:'Ayesha Siddiqui',  contact_phone_e164:'+923355566677', contact_email:'ayesha.siddiqui@example.com',  stage:'new',         source:'whatsapp',  owner_id:'u-001', priority:'hot',  estimated_value:275000, currency:'PKR', created_at:'2026-05-05T06:00:00Z', updated_at:'2026-05-05T06:00:00Z' },
    { lead_id:'l-009', contact_name:'Faisal Mahmood',   contact_phone_e164:'+923217788990', contact_email:'faisal.mahmood@example.com',   stage:'qualifying',  source:'web',       owner_id:'u-002', priority:'warm', estimated_value:120000, currency:'PKR', created_at:'2026-05-01T13:00:00Z', updated_at:'2026-05-03T09:00:00Z' },
    { lead_id:'l-010', contact_name:'Sobia Nawaz',      contact_phone_e164:'+923001239876', contact_email:'sobia.nawaz@example.com',      stage:'qualifying',  source:'referral',  owner_id:'u-003', priority:'hot',  estimated_value:180000, currency:'PKR', created_at:'2026-04-29T15:00:00Z', updated_at:'2026-05-04T14:00:00Z' },
    { lead_id:'l-011', contact_name:'Ali Hassan',       contact_phone_e164:'+923451239876', contact_email:'ali.hassan@example.com',       stage:'proposal',    source:'whatsapp',  owner_id:'u-004', priority:'hot',  estimated_value:420000, currency:'PKR', created_at:'2026-04-27T10:00:00Z', updated_at:'2026-05-02T11:00:00Z' },
    { lead_id:'l-012', contact_name:'Mariam Zaidi',     contact_phone_e164:'+923331239876', contact_email:'mariam.zaidi@example.com',     stage:'negotiation', source:'manual',    owner_id:'u-001', priority:'hot',  estimated_value:650000, currency:'PKR', created_at:'2026-04-24T09:00:00Z', updated_at:'2026-05-01T16:00:00Z' },
    { lead_id:'l-013', contact_name:'Omar Farhan',      contact_phone_e164:'+923219876001', contact_email:'omar.farhan@example.com',      stage:'new',         source:'web',       owner_id:'u-002', priority:'warm', estimated_value:75000,  currency:'PKR', created_at:'2026-05-05T07:30:00Z', updated_at:'2026-05-05T07:30:00Z' },
    { lead_id:'l-014', contact_name:'Hina Baig',        contact_phone_e164:'+923012345001', contact_email:'hina.baig@example.com',        stage:'qualifying',  source:'campaign',  owner_id:'u-005', priority:'cold', estimated_value:50000,  currency:'PKR', created_at:'2026-05-03T12:00:00Z', updated_at:'2026-05-04T10:00:00Z' },
    { lead_id:'l-015', contact_name:'Saad Qureshi',     contact_phone_e164:'+923459876001', contact_email:'saad.qureshi@example.com',     stage:'qualifying',  source:'web',       owner_id:'u-003', priority:'hot',  estimated_value:300000, currency:'PKR', created_at:'2026-04-26T11:00:00Z', updated_at:'2026-05-03T13:00:00Z' },
    { lead_id:'l-016', contact_name:'Asma Riaz',        contact_phone_e164:'+923211112223', contact_email:'asma.riaz@example.com',        stage:'new',         source:'whatsapp',  owner_id:'u-001', priority:'warm', estimated_value:90000,  currency:'PKR', created_at:'2026-05-04T16:00:00Z', updated_at:'2026-05-04T16:00:00Z' },
    { lead_id:'l-017', contact_name:'Waqar Ijaz',       contact_phone_e164:'+923334445556', contact_email:'waqar.ijaz@example.com',       stage:'proposal',    source:'referral',  owner_id:'u-004', priority:'hot',  estimated_value:750000, currency:'PKR', created_at:'2026-04-22T09:00:00Z', updated_at:'2026-04-30T14:00:00Z' },
    { lead_id:'l-018', contact_name:'Naila Shafiq',     contact_phone_e164:'+923001112221', contact_email:'naila.shafiq@example.com',     stage:'qualifying',  source:'web',       owner_id:'u-002', priority:'cold', estimated_value:45000,  currency:'PKR', created_at:'2026-05-02T08:00:00Z', updated_at:'2026-05-04T09:30:00Z' },
    { lead_id:'l-019', contact_name:'Adeel Aslam',      contact_phone_e164:'+923218887776', contact_email:'adeel.aslam@example.com',      stage:'won',         source:'manual',    owner_id:'u-005', priority:'warm', estimated_value:135000, currency:'PKR', created_at:'2026-04-15T10:00:00Z', updated_at:'2026-04-28T11:00:00Z' },
    { lead_id:'l-020', contact_name:'Kiran Shahid',     contact_phone_e164:'+923451118889', contact_email:'kiran.shahid@example.com',     stage:'new',         source:'import',    owner_id:'u-003', priority:'warm', estimated_value:110000, currency:'PKR', created_at:'2026-05-05T09:00:00Z', updated_at:'2026-05-05T09:00:00Z' },
  ];

  const FOLLOWUPS = [
    { task_id:'f-001', lead_id:'l-001', lead_name:'Tariq Mehmood',   state:'overdue',   escalation_level:'escalated', due_at:'2026-05-01T10:00:00Z', owner_id:'u-001', owner_name:'Ahmed Raza',    rule_type:'first_contact',    action_type:'Call',      attempts_count:3  },
    { task_id:'f-002', lead_id:'l-002', lead_name:'Nadia Hussain',   state:'overdue',   escalation_level:'escalated', due_at:'2026-04-30T14:00:00Z', owner_id:'u-002', owner_name:'Sana Malik',    rule_type:'idle_lead',        action_type:'WhatsApp',  attempts_count:2  },
    { task_id:'f-003', lead_id:'l-009', lead_name:'Faisal Mahmood',  state:'overdue',   escalation_level:'escalated', due_at:'2026-05-02T09:00:00Z', owner_id:'u-002', owner_name:'Sana Malik',    rule_type:'stage_stall',      action_type:'Reminder',  attempts_count:4  },
    { task_id:'f-004', lead_id:'l-003', lead_name:'Kamran Iqbal',    state:'overdue',   escalation_level:'warning',   due_at:'2026-05-03T11:00:00Z', owner_id:'u-001', owner_name:'Ahmed Raza',    rule_type:'idle_lead',        action_type:'Call',      attempts_count:1  },
    { task_id:'f-005', lead_id:'l-014', lead_name:'Hina Baig',       state:'overdue',   escalation_level:'warning',   due_at:'2026-05-04T08:00:00Z', owner_id:'u-005', owner_name:'Usman Farooq',  rule_type:'first_contact',    action_type:'WhatsApp',  attempts_count:0  },
    { task_id:'f-006', lead_id:'l-018', lead_name:'Naila Shafiq',    state:'overdue',   escalation_level:'warning',   due_at:'2026-05-04T12:00:00Z', owner_id:'u-002', owner_name:'Sana Malik',    rule_type:'stage_stall',      action_type:'Call',      attempts_count:1  },
    { task_id:'f-007', lead_id:'l-004', lead_name:'Zara Ahmed',      state:'pending',   escalation_level:'reminder',  due_at:'2026-05-26T10:00:00Z', owner_id:'u-003', owner_name:'Bilal Khan',    rule_type:'proposal_followup',action_type:'WhatsApp',  attempts_count:2  },
    { task_id:'f-008', lead_id:'l-005', lead_name:'Imran Butt',      state:'pending',   escalation_level:'reminder',  due_at:'2026-05-27T14:00:00Z', owner_id:'u-002', owner_name:'Sana Malik',    rule_type:'negotiation_check',action_type:'Call',      attempts_count:0  },
    { task_id:'f-009', lead_id:'l-010', lead_name:'Sobia Nawaz',     state:'pending',   escalation_level:'reminder',  due_at:'2026-05-28T09:00:00Z', owner_id:'u-003', owner_name:'Bilal Khan',    rule_type:'idle_lead',        action_type:'Reminder',  attempts_count:5  },
    { task_id:'f-010', lead_id:'l-011', lead_name:'Ali Hassan',      state:'pending',   escalation_level:'warning',   due_at:'2026-05-26T16:00:00Z', owner_id:'u-004', owner_name:'Fatima Sheikh', rule_type:'proposal_followup',action_type:'WhatsApp',  attempts_count:1  },
    { task_id:'f-011', lead_id:'l-006', lead_name:'Rabia Chaudhry',  state:'completed', escalation_level:'reminder',  due_at:'2026-05-01T10:00:00Z', owner_id:'u-004', owner_name:'Fatima Sheikh', rule_type:'first_contact',    action_type:'Call',      attempts_count:3  },
    { task_id:'f-012', lead_id:'l-019', lead_name:'Adeel Aslam',     state:'completed', escalation_level:'reminder',  due_at:'2026-04-27T09:00:00Z', owner_id:'u-005', owner_name:'Usman Farooq',  rule_type:'stage_stall',      action_type:'Reminder',  attempts_count:2  },
    { task_id:'f-013', lead_id:'l-013', lead_name:'Omar Farhan',     state:'pending',   escalation_level:'reminder',  due_at:'2026-05-29T11:00:00Z', owner_id:'u-002', owner_name:'Sana Malik',    rule_type:'first_contact',    action_type:'WhatsApp',  attempts_count:0  },
    { task_id:'f-014', lead_id:'l-015', lead_name:'Saad Qureshi',    state:'pending',   escalation_level:'reminder',  due_at:'2026-05-30T10:00:00Z', owner_id:'u-003', owner_name:'Bilal Khan',    rule_type:'idle_lead',        action_type:'Call',      attempts_count:1  },
    { task_id:'f-015', lead_id:'l-017', lead_name:'Waqar Ijaz',      state:'overdue',   escalation_level:'escalated', due_at:'2026-05-03T09:00:00Z', owner_id:'u-004', owner_name:'Fatima Sheikh', rule_type:'proposal_followup',action_type:'Call',      attempts_count:4  },
  ];

  const OPPORTUNITIES = [
    { opportunity_id:'o-001', name:'Al-Noor Textile ERP',      account_id:'a-001', account_name:'Al-Noor Textile',      stage:'proposal',     amount:850000,  currency:'PKR', forecast_category:'best_case', close_date:'2026-06-30', owner_id:'u-003', probability:65 },
    { opportunity_id:'o-002', name:'City Pharma CRM Rollout',  account_id:'a-002', account_name:'City Pharma Ltd',      stage:'negotiation',  amount:1200000, currency:'PKR', forecast_category:'commit',    close_date:'2026-05-31', owner_id:'u-001', probability:80 },
    { opportunity_id:'o-003', name:'FastLog Logistics Portal', account_id:'a-003', account_name:'FastLog Pvt Ltd',      stage:'qualification',amount:320000,  currency:'PKR', forecast_category:'pipeline',  close_date:'2026-07-15', owner_id:'u-002', probability:30 },
    { opportunity_id:'o-004', name:'Sunrise Builders Suite',   account_id:'a-004', account_name:'Sunrise Builders',     stage:'closed_won',   amount:950000,  currency:'PKR', forecast_category:'closed',    close_date:'2026-04-30', owner_id:'u-004', probability:100 },
    { opportunity_id:'o-005', name:'KPK Agri Connect',         account_id:'a-005', account_name:'KPK Agri Traders',     stage:'discovery',    amount:450000,  currency:'PKR', forecast_category:'pipeline',  close_date:'2026-08-01', owner_id:'u-005', probability:40 },
    { opportunity_id:'o-006', name:'Metro Retail POS',         account_id:'a-006', account_name:'Metro Retail Group',   stage:'proposal',     amount:680000,  currency:'PKR', forecast_category:'best_case', close_date:'2026-06-15', owner_id:'u-001', probability:60 },
    { opportunity_id:'o-007', name:'Pak Steel HR Module',      account_id:'a-007', account_name:'Pak Steel Works',      stage:'negotiation',  amount:2100000, currency:'PKR', forecast_category:'commit',    close_date:'2026-05-20', owner_id:'u-003', probability:85 },
    { opportunity_id:'o-008', name:'Horizon Real Estate CRM',  account_id:'a-008', account_name:'Horizon Properties',   stage:'closed_lost',  amount:550000,  currency:'PKR', forecast_category:'omitted',   close_date:'2026-04-15', owner_id:'u-002', probability:0  },
    { opportunity_id:'o-009', name:'Iqbal Foods ERP Upgrade',  account_id:'a-009', account_name:'Iqbal Foods Ltd',      stage:'qualification',amount:390000,  currency:'PKR', forecast_category:'pipeline',  close_date:'2026-09-01', owner_id:'u-004', probability:25 },
    { opportunity_id:'o-010', name:'Pakistan TeleCo Support',  account_id:'a-010', account_name:'PK Telecom Services',  stage:'proposal',     amount:1450000, currency:'PKR', forecast_category:'best_case', close_date:'2026-07-01', owner_id:'u-005', probability:55 },
    { opportunity_id:'o-011', name:'Lahore Hospital Suite',    account_id:'a-011', account_name:'Lahore Gen Hospital',  stage:'discovery',    amount:870000,  currency:'PKR', forecast_category:'pipeline',  close_date:'2026-08-15', owner_id:'u-001', probability:35 },
    { opportunity_id:'o-012', name:'ZK Motors Inventory',      account_id:'a-012', account_name:'ZK Motors Ltd',        stage:'negotiation',  amount:780000,  currency:'PKR', forecast_category:'commit',    close_date:'2026-05-28', owner_id:'u-002', probability:75 },
  ];

  const CONTACTS = [
    { contact_id:'c-001', display_name:'Tariq Mehmood',   phone_e164:'+923011234567', email:'tariq@example.com',  account_id:'a-001', account_name:'Al-Noor Textile',    completeness_score:85, created_at:'2026-04-01T09:00:00Z', open_cases:1, idle:0, tags:['Lead','Hot'],       last_touchpoint:'5 hrs ago'  },
    { contact_id:'c-002', display_name:'Nadia Hussain',   phone_e164:'+923219876543', email:'nadia@example.com',  account_id:'a-002', account_name:'City Pharma Ltd',    completeness_score:72, created_at:'2026-04-05T10:00:00Z', open_cases:0, idle:0, tags:['Customer'],         last_touchpoint:'Today'      },
    { contact_id:'c-003', display_name:'Kamran Iqbal',    phone_e164:'+923331122334', email:'kamran@example.com', account_id:'a-003', account_name:'FastLog Pvt Ltd',    completeness_score:91, created_at:'2026-03-28T11:00:00Z', open_cases:1, idle:1, tags:['Lead','Hot'],       last_touchpoint:'1 day ago'  },
    { contact_id:'c-004', display_name:'Zara Ahmed',      phone_e164:'+923451234567', email:'zara@example.com',   account_id:'a-004', account_name:'Sunrise Builders',   completeness_score:68, created_at:'2026-04-10T08:00:00Z', open_cases:0, idle:0, tags:['WhatsApp'],         last_touchpoint:'3 hrs ago'  },
    { contact_id:'c-005', display_name:'Imran Butt',      phone_e164:'+923001111222', email:'imran@example.com',  account_id:'a-005', account_name:'KPK Agri Traders',   completeness_score:55, created_at:'2026-04-12T14:00:00Z', open_cases:1, idle:0, tags:['Lead'],             last_touchpoint:'30 min ago' },
    { contact_id:'c-006', display_name:'Rabia Chaudhry',  phone_e164:'+923123334455', email:'rabia@example.com',  account_id:'a-006', account_name:'Metro Retail Group', completeness_score:79, created_at:'2026-04-08T10:00:00Z', open_cases:0, idle:0, tags:['Customer','VIP'],   last_touchpoint:'4 hrs ago'  },
    { contact_id:'c-007', display_name:'Hassan Mirza',    phone_e164:'+923049988776', email:'hassan@example.com', account_id:'a-007', account_name:'Pak Steel Works',    completeness_score:88, created_at:'2026-03-20T09:00:00Z', open_cases:0, idle:0, tags:['Lead'],             last_touchpoint:'1 hr ago'   },
    { contact_id:'c-008', display_name:'Ayesha Siddiqui', phone_e164:'+923355566677', email:'ayesha@example.com', account_id:'a-008', account_name:'Horizon Properties', completeness_score:62, created_at:'2026-04-18T11:00:00Z', open_cases:2, idle:1, tags:['Customer'],         last_touchpoint:'6 hrs ago'  },
    { contact_id:'c-009', display_name:'Faisal Mahmood',  phone_e164:'+923217788990', email:'faisal@example.com', account_id:'a-009', account_name:'Iqbal Foods Ltd',    completeness_score:74, created_at:'2026-04-02T13:00:00Z', open_cases:0, idle:0, tags:['Lead','New'],       last_touchpoint:'45 min ago' },
    { contact_id:'c-010', display_name:'Sobia Nawaz',     phone_e164:'+923001239876', email:'sobia@example.com',  account_id:'a-010', account_name:'PK Telecom Services',completeness_score:81, created_at:'2026-03-25T10:00:00Z', open_cases:0, idle:1, tags:['Customer'],         last_touchpoint:'2 days ago' },
    { contact_id:'c-011', display_name:'Ali Hassan',      phone_e164:'+923451239876', email:'ali@example.com',    account_id:'a-011', account_name:'Lahore Gen Hospital', completeness_score:93, created_at:'2026-03-15T09:00:00Z', open_cases:2, idle:0, tags:['Lead','WhatsApp'],  last_touchpoint:'2 hrs ago'  },
    { contact_id:'c-012', display_name:'Mariam Zaidi',    phone_e164:'+923331239876', email:'mariam@example.com', account_id:'a-012', account_name:'ZK Motors Ltd',      completeness_score:70, created_at:'2026-04-14T08:30:00Z', open_cases:0, idle:0, tags:['Lead'],             last_touchpoint:'30 min ago' },
    { contact_id:'c-013', display_name:'Omar Farhan',     phone_e164:'+923219876001', email:'omar@example.com',   account_id:'a-001', account_name:'Al-Noor Textile',    completeness_score:58, created_at:'2026-04-20T11:00:00Z', open_cases:0, idle:0, tags:['Lead','New'],       last_touchpoint:'1 hr ago'   },
    { contact_id:'c-014', display_name:'Hina Baig',       phone_e164:'+923012345001', email:'hina@example.com',   account_id:'a-003', account_name:'FastLog Pvt Ltd',    completeness_score:83, created_at:'2026-04-22T09:00:00Z', open_cases:0, idle:1, tags:['WhatsApp'],         last_touchpoint:'Yesterday'  },
    { contact_id:'c-015', display_name:'Saad Qureshi',    phone_e164:'+923459876001', email:'saad@example.com',   account_id:'a-005', account_name:'KPK Agri Traders',   completeness_score:76, created_at:'2026-04-25T10:00:00Z', open_cases:1, idle:0, tags:['Lead'],             last_touchpoint:'3 hrs ago'  },
  ];

  const ACTIVITIES = [
    { activity_id:'act-001', activity_type:'call',       description:'Introductory call with Tariq re: ERP needs',     entity_type:'lead', entity_id:'l-001', performed_by:'u-001', occurred_at:'2026-05-04T09:30:00Z' },
    { activity_id:'act-002', activity_type:'email',      description:'Sent product brochure to Nadia',                 entity_type:'lead', entity_id:'l-002', performed_by:'u-002', occurred_at:'2026-05-04T08:00:00Z' },
    { activity_id:'act-003', activity_type:'whatsapp',   description:'WhatsApp message from Kamran re: proposal',      entity_type:'lead', entity_id:'l-003', performed_by:'u-001', occurred_at:'2026-05-03T17:00:00Z' },
    { activity_id:'act-004', activity_type:'meeting',    description:'In-person meeting at Sunrise Builders office',   entity_type:'lead', entity_id:'l-004', performed_by:'u-003', occurred_at:'2026-05-03T14:00:00Z' },
    { activity_id:'act-005', activity_type:'note',       description:'Updated lead value estimate after site visit',   entity_type:'lead', entity_id:'l-005', performed_by:'u-002', occurred_at:'2026-05-03T11:00:00Z' },
    { activity_id:'act-006', activity_type:'stage_change',description:'Lead moved from qualifying to proposal',        entity_type:'lead', entity_id:'l-003', performed_by:'u-001', occurred_at:'2026-05-02T10:30:00Z' },
    { activity_id:'act-007', activity_type:'call',       description:'Follow-up call with Imran re: contract terms',   entity_type:'lead', entity_id:'l-005', performed_by:'u-002', occurred_at:'2026-05-02T09:00:00Z' },
    { activity_id:'act-008', activity_type:'email',      description:'Sent revised quote to Zara',                     entity_type:'lead', entity_id:'l-004', performed_by:'u-003', occurred_at:'2026-05-01T16:00:00Z' },
    { activity_id:'act-009', activity_type:'whatsapp',   description:'New inbound WhatsApp from Ayesha',               entity_type:'lead', entity_id:'l-008', performed_by:'u-001', occurred_at:'2026-05-01T13:00:00Z' },
    { activity_id:'act-010', activity_type:'deal_won',   description:'Rabia Chaudhry — Deal Closed Won PKR 95,000',    entity_type:'lead', entity_id:'l-006', performed_by:'u-004', occurred_at:'2026-05-01T11:00:00Z' },
    { activity_id:'act-011', activity_type:'note',       description:'Left voicemail for Faisal — no answer',          entity_type:'lead', entity_id:'l-009', performed_by:'u-002', occurred_at:'2026-04-30T15:00:00Z' },
    { activity_id:'act-012', activity_type:'meeting',    description:'Negotiation call with Pak Steel finance team',   entity_type:'opportunity', entity_id:'o-007', performed_by:'u-003', occurred_at:'2026-04-30T10:00:00Z' },
    { activity_id:'act-013', activity_type:'email',      description:'Proposal PDF sent to PK Telecom',               entity_type:'opportunity', entity_id:'o-010', performed_by:'u-005', occurred_at:'2026-04-29T14:00:00Z' },
    { activity_id:'act-014', activity_type:'call',       description:'Discovery call with KPK Agri owner',            entity_type:'opportunity', entity_id:'o-005', performed_by:'u-005', occurred_at:'2026-04-29T11:00:00Z' },
    { activity_id:'act-015', activity_type:'stage_change',description:'Opportunity moved to Negotiation — City Pharma',entity_type:'opportunity', entity_id:'o-002', performed_by:'u-001', occurred_at:'2026-04-28T09:00:00Z' },
    { activity_id:'act-016', activity_type:'whatsapp',   description:'New lead from WhatsApp — Asma Riaz',            entity_type:'lead', entity_id:'l-016', performed_by:'u-001', occurred_at:'2026-05-04T16:30:00Z' },
    { activity_id:'act-017', activity_type:'call',       description:'Manual outbound call connected — Waqar Ijaz interested', entity_type:'lead', entity_id:'l-017', performed_by:'u-004', occurred_at:'2026-04-22T10:00:00Z' },
    { activity_id:'act-018', activity_type:'note',       description:'Demo scheduled for ZK Motors next week',        entity_type:'opportunity', entity_id:'o-012', performed_by:'u-002', occurred_at:'2026-05-04T13:00:00Z' },
    { activity_id:'act-019', activity_type:'deal_won',   description:'Adeel Aslam — Deal Closed Won PKR 1,35,000',   entity_type:'lead', entity_id:'l-019', performed_by:'u-005', occurred_at:'2026-04-28T11:30:00Z' },
    { activity_id:'act-020', activity_type:'email',      description:'Welcome email sent to new contact Kiran Shahid',entity_type:'lead', entity_id:'l-020', performed_by:'u-003', occurred_at:'2026-05-05T09:15:00Z' },
  ];

  const TASKS = [
    { task_id:'t-001', title:'Send pricing sheet to Kamran',    status:'open',        due_at:'2026-05-06T12:00:00Z', owner_id:'u-001', entity_type:'lead',        entity_id:'l-003', priority:'hot'  },
    { task_id:'t-002', title:'Prepare Pak Steel proposal v2',   status:'in_progress', due_at:'2026-05-07T17:00:00Z', owner_id:'u-003', entity_type:'opportunity', entity_id:'o-007', priority:'hot'  },
    { task_id:'t-003', title:'Follow up with City Pharma CFO',  status:'open',        due_at:'2026-05-05T15:00:00Z', owner_id:'u-001', entity_type:'opportunity', entity_id:'o-002', priority:'hot'  },
    { task_id:'t-004', title:'Demo walkthrough for Metro Retail',status:'open',        due_at:'2026-05-08T10:00:00Z', owner_id:'u-001', entity_type:'opportunity', entity_id:'o-006', priority:'warm' },
    { task_id:'t-005', title:'Collect signed NDA from Sunrise', status:'completed',   due_at:'2026-04-30T12:00:00Z', owner_id:'u-004', entity_type:'opportunity', entity_id:'o-004', priority:'hot'  },
    { task_id:'t-006', title:'Schedule discovery call KPK Agri',status:'open',        due_at:'2026-05-09T11:00:00Z', owner_id:'u-005', entity_type:'opportunity', entity_id:'o-005', priority:'cold' },
    { task_id:'t-007', title:'Update contact info for Hina Baig',status:'open',       due_at:'2026-05-06T09:00:00Z', owner_id:'u-005', entity_type:'contact',     entity_id:'c-014', priority:'cold' },
    { task_id:'t-008', title:'Send contract to ZK Motors',      status:'in_progress', due_at:'2026-05-07T16:00:00Z', owner_id:'u-002', entity_type:'opportunity', entity_id:'o-012', priority:'hot'  },
    { task_id:'t-009', title:'Prepare Q2 forecast report',      status:'open',        due_at:'2026-05-12T17:00:00Z', owner_id:'u-003', entity_type:null,          entity_id:null,    priority:'warm' },
    { task_id:'t-010', title:'Onboarding call with Rabia',      status:'completed',   due_at:'2026-05-01T10:00:00Z', owner_id:'u-004', entity_type:'lead',        entity_id:'l-006', priority:'warm' },
    { task_id:'t-011', title:'Renew support contract — PK Tel', status:'open',        due_at:'2026-05-15T12:00:00Z', owner_id:'u-005', entity_type:'opportunity', entity_id:'o-010', priority:'hot'  },
    { task_id:'t-012', title:'WhatsApp broadcast — Eid offer',  status:'open',        due_at:'2026-05-10T09:00:00Z', owner_id:'u-002', entity_type:null,          entity_id:null,    priority:'warm' },
  ];

  const INVOICE_SUMMARIES = {
    today:  { total_revenue: 125000,  period: 'today'  },
    week:   { total_revenue: 840000,  period: 'week'   },
    month:  { total_revenue: 3200000, period: 'month'  },
    today_trend:  [5, 8, 6, 11, 9, 15, 5, 8, 7, 11, 8, 7],
    week_trend:   [70, 85, 75, 120, 100, 150, 140],
    monthly_trend: [
      { month:'Nov', revenue: 2100000, expenses: 1200000 },
      { month:'Dec', revenue: 2800000, expenses: 1500000 },
      { month:'Jan', revenue: 1900000, expenses: 1100000 },
      { month:'Feb', revenue: 2400000, expenses: 1300000 },
      { month:'Mar', revenue: 3100000, expenses: 1700000 },
      { month:'Apr', revenue: 2900000, expenses: 1600000 },
      { month:'May', revenue: 3200000, expenses: 1800000 },
    ]
  };

  const KPI_DELTAS = {
    contacts:    { pct: '+2.1%',  badge_cls: 'bg-success-subtle text-success' },
    deals:       { pct: '+2.6%',  badge_cls: 'bg-success-subtle text-success' },
    revenue:     { label: '+18% vs last month' },
    deals_growth:{ label: '+15% vs last month' }
  };

  const KPI_SPARKLINES = {
    contacts: [180, 210, 240, 195, 225, 284],
    leads:    [65,  72,  68,  80,  75,  82],
    deals:    [60, -10,  75,  30, -20,  80, 50, -15, 85, 60]
  };

  const FOLLOWUP_TREND = [
    { month: 'Dec', completed: 18, snoozed: 8,  overdue: 4  },
    { month: 'Jan', completed: 22, snoozed: 10, overdue: 6  },
    { month: 'Feb', completed: 25, snoozed: 12, overdue: 5  },
    { month: 'Mar', completed: 30, snoozed: 9,  overdue: 8  },
    { month: 'Apr', completed: 28, snoozed: 11, overdue: 7  },
    { month: 'May', completed: 12, snoozed: 6,  overdue: 7  },
  ];

  const LEADS_BY_HOUR = [
    { hour: '8am',  data: [8,  12, 6,  14, 4,  5,  7]  },
    { hour: '10am', data: [18, 22, 16, 28, 10, 12, 8]  },
    { hour: '12pm', data: [28, 26, 20, 45, 22, 18, 15] },
    { hour: '2pm',  data: [12, 16, 10, 20, 25, 22, 12] },
    { hour: '4pm',  data: [8,  12, 7,  16, 18, 14, 10] },
  ];

  const LEAD_FUNNEL_DELTAS = {
    total:         { pct: '+11.6%', badge_cls: 'bg-success-subtle text-success' },
    new_week:      { pct: '+4.2%',  badge_cls: 'bg-success-subtle text-success' },
    qualified:     { pct: '-2.1%',  badge_cls: 'bg-danger-subtle text-danger'   },
    opportunities: { pct: '+6.4%',  badge_cls: 'bg-success-subtle text-success' },
    won:           { pct: '+3.8%',  badge_cls: 'bg-success-subtle text-success' },
    opp_value:     { pct: '+9.4%',  badge_cls: 'bg-success-subtle text-success' },
  };

  const PRICE_BOOKS = [
    { price_book_id:'pbk-001', name:'Standard PKR',            currency:'PKR', is_default:true,  active_from:'2026-01-01T00:00:00Z', active_to:null,
      products: [
        { product_id:'p-001', name:'CRM Base License',        list_price:250000 },
        { product_id:'p-002', name:'Implementation Services', list_price:150000 },
        { product_id:'p-003', name:'Annual Support Contract', list_price:80000  },
        { product_id:'p-004', name:'WhatsApp Integration',    list_price:45000  },
        { product_id:'p-005', name:'Custom Reporting Module', list_price:120000 },
        { product_id:'p-006', name:'Data Migration Service',  list_price:60000  },
      ]
    },
    { price_book_id:'pbk-002', name:'Enterprise PKR',          currency:'PKR', is_default:false, active_from:'2026-01-01T00:00:00Z', active_to:null,
      products: [
        { product_id:'p-001', name:'CRM Base License',        list_price:225000 },
        { product_id:'p-002', name:'Implementation Services', list_price:130000 },
        { product_id:'p-003', name:'Annual Support Contract', list_price:70000  },
      ]
    },
  ];

  const QUOTES = [
    { quote_id:'q-001', quote_number:'Q-2026-0042', status:'pending_approval', account_id:'a-002', account_name:'City Pharma Ltd',   opportunity_id:'o-002', opportunity_name:'City Pharma CRM Rollout',  currency:'PKR', valid_until:'2026-06-30', created_by:'u-001', created_at:'2026-05-20T09:15:00Z',
      line_items:[{ product_id:'p-001', product:'CRM Base License', qty:1, list_price:250000, discount:5 },{ product_id:'p-002', product:'Implementation Services', qty:1, list_price:150000, discount:0 },{ product_id:'p-003', product:'Annual Support Contract', qty:1, list_price:80000, discount:0 }] },
    { quote_id:'q-002', quote_number:'Q-2026-0039', status:'approved',          account_id:'a-007', account_name:'Pak Steel Works',    opportunity_id:'o-007', opportunity_name:'Pak Steel HR Module',      currency:'PKR', valid_until:'2026-06-15', created_by:'u-003', created_at:'2026-05-15T11:00:00Z',
      line_items:[{ product_id:'p-001', product:'CRM Base License', qty:1, list_price:250000, discount:10 },{ product_id:'p-002', product:'Implementation Services', qty:2, list_price:150000, discount:5 }] },
    { quote_id:'q-003', quote_number:'Q-2026-0035', status:'draft',             account_id:'a-001', account_name:'Al-Noor Textile',    opportunity_id:'o-001', opportunity_name:'Al-Noor Textile ERP',      currency:'PKR', valid_until:'2026-07-31', created_by:'u-003', created_at:'2026-05-10T08:30:00Z',
      line_items:[{ product_id:'p-001', product:'CRM Base License', qty:1, list_price:250000, discount:0 },{ product_id:'p-005', product:'Custom Reporting Module', qty:1, list_price:120000, discount:0 }] },
  ];

  const COLLECTIONS = [
    { invoice_id:'inv-001', invoice_number:'INV-001', account_name:'Ahmed Raza',       account_tier:'Individual · South PK',  amount_due:45000,  status:'open', due_date:'2026-04-15', last_reminder_at:'2026-05-24T09:00:00Z', is_overdue:true  },
    { invoice_id:'inv-002', invoice_number:'INV-002', account_name:'Sara Enterprises', account_tier:'SMB · Tier 2',            amount_due:120000, status:'open', due_date:'2026-04-20', last_reminder_at:'2026-05-26T11:00:00Z', is_overdue:true  },
    { invoice_id:'inv-005', invoice_number:'INV-005', account_name:'Hassan Traders',   account_tier:'SMB · Tier 1',            amount_due:95000,  status:'open', due_date:'2026-04-25', last_reminder_at:'2026-05-27T07:00:00Z', is_overdue:true  },
    { invoice_id:'inv-003', invoice_number:'INV-003', account_name:'Bilal & Sons',     account_tier:'SMB · Tier 2',            amount_due:78500,  status:'open', due_date:'2026-05-05', last_reminder_at:'2026-05-27T06:30:00Z', is_overdue:false },
    { invoice_id:'inv-004', invoice_number:'INV-004', account_name:'Zainab Trading',   account_tier:'Individual',              amount_due:32000,  status:'open', due_date:'2026-05-10', last_reminder_at:'2026-05-25T14:00:00Z', is_overdue:false },
    { invoice_id:'inv-006', invoice_number:'INV-006', account_name:'Nadia Enterprises',account_tier:'SMB · Tier 1',            amount_due:55000,  status:'open', due_date:'2026-05-15', last_reminder_at:'2026-05-26T16:00:00Z', is_overdue:false },
    { invoice_id:'inv-007', invoice_number:'INV-007', account_name:'Usman Corp',       account_tier:'Enterprise · Tier 1',    amount_due:88000,  status:'open', due_date:'2026-05-18', last_reminder_at:'2026-05-27T04:00:00Z', is_overdue:false },
    { invoice_id:'inv-008', invoice_number:'INV-008', account_name:'Fatima Industries',account_tier:'SMB · Tier 2',            amount_due:42000,  status:'open', due_date:'2026-05-20', last_reminder_at:'2026-05-27T08:00:00Z', is_overdue:false },
    { invoice_id:'inv-009', invoice_number:'INV-009', account_name:'Kamran Ltd',       account_tier:'Enterprise · Tier 1',    amount_due:165000, status:'open', due_date:'2026-05-22', last_reminder_at:'2026-05-27T09:30:00Z', is_overdue:false },
    { invoice_id:'inv-010', invoice_number:'INV-010', account_name:'Iqra Group',       account_tier:'SMB · Tier 2',            amount_due:28500,  status:'paid', due_date:'2026-05-15', last_reminder_at:'2026-05-24T10:00:00Z', is_overdue:false },
  ];

  const COLLECTIONS_KPI = {
    total_outstanding: 720500,
    overdue_count: 3,
    overdue_value: 260000,
    paid_this_month: 245000,
    paid_this_month_delta: 12,
    collection_rate: 73,
    collection_rate_delta: -3
  };

  const CONTACTS_KPI = {
    total: 1248,
    whatsapp_active: 843,
    open_cases: 47,
    idle_7d: 18,
    new_this_month: 34
  };

  const LEAD_FUNNEL_KPI = {
    total: 8420,
    new_week: 320,
    qualified: 2780,
    opportunities: 1950,
    conversion_rate: '33.0%',
    avg_latency: '2.4 hrs',
    growth_delta: '+18%'
  };

  const AI_MODEL_KPI = {
    model_accuracy: 78,
    lead_score_demo: { score: 72, score_band: 'warm', top_drivers: ['Deal stage', 'Follow-up count', 'Estimated value'] }
  };

  const FORECASTS = {
    period:        'current_quarter',
    generated_at:  '2026-05-27T00:00:00Z',
    weighted_value: 4280000,
    by_category: {
      pipeline:  { count: 8, total_value: 5240000 },
      best_case: { count: 4, total_value: 3180000 },
      commit:    { count: 3, total_value: 4050000 },
      closed:    { count: 2, total_value: 1045000 },
    },
    stage_breakdown: [
      { stage:'qualification', weight:0.10, opportunity_count:2, total_value:710000,  weighted:71000   },
      { stage:'discovery',     weight:0.20, opportunity_count:2, total_value:1320000, weighted:264000  },
      { stage:'proposal',      weight:0.40, opportunity_count:3, total_value:2980000, weighted:1192000 },
      { stage:'negotiation',   weight:0.70, opportunity_count:3, total_value:4080000, weighted:2856000 },
      { stage:'closed_won',    weight:1.00, opportunity_count:1, total_value:950000,  weighted:950000  },
      { stage:'closed_lost',   weight:0.00, opportunity_count:1, total_value:550000,  weighted:0       },
    ],
  };

  const AUDIT_LOG = [
    { audit_id:'aud-00001', occurred_at:'2026-05-27T14:32:00Z', actor_id:'u-001', actor_name:'Ahmed Raza',     action_type:'create', resource_type:'Lead', resource_id:'l-020', result:'allow', hash:'sha256_a1b2c3d4e5f6', chain_position:8, prev_hash:'sha256_h8c9d0e1f2g3' },
    { audit_id:'aud-00002', occurred_at:'2026-05-27T13:15:00Z', actor_id:'u-002', actor_name:'Sana Malik',      action_type:'update', resource_type:'Opportunity', resource_id:'o-002', result:'allow', hash:'sha256_b2c3d4e5f6a7', chain_position:7, prev_hash:'sha256_g7b8c9d0e1f2' },
    { audit_id:'aud-00003', occurred_at:'2026-05-27T12:45:00Z', actor_id:'u-003', actor_name:'Bilal Khan',      action_type:'login', resource_type:'User', resource_id:'u-003', result:'allow', hash:'sha256_c3d4e5f6a7b8', chain_position:6, prev_hash:'sha256_f6a7b8c9d0e1' },
    { audit_id:'aud-00004', occurred_at:'2026-05-27T11:22:00Z', actor_id:'u-001', actor_name:'Ahmed Raza',     action_type:'export', resource_type:'Lead', resource_id:'l-005', result:'allow', hash:'sha256_d4e5f6a7b8c9', chain_position:5, prev_hash:'sha256_e5f6a7b8c9d0' },
    { audit_id:'aud-00005', occurred_at:'2026-05-27T10:08:00Z', actor_id:'u-004', actor_name:'Fatima Sheikh',   action_type:'delete', resource_type:'Task', resource_id:'t-001', result:'deny', hash:'sha256_e5f6a7b8c9d0', chain_position:4, prev_hash:'sha256_d4e5f6a7b8c9' },
    { audit_id:'aud-00006', occurred_at:'2026-05-27T09:33:00Z', actor_id:'u-002', actor_name:'Sana Malik',      action_type:'create', resource_type:'Contact', resource_id:'c-015', result:'allow', hash:'sha256_f6a7b8c9d0e1', chain_position:3, prev_hash:'sha256_c3d4e5f6a7b8' },
    { audit_id:'aud-00007', occurred_at:'2026-05-27T08:19:00Z', actor_id:'u-005', actor_name:'Usman Farooq',    action_type:'update', resource_type:'Opportunity', resource_id:'o-007', result:'allow', hash:'sha256_g7b8c9d0e1f2', chain_position:2, prev_hash:'sha256_b2c3d4e5f6a7' },
    { audit_id:'aud-00008', occurred_at:'2026-05-27T07:42:00Z', actor_id:'u-001', actor_name:'Ahmed Raza',     action_type:'login', resource_type:'User', resource_id:'u-001', result:'allow', hash:'sha256_h8c9d0e1f2g3', chain_position:1, prev_hash:null },
  ];

  const ACCOUNTS = [
    { account_id:'a-001', name:'Al-Noor Textile',     tier:'SMB',        industry:'Textile',      owner_id:'u-001', city:'Lahore',    open_opps:1, outstanding_balance:370000  },
    { account_id:'a-002', name:'City Pharma Ltd',     tier:'Mid-Market', industry:'Healthcare',   owner_id:'u-001', city:'Karachi',   open_opps:1, outstanding_balance:750000  },
    { account_id:'a-003', name:'FastLog Pvt Ltd',     tier:'SMB',        industry:'Logistics',    owner_id:'u-002', city:'Lahore',    open_opps:1, outstanding_balance:160000  },
    { account_id:'a-004', name:'Sunrise Builders',    tier:'SMB',        industry:'Real Estate',  owner_id:'u-004', city:'Islamabad', open_opps:0, outstanding_balance:0       },
    { account_id:'a-005', name:'KPK Agri Traders',    tier:'SMB',        industry:'Agriculture',  owner_id:'u-005', city:'Peshawar',  open_opps:1, outstanding_balance:225000  },
    { account_id:'a-006', name:'Metro Retail Group',  tier:'Mid-Market', industry:'Retail',       owner_id:'u-001', city:'Karachi',   open_opps:1, outstanding_balance:250000  },
    { account_id:'a-007', name:'Pak Steel Works',     tier:'Enterprise', industry:'Manufacturing',owner_id:'u-003', city:'Lahore',    open_opps:1, outstanding_balance:275000  },
    { account_id:'a-008', name:'Horizon Properties',  tier:'SMB',        industry:'Real Estate',  owner_id:'u-002', city:'Islamabad', open_opps:0, outstanding_balance:0       },
    { account_id:'a-009', name:'Iqbal Foods Ltd',     tier:'SMB',        industry:'Food & Bev',   owner_id:'u-004', city:'Faisalabad',open_opps:1, outstanding_balance:0       },
    { account_id:'a-010', name:'PK Telecom Services', tier:'Enterprise', industry:'Telecom',      owner_id:'u-005', city:'Karachi',   open_opps:2, outstanding_balance:820000  },
    { account_id:'a-011', name:'Lahore Gen Hospital', tier:'Mid-Market', industry:'Healthcare',   owner_id:'u-001', city:'Lahore',    open_opps:1, outstanding_balance:0       },
    { account_id:'a-012', name:'ZK Motors Ltd',       tier:'SMB',        industry:'Automotive',   owner_id:'u-002', city:'Lahore',    open_opps:1, outstanding_balance:290000  },
  ];

  const ORDERS = [
    { order_id:'ord-001', order_number:'ORD-2026-001', account_id:'a-002', account_name:'City Pharma Ltd',  status:'activated', total_amount:480000, currency:'PKR',
      billing_address:'23 PECHS Block 2, Karachi', shipping_address:'23 PECHS Block 2, Karachi',
      created_at:'2026-04-28T10:00:00Z', quote_id:'q-001', fulfillment_status:'delivered', invoice_ids:['i-001'],
      line_items:[{ product:'CRM Base License', qty:1, unit_price:237500, discount:5, total:237500 },{ product:'Implementation Services', qty:1, unit_price:150000, discount:0, total:150000 },{ product:'Annual Support Contract', qty:1, unit_price:80000, discount:0, total:80000 }] },
    { order_id:'ord-002', order_number:'ORD-2026-002', account_id:'a-007', account_name:'Pak Steel Works',  status:'draft',     total_amount:550000, currency:'PKR',
      billing_address:'Industrial Area, Lahore', shipping_address:'Industrial Area, Lahore',
      created_at:'2026-05-15T11:00:00Z', quote_id:'q-002', fulfillment_status:'pending', invoice_ids:['i-002'],
      line_items:[{ product:'CRM Base License', qty:1, unit_price:225000, discount:10, total:225000 },{ product:'Implementation Services', qty:2, unit_price:142500, discount:5, total:285000 }] },
  ];

  const TENANT_KPI = {
    tenant_count: 1, plan_tier: 'Growth', seat_count: 5, seat_limit: 20,
    enabled_feature_count: 12, entitlement_limit: 15,
    entitlements_at_limit: 2, entitlement_overage_count: 0,
    renewal_date: '2027-01-01', active_sessions: 3,
  };

  const FEATURE_FLAGS = [
    { flag_key:'contact.fuzzy_name_match', label:'Fuzzy Contact Dedup',      enabled:true,  category:'data',      description:'Enable fuzzy name matching for duplicate contact detection',    rule_type:'tenant_match'       },
    { flag_key:'whatsapp.broadcast',       label:'WhatsApp Broadcast',        enabled:true,  category:'comms',     description:'Allow sending broadcast messages to contact lists',            rule_type:'role_match'         },
    { flag_key:'ai.lead_scoring',          label:'AI Lead Scoring',           enabled:false, category:'ai',        description:'ML-based lead priority scoring (Phase 6 feature)',             rule_type:'percentage_rollout' },
    { flag_key:'cpq.approval_routing',     label:'CPQ Approval Routing',      enabled:true,  category:'sales',     description:'Route quotes with discount >10% to manager approval',          rule_type:'tenant_match'       },
    { flag_key:'collections.auto_remind',  label:'Auto Collections Reminder', enabled:true,  category:'finance',   description:'Auto WhatsApp reminder on overdue invoices',                   rule_type:'tenant_match'       },
    { flag_key:'reports.custom_builder',   label:'Custom Report Builder',     enabled:false, category:'analytics', description:'Drag-and-drop report builder (Phase 6 feature)',               rule_type:'percentage_rollout' },
  ];

  const ROLES = [
    { role_id:'sales_rep',    name:'Sales Rep',    user_count:3, is_system:true,  permissions:['leads.read','leads.create','leads.update','contacts.read','opportunities.read','opportunities.update','followups.read','followups.create'] },
    { role_id:'sales_manager',name:'Sales Manager',user_count:2, is_system:true,  permissions:['leads.*','contacts.*','opportunities.*','followups.*','reports.read','users.read','collections.read'] },
    { role_id:'finance',      name:'Finance',      user_count:0, is_system:true,  permissions:['invoices.*','collections.*','reports.finance','subscriptions.read'] },
    { role_id:'tenant_admin', name:'Tenant Admin', user_count:1, is_system:false, permissions:['*'] },
  ];

  const INVOICES = [
    { invoice_id:'i-001', invoice_number:'INV-2026-001', account_id:'a-002', account_name:'City Pharma Ltd',     total_amount:480000, paid_amount:480000, status:'paid',     due_date:'2026-04-30', created_at:'2026-04-15T09:00:00Z', opportunity_id:'o-002' },
    { invoice_id:'i-002', invoice_number:'INV-2026-002', account_id:'a-007', account_name:'Pak Steel Works',     total_amount:550000, paid_amount:275000, status:'partial',   due_date:'2026-05-15', created_at:'2026-04-28T10:00:00Z', opportunity_id:'o-007' },
    { invoice_id:'i-003', invoice_number:'INV-2026-003', account_id:'a-001', account_name:'Al-Noor Textile',     total_amount:370000, paid_amount:0,       status:'overdue',   due_date:'2026-05-01', created_at:'2026-05-01T08:00:00Z', opportunity_id:'o-001' },
    { invoice_id:'i-004', invoice_number:'INV-2026-004', account_id:'a-006', account_name:'Metro Retail Group',  total_amount:250000, paid_amount:0,       status:'sent',      due_date:'2026-06-01', created_at:'2026-05-15T11:00:00Z', opportunity_id:'o-006' },
    { invoice_id:'i-005', invoice_number:'INV-2026-005', account_id:'a-010', account_name:'PK Telecom Services', total_amount:820000, paid_amount:0,       status:'draft',     due_date:'2026-06-15', created_at:'2026-05-20T14:00:00Z', opportunity_id:'o-010' },
    { invoice_id:'i-006', invoice_number:'INV-2026-006', account_id:'a-004', account_name:'Sunrise Builders',    total_amount:950000, paid_amount:950000,  status:'paid',      due_date:'2026-04-15', created_at:'2026-03-30T09:00:00Z', opportunity_id:'o-004' },
    { invoice_id:'i-007', invoice_number:'INV-2026-007', account_id:'a-012', account_name:'ZK Motors Ltd',       total_amount:390000, paid_amount:100000,  status:'partial',   due_date:'2026-05-28', created_at:'2026-05-10T10:00:00Z', opportunity_id:'o-012' },
    { invoice_id:'i-008', invoice_number:'INV-2026-008', account_id:'a-003', account_name:'FastLog Pvt Ltd',     total_amount:160000, paid_amount:0,       status:'overdue',   due_date:'2026-04-20', created_at:'2026-04-05T08:00:00Z', opportunity_id:'o-003' },
    { invoice_id:'i-009', invoice_number:'INV-2026-009', account_id:'a-005', account_name:'KPK Agri Traders',    total_amount:225000, paid_amount:0,       status:'sent',      due_date:'2026-06-10', created_at:'2026-05-22T09:00:00Z', opportunity_id:'o-005' },
    { invoice_id:'i-010', invoice_number:'INV-2026-010', account_id:'a-009', account_name:'Iqbal Foods Ltd',     total_amount:195000, paid_amount:195000,  status:'paid',      due_date:'2026-05-05', created_at:'2026-04-20T11:00:00Z', opportunity_id:'o-009' },
  ];

  const SUBSCRIPTIONS = [
    { subscription_id:'sub-001', plan:'CRM Growth',   account_id:'a-002', account_name:'City Pharma Ltd',     mrr:40000, arr:480000,  status:'active',    start_date:'2026-01-01', renewal_date:'2027-01-01', auto_renew:true,  billing_cycle:'annual',  churn_risk:'low',    contact_name:'Nadia Hussain'   },
    { subscription_id:'sub-002', plan:'CRM Business', account_id:'a-007', account_name:'Pak Steel Works',     mrr:87500, arr:1050000, status:'active',    start_date:'2025-07-01', renewal_date:'2026-07-01', auto_renew:true,  billing_cycle:'annual',  churn_risk:'low',    contact_name:'Hassan Mirza'    },
    { subscription_id:'sub-003', plan:'CRM Starter',  account_id:'a-001', account_name:'Al-Noor Textile',     mrr:20000, arr:240000,  status:'past_due',  start_date:'2026-02-01', renewal_date:'2027-02-01', auto_renew:false, billing_cycle:'monthly', churn_risk:'high',   contact_name:'Tariq Mehmood'   },
    { subscription_id:'sub-004', plan:'CRM Growth',   account_id:'a-004', account_name:'Sunrise Builders',    mrr:40000, arr:480000,  status:'active',    start_date:'2025-10-01', renewal_date:'2026-10-01', auto_renew:true,  billing_cycle:'annual',  churn_risk:'medium', contact_name:'Zara Ahmed'      },
    { subscription_id:'sub-005', plan:'CRM Starter',  account_id:'a-009', account_name:'Iqbal Foods Ltd',     mrr:20000, arr:240000,  status:'trialing',  start_date:'2026-05-01', renewal_date:'2026-08-01', auto_renew:false, billing_cycle:'monthly', churn_risk:'medium', contact_name:'Faisal Mahmood'  },
    { subscription_id:'sub-006', plan:'CRM Business', account_id:'a-010', account_name:'PK Telecom Services', mrr:87500, arr:1050000, status:'active',    start_date:'2025-09-01', renewal_date:'2026-09-01', auto_renew:true,  billing_cycle:'annual',  churn_risk:'low',    contact_name:'Sobia Nawaz'     },
    { subscription_id:'sub-007', plan:'CRM Growth',   account_id:'a-006', account_name:'Metro Retail Group',  mrr:40000, arr:480000,  status:'paused',    start_date:'2026-01-15', renewal_date:'2027-01-15', auto_renew:false, billing_cycle:'annual',  churn_risk:'high',   contact_name:'Rabia Chaudhry'  },
    { subscription_id:'sub-008', plan:'CRM Starter',  account_id:'a-012', account_name:'ZK Motors Ltd',       mrr:20000, arr:240000,  status:'cancelled', start_date:'2025-06-01', renewal_date:'2026-06-01', auto_renew:false, billing_cycle:'monthly', churn_risk:'high',   contact_name:'Mariam Zaidi'    },
  ];

  const SUBSCRIPTION_KPI = {
    mrr: 335000,
    arr: 4020000,
    renewal_rate: 87,
    churn_flag_count: 3,
    delinquency_count: 1,
    expansion_churn_delta: 12,
    cohort_retention: [
      { month:'Dec', rate:82 }, { month:'Jan', rate:85 }, { month:'Feb', rate:84 },
      { month:'Mar', rate:86 }, { month:'Apr', rate:88 }, { month:'May', rate:87 },
    ]
  };

  const RBAC_ASSIGNMENT_LOG = [
    { log_id:'rbac-00001', event_date:'2026-05-25T14:00:00Z', user_id:'u-002', user_name:'Sana Malik',    action:'assigned', role_id:'sales_rep', role_name:'Sales Rep', assigned_by:'u-001' },
    { log_id:'rbac-00002', event_date:'2026-05-23T10:30:00Z', user_id:'u-003', user_name:'Bilal Khan',    action:'assigned', role_id:'sales_manager', role_name:'Sales Manager', assigned_by:'u-001' },
    { log_id:'rbac-00003', event_date:'2026-05-20T09:00:00Z', user_id:'u-004', user_name:'Fatima Sheikh', action:'removed', role_id:'compliance_officer', role_name:'Compliance Officer', assigned_by:'u-001' },
    { log_id:'rbac-00004', event_date:'2026-05-18T15:45:00Z', user_id:'u-005', user_name:'Usman Farooq',  action:'assigned', role_id:'sales_manager', role_name:'Sales Manager', assigned_by:'u-001' },
    { log_id:'rbac-00005', event_date:'2026-05-15T11:20:00Z', user_id:'u-001', user_name:'Ahmed Raza',    action:'assigned', role_id:'sales_rep', role_name:'Sales Rep', assigned_by:'u-001' },
  ];

  const CASES = [
    { case_id:'cs-001', case_number:'CS-2026-001', subject:'Cannot access CRM dashboard',      status:'OPEN',               priority:'high',     assigned_to_id:null,    contact_id:'c-001', contact_name:'Tariq Mehmood',   account_id:'a-001', account_name:'Al-Noor Textile',    sla_state:'breached', response_due_at:'2026-05-27T10:00:00Z', sla_resolution_due_at:'2026-05-28T10:00:00Z', category:'technical', queue:'Tier 1 Support', created_at:'2026-05-27T08:00:00Z', source:'whatsapp' },
    { case_id:'cs-002', case_number:'CS-2026-002', subject:'Invoice payment not reflecting',   status:'IN_PROGRESS',        priority:'critical', assigned_to_id:'u-001', contact_id:'c-002', contact_name:'Nadia Hussain',    account_id:'a-002', account_name:'City Pharma Ltd',    sla_state:'breached', response_due_at:'2026-05-26T14:00:00Z', sla_resolution_due_at:'2026-05-27T14:00:00Z', category:'billing',   queue:'Billing',        created_at:'2026-05-26T12:00:00Z', source:'email'    },
    { case_id:'cs-003', case_number:'CS-2026-003', subject:'WhatsApp integration failing',     status:'ASSIGNED',           priority:'high',     assigned_to_id:'u-002', contact_id:'c-003', contact_name:'Kamran Iqbal',     account_id:'a-003', account_name:'FastLog Pvt Ltd',    sla_state:'at_risk',  response_due_at:'2026-05-29T11:00:00Z', sla_resolution_due_at:'2026-05-30T11:00:00Z', category:'technical', queue:'Tier 2 Support', created_at:'2026-05-28T09:00:00Z', source:'web_form' },
    { case_id:'cs-004', case_number:'CS-2026-004', subject:'Data import failed for leads',     status:'WAITING_ON_CUSTOMER',priority:'medium',   assigned_to_id:'u-003', contact_id:'c-004', contact_name:'Zara Ahmed',       account_id:'a-004', account_name:'Sunrise Builders',   sla_state:'healthy',  response_due_at:'2026-05-30T16:00:00Z', sla_resolution_due_at:'2026-06-01T16:00:00Z', category:'technical', queue:'Tier 1 Support', created_at:'2026-05-28T14:00:00Z', source:'email'    },
    { case_id:'cs-005', case_number:'CS-2026-005', subject:'User password reset needed',       status:'OPEN',               priority:'low',      assigned_to_id:null,    contact_id:'c-005', contact_name:'Imran Butt',       account_id:'a-005', account_name:'KPK Agri Traders',   sla_state:'at_risk',  response_due_at:'2026-05-29T09:00:00Z', sla_resolution_due_at:'2026-05-31T09:00:00Z', category:'general',   queue:'Tier 1 Support', created_at:'2026-05-29T07:00:00Z', source:'phone'    },
    { case_id:'cs-006', case_number:'CS-2026-006', subject:'Monthly report export failing',    status:'RESOLVED',           priority:'medium',   assigned_to_id:'u-004', contact_id:'c-006', contact_name:'Rabia Chaudhry',   account_id:'a-006', account_name:'Metro Retail Group', sla_state:'healthy',  response_due_at:'2026-05-28T12:00:00Z', sla_resolution_due_at:'2026-05-29T12:00:00Z', category:'billing',   queue:'Billing',        created_at:'2026-05-27T10:00:00Z', source:'whatsapp' },
    { case_id:'cs-007', case_number:'CS-2026-007', subject:'Role permissions not applying',    status:'IN_PROGRESS',        priority:'high',     assigned_to_id:'u-002', contact_id:'c-007', contact_name:'Hassan Mirza',     account_id:'a-007', account_name:'Pak Steel Works',    sla_state:'at_risk',  response_due_at:'2026-05-29T14:00:00Z', sla_resolution_due_at:'2026-05-30T14:00:00Z', category:'technical', queue:'Tier 2 Support', created_at:'2026-05-28T11:00:00Z', source:'email'    },
    { case_id:'cs-008', case_number:'CS-2026-008', subject:'API integration timeout errors',   status:'ESCALATED',          priority:'critical', assigned_to_id:'u-003', contact_id:'c-008', contact_name:'Ayesha Siddiqui',  account_id:'a-008', account_name:'Horizon Properties', sla_state:'breached', response_due_at:'2026-05-26T09:00:00Z', sla_resolution_due_at:'2026-05-27T09:00:00Z', category:'technical', queue:'Escalation',     created_at:'2026-05-25T08:00:00Z', source:'phone'    },
    { case_id:'cs-009', case_number:'CS-2026-009', subject:'Subscription renewal failed',      status:'OPEN',               priority:'high',     assigned_to_id:null,    contact_id:'c-009', contact_name:'Faisal Mahmood',   account_id:'a-009', account_name:'Iqbal Foods Ltd',    sla_state:'healthy',  response_due_at:'2026-05-30T10:00:00Z', sla_resolution_due_at:'2026-06-01T10:00:00Z', category:'billing',   queue:'Billing',        created_at:'2026-05-29T08:00:00Z', source:'whatsapp' },
    { case_id:'cs-010', case_number:'CS-2026-010', subject:'Custom report not loading',        status:'ASSIGNED',           priority:'medium',   assigned_to_id:'u-005', contact_id:'c-010', contact_name:'Sobia Nawaz',      account_id:'a-010', account_name:'PK Telecom Services',sla_state:'healthy',  response_due_at:'2026-05-31T11:00:00Z', sla_resolution_due_at:'2026-06-02T11:00:00Z', category:'general',   queue:'Tier 1 Support', created_at:'2026-05-29T09:30:00Z', source:'email'    },
  ];

  const CASE_SLA_KPI = {
    sla_breach_count: 3, open_case_count: 7, avg_first_response_minutes: 42,
    breach_rate: 17, at_risk_case_count: 3, unacknowledged_breach_count: 2,
  };

  const PARTNERS = [
    { partner_id:'p-001', name:'NovaTech Solutions',    partner_tier:'Platinum', region:'Punjab',      city:'Lahore',    status:'active',   attributed_opp_count:5, commission_due:185000, contact_name:'Qasim Ali',    contact_email:'qasim@novatech.pk',    created_at:'2025-03-15T09:00:00Z' },
    { partner_id:'p-002', name:'DigitalBridge Pvt Ltd', partner_tier:'Gold',     region:'Sindh',       city:'Karachi',   status:'active',   attributed_opp_count:3, commission_due:92000,  contact_name:'Rida Farouk',  contact_email:'rida@digitalbridge.pk', created_at:'2025-06-01T10:00:00Z' },
    { partner_id:'p-003', name:'PakSystems Inc',        partner_tier:'Gold',     region:'Punjab',      city:'Islamabad', status:'active',   attributed_opp_count:4, commission_due:140000, contact_name:'Shahzad Gill', contact_email:'shahzad@paksystems.pk', created_at:'2025-04-20T09:00:00Z' },
    { partner_id:'p-004', name:'ByteWave Technologies', partner_tier:'Silver',   region:'KPK',         city:'Peshawar',  status:'active',   attributed_opp_count:2, commission_due:48000,  contact_name:'Asif Khattak', contact_email:'asif@bytewave.pk',      created_at:'2025-09-10T11:00:00Z' },
    { partner_id:'p-005', name:'CloudFirst Pakistan',   partner_tier:'Silver',   region:'Sindh',       city:'Karachi',   status:'active',   attributed_opp_count:1, commission_due:32000,  contact_name:'Mehwish Baig', contact_email:'mehwish@cloudfirst.pk', created_at:'2025-11-05T10:00:00Z' },
    { partner_id:'p-006', name:'SmartLink Pvt Ltd',     partner_tier:'Platinum', region:'Punjab',      city:'Lahore',    status:'active',   attributed_opp_count:7, commission_due:265000, contact_name:'Tariq Aziz',   contact_email:'tariq@smartlink.pk',    created_at:'2025-01-20T09:00:00Z' },
    { partner_id:'p-007', name:'DataSphere Corp',       partner_tier:'Gold',     region:'Balochistan', city:'Quetta',    status:'inactive', attributed_opp_count:0, commission_due:0,      contact_name:'Khalid Mengal',contact_email:'khalid@datasphere.pk',  created_at:'2025-07-15T10:00:00Z' },
    { partner_id:'p-008', name:'TechAxis Solutions',    partner_tier:'Silver',   region:'KPK',         city:'Peshawar',  status:'active',   attributed_opp_count:1, commission_due:25000,  contact_name:'Adnan Yusuf',  contact_email:'adnan@techaxis.pk',     created_at:'2026-01-10T09:00:00Z' },
  ];

  const CAMPAIGNS = [
    { campaign_id:'cmp-001', name:'Eid Mubarak Offer 2026',    type:'whatsapp_broadcast', status:'completed', segment_name:'All Active Leads',  start_date:'2026-04-01', end_date:'2026-04-10', reach:1240, delivery_rate:94, open_rate:68, reply_rate:22, leads_generated:87, conversions:14, created_by:'u-003', created_at:'2026-03-25T09:00:00Z' },
    { campaign_id:'cmp-002', name:'Q2 Product Launch',          type:'email',              status:'completed', segment_name:'SMB Prospects',     start_date:'2026-04-15', end_date:'2026-04-20', reach:450,  delivery_rate:88, open_rate:42, reply_rate:8,  leads_generated:32, conversions:6,  created_by:'u-001', created_at:'2026-04-10T10:00:00Z' },
    { campaign_id:'cmp-003', name:'WhatsApp Re-engagement',     type:'whatsapp_broadcast', status:'active',    segment_name:'Idle Contacts 30d', start_date:'2026-05-01', end_date:'2026-05-31', reach:380,  delivery_rate:91, open_rate:55, reply_rate:18, leads_generated:45, conversions:9,  created_by:'u-002', created_at:'2026-04-28T09:00:00Z' },
    { campaign_id:'cmp-004', name:'Enterprise Demo Invite',     type:'email',              status:'active',    segment_name:'Enterprise Tier',   start_date:'2026-05-10', end_date:'2026-05-25', reach:85,   delivery_rate:97, open_rate:51, reply_rate:12, leads_generated:8,  conversions:2,  created_by:'u-003', created_at:'2026-05-08T11:00:00Z' },
    { campaign_id:'cmp-005', name:'SMS Flash Sale',             type:'sms',                status:'draft',     segment_name:'Karachi Contacts',  start_date:'2026-06-01', end_date:'2026-06-03', reach:0,    delivery_rate:0,  open_rate:0,  reply_rate:0,  leads_generated:0,  conversions:0,  created_by:'u-004', created_at:'2026-05-28T14:00:00Z' },
    { campaign_id:'cmp-006', name:'Ramadan Finance Package',    type:'whatsapp_broadcast', status:'paused',    segment_name:'Finance Leads',     start_date:'2026-03-01', end_date:'2026-03-30', reach:620,  delivery_rate:89, open_rate:61, reply_rate:19, leads_generated:56, conversions:11, created_by:'u-005', created_at:'2026-02-25T09:00:00Z' },
  ];

  const COMMS_KPI = {
    delivery_rate: 91, open_rate: 57, reply_rate: 18, failed_delivery_count: 34,
    low_delivery_channel_count: 0, whatsapp_opted_in: 843, whatsapp_opt_out_rate: 2.1,
  };

  const KNOWLEDGE_ARTICLES = [
    { article_id:'art-001', title:'How to set up WhatsApp integration',   category:'getting_started', status:'published', view_count:342, deflection_count:28, last_updated_at:'2026-04-15T09:00:00Z', author_id:'u-003', stale:false },
    { article_id:'art-002', title:'Invoice creation and payment guide',    category:'billing',         status:'published', view_count:215, deflection_count:19, last_updated_at:'2026-05-01T10:00:00Z', author_id:'u-001', stale:false },
    { article_id:'art-003', title:'Managing user roles and permissions',   category:'how_to',          status:'published', view_count:187, deflection_count:14, last_updated_at:'2026-03-20T11:00:00Z', author_id:'u-003', stale:false },
    { article_id:'art-004', title:'Setting up SLA tiers for support',      category:'technical',       status:'published', view_count:98,  deflection_count:7,  last_updated_at:'2026-01-10T09:00:00Z', author_id:'u-002', stale:true  },
    { article_id:'art-005', title:'CRM lead import via CSV',               category:'getting_started', status:'published', view_count:412, deflection_count:35, last_updated_at:'2026-04-28T14:00:00Z', author_id:'u-001', stale:false },
    { article_id:'art-006', title:'Territory assignment rules explained',  category:'how_to',          status:'draft',     view_count:0,   deflection_count:0,  last_updated_at:'2026-05-25T09:00:00Z', author_id:'u-003', stale:false },
    { article_id:'art-007', title:'API key creation and management',       category:'technical',       status:'published', view_count:56,  deflection_count:4,  last_updated_at:'2025-11-15T09:00:00Z', author_id:'u-002', stale:true  },
    { article_id:'art-008', title:'WhatsApp broadcast best practices',     category:'how_to',          status:'published', view_count:0,   deflection_count:0,  last_updated_at:'2026-05-22T10:00:00Z', author_id:'u-004', stale:false },
  ];

  const KNOWLEDGE_KPI = {
    published_article_count: 6, case_deflection_rate: 23, stale_article_count: 2, zero_view_article_count: 2,
    article_adoption_trend: [
      { month:'Dec', views:120 }, { month:'Jan', views:180 }, { month:'Feb', views:210 },
      { month:'Mar', views:265 }, { month:'Apr', views:310 }, { month:'May', views:342 },
    ],
  };

  const WORKFLOW_EXECUTIONS = [
    { execution_id:'exec-001', workflow_key:'lead_followup_enforcement', workflow_name:'Lead Follow-up Enforcement', status:'succeeded', trigger_event:'lead.idle.v1',                   started_at:'2026-05-29T08:00:00Z', ended_at:'2026-05-29T08:00:05Z', duration_ms:5200,  step_count:3, failed_step:null               },
    { execution_id:'exec-002', workflow_key:'collections_reminder',       workflow_name:'Collections Auto-Reminder',  status:'failed',    trigger_event:'invoice.overdue.v1',             started_at:'2026-05-29T07:30:00Z', ended_at:'2026-05-29T07:30:03Z', duration_ms:3100,  step_count:2, failed_step:'send_whatsapp'    },
    { execution_id:'exec-003', workflow_key:'sla_breach_notify',          workflow_name:'SLA Breach Notification',    status:'succeeded', trigger_event:'case.sla.breached.v1',           started_at:'2026-05-29T07:00:00Z', ended_at:'2026-05-29T07:00:08Z', duration_ms:8200,  step_count:4, failed_step:null               },
    { execution_id:'exec-004', workflow_key:'lead_assignment',            workflow_name:'Lead Territory Assignment',  status:'succeeded', trigger_event:'lead.created.v1',                started_at:'2026-05-29T06:45:00Z', ended_at:'2026-05-29T06:45:04Z', duration_ms:4000,  step_count:2, failed_step:null               },
    { execution_id:'exec-005', workflow_key:'collections_reminder',       workflow_name:'Collections Auto-Reminder',  status:'retrying',  trigger_event:'invoice.overdue.v1',             started_at:'2026-05-28T20:00:00Z', ended_at:null,                   duration_ms:null,  step_count:2, failed_step:'send_whatsapp'    },
    { execution_id:'exec-006', workflow_key:'opportunity_stage_notify',   workflow_name:'Stage Change Notification',  status:'succeeded', trigger_event:'opportunity.stage.changed.v1',   started_at:'2026-05-28T15:30:00Z', ended_at:'2026-05-28T15:30:06Z', duration_ms:6000,  step_count:3, failed_step:null               },
    { execution_id:'exec-007', workflow_key:'lead_followup_enforcement',  workflow_name:'Lead Follow-up Enforcement', status:'failed',    trigger_event:'lead.idle.v1',                   started_at:'2026-05-28T14:00:00Z', ended_at:'2026-05-28T14:00:02Z', duration_ms:2100,  step_count:3, failed_step:'escalate_to_manager' },
    { execution_id:'exec-008', workflow_key:'sla_breach_notify',          workflow_name:'SLA Breach Notification',    status:'running',   trigger_event:'case.sla.breached.v1',           started_at:'2026-05-29T09:00:00Z', ended_at:null,                   duration_ms:null,  step_count:4, failed_step:null               },
  ];

  const WORKFLOW_KPI = {
    failure_count: 2, execution_volume: 8, success_rate: 62, retry_queue_depth: 1, escalation_count: 0,
    execution_trend: [
      { day:'Mon', succeeded:12, failed:2 }, { day:'Tue', succeeded:18, failed:1 },
      { day:'Wed', succeeded:15, failed:3 }, { day:'Thu', succeeded:20, failed:1 }, { day:'Fri', succeeded:8, failed:2 },
    ],
  };

  const MESSAGE_THREADS = [
    { thread_id:'th-001', contact_name:'Tariq Mehmood',   contact_phone:'+923011234567', channel:'whatsapp', last_message_preview:'Sir, order delivery kab hogi?',         last_message_at:'2026-05-29T09:45:00Z', unread_count:2, assigned_agent_id:'u-001', queue_id:'q-001', status:'open',     intent:'payment_query'     },
    { thread_id:'th-002', contact_name:'Nadia Hussain',   contact_phone:'+923219876543', channel:'email',    last_message_preview:'Regarding invoice INV-2026-002...',      last_message_at:'2026-05-29T08:30:00Z', unread_count:0, assigned_agent_id:'u-002', queue_id:'q-002', status:'open',     intent:'follow_up_response'},
    { thread_id:'th-003', contact_name:'Kamran Iqbal',    contact_phone:'+923331122334', channel:'whatsapp', last_message_preview:'Payment kar diya, please confirm',       last_message_at:'2026-05-29T07:15:00Z', unread_count:1, assigned_agent_id:null,    queue_id:'q-001', status:'open',     intent:'payment_query'     },
    { thread_id:'th-004', contact_name:'Zara Ahmed',      contact_phone:'+923451234567', channel:'sms',      last_message_preview:'Please call me regarding proposal',      last_message_at:'2026-05-28T16:00:00Z', unread_count:0, assigned_agent_id:'u-003', queue_id:'q-001', status:'open',     intent:'lead_inquiry'      },
    { thread_id:'th-005', contact_name:'Imran Butt',      contact_phone:'+923001111222', channel:'whatsapp', last_message_preview:'Contract terms mein ek cheez clear...',  last_message_at:'2026-05-28T14:30:00Z', unread_count:3, assigned_agent_id:'u-002', queue_id:'q-001', status:'open',     intent:'lead_inquiry'      },
    { thread_id:'th-006', contact_name:'+923112223344',   contact_phone:'+923112223344', channel:'whatsapp', last_message_preview:'Hello, I want to know about CRM',        last_message_at:'2026-05-28T11:00:00Z', unread_count:1, assigned_agent_id:null,    queue_id:'q-001', status:'open',     intent:'lead_inquiry'      },
    { thread_id:'th-007', contact_name:'Hassan Mirza',    contact_phone:'+923049988776', channel:'email',    last_message_preview:'Following up on our meeting yesterday',  last_message_at:'2026-05-27T15:00:00Z', unread_count:0, assigned_agent_id:'u-004', queue_id:'q-002', status:'resolved', intent:'follow_up_response'},
    { thread_id:'th-008', contact_name:'Ayesha Siddiqui', contact_phone:'+923355566677', channel:'whatsapp', last_message_preview:'Feature request: export to Excel',       last_message_at:'2026-05-27T10:00:00Z', unread_count:0, assigned_agent_id:'u-005', queue_id:'q-003', status:'resolved', intent:'support_request'   },
  ];

  const TERRITORIES = [
    { territory_id:'t-001', name:'Punjab North',     criteria_type:'geographic',   primary_manager:'u-003', assigned_reps:['u-001','u-004'], parent_id:null, routing_priority:1,  is_default:false },
    { territory_id:'t-002', name:'Punjab South',     criteria_type:'geographic',   primary_manager:'u-003', assigned_reps:['u-002'],         parent_id:null, routing_priority:2,  is_default:false },
    { territory_id:'t-003', name:'Sindh',            criteria_type:'geographic',   primary_manager:'u-005', assigned_reps:['u-001','u-002'], parent_id:null, routing_priority:3,  is_default:false },
    { territory_id:'t-004', name:'Rest of Pakistan', criteria_type:'rep_assigned', primary_manager:'u-005', assigned_reps:['u-003','u-005'], parent_id:null, routing_priority:99, is_default:true  },
  ];

  /* --- Envelope wrappers (match API response format exactly) --- */
  return {
    users: {
      data: USERS,
      meta: { count: USERS.length, total: USERS.length, limit: 25, offset: 0 }
    },
    leads: {
      data: LEADS,
      meta: { count: LEADS.length, total: 847, limit: 25, offset: 0 }
    },
    followups: {
      data: FOLLOWUPS,
      meta: { count: FOLLOWUPS.length, total: FOLLOWUPS.length, limit: 25, offset: 0 }
    },
    opportunities: {
      data: OPPORTUNITIES,
      meta: { count: OPPORTUNITIES.length, total: OPPORTUNITIES.length, limit: 25, offset: 0 }
    },
    contacts: {
      data: CONTACTS,
      meta: { count: CONTACTS.length, total: 284, limit: 25, offset: 0 }
    },
    activities: {
      data: ACTIVITIES,
      meta: { count: ACTIVITIES.length, total: ACTIVITIES.length, limit: 25, offset: 0 }
    },
    tasks: {
      data: TASKS,
      meta: { count: TASKS.length, total: TASKS.length, limit: 25, offset: 0 }
    },
    invoiceSummaries: INVOICE_SUMMARIES,
    forecasts: FORECASTS,
    kpiDeltas: KPI_DELTAS,
    kpiSparklines: KPI_SPARKLINES,
    followupTrend: FOLLOWUP_TREND,
    leadsByHour: LEADS_BY_HOUR,
    leadFunnelDeltas: LEAD_FUNNEL_DELTAS,
    collections: {
      data: COLLECTIONS,
      meta: { count: COLLECTIONS.length, total: COLLECTIONS.length, limit: 25, offset: 0 }
    },
    collectionsKpi: COLLECTIONS_KPI,
    contactsKpi: CONTACTS_KPI,
    leadFunnelKpi: LEAD_FUNNEL_KPI,
    aiModelKpi: AI_MODEL_KPI,
    priceBooks: {
      data: PRICE_BOOKS,
      meta: { pagination: { page: 1, page_size: 25, total_items: PRICE_BOOKS.length, total_pages: 1 } }
    },
    quotes: {
      data: QUOTES,
      meta: { count: QUOTES.length, total: QUOTES.length, limit: 25, offset: 0 }
    },
    auditLog: {
      data: AUDIT_LOG,
      meta: { count: AUDIT_LOG.length, total: AUDIT_LOG.length, limit: 25, offset: 0 }
    },
    rbacAssignmentLog: {
      data: RBAC_ASSIGNMENT_LOG,
      meta: { count: RBAC_ASSIGNMENT_LOG.length, total: RBAC_ASSIGNMENT_LOG.length, limit: 25, offset: 0 }
    },
    accounts: {
      data: ACCOUNTS,
      meta: { count: ACCOUNTS.length, total: ACCOUNTS.length, limit: 25, offset: 0 }
    },
    orders: {
      data: ORDERS,
      meta: { count: ORDERS.length, total: ORDERS.length, limit: 25, offset: 0 }
    },
    tenantKpi: TENANT_KPI,
    featureFlags: {
      data: FEATURE_FLAGS,
      meta: { count: FEATURE_FLAGS.length, total: FEATURE_FLAGS.length, limit: 25, offset: 0 }
    },
    roles: {
      data: ROLES,
      meta: { count: ROLES.length, total: ROLES.length, limit: 25, offset: 0 }
    },
    invoices: {
      data: INVOICES,
      meta: { count: INVOICES.length, total: INVOICES.length, limit: 25, offset: 0 }
    },
    subscriptions: {
      data: SUBSCRIPTIONS,
      meta: { count: SUBSCRIPTIONS.length, total: SUBSCRIPTIONS.length, limit: 25, offset: 0 }
    },
    subscriptionKpi: SUBSCRIPTION_KPI,
    AUDIT_LOG: AUDIT_LOG,
    RBAC_ASSIGNMENT_LOG: RBAC_ASSIGNMENT_LOG,
    cases: {
      data: CASES,
      meta: { count: CASES.length, total: CASES.length, limit: 25, offset: 0 }
    },
    caseSlaKpi: CASE_SLA_KPI,
    partners: {
      data: PARTNERS,
      meta: { count: PARTNERS.length, total: PARTNERS.length, limit: 25, offset: 0 }
    },
    campaigns: {
      data: CAMPAIGNS,
      meta: { count: CAMPAIGNS.length, total: CAMPAIGNS.length, limit: 25, offset: 0 }
    },
    commsKpi: COMMS_KPI,
    knowledgeArticles: {
      data: KNOWLEDGE_ARTICLES,
      meta: { count: KNOWLEDGE_ARTICLES.length, total: KNOWLEDGE_ARTICLES.length, limit: 25, offset: 0 }
    },
    knowledgeKpi: KNOWLEDGE_KPI,
    workflowExecutions: {
      data: WORKFLOW_EXECUTIONS,
      meta: { count: WORKFLOW_EXECUTIONS.length, total: WORKFLOW_EXECUTIONS.length, limit: 25, offset: 0 }
    },
    workflowKpi: WORKFLOW_KPI,
    messageThreads: {
      data: MESSAGE_THREADS,
      meta: { count: MESSAGE_THREADS.length, total: MESSAGE_THREADS.length, limit: 25, offset: 0 }
    },
    territories: {
      data: TERRITORIES,
      meta: { count: TERRITORIES.length, total: TERRITORIES.length, limit: 25, offset: 0 }
    },
    /* computed helpers */
    overdueFollowups: FOLLOWUPS.filter(f => f.state === 'overdue'),
    todayLeads: LEADS.filter(l => l.created_at.startsWith('2026-05-05')),
    userMap: USERS.reduce((m, u) => { m[u.id] = u; return m; }, {}),
  };
})();
