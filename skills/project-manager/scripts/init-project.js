// 项目初始化脚本
const fs = require('fs');
const path = require('path');

const projectName = process.argv[2];
if (!projectName) {
  console.error('用法: node init-project.js <project-name>');
  process.exit(1);
}

const workspaceRoot = path.join(__dirname, '../../../projects');
const projectRoot = path.join(workspaceRoot, projectName);

// 创建目录结构
const dirs = [
  '',
  'spec',
  'docs',
  'iterations',
  'decisions',
  'src',
  'tests'
];

dirs.forEach(dir => {
  const dirPath = path.join(projectRoot, dir);
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
});

console.log(`✅ 项目目录创建完成: ${projectRoot}`);

// 生成 README.md
const readme = `# ${projectName}

## 一句话描述
{项目简介}

## 当前状态
- 状态：需求设计中
- 版本：v0.0.0
- 最后更新：${new Date().toISOString().split('T')[0]}

## 快速链接
- [产品需求文档](spec/PRD.md)
- [技术设计](spec/technical-design.md)

## 团队
- 产品：张洵
- 开发：丑丑虾

---
_创建：${new Date().toISOString().split('T')[0]}_
`;

fs.writeFileSync(path.join(projectRoot, 'README.md'), readme);
console.log('✅ README.md 已创建');

console.log('\n下一步：');
console.log(`1. 编辑 ${projectName}/README.md`);
console.log(`2. 创建 ${projectName}/spec/PRD.md`);
