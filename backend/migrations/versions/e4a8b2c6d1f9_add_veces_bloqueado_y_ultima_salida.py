"""add veces_bloqueado y ultima_salida a usuario

Revision ID: e4a8b2c6d1f9
Revises: b2c65c717ae6
Create Date: 2026-04-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'e4a8b2c6d1f9'
down_revision = 'b2c65c717ae6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('usuario', sa.Column('veces_bloqueado', sa.SmallInteger(), nullable=False, server_default='0'))
    op.add_column('usuario', sa.Column('ultima_salida', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('usuario', 'ultima_salida')
    op.drop_column('usuario', 'veces_bloqueado')
