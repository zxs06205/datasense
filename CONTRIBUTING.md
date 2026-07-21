# 贡献指南

感谢你对 datasense 的关注！欢迎通过以下方式参与贡献。

## 开发流程

1. 在 Issue 中认领任务或创建新的 Issue
2. Fork 本仓库并创建功能分支：`git checkout -b feature/xxx`
3. 完成开发后提交 Pull Request
4. 至少一名其他成员进行 Review
5. Review 通过且 CI 检查通过后合并到 main 分支

## 代码规范

- 使用 Python 3.9+ 语法
- 函数和类需包含 docstring
- 新增功能需添加单元测试
- 运行 `pytest` 确保所有测试通过

## 分支命名

- 功能开发：`feature/<描述>`，如 `feature/add-stats-module`
- Bug 修复：`fix/<描述>`，如 `fix/csv-encoding-error`
- 文档更新：`docs/<描述>`

## 测试

```bash
pip install pytest
pytest tests/ -v
```

## 问题反馈

发现 Bug 或有功能建议，请在 GitHub Issues 中提交。
