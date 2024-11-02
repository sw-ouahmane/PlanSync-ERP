from flask_login import login_required
from app.utils import get_active_sessions_count
from app.models import db, User, Todo
from app.models import Conference, ConferenceDetail
from flask import render_template, url_for, request, redirect, session, flash,  url_for, flash, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import calendar
import json
from datetime import datetime
from flask import Blueprint
from flask_login import login_required, current_user
from flask import send_file
from collections import defaultdict


bp = Blueprint('admin', __name__)


@bp.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))

    # Fetch user statistics
    total_users = User.query.count()  # Get total number of users
    pending_users = User.query.filter_by(
        is_admin=False, is_approved=False).all()
    normal_users = User.query.filter_by(is_admin=False, is_approved=True).all()
    admins = User.query.filter_by(is_admin=True).all()

    active_sessions = get_active_sessions_count()  # Get active sessions count

    # Get search parameter
    prenom = request.args.get('prenom', '')
    conferences = Conference.query.all()
    print(f"Conferences fetched: {conferences}")  # Debugging line

    # Get current page and set tasks per page
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Start with the base query
    query = Todo.query.join(User).filter(Todo.user_id == User.id)

    # Filter by prenom (from User model)
    if prenom:
        query = query.filter(User.prenom.ilike(f'%{prenom}%'))

    # Paginate the query
    tasks = query.paginate(page=page, per_page=per_page)

    return render_template('admin/admin.html',
                           total_users=total_users,
                           pending_users=pending_users,
                           normal_users=normal_users,
                           admins=admins,
                           conferences=conferences,
                           active_sessions=active_sessions,
                           tasks=tasks)


@bp.route('/delete_user/<int:id>')
@login_required
def delete_user(id):
    # Ensure that only admins can delete users
    if not current_user.is_admin:
        return redirect(url_for('main.index'))  # Redirect if not an admin

    user_to_delete = User.query.get_or_404(id)

    try:
        # Option 1: Delete all tasks associated with the user
        Todo.query.filter_by(user_id=id).delete()

        # Option 2: Reassign tasks to another user or set to null if allowed
        # Todo.query.filter_by(user_id=id).update({Todo.user_id: None})

        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect(url_for('admin.admin'))
    except Exception as e:
        return f'There was a problem deleting the user: {e}'


@bp.route('/delete_admin/<int:id>')
@login_required
def delete_admin(id):
    # Check if the current user is an admin
    if not current_user.is_admin:
        return redirect(url_for('main.index'))  # Redirect if not an admin

    # Fetch the admin to be deleted
    admin_user = User.query.get_or_404(id)

    # Check if the user to be deleted is an admin
    if not admin_user.is_admin:
        return 'The user is not an admin.'

    # Prevent deletion of the super admin
    if admin_user.is_super_admin:
        return 'You cannot delete the super admin.'

    # Proceed with deletion
    try:
        db.session.delete(admin_user)
        db.session.commit()
        return redirect(url_for('admin.admin'))
    except Exception as e:
        return f'There was a problem deleting the admin user: {e}'


@bp.route('/admin/change_password', methods=['GET', 'POST'])
@login_required
def admin_change_password():
    # Check if the current user is an admin
    if not current_user.is_admin:
        return redirect(url_for('main.index'))  # Redirect if not an admin

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Verify the current password
        if not check_password_hash(current_user.password, current_password):
            return 'Current password is incorrect.'

        # Check if new passwords match
        if new_password != confirm_password:
            return 'New passwords do not match.'

        # Hash the new password and update the user
        current_user.password = generate_password_hash(
            new_password, method='pbkdf2:sha256', salt_length=8
        )

        try:
            db.session.commit()  # Save the updated password to the database
            return 'Password changed successfully.'
        except Exception as e:
            return f'There was an issue changing your password: {e}'

    return render_template('admin/admin_change_password.html')


