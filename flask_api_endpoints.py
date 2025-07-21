# flask_api_endpoints.py
import pandas as pd
import psycopg2
from flask import Blueprint, jsonify, request
from sqlalchemy import create_engine
import os # Для работы с путями к файлам

# Создаем Blueprint для группировки API-маршрутов
api_bp = Blueprint('api', __name__)

# Ваш существующий движок SQLAlchemy
# Убедитесь, что эта строка подключения корректна и доступна из этой среды
engine = create_engine("postgresql+psycopg2://postgres:akzhol2030@86.107.198.48:5432/karatobe")

# --- Вспомогательная функция для получения соединения с БД ---
def get_db_connection():
    return psycopg2.connect(host="86.107.198.48", port="5432", dbname="karatobe", user="postgres", password="akzhol2030")

# --- Эндпоинт для получения данных о скважинах (wells) ---
@api_bp.route("/karatobe/wells", methods=["GET"])
def get_wells():
    conn = None
    try:
        conn = get_db_connection()
        df_wells = pd.read_sql_table("wells", con=conn)
        # Преобразуем float столбцы явно
        float_columns = ['x', 'y', 'lat', 'lon']
        for col in float_columns:
            if col in df_wells.columns:
                df_wells[col] = pd.to_numeric(df_wells[col], errors='coerce')
        return jsonify(df_wells.to_dict(orient="records"))
    except Exception as e:
        print(f"Ошибка при получении данных wells: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

# --- Эндпоинт для получения данных о добыче (production data) ---
@api_bp.route("/karatobe/production", methods=["GET"])
def get_production_data():
    conn = None
    try:
        conn = get_db_connection()
        # Избегаем выбора MAX("Date") в Python, лучше SQL-запросом
        # Получаем данные за последние 2 дня, как у вас было в Dash
        query = '''
            SELECT * FROM prod
            WHERE "Date" >= (SELECT MAX("Date") - INTERVAL '1 day' FROM prod)
            ORDER BY "Date" DESC;
        '''
        df_prod = pd.read_sql(query, con=conn)

        # Преобразование типов данных, как в вашем Dash-коде
        df_prod['Date'] = pd.to_datetime(df_prod['Date'])
        string_columns = ['well', 'Horizon']
        df_prod[string_columns] = df_prod[string_columns].astype(str)
        float_columns = ['Pump', 'H_m', 'Ptr_atm', 'Pztr_atm', 'Time_hr',
                         'Ql_m3', 'Qo_m3', 'Qw_m3', 'Qo_ton', 'Qi_m3']
        for col in float_columns:
            if col in df_prod.columns:
                df_prod[col] = pd.to_numeric(df_prod[col], errors='coerce')
        df_prod['Obv_percent'] = (100 * df_prod['Qw_m3'].div(df_prod['Ql_m3'])).replace(float('inf'), 0).round(1)

        # Вы можете вернуть все данные или только последние для карты
        # Для начала, вернем все данные за последние 2 дня
        return jsonify(df_prod.to_dict(orient="records"))
    except Exception as e:
        print(f"Ошибка при получении данных production: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

# --- Эндпоинт для получения данных разломов (Faults) ---
@api_bp.route("/karatobe/faults", methods=["GET"])
def get_faults():
    try:
        # Убедитесь, что путь к файлу корректен относительно места запуска Flask-приложения
        script_dir = os.path.dirname(__file__)
        filepath = os.path.join(script_dir, 'assets', 'karatobe', 'Faults.csv')
        df_faults = pd.read_csv(filepath)
        return jsonify(df_faults.to_dict(orient="records"))
    except Exception as e:
        print(f"Ошибка при получении данных faults: {e}")
        return jsonify({"error": str(e)}), 500

# --- Эндпоинт для получения данных границ (Gornyi_Otvod) ---
@api_bp.route("/karatobe/boundaries", methods=["GET"])
def get_boundaries():
    try:
        script_dir = os.path.dirname(__file__)
        filepath = os.path.join(script_dir, 'assets', 'karatobe', 'Gornyi_Otvod.csv')
        df_boundaries = pd.read_csv(filepath, skiprows=[1]) # Пропускаем первую строку, если она пустая
        return jsonify(df_boundaries.to_dict(orient="records"))
    except Exception as e:
        print(f"Ошибка при получении данных boundaries: {e}")
        return jsonify({"error": str(e)}), 500

# --- Эндпоинт для получения данных Gantt-чарта ---
@api_bp.route("/karatobe/gantt", methods=["GET"])
def get_gantt_data():
    try:
        script_dir = os.path.dirname(__file__)
        filepath = os.path.join(script_dir, 'assets', 'karatobe', 'gantt.csv')
        df_gantt = pd.read_csv(filepath)
        return jsonify(df_gantt.to_dict(orient="records"))
    except Exception as e:
        print(f"Ошибка при получении данных gantt: {e}")
        return jsonify({"error": str(e)}), 500

# --- Эндпоинт для получения данных PVT ---
@api_bp.route("/karatobe/pvt", methods=["GET"])
def get_pvt_data():
    conn = None
    try:
        conn = get_db_connection()
        df_pvt = pd.read_sql_table("pvt", con=conn)
        return jsonify(df_pvt.to_dict(orient="records"))
    except Exception as e:
        print(f"Ошибка при получении данных PVT: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

# --- Эндпоинт для получения данных TOPS ---
@api_bp.route("/karatobe/tops", methods=["GET"])
def get_tops_data():
    conn = None
    try:
        conn = get_db_connection()
        df_tops = pd.read_sql_table("tops", con=conn)
        return jsonify(df_tops.to_dict(orient="records"))
    except Exception as e:
        print(f"Ошибка при получении данных Tops: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

# --- Эндпоинт для получения данных RELATIVE PERMEABILITY TABLE ---
@api_bp.route("/karatobe/relative_permeability_table", methods=["GET"])
def get_rp_table_data():
    try:
        script_dir = os.path.dirname(__file__)
        filepath = os.path.join(script_dir, 'assets', 'karatobe', 'relative_permeability_table.csv')
        df_rp_table = pd.read_csv(filepath)
        return jsonify(df_rp_table.to_dict(orient="records"))
    except Exception as e:
        print(f"Ошибка при получении данных relative_permeability_table: {e}")
        return jsonify({"error": str(e)}), 500

# --- Эндпоинт для получения данных RELATIVE PERMEABILITY SUMMARY ---
@api_bp.route("/karatobe/relative_permeability_summary", methods=["GET"])
def get_rp_summary_data():
    try:
        script_dir = os.path.dirname(__file__)
        filepath = os.path.join(script_dir, 'assets', 'karatobe', 'relative_permeability_summary.csv')
        df_rp_summary = pd.read_csv(filepath)
        return jsonify(df_rp_summary.to_dict(orient="records"))
    except Exception as e:
        print(f"Ошибка при получении данных relative_permeability_summary: {e}")
        return jsonify({"error": str(e)}), 500

# --- Эндпоинт для получения данных XPT ---
@api_bp.route("/karatobe/xpt_data/<well_name>", methods=["GET"])
def get_xpt_data(well_name: str):
    try:
        # Путь к файлам XPT
        script_dir = os.path.dirname(__file__)
        filepath = os.path.join(script_dir, 'assets', 'karatobe', 'XPTs', well_name, 'XPT.csv')
        if not os.path.exists(filepath):
            return jsonify({"error": f"XPT data for well {well_name} not found."}), 404
        df_xpt = pd.read_csv(filepath)
        return jsonify(df_xpt.to_dict(orient="records"))
    except Exception as e:
        print(f"Ошибка при получении данных XPT для скважины {well_name}: {e}")
        return jsonify({"error": str(e)}), 500

# --- Эндпоинт для получения данных Well Log (LAS) ---
# Это будет сложнее, так как lasio возвращает объект, а не DataFrame
# Возможно, лучше отдавать LAS-файл напрямую и парсить его на клиенте,
# или парсить на сервере и отдавать только нужные кривые
@api_bp.route("/karatobe/logs/<well_name>", methods=["GET"])
def get_well_log_data(well_name: str):
    try:
        script_dir = os.path.dirname(__file__)
        log_dir = os.path.join(script_dir, 'assets', 'karatobe', 'LOGs', well_name)
        
        # Находим первый LAS-файл в директории
        log_file = None
        for f in os.listdir(log_dir):
            if f.lower().endswith('.las'):
                log_file = os.path.join(log_dir, f)
                break
        
        if not log_file:
            return jsonify({"error": f"No LAS file found for well {well_name}."}), 404

        las = lasio.read(log_file)
        df_log = las.df()
        df_log.reset_index(inplace=True) # Сделаем 'DEPT' обычной колонкой

        # Convert datetime columns to string if any (lasio might parse dates)
        for col in df_log.columns:
            if pd.api.types.is_datetime64_any_dtype(df_log[col]):
                df_log[col] = df_log[col].dt.isoformat()

        # Заменяем NaN на None для JSON-сериализации
        return jsonify(df_log.replace({np.nan: None}).to_dict(orient="records"))
    except Exception as e:
        print(f"Ошибка при получении данных лога для скважины {well_name}: {e}")
        return jsonify({"error": str(e)}), 500

# --- Временный эндпоинт для имитации логина с Next.js (без Flask-Login) ---
@api_bp.route("/login_from_nextjs", methods=["POST"])
def login_from_nextjs():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Здесь можно добавить простую проверку:
    if username == "test" and password == "test":
        # Или более сложную, если хотите, чтобы она совпадала с вашими текущими пользователями Flask-Login
        # Например, получить пользователя из вашей DB и проверить пароль:
        # from run import db, bcrypt, User # Импортировать из вашего run.py
        # user = db.session.query(User).filter_by(username=username).first()
        # if user and bcrypt.check_password_hash(user.password, password):
        #     return jsonify({"message": "Login successful", "user_level": user.user_level}), 200
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401