# Actors in Python

### Arjan does Actors

---

## How it started

I had a small temperature monitoring app using the observer pattern, and Tornado.

    class LoggerHandler(tornado.web.RequestHandler):

        @tornado.web.asynchronous
        def get(self):
            if not 'text/event-stream' in self.request.headers.get("Accept"):
                self.write('Expected an event stream')
                self.flush()
                self.finish()
                return
            self.set_header('Content-Type', 'text/event-stream')
            self.set_header('Cache-Control', 'no-cache, no-store')
            last_event_id = self.request.headers.get('Last-Event-ID')
            print 'last event: ', last_event_id

            sampler.observers.add(self)

        def __call__(self, sample):
            s = sample.as_dict()
            self.write('id: %s\n' % s['time'])
            self.write('event: sample\n')
            self.write('data: %s\n\n' % json_encode(s))
            self.flush()

        def on_connection_close(self):
            print 'Connection closed', id(self)
            sampler.observers.remove(self)

----

That is quite some code.

---

# GEvent

Then I found gevent. Gevent is 

* build op top  and Python's Greenlet library
* Lightweight threads.

Hmmm....

http://www.gevent.org

----

Anyway, this looks more readable:

    @get('/logger')
    def logger():
        response.content_type  = 'text/event-stream'
        response.cache_control = 'no-cache'

        # Set client-side auto-reconnect timeout, ms.
        yield 'retry: 100\n\n'

        queue = Queue()
        queue_put = queue.put
        try:
            topic_registry(register=queue_put)
            for sample in queue:
                yield 'id: %s\nevent: sample\ndata: %s\n\n' % (sample.time, json.dumps(sample.as_dict()))
        finally:
            topic_registry(deregister=queue_put)

---

# Greenlet + queue = actor

----

Sort of...


----

## What is an actor?

An actor is the fundamental unit of computation which embodies the 3 things that are essential to computation.

* processing
* storage
* communications

----

Actors can

1. send a finite number of messages to other actors
2. spawn a finite number of new actors
3. change its own internal behavior, taking effect when the next incoming message is handled

----

When an actor receives a message it can

1. create new actors
2. send messages to actors it has addresses before
3. designate how to handle the next message it receives (e.g. state)


https://channel9.msdn.com/Shows/Going+Deep/Hewitt-Meijer-and-Szyperski-The-Actor-Model-everything-you-wanted-to-know-but-were-afraid-to-ask

---

## Now to rebuild our OO design

* Classes vs functions
* How to receive messages
* Pattern matching
* State machine
* Supervision

---

## Classes vs functions

    def topic(topic_registry):
        def _topic(*args, **kwargs):
            receivers = ask(topic_registry, 'which_receivers')
            for r in receivers:
                r(*args, **kwargs)
            return _topic
        return _topic


---

## How to receive messages

In Erlang, a process has a special `receive` method.

     my_func() ->
       receive
         { message, Str } -> io:format("~p~n", [Str])
       end,
       my_func().
   
     my_func_pid = spawn(my_func)
     my_func_pid ! { message, "Hello" }



----


Where to put the `receive` function? How to do state changes? Return function to call on next iteration.

    def my_func(message=None):
        if message:
            print message
        return my_func

    my_func_addr = spawn(my_func)
    my_func_addr(message='Hello')

----

## State machines


    @with_self_address
    def ping(self, queue, i):
        queue.put('ping %d' % i)
        if i == 0: return
        self(queue, i - 1)
        return pong


    @with_self_address
    def pong(self, queue, i):
        queue.put('pong %d' % i)
        if i == 0: return
        self(queue, i - 1)
        return ping


---

## Pattern matching

In functional languages, pattern matching comes naturally.
Python does not do pattern matching. Use named method parameters where possible.

    spawn_link(timer, receiver=self, interval=SAMPLE_INTERVAL)


---

## Supervisors

Supervisors are smart: they link with their children, but trap their exit state.

    def one_for_one_supervisor(child_specs, restarts=5):

        def _start_child_spec(spec):
            return spawn_trap_link(spec.start_func, *spec.args, **spec.kwargs)

        def deputy(child_addrs, restarts_left, trap_exit=None):
            if trap_exit and trap_exit[1]:
                func, exc = trap_exit
                if restarts_left <= 1:
                    raise Killed
                child_spec = child_addrs[func]
                new_child_addr = _start_child_spec(child_spec)
                return partial(deputy,
                              {(new_child_addr if addr is func else addr): cs for addr, cs in child_addrs.items()},
                              restarts_left - 1)
            return partial(deputy, child_addrs, restarts_left)

        child_addrs = {_start_child_spec(cs): cs for cs in child_specs}

        return partial(deputy, child_addrs, restarts)

---


Split the controller. Enable and disable the state machine. 

---

Need topics with registration for the web interface -> 2 actors. Partials for the win.

    def topic_registry(receivers=(), register=None, deregister=None, which_receivers=None):
        if register:
            return partial(topic_registry, receivers=receivers + (register,))
        elif deregister:
            return partial(topic_registry, receivers=tuple(filter(lambda r: r is not deregister, receivers)))
        elif which_receivers:
            which_receivers(receivers)
        return partial(topic_registry, receivers=receivers)

---

# What I learned

* Actor thinking is more different from OO than I expected
* It's easier when you think in functions
* 