@bp.route('/admin/add_admin', methods=['GET', 'POST'])
@login_required
def add_admin():
    # Check if the current user is an admin and a super admin
    if not current_user.is_admin:
        return redirect(url_for('main.index'))  # Redirect if not an admin
    if not current_user.is_super_admin:
        return "You do not have permission to add a new admin."

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        shift = request.form['shift']
        prenom = request.form['prenom']
        matricule = request.form['matricule']
        fonction = request.form['fonction']
        password = request.form['password']
        hashed_password = generate_password_hash(
            password, method='pbkdf2:sha256', salt_length=8
        )

        # Check for existing user by username, email, or phone
        existing_user = User.query.filter(
            (User.username == username) |
            (User.email == email) |
            (User.phone == phone) |
            (User.matricule == matricule)
        ).first()

        if existing_user:
            return 'Username, email, or phone already exists. Please choose another.'

        # Create new admin
        new_admin = User(
            username=username,
            email=email,
            matricule=matricule,
            shift=shift,
            phone=phone,
            fonction=fonction,
            prenom=prenom,
            password=hashed_password,
            is_admin=True
        )

        try:
            db.session.add(new_admin)
            db.session.commit()
            return redirect(url_for('admin.admin'))
        except Exception as e:
            return f'There was an issue creating the admin: {e}'

    return render_template('admin/add_admin.html')


@bp.route('/admin/approve_user/<int:user_id>', methods=['POST'])
@login_required
def approve_user(user_id):
    if not current_user.is_admin:
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)

    if request.form['action'] == 'approve':
        # Assign the shift only if the user is approved
        shift = request.form.get('shift')
        if shift in ['A', 'B', 'C']:
            user.shift = shift
            user.is_approved = True
            user.is_pending = False  # Ensure the user is no longer pending
            db.session.commit()
            flash(
                f'User {user.username} approved and assigned to Shift {shift}.', 'success')
        else:
            flash('Invalid shift selection.', 'danger')

    elif request.form['action'] == 'reject':
        # If the user is rejected, remove them from the database
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} has been rejected.', 'info')

    # Redirect back to the pending users page
    return redirect(url_for('admin.view_pending_users'))


@bp.route('/view_admins')
def view_admins():
    admins = User.query.filter_by(is_admin=True).all()
    return render_template('admin/admin_list.html', admins=admins)


@bp.route('/view_pending_users')
@login_required
def view_pending_users():
    # Ensure query only gets pending, unapproved users
    pending_users = User.query.filter_by(
        is_admin=False, is_approved=False, is_pending=True).all()
    return render_template('admin/pending_users.html', pending_users=pending_users)


@bp.route('/view_normal_users', methods=['GET', 'POST'])
@login_required
def view_normal_users():
    search_query = request.args.get('search', '')  # Get search query from URL
    page = request.args.get('page', 1, type=int)  # Get the current page

    # Base query for normal users
    query = User.query.filter_by(is_admin=False, is_approved=True)

    # Apply search filter if query is present
    if search_query:
        query = query.filter(
            (User.username.ilike(f'%{search_query}%')) |
            (User.matricule.ilike(f'%{search_query}%'))
        )

    # Paginate the results
    pagination = query.paginate(page=page, per_page=10)

    # Pass both normal_users and pagination to the template
    return render_template(
        'admin/normal_users.html',
        normal_users=pagination.items,
        search_query=search_query,
        pagination=pagination
    )


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')


@bp.route('/load_conference', methods=['GET', 'POST'])
@login_required
def load_conference():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part. Please choose a file to upload.')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file. Please choose a file to upload.')
            return redirect(request.url)

        if file and file.filename.lower().endswith(('.xlsx', '.xls')):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            uploaded_files = session.get('uploaded_files', [])
            uploaded_files.append(
                {'filename': filename, 'filepath': file_path,
                    'upload_time': upload_time}
            )
            session['uploaded_files'] = uploaded_files

            flash('File successfully uploaded and processed.')
            return redirect(url_for('admin.load_conference'))

        flash(
            'Invalid file type. Please upload an Excel file with .xlsx or .xls extension.')

    uploaded_files = session.get('uploaded_files', [])
    return render_template('admin/load_conference.html', user=current_user, uploaded_files=uploaded_files)


@bp.route('/open_file/<filename>', methods=['GET'])
@login_required
def open_file(filename):
    # Construct the file path
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # Check if file exists
    if not os.path.exists(file_path):
        flash(f'File {filename} not found.')
        return redirect(url_for('admin.load_conference'))

    # Return the file for download
    try:
        return send_file(file_path)
    except Exception as e:
        flash(f'Error opening file: {str(e)}')
        return redirect(url_for('admin.load_conference'))


