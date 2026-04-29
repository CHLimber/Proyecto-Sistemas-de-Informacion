"""add_bitacora_sistema

Revision ID: bd9a37863492
Revises: e4a8b2c6d1f9
Create Date: 2026-04-29 12:38:26.383305

"""
from alembic import op
import sqlalchemy as sa

revision = 'bd9a37863492'
down_revision = 'e4a8b2c6d1f9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('bitacora',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_usuario', sa.Integer(), nullable=True),
        sa.Column('accion', sa.String(length=50), nullable=False),
        sa.Column('modulo', sa.String(length=50), nullable=True),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('ip', sa.String(length=45), nullable=True),
        sa.Column('fecha', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id'], name='fk_bitacora_usuario'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('bitacora', schema=None) as batch_op:
        batch_op.create_index('ix_bitacora_accion', ['accion'], unique=False)
        batch_op.create_index('ix_bitacora_fecha', ['fecha'], unique=False)
        batch_op.create_index('ix_bitacora_id_usuario', ['id_usuario'], unique=False)
        batch_op.create_index('ix_bitacora_modulo', ['modulo'], unique=False)

    op.create_table('bitacora_detalle',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_bitacora', sa.Integer(), nullable=False),
        sa.Column('campo', sa.String(length=100), nullable=False),
        sa.Column('valor_anterior', sa.Text(), nullable=True),
        sa.Column('valor_nuevo', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['id_bitacora'], ['bitacora.id'], name='fk_bitdet_bitacora', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('bitacora_detalle')
    with op.batch_alter_table('bitacora', schema=None) as batch_op:
        batch_op.drop_index('ix_bitacora_modulo')
        batch_op.drop_index('ix_bitacora_id_usuario')
        batch_op.drop_index('ix_bitacora_fecha')
        batch_op.drop_index('ix_bitacora_accion')
    op.drop_table('bitacora')
