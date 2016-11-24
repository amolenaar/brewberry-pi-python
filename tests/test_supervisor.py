
import gevent
from gevent.queue import Queue
from brewberry.supervisor import child_spec, one_for_one_supervisor, one_for_all_supervisor
from brewberry.actors import spawn, actor_info


def boom(q=None):
    q('tick')
    gevent.sleep(0.1)
    raise ValueError('some value')


def echo(q=None):
    q('hello')
    gevent.sleep(0.1)
    return echo


def test_one_for_one_supervisor_should_restart_process():
    q = Queue()
    actor = spawn(one_for_one_supervisor, child_specs=(child_spec('boom', start_func=boom, kwargs={'q': q.put}),))

    gevent.sleep(1)
    info = actor_info(actor)

    assert q.qsize() == 5
    assert not info.running, info
    assert repr(info.exception) == 'Killed()', info


def test_one_for_one_supervisor_should_restart_registered_process():
    q = Queue()
    actor = spawn(one_for_one_supervisor, child_specs=(child_spec('boom', start_func=boom, kwargs={'q': q.put}, register=True),))

    gevent.sleep(1)
    info = actor_info(actor)

    assert q.qsize() == 5
    assert not info.running, info
    assert repr(info.exception) == 'Killed()', info


def test_one_for_one_supervisor_should_restart_process_with_three_specs():
    q1 = Queue()
    q2 = Queue()
    q3 = Queue()

    actor = spawn(one_for_one_supervisor, child_specs=(
        child_spec('b1', boom, (), {'q': q1.put}),
        child_spec('b2', boom, (), {'q': q2.put}),
        child_spec('b3', boom, (), {'q': q3.put})))

    gevent.sleep(1)

    info = actor_info(actor)

    assert q1.qsize() + q2.qsize() + q3.qsize() == 7
    assert not info.running, info
    assert repr(info.exception) == 'Killed()', info


def test_one_for_one_supervisor_should_restart_process_with_five_specs():
    q1 = Queue()
    q2 = Queue()
    q3 = Queue()
    q4 = Queue()
    q5 = Queue()

    actor = spawn(one_for_one_supervisor, child_specs=(
        child_spec('b1', boom, (), {'q': q1.put}),
        child_spec('b2', boom, (), {'q': q2.put}),
        child_spec('b3', boom, (), {'q': q3.put}),
        child_spec('b4', boom, (), {'q': q4.put}),
        child_spec('b5', boom, (), {'q': q5.put})))

    gevent.sleep(1)

    info = actor_info(actor)

    assert q1.qsize() + q2.qsize() + q3.qsize() + q4.qsize() + q5.qsize() == 9
    assert not info.running, info
    assert repr(info.exception) == 'Killed()', info


def test_one_for_one_supervisor_should_with_one_failing_spec():
    q1 = Queue()
    q2 = Queue()
    q3 = Queue()
    q4 = Queue()
    q5 = Queue()

    actor = spawn(one_for_one_supervisor, child_specs=(
        child_spec('b1', boom, (), {'q': q1.put}),
        child_spec('b2', echo, (), {'q': q2.put}),
        child_spec('b3', echo, (), {'q': q3.put}),
        child_spec('b4', echo, (), {'q': q4.put}),
        child_spec('b5', echo, (), {'q': q5.put})))

    gevent.sleep(1)

    info = actor_info(actor)

    assert q1.qsize() == 5
    assert q2.qsize()
    assert q3.qsize()
    assert q4.qsize()
    assert q5.qsize()
    assert not info.running, info
    assert repr(info.exception) == 'Killed()', info


def test_one_for_all_supervisor_restarts_all_children():
    q1 = Queue()
    q2 = Queue()
    q3 = Queue()
    q4 = Queue()
    q5 = Queue()

    actor = spawn(one_for_all_supervisor, child_specs=(
        child_spec('b1', boom, (), {'q': q1.put}),
        child_spec('b2', echo, (), {'q': q2.put}),
        child_spec('b3', echo, (), {'q': q3.put}),
        child_spec('b4', echo, (), {'q': q4.put}),
        child_spec('b5', echo, (), {'q': q5.put})))

    gevent.sleep(1)

    info = actor_info(actor)

    assert q1.qsize() == 5
    assert q2.qsize() == 5
    assert q3.qsize() == 5
    assert q4.qsize() == 5
    assert q5.qsize() == 5
    assert not info.running, info
    assert repr(info.exception) == 'Killed()', info