@bp.route('/conference_file', methods=['GET'])
@login_required
def conference_file():
    # Get the list of uploaded files from the session
    uploaded_files = session.get('uploaded_files', [])
    if not uploaded_files:
        flash('No uploaded conference files found.')

    # Render the 'conference.html' to list uploaded files
    return render_template('conference.html', user=current_user, uploaded_files=uploaded_files)


@bp.route('/download_conference/<filename>', methods=['GET'])
def download_conference(filename):
    # Construct the file path
    file_path = os.path.join(os.getcwd(), 'uploads', filename)

    # Check if the file exists
    if not os.path.exists(file_path):
        return "File not found", 404

    # Check the file extension and send the file as an attachment
    if filename.endswith('.xlsx') or filename.endswith('.xls'):
        try:
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            print(f"Error sending file: {e}")
            return "Error sending file", 500
    else:
        return "Unsupported file format", 400


@bp.route('/statistiques_admin')
@login_required
def statistiques_admin():
    # Get the selected filters from the form
    month_filter = request.args.get('month')
    year_filter = request.args.get('year')
    shift_filter = request.args.get('shift')
    Escale_filter = request.args.get('Escale')
    marchandise_filter = request.args.get('marchandise')
    grue_filter = request.args.get('grue')

    # Query all validated tasks
    query = Todo.query.filter_by(status='Validated')

    # Apply filters if selected
    if month_filter:
        query = query.filter(db.extract(
            'month', Todo.date_created) == month_filter)
    if year_filter:
        query = query.filter(db.extract(
            'year', Todo.date_created) == year_filter)
    if shift_filter:
        query = query.filter_by(shift=shift_filter)
    if Escale_filter:
        query = query.filter_by(Escale=Escale_filter)
    if marchandise_filter:
        query = query.filter_by(marchandise=marchandise_filter)
    if grue_filter:
        query = query.filter_by(grue=grue_filter)

    # Get all validated tasks based on filters
    validated_todos = query.all()

    # Dictionary to store count of validated tasks by month
    tasks_per_month = defaultdict(int)

    # Populate tasks_per_month with filtered data
    for todo in validated_todos:
        if todo.date_created:
            month = todo.date_created.month
            tasks_per_month[month] += 1

    # Sort and prepare data for display
    months = [calendar.month_name[i] for i in sorted(tasks_per_month)]
    task_counts = [tasks_per_month[i] for i in sorted(tasks_per_month)]

    # Fetch available years for year dropdown
    available_years = sorted(
        set(todo.date_created.year for todo in Todo.query.all()))

    # Fetch distinct values for the filters
    available_escales = sorted(
        set(todo.Escale for todo in Todo.query.all() if todo.Escale))
    available_marchandises = sorted(
        set(todo.marchandise for todo in Todo.query.all() if todo.marchandise))
    available_grues = sorted(
        set(todo.grue for todo in Todo.query.all() if todo.grue))

    # Pass month names and other data to the template
    return render_template('admin/admin_statistiques.html',
                           months=months,
                           task_counts=task_counts,
                           available_years=available_years,
                           available_escales=available_escales,
                           # Pass available Marchandise options
                           available_marchandises=available_marchandises,
                           available_grues=available_grues,  # Pass available Grue options
                           month_names=calendar.month_name,
                           stats=zip(months, task_counts))


