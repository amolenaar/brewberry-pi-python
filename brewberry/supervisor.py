
from __future__ import absolute_import

from .actors import spawn_trap_link, register, Killed
from collections import namedtuple
from functools import partial, wraps

class KilledByChild(Killed): pass


ChildSpecTuple = namedtuple('ChildSpecTuple', ['id', 'start_func', 'args', 'kwargs', 'register', 'restart', 'shutdown'])


def child_spec(id, start_func, args=(), kwargs=None, register=False, restart='transient', shutdown=1):
    assert restart in ('permanent', 'transient', 'temporary')
    assert type(shutdown) is int or shutdown in ('brutal_kill', 'infinity')
    return ChildSpecTuple(id, start_func, args, kwargs or {}, register, restart, shutdown)


def supervisor(func):
    """
    This decorator can be used to tell the environment that a function is
    supervisor. Supervisors can be handled differently by (parent) supervisors.
    :param func:
    :return:
    """
    return func


def one_for_one_supervisor(child_specs, restarts=5):

    def _start_child_spec(spec):
        child = spawn_trap_link(spec.start_func, *spec.args, **spec.kwargs)
        if spec.register:
            register(spec.id, child)
        return child

    def deputy(child_addrs, restarts, start_child=None, terminate_child=None, which_children=None, trap_exit=None):
        if trap_exit and trap_exit[1]:
            func, exc = trap_exit
            if restarts <= 1:
                raise Killed
            child_spec = child_addrs[func]
            new_child_addr = _start_child_spec(child_spec)
            return partial(deputy, {(new_child_addr if addr is func else addr): cs for addr, cs in child_addrs.items()}, restarts - 1)
        elif start_child:
            pass
        elif terminate_child:
            pass
        elif which_children:
            which_children({cs.id: addr for addr, cs in child_addrs.items()})
        return partial(deputy, child_addrs, restarts)

    child_addrs = {_start_child_spec(cs): cs for cs in child_specs}

    return partial(deputy, child_addrs, restarts)


def one_for_all_supervisor(child_specs, restarts=5):

    StopChild = intern('__StopChild__')

    def stoppable(func):
        def wrapper(*args, **kwargs):
            if len(args) == 1 and args[0] is StopChild:
                return
            return func(*args, **kwargs)
        return wrapper

    def _start_child_spec(spec):
        child = spawn_trap_link(stoppable(spec.start_func), *spec.args, **spec.kwargs)
        if spec.register:
            register(spec.id, child)
        return child

    def deputy(child_addrs, restarts, start_child=None, terminate_child=None, which_children=None, trap_exit=None):
        if trap_exit and trap_exit[1]:
            if restarts <= 1:
                raise Killed
            for addr in child_addrs.keys():
                addr(StopChild)
            return partial(deputy, {_start_child_spec(cs): cs for cs in child_specs}, restarts - 1)
        elif start_child:
            pass
        elif terminate_child:
            pass
        elif which_children:
            which_children({cs.id: addr for addr, cs in child_addrs.items()})
        return partial(deputy, child_addrs, restarts)

    child_addrs = {_start_child_spec(cs): cs for cs in child_specs}

    return partial(deputy, child_addrs, restarts)
