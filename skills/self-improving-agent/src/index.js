/**
 * Self-Improving Agent - Main Entry Point
 * 
 * Exports all services and utilities for the self-improving agent skill.
 */

const learningService = require('./services/learning-service');
const errorService = require('./services/error-service');
const extractionService = require('./services/extraction-service');
const patternMatcher = require('./utils/pattern-matcher');
const templateRenderer = require('./utils/template-renderer');
const activatorHook = require('./hooks/activator-hook');
const errorHook = require('./hooks/error-hook');

module.exports = {
  // Services
  learning: learningService,
  error: errorService,
  extraction: extractionService,
  
  // Utilities
  patternMatcher,
  templateRenderer,
  
  // Hooks
  hooks: {
    activator: activatorHook,
    error: errorHook,
  },
  
  // Convenience exports
  captureLearning: learningService.captureLearning,
  detectErrors: errorService.detectErrors,
  logError: errorService.logError,
  extractSkill: extractionService.extractSkill,
};
