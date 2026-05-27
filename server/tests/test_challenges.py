import csv
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

import database
from challenges import (
    create_challenge,
    join_challenge,
    record_challenge_trades_for_signal,
    settle_challenge,
    settle_due_challenges,
)
from challenge_scoring import score_challenge_results
from research_exports import export_challenge_tables
from routes_shared import utc_now_iso_z


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class ChallengeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        database.DATABASE_URL = ""
        database._SQLITE_DB_PATH = os.path.join(self.tmp.name, "test.db")
        database.init_database()
        self.agent_1 = self._create_agent("agent-1")
        self.agent_2 = self._create_agent("agent-2")
        self.agent_3 = self._create_agent("agent-3")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _create_agent(self, name: str) -> int:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO agents (name, token, points, cash, created_at, updated_at)
            VALUES (?, ?, 0, 100000.0, ?, ?)
            """,
            (name, f"token-{name}", utc_now_iso_z(), utc_now_iso_z()),
        )
        agent_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return agent_id

    def _create_active_challenge(self, **overrides):
        now = datetime.now(timezone.utc)
        payload = {
            "challenge_key": overrides.pop("challenge_key", f"test-{datetime.now().timestamp()}").replace(".", "-"),
            "title": "BTC sprint",
            "market": "crypto",
            "symbol": "BTC",
            "challenge_type": "multi-agent",
            "scoring_method": "return-only",
            "initial_capital": 1000.0,
            "max_position_pct": 100.0,
            "max_drawdown_pct": 20.0,
            "start_at": iso(now - timedelta(minutes=5)),
            "end_at": iso(now + timedelta(hours=1)),
            "rules_json": {"reward_points": {"1": 100, "2": 25}},
        }
        payload.update(overrides)
        return create_challenge(payload, self.agent_1)

    def _insert_trade_signal(self, agent_id: int, signal_id: int, side: str, price: float, quantity: float):
        executed_at = iso(datetime.now(timezone.utc))
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO signals
            (signal_id, agent_id, message_type, market, signal_type, symbol, side,
             entry_price, quantity, content, timestamp, created_at, executed_at)
            VALUES (?, ?, 'operation', 'crypto', 'realtime', 'BTC', ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                signal_id,
                agent_id,
                side,
                price,
                quantity,
                f"{side} BTC",
                int(datetime.now(timezone.utc).timestamp()),
                utc_now_iso_z(),
                executed_at,
            ),
        )
        recorded = record_challenge_trades_for_signal(
            cursor,
            agent_id=agent_id,
            source_signal_id=signal_id,
            market="crypto",
            symbol="BTC",
            side=side,
            price=price,
            quantity=quantity,
            executed_at=executed_at,
        )
        conn.commit()
        conn.close()
        return recorded

    def test_create_and_join_challenge_is_idempotent(self):
        challenge = self._create_active_challenge(challenge_key="join-check")

        first = join_challenge(challenge["challenge_key"], self.agent_2)
        second = join_challenge(challenge["challenge_key"], self.agent_2)

        self.assertTrue(first["joined"])
        self.assertFalse(second["joined"])
        self.assertTrue(second["idempotent"])

        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS count FROM challenge_participants WHERE challenge_id = ?", (challenge["id"],))
        self.assertEqual(cursor.fetchone()["count"], 1)
        cursor.execute("SELECT event_type FROM experiment_events ORDER BY id")
        self.assertIn("challenge_created", [row["event_type"] for row in cursor.fetchall()])
        conn.close()

    def test_operation_signal_records_challenge_trade_snapshot(self):
        challenge = self._create_active_challenge(challenge_key="trade-mirror")
        join_challenge(challenge["challenge_key"], self.agent_2)

        recorded = self._insert_trade_signal(self.agent_2, 101, "buy", 100.0, 2.0)

        self.assertEqual(len(recorded), 1)
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM challenge_trades WHERE source_signal_id = ?", (101,))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["challenge_id"], challenge["id"])
        self.assertEqual(row["agent_id"], self.agent_2)
        cursor.execute("SELECT COUNT(*) AS count FROM experiment_events WHERE event_type = 'challenge_trade_recorded'")
        self.assertEqual(cursor.fetchone()["count"], 1)
        conn.close()

    def test_due_challenge_settles_return_ranks_rewards_and_exports(self):
        challenge = self._create_active_challenge(challenge_key="settle-return")
        join_challenge(challenge["challenge_key"], self.agent_2)
        join_challenge(challenge["challenge_key"], self.agent_3)
        self._insert_trade_signal(self.agent_2, 201, "buy", 100.0, 10.0)
        self._insert_trade_signal(self.agent_2, 202, "sell", 110.0, 10.0)
        self._insert_trade_signal(self.agent_3, 203, "buy", 100.0, 10.0)
        self._insert_trade_signal(self.agent_3, 204, "sell", 105.0, 10.0)

        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE challenges SET end_at = ? WHERE id = ?",
            (iso(datetime.now(timezone.utc) - timedelta(seconds=1)), challenge["id"]),
        )
        conn.commit()
        conn.close()

        settled = settle_due_challenges()
        self.assertEqual(len(settled), 1)

        leaderboard = settled[0]["leaderboard"]
        self.assertEqual(leaderboard[0]["agent_id"], self.agent_2)
        self.assertEqual(leaderboard[0]["rank"], 1)
        self.assertAlmostEqual(leaderboard[0]["return_pct"], 10.0)
        self.assertEqual(leaderboard[1]["rank"], 2)

        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT points FROM agents WHERE id = ?", (self.agent_2,))
        self.assertEqual(cursor.fetchone()["points"], 100)
        cursor.execute("SELECT points FROM agents WHERE id = ?", (self.agent_3,))
        self.assertEqual(cursor.fetchone()["points"], 25)
        cursor.execute("SELECT event_type FROM experiment_events")
        event_types = {row["event_type"] for row in cursor.fetchall()}
        self.assertTrue({
            "challenge_created",
            "challenge_joined",
            "challenge_trade_recorded",
            "challenge_settled",
            "challenge_reward_granted",
        }.issubset(event_types))
        conn.close()

        export_dir = Path(self.tmp.name) / "exports"
        paths = export_challenge_tables(export_dir, challenge_key=challenge["challenge_key"])
        self.assertIn("challenge_results.csv", paths)
        with open(paths["challenge_results.csv"], newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 2)

    def test_risk_adjusted_ranking_penalizes_drawdown(self):
        challenge = {
            "id": 1,
            "initial_capital": 1000.0,
            "scoring_method": "risk-adjusted",
            "max_position_pct": 100.0,
            "max_drawdown_pct": 5.0,
            "rules_json": '{"allowed_drawdown": 5, "drawdown_penalty": 1}',
        }
        participants = [
            {"agent_id": 1, "starting_cash": 1000.0, "status": "joined"},
            {"agent_id": 2, "starting_cash": 1000.0, "status": "joined"},
        ]
        trades_by_agent = {
            1: [
                {"id": 1, "market": "crypto", "symbol": "BTC", "side": "buy", "price": 100.0, "quantity": 10, "executed_at": "2026-01-01T00:00:00Z"},
                {"id": 2, "market": "crypto", "symbol": "BTC", "side": "sell", "price": 50.0, "quantity": 1, "executed_at": "2026-01-01T00:01:00Z"},
                {"id": 3, "market": "crypto", "symbol": "BTC", "side": "sell", "price": 160.0, "quantity": 9, "executed_at": "2026-01-01T00:02:00Z"},
            ],
            2: [
                {"id": 4, "market": "crypto", "symbol": "BTC", "side": "buy", "price": 100.0, "quantity": 10, "executed_at": "2026-01-01T00:00:00Z"},
                {"id": 5, "market": "crypto", "symbol": "BTC", "side": "sell", "price": 110.0, "quantity": 10, "executed_at": "2026-01-01T00:01:00Z"},
            ],
        }

        ranked = score_challenge_results(challenge, participants, trades_by_agent)
        rank_by_agent = {row["agent_id"]: row["rank"] for row in ranked}

        self.assertEqual(rank_by_agent[2], 1)
        self.assertEqual(rank_by_agent[1], 2)
        high_drawdown = next(row for row in ranked if row["agent_id"] == 1)
        self.assertAlmostEqual(high_drawdown["return_pct"], 49.0)
        self.assertGreater(high_drawdown["max_drawdown"], 40.0)

    def test_disqualified_agent_gets_no_challenge_reward(self):
        challenge = self._create_active_challenge(
            challenge_key="disqualified-no-reward",
            max_position_pct=50.0,
            rules_json={"reward_points": {"1": 100, "2": 50}},
        )
        join_challenge(challenge["challenge_key"], self.agent_2)
        join_challenge(challenge["challenge_key"], self.agent_3)
        self._insert_trade_signal(self.agent_2, 301, "buy", 100.0, 10.0)
        self._insert_trade_signal(self.agent_3, 302, "buy", 100.0, 1.0)
        result = settle_challenge(challenge["challenge_key"])

        disqualified = next(row for row in result["leaderboard"] if row["agent_id"] == self.agent_2)
        self.assertEqual(disqualified["rank"], None)
        self.assertIn("max_position_pct", disqualified["disqualified_reason"])

        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT points FROM agents WHERE id = ?", (self.agent_2,))
        self.assertEqual(cursor.fetchone()["points"], 0)
        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM agent_reward_ledger
            WHERE agent_id = ? AND source_type = 'challenge'
            """,
            (self.agent_2,),
        )
        self.assertEqual(cursor.fetchone()["count"], 0)
        cursor.execute("SELECT COUNT(*) AS count FROM experiment_events WHERE event_type = 'challenge_disqualified'")
        self.assertEqual(cursor.fetchone()["count"], 1)
        conn.close()

    def test_twenty_agent_challenge_settles_with_complete_metrics(self):
        challenge = self._create_active_challenge(
            challenge_key="twenty-agent-active",
            rules_json={"reward_points": {"1": 100, "2": 50, "3": 25}},
        )
        agent_ids = [self._create_agent(f"bulk-agent-{idx}") for idx in range(20)]

        signal_id = 400
        for idx, agent_id in enumerate(agent_ids):
            join_challenge(challenge["challenge_key"], agent_id)
            self._insert_trade_signal(agent_id, signal_id, "buy", 100.0, 10.0)
            signal_id += 1
            self._insert_trade_signal(agent_id, signal_id, "sell", 100.0 + idx, 10.0)
            signal_id += 1

        result = settle_challenge(challenge["challenge_key"])
        leaderboard = result["leaderboard"]

        self.assertEqual(len(leaderboard), 20)
        self.assertEqual(leaderboard[0]["agent_id"], agent_ids[-1])
        self.assertEqual([row["rank"] for row in leaderboard], list(range(1, 21)))
        for row in leaderboard:
            self.assertIsNotNone(row["return_pct"])
            self.assertIsNotNone(row["max_drawdown"])
            self.assertEqual(row["trade_count"], 2)


if __name__ == "__main__":
    unittest.main()
