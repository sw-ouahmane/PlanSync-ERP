from flask_login import login_required
from app.models import db, X
from app.models import Conference
from flask import render_template, url_for, request, redirect, session, flash,  url_for, flash, session, send_file
from werkzeug.utils import secure_filename

from flask import Blueprint
from flask_login import login_required, current_user


bp = Blueprint('test', __name__)


@bp.route('/add_tablex', methods=['GET', 'POST'])
@login_required
def add_tablex():
    if request.method == 'POST':
        # Retrieve multiple values for columns 'a' and 'b' as lists
        a_values = request.form.getlist('a')
        b_values = request.form.getlist('b')

        # Iterate through the values and add them to the database
        for a, b in zip(a_values, b_values):
            new_row = X(a=a, b=b)
            db.session.add(new_row)

        # Commit all changes at once
        db.session.commit()

        # Redirect after submission
        return redirect(url_for('admin.admin'))

    # For GET request, render the form
    return render_template('tabletest/add_table.html')


@bp.route('/get_tablex')
@login_required
def get_tablex():
    # Query all rows from the 'X' table
    rows = X.query.all()

    # Pass the rows to the template
    return render_template('tabletest/get_table.html', rows=rows)
