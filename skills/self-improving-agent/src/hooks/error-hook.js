/**
 * Error Hook
 * 
 * Detects errors in command output and injects reminders.
 * Fires on PostToolUse for Bash to detect command failures.
 */

const { containsError } = require('../utils/pattern-matcher');
const { getErrorReminder } = require('../utils/template-renderer');

const ERROR_REMINDER = getErrorReminder();

/**
 * Check if output contains errors and return reminder if so
 * @param {string} output - Command output to check
 * @returns {string|null} Error reminder if errors detected, null otherwise
 */
function handleErrorDetection(output) {
  if (containsError(output)) {
    return ERROR_REMINDER;
  }
  return null;
}

/**
 * CLI-compatible entry point
 * Reads from CLAUDE_TOOL_OUTPUT env var and outputs reminder if errors detected
 */
function runErrorHook() {
  const output = process.env.CLAUDE_TOOL_OUTPUT || '';
  const reminder = handleErrorDetection(output);
  
  if (reminder) {
    console.log(reminder);
  }
}

module.exports = {
  handleErrorDetection,
  runErrorHook,
  ERROR_REMINDER,
};

// CLI execution
if (require.main === module) {
  runErrorHook();
}
