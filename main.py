from fastapi import FastAPI, Query
import uvicorn

app = FastAPI()

# 硬编码的演示数据
MACHINE_PARAMS = [
    {"time": "13:00", "zone": "预热区", "set_temp": 150.0, "actual_temp": 150.5, "belt_speed": 80.0},
    {"time": "13:30", "zone": "预热区", "set_temp": 150.0, "actual_temp": 150.7, "belt_speed": 80.0},
    {"time": "14:00", "zone": "预热区", "set_temp": 150.0, "actual_temp": 151.8, "belt_speed": 80.0},
    {"time": "14:15", "zone": "预热区", "set_temp": 153.0, "actual_temp": 154.2, "belt_speed": 80.0},
    {"time": "14:30", "zone": "预热区", "set_temp": 153.0, "actual_temp": 155.1, "belt_speed": 80.0},
    {"time": "14:45", "zone": "预热区", "set_temp": 153.0, "actual_temp": 155.5, "belt_speed": 80.0},
    {"time": "13:00", "zone": "回流区", "set_temp": 240.0, "actual_temp": 240.2, "belt_speed": 80.0},
    {"time": "14:00", "zone": "回流区", "set_temp": 240.0, "actual_temp": 240.5, "belt_speed": 80.0},
    {"time": "14:30", "zone": "回流区", "set_temp": 240.0, "actual_temp": 241.0, "belt_speed": 80.0},
]

MAINTENANCE_LOGS = [
    {"time": "09:00", "type": "日常点检", "description": "设备运行正常，各温区温度偏差均在±2°C内", "operator": "张工"},
    {"time": "14:00", "type": "外部维保", "description": "车间空调例行维护，预计14:00-14:20车间温度可能短时升高2-5°C", "operator": "外部供应商"},
    {"time": "14:15", "type": "参数调整", "description": "手动将预热区设定温度从150°C调整为153°C", "operator": "李工（当班操作员）"},
]

MATERIAL_BATCHES = [
    {"batch_no": "SP-2025-0610", "material_type": "锡膏 SAC305", "supplier": "铟泰科技", "in_time": "06-10 08:00", "inspection_result": "合格", "notes": "粘度、金属含量均符合标准"},
    {"batch_no": "PCB-2025-0612", "material_type": "PCB板 FR-4", "supplier": "深南电路", "in_time": "06-12 08:00", "inspection_result": "合格", "notes": "焊盘氧化度在标准范围内"},
    {"batch_no": "SP-2025-0614", "material_type": "锡膏 SAC305", "supplier": "铟泰科技", "in_time": "06-14 08:00", "inspection_result": "合格", "notes": "新批次，各项指标正常"},
]

PRODUCTION_LOGS = [
    {"time": "13:00", "total": 200, "defect": 1, "type": "BGA空洞", "rate": 0.50},
    {"time": "13:15", "total": 200, "defect": 1, "type": "BGA空洞", "rate": 0.50},
    {"time": "13:30", "total": 200, "defect": 1, "type": "BGA空洞", "rate": 0.50},
    {"time": "13:45", "total": 200, "defect": 0, "type": "BGA空洞", "rate": 0.00},
    {"time": "14:00", "total": 200, "defect": 1, "type": "BGA空洞", "rate": 0.50},
    {"time": "14:15", "total": 200, "defect": 2, "type": "BGA空洞", "rate": 1.00},
    {"time": "14:30", "total": 200, "defect": 6, "type": "BGA空洞", "rate": 3.00},
    {"time": "14:45", "total": 200, "defect": 7, "type": "BGA空洞", "rate": 3.50},
    {"time": "15:00", "total": 200, "defect": 6, "type": "BGA空洞", "rate": 3.00},
]

@app.get("/")
async def root():
    return {"status": "running"}

@app.get("/query_machine_params")
async def query_machine_params(device_id: str = Query(...), start_time: str = Query(...), end_time: str = Query(...)):
    return {"data": MACHINE_PARAMS}

@app.get("/query_maintenance_logs")
async def query_maintenance_logs(device_id: str = Query(...), start_time: str = Query(...), end_time: str = Query(...)):
    return {"data": MAINTENANCE_LOGS}

@app.get("/query_material_batch")
async def query_material_batch(batch_no: str = Query(default=""), material_type: str = Query(default="")):
    return {"data": MATERIAL_BATCHES}

@app.get("/query_production_logs")
async def query_production_logs(product_model: str = Query(...), start_time: str = Query(...), end_time: str = Query(...)):
    return {"data": PRODUCTION_LOGS}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
