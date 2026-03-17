#!/usr/bin/env node
/**
 * Skill 安全扫描器
 * 用法: node security-scanner.js <skill-path>
 */

const fs = require('fs');
const path = require('path');

// 风险规则
const RULES = {
  critical: [
    { pattern: /eval\s*\(/g, desc: '任意代码执行: eval()' },
    { pattern: /new\s+Function\s*\(/g, desc: '任意代码执行: new Function()' },
    { pattern: /child_process\.exec\(/g, desc: '命令注入风险: exec()' },
    { pattern: /(rm\s+-rf|Remove-Item\s+-Recurse)/g, desc: '危险删除操作' },
    { pattern: /process\.env\.[A-Z_]+.*fetch|axios|request/gs, desc: '环境变量外泄' },
  ],
  high: [
    { pattern: /sudo\s+/g, desc: '权限提升: sudo' },
    { pattern: /curl.*\|.*bash|wget.*\|.*sh/g, desc: '远程脚本执行' },
    { pattern: /writeFile.*\.openclaw/g, desc: '修改系统配置' },
    { pattern: /fetch\(['"]https?:\/\/(?!github\.com|npmjs\.com)/g, desc: '非白名单域名请求' },
  ],
  medium: [
    { pattern: /while\s*\(\s*true\s*\)/g, desc: '无限循环风险' },
    { pattern: /require\(['"][^'"]*latest['"]\)/g, desc: '未锁定依赖版本' },
  ]
};

function scanFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const issues = [];
  let totalScore = 0;

  // 扫描各级别风险
  for (const [level, rules] of Object.entries(RULES)) {
    const weight = { critical: 10, high: 5, medium: 2 }[level];
    
    for (const rule of rules) {
      const matches = content.match(rule.pattern);
      if (matches) {
        issues.push({
          level,
          desc: rule.desc,
          count: matches.length,
          lines: findLines(content, rule.pattern)
        });
        totalScore += matches.length * weight;
      }
    }
  }

  // 计算风险等级
  let riskLevel = 'safe';
  if (totalScore >= 20) riskLevel = 'critical';
  else if (totalScore >= 10) riskLevel = 'high';
  else if (totalScore >= 5) riskLevel = 'medium';

  return {
    file: path.basename(filePath),
    risk_level: riskLevel,
    score: totalScore,
    issues,
    scanned_at: new Date().toISOString()
  };
}

function findLines(content, pattern) {
  const lines = content.split('\n');
  const matched = [];
  lines.forEach((line, idx) => {
    if (pattern.test(line)) {
      matched.push(idx + 1);
    }
  });
  return matched.slice(0, 3); // 最多返回3行
}

// 主逻辑
const skillPath = process.argv[2];
if (!skillPath) {
  console.error('用法: node security-scanner.js <skill-path>');
  process.exit(1);
}

try {
  const result = scanFile(skillPath);
  console.log(JSON.stringify(result, null, 2));
} catch (err) {
  console.error('扫描失败:', err.message);
  process.exit(1);
}
