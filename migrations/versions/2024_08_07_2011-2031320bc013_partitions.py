from typing import Sequence, Union
from alembic import op
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = '2031320bc013'
down_revision: Union[str, None] = 'f366b824f054'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем временную партиционированную таблицу
    op.execute(
        text(
            '''
            CREATE TABLE IF NOT EXISTS history_new (
                id UUID NOT NULL DEFAULT gen_random_uuid(),
                created_by TEXT,
                created_at TIMESTAMPTZ DEFAULT current_timestamp NOT NULL,
                updated_by TEXT,
                updated_at TIMESTAMPTZ,
                user_agent TEXT NOT NULL,
                login_type TEXT NOT NULL,
                session_id UUID NOT NULL,
                auth_date TIMESTAMPTZ NOT NULL,
                user_id UUID NOT NULL,
                PRIMARY KEY (id, auth_date),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) PARTITION BY RANGE (auth_date);
            '''
        )
    )

    # Создаем все необходимые партиции для существующих данных и будущих данных до августа 2025 года
    partitions = [
        ("2024-01-01", "2024-02-01"),
        ("2024-02-01", "2024-03-01"),
        ("2024-03-01", "2024-04-01"),
        ("2024-04-01", "2024-05-01"),
        ("2024-05-01", "2024-06-01"),
        ("2024-06-01", "2024-07-01"),
        ("2024-07-01", "2024-08-01"),
        ("2024-08-01", "2024-09-01"),
        ("2024-09-01", "2024-10-01"),
        ("2024-10-01", "2024-11-01"),
        ("2024-11-01", "2024-12-01"),
        ("2024-12-01", "2025-01-01"),
        ("2025-01-01", "2025-02-01"),
        ("2025-02-01", "2025-03-01"),
        ("2025-03-01", "2025-04-01"),
        ("2025-04-01", "2025-05-01"),
        ("2025-05-01", "2025-06-01"),
        ("2025-06-01", "2025-07-01"),
        ("2025-07-01", "2025-08-01")
    ]

    for start_date, end_date in partitions:
        op.execute(
            text(
                f"""CREATE TABLE IF NOT EXISTS "history_{start_date[:4]}_{start_date[5:7]}" PARTITION OF "history_new" 
                FOR VALUES FROM ('{start_date}') TO ('{end_date}')"""
            )
        )

    # Перемещаем данные из старой таблицы в новую
    op.execute(
        text(
            '''
            INSERT INTO history_new (id, created_by, created_at, updated_by, updated_at, user_agent, login_type, session_id, auth_date, user_id)
            SELECT id, created_by, created_at, updated_by, updated_at, user_agent, login_type, session_id, auth_date, user_id
            FROM history;
            '''
        )
    )

    # Переименовываем старую таблицу и новую таблицу
    op.execute("ALTER TABLE history RENAME TO history_old;")
    op.execute("ALTER TABLE history_new RENAME TO history;")

    # Удаляем старую таблицу
    op.execute("DROP TABLE IF EXISTS history_old;")

def downgrade() -> None:
    # Создаем временную таблицу для отката
    op.execute(
        text(
            '''
            CREATE TABLE IF NOT EXISTS history_old (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                created_by TEXT,
                created_at TIMESTAMPTZ DEFAULT current_timestamp,
                updated_by TEXT,
                updated_at TIMESTAMPTZ,
                user_agent TEXT NOT NULL,
                login_type TEXT NOT NULL,
                session_id UUID NOT NULL,
                auth_date TIMESTAMPTZ NOT NULL,
                user_id UUID NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            '''
        )
    )

    # Перемещение данных из партиционированной таблицы обратно в обычную таблицу
    op.execute(
        text(
            '''
            INSERT INTO history_old (id, created_by, created_at, updated_by, updated_at, user_agent, login_type, session_id, auth_date, user_id)
            SELECT id, created_by, created_at, updated_by, updated_at, user_agent, login_type, session_id, auth_date, user_id
            FROM history;
            '''
        )
    )

    # Переименование таблиц
    op.execute("ALTER TABLE history RENAME TO history_new;")
    op.execute("ALTER TABLE history_old RENAME TO history;")

    # Удаление партиционированной таблицы
    partitions = [
        "history_2024_01",
        "history_2024_02",
        "history_2024_03",
        "history_2024_04",
        "history_2024_05",
        "history_2024_06",
        "history_2024_07",
        "history_2024_08",
        "history_2024_09",
        "history_2024_10",
        "history_2024_11",
        "history_2024_12",
        "history_2025_01",
        "history_2025_02",
        "history_2025_03",
        "history_2025_04",
        "history_2025_05",
        "history_2025_06",
        "history_2025_07"
    ]

    for partition in partitions:
        op.execute(text(f"DROP TABLE IF EXISTS {partition}"))

    op.execute("DROP TABLE IF EXISTS history_new;")