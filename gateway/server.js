const { app } = require('./app');

const port = Number(process.env.PORT || 8080);

app.listen(port, () => {
  // eslint-disable-next-line no-console
  console.log(`API gateway listening on ${port}`);
});
