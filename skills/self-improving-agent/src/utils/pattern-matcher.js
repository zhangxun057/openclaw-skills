/**
 * Pattern Matcher Utility
 * 
 * Detects error patterns in command output.
 * Used by error detection hooks and services.
 */

// Default error patterns for detecting command failures
const DEFAULT_ERROR_PATTERNS = [
  'error:',
  'Error:',
  'ERROR:',
  'failed',
  'FAILED',
  'command not found',
  'No such file',
  'Permission denied',
  'fatal:',
  'Exception',
  'Traceback',
  'npm ERR!',
  'ModuleNotFoundError',
  'SyntaxError',
  'TypeError',
  'exit code',
  'non-zero',
];

/**
 * Check if output contains any error patterns
 * @param {string} output - The output to check
 * @param {string[]} patterns - Array of patterns to match (optional)
 * @returns {boolean} True if any pattern is found
 */
function containsError(output, patterns = DEFAULT_ERROR_PATTERNS) {
  if (!output || typeof output !== 'string') {
    return false;
  }
  
  return patterns.some(pattern => output.includes(pattern));
}

/**
 * Get all matching error patterns from output
 * @param {string} output - The output to check
 * @param {string[]} patterns - Array of patterns to match (optional)
 * @returns {string[]} Array of matched patterns
 */
function getMatchingPatterns(output, patterns = DEFAULT_ERROR_PATTERNS) {
  if (!output || typeof output !== 'string') {
    return [];
  }
  
  return patterns.filter(pattern => output.includes(pattern));
}

/**
 * Create a custom pattern matcher with specific patterns
 * @param {string[]} patterns - Patterns to use
 * @returns {Object} Pattern matcher object
 */
function createPatternMatcher(patterns) {
  return {
    patterns,
    containsError: (output) => containsError(output, patterns),
    getMatchingPatterns: (output) => getMatchingPatterns(output, patterns),
  };
}

module.exports = {
  DEFAULT_ERROR_PATTERNS,
  containsError,
  getMatchingPatterns,
  createPatternMatcher,
};
