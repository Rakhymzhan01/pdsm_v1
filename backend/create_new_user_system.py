#!/usr/bin/env python3
"""
Create new user system with projects and approval workflow
"""
import psycopg2
import bcrypt

conn = psycopg2.connect(
    host="86.107.198.48",
    port="5432", 
    dbname="karatobe",
    user="postgres",
    password="akzhol2030"
)
cursor = conn.cursor()

print("Создаем новую систему пользователей...")

# 1. Создаем таблицу проектов
cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# 2. Создаем новую таблицу пользователей
cursor.execute("""
    CREATE TABLE IF NOT EXISTS app_users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        role VARCHAR(20) DEFAULT 'user',
        status VARCHAR(20) DEFAULT 'pending',
        project_id INTEGER REFERENCES projects(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        approved_at TIMESTAMP NULL,
        approved_by INTEGER REFERENCES app_users(id)
    )
""")

# 3. Добавляем проекты
projects = [
    ('Karatobe Field', 'Karatobe oil field development project'),
    ('Airankol Field', 'Airankol field exploration project'),
    ('Crystal Management', 'Crystal management system project'),
    ('SeiPulse', 'Seismic data analysis project'),
    ('General Access', 'General system access for all projects')
]

for name, desc in projects:
    cursor.execute("""
        INSERT INTO projects (name, description) 
        VALUES (%s, %s) 
        ON CONFLICT (name) DO NOTHING
    """, (name, desc))

# 4. Создаем мастер-пользователя Aman
master_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
cursor.execute("""
    INSERT INTO app_users (username, email, password, first_name, last_name, role, status, project_id) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, 
            (SELECT id FROM projects WHERE name = 'General Access'))
    ON CONFLICT (username) DO UPDATE SET
        password = EXCLUDED.password,
        role = EXCLUDED.role,
        status = EXCLUDED.status
""", ('Aman', 'aman@pdms.kz', master_password, 'Aman', 'Master', 'master', 'approved'))

# 5. Создаем несколько тестовых пользователей
test_users = [
    ('guest', 'guest@pdms.kz', 'guest123', 'Guest', 'User', 'user', 'approved', 'Karatobe Field'),
    ('engineer', 'eng@pdms.kz', 'eng123', 'Test', 'Engineer', 'user', 'pending', 'Airankol Field'),
    ('analyst', 'analyst@pdms.kz', 'analyst123', 'Data', 'Analyst', 'user', 'pending', 'Crystal Management')
]

for username, email, password, fname, lname, role, status, project in test_users:
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute("""
        INSERT INTO app_users (username, email, password, first_name, last_name, role, status, project_id) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, 
                (SELECT id FROM projects WHERE name = %s))
        ON CONFLICT (username) DO UPDATE SET
            password = EXCLUDED.password,
            status = EXCLUDED.status
    """, (username, email, hashed_pw, fname, lname, role, status, project))

conn.commit()

# Показываем созданные данные
print("\n✅ Система создана!")
print("\n📋 ПРОЕКТЫ:")
cursor.execute("SELECT id, name, description FROM projects")
for proj in cursor.fetchall():
    print(f"  {proj[0]}. {proj[1]} - {proj[2]}")

print("\n👥 ПОЛЬЗОВАТЕЛИ:")
cursor.execute("""
    SELECT au.username, au.email, au.role, au.status, p.name as project 
    FROM app_users au 
    LEFT JOIN projects p ON au.project_id = p.id 
    ORDER BY au.role DESC, au.status
""")
for user in cursor.fetchall():
    print(f"  {user[0]:10} | {user[1]:15} | {user[2]:6} | {user[3]:8} | {user[4]}")

print("\n🔑 ЛОГИН ДАННЫЕ:")
print("="*50)
print("МАСТЕР-ПОЛЬЗОВАТЕЛЬ:")
print("  Username: Aman")
print("  Password: admin123")
print("  Role: master (может аппрувить пользователей)")
print("\nТЕСТОВЫЕ ПОЛЬЗОВАТЕЛИ:")
print("  guest/guest123 (approved - может логиниться)")
print("  engineer/eng123 (pending - нужен аппрув)")
print("  analyst/analyst123 (pending - нужен аппрув)")
print("="*50)

conn.close()