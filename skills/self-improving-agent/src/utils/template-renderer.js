/**
 * Template Renderer Utility
 * 
 * Renders learning capture templates and reminders.
 */

const LEARNING_REMINDER_CONTENT = `
## Self-Improvement Reminder

After completing tasks, evaluate if any learnings should be captured:

**Log when:**
- User corrects you → \`.learnings/LEARNINGS.md\`
- Command/operation fails → \`.learnings/ERRORS.md\`
- User wants missing capability → \`.learnings/FEATURE_REQUESTS.md\`
- You discover your knowledge was wrong → \`.learnings/LEARNINGS.md\`
- You find a better approach → \`.learnings/LEARNINGS.md\`

**Promote when pattern is proven:**
- Behavioral patterns → \`SOUL.md\`
- Workflow improvements → \`AGENTS.md\`
- Tool gotchas → \`TOOLS.md\`

Keep entries simple: date, title, what happened, what to do differently.
`.trim();

const ACTIVATOR_REMINDER_CONTENT = `<self-improvement-reminder>
After completing this task, evaluate if extractable knowledge emerged:
- Non-obvious solution discovered through investigation?
- Workaround for unexpected behavior?
- Project-specific pattern learned?
- Error required debugging to resolve?

If yes: Log to .learnings/ using the self-improvement skill format.
If high-value (recurring, broadly applicable): Consider skill extraction.
</self-improvement-reminder>`;

const ERROR_DETECTION_REMINDER = `<error-detected>
A command error was detected. Consider logging this to .learnings/ERRORS.md if:
- The error was unexpected or non-obvious
- It required investigation to resolve
- It might recur in similar contexts
- The solution could benefit future sessions

Use the self-improvement skill format: [ERR-YYYYMMDD-XXX]
</error-detected>`;

/**
 * Get the learning reminder content
 * @returns {string} Formatted reminder content
 */
function getLearningReminder() {
  return LEARNING_REMINDER_CONTENT;
}

/**
 * Get the activator hook reminder
 * @returns {string} Formatted activator reminder
 */
function getActivatorReminder() {
  return ACTIVATOR_REMINDER_CONTENT;
}

/**
 * Get the error detection reminder
 * @returns {string} Formatted error reminder
 */
function getErrorReminder() {
  return ERROR_DETECTION_REMINDER;
}

/**
 * Render a learning entry template
 * @param {Object} learning - Learning entry data
 * @returns {string} Formatted learning entry
 */
function renderLearningEntry(learning) {
  const { id, date, title, category, description, solution, tags = [] } = learning;
  
  let entry = `### ${id}\n\n`;
  entry += `**Date:** ${date}\n\n`;
  entry += `**Category:** ${category}\n\n`;
  entry += `**Title:** ${title}\n\n`;
  
  if (tags.length > 0) {
    entry += `**Tags:** ${tags.join(', ')}\n\n`;
  }
  
  entry += `**Description:**\n${description}\n\n`;
  
  if (solution) {
    entry += `**Solution:**\n${solution}\n\n`;
  }
  
  entry += `---\n`;
  
  return entry;
}

/**
 * Render an error entry template
 * @param {Object} error - Error entry data
 * @returns {string} Formatted error entry
 */
function renderErrorEntry(error) {
  const { id, date, command, error: errorMsg, context, resolution } = error;
  
  let entry = `### ${id}\n\n`;
  entry += `**Date:** ${date}\n\n`;
  entry += `**Command:** \`\`\`\n${command}\n\`\`\`\n\n`;
  entry += `**Error:**\n${errorMsg}\n\n`;
  
  if (context) {
    entry += `**Context:** ${context}\n\n`;
  }
  
  if (resolution) {
    entry += `**Resolution:**\n${resolution}\n\n`;
  }
  
  entry += `---\n`;
  
  return entry;
}

module.exports = {
  getLearningReminder,
  getActivatorReminder,
  getErrorReminder,
  renderLearningEntry,
  renderErrorEntry,
};
