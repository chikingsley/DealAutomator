"""initial migration

Revision ID: initial_migration
Revises: 
Create Date: 2024-01-20

"""
from alembic import op
import sqlalchemy as sa

revision = 'initial_migration'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create message_processing table
    op.create_table(
        'message_processing',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_message_id', sa.String(), nullable=True),
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('attempts', sa.Integer(), default=0),
        sa.Column('partner_name', sa.String(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create parsed_deals table
    op.create_table(
        'parsed_deals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=True),
        sa.Column('geo', sa.String(length=2), nullable=True),
        sa.Column('language_code', sa.String(length=5), nullable=True),
        sa.Column('is_native', sa.Boolean(), nullable=True),
        sa.Column('pricing_model', sa.String(length=3), nullable=True),
        sa.Column('cpa_amount', sa.DECIMAL(), nullable=True),
        sa.Column('crg_percentage', sa.DECIMAL(), nullable=True),
        sa.Column('cpl_amount', sa.DECIMAL(), nullable=True),
        sa.Column('deduction_limit', sa.Text(), nullable=True),
        sa.Column('conversion_rate', sa.Text(), nullable=True),
        sa.Column('conversion_current', sa.Text(), nullable=True),
        sa.Column('conversion_details', sa.Text(), nullable=True),
        sa.Column('sources', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('funnels', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('notion_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['message_id'], ['message_processing.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_message_processing_status', 'message_processing', ['status'])
    op.create_index('idx_parsed_deals_geo', 'parsed_deals', ['geo'])
    op.create_index('idx_parsed_deals_created_at', 'parsed_deals', ['created_at'])

def downgrade():
    op.drop_index('idx_parsed_deals_created_at')
    op.drop_index('idx_parsed_deals_geo')
    op.drop_index('idx_message_processing_status')
    op.drop_table('parsed_deals')
    op.drop_table('message_processing')
