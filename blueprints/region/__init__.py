

from flask import Blueprint, render_template
from utils.auth_helpers import role_required, get_current_user

region_bp = Blueprint('region', __name__, url_prefix='/region', template_folder='../../templates/region')


@region_bp.route('/dashboard')
@role_required('region_admin')
def dashboard():
    user = get_current_user()
    return render_template('dashboard.html', current_user=user)


@region_bp.route('/referrals')
@role_required('region_admin')
def referrals():
    user = get_current_user()
    return render_template('referrals.html', current_user=user)


@region_bp.route('/admissions')
@role_required('region_admin')
def admissions():
    user = get_current_user()
    return render_template('admissions.html', current_user=user)


@region_bp.route('/discharges')
@role_required('region_admin')
def discharges():
    user = get_current_user()
    return render_template('discharges.html', current_user=user)


@region_bp.route('/counter-referrals')
@role_required('region_admin')
def counter_referrals():
    user = get_current_user()
    return render_template('counter_referrals.html', current_user=user)
