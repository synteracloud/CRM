const { app } = require('./app');
const { buildRuntimeConfig } = require('./config/runtime-config');

const runtimeConfig = buildRuntimeConfig();
const port = runtimeConfig.service.port;

app.listen(port, () => {
  // eslint-disable-next-line no-console
  console.log(`API gateway listening on ${port} (${runtimeConfig.service.name}@${runtimeConfig.service.version})`);
});
