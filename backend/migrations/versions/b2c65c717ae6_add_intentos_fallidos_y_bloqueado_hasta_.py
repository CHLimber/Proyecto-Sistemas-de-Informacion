"""add intentos_fallidos y bloqueado_hasta a usuario

Revision ID: b2c65c717ae6
Revises:
Create Date: 2026-04-13 19:52:06.680130

"""
from alembic import op
import sqlalchemy as sa

revision = 'b2c65c717ae6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('usuario', sa.Column('intentos_fallidos', sa.SmallInteger(), nullable=False, server_default='0'))
    op.add_column('usuario', sa.Column('bloqueado_hasta', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('usuario', 'bloqueado_hasta')
    op.drop_column('usuario', 'intentos_fallidos')
