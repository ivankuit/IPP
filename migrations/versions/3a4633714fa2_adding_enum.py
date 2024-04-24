"""adding enum

Revision ID: 3a4633714fa2
Revises: 777c6a32a573
Create Date: 2024-04-15 18:56:57.128369

"""
from alembic import op
import sqlalchemy as sa


revision = '3a4633714fa2'
down_revision = '777c6a32a573'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('tag', schema=None) as batch_op:
        batch_op.add_column(sa.Column('type', sa.Enum('prediction', 'actual', name='tagtypeenum'), nullable=True))



def downgrade():
    with op.batch_alter_table('tag', schema=None) as batch_op:
        batch_op.drop_column('type')

