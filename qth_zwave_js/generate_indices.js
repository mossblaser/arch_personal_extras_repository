const ConfigManager = require("@zwave-js/config").ConfigManager;

async function main() {
  const cm = new ConfigManager();
  await cm.loadDeviceClasses();
  await cm.loadManufacturers();
  await cm.loadDeviceIndex();
  await cm.loadNotifications();
  await cm.loadNamedScales();
  await cm.loadSensorTypes();
  await cm.loadMeters();
  await cm.loadIndicators();
}

main();