@bp.route('/saisai_conference', methods=['GET', 'POST'])
def saisai_conference():
    if request.method == 'POST':
        try:
            # Retrieve form data for multiple lines
            postes = request.form.getlist('poste[]')
            pms = request.form.getlist('pm[]')
            shifts = request.form.getlist('shift[]')
            dates = request.form.getlist('Date[]')
            navires = request.form.getlist('navire[]')
            marchandises = request.form.getlist('marchandise[]')
            tonnages_manif = request.form.getlist('tonnage_manif[]')
            tonnages_rest = request.form.getlist('tonnage_rest[]')
            consignataires = request.form.getlist('consignataire[]')
            receptionnaires = request.form.getlist('receptionnaire[]')
            grues = request.form.getlist('grue[]')
            elevateurs = request.form.getlist('elevateur[]')
            materiels_a_bord = request.form.getlist('materiel_a_bord[]')
            dates_debut_travail = request.form.getlist('Date_debut_travail[]')
            dates_fin_travail = request.form.getlist('Date_fin_travail[]')
            heures_terminaison_travail_prevues = request.form.getlist(
                'Heure_Terminaison_Travail_Prévue[]')
            observations = request.form.getlist('observation[]')

            # Ensure we have consistent data lengths
            num_conferences = len(postes)
            if not all(len(lst) == num_conferences for lst in [
                pms, shifts, dates, navires, marchandises, tonnages_manif,
                tonnages_rest, consignataires, receptionnaires, grues,
                elevateurs, materiels_a_bord, dates_debut_travail,
                dates_fin_travail, heures_terminaison_travail_prevues,
                observations
            ]):
                flash(
                    'Inconsistent number of inputs for multiple conferences.', 'danger')
                return redirect(url_for('admin.saisai_conference'))

            # Create a new Conference object
            new_conference = Conference()

            # Loop through the number of conferences to create
            for i in range(num_conferences):
                # Parse date fields correctly
                date_entered = datetime.strptime(dates[i], '%Y-%m-%d').date()
                Date_debut_travail = datetime.strptime(
                    dates_debut_travail[i], '%Y-%m-%d').date()
                Date_fin_travail = datetime.strptime(
                    dates_fin_travail[i], '%Y-%m-%d').date()

                # Parse time if provided
                Heure_Terminaison_Travail_Prévue = None
                if heures_terminaison_travail_prevues[i]:
                    try:
                        Heure_Terminaison_Travail_Prévue = datetime.strptime(
                            heures_terminaison_travail_prevues[i], '%H:%M').time()
                    except ValueError:
                        flash(
                            f'Invalid time format for Heure Terminaison in row {i + 1}.', 'danger')
                        return redirect(url_for('admin.saisai_conference'))

                # Create a new ConferenceDetail object
                new_conference_detail = ConferenceDetail(
                    pm=pms[i],
                    marchandise=marchandises[i],
                    navire=navires[i],
                    Date=date_entered,
                    shift=shifts[i],
                    poste=postes[i],
                    grue=grues[i],
                    tonnage_manif=tonnages_manif[i],
                    tonnage_rest=tonnages_rest[i],
                    consignataire=consignataires[i],
                    receptionnaire=receptionnaires[i],
                    elevateur=elevateurs[i],
                    materiel_a_bord=materiels_a_bord[i],
                    Date_debut_travail=Date_debut_travail,
                    Date_fin_travail=Date_fin_travail,
                    Heure_Terminaison_Travail_Prévue=Heure_Terminaison_Travail_Prévue,
                    observation=observations[i]
                )

                # Associate the detail with the conference
                new_conference.details.append(new_conference_detail)

            # Save the conference with its details to the database
            db.session.add(new_conference)
            db.session.commit()

            flash(f'{num_conferences} Conferences added successfully!', 'success')
            return redirect(url_for('admin.saisai_conference'))

        except Exception as e:
            # Log the full exception for debugging
            flash(f'An error occurred: {e}', 'danger')
            return redirect(url_for('admin.saisai_conference'))

    # If it's a GET request, display the form
    return render_template('admin/saisai_conference.html')


