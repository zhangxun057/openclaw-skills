/**
 * Error Hook Tests
 */

const { describe, it, before, after } = require('node:test');
const assert = require('node:assert');

const {
  handleErrorDetection,
  runErrorHook,
  ERROR_REMINDER,
} = require('../../../src/hooks/error-hook');

describe('error-hook', () => {
  describe('handleErrorDetection', () => {
    it('should return reminder when error is detected', () => {
      const result = handleErrorDetection('Command failed with exit code 1');
      assert.ok(typeof result === 'string');
      assert.ok(result.includes('error-detected'));
    });

    it('should return null when no error detected', () => {
      const result = handleErrorDetection('Everything completed successfully');
      assert.strictEqual(result, null);
    });

    it('should detect various error patterns', () => {
      assert.ok(handleErrorDetection('Error: Something went wrong'));
      assert.ok(handleErrorDetection('npm ERR! code ENOENT'));
      assert.ok(handleErrorDetection('Traceback (most recent call last)'));
      assert.ok(handleErrorDetection('Permission denied'));
    });

    it('should handle empty string', () => {
      const result = handleErrorDetection('');
      assert.strictEqual(result, null);
    });

    it('should handle null input', () => {
      const result = handleErrorDetection(null);
      assert.strictEqual(result, null);
    });

    it('should handle undefined input', () => {
      const result = handleErrorDetection(undefined);
      assert.strictEqual(result, null);
    });
  });

  describe('ERROR_REMINDER', () => {
    it('should be a non-empty string', () => {
      assert.ok(typeof ERROR_REMINDER === 'string');
      assert.ok(ERROR_REMINDER.length > 0);
    });

    it('should contain XML-like tags', () => {
      assert.ok(ERROR_REMINDER.includes('<error-detected>'));
      assert.ok(ERROR_REMINDER.includes('</error-detected>'));
    });

    it('should mention ERRORS.md', () => {
      assert.ok(ERROR_REMINDER.includes('ERRORS.md'));
    });

    it('should mention ERR- ID format', () => {
      assert.ok(ERROR_REMINDER.includes('ERR-'));
    });
  });

  describe('runErrorHook', () => {
    let originalOutput;
    let consoleOutput = [];
    const originalLog = console.log;

    before(() => {
      originalOutput = process.env.CLAUDE_TOOL_OUTPUT;
      console.log = (...args) => consoleOutput.push(args.join(' '));
    });

    after(() => {
      process.env.CLAUDE_TOOL_OUTPUT = originalOutput;
      console.log = originalLog;
    });

    it('should output reminder when CLAUDE_TOOL_OUTPUT contains error', () => {
      consoleOutput = [];
      process.env.CLAUDE_TOOL_OUTPUT = 'Command failed with error: exit code 1';
      runErrorHook();
      assert.ok(consoleOutput.length > 0);
      assert.ok(consoleOutput[0].includes('error-detected'));
    });

    it('should not output when CLAUDE_TOOL_OUTPUT is clean', () => {
      consoleOutput = [];
      process.env.CLAUDE_TOOL_OUTPUT = 'Everything completed successfully';
      runErrorHook();
      assert.strictEqual(consoleOutput.length, 0);
    });

    it('should handle empty CLAUDE_TOOL_OUTPUT', () => {
      consoleOutput = [];
      process.env.CLAUDE_TOOL_OUTPUT = '';
      runErrorHook();
      assert.strictEqual(consoleOutput.length, 0);
    });
  });
});
