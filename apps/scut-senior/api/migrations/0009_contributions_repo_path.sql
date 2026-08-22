-- 迭代 7 追加：贡献的仓库落点（add file 语义）。
--
-- proposed_repo_path 是“若维护者采纳，文件应加入学科资料下哪个路径”的
-- 确定性提议（来自课程注册表 repository_paths + 标题派生文件名）。
-- 它只是提议：真正写入公共仓库永远由维护者人工执行，应用不自动提交。
ALTER TABLE contributions ADD COLUMN proposed_repo_path TEXT NOT NULL DEFAULT '';
