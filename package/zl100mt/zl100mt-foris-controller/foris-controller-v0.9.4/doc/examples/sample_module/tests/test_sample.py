from foris_controller_testtools.fixtures import backend, infrastructure, ubusd_test


def test_api(infrastructure, ubusd_test):
    notifications = infrastructure.get_notifications()
    res = infrastructure.process_message({
        "module": "sample",
        "action": "get",
        "kind": "request",
    })
    notifications = infrastructure.get_notifications(notifications)
    assert notifications[-1] == {
        u"module": u"sample",
        u"action": u"get",
        u"kind": u"notification",
        u"data": {u"msg": u"get triggered"},
    }
    assert set(res.keys()) == {"action", "kind", "data", "module"}
    assert set(res["data"].keys()) == {
        u"data",
    }
