from utils.db import query_db, execute_db

ALLOWED_TABLES = {'patients', 'facilities', 'vehicles', 'users', 'centers'}

def _next_seq(table, prefix_pattern):
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table name for ID generation: {table}")
    row = query_db(
        f"SELECT COUNT(*) as cnt FROM {table} WHERE id LIKE %s",
        (prefix_pattern + '%',),
        one=True
    )
    return (row['cnt'] if row else 0) + 1


def generate_patient_id(state, facility_code):
    prefix = f"PT-{state}-{facility_code}"
    seq = _next_seq('patients', prefix)
    return f"{prefix}-{seq:04d}"


def generate_facility_id(fac_type, region):
    type_code = fac_type[:3].upper()
    region_code = region[:3].upper()
    prefix = f"FC-{type_code}-{region_code}"
    seq = _next_seq('facilities', prefix)
    return f"{prefix}-{seq:04d}"


def generate_staff_id(role, facility_code):
    role_code = role[:3].upper()
    prefix = f"ST-{role_code}-{facility_code}"
    row = query_db(
        "SELECT COUNT(*) as cnt FROM users WHERE staff_id LIKE %s",
        (prefix + '%',),
        one=True
    )
    seq = (row['cnt'] if row else 0) + 1
    return f"{prefix}-{seq:04d}"


def generate_vehicle_id(region):
    region_code = region[:3].upper()
    prefix = f"VH-{region_code}"
    seq = _next_seq('vehicles', prefix)
    return f"{prefix}-{seq:04d}"
