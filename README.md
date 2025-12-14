![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green)
![Docker](https://img.shields.io/badge/Docker-✓-blue)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)

### 前提条件
- Docker Desktop
- Git

### 部署步骤
1. 克隆项目
```bash
git clone https://github.com/QuetzalcoatlusFlos/Small-Shooting-Range
cd hello-vuln
```
2. 启动应用
```bash
docker compose up --build
```
3. 访问应用
打开浏览器访问：http://localhost:5001

 默认账号
 
 用户名: admin，密码: admin123

 用户名: test，密码: test123

### 包含的漏洞
1. SQL注入
位置: 登录页面

漏洞描述: 使用字符串拼接构造SQL语句

测试方法:

text
用户名: admin' -- 

密码: 任意

修复方案: 使用参数化查询

2. 存储型XSS

位置: 留言板

漏洞描述: 直接存储和显示用户输入，无过滤

测试方法:

```html
<script>alert('XSS攻击')</script>
```

修复方案: HTML实体编码
### 漏洞详情
SQL注入原理
```python
# 危险代码
sql = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
cursor.execute(sql)
```
 当输入 username = "admin' -- " 时，SQL变为：
 
 SELECT * FROM users WHERE username = 'admin' -- ' AND password = '任意'

XSS原理
```python
# 危险代码（Flask模板）
{{ message[0] | safe }}

# 修复代码
{{ message[0] }}  # Flask默认转义
```
### 技术栈

后端: Python Flask

前端: HTML, CSS, JavaScript

数据库: MySQL 8.0

容器: Docker, Docker Compose

部署: 一键容器化部署
