from flask import Flask, render_template, request, redirect, url_for, session
import pymysql
import os
import time
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# 数据库配置 - 增加重试逻辑
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'app_user'),
    'password': os.getenv('DB_PASSWORD', 'app_password'),
    'database': os.getenv('DB_NAME', 'vuln_app'),
    'charset': 'utf8mb4',
    'connect_timeout': 30
}


def get_db_connection(max_retries=5, delay=2):
    """获取数据库连接，带有重试机制"""
    for attempt in range(max_retries):
        try:
            conn = pymysql.connect(**db_config)
            logger.info("数据库连接成功")
            return conn
        except pymysql.Error as e:
            logger.warning(f"数据库连接失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                raise e


# 初始化数据库
def init_db():
    max_retries = 10
    for attempt in range(max_retries):
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                # 创建用户表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(50) NOT NULL
                    )
                ''')
                # 创建留言表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                # 插入示例用户
                cursor.execute("INSERT IGNORE INTO users (username, password) VALUES (%s, %s)",
                               ('admin', 'admin123'))
                cursor.execute("INSERT IGNORE INTO users (username, password) VALUES (%s, %s)",
                               ('test', 'test123'))
                conn.commit()
            conn.close()
            logger.info("数据库初始化成功")
            break
        except Exception as e:
            logger.warning(f"数据库初始化失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                logger.error("数据库初始化最终失败")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            # 🚨 存在SQL注入漏洞的代码！
            conn = get_db_connection()
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # 危险：直接拼接SQL字符串
            sql = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

            logger.debug(f"执行的SQL: {sql}")  # 用于调试
            cursor.execute(sql)
            user = cursor.fetchone()
            conn.close()

            if user:
                session['logged_in'] = True
                session['username'] = user['username']
                return redirect(url_for('guestbook'))
            else:
                error = '用户名或密码错误！'
        except Exception as e:
            error = f'数据库错误: {str(e)}'
            logger.error(f"登录错误: {e}")

    return render_template('login.html', error=error)


@app.route('/guestbook', methods=['GET', 'POST'])
def guestbook():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()

        if request.method == 'POST':
            content = request.form['content']
            # 🚨 直接存储用户输入，存在XSS漏洞！
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO messages (content) VALUES (%s)", (content,))
                conn.commit()

        # 获取所有留言
        with conn.cursor() as cursor:
            cursor.execute("SELECT content, created_at FROM messages ORDER BY created_at DESC")
            messages = cursor.fetchall()
        conn.close()

        return render_template('guestbook.html',
                               username=session['username'],
                               messages=messages)
    except Exception as e:
        logger.error(f"留言板错误: {e}")
        return f"数据库错误: {str(e)}", 500


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/health')
def health():
    """健康检查端点"""
    try:
        conn = get_db_connection()
        conn.close()
        return "OK", 200
    except Exception as e:
        return f"Database error: {str(e)}", 500


if __name__ == '__main__':
    # 延迟初始化，等待数据库就绪
    time.sleep(10)
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)