#!/usr/bin/env node
/**
 * Self-Improving Agent CLI
 * 
 * Command-line interface for self-improvement operations.
 * 
 * Usage:
 *   node cli.js learning --title "Title" --category "best_practice" --description "..."
 *   node cli.js error --command "npm test" --error "..." --resolution "..."
 *   node cli.js extract --name "skill-name" [--dry-run]
 *   node cli.js activator
 *   node cli.js error-hook
 */

const learningService = require('./services/learning-service');
const errorService = require('./services/error-service');
const extractionService = require('./services/extraction-service');
const activatorHook = require('./hooks/activator-hook');
const errorHook = require('./hooks/error-hook');

function showUsage() {
  console.log(`
Usage: node cli.js <command> [options]

Commands:
  learning    Capture a learning entry
  error       Log an error entry
  extract     Extract a skill from learning
  activator   Output activator reminder
  error-hook  Run error detection hook

Learning options:
  --title, -t        Learning title (required)
  --category, -c     Category: best_practice, correction, knowledge_gap
  --description, -d  Description (required)
  --solution, -s     Solution/workaround
  --tags             Comma-separated tags

Error options:
  --command, -c      Command that failed (required)
  --error, -e        Error message (required)
  --context          Additional context
  --resolution       How the error was resolved

Extract options:
  --name, -n         Skill name (required)
  --output-dir, -o   Output directory (default: ./skills)
  --dry-run          Show what would be created

Examples:
  node cli.js learning -t "Docker M1 Fix" -c "best_practice" -d "Use platform flag"
  node cli.js error -c "npm install" -e "Module not found" -r "Install with --legacy-peer-deps"
  node cli.js extract -n "docker-m1-fixes"
`);
}

function parseArgs(args) {
  const options = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    const nextArg = args[i + 1];
    
    switch (arg) {
      case '--title':
      case '-t':
        options.title = nextArg;
        i++;
        break;
      case '--category':
      case '-c':
        options.category = nextArg;
        i++;
        break;
      case '--description':
      case '-d':
        options.description = nextArg;
        i++;
        break;
      case '--solution':
      case '-s':
        options.solution = nextArg;
        i++;
        break;
      case '--tags':
        options.tags = nextArg.split(',').map(t => t.trim());
        i++;
        break;
      case '--command':
      case '-cmd':
        options.command = nextArg;
        i++;
        break;
      case '--error':
      case '-e':
        options.error = nextArg;
        i++;
        break;
      case '--context':
        options.context = nextArg;
        i++;
        break;
      case '--resolution':
      case '-r':
        options.resolution = nextArg;
        i++;
        break;
      case '--name':
      case '-n':
        options.name = nextArg;
        i++;
        break;
      case '--output-dir':
      case '-o':
        options.outputDir = nextArg;
        i++;
        break;
      case '--dry-run':
        options.dryRun = true;
        break;
    }
  }
  return options;
}

function handleLearning(args) {
  const options = parseArgs(args);
  
  if (!options.title || !options.description) {
    console.error('Error: --title and --description are required');
    process.exit(1);
  }
  
  const result = learningService.captureLearning({
    title: options.title,
    category: options.category || 'best_practice',
    description: options.description,
    solution: options.solution,
    tags: options.tags || [],
  });
  
  if (result.success) {
    console.log(`Learning captured: ${result.id}`);
    console.log(`File: ${result.file}`);
  } else {
    console.error(`Error: ${result.error}`);
    process.exit(1);
  }
}

function handleError(args) {
  const options = parseArgs(args);
  
  if (!options.command || !options.error) {
    console.error('Error: --command and --error are required');
    process.exit(1);
  }
  
  const result = errorService.logError({
    command: options.command,
    error: options.error,
    context: options.context,
    resolution: options.resolution,
  });
  
  if (result.success) {
    console.log(`Error logged: ${result.id}`);
    console.log(`File: ${result.file}`);
  } else {
    console.error(`Error: ${result.error}`);
    process.exit(1);
  }
}

function handleExtract(args) {
  const options = parseArgs(args);
  
  if (!options.name) {
    console.error('Error: --name is required');
    process.exit(1);
  }
  
  const result = extractionService.extractSkill({
    skillName: options.name,
    outputDir: options.outputDir,
    dryRun: options.dryRun,
  });
  
  if (result.success) {
    if (result.dryRun) {
      console.log('Dry run - would create:');
      console.log(`  ${result.skillPath}/`);
      console.log(`  ${result.skillFile}`);
      console.log('\nContent:');
      console.log(result.content);
    } else {
      console.log(`Skill created: ${result.skillPath}`);
      console.log(`File: ${result.skillFile}`);
    }
  } else {
    console.error(`Error: ${result.error}`);
    process.exit(1);
  }
}

function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (!command || command === '--help' || command === '-h') {
    showUsage();
    process.exit(0);
  }
  
  switch (command) {
    case 'learning':
      handleLearning(args.slice(1));
      break;
    case 'error':
      handleError(args.slice(1));
      break;
    case 'extract':
      handleExtract(args.slice(1));
      break;
    case 'activator':
      activatorHook.runActivator();
      break;
    case 'error-hook':
      errorHook.runErrorHook();
      break;
    default:
      console.error(`Unknown command: ${command}`);
      showUsage();
      process.exit(1);
  }
}

main();
