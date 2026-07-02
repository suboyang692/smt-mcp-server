import os
import json
import asyncio
from fastapi import FastAPI, Request, Query
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn

app = FastAPI()

# ==========================================
# 硬编码演示数据
# ==========================================
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
    {"time": "09:00", "type": "日常点检", "description": "设备运行正常，各温区偏差±2°C内", "operator": "张工"},
    {"time": "14:00", "type": "外部维保", "description": "车间空调例行维护，14:00-14:20车间温度短时升高2-5°C", "operator": "外部供应商"},
    {"time": "14:15", "type": "参数调整", "description": "手动将预热区设定温度从150°C调为153°C", "operator": "李工"},
]

MATERIAL_BATCHES = [
    {"batch_no": "SP-2025-0610", "material_type": "锡膏 SAC305", "supplier": "铟泰科技", "in_time": "06-10", "result": "合格", "notes": "粘度正常"},
    {"batch_no": "SP-2025-0614", "material_type": "锡膏 SAC305", "supplier": "铟泰科技", "in_time": "06-14", "result": "合格", "notes": "新批次"},
]

PRODUCTION_LOGS = [
    {"time": "13:00", "total": 200, "defect": 1, "rate": 0.5},
    {"time": "13:30", "total": 200, "defect": 1, "rate": 0.5},
    {"time": "14:00", "total": 200, "defect": 1, "rate": 0.5},
    {"time": "14:15", "total": 200, "defect": 2, "rate": 1.0},
    {"time": "14:30", "total": 200, "defect": 6, "rate": 3.0},
    {"time": "14:45", "total": 200, "defect": 7, "rate": 3.5},
]

@app.get("/")
async def root():
    return {"status": "MCP service running"}

# MCP SSE endpoint
@app.get("/sse")
async def sse_endpoint(request: Request):
    async def event_stream():
        yield f"data: {json.dumps({'type': 'endpoint', 'url': '/message'})}\n\n"
        while True:
            await asyncio.sleep(30)
            yield f": keepalive\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")

# MCP message endpoint
@app.post("/message")
async def mcp_message(request: Request):
    body = await request.json()
    method = body.get("method", "")
    params = body.get("params", {}).get("arguments", {})
    
    # List tools
    if method == "tools/list":
        return JSONResponse({
            "tools": [
                {"name": "query_production_logs", "description": "查询生产记录", "inputSchema": {"type": "object", "properties": {"product_model": {"type": "string"}, "start_time": {"type": "string"}, "end_time": {"type": "string"}}}},
                {"name": "query_machine_params", "description": "查询设备参数", "inputSchema": {"type": "object", "properties": {"device_id": {"type": "string"}, "start_time": {"type": "string"}, "end_time": {"type": "string"}}}},
                {"name": "query_maintenance_logs", "description": "查询维保记录", "inputSchema": {"type": "object", "properties": {"device_id": {"type": "string"}, "start_time": {"type": "string"}, "end_time": {"type": "string"}}}},
                {"name": "query_material_batch", "description": "查询来料批次", "inputSchema": {"type": "object", "properties": {"material_type": {"type": "string"}}}},
            ]
        })
    
    # Call tool
    elif method == "tools/call":
        tool_name = body.get("params", {}).get("name", "")
        
        if tool_name == "query_production_logs":
            result = json.dumps(PRODUCTION_LOGS, ensure_ascii=False)
        elif tool_name == "query_machine_params":
            result = json.dumps(MACHINE_PARAMS, ensure_ascii=False)
        elif tool_name == "query_maintenance_logs":
            result = json.dumps(MAINTENANCE_LOGS, ensure_ascii=False)
        elif tool_name == "query_material_batch":
            result = json.dumps(MATERIAL_BATCHES, ensure_ascii=False)
        else:
            result = "Tool not found"
        
        return JSONResponse({
            "content": [{"type": "text", "text": result}]
        })
    
    return JSONResponse({"error": "Unknown method"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
