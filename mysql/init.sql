-- ~/lnmp-docker/mysql/init.sql
-- 此文件会在 MySQL 容器首次启动、数据目录为空时自动执行
CREATE TABLE IF NOT EXISTS visitors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip VARCHAR(45),
    visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
