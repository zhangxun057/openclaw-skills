/**
 * Error Service
 * 
 * Handles error detection and error logging logic.
 */

const fs = require('fs');
const path = require('path');
const { containsError } = require('../utils/pattern-matcher');
const { renderErrorEntry } = require('../utils/template-renderer');

const DEFAULT_LEARNINGS_DIR = '.learnings';
const ERRORS_FILE = 'ERRORS.md';

/**
 * Generate an error ID
 * @param {Date} date - Date for the ID (defaults to now)
 * @param {number} sequence - Sequence number
 * @returns {string} Error ID in format ERR-YYYYMMDD-XXX
 */
function generateErrorId(date = new Date(), sequence = 1) {
  const dateStr = date.toISOString().slice(0, 10).replace(/-/g, '');
  const seqStr = sequence.toString().padStart(3, '0');
  return `ERR-${dateStr}-${seqStr}`;
}

/**
 * Ensure the errors file exists
 * @param {string} baseDir - Base directory
 * @returns {string} Path to errors file
 */
function ensureErrorsFile(baseDir = process.cwd()) {
  const learningsDir = path.join(baseDir, DEFAULT_LEARNINGS_DIR);
  if (!fs.existsSync(learningsDir)) {
    fs.mkdirSync(learningsDir, { recursive: true });
  }
  return path.join(learningsDir, ERRORS_FILE);
}

/**
 * Get the next sequence number for error IDs
 * @param {string} errorsFile - Path to errors file
 * @returns {number} Next sequence number
 */
function getNextErrorSequence(errorsFile) {
  if (!fs.existsSync(errorsFile)) {
    return 1;
  }
  
  const content = fs.readFileSync(errorsFile, 'utf8');
  const matches = content.match(/### ERR-\d{8}-(\d{3})/g);
  
  if (!matches || matches.length === 0) {
    return 1;
  }
  
  const numbers = matches.map(m => {
    const match = m.match(/ERR-\d{8}-(\d{3})/);
    return match ? parseInt(match[1], 10) : 0;
  });
  
  return Math.max(...numbers) + 1;
}

/**
 * Detect if output contains errors
 * @param {string} output - Command output to check
 * @returns {boolean} True if errors detected
 */
function detectErrors(output) {
  return containsError(output);
}

/**
 * Log an error entry
 * @param {Object} error - Error data
 * @param {string} baseDir - Base directory
 * @returns {Object} Result with success status and error ID
 */
function logError(error, baseDir = process.cwd()) {
  try {
    const errorsFile = ensureErrorsFile(baseDir);
    const sequence = getNextErrorSequence(errorsFile);
    const errorId = generateErrorId(new Date(), sequence);
    
    const entry = renderErrorEntry({
      ...error,
      id: errorId,
      date: new Date().toISOString().slice(0, 10),
    });
    
    fs.appendFileSync(errorsFile, entry + '\n');
    
    return {
      success: true,
      id: errorId,
      file: errorsFile,
    };
  } catch (err) {
    return {
      success: false,
      error: err.message,
    };
  }
}

/**
 * Read all logged errors
 * @param {string} baseDir - Base directory
 * @returns {Array} Array of error entries
 */
function readErrors(baseDir = process.cwd()) {
  const errorsFile = path.join(baseDir, DEFAULT_LEARNINGS_DIR, ERRORS_FILE);
  
  if (!fs.existsSync(errorsFile)) {
    return [];
  }
  
  const content = fs.readFileSync(errorsFile, 'utf8');
  const entries = content.split('---').filter(e => e.trim());
  
  return entries.map(entry => ({
    raw: entry.trim(),
  }));
}

module.exports = {
  generateErrorId,
  ensureErrorsFile,
  getNextErrorSequence,
  detectErrors,
  logError,
  readErrors,
  DEFAULT_LEARNINGS_DIR,
  ERRORS_FILE,
};
