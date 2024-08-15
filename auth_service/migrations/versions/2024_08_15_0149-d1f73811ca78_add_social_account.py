"""add_social_account

Revision ID: d1f73811ca78
Revises: 2031320bc013
Create Date: 2024-08-15 01:49:48.135128

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'd1f73811ca78'
down_revision: Union[str, None] = '2031320bc013'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'social_account',
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('social_id', sa.String(), nullable=False),
        sa.Column('social_name', sa.String(), nullable=False),
        sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_by', sa.TEXT(), nullable=True),
        sa.Column(
            'created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False
        ),
        sa.Column('updated_by', sa.TEXT(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('social_id', 'social_name', name='social_pk'),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('social_account')
    # ### end Alembic commands ###
