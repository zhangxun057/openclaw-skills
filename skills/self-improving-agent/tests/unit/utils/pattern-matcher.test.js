/**
 * Pattern Matcher Tests
 */

const { describe, it } = require('node:test');
const assert = require('node:assert');
const {
  DEFAULT_ERROR_PATTERNS,
  containsError,
  getMatchingPatterns,
  createPatternMatcher,
} = require('../../../src/utils/pattern-matcher');

describe('pattern-matcher', () => {
  describe('containsError', () => {
    it('should detect "error:" pattern', () => {
      assert.strictEqual(containsError('Something went error: failed'), true);
    });

    it('should detect "Error:" pattern', () => {
      assert.strictEqual(containsError('Error: Connection refused'), true);
    });

    it('should detect "failed" pattern', () => {
      assert.strictEqual(containsError('Command failed with exit code 1'), true);
    });

    it('should detect "command not found" pattern', () => {
      assert.strictEqual(containsError('bash: command not found: xyz'), true);
    });

    it('should detect "Permission denied" pattern', () => {
      assert.strictEqual(containsError('Permission denied: /root/file'), true);
    });

    it('should detect "fatal:" pattern', () => {
      assert.strictEqual(containsError('fatal: repository not found'), true);
    });

    it('should detect "Traceback" pattern', () => {
      assert.strictEqual(containsError('Traceback (most recent call last):'), true);
    });

    it('should detect "npm ERR!" pattern', () => {
      assert.strictEqual(containsError('npm ERR! code ENOENT'), true);
    });

    it('should detect "ModuleNotFoundError" pattern', () => {
      assert.strictEqual(containsError('ModuleNotFoundError: No module named'), true);
    });

    it('should detect "SyntaxError" pattern', () => {
      assert.strictEqual(containsError('SyntaxError: Unexpected token'), true);
    });

    it('should detect "exit code" pattern', () => {
      assert.strictEqual(containsError('Process exited with exit code 1'), true);
    });

    it('should return false for clean output', () => {
      assert.strictEqual(containsError('Everything completed successfully'), false);
    });

    it('should return false for empty string', () => {
      assert.strictEqual(containsError(''), false);
    });

    it('should return false for null', () => {
      assert.strictEqual(containsError(null), false);
    });

    it('should return false for undefined', () => {
      assert.strictEqual(containsError(undefined), false);
    });

    it('should work with custom patterns', () => {
      const custom = ['CUSTOM_ERROR', 'custom_warning'];
      assert.strictEqual(containsError('Something CUSTOM_ERROR happened', custom), true);
      assert.strictEqual(containsError('Something else', custom), false);
    });
  });

  describe('getMatchingPatterns', () => {
    it('should return all matching patterns', () => {
      const output = 'Error: Something failed and exit code 1';
      const matches = getMatchingPatterns(output);
      assert.ok(matches.includes('Error:'));
      assert.ok(matches.includes('failed'));
      assert.ok(matches.includes('exit code'));
    });

    it('should return empty array for no matches', () => {
      const matches = getMatchingPatterns('All good');
      assert.deepStrictEqual(matches, []);
    });

    it('should return empty array for null', () => {
      assert.deepStrictEqual(getMatchingPatterns(null), []);
    });
  });

  describe('createPatternMatcher', () => {
    it('should create matcher with custom patterns', () => {
      const patterns = ['WARN', 'WARNING'];
      const matcher = createPatternMatcher(patterns);
      
      assert.deepStrictEqual(matcher.patterns, patterns);
      assert.strictEqual(matcher.containsError('WARN: Something'), true);
      assert.strictEqual(matcher.containsError('Error: Something'), false);
    });

    it('should return matching patterns', () => {
      const matcher = createPatternMatcher(['A', 'B', 'C']);
      const matches = matcher.getMatchingPatterns('A and B occurred');
      assert.ok(matches.includes('A'));
      assert.ok(matches.includes('B'));
    });
  });
});
