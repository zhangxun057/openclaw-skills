#!/usr/bin/env node
/**
 * Test Runner
 * 
 * Runs all tests using Node.js built-in test runner.
 */

const { run } = require('node:test');
const path = require('path');

async function main() {
  console.log('🧪 Running Self-Improving Agent Tests\n');
  
  const testFiles = [
    'tests/unit/utils/pattern-matcher.test.js',
    'tests/unit/utils/template-renderer.test.js',
    'tests/unit/services/learning-service.test.js',
    'tests/unit/services/error-service.test.js',
    'tests/unit/services/extraction-service.test.js',
    'tests/integration/hooks.test.js',
  ];
  
  let passed = 0;
  let failed = 0;
  
  for (const file of testFiles) {
    process.stdout.write(`Running ${file}... `);
    
    try {
      const result = await run({ files: [file] });
      let filePassed = 0;
      let fileFailed = 0;
      
      for await (const event of result) {
        if (event.type === 'test:pass') {
          filePassed++;
        } else if (event.type === 'test:fail') {
          fileFailed++;
        }
      }
      
      if (fileFailed === 0) {
        console.log(`✅ (${filePassed} passed)`);
        passed += filePassed;
      } else {
        console.log(`❌ (${filePassed} passed, ${fileFailed} failed)`);
        passed += filePassed;
        failed += fileFailed;
      }
    } catch (error) {
      console.log(`❌ Error: ${error.message}`);
      failed++;
    }
  }
  
  console.log(`\n${'='.repeat(50)}`);
  console.log(`Results: ${passed} passed, ${failed} failed`);
  
  if (failed > 0) {
    process.exit(1);
  }
}

main().catch(err => {
  console.error('Test runner error:', err);
  process.exit(1);
});
