/**
 * Activator Hook
 * 
 * Injects self-improvement reminders during agent bootstrap.
 * Fires on UserPromptSubmit to remind about learning capture.
 */

const { getActivatorReminder } = require('../utils/template-renderer');

const REMINDER_CONTENT = getActivatorReminder();

/**
 * Handle the activator hook event
 * @returns {string} Reminder content to inject
 */
function handleActivator() {
  return REMINDER_CONTENT;
}

/**
 * CLI-compatible entry point
 * Outputs the reminder to stdout
 */
function runActivator() {
  console.log(REMINDER_CONTENT);
}

module.exports = {
  handleActivator,
  runActivator,
  REMINDER_CONTENT,
};

// CLI execution
if (require.main === module) {
  runActivator();
}
