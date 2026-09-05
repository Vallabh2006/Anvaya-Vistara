from flask import Blueprint, render_template, abort
from utils.auth_helpers import login_required, get_current_user
from utils.db import query_db

center_bp = Blueprint('center', __name__, url_prefix='/center', template_folder='../../templates/center')

def verify_access(user, center_id):
    if user['role'] not in ('region_admin', 'system_admin') and user.get('center_id') != center_id:
        abort(403)

@center_bp.route('/<center_id>/dashboard')
@login_required
def dashboard(center_id):
    user = get_current_user()
    verify_access(user, center_id)
    center = query_db('SELECT * FROM centers WHERE id = %s', (center_id,), one=True)
    if not center:
        abort(404)
    return render_template('dashboard.html', current_user=user, center=center)

@center_bp.route('/<center_id>/triage')
@login_required
def triage(center_id):
    user = get_current_user()
    verify_access(user, center_id)
    center = query_db('SELECT * FROM centers WHERE id = %s', (center_id,), one=True)
    return render_template('triage.html', current_user=user, center=center)

@center_bp.route('/<center_id>/referrals')
@login_required
def referrals(center_id):
    user = get_current_user()
    verify_access(user, center_id)
    center = query_db('SELECT * FROM centers WHERE id = %s', (center_id,), one=True)
    return render_template('referrals.html', current_user=user, center=center)

@center_bp.route('/<center_id>/patients')
@login_required
def patients(center_id):
    user = get_current_user()
    verify_access(user, center_id)
    center = query_db('SELECT * FROM centers WHERE id = %s', (center_id,), one=True)
    return render_template('patients.html', current_user=user, center=center)
