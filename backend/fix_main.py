content = open(r'D:\ai-carbon-system\backend\app\main.py', 'r', encoding='utf-8').read()
content = content.replace(
    'from app.api import carbon_asset, optimization, measures, alert, auth, backup',
    'from app.api import carbon_asset, optimization, measures, alert, auth, backup, footprint'
)
insert_after = 'app.include_router(backup.router, prefix="/api/v1/backup", tags=["数据备份"])'
insert_line = 'app.include_router(footprint.router, prefix="/api/v1/footprint", tags=["碳足迹追踪"])'
content = content.replace(insert_after, insert_after + '\n' + insert_line)
open(r'D:\ai-carbon-system\backend\app\main.py', 'w', encoding='utf-8').write(content)
print('Done')