import os


class Config:
    SECRET_KEY = os.environ.get(
        'f9b7e53d705071997a5da4d1b8513479') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # or \ 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Set the upload folder path
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')


# postgresql://plansync_erp_l4ay_user:zL0sbPgekwRt7zxBZDnjXYIaQImXkvpw@dpg-cs1ejq88fa8c73d01r9g-a.oregon-postgres.render.com/plansync_erp_l4ay
# postgresql://plansync_erp_l4ay_user:zL0sbPgekwRt7zxBZDnjXYIaQImXkvpw@dpg-cs1ejq88fa8c73d01r9g-a.oregon-postgres.render.com/plansync_erp_l4ay

SQLALCHEMY_DATABASE_URI = 'postgresql: // plansync_erp_l4ay_user: zL0sbPgekwRt7zxBZDnjXYIaQImXkvpw@dpg-cs1ejq88fa8c73d01r9g-a.oregon-postgres.render.com/plansync_erp_l4ay'


# postgresql://plansync_erp_l4ay_user:zL0sbPgekwRt7zxBZDnjXYIaQImXkvpw@dpg-cs1ejq88fa8c73d01r9g-a.oregon-postgres.render.com/plansync_erp_l4ay


# postgresql://plansync_erp_l4ay_user:zL0sbPgekwRt7zxBZDnjXYIaQImXkvpw@dpg-cs1ejq88fa8c73d01r9g-a.oregon-postgres.render.com/plansync_erp_l4ay

# set DATABASE_URL=postgresql://plansync_erp_l4ay_user:zL0sbPgekwRt7zxBZDnjXYIaQImXkvpw@dpg-cs1ejq88fa8c73d01r9g-a.oregon-postgres.render.com/plansync_erp_l4ay?sslmode=require
