"""Adding configuration

Revision ID: 65c772c97f6b
Revises: b14cde567cc8
Create Date: 2024-04-14 14:25:40.160692

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65c772c97f6b'
down_revision = 'b14cde567cc8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('configuration',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('max_plant_output', sa.Float(), nullable=True),
    sa.Column('penalty', sa.Float(), nullable=True),
    sa.Column('sale_value', sa.Float(), nullable=True),
    sa.Column('max_sale_output', sa.Float(), nullable=True),
    sa.Column('battery_capacity', sa.Float(), nullable=True),
    sa.Column('batter_discharge_rate', sa.Float(), nullable=True),
    sa.Column('battery_charge_rate', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('configuration')
