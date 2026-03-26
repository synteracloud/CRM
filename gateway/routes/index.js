const express = require('express');
const usersV1Router = require('./v1-users.routes');
const activitiesV1Router = require('./v1-activities.routes');
const tasksV1Router = require('./v1-tasks.routes');
const { respondError } = require('../middleware/response-wrapper');

const router = express.Router();

router.use('/api/v1/users', usersV1Router);
router.use('/api/v1/activities', activitiesV1Router);
router.use('/api/v1/tasks', tasksV1Router);

router.use((req, res) => respondError(res, 'not_found', 'The requested resource was not found.', [], 404));

module.exports = router;
