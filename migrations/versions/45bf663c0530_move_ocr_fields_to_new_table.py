"""move_ocr_fields_to_new_table

Revision ID: 45bf663c0530
Revises: 6748a9d541e5
Create Date: 2024-12-16 10:18:20.931236

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "45bf663c0530"
down_revision: Union[str, None] = "6748a9d541e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ocr_results table
    op.create_table(
        "ocr_results",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("scan_id", sa.Integer(), nullable=False),
        sa.Column("ocr_source", sa.String(length=50), nullable=True),
        sa.Column("llm_source", sa.String(length=50), nullable=True),
        sa.Column("error_message", sa.String(length=255), nullable=True),
        sa.Column("ocr_text", sa.Text(), nullable=True),
        sa.Column("ocr_text_cleaned", sa.Text(), nullable=True),
        sa.Column("processing_time", sa.Float(), nullable=True),
        sa.Column("statement_date", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["scan_id"],
            ["scans.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scan_id"),
    )
    op.create_index("ix_ocr_results_scan_id", "ocr_results", ["scan_id"])

    # Copy data from scans to ocr_results
    op.execute("""
        INSERT INTO ocr_results (
            scan_id, ocr_source, llm_source, error_message, 
            ocr_text, ocr_text_cleaned, processing_time,
            statement_date, created_at, updated_at
        )
        SELECT 
            id, ocr_source, llm_source, error_message,
            ocr_text, ocr_text_cleaned, processing_time,
            statement_date, created_at, updated_at
        FROM scans
        WHERE ocr_source IS NOT NULL 
           OR llm_source IS NOT NULL 
           OR error_message IS NOT NULL 
           OR ocr_text IS NOT NULL 
           OR ocr_text_cleaned IS NOT NULL 
           OR processing_time IS NOT NULL
           OR statement_date IS NOT NULL
    """)

    # Drop columns from scans table
    op.drop_column("scans", "processing_time")
    op.drop_column("scans", "ocr_text_cleaned")
    op.drop_column("scans", "ocr_text")
    op.drop_column("scans", "error_message")
    op.drop_column("scans", "llm_source")
    op.drop_column("scans", "ocr_source")
    op.drop_column("scans", "statement_date")
    op.drop_column("scans", "uploaded_file")


def downgrade() -> None:
    # Add columns back to scans table
    op.add_column(
        "scans", sa.Column("ocr_source", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "scans", sa.Column("llm_source", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "scans", sa.Column("error_message", sa.String(length=255), nullable=True)
    )
    op.add_column("scans", sa.Column("ocr_text", sa.Text(), nullable=True))
    op.add_column("scans", sa.Column("ocr_text_cleaned", sa.Text(), nullable=True))
    op.add_column("scans", sa.Column("processing_time", sa.Float(), nullable=True))
    op.add_column(
        "scans", sa.Column("statement_date", sa.BigInteger(), nullable=True)
    )

    # Copy data back from ocr_results to scans
    op.execute("""
        UPDATE scans s
        SET 
            ocr_source = o.ocr_source,
            llm_source = o.llm_source,
            error_message = o.error_message,
            ocr_text = o.ocr_text,
            ocr_text_cleaned = o.ocr_text_cleaned,
            processing_time = o.processing_time,
            statement_date = o.statement_date
        FROM ocr_results o
        WHERE s.id = o.scan_id
    """)

    # Drop ocr_results table and its index
    op.drop_index("ix_ocr_results_scan_id", "ocr_results")
    op.drop_table("ocr_results")
