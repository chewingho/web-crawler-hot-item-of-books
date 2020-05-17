CREATE ROLE 'developer';

GRANT ALL ON TB_RANKING TO developer;
GRANT ALL ON TB_SUBCATEGORY TO developer;

CREATE USER 'python_user'@'localhost' IDENTIFIED BY 'python123';
SET DEFAULT ROLE developer TO 'python_user'@'localhost';