@bp.route('/conference1/<int:id>', methods=['GET', 'POST'])
def conference1(id):
    conferencee = Conference.query.get(id)

    if not conferencee:
        return 'Conference not found.', 404

    if request.method == 'POST':
        # Process form data for updating the conference
        poste = request.form.getlist('poste[]')
        pm = request.form.getlist('pm[]')
        shift = request.form.getlist('shift[]')
        date = request.form.getlist('Date[]')
        navire = request.form.getlist('navire[]')
        marchandise = request.form.getlist('marchandise[]')
        tonnage_manif = request.form.getlist('tonnage_manif[]')
        tonnage_rest = request.form.getlist('tonnage_rest[]')
        consignataire = request.form.getlist('consignataire[]')
        receptionnaire = request.form.getlist('receptionnaire[]')
        grue = request.form.getlist('grue[]')
        elevateur = request.form.getlist('elevateur[]')
        materiel_a_bord = request.form.getlist('materiel_a_bord[]')
        date_debut_travail = request.form.getlist('Date_debut_travail[]')
        date_fin_travail = request.form.getlist('Date_fin_travail[]')
        heure_terminaison_travail = request.form.getlist(
            'Heure_Terminaison_Travail_Prévue[]')
        observation = request.form.getlist('observation[]')

        # Validate required fields
        if not all([poste, pm, navire, tonnage_manif, shift, date, tonnage_rest, consignataire, receptionnaire, grue, elevateur, materiel_a_bord, date_debut_travail, date_fin_travail, heure_terminaison_travail, observation]):
            flash('All fields are required.', 'error')
            return redirect(request.url)

        # Update the existing conference object with the new data
        conferencee.pm = pm[0]
        conferencee.shift = shift[0]
        conferencee.Date = date
        conferencee.navire = navire[0]
        conferencee.marchandise = marchandise[0]
        conferencee.tonnage_manif = tonnage_manif[0]
        conferencee.tonnage_rest = tonnage_rest[0]
        conferencee.consignataire = consignataire[0]
        conferencee.receptionnaire = receptionnaire[0]
        conferencee.grue = grue[0]
        conferencee.elevateur = elevateur[0]
        conferencee.materiel_a_bord = materiel_a_bord[0]
        conferencee.Date_debut_travail = datetime.strptime(
            date_debut_travail[0], '%Y-%m-%d')
        conferencee.Date_fin_travail = datetime.strptime(
            date_fin_travail[0], '%Y-%m-%d')
        conferencee.Heure_Terminaison_Travail_Prévue = datetime.strptime(
            heure_terminaison_travail[0], '%H:%M').time() if heure_terminaison_travail else None
        conferencee.observation = observation[0]

        # Update the details for each ConferenceDetail
        for detail_id, post in zip(request.form.getlist('detail_id[]'), poste):
            detail = ConferenceDetail.query.get(detail_id)
            if detail:
                detail.shift = shift[0]
                detail.date = date
                detail.poste = post
                detail.pm = pm[0]
                detail.navire = navire[0]
                detail.marchandise = marchandise[0]
                detail.tonnage_manif = tonnage_manif[0]
                detail.tonnage_rest = tonnage_rest[0]
                detail.consignataire = consignataire[0]
                detail.receptionnaire = receptionnaire[0]
                detail.grue = grue[0]
                detail.elevateur = elevateur[0]
                detail.materiel_a_bord = materiel_a_bord[0]
                detail.Date_debut_travail = datetime.strptime(
                    date_debut_travail[0], '%Y-%m-%d')
                detail.Date_fin_travail = datetime.strptime(
                    date_fin_travail[0], '%Y-%m-%d')
                detail.Heure_Terminaison_Travail_Prévue = datetime.strptime(
                    heure_terminaison_travail[0], '%H:%M').time() if heure_terminaison_travail else None
                detail.observation = observation[0]

        try:
            db.session.commit()
            flash('Conference updated successfully!', 'success')
            return redirect(url_for('admin.conference1', id=conferencee.id))
        except Exception as e:
            flash(f'There was an issue updating the conference: {e}', 'error')
            return redirect(request.url)

    # Get ConferenceDetails for the conference
    details = conferencee.details.all()  # Fetch all details for the conference

    return render_template('admin/get_conferences.html', conferencee=conferencee, details=details)


@bp.route('/all_conferences')
@login_required
def all_conferences():
    # Query all conferences from the database
    # Ensure you have the Conference model imported
    conferences = Conference.query.all()
    return render_template('admin/all_conferences.html', conferences=conferences)


@bp.route('/delete_conference/<int:id>', methods=['POST'])
@login_required
def delete_conference(id):
    conference = Conference.query.get(id)
    if conference:
        # Delete related ConferenceDetail entries
        ConferenceDetail.query.filter_by(conference_id=id).delete()

        # Now delete the Conference
        db.session.delete(conference)
        db.session.commit()

    return redirect(url_for('admin.all_conferences'))


