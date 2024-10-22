"""Added missing fields to Conference

Revision ID: 9d27f6b5ce5e
Revises: 
Create Date: 2024-10-21 15:45:24.689229

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9d27f6b5ce5e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    # First, drop the foreign key constraint
    op.drop_constraint('conference_id_fkey', 'conference', type_='foreignkey')

    # Now drop the todos table
    op.drop_table('todos')

    with op.batch_alter_table('conference', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('marchandise', sa.String(length=50), nullable=True))
        batch_op.add_column(
            sa.Column('navire', sa.String(length=50), nullable=True))
        batch_op.add_column(
            sa.Column('poste', sa.String(length=50), nullable=True))
        batch_op.add_column(
            sa.Column('grue', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.alter_column('Date_debut_travail',
                              existing_type=postgresql.TIMESTAMP(),
                              type_=sa.Date(),
                              existing_nullable=True)
        batch_op.alter_column('Date_fin_travail',
                              existing_type=postgresql.TIMESTAMP(),
                              type_=sa.Date(),
                              existing_nullable=True)
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    with op.batch_alter_table('todo', schema=None) as batch_op:
        batch_op.drop_column('consignataire')
        batch_op.drop_column('observation')
        batch_op.drop_column('tonnage_manif')
        batch_op.drop_column('Heure_Terminaison_Travail_Prévue')
        batch_op.drop_column('materiel_a_bord')
        batch_op.drop_column('Date_debut_travail')
        batch_op.drop_column('tonnage_rest')
        batch_op.drop_column('pm')
        batch_op.drop_column('elevateur')
        batch_op.drop_column('receptionnaire')
        batch_op.drop_column('Date_fin_travail')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('todo', schema=None) as batch_op:
        batch_op.add_column(sa.Column(
            'Date_fin_travail', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('receptionnaire', sa.VARCHAR(
            length=50), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('elevateur', sa.VARCHAR(
            length=50), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('pm', sa.VARCHAR(
            length=50), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('tonnage_rest', sa.VARCHAR(
            length=50), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column(
            'Date_debut_travail', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('materiel_a_bord', sa.VARCHAR(
            length=50), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('Heure_Terminaison_Travail_Prévue',
                            postgresql.TIME(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('tonnage_manif', sa.VARCHAR(
            length=50), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('observation', sa.VARCHAR(
            length=255), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('consignataire', sa.VARCHAR(
            length=50), autoincrement=False, nullable=True))

    with op.batch_alter_table('conference', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(
            'conference_id_fkey', 'todos', ['id'], ['id'])
        batch_op.alter_column('Date_fin_travail',
                              existing_type=sa.Date(),
                              type_=postgresql.TIMESTAMP(),
                              existing_nullable=True)
        batch_op.alter_column('Date_debut_travail',
                              existing_type=sa.Date(),
                              type_=postgresql.TIMESTAMP(),
                              existing_nullable=True)
        batch_op.drop_column('user_id')
        batch_op.drop_column('grue')
        batch_op.drop_column('poste')
        batch_op.drop_column('navire')
        batch_op.drop_column('marchandise')

    op.create_table('todos',
                    sa.Column('id', sa.INTEGER(),
                              autoincrement=True, nullable=False),
                    sa.Column('content', sa.VARCHAR(length=200),
                              autoincrement=False, nullable=True),
                    sa.Column('shift', sa.VARCHAR(length=50),
                              autoincrement=False, nullable=True),
                    sa.Column('poste', sa.VARCHAR(length=50),
                              autoincrement=False, nullable=True),
                    sa.Column('navire', sa.VARCHAR(length=50),
                              autoincrement=False, nullable=True),
                    sa.Column('grue', sa.VARCHAR(length=50),
                              autoincrement=False, nullable=True),
                    sa.Column('marchandise', sa.VARCHAR(length=50),
                              autoincrement=False, nullable=True),
                    sa.Column('nb_cs_pcs', sa.VARCHAR(length=50),
                              autoincrement=False, nullable=True),
                    sa.Column('unite', sa.VARCHAR(length=50),
                              autoincrement=False, nullable=True),
                    sa.Column('raclage', sa.VARCHAR(length=50),
                              autoincrement=False, nullable=True),
                    sa.Column('comentaire', sa.VARCHAR(length=50),
                              autoincrement=False, nullable=True),
                    sa.Column('date_created', postgresql.TIMESTAMP(),
                              autoincrement=False, nullable=True),
                    sa.Column('user_id', sa.INTEGER(),
                              autoincrement=False, nullable=False),
                    sa.Column('is_validated', sa.BOOLEAN(),
                              autoincrement=False, nullable=True),
                    sa.Column('validated_by', sa.VARCHAR(length=150),
                              autoincrement=False, nullable=True),
                    sa.Column('status', sa.VARCHAR(length=50),
                              autoincrement=False, nullable=True),
                    sa.Column('remark', sa.VARCHAR(length=255),
                              autoincrement=False, nullable=True),
                    sa.Column('Escale', sa.VARCHAR(length=15),
                              autoincrement=False, nullable=True),
                    sa.Column('execution_time', sa.DOUBLE_PRECISION(
                        precision=53), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(
                        ['user_id'], ['user.id'], name='todos_user_id_fkey'),
                    sa.PrimaryKeyConstraint('id', name='todos_pkey')
                    )
    # ### end Alembic commands ###