import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, Query
import uvicorn

# ==========================================
# 改这里！
# ==========================================
DB_URL = "postgresql://postgres:mEQ2SNFjpb7R1XqV@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
# ==========================================
app = FastAPI()

def get_db():
    return psycopg2.connect(DB_URL, connect_timeout=10, sslmode='require')

@app.get("/")
async def root():
    return {"status": "running"}

@app.get("/query_machine_params")
async def query_machine_params(
    device_id: str = Query(...),
    start_time: str = Query(...),
    end_time: str = Query(...)
):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT timestamp, zone_name, set_temp, actual_temp, belt_speed
        FROM machine_params
        WHERE device_id = %s AND timestamp >= %s::timestamp AND timestamp <= %s::timestamp
        ORDER BY timestamp, zone_name
    """, (device_id, start_time, end_time))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "time": r['timestamp'].strftime('%H:%M'),
            "zone": r['zone_name'],
            "set_temp": float(r['set_temp']),
            "actual_temp": float(r['actual_temp']),
            "belt_speed": float(r['belt_speed'])
        })
    return {"data": result}

@app.get("/query_maintenance_logs")
async def query_maintenance_logs(
    device_id: str = Query(...),
    start_time: str = Query(...),
    end_time: str = Query(...)
):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT timestamp, log_type, description, operator
        FROM maintenance_logs
        WHERE device_id = %s AND timestamp >= %s::timestamp AND timestamp <= %s::timestamp
        ORDER BY timestamp
    """, (device_id, start_time, end_time))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "time": r['timestamp'].strftime('%H:%M'),
            "type": r['log_type'],
            "description": r['description'],
            "operator": r['operator']
        })
    return {"data": result}

@app.get("/query_material_batch")
async def query_material_batch(
    batch_no: str = Query(default=""),
    material_type: str = Query(default="")
):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    if batch_no:
        cur.execute("SELECT * FROM material_batches WHERE batch_no = %s", (batch_no,))
    elif material_type:
        cur.execute("SELECT * FROM material_batches WHERE material_type LIKE %s ORDER BY in_time DESC", (f'%{material_type}%',))
    else:
        cur.execute("SELECT * FROM material_batches ORDER BY in_time DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "batch_no": r['batch_no'],
            "material_type": r['material_type'],
            "supplier": r['supplier'],
            "in_time": r['in_time'].strftime('%m-%d %H:%M'),
            "inspection_result": r['inspection_result'],
            "notes": r['inspection_notes']
        })
    return {"data": result}

@app.get("/query_production_logs")
async def query_production_logs(
    product_model: str = Query(...),
    start_time: str = Query(...),
    end_time: str = Query(...)
):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT timestamp, total_produced, defect_count, defect_type, defect_rate
        FROM production_logs
        WHERE product_model = %s AND timestamp >= %s::timestamp AND timestamp <= %s::timestamp
        ORDER BY timestamp
    """, (product_model, start_time, end_time))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "time": r['timestamp'].strftime('%H:%M'),
            "total_produced": r['total_produced'],
            "defect_count": r['defect_count'],
            "defect_type": r['defect_type'],
            "defect_rate": float(r['defect_rate'])
        })
    return {"data": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)



