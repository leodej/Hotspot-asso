# app.py

# Placeholder for the rest of the code
def credits():
    base_query = "SELECT * FROM users_credits uc"
    params = []

    # Aplicar filtro de mês
    if month_filter:
        base_query += ' AND strftime("%Y-%m", uc.created_at) = ?'
        params.append(month_filter)

    base_query += ' ORDER BY uc.updated_at DESC'

    # Placeholder for the rest of the code
    pass
