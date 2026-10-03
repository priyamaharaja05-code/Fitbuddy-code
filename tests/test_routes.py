def test_homepage_and_health(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Your fitness profile" in response.text
    health = client.get("/health")
    assert health.json() == {"status": "ok", "generator": "local-rules", "external_api": False}


def test_generate_plan_persists_and_shows_seven_days(client, valid_form):
    response = client.post("/generate-workout", data=valid_form)
    assert response.status_code == 200
    assert "Your 7-day plan is ready" in response.text
    assert "Day 7" in response.text
    assert "nutrition" in response.text.lower()
    dashboard = client.get("/view-all-users")
    assert "Taylor Reed" in dashboard.text
    assert "taylor01" in dashboard.text


def test_invalid_user_form_is_friendly_and_not_saved(client, valid_form):
    valid_form["age"] = "9"
    response = client.post("/generate-workout", data=valid_form)
    assert response.status_code == 422
    assert "Input should be greater than or equal to 13" in response.text
    assert "Taylor Reed" not in client.get("/view-all-users").text


def test_feedback_updates_but_preserves_original(client, valid_form):
    client.post("/generate-workout", data=valid_form)
    response = client.post("/submit-feedback", data={"user_id": "taylor01", "feedback": "Please add more cardio and yoga"})
    assert response.status_code == 200
    assert "plan was updated" in response.text
    assert "easy cardio" in response.text.lower()
    dashboard = client.get("/view-all-users")
    assert "View original 7-day plan" in dashboard.text
    assert "View feedback and updated plan" in dashboard.text
    assert "Please add more cardio and yoga" in dashboard.text


def test_feedback_requires_existing_user_and_nonempty_feedback(client, valid_form):
    missing = client.post("/submit-feedback", data={"user_id": "missing01", "feedback": "Make it shorter"})
    assert missing.status_code == 404
    client.post("/generate-workout", data=valid_form)
    invalid = client.post("/submit-feedback", data={"user_id": "taylor01", "feedback": "  "})
    assert invalid.status_code == 422
    assert "tell us what you would like to change" in invalid.text.lower()
