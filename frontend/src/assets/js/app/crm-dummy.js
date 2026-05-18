/* Pakistan CRM — Dummy Data (single source of truth for all pages) */
/* All data mirrors the exact API response envelope: { data: [...], meta: { count, total, limit, offset } } */

window.CRM_DUMMY = (function () {
  'use strict';

  const USERS = [
    { user_id: 'u-001', display_name: 'Ahmed Raza',       email: 'ahmed.raza@crm.pk',    role: 'sales_rep',     avatar: 'avatar1' },
    { user_id: 'u-002', display_name: 'Sana Malik',       email: 'sana.malik@crm.pk',    role: 'sales_rep',     avatar: 'avatar2' },
    { user_id: 'u-003', display_name: 'Bilal Khan',       email: 'bilal.khan@crm.pk',    role: 'sales_manager', avatar: 'avatar3' },
    { user_id: 'u-004', display_name: 'Fatima Sheikh',    email: 'fatima.sheikh@crm.pk', role: 'sales_rep',     avatar: 'avatar4' },
    { user_id: 'u-005', display_name: 'Usman Farooq',     email: 'usman.farooq@crm.pk',  role: 'sales_manager', avatar: 'avatar5' },
  ];

  const LEADS = [
    { lead_id:'l-001', contact_name:'Tariq Mehmood',    contact_phone_e164:'+923011234567', contact_email:'tariq.mehmood@example.com',    stage:'new',          source:'whatsapp',  owner_id:'u-001', priority:'high',   estimated_value:150000, currency:'PKR', created_at:'2026-05-04T08:00:00Z', updated_at:'2026-05-04T09:00:00Z' },
    { lead_id:'l-002', contact_name:'Nadia Hussain',    contact_phone_e164:'+923219876543', contact_email:'nadia.hussain@example.com',    stage:'contacted',    source:'web',       owner_id:'u-002', priority:'medium', estimated_value:85000,  currency:'PKR', created_at:'2026-05-03T10:30:00Z', updated_at:'2026-05-04T07:00:00Z' },
    { lead_id:'l-003', contact_name:'Kamran Iqbal',     contact_phone_e164:'+923331122334', contact_email:'kamran.iqbal@example.com',     stage:'qualified',    source:'referral',  owner_id:'u-001', priority:'urgent', estimated_value:320000, currency:'PKR', created_at:'2026-05-02T09:15:00Z', updated_at:'2026-05-04T11:00:00Z' },
    { lead_id:'l-004', contact_name:'Zara Ahmed',       contact_phone_e164:'+923451234567', contact_email:'zara.ahmed@example.com',       stage:'proposal',     source:'cold_call', owner_id:'u-003', priority:'high',   estimated_value:200000, currency:'PKR', created_at:'2026-04-30T14:00:00Z', updated_at:'2026-05-03T16:00:00Z' },
    { lead_id:'l-005', contact_name:'Imran Butt',       contact_phone_e164:'+923001111222', contact_email:'imran.butt@example.com',       stage:'negotiation',  source:'event',     owner_id:'u-002', priority:'high',   estimated_value:500000, currency:'PKR', created_at:'2026-04-28T11:00:00Z', updated_at:'2026-05-02T10:00:00Z' },
    { lead_id:'l-006', contact_name:'Rabia Chaudhry',   contact_phone_e164:'+923123334455', contact_email:'rabia.chaudhry@example.com',   stage:'closed_won',   source:'web',       owner_id:'u-004', priority:'medium', estimated_value:95000,  currency:'PKR', created_at:'2026-04-25T09:00:00Z', updated_at:'2026-05-01T13:00:00Z' },
    { lead_id:'l-007', contact_name:'Hassan Mirza',     contact_phone_e164:'+923049988776', contact_email:'hassan.mirza@example.com',     stage:'closed_lost',  source:'import',    owner_id:'u-005', priority:'low',    estimated_value:60000,  currency:'PKR', created_at:'2026-04-20T08:30:00Z', updated_at:'2026-04-29T09:00:00Z' },
    { lead_id:'l-008', contact_name:'Ayesha Siddiqui',  contact_phone_e164:'+923355566677', contact_email:'ayesha.siddiqui@example.com',  stage:'new',          source:'whatsapp',  owner_id:'u-001', priority:'urgent', estimated_value:275000, currency:'PKR', created_at:'2026-05-05T06:00:00Z', updated_at:'2026-05-05T06:00:00Z' },
    { lead_id:'l-009', contact_name:'Faisal Mahmood',   contact_phone_e164:'+923217788990', contact_email:'faisal.mahmood@example.com',   stage:'contacted',    source:'web',       owner_id:'u-002', priority:'medium', estimated_value:120000, currency:'PKR', created_at:'2026-05-01T13:00:00Z', updated_at:'2026-05-03T09:00:00Z' },
    { lead_id:'l-010', contact_name:'Sobia Nawaz',      contact_phone_e164:'+923001239876', contact_email:'sobia.nawaz@example.com',      stage:'qualified',    source:'referral',  owner_id:'u-003', priority:'high',   estimated_value:180000, currency:'PKR', created_at:'2026-04-29T15:00:00Z', updated_at:'2026-05-04T14:00:00Z' },
    { lead_id:'l-011', contact_name:'Ali Hassan',       contact_phone_e164:'+923451239876', contact_email:'ali.hassan@example.com',       stage:'proposal',     source:'whatsapp',  owner_id:'u-004', priority:'high',   estimated_value:420000, currency:'PKR', created_at:'2026-04-27T10:00:00Z', updated_at:'2026-05-02T11:00:00Z' },
    { lead_id:'l-012', contact_name:'Mariam Zaidi',     contact_phone_e164:'+923331239876', contact_email:'mariam.zaidi@example.com',     stage:'negotiation',  source:'cold_call', owner_id:'u-001', priority:'urgent', estimated_value:650000, currency:'PKR', created_at:'2026-04-24T09:00:00Z', updated_at:'2026-05-01T16:00:00Z' },
    { lead_id:'l-013', contact_name:'Omar Farhan',      contact_phone_e164:'+923219876001', contact_email:'omar.farhan@example.com',      stage:'new',          source:'web',       owner_id:'u-002', priority:'medium', estimated_value:75000,  currency:'PKR', created_at:'2026-05-05T07:30:00Z', updated_at:'2026-05-05T07:30:00Z' },
    { lead_id:'l-014', contact_name:'Hina Baig',        contact_phone_e164:'+923012345001', contact_email:'hina.baig@example.com',        stage:'contacted',    source:'event',     owner_id:'u-005', priority:'low',    estimated_value:50000,  currency:'PKR', created_at:'2026-05-03T12:00:00Z', updated_at:'2026-05-04T10:00:00Z' },
    { lead_id:'l-015', contact_name:'Saad Qureshi',     contact_phone_e164:'+923459876001', contact_email:'saad.qureshi@example.com',     stage:'qualified',    source:'web',       owner_id:'u-003', priority:'high',   estimated_value:300000, currency:'PKR', created_at:'2026-04-26T11:00:00Z', updated_at:'2026-05-03T13:00:00Z' },
    { lead_id:'l-016', contact_name:'Asma Riaz',        contact_phone_e164:'+923211112223', contact_email:'asma.riaz@example.com',        stage:'new',          source:'whatsapp',  owner_id:'u-001', priority:'medium', estimated_value:90000,  currency:'PKR', created_at:'2026-05-04T16:00:00Z', updated_at:'2026-05-04T16:00:00Z' },
    { lead_id:'l-017', contact_name:'Waqar Ijaz',       contact_phone_e164:'+923334445556', contact_email:'waqar.ijaz@example.com',       stage:'proposal',     source:'referral',  owner_id:'u-004', priority:'urgent', estimated_value:750000, currency:'PKR', created_at:'2026-04-22T09:00:00Z', updated_at:'2026-04-30T14:00:00Z' },
    { lead_id:'l-018', contact_name:'Naila Shafiq',     contact_phone_e164:'+923001112221', contact_email:'naila.shafiq@example.com',     stage:'contacted',    source:'web',       owner_id:'u-002', priority:'low',    estimated_value:45000,  currency:'PKR', created_at:'2026-05-02T08:00:00Z', updated_at:'2026-05-04T09:30:00Z' },
    { lead_id:'l-019', contact_name:'Adeel Aslam',      contact_phone_e164:'+923218887776', contact_email:'adeel.aslam@example.com',      stage:'closed_won',   source:'cold_call', owner_id:'u-005', priority:'medium', estimated_value:135000, currency:'PKR', created_at:'2026-04-15T10:00:00Z', updated_at:'2026-04-28T11:00:00Z' },
    { lead_id:'l-020', contact_name:'Kiran Shahid',     contact_phone_e164:'+923451118889', contact_email:'kiran.shahid@example.com',     stage:'new',          source:'import',    owner_id:'u-003', priority:'medium', estimated_value:110000, currency:'PKR', created_at:'2026-05-05T09:00:00Z', updated_at:'2026-05-05T09:00:00Z' },
  ];

  const FOLLOWUPS = [
    { followup_id:'f-001', lead_id:'l-001', lead_name:'Tariq Mehmood',   state:'overdue',   escalation_level:'strict', due_at:'2026-05-01T10:00:00Z', owner_id:'u-001', owner_name:'Ahmed Raza',    rule_type:'first_contact' },
    { followup_id:'f-002', lead_id:'l-002', lead_name:'Nadia Hussain',   state:'overdue',   escalation_level:'strict', due_at:'2026-04-30T14:00:00Z', owner_id:'u-002', owner_name:'Sana Malik',    rule_type:'idle_lead' },
    { followup_id:'f-003', lead_id:'l-009', lead_name:'Faisal Mahmood',  state:'overdue',   escalation_level:'strict', due_at:'2026-05-02T09:00:00Z', owner_id:'u-002', owner_name:'Sana Malik',    rule_type:'stage_stall' },
    { followup_id:'f-004', lead_id:'l-003', lead_name:'Kamran Iqbal',    state:'overdue',   escalation_level:'medium', due_at:'2026-05-03T11:00:00Z', owner_id:'u-001', owner_name:'Ahmed Raza',    rule_type:'idle_lead' },
    { followup_id:'f-005', lead_id:'l-014', lead_name:'Hina Baig',       state:'overdue',   escalation_level:'medium', due_at:'2026-05-04T08:00:00Z', owner_id:'u-005', owner_name:'Usman Farooq',  rule_type:'first_contact' },
    { followup_id:'f-006', lead_id:'l-018', lead_name:'Naila Shafiq',    state:'overdue',   escalation_level:'medium', due_at:'2026-05-04T12:00:00Z', owner_id:'u-002', owner_name:'Sana Malik',    rule_type:'stage_stall' },
    { followup_id:'f-007', lead_id:'l-004', lead_name:'Zara Ahmed',      state:'pending',   escalation_level:'soft',   due_at:'2026-05-06T10:00:00Z', owner_id:'u-003', owner_name:'Bilal Khan',    rule_type:'proposal_followup' },
    { followup_id:'f-008', lead_id:'l-005', lead_name:'Imran Butt',      state:'pending',   escalation_level:'soft',   due_at:'2026-05-07T14:00:00Z', owner_id:'u-002', owner_name:'Sana Malik',    rule_type:'negotiation_check' },
    { followup_id:'f-009', lead_id:'l-010', lead_name:'Sobia Nawaz',     state:'pending',   escalation_level:'soft',   due_at:'2026-05-08T09:00:00Z', owner_id:'u-003', owner_name:'Bilal Khan',    rule_type:'idle_lead' },
    { followup_id:'f-010', lead_id:'l-011', lead_name:'Ali Hassan',      state:'pending',   escalation_level:'medium', due_at:'2026-05-05T16:00:00Z', owner_id:'u-004', owner_name:'Fatima Sheikh', rule_type:'proposal_followup' },
    { followup_id:'f-011', lead_id:'l-006', lead_name:'Rabia Chaudhry',  state:'completed', escalation_level:'soft',   due_at:'2026-05-01T10:00:00Z', owner_id:'u-004', owner_name:'Fatima Sheikh', rule_type:'first_contact' },
    { followup_id:'f-012', lead_id:'l-019', lead_name:'Adeel Aslam',     state:'completed', escalation_level:'soft',   due_at:'2026-04-27T09:00:00Z', owner_id:'u-005', owner_name:'Usman Farooq',  rule_type:'stage_stall' },
    { followup_id:'f-013', lead_id:'l-013', lead_name:'Omar Farhan',     state:'pending',   escalation_level:'soft',   due_at:'2026-05-09T11:00:00Z', owner_id:'u-002', owner_name:'Sana Malik',    rule_type:'first_contact' },
    { followup_id:'f-014', lead_id:'l-015', lead_name:'Saad Qureshi',    state:'pending',   escalation_level:'soft',   due_at:'2026-05-10T10:00:00Z', owner_id:'u-003', owner_name:'Bilal Khan',    rule_type:'idle_lead' },
    { followup_id:'f-015', lead_id:'l-017', lead_name:'Waqar Ijaz',      state:'overdue',   escalation_level:'strict', due_at:'2026-05-03T09:00:00Z', owner_id:'u-004', owner_name:'Fatima Sheikh', rule_type:'proposal_followup' },
  ];

  const OPPORTUNITIES = [
    { opp_id:'o-001', name:'Al-Noor Textile ERP',      account_id:'a-001', account_name:'Al-Noor Textile',      stage:'proposal',     amount:850000,  currency:'PKR', forecast_category:'best_case', close_date:'2026-06-30', owner_id:'u-003', probability:65 },
    { opp_id:'o-002', name:'City Pharma CRM Rollout',  account_id:'a-002', account_name:'City Pharma Ltd',      stage:'negotiation',  amount:1200000, currency:'PKR', forecast_category:'commit',    close_date:'2026-05-31', owner_id:'u-001', probability:80 },
    { opp_id:'o-003', name:'FastLog Logistics Portal', account_id:'a-003', account_name:'FastLog Pvt Ltd',      stage:'qualification',amount:320000,  currency:'PKR', forecast_category:'pipeline',  close_date:'2026-07-15', owner_id:'u-002', probability:30 },
    { opp_id:'o-004', name:'Sunrise Builders Suite',   account_id:'a-004', account_name:'Sunrise Builders',     stage:'closed_won',   amount:950000,  currency:'PKR', forecast_category:'closed',    close_date:'2026-04-30', owner_id:'u-004', probability:100 },
    { opp_id:'o-005', name:'KPK Agri Connect',         account_id:'a-005', account_name:'KPK Agri Traders',     stage:'discovery',    amount:450000,  currency:'PKR', forecast_category:'pipeline',  close_date:'2026-08-01', owner_id:'u-005', probability:40 },
    { opp_id:'o-006', name:'Metro Retail POS',         account_id:'a-006', account_name:'Metro Retail Group',   stage:'proposal',     amount:680000,  currency:'PKR', forecast_category:'best_case', close_date:'2026-06-15', owner_id:'u-001', probability:60 },
    { opp_id:'o-007', name:'Pak Steel HR Module',      account_id:'a-007', account_name:'Pak Steel Works',      stage:'negotiation',  amount:2100000, currency:'PKR', forecast_category:'commit',    close_date:'2026-05-20', owner_id:'u-003', probability:85 },
    { opp_id:'o-008', name:'Horizon Real Estate CRM',  account_id:'a-008', account_name:'Horizon Properties',   stage:'closed_lost',  amount:550000,  currency:'PKR', forecast_category:'omitted',   close_date:'2026-04-15', owner_id:'u-002', probability:0  },
    { opp_id:'o-009', name:'Iqbal Foods ERP Upgrade',  account_id:'a-009', account_name:'Iqbal Foods Ltd',      stage:'qualification',amount:390000,  currency:'PKR', forecast_category:'pipeline',  close_date:'2026-09-01', owner_id:'u-004', probability:25 },
    { opp_id:'o-010', name:'Pakistan TeleCo Support',  account_id:'a-010', account_name:'PK Telecom Services',  stage:'proposal',     amount:1450000, currency:'PKR', forecast_category:'best_case', close_date:'2026-07-01', owner_id:'u-005', probability:55 },
    { opp_id:'o-011', name:'Lahore Hospital Suite',    account_id:'a-011', account_name:'Lahore Gen Hospital',  stage:'discovery',    amount:870000,  currency:'PKR', forecast_category:'pipeline',  close_date:'2026-08-15', owner_id:'u-001', probability:35 },
    { opp_id:'o-012', name:'ZK Motors Inventory',      account_id:'a-012', account_name:'ZK Motors Ltd',        stage:'negotiation',  amount:780000,  currency:'PKR', forecast_category:'commit',    close_date:'2026-05-28', owner_id:'u-002', probability:75 },
  ];

  const CONTACTS = [
    { contact_id:'c-001', display_name:'Tariq Mehmood',  phone_e164:'+923011234567', email:'tariq@example.com',  account_id:'a-001', account_name:'Al-Noor Textile',    completeness_score:85, created_at:'2026-04-01T09:00:00Z' },
    { contact_id:'c-002', display_name:'Nadia Hussain',  phone_e164:'+923219876543', email:'nadia@example.com',  account_id:'a-002', account_name:'City Pharma Ltd',    completeness_score:72, created_at:'2026-04-05T10:00:00Z' },
    { contact_id:'c-003', display_name:'Kamran Iqbal',   phone_e164:'+923331122334', email:'kamran@example.com', account_id:'a-003', account_name:'FastLog Pvt Ltd',    completeness_score:91, created_at:'2026-03-28T11:00:00Z' },
    { contact_id:'c-004', display_name:'Zara Ahmed',     phone_e164:'+923451234567', email:'zara@example.com',   account_id:'a-004', account_name:'Sunrise Builders',   completeness_score:68, created_at:'2026-04-10T08:00:00Z' },
    { contact_id:'c-005', display_name:'Imran Butt',     phone_e164:'+923001111222', email:'imran@example.com',  account_id:'a-005', account_name:'KPK Agri Traders',   completeness_score:55, created_at:'2026-04-12T14:00:00Z' },
    { contact_id:'c-006', display_name:'Rabia Chaudhry', phone_e164:'+923123334455', email:'rabia@example.com',  account_id:'a-006', account_name:'Metro Retail Group', completeness_score:79, created_at:'2026-04-08T10:00:00Z' },
    { contact_id:'c-007', display_name:'Hassan Mirza',   phone_e164:'+923049988776', email:'hassan@example.com', account_id:'a-007', account_name:'Pak Steel Works',    completeness_score:88, created_at:'2026-03-20T09:00:00Z' },
    { contact_id:'c-008', display_name:'Ayesha Siddiqui',phone_e164:'+923355566677', email:'ayesha@example.com', account_id:'a-008', account_name:'Horizon Properties', completeness_score:62, created_at:'2026-04-18T11:00:00Z' },
    { contact_id:'c-009', display_name:'Faisal Mahmood', phone_e164:'+923217788990', email:'faisal@example.com', account_id:'a-009', account_name:'Iqbal Foods Ltd',    completeness_score:74, created_at:'2026-04-02T13:00:00Z' },
    { contact_id:'c-010', display_name:'Sobia Nawaz',    phone_e164:'+923001239876', email:'sobia@example.com',  account_id:'a-010', account_name:'PK Telecom Services',completeness_score:81, created_at:'2026-03-25T10:00:00Z' },
    { contact_id:'c-011', display_name:'Ali Hassan',     phone_e164:'+923451239876', email:'ali@example.com',    account_id:'a-011', account_name:'Lahore Gen Hospital', completeness_score:93, created_at:'2026-03-15T09:00:00Z' },
    { contact_id:'c-012', display_name:'Mariam Zaidi',   phone_e164:'+923331239876', email:'mariam@example.com', account_id:'a-012', account_name:'ZK Motors Ltd',      completeness_score:70, created_at:'2026-04-14T08:30:00Z' },
    { contact_id:'c-013', display_name:'Omar Farhan',    phone_e164:'+923219876001', email:'omar@example.com',   account_id:'a-001', account_name:'Al-Noor Textile',    completeness_score:58, created_at:'2026-04-20T11:00:00Z' },
    { contact_id:'c-014', display_name:'Hina Baig',      phone_e164:'+923012345001', email:'hina@example.com',   account_id:'a-003', account_name:'FastLog Pvt Ltd',    completeness_score:83, created_at:'2026-04-22T09:00:00Z' },
    { contact_id:'c-015', display_name:'Saad Qureshi',   phone_e164:'+923459876001', email:'saad@example.com',   account_id:'a-005', account_name:'KPK Agri Traders',   completeness_score:76, created_at:'2026-04-25T10:00:00Z' },
  ];

  const ACTIVITIES = [
    { activity_id:'act-001', activity_type:'call',       description:'Introductory call with Tariq re: ERP needs',     entity_type:'lead', entity_id:'l-001', performed_by:'u-001', occurred_at:'2026-05-04T09:30:00Z' },
    { activity_id:'act-002', activity_type:'email',      description:'Sent product brochure to Nadia',                 entity_type:'lead', entity_id:'l-002', performed_by:'u-002', occurred_at:'2026-05-04T08:00:00Z' },
    { activity_id:'act-003', activity_type:'whatsapp',   description:'WhatsApp message from Kamran re: proposal',      entity_type:'lead', entity_id:'l-003', performed_by:'u-001', occurred_at:'2026-05-03T17:00:00Z' },
    { activity_id:'act-004', activity_type:'meeting',    description:'In-person meeting at Sunrise Builders office',   entity_type:'lead', entity_id:'l-004', performed_by:'u-003', occurred_at:'2026-05-03T14:00:00Z' },
    { activity_id:'act-005', activity_type:'note',       description:'Updated lead value estimate after site visit',   entity_type:'lead', entity_id:'l-005', performed_by:'u-002', occurred_at:'2026-05-03T11:00:00Z' },
    { activity_id:'act-006', activity_type:'stage_change',description:'Lead moved from contacted to qualified',        entity_type:'lead', entity_id:'l-003', performed_by:'u-001', occurred_at:'2026-05-02T10:30:00Z' },
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
    { activity_id:'act-017', activity_type:'call',       description:'Cold call connected — Waqar Ijaz interested',   entity_type:'lead', entity_id:'l-017', performed_by:'u-004', occurred_at:'2026-04-22T10:00:00Z' },
    { activity_id:'act-018', activity_type:'note',       description:'Demo scheduled for ZK Motors next week',        entity_type:'opportunity', entity_id:'o-012', performed_by:'u-002', occurred_at:'2026-05-04T13:00:00Z' },
    { activity_id:'act-019', activity_type:'deal_won',   description:'Adeel Aslam — Deal Closed Won PKR 1,35,000',   entity_type:'lead', entity_id:'l-019', performed_by:'u-005', occurred_at:'2026-04-28T11:30:00Z' },
    { activity_id:'act-020', activity_type:'email',      description:'Welcome email sent to new contact Kiran Shahid',entity_type:'lead', entity_id:'l-020', performed_by:'u-003', occurred_at:'2026-05-05T09:15:00Z' },
  ];

  const TASKS = [
    { task_id:'t-001', title:'Send pricing sheet to Kamran',    status:'open',        due_at:'2026-05-06T12:00:00Z', owner_id:'u-001', entity_type:'lead',        entity_id:'l-003', priority:'high'   },
    { task_id:'t-002', title:'Prepare Pak Steel proposal v2',   status:'in_progress', due_at:'2026-05-07T17:00:00Z', owner_id:'u-003', entity_type:'opportunity', entity_id:'o-007', priority:'urgent' },
    { task_id:'t-003', title:'Follow up with City Pharma CFO',  status:'open',        due_at:'2026-05-05T15:00:00Z', owner_id:'u-001', entity_type:'opportunity', entity_id:'o-002', priority:'high'   },
    { task_id:'t-004', title:'Demo walkthrough for Metro Retail',status:'open',        due_at:'2026-05-08T10:00:00Z', owner_id:'u-001', entity_type:'opportunity', entity_id:'o-006', priority:'medium' },
    { task_id:'t-005', title:'Collect signed NDA from Sunrise', status:'completed',   due_at:'2026-04-30T12:00:00Z', owner_id:'u-004', entity_type:'opportunity', entity_id:'o-004', priority:'high'   },
    { task_id:'t-006', title:'Schedule discovery call KPK Agri',status:'open',        due_at:'2026-05-09T11:00:00Z', owner_id:'u-005', entity_type:'opportunity', entity_id:'o-005', priority:'low'    },
    { task_id:'t-007', title:'Update contact info for Hina Baig',status:'open',       due_at:'2026-05-06T09:00:00Z', owner_id:'u-005', entity_type:'contact',     entity_id:'c-014', priority:'low'    },
    { task_id:'t-008', title:'Send contract to ZK Motors',      status:'in_progress', due_at:'2026-05-07T16:00:00Z', owner_id:'u-002', entity_type:'opportunity', entity_id:'o-012', priority:'urgent' },
    { task_id:'t-009', title:'Prepare Q2 forecast report',      status:'open',        due_at:'2026-05-12T17:00:00Z', owner_id:'u-003', entity_type:null,          entity_id:null,    priority:'medium' },
    { task_id:'t-010', title:'Onboarding call with Rabia',      status:'completed',   due_at:'2026-05-01T10:00:00Z', owner_id:'u-004', entity_type:'lead',        entity_id:'l-006', priority:'medium' },
    { task_id:'t-011', title:'Renew support contract — PK Tel', status:'open',        due_at:'2026-05-15T12:00:00Z', owner_id:'u-005', entity_type:'opportunity', entity_id:'o-010', priority:'high'   },
    { task_id:'t-012', title:'WhatsApp broadcast — Eid offer',  status:'open',        due_at:'2026-05-10T09:00:00Z', owner_id:'u-002', entity_type:null,          entity_id:null,    priority:'medium' },
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

  const FORECASTS = {
    current_month: {
      pipeline:   { count: 8,  total_value: 5240000 },
      best_case:  { count: 4,  total_value: 3180000 },
      commit:     { count: 3,  total_value: 4050000 },
      closed:     { count: 2,  total_value: 1045000 },
      weighted_pipeline: 4280000
    }
  };

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
    /* computed helpers */
    overdueFollowups: FOLLOWUPS.filter(f => f.state === 'overdue'),
    todayLeads: LEADS.filter(l => l.created_at.startsWith('2026-05-05')),
    userMap: USERS.reduce((m, u) => { m[u.user_id] = u; return m; }, {}),
  };
})();
