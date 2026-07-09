"""Add financial_risk_score table

Revision ID: a1b2c3d4e5f6
Revises: 8b0e2560c749
Create Date: 2026-07-09 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '8b0e2560c749'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('financial_risk_score',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('loan_application_id', UUID(as_uuid=True), nullable=False),
        sa.Column('financial_score', sa.Numeric(precision=6, scale=4), nullable=False),
        sa.Column('industry_score', sa.Numeric(precision=6, scale=4), nullable=False),
        sa.Column('combined_score', sa.Numeric(precision=6, scale=4), nullable=False),
        sa.Column('risk_tier', sa.String(), nullable=False),
        sa.Column('matched_features', sa.JSON(), nullable=True),
        sa.Column('features_provided', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['loan_application_id'], ['loan_application.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('loan_application_id')
    )


def downgrade() -> None:
    op.drop_table('financial_risk_score')