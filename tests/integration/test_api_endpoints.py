"""Integration tests for FastAPI application and routes."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fastapi.testclient import TestClient
import pytest
import types

from opengov_earlymathematics.api.main import app as live_app, create_application
from opengov_earlymathematics.config import settings


def test_health_and_root_endpoints():
    # Use context manager to exercise startup/shutdown (lifespan)
    with TestClient(live_app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

        r2 = client.get("/")
        assert r2.status_code == 200
        data = r2.json()
        assert data["name"].startswith("OpenGov-EarlyMathematics API")


def test_curriculum_topics_for_grade_and_invalid():
    client = TestClient(live_app)
    r = client.get(f"{settings.api_prefix}/curriculum/grades/3/topics")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    r_bad = client.get(f"{settings.api_prefix}/curriculum/grades/invalid/topics")
    assert r_bad.status_code == 400


def test_lessons_for_topic_and_invalid_topic():
    client = TestClient(live_app)
    r = client.get(f"{settings.api_prefix}/curriculum/topics/multiplication/lessons", params={"grade": "3"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    r_bad = client.get(f"{settings.api_prefix}/curriculum/topics/not_a_topic/lessons")
    assert r_bad.status_code == 400


def test_get_problem_found_and_not_found():
    client = TestClient(live_app)
    ok = client.get(f"{settings.api_prefix}/problems/prob_mult_1")
    assert ok.status_code == 200
    miss = client.get(f"{settings.api_prefix}/problems/does_not_exist")
    assert miss.status_code == 404


def test_generate_and_check_problem():
    client = TestClient(live_app)
    gen = client.post(
        f"{settings.api_prefix}/problems/generate",
        json={"topic": "multiplication", "difficulty_level": 2, "student_level": 3},
    )
    assert gen.status_code == 200
    body = gen.json()
    assert "question" in body and body["topic"] == "multiplication"

    chk = client.post(
        f"{settings.api_prefix}/problems/check-solution",
        json={"problem_id": body["id"], "student_answer": "not-a-number", "show_steps": True},
    )
    assert chk.status_code == 200
    assert chk.json().get("hint")


def test_learning_path_endpoints():
    client = TestClient(live_app)
    lp = client.post(
        f"{settings.api_prefix}/learning-paths/create",
        json={
            "student_id": "stud_api",
            "grade_level": 3,
            "assessment_results": {"multiplication": 0.7, "fractions": 0.5},
            "learning_style": "visual",
        },
    )
    assert lp.status_code == 200
    data = lp.json()
    assert data["student_id"] == "stud_api"

    lp_get = client.get(f"{settings.api_prefix}/learning-paths/{data['path_id']}")
    assert lp_get.status_code == 200

    next_lesson = client.get(f"{settings.api_prefix}/learning-paths/{data['path_id']}/next-lesson")
    assert next_lesson.status_code == 200
    assert isinstance(next_lesson.json(), str) or next_lesson.json() is None


def test_tutoring_endpoints_with_mocks(monkeypatch):
    client = TestClient(live_app)

    class DummyTutor:
        def __init__(self, student_id: str):
            self.student_id = student_id

        def start_session(self, topic: str):
            return {"session_id": f"s_{self.student_id}", "greeting": "hi", "topic": topic}

        def help_with(self, question: str):
            return "an answer"

    # Patch AITutor used within routes
    import opengov_earlymathematics.ai.tutor as tutor_mod

    monkeypatch.setattr(tutor_mod, "AITutor", DummyTutor)

    start = client.post(f"{settings.api_prefix}/tutoring/start-session", params={"student_id": "s1", "topic": "algebra"})
    assert start.status_code == 200 and start.json()["topic"] == "algebra"

    ask = client.post(
        f"{settings.api_prefix}/tutoring/ask",
        json={"student_id": "s1", "topic": "algebra", "question": "what is 2+2?"},
    )
    assert ask.status_code == 200 and ask.json() == "an answer"


def test_misc_info_endpoints():
    with TestClient(live_app) as client:
        # Student progress endpoint
        prog = client.get(f"{settings.api_prefix}/students/s1/progress")
        assert prog.status_code == 200
        data = prog.json()
        assert data["student_id"] == "s1"

        # Analytics overview and detailed health
        ana = client.get(f"{settings.api_prefix}/analytics/overview")
        assert ana.status_code == 200
        det = client.get(f"{settings.api_prefix}/health/detailed")
        assert det.status_code == 200


def test_global_exception_handler_via_custom_route():
    # Build a fresh app and register a route that raises, to exercise global handler
    test_app = create_application()

    @test_app.get("/boom")
    async def boom():  # noqa: F811
        raise RuntimeError("kaboom")

    with TestClient(test_app, raise_server_exceptions=False) as client:
        r = client.get("/boom")
        assert r.status_code == 500
        assert r.json().get("detail") == "Internal server error"


def test_error_paths_for_routes(monkeypatch):
    # Exercise error handling branches in routes
    from opengov_earlymathematics.api import routes as routes_mod

    # Problem generation failure
    monkeypatch.setattr(
        routes_mod.problem_solver,
        "generate_problem",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("fail")),
    )
    with TestClient(live_app) as client:
        res = client.post(
            f"{settings.api_prefix}/problems/generate",
            json={"topic": "multiplication", "difficulty_level": 1, "student_level": 3},
        )
        assert res.status_code == 500

    # Solution check failure
    monkeypatch.setattr(
        routes_mod.problem_solver,
        "check_solution",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("fail")),
    )
    with TestClient(live_app) as client:
        res = client.post(
            f"{settings.api_prefix}/problems/check-solution",
            json={"problem_id": "p1", "student_answer": "1", "show_steps": False},
        )
        assert res.status_code == 500

    # Learning path create failure
    class BadLPG:
        def create_path(self, *a, **k):
            raise RuntimeError("fail")

    monkeypatch.setattr(routes_mod, "learning_path_generator", BadLPG())
    with TestClient(live_app) as client:
        res = client.post(
            f"{settings.api_prefix}/learning-paths/create",
            json={"student_id": "s", "grade_level": 3, "assessment_results": {"fractions": 0.2}},
        )
        assert res.status_code == 500

    # Tutoring endpoints failures
    import types, sys
    class RaisingTutor:
        def __init__(self, *a, **k):
            raise RuntimeError("init fail")

    dummy_module = types.SimpleNamespace(AITutor=RaisingTutor)
    # Ensure import inside route picks up our dummy
    monkeypatch.setitem(sys.modules, "opengov_earlymathematics.ai.tutor", dummy_module)
    with TestClient(live_app) as client:
        res = client.post(
            f"{settings.api_prefix}/tutoring/start-session",
            params={"student_id": "s1", "topic": "algebra"},
        )
        assert res.status_code == 500

        res2 = client.post(
            f"{settings.api_prefix}/tutoring/ask",
            json={"student_id": "s1", "topic": "algebra", "question": "?"},
        )
        assert res2.status_code == 500


def test_initialize_services_exception_path(monkeypatch):
    import asyncio
    from opengov_earlymathematics.api import main as main_mod

    # Force an exception inside initialize_services by making logger.info raise
    def boom_info(*a, **k):
        raise RuntimeError("log fail")

    def ok_error(*a, **k):
        # ensure the function reaches the 'raise' line after logging
        return None

    monkeypatch.setattr(main_mod, "logger", types.SimpleNamespace(info=boom_info, error=ok_error))

    with pytest.raises(RuntimeError):
        asyncio.get_event_loop().run_until_complete(main_mod.initialize_services())
