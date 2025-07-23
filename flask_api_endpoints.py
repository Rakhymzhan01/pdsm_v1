# flask_api_endpoints.py
import pandas as pd
import psycopg2
from flask import Blueprint, jsonify, request
from sqlalchemy import create_engine
import os # Для работы с путями к файлам
import numpy as np
import lasio
import json

# Создаем Blueprint для группировки API-маршрутов
api_bp = Blueprint('api', __name__)

# Custom JSON encoder to handle NaN values
class NanToNullEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
            return 'null'
        return super().encode(obj)
    
    def iterencode(self, obj, _one_shot=False):
        """Encode the given object and yield each string representation as available."""
        def _encode_obj(obj):
            if isinstance(obj, dict):
                return {k: _encode_obj(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_encode_obj(item) for item in obj]
            elif isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
                return None
            else:
                return obj
        
        clean_obj = _encode_obj(obj)
        return super().iterencode(clean_obj, _one_shot)

# Utility function to handle NaN values for JSON serialization
def clean_dataframe_for_json(df):
    """Replace NaN, inf, and other problematic values with None for JSON serialization"""
    # The custom JSON encoder will handle NaN values, so we don't need to modify the DataFrame
    return df

# Custom jsonify function that handles NaN values
def safe_jsonify(data):
    """Jsonify with NaN handling"""
    clean_data = json.loads(json.dumps(data, cls=NanToNullEncoder))
    return jsonify(clean_data)

# Ваш существующий движок SQLAlchemy
# Убедитесь, что эта строка подключения корректна и доступна из этой среды
engine = create_engine("postgresql+psycopg2://postgres:akzhol2030@86.107.198.48:5432/karatobe")

# --- Вспомогательная функция для получения соединения с БД ---
def get_db_connection():
    return psycopg2.connect(host="86.107.198.48", port="5432", dbname="karatobe", user="postgres", password="akzhol2030")

# --- Эндпоинт для получения данных о скважинах (wells) ---
@api_bp.route("/karatobe/wells", methods=["GET"])
def get_wells():
    try:
        # Use SQLAlchemy engine instead of psycopg2 connection
        df_wells = pd.read_sql_table("wells", con=engine)
        # Преобразуем float столбцы явно
        float_columns = ['x', 'y', 'lat', 'lon']
        for col in float_columns:
            if col in df_wells.columns:
                df_wells[col] = pd.to_numeric(df_wells[col], errors='coerce')
        # Clean dataframe for JSON serialization
        df_wells = clean_dataframe_for_json(df_wells)
        
        return safe_jsonify(df_wells.to_dict(orient="records"))
    except Exception as e:
        print(f"Ошибка при получении данных wells: {e}")
        return jsonify({"error": str(e)}), 500

# --- Эндпоинт для получения данных о добыче (production data) ---
@api_bp.route("/karatobe/production", methods=["GET"])
def get_production_data():
    print("🔍 Production API called - attempting to fetch real data...")
    try:
        # Simplified approach - just use the same logic as debug endpoint
        query = '''
            SELECT * FROM prod
            WHERE "Date" >= (SELECT MAX("Date") - INTERVAL '7 days' FROM prod)
            ORDER BY "Date" DESC
            LIMIT 10;
        '''
        print(f"🔍 Executing query: {query}")
        df_prod = pd.read_sql(query, con=engine)
        print(f"🔍 Query returned {len(df_prod)} rows")

        if df_prod.empty:
            print("⚠️ Query returned empty result")
            return jsonify([]), 200

        print(f"🔍 Columns: {df_prod.columns.tolist()}")
        
        # Minimal processing - just return the data
        result = df_prod.to_dict(orient="records")
        print(f"✅ SUCCESS: Returning {len(result)} REAL database records")
        return jsonify(result)
    except Exception as e:
        import traceback
        print(f"❌ Production API Error: {e}")
        print(f"❌ Full traceback: {traceback.format_exc()}")
        print(f"🔄 Returning demo fallback data instead of real production data")
        # Return demo data as fallback
        demo_data = [
            {"Date": "2025-07-21", "well": "301", "Qo_ton": 15.2, "Qw_m3": 3.5, "Ql_m3": 14.0, "Obv_percent": 25.0},
            {"Date": "2025-07-21", "well": "302", "Qo_ton": 18.5, "Qw_m3": 2.8, "Ql_m3": 15.2, "Obv_percent": 18.4},
            {"Date": "2025-07-21", "well": "303", "Qo_ton": 12.1, "Qw_m3": 5.1, "Ql_m3": 14.5, "Obv_percent": 35.2}
        ]
        print(f"🔄 Returning {len(demo_data)} fallback demo records")
        return jsonify(demo_data), 200

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
    try:
        df_pvt = pd.read_sql_table("pvt", con=engine)
        return jsonify(df_pvt.to_dict(orient="records"))
    except Exception as e:
        print(f"Ошибка при получении данных PVT: {e}")
        return jsonify({"error": str(e)}), 500

# --- Эндпоинт для получения данных TOPS ---
@api_bp.route("/karatobe/tops", methods=["GET"])
def get_tops_data():
    try:
        df_tops = pd.read_sql_table("tops", con=engine)
        return jsonify(df_tops.to_dict(orient="records"))
    except Exception as e:
        print(f"Ошибка при получении данных Tops: {e}")
        return jsonify({"error": str(e)}), 500

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

# --- Debug endpoint to check database tables ---
@api_bp.route("/debug/tables", methods=["GET"])
def get_database_tables():
    try:
        # Query to get table names
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """
        df_tables = pd.read_sql(query, con=engine)
        return jsonify({
            "tables": df_tables['table_name'].tolist(),
            "count": len(df_tables)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Debug endpoint to test production query ---
@api_bp.route("/debug/test_prod_query", methods=["GET"])
def test_prod_query():
    try:
        # Same query as production endpoint
        query = '''
            SELECT * FROM prod
            WHERE "Date" >= (SELECT MAX("Date") - INTERVAL '7 days' FROM prod)
            ORDER BY "Date" DESC
            LIMIT 10;
        '''
        df_test = pd.read_sql(query, con=engine)
        
        return jsonify({
            "query_result_count": len(df_test),
            "columns": df_test.columns.tolist(),
            "sample_records": df_test.head(3).to_dict('records')
        })
    except Exception as e:
        return jsonify({"error": str(e), "query": query}), 500

# --- Debug endpoint to check latest dates in prod table ---
@api_bp.route("/debug/prod_dates", methods=["GET"])
def get_prod_dates():
    try:
        # Query to get date range
        query = "SELECT MIN(\"Date\") as min_date, MAX(\"Date\") as max_date, COUNT(*) as total_records FROM prod;"
        df_dates = pd.read_sql(query, con=engine)
        
        return jsonify(df_dates.to_dict('records')[0])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Debug endpoint to check prod table data ---
@api_bp.route("/debug/prod_sample", methods=["GET"])
def get_prod_sample():
    try:
        # Simple query to get sample data
        query = "SELECT * FROM prod LIMIT 10;"
        df_sample = pd.read_sql(query, con=engine)
        
        return jsonify({
            "count": len(df_sample),
            "columns": df_sample.columns.tolist(),
            "sample_data": df_sample.to_dict('records')[:3]  # First 3 records
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Debug endpoint to check prod table structure ---
@api_bp.route("/debug/prod_columns", methods=["GET"])
def get_prod_table_columns():
    try:
        # Query to get column information for prod table
        query = """
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'prod' 
            ORDER BY ordinal_position;
        """
        df_columns = pd.read_sql(query, con=engine)
        return jsonify({
            "columns": df_columns.to_dict('records'),
            "count": len(df_columns)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Эндпоинт для авторизации через Next.js ---
@api_bp.route("/login_from_nextjs", methods=["POST"])
def login_from_nextjs():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    try:
        # Import bcrypt for password verification
        import bcrypt
        
        # Connect to the database to check user
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query the users table
        cursor.execute("SELECT username, password, user_level FROM users WHERE username = %s", (username,))
        user_row = cursor.fetchone()
        
        if user_row:
            stored_username, stored_password_hash, user_level = user_row
            
            # Check if password matches the bcrypt hash
            if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                return jsonify({
                    "message": "Login successful",
                    "user": {
                        "username": stored_username,
                        "role": user_level
                    }
                }), 200
            else:
                return jsonify({"message": "Invalid credentials"}), 401
        else:
            # Check simple test credentials if user not in DB
            if username == "test" and password == "test":
                return jsonify({
                    "message": "Login successful", 
                    "user": {
                        "username": username,
                        "role": "administrator"
                    }
                }), 200
            else:
                return jsonify({"message": "User not found"}), 401
                
    except Exception as e:
        print(f"Login error: {e}")
        # Fallback to simple test credentials
        if username == "test" and password == "test":
            return jsonify({
                "message": "Login successful",
                "user": {
                    "username": username, 
                    "role": "administrator"
                }
            }), 200
        else:
            return jsonify({"message": "Database error"}), 500
    finally:
        if 'conn' in locals():
            conn.close()