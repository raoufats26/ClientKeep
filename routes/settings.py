from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import ActivityLog

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

CURRENCIES = [
    ('USD', 'US Dollar', '$'),
    ('EUR', 'Euro', '€'),
    ('GBP', 'British Pound', '£'),
    ('DZD', 'Algerian Dinar', 'DA'),
    ('MAD', 'Moroccan Dirham', 'MAD'),
    ('CAD', 'Canadian Dollar', 'CA$'),
    ('AUD', 'Australian Dollar', 'A$'),
    ('JPY', 'Japanese Yen', '¥'),
    ('INR', 'Indian Rupee', '₹'),
    ('BRL', 'Brazilian Real', 'R$'),
]


@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'profile':
            name  = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            currency = request.form.get('currency', 'USD')

            if not name or not email:
                flash('Name and email are required.', 'error')
            else:
                from models import User
                existing = User.query.filter(
                    User.email == email, User.id != current_user.id
                ).first()
                if existing:
                    flash('That email is already in use.', 'error')
                else:
                    current_user.name     = name
                    current_user.email    = email
                    current_user.currency = currency
                    db.session.add(ActivityLog(
                        user_id=current_user.id, action='Profile updated', icon='user'
                    ))
                    db.session.commit()
                    flash('Profile updated!', 'success')

        elif action == 'password':
            current_pw  = request.form.get('current_password', '')
            new_pw      = request.form.get('new_password', '')
            confirm_pw  = request.form.get('confirm_password', '')

            if not current_user.check_password(current_pw):
                flash('Current password is incorrect.', 'error')
            elif len(new_pw) < 8:
                flash('New password must be at least 8 characters.', 'error')
            elif new_pw != confirm_pw:
                flash('Passwords do not match.', 'error')
            else:
                current_user.set_password(new_pw)
                db.session.add(ActivityLog(
                    user_id=current_user.id, action='Password changed', icon='lock'
                ))
                db.session.commit()
                flash('Password changed successfully!', 'success')

        return redirect(url_for('settings.index'))

    return render_template('settings/index.html', currencies=CURRENCIES)
