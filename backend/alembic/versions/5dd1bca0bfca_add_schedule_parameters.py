"""add_schedule_parameters

Revision ID: 5dd1bca0bfca
Revises: b7576b9fcbf2
Create Date: 2025-11-30 01:45:33.341317

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5dd1bca0bfca'
down_revision: Union[str, None] = 'b7576b9fcbf2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('monthly_schedules', sa.Column('params_total_shifts', sa.Integer(), server_default='18', nullable=False))
    op.add_column('monthly_schedules', sa.Column('params_night_shifts', sa.Integer(), server_default='2', nullable=False))
    op.add_column('monthly_schedules', sa.Column('params_max_consecutive_days_off', sa.Integer(), server_default='3', nullable=False))
    op.add_column('monthly_schedules', sa.Column('params_max_consecutive_work_days', sa.Integer(), server_default='6', nullable=False))
    op.add_column('monthly_schedules', sa.Column('params_unavailability_weight', sa.Integer(), server_default='1', nullable=False))
    op.add_column('monthly_schedules', sa.Column('params_post_night_shift_off', sa.Boolean(), server_default='1', nullable=False))


def downgrade() -> None:
    op.drop_column('monthly_schedules', 'params_post_night_shift_off')
    op.drop_column('monthly_schedules', 'params_unavailability_weight')
    op.drop_column('monthly_schedules', 'params_max_consecutive_work_days')
    op.drop_column('monthly_schedules', 'params_max_consecutive_days_off')
    op.drop_column('monthly_schedules', 'params_night_shifts')
    op.drop_column('monthly_schedules', 'params_total_shifts')
