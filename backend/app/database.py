"""
数据库连接配置 - SQLite
"""
import sqlite3
from pathlib import Path
from datetime import datetime

# Railway 使用 /app 目录，本地开发使用项目目录
import os
if os.environ.get('RAILWAY_ENVIRONMENT'):
    DB_PATH = Path("/app/data/carbon.db")
else:
    DB_PATH = Path(__file__).resolve().parent.parent / "carbon.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def init_db():
    """初始化数据库表"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA encoding = 'UTF-8'")
    cursor = conn.cursor()
    
    # 企业表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            industry TEXT,
            region TEXT DEFAULT '默认',
            employee_count INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    """)
    
    # 碳排放记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carbon_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            record_date TEXT NOT NULL,
            scope TEXT NOT NULL,
            emission_source TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            co2_emission REAL,
            emission_factor REAL,
            region TEXT DEFAULT '默认',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)
    
    # OCR识别记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ocr_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            image_path TEXT,
            extracted_data TEXT,
            confidence REAL,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)
    
    # 降碳措施库表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carbon_measures (
            id TEXT PRIMARY KEY,
            industry TEXT NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            reduction_potential REAL NOT NULL,
            investment_cost REAL NOT NULL,
            annual_saving REAL NOT NULL,
            difficulty TEXT NOT NULL,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_measures_industry ON carbon_measures(industry)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_measures_category ON carbon_measures(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_measures_active ON carbon_measures(is_active)')
    
    # 行业基准数据表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS industry_benchmarks (
            industry TEXT PRIMARY KEY,
            emission_intensity_avg REAL NOT NULL,
            emission_intensity_advanced REAL NOT NULL,
            reduction_potential REAL NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 排放因子表（年份+地区维度）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emission_factors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emission_source TEXT NOT NULL,
            unit TEXT NOT NULL,
            factor REAL NOT NULL,
            region TEXT DEFAULT '全国',
            year INTEGER DEFAULT 2022,
            source TEXT DEFAULT 'GB/T 32150',
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(emission_source, unit, region, year)
        )
    """)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ef_source ON emission_factors(emission_source)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ef_region ON emission_factors(region)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ef_year ON emission_factors(year)')
    
    # 用户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            hashed_password TEXT NOT NULL,
            company_name TEXT NOT NULL,
            industry TEXT,
            role TEXT DEFAULT 'user',
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')

    # 预警阈值表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alert_thresholds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL UNIQUE,
            monthly_total REAL DEFAULT 10000,
            scope1_ratio REAL DEFAULT 0.5,
            scope2_ratio REAL DEFAULT 0.6,
            mom_increase REAL DEFAULT 0.2,
            yoy_increase REAL DEFAULT 0.3,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)

    # 预警历史表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alert_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            alert_type TEXT NOT NULL,
            level TEXT NOT NULL,
            message TEXT NOT NULL,
            threshold_value REAL,
            actual_value REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_alert_history_company ON alert_history(company_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_alert_history_created ON alert_history(created_at)')

    # 产品碳足迹表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_footprints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            product_code TEXT,
            category TEXT,
            functional_unit TEXT DEFAULT '件',
            lifespan_years REAL DEFAULT 1.0,
            total_emission REAL,
            status TEXT DEFAULT 'draft',
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fp_company ON product_footprints(company_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fp_status ON product_footprints(status)')

    # 碳足迹阶段明细表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS footprint_stages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            stage TEXT NOT NULL,
            material_name TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            emission_factor REAL,
            emission REAL NOT NULL,
            source TEXT DEFAULT '用户自定义',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES product_footprints(id) ON DELETE CASCADE
        )
    """)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fs_product ON footprint_stages(product_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fs_stage ON footprint_stages(stage)')

    # 种子数据迁移
    _seed_measures(cursor)
    _seed_benchmarks(cursor)
    _seed_emission_factors(cursor)
    _seed_product_footprint_tables(cursor)
    
    conn.commit()
    conn.close()
    print(f"数据库初始化完成: {DB_PATH}")

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA encoding = 'UTF-8'")
    conn.row_factory = sqlite3.Row
    return conn


def _seed_measures(cursor):
    """将硬编码措施数据迁移到数据库（幂等）"""
    cursor.execute('SELECT COUNT(*) FROM carbon_measures')
    if cursor.fetchone()[0] > 0:
        return  # 已有数据，跳过
    
    measures = [
        # 制造业
        ('mfg_001', '制造业', '高效电机替换', 'equipment', 50, 15, 8, 'medium', '将老旧电机更换为一级能效电机，节能15-20%'),
        ('mfg_002', '制造业', '余热回收系统', 'energy', 80, 30, 18, 'hard', '回收生产过程中的余热用于供暖或发电'),
        ('mfg_003', '制造业', '智能照明改造', 'energy', 15, 3, 2.5, 'easy', 'LED灯具+智能控制系统，节能60%'),
        ('mfg_004', '制造业', '光伏发电系统', 'renewable', 120, 50, 15, 'medium', '屋顶分布式光伏，自发自用余电上网'),
        ('mfg_005', '制造业', '变频空调系统', 'equipment', 25, 8, 4, 'easy', '变频技术降低空调能耗30%'),
        ('mfg_006', '制造业', '空压机系统优化', 'energy', 35, 12, 6, 'medium', '变频空压机+管网优化，节能25%'),
        ('mfg_007', '制造业', '锅炉节能改造', 'energy', 60, 25, 14, 'hard', '冷凝水回收+燃烧优化，提高热效率15%'),
        ('mfg_008', '制造业', '变压器经济运行', 'energy', 20, 5, 3, 'easy', '优化变压器负载率，降低损耗'),
        ('mfg_009', '制造业', '高效注塑机', 'equipment', 45, 35, 12, 'hard', '全电动注塑机替代液压式，节能50%'),
        ('mfg_010', '制造业', '高效水泵改造', 'equipment', 25, 8, 4.5, 'easy', '高效水泵+变频控制，节能30%'),
        ('mfg_011', '制造业', '智能温控系统', 'equipment', 30, 10, 5, 'medium', '生产车间智能温控，按需供能'),
        ('mfg_012', '制造业', '储能系统', 'renewable', 40, 45, 10, 'hard', '削峰填谷储能，降低电费支出'),
        ('mfg_013', '制造业', '生物质锅炉', 'renewable', 90, 40, 8, 'hard', '生物质燃料替代燃煤锅炉'),
        ('mfg_014', '制造业', '精益生产改造', 'process', 35, 8, 5, 'medium', '优化生产流程，减少能耗浪费'),
        ('mfg_015', '制造业', '数字化能源管理', 'process', 25, 20, 8, 'medium', 'EMS系统实时监控能耗'),
        # 纺织业
        ('tex_001', '纺织业', '印染废水余热回收', 'energy', 60, 25, 12, 'medium', '回收印染废水热量，降低蒸汽消耗'),
        ('tex_002', '纺织业', '高效定型机改造', 'equipment', 45, 20, 10, 'medium', '升级定型机热交换系统'),
        ('tex_003', '纺织业', '太阳能热水系统', 'renewable', 35, 12, 5, 'easy', '利用太阳能预热工艺用水'),
        ('tex_004', '纺织业', '低浴比染色工艺', 'process', 30, 10, 6, 'medium', '采用低浴比染色技术，节水节能'),
        ('tex_005', '纺织业', '高效锅炉系统', 'energy', 50, 30, 15, 'hard', '冷凝水回收+变频风机，热效率提升18%'),
        ('tex_006', '纺织业', '空压机热回收', 'energy', 35, 15, 7, 'medium', '回收压缩热用于工艺加热'),
        ('tex_007', '纺织业', '高效织机升级', 'equipment', 30, 25, 8, 'hard', '新型喷气织机，能耗降低25%'),
        ('tex_008', '纺织业', '智能染色机', 'equipment', 40, 35, 12, 'hard', '自动化染色控制，减少能耗20%'),
        ('tex_009', '纺织业', '屋顶光伏电站', 'renewable', 80, 60, 18, 'medium', '厂房屋顶光伏，自发自用'),
        ('tex_010', '纺织业', '冷轧堆前处理', 'process', 35, 18, 9, 'medium', '低能耗前处理工艺'),
        ('tex_011', '纺织业', '数码印花技术', 'process', 25, 22, 7, 'medium', '数码印花替代传统印花，节水60%'),
        ('tex_012', '纺织业', '能耗监测系统', 'process', 20, 8, 4, 'easy', '实时能耗监控与分析'),
        # 零售业
        ('ret_001', '零售业', '智能冷链系统', 'equipment', 20, 8, 3.5, 'medium', '智能温控+高效压缩机'),
        ('ret_002', '零售业', 'LED照明升级', 'energy', 12, 2, 1.8, 'easy', '全店LED灯具替换'),
        ('ret_003', '零售业', '绿色物流配送', 'process', 25, 15, 6, 'medium', '新能源配送车辆+路径优化'),
        ('ret_004', '零售业', '智能照明控制', 'energy', 8, 3, 1.2, 'easy', '光感+人感自动调光'),
        ('ret_005', '零售业', '空调系统优化', 'energy', 15, 5, 2.5, 'medium', '变频空调+智能温控'),
        ('ret_006', '零售业', '高效冷柜', 'equipment', 10, 4, 1.5, 'easy', '新型节能冷柜，能耗降低30%'),
        ('ret_007', '零售业', '智能POS终端', 'equipment', 5, 2, 0.8, 'easy', '低功耗POS设备'),
        ('ret_008', '零售业', '屋顶光伏', 'renewable', 25, 15, 4, 'medium', '商场屋顶光伏发电'),
        ('ret_009', '零售业', '智能库存管理', 'process', 10, 6, 2, 'medium', '减少损耗，优化补货'),
        ('ret_010', '零售业', '可降解包装', 'process', 8, 3, 1, 'easy', '环保包装材料替代'),
        # 科技
        ('tech_001', '科技', '数据中心节能', 'equipment', 100, 40, 25, 'hard', '精密空调+冷热通道隔离'),
        ('tech_002', '科技', '智能楼宇系统', 'energy', 35, 15, 8, 'medium', 'BMS系统优化能耗管理'),
        ('tech_003', '科技', '光伏车棚', 'renewable', 40, 18, 5, 'easy', '停车场光伏发电+充电桩'),
        ('tech_004', '科技', '高效UPS系统', 'energy', 20, 12, 5, 'medium', '模块化UPS，效率提升至96%'),
        ('tech_005', '科技', '智能照明', 'energy', 10, 3, 1.5, 'easy', '办公区智能调光'),
        ('tech_006', '科技', '液冷服务器', 'equipment', 80, 60, 20, 'hard', '液体冷却技术，PUE降至1.1'),
        ('tech_007', '科技', '高效空调机组', 'equipment', 30, 18, 6, 'medium', '磁悬浮离心机组'),
        ('tech_008', '科技', '绿色电力采购', 'renewable', 150, 5, 0, 'easy', '直接购买绿电，减排效果显著'),
        ('tech_009', '科技', '储能削峰填谷', 'renewable', 25, 30, 8, 'medium', '锂电池储能系统'),
        ('tech_010', '科技', '服务器虚拟化', 'process', 45, 10, 12, 'medium', '提高服务器利用率30%'),
        ('tech_011', '科技', '智能运维平台', 'process', 15, 8, 3, 'medium', 'AI驱动的能耗优化'),
        ('tech_012', '科技', '远程办公系统', 'process', 20, 5, 4, 'easy', '减少通勤碳排放'),
    ]
    
    cursor.executemany(
        'INSERT OR IGNORE INTO carbon_measures (id, industry, name, category, reduction_potential, investment_cost, annual_saving, difficulty, description) VALUES (?,?,?,?,?,?,?,?,?)',
        measures
    )
    print(f'种子数据: 已迁移 {len(measures)} 条措施')


def _seed_benchmarks(cursor):
    """将行业基准数据迁移到数据库（幂等）"""
    cursor.execute('SELECT COUNT(*) FROM industry_benchmarks')
    if cursor.fetchone()[0] > 0:
        return
    
    benchmarks = [
        ('制造业', 0.85, 0.55, 0.25),
        ('纺织业', 1.2, 0.8, 0.30),
        ('零售业', 0.35, 0.22, 0.20),
        ('科技', 0.25, 0.15, 0.35),
    ]
    cursor.executemany(
        'INSERT OR IGNORE INTO industry_benchmarks (industry, emission_intensity_avg, emission_intensity_advanced, reduction_potential) VALUES (?,?,?,?)',
        benchmarks
    )
    print(f'种子数据: 已迁移 {len(benchmarks)} 条行业基准')


def _seed_emission_factors(cursor):
    """将硬编码排放因子数据迁移到数据库（幂等）"""
    cursor.execute('SELECT COUNT(*) FROM emission_factors')
    if cursor.fetchone()[0] > 0:
        return

    factors = [
        # Scope 1: 直接排放
        ('natural_gas', 'm3', 2.09, '全国', 2022, 'GB/T 32150'),
        ('natural_gas', 'GJ', 56.84, '全国', 2022, 'GB/T 32150'),
        ('coal', 'kg', 2.52, '全国', 2022, 'GB/T 32150'),
        ('coal', 't', 2512, '全国', 2022, 'GB/T 32150'),
        ('gasoline', 'L', 2.30, '全国', 2022, 'GB/T 32150'),
        ('gasoline', 'kg', 3.10, '全国', 2022, 'GB/T 32150'),
        ('diesel', 'L', 2.63, '全国', 2022, 'GB/T 32150'),
        ('diesel', 'kg', 2.98, '全国', 2022, 'GB/T 32150'),
        # Scope 2: 外购电力（按地区）
        ('electricity', 'kWh', 0.581, '华北', 2022, '生态环境部2022'),
        ('electricity', 'kWh', 0.680, '东北', 2022, '生态环境部2022'),
        ('electricity', 'kWh', 0.581, '华东', 2022, '生态环境部2022'),
        ('electricity', 'kWh', 0.525, '华中', 2022, '生态环境部2022'),
        ('electricity', 'kWh', 0.475, '南方', 2022, '生态环境部2022'),
        ('electricity', 'kWh', 0.625, '西北', 2022, '生态环境部2022'),
        ('electricity', 'kWh', 0.581, '全国', 2022, '生态环境部2022'),
        # Scope 3: 可再生能源
        ('renewable', 'kWh', 0, '全国', 2022, '绿电认证'),
        ('renewable', 't', 0, '全国', 2022, '绿电认证'),
        # Scope 3: 商务差旅
        ('business_flight_short', 'km', 0.255, '全国', 2022, 'GHG Protocol'),
        ('business_flight_medium', 'km', 0.156, '全国', 2022, 'GHG Protocol'),
        ('business_flight_long', 'km', 0.195, '全国', 2022, 'GHG Protocol'),
        ('business_train', 'km', 0.041, '全国', 2022, 'GHG Protocol'),
        ('business_car', 'km', 0.171, '全国', 2022, 'GHG Protocol'),
        ('business_car', 'L', 2.30, '全国', 2022, 'GHG Protocol'),
        # Scope 3: 废物处理
        ('waste_landfill', 'kg', 0.45, '全国', 2022, 'IPCC 2019'),
        ('waste_landfill', 't', 450, '全国', 2022, 'IPCC 2019'),
        ('waste_incineration', 'kg', 0.38, '全国', 2022, 'IPCC 2019'),
        ('waste_incineration', 't', 380, '全国', 2022, 'IPCC 2019'),
        ('waste_composting', 'kg', 0.02, '全国', 2022, 'IPCC 2019'),
        ('waste_composting', 't', 20, '全国', 2022, 'IPCC 2019'),
        # Scope 3: 采购商品
        ('purchased_office', 'CNY', 0.0028, '全国', 2022, 'EEIO估算'),
        ('purchased_equipment', 'CNY', 0.0055, '全国', 2022, 'EEIO估算'),
    ]

    cursor.executemany(
        'INSERT OR IGNORE INTO emission_factors (emission_source, unit, factor, region, year, source) VALUES (?,?,?,?,?,?)',
        factors
    )
    print(f'种子数据: 已迁移 {len(factors)} 条排放因子')

if __name__ == "__main__":
    init_db()

def _seed_product_footprint_tables(cursor):
    pass  # Product footprint tables already created above
