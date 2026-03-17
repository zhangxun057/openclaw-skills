/**
 * Integration Tests for Hooks
 */

const { describe, it, before, after } = require('node:test');
const assert = require('node:assert');

const activatorHook = require('../../src/hooks/activator-hook');
const errorHook = require('../../src/hooks/error-hook');

describe('hooks integration', () => {
  describe('activator and error hooks', () => {
    it('should have different reminder content', () => {
      const activator = activatorHook.REMINDER_CONTENT;
      const error = errorHook.ERROR_REMINDER;
      
      assert.notStrictEqual(activator, error);
    });

    it('activator should always return content', () => {
      const result = activatorHook.handleActivator();
      assert.ok(result);
      assert.ok(result.includes('self-improvement-reminder'));
    });

    it('error hook should conditionally return content', () => {
      const withError = errorHook.handleErrorDetection('Command failed');
      const withoutError = errorHook.handleErrorDetection('Success');
      
      assert.ok(withError);
      assert.strictEqual(withoutError, null);
    });
  });

  describe('hook exports', () => {
    it('activator hook should export required functions', () => {
      assert.ok(typeof activatorHook.handleActivator === 'function');
      assert.ok(typeof activatorHook.runActivator === 'function');
      assert.ok(typeof activatorHook.REMINDER_CONTENT === 'string');
    });

    it('error hook should export required functions', () => {
      assert.ok(typeof errorHook.handleErrorDetection === 'function');
      assert.ok(typeof errorHook.runErrorHook === 'function');
      assert.ok(typeof errorHook.ERROR_REMINDER === 'string');
    });
  });
});
