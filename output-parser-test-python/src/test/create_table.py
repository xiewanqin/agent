"""
对应 output-parser-test/src/test/create-table.mjs

依赖: pip install pymysql  或 项目已包含 pymysql（见 pyproject.toml）
"""
import pymysql

CONNECTION_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "admin",
    "charset": "utf8mb4",
    "autocommit": True,
}


def main() -> None:
  connection = pymysql.connect(**CONNECTION_CONFIG)

  try:
    with connection.cursor() as cursor:
      cursor.execute(
          "CREATE DATABASE IF NOT EXISTS hello "
          "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
      )
      cursor.execute("USE hello;")

      cursor.execute(
          """
                CREATE TABLE IF NOT EXISTS friends (
                  id INT AUTO_INCREMENT PRIMARY KEY,
                  name VARCHAR(50) NOT NULL,
                  gender VARCHAR(10),
                  birth_date DATE,
                  company VARCHAR(100),
                  title VARCHAR(100),
                  phone VARCHAR(20),
                  wechat VARCHAR(50)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """
      )

      insert_sql = """
                INSERT INTO friends (
                  name,
                  gender,
                  birth_date,
                  company,
                  title,
                  phone,
                  wechat
                ) VALUES (%s, %s, %s, %s, %s, %s, %s);
            """

      values = (
          "王经理",
          "男",
          "1990-01-01",
          "字节跳动",
          "产品经理/产品总监",
          "18612345678",
          "wangjingli2024",
      )

      cursor.execute(insert_sql, values)
      insert_id = cursor.lastrowid

    print("成功创建数据库和表，并插入 demo 数据，插入ID：", insert_id)

  except Exception as err:
    print("执行出错：", err)
    raise
  finally:
    connection.close()


if __name__ == "__main__":
  main()