@bp.route('/edit_conference/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_conference(id):
    # Retrieve the conference to edit
    conference = Conference.query.get(id)

    if not conference:
        flash('Conference not found.', 'error')
        return redirect(url_for('admin.all_conferences'))

    # Handle form submission
    if request.method == 'POST':
        # Retrieve form data
        poste = request.form.getlist('poste[]')
        pm = request.form.getlist('pm[]')
        shift = request.form.getlist('shift[]')
        date = request.form.getlist('Date[]')
        navire = request.form.getlist('navire[]')
        marchandise = request.form.getlist('marchandise[]')
        tonnage_manif = request.form.getlist('tonnage_manif[]')
        tonnage_rest = request.form.getlist('tonnage_rest[]')
        consignataire = request.form.getlist('consignataire[]')
        receptionnaire = request.form.getlist('receptionnaire[]')
        grue = request.form.getlist('grue[]')
        elevateur = request.form.getlist('elevateur[]')
        materiel_a_bord = request.form.getlist('materiel_a_bord[]')
        date_debut_travail = request.form.getlist('Date_debut_travail[]')
        date_fin_travail = request.form.getlist('Date_fin_travail[]')
        heure_terminaison_travail = request.form.getlist(
            'Heure_Terminaison_Travail_Prévue[]')
        observation = request.form.getlist('observation[]')

        # Check for required fields before accessing the first element
        if not poste or not pm or not navire or not tonnage_manif or not shift or not date or not tonnage_rest or not consignataire or not receptionnaire or not grue or not elevateur or not materiel_a_bord or not date_debut_travail or not date_fin_travail or not heure_terminaison_travail or not observation:
            flash('All fields are required.', 'error')
            return redirect(request.url)

        # Update the conference object with the new data
        conference.pm = pm[0] if pm else None
        conference.shift = shift[0] if shift else None
        conference.Date = date[0] if date else None
        conference.navire = navire[0] if navire else None
        conference.marchandise = marchandise[0] if marchandise else None
        conference.tonnage_manif = tonnage_manif[0] if tonnage_manif else None
        conference.tonnage_rest = tonnage_rest[0] if tonnage_rest else None
        conference.consignataire = consignataire[0] if consignataire else None
        conference.receptionnaire = receptionnaire[0] if receptionnaire else None
        conference.grue = grue[0] if grue else None
        conference.elevateur = elevateur[0] if elevateur else None
        conference.materiel_a_bord = materiel_a_bord[0] if materiel_a_bord else None
        conference.Date_debut_travail = datetime.strptime(
            date_debut_travail[0], '%Y-%m-%d') if date_debut_travail else None
        conference.Date_fin_travail = datetime.strptime(
            date_fin_travail[0], '%Y-%m-%d') if date_fin_travail else None
        conference.Heure_Terminaison_Travail_Prévue = datetime.strptime(
            heure_terminaison_travail[0], '%H:%M').time() if heure_terminaison_travail else None
        conference.observation = observation[0] if observation else None

        # Update the details for each ConferenceDetail
        for detail_id, post in zip(request.form.getlist('detail_id[]'), poste):
            detail = ConferenceDetail.query.get(detail_id)
            if detail:
                detail.shift = shift[0] if shift else None
                detail.date = date[0] if date else None
                detail.poste = post
                detail.pm = pm[0] if pm else None
                detail.navire = navire[0] if navire else None
                detail.marchandise = marchandise[0] if marchandise else None
                detail.tonnage_manif = tonnage_manif[0] if tonnage_manif else None
                detail.tonnage_rest = tonnage_rest[0] if tonnage_rest else None
                detail.consignataire = consignataire[0] if consignataire else None
                detail.receptionnaire = receptionnaire[0] if receptionnaire else None
                detail.grue = grue[0] if grue else None
                detail.elevateur = elevateur[0] if elevateur else None
                detail.materiel_a_bord = materiel_a_bord[0] if materiel_a_bord else None
                detail.Date_debut_travail = datetime.strptime(
                    date_debut_travail[0], '%Y-%m-%d') if date_debut_travail else None
                detail.Date_fin_travail = datetime.strptime(
                    date_fin_travail[0], '%Y-%m-%d') if date_fin_travail else None
                detail.Heure_Terminaison_Travail_Prévue = datetime.strptime(
                    heure_terminaison_travail[0], '%H:%M').time() if heure_terminaison_travail else None
                detail.observation = observation[0] if observation else None

        try:
            db.session.commit()
            flash('Conference updated successfully!', 'success')
            return redirect(url_for('admin.all_conferences'))
        except Exception as e:
            db.session.rollback()
            flash(f'There was an issue updating the conference: {e}', 'error')
            return redirect(request.url)

    # For GET requests, retrieve details and render the edit form
    details = conference.details.all()
    return render_template('admin/edit_conference.html', conference=conference, details=details)


@bp.route('/get_file_path/<path:filename>', methods=['GET'])
@login_required
def get_file_path(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    print("Checking for file at:", file_path)  # Debugging line

    if os.path.exists(file_path):
        return f'The absolute path for the uploaded file is: {file_path}'
    else:
        return 'File not found.', 404